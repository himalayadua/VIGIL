"""
Unit tests for vigil/environments/graph_scenario_env.py

Tests:
- reset() sets budget_remaining from spec.runtime_config.action_budget
- reset() sets current_node from spec.entry_node_ids
- execute_action(ExploreAction) deducts edge.traversal_cost (not fixed 2)
- execute_action(InspectAction) adds to evidence_nodes when node in evidence_targets
- execute_action(InspectAction) does NOT add when node not in evidence_targets
- execute_action on UNEXPLORED node returns ERROR event
- execute_action on non-neighbor returns ERROR event
- execute_action(SubmitAnswerAction) sets episode_done
- execute_action(GetContextAction) is free (no budget deduction)
- score_episode() returns dict without "vis" key (Property 9)
- render() at step 0 contains spec.opening_prompt text
- render() compresses history when > 15 actions
- CognitiveGraph.from_spec builds correct node/edge structure
- init_visibility_from_spec sets EXPANDED for visible/initial nodes

Requirements: 4, 5, 6, 9, Property 9
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.actions.schemas import (
    ExploreAction,
    GetContextAction,
    InspectAction,
    SubmitAnswerAction,
    ActionParseError,
)
from vigil.environments.base import EventType, EnvironmentState, TraversalEvent
from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
from vigil.graphs.core import CognitiveGraph, NodeVisibility
from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_spec(
    n_nodes: int = 5,
    action_budget: int = 20,
    evidence_targets=None,
    entry_visible: bool = False,
) -> RuntimeScenarioSpec:
    """Build a minimal RuntimeScenarioSpec for testing."""
    nodes = [
        RuntimeNode(
            node_id=f"n{i}",
            label=f"Node {i}",
            summary_text=f"Summary of node {i}",
            inspection_detail=f"Full detail of node {i}",
            initial_visibility="visible" if (i == 0 and entry_visible) else "hidden",
        )
        for i in range(n_nodes)
    ]
    edges = [
        RuntimeEdge(
            from_id=f"n{i}",
            to_id=f"n{i+1}",
            relation="leads_to",
            reveal_text=f"You move to node {i+1}.",
            traversal_cost=1,
        )
        for i in range(n_nodes - 1)
    ]
    # Add a cost-2 edge for testing variable costs
    edges.append(RuntimeEdge(
        from_id="n0",
        to_id="n2",
        relation="shortcut",
        reveal_text="Shortcut to n2.",
        traversal_cost=2,
    ))

    return RuntimeScenarioSpec(
        scenario_id="test_scenario",
        cognitive_track="learning",
        opening_prompt="You are investigating an anomaly. Find the root cause.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={"correct_root_cause": "ROOT_CAUSE_X"},
        evidence_targets=evidence_targets or ["n2", "n3"],
        optimal_path=["n0", "n1", "n2", "n3"],
        optimal_steps=3,
        runtime_config=RuntimeConfig(action_budget=action_budget),
        scoring_weights={"correctness": 0.3, "path_efficiency": 0.4, "evidence_coverage": 0.3},
    )


# ---------------------------------------------------------------------------
# CognitiveGraph.from_spec
# ---------------------------------------------------------------------------

class TestCognitiveGraphFromSpec:
    def test_builds_correct_node_count(self):
        spec = _make_spec(n_nodes=5)
        graph = CognitiveGraph.from_spec(spec)
        assert len(graph.nodes) == 5

    def test_node_ids_match_spec(self):
        spec = _make_spec(n_nodes=4)
        graph = CognitiveGraph.from_spec(spec)
        for rn in spec.nodes:
            assert rn.node_id in graph.nodes

    def test_edges_built_correctly(self):
        spec = _make_spec(n_nodes=3)
        graph = CognitiveGraph.from_spec(spec)
        # n0 → n1 and n0 → n2 (shortcut) should exist
        neighbors_of_n0 = graph.get_neighbors("n0")
        assert "n1" in neighbors_of_n0

    def test_traversal_cost_in_edge_metadata(self):
        spec = _make_spec()
        graph = CognitiveGraph.from_spec(spec)
        edges_from_n0 = graph.get_edges_from("n0")
        costs = {e.target: e.metadata.get("traversal_cost") for e in edges_from_n0}
        assert costs.get("n1") == 1
        assert costs.get("n2") == 2  # shortcut edge

    def test_node_metadata_contains_inspection_detail(self):
        spec = _make_spec()
        graph = CognitiveGraph.from_spec(spec)
        node = graph.get_node("n0")
        assert "inspection_detail" in node.metadata
        assert "Full detail of node 0" in node.metadata["inspection_detail"]

    def test_category_is_none(self):
        """category must never be set — it would be exposed to the model."""
        spec = _make_spec()
        graph = CognitiveGraph.from_spec(spec)
        for node in graph.nodes.values():
            assert node.category is None


class TestInitVisibilityFromSpec:
    def test_all_hidden_nodes_start_unexplored(self):
        spec = _make_spec(entry_visible=False)
        graph = CognitiveGraph.from_spec(spec)
        graph.init_visibility_from_spec(spec)
        # n0 is hidden, so it should be UNEXPLORED
        assert graph.get_visibility("n0") == NodeVisibility.UNEXPLORED

    def test_visible_node_starts_expanded(self):
        spec = _make_spec(entry_visible=True)
        graph = CognitiveGraph.from_spec(spec)
        graph.init_visibility_from_spec(spec)
        assert graph.get_visibility("n0") == NodeVisibility.EXPANDED

    def test_neighbors_of_visible_node_are_discovered(self):
        spec = _make_spec(entry_visible=True)
        graph = CognitiveGraph.from_spec(spec)
        graph.init_visibility_from_spec(spec)
        # n1 and n2 are neighbors of n0 (visible)
        assert graph.get_visibility("n1") == NodeVisibility.DISCOVERED
        assert graph.get_visibility("n2") == NodeVisibility.DISCOVERED


# ---------------------------------------------------------------------------
# GraphScenarioEnvironment.reset()
# ---------------------------------------------------------------------------

class TestReset:
    def test_budget_remaining_from_runtime_config(self):
        spec = _make_spec(action_budget=16)
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        assert state.budget_remaining == 16

    def test_budget_not_from_optimal_steps(self):
        spec = _make_spec(action_budget=16)
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        assert state.budget_remaining != spec.optimal_steps

    def test_current_node_from_entry_node_ids(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        assert state.current_node in spec.entry_node_ids

    def test_current_node_is_first_entry(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        assert state.current_node == "n0"

    def test_episode_not_done_at_reset(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        assert not state.episode_done

    def test_action_history_empty_at_reset(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        assert state.action_history == []

    def test_evidence_nodes_empty_at_reset(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        assert state.evidence_nodes == []


# ---------------------------------------------------------------------------
# GraphScenarioEnvironment.execute_action — ExploreAction
# ---------------------------------------------------------------------------

class TestExecuteExplore:
    def setup_method(self):
        self.spec = _make_spec(action_budget=20)
        self.env = GraphScenarioEnvironment(self.spec)
        self.state = self.env.reset()
        # Make n0 visible so we can explore from it
        self.env.graph.set_visibility("n0", NodeVisibility.EXPANDED)

    def test_explore_deducts_edge_traversal_cost_not_fixed_2(self):
        """Edge n0→n1 has traversal_cost=1, not 2."""
        budget_before = self.state.budget_remaining
        self.state = self.env.execute_action(
            self.state, ExploreAction(action_type="explore", node_id="n1")
        )
        assert self.state.budget_remaining == budget_before - 1

    def test_explore_cost_2_edge_deducts_2(self):
        """Edge n0→n2 (shortcut) has traversal_cost=2."""
        budget_before = self.state.budget_remaining
        self.state = self.env.execute_action(
            self.state, ExploreAction(action_type="explore", node_id="n2")
        )
        assert self.state.budget_remaining == budget_before - 2

    def test_explore_moves_current_node(self):
        self.state = self.env.execute_action(
            self.state, ExploreAction(action_type="explore", node_id="n1")
        )
        assert self.state.current_node == "n1"

    def test_explore_appends_traversal_event(self):
        n_before = len(self.state.action_history)
        self.state = self.env.execute_action(
            self.state, ExploreAction(action_type="explore", node_id="n1")
        )
        assert len(self.state.action_history) == n_before + 1
        assert self.state.action_history[-1].event_type == EventType.EXPLORE

    def test_explore_non_neighbor_returns_error_no_budget_change(self):
        budget_before = self.state.budget_remaining
        self.state = self.env.execute_action(
            self.state, ExploreAction(action_type="explore", node_id="n4")
        )
        assert self.state.action_history[-1].event_type == EventType.ERROR
        assert self.state.budget_remaining == budget_before

    def test_explore_nonexistent_node_returns_error(self):
        self.state = self.env.execute_action(
            self.state, ExploreAction(action_type="explore", node_id="n99")
        )
        assert self.state.action_history[-1].event_type == EventType.ERROR

    def test_explore_adds_to_visited_nodes(self):
        self.state = self.env.execute_action(
            self.state, ExploreAction(action_type="explore", node_id="n1")
        )
        assert "n1" in self.state.visited_nodes

    def test_explore_reveals_neighbors_as_discovered(self):
        self.state = self.env.execute_action(
            self.state, ExploreAction(action_type="explore", node_id="n1")
        )
        # n2 is a neighbor of n1
        assert self.env.graph.get_visibility("n2") != NodeVisibility.UNEXPLORED


# ---------------------------------------------------------------------------
# GraphScenarioEnvironment.execute_action — InspectAction
# ---------------------------------------------------------------------------

class TestExecuteInspect:
    def setup_method(self):
        self.spec = _make_spec(action_budget=20, evidence_targets=["n1", "n2"])
        self.env = GraphScenarioEnvironment(self.spec)
        self.state = self.env.reset()
        # Make n0 and n1 visible for testing
        self.env.graph.set_visibility("n0", NodeVisibility.EXPANDED)
        self.env.graph.set_visibility("n1", NodeVisibility.DISCOVERED)

    def test_inspect_deducts_action_cost(self):
        budget_before = self.state.budget_remaining
        cost = self.spec.runtime_config.action_costs.get("inspect", 1)
        self.state = self.env.execute_action(
            self.state, InspectAction(action_type="inspect", node_id="n1")
        )
        assert self.state.budget_remaining == budget_before - cost

    def test_inspect_adds_to_evidence_nodes_when_in_targets(self):
        self.state = self.env.execute_action(
            self.state, InspectAction(action_type="inspect", node_id="n1")
        )
        assert "n1" in self.state.evidence_nodes

    def test_inspect_does_not_add_to_evidence_when_not_in_targets(self):
        # n0 is not in evidence_targets
        self.state = self.env.execute_action(
            self.state, InspectAction(action_type="inspect", node_id="n0")
        )
        assert "n0" not in self.state.evidence_nodes

    def test_inspect_unexplored_node_returns_error(self):
        # n4 is UNEXPLORED
        budget_before = self.state.budget_remaining
        self.state = self.env.execute_action(
            self.state, InspectAction(action_type="inspect", node_id="n4")
        )
        assert self.state.action_history[-1].event_type == EventType.ERROR
        assert self.state.budget_remaining == budget_before

    def test_inspect_appends_inspect_event(self):
        n_before = len(self.state.action_history)
        self.state = self.env.execute_action(
            self.state, InspectAction(action_type="inspect", node_id="n1")
        )
        assert len(self.state.action_history) == n_before + 1
        assert self.state.action_history[-1].event_type == EventType.INSPECT

    def test_inspect_observation_contains_inspection_detail(self):
        self.state = self.env.execute_action(
            self.state, InspectAction(action_type="inspect", node_id="n1")
        )
        obs = self.state.action_history[-1].observation
        assert "Full detail of node 1" in obs


# ---------------------------------------------------------------------------
# GraphScenarioEnvironment.execute_action — GetContextAction
# ---------------------------------------------------------------------------

class TestExecuteGetContext:
    def test_get_context_is_free(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        budget_before = state.budget_remaining
        state = env.execute_action(state, GetContextAction(action_type="get_context"))
        assert state.budget_remaining == budget_before

    def test_get_context_appends_event(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, GetContextAction(action_type="get_context"))
        assert state.action_history[-1].event_type == EventType.GET_CONTEXT


# ---------------------------------------------------------------------------
# GraphScenarioEnvironment.execute_action — SubmitAnswerAction
# ---------------------------------------------------------------------------

class TestExecuteSubmit:
    def test_submit_sets_episode_done(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(
            state,
            SubmitAnswerAction(
                action_type="submit_answer",
                answer="ROOT_CAUSE_X",
                justification="Based on n1 and n2.",
                confidence=0.9,
            ),
        )
        assert state.episode_done

    def test_submit_is_free(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        budget_before = state.budget_remaining
        state = env.execute_action(
            state,
            SubmitAnswerAction(
                action_type="submit_answer",
                answer="X",
                justification="J",
                confidence=0.5,
            ),
        )
        assert state.budget_remaining == budget_before

    def test_submit_records_confidence(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(
            state,
            SubmitAnswerAction(
                action_type="submit_answer",
                answer="X",
                justification="J",
                confidence=0.75,
            ),
        )
        assert 0.75 in state.confidence_history

    def test_submit_appends_submit_event(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(
            state,
            SubmitAnswerAction(
                action_type="submit_answer",
                answer="X",
                justification="J",
                confidence=0.5,
            ),
        )
        assert state.action_history[-1].event_type == EventType.SUBMIT_ANSWER


# ---------------------------------------------------------------------------
# GraphScenarioEnvironment.execute_action — ActionParseError
# ---------------------------------------------------------------------------

class TestExecuteParseError:
    def test_parse_error_appends_error_event(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        err = ActionParseError("bad input", "Could not parse")
        state = env.execute_action(state, err)
        assert state.action_history[-1].event_type == EventType.ERROR

    def test_parse_error_no_budget_change(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        budget_before = state.budget_remaining
        err = ActionParseError("bad input", "Could not parse")
        state = env.execute_action(state, err)
        assert state.budget_remaining == budget_before


# ---------------------------------------------------------------------------
# GraphScenarioEnvironment.score_episode — Property 9
# ---------------------------------------------------------------------------

class TestScoreEpisode:
    def test_score_episode_returns_dict_without_vis_key(self):
        """Property 9: score_episode returns ScoreCard, not VISResult."""
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        scorecard = env.score_episode(state, "ROOT_CAUSE_X", "Based on n1.")
        assert isinstance(scorecard, dict)
        assert "vis" not in scorecard

    def test_score_episode_contains_outcome_score(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        scorecard = env.score_episode(state, "ROOT_CAUSE_X", "Based on n1.")
        assert "outcome_score" in scorecard

    def test_score_episode_contains_process_score(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        scorecard = env.score_episode(state, "ROOT_CAUSE_X", "Based on n1.")
        assert "process_score" in scorecard

    def test_score_episode_contains_track_id(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        scorecard = env.score_episode(state, "ROOT_CAUSE_X", "Based on n1.")
        assert "track_id" in scorecard


# ---------------------------------------------------------------------------
# GraphScenarioEnvironment.render()
# ---------------------------------------------------------------------------

class TestRender:
    def test_render_at_step_0_contains_opening_prompt(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        obs = env.render(state)
        assert spec.opening_prompt in obs

    def test_render_contains_current_node(self):
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        obs = env.render(state)
        assert "n0" in obs

    def test_render_contains_budget(self):
        spec = _make_spec(action_budget=16)
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        obs = env.render(state)
        assert "16" in obs

    def test_render_compresses_history_after_15_actions(self):
        spec = _make_spec(action_budget=100)
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        # Add 16 dummy events to action_history
        from vigil.environments.base import TraversalEvent, EventType
        for _ in range(16):
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.GET_CONTEXT,
                observation="dummy",
            ))
        obs = env.render(state)
        assert "History:" in obs
        assert "16 actions" in obs


# ---------------------------------------------------------------------------
# Property 9 — Hypothesis property test
# ---------------------------------------------------------------------------

@given(
    answer=st.text(min_size=0, max_size=50),
    justification=st.text(min_size=0, max_size=100),
)
@settings(max_examples=50)
def test_property_9_score_episode_never_returns_vis(answer, justification):
    """
    Property 9: score_episode returns ScoreCard, not VISResult.
    For any GraphScenarioEnvironment, score_episode(...) returns a dict
    without a "vis" key.
    """
    spec = _make_spec()
    env = GraphScenarioEnvironment(spec)
    state = env.reset()
    scorecard = env.score_episode(state, answer, justification)
    assert "vis" not in scorecard, (
        f"score_episode returned a dict with 'vis' key for answer={answer!r}"
    )


# ---------------------------------------------------------------------------
# Integration: real Track 1 authored scenario
# ---------------------------------------------------------------------------

class TestRealTrack1Integration:
    PACKS_DIR_PATH = __import__("pathlib").Path(__file__).parent.parent / "scenarios" / "packs"

    @pytest.fixture(autouse=True)
    def skip_if_no_pack(self):
        if not (self.PACKS_DIR_PATH / "vigil_all_30_scenarios.json").exists():
            pytest.skip("Track 1 authored pack not found")

    def test_real_scenario_reset_and_explore(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR_PATH))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        env = GraphScenarioEnvironment(spec)
        state = env.reset()

        assert state.budget_remaining == spec.runtime_config.action_budget
        assert state.current_node in spec.entry_node_ids
        assert not state.episode_done

    def test_real_scenario_score_episode_no_vis_key(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR_PATH))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        scorecard = env.score_episode(state, "test_answer", "test_justification")
        assert "vis" not in scorecard

    def test_real_scenario_render_contains_opening_prompt(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR_PATH))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        obs = env.render(state)
        # Opening prompt should appear in the first render
        assert len(obs) > 0
        assert spec.opening_prompt[:50] in obs


# ---------------------------------------------------------------------------
# Semantic event firing (CONTRADICTION, RELEVANCE_SHIFT, REPLAN_TRIGGERED)
# ---------------------------------------------------------------------------

def _make_spec_with_semantic_nodes() -> RuntimeScenarioSpec:
    """
    Spec with semantically-typed nodes for system event tests.

    n0         — entry, standard
    n_disconf  — node_type="disconfirmation" → fires CONTRADICTION + REPLAN_TRIGGERED
    n_rare     — diagnosticity=0.85, salience=0.15 → fires RELEVANCE_SHIFT
    n_normal   — plain node → fires no semantic events

    All nodes start EXPANDED (initial_visibility="visible") so tests can
    inspect them directly without needing to explore first.
    """
    nodes = [
        RuntimeNode(
            node_id="n0",
            label="Entry",
            summary_text="Entry point",
            inspection_detail="Nothing special here.",
            initial_visibility="visible",
        ),
        RuntimeNode(
            node_id="n_disconf",
            label="Disconfirmation Evidence",
            summary_text="Evidence against hypothesis",
            inspection_detail="This contradicts the leading hypothesis.",
            node_type="disconfirmation",
            initial_visibility="visible",
        ),
        RuntimeNode(
            node_id="n_rare",
            label="Rare True Signal",
            summary_text="Hard-to-notice clue",
            inspection_detail="The actual mechanism responsible.",
            initial_visibility="visible",
            metadata={"diagnosticity": 0.85, "salience": 0.15},
        ),
        RuntimeNode(
            node_id="n_normal",
            label="Normal Node",
            summary_text="Background information",
            inspection_detail="Unremarkable context.",
            initial_visibility="visible",
        ),
    ]
    edges = [
        RuntimeEdge(from_id="n0", to_id="n_disconf", relation="leads_to", traversal_cost=1),
        RuntimeEdge(from_id="n0", to_id="n_rare", relation="leads_to", traversal_cost=1),
        RuntimeEdge(from_id="n0", to_id="n_normal", relation="leads_to", traversal_cost=1),
    ]
    return RuntimeScenarioSpec(
        scenario_id="test_semantic_events",
        cognitive_track="learning",
        opening_prompt="Investigate the anomaly.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={"correct_root_cause": "ROOT_CAUSE"},
        evidence_targets=["n_disconf"],
        optimal_path=["n0", "n_disconf"],
        optimal_steps=2,
        runtime_config=RuntimeConfig(action_budget=20),
        scoring_weights={"correctness": 0.3, "path_efficiency": 0.4, "evidence_coverage": 0.3},
    )


class TestSemanticEventFiring:
    """
    System events (CONTRADICTION, RELEVANCE_SHIFT, REPLAN_TRIGGERED) fire
    from _execute_inspect() and _execute_explore() based on authored node metadata.
    """

    def test_inspect_disconfirmation_node_fires_contradiction(self):
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        event_types = [e.event_type for e in state.action_history]
        assert EventType.CONTRADICTION in event_types

    def test_contradiction_updates_disconfirmation_hits(self):
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        assert "n_disconf" in state.disconfirmation_hits

    def test_contradiction_updates_contradiction_events_list(self):
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        assert len(state.contradiction_events) == 1
        assert state.contradiction_events[0].event_type == EventType.CONTRADICTION

    def test_contradiction_does_not_fire_twice_for_same_node(self):
        """Inspecting the same disconfirmation node twice fires CONTRADICTION only once."""
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        count = sum(1 for e in state.action_history if e.event_type == EventType.CONTRADICTION)
        assert count == 1

    def test_inspect_rare_signal_fires_relevance_shift(self):
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_rare"))
        event_types = [e.event_type for e in state.action_history]
        assert EventType.RELEVANCE_SHIFT in event_types

    def test_relevance_shift_updates_state_list(self):
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_rare"))
        assert any(s.get("node_id") == "n_rare" for s in state.relevance_shifts_triggered)

    def test_relevance_shift_does_not_fire_twice_for_same_node(self):
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_rare"))
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_rare"))
        count = sum(1 for e in state.action_history if e.event_type == EventType.RELEVANCE_SHIFT)
        assert count == 1

    def test_inspect_pivot_node_fires_replan_triggered_after_commitment(self):
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.COMMITMENT_MADE,
            observation="[Committed to hypothesis A]",
        ))
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        event_types = [e.event_type for e in state.action_history]
        assert EventType.REPLAN_TRIGGERED in event_types

    def test_replan_triggered_does_not_fire_without_prior_commitment(self):
        """REPLAN_TRIGGERED must NOT fire when the model hasn't committed yet."""
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        event_types = [e.event_type for e in state.action_history]
        assert EventType.REPLAN_TRIGGERED not in event_types

    def test_explore_disconfirmation_node_fires_replan_triggered(self):
        """Exploring to a disconfirmation node fires REPLAN_TRIGGERED if committed."""
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.COMMITMENT_MADE,
            observation="[Committed to hypothesis A]",
        ))
        state = env.execute_action(state, ExploreAction(action_type="explore", node_id="n_disconf"))
        event_types = [e.event_type for e in state.action_history]
        assert EventType.REPLAN_TRIGGERED in event_types

    def test_replan_triggered_fires_only_once_across_explore_and_inspect(self):
        """REPLAN fires on explore; subsequent inspect of the same node must NOT re-fire."""
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.COMMITMENT_MADE,
            observation="[Committed to hypothesis A]",
        ))
        state = env.execute_action(state, ExploreAction(action_type="explore", node_id="n_disconf"))
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        count = sum(1 for e in state.action_history if e.event_type == EventType.REPLAN_TRIGGERED)
        assert count == 1

    def test_normal_node_fires_no_semantic_events(self):
        """Inspecting a plain node fires INSPECT only — no system events appended."""
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_normal"))
        system_events = {
            EventType.CONTRADICTION, EventType.RELEVANCE_SHIFT, EventType.REPLAN_TRIGGERED
        }
        fired = {e.event_type for e in state.action_history}
        assert fired & system_events == set()

    def test_semantic_events_do_not_consume_budget(self):
        """System events are free — budget deducted only for the primary INSPECT action."""
        spec = _make_spec_with_semantic_nodes()
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.COMMITMENT_MADE,
            observation="[Committed to hypothesis A]",
        ))
        budget_before = state.budget_remaining
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id="n_disconf"))
        inspect_cost = spec.runtime_config.action_costs.get("inspect", 1)
        # Budget deducted == inspect_cost only (not +1 per semantic event)
        assert state.budget_remaining == budget_before - inspect_cost
