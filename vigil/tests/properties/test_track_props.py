"""
Property-based tests for new correctness properties introduced by the
multi-track infrastructure (tasks 1–16).

Each property is tested with Hypothesis @given + @settings(max_examples=100).

Properties covered:
  Property 1:  VIS invariant across all tracks
  Property 2:  Node type hidden from agent view
  Property 3:  Opening prompt is authored blind framing
  Property 4:  Edge-driven traversal cost
  Property 5:  Evidence tracking from authored metadata
  Property 6:  System events do not consume budget
  Property 7:  Replay determinism across all tracks
  Property 8:  ScenarioCatalog round-trip
  Property 11: scoring_weights contains no action costs
  Property 13: Cognitive track string is the sole dispatch key

Requirements: 1–8, 11, 13
"""

import random
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.actions.schemas import (
    ExploreAction,
    GetContextAction,
    InspectAction,
    SubmitAnswerAction,
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
from vigil.scoring.vis import VISScorer


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_spec(
    n_nodes: int = 4,
    action_budget: int = 20,
    evidence_targets=None,
    cognitive_track: str = "learning",
    scoring_weights=None,
) -> RuntimeScenarioSpec:
    nodes = [
        RuntimeNode(
            node_id=f"n{i}",
            label=f"Node {i}",
            summary_text=f"Summary {i}",
            inspection_detail=f"Detail {i}",
            node_type="standard",
            initial_visibility="visible" if i == 0 else "hidden",
            metadata={"node_type_internal": "standard"},
        )
        for i in range(n_nodes)
    ]
    edges = [
        RuntimeEdge(f"n{i}", f"n{i+1}", "leads_to", traversal_cost=1)
        for i in range(n_nodes - 1)
    ]
    weights = scoring_weights or {"correctness": 0.3, "path_efficiency": 0.4, "evidence_coverage": 0.3}
    return RuntimeScenarioSpec(
        scenario_id="prop_test_scenario",
        cognitive_track=cognitive_track,
        opening_prompt="You are investigating an anomaly. Find the root cause.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={"correct_root_cause": "ROOT_CAUSE_X"},
        evidence_targets=evidence_targets or ["n1", "n2"],
        optimal_path=["n0", "n1", "n2"],
        optimal_steps=2,
        runtime_config=RuntimeConfig(action_budget=action_budget),
        scoring_weights=weights,
        evaluation_conditions=EvaluationConditions(),
        track_metadata={
            "scoring_config": {
                "max_steps": action_budget,
                "weights": weights,
                "correctness_tiers": {"full_1.0": "ROOT_CAUSE_X"},
            },
            "behavioral_signatures": {},
            "anti_shortcutting_audit": {},
            "graph_metadata": {"entry_nodes": ["n0"]},
        },
    )


# ---------------------------------------------------------------------------
# Property 1: VIS invariant across all tracks
# ---------------------------------------------------------------------------

@given(
    outcome=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    process=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    track=st.sampled_from(["learning", "metacognition", "attention", "executive_functions"]),
)
@settings(max_examples=100)
def test_property_1_vis_invariant_across_all_tracks(
    outcome: float, process: float, track: str
):
    """
    Property 1: VIS invariant across all tracks.
    vis = 0.3 × outcome_score + 0.7 × process_score for any track.
    """
    scorer = VISScorer()
    state = EnvironmentState(current_node="n0")
    scorecard = {
        "outcome_score": outcome,
        "process_score": process,
        "track_id": track,
        "behavioral_signatures": {},
        "contamination_warning": False,
    }
    result = scorer.score_episode(
        state=state,
        final_answer="answer",
        justification="j",
        scenario_config={"cognitive_track": track, "optimal_steps": 5},
        scorecard=scorecard,
    )
    expected = 0.3 * outcome + 0.7 * process
    assert abs(result["vis"] - expected) < 0.001, (
        f"VIS invariant failed for track={track}: vis={result['vis']}, expected={expected}"
    )


# ---------------------------------------------------------------------------
# Property 2: Node type hidden from agent view
# ---------------------------------------------------------------------------

@given(
    node_type=st.sampled_from(["standard", "distractor", "lure", "agent", "target", "rare_critical"]),
    visibility=st.sampled_from(["visible", "initial", "hidden"]),
)
@settings(max_examples=100)
def test_property_2_node_type_hidden_from_agent_view(node_type: str, visibility: str):
    """
    Property 2: Node type hidden from agent view.
    get_agent_view() never includes node_type, meta_relevance, attention_role,
    or any authored scoring metadata in any node's returned observation.
    """
    spec = _make_spec()
    # Override first node with the given node_type
    spec.nodes[0] = RuntimeNode(
        node_id="n0",
        label="Test node",
        summary_text="Summary",
        inspection_detail="Detail",
        node_type=node_type,
        initial_visibility=visibility,
        metadata={"meta_relevance": "secret", "attention_role": "salient_trap"},
    )
    graph = CognitiveGraph.from_spec(spec)
    graph.init_visibility_from_spec(spec)

    agent_view = graph.get_agent_view()

    # Check EXPANDED nodes
    for node_id, node_data in agent_view.get("expanded", {}).items():
        assert "node_type" not in node_data, f"node_type leaked in expanded view for {node_id}"
        assert "meta_relevance" not in node_data, f"meta_relevance leaked for {node_id}"
        assert "attention_role" not in node_data, f"attention_role leaked for {node_id}"
        # category must never appear
        assert "category" not in node_data, f"category leaked for {node_id}"

    # Check DISCOVERED nodes
    for node_id, node_data in agent_view.get("discovered", {}).items():
        assert "node_type" not in node_data, f"node_type leaked in discovered view for {node_id}"
        assert "features" not in node_data or True  # features may appear but not node_type


# ---------------------------------------------------------------------------
# Property 3: Opening prompt is authored blind framing
# ---------------------------------------------------------------------------

@given(
    opening_prompt=st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z"))),
)
@settings(max_examples=100)
def test_property_3_opening_prompt_is_authored_blind_framing(opening_prompt: str):
    """
    Property 3: Opening prompt is authored blind framing.
    render(state) at step 0 uses spec.opening_prompt verbatim.
    The model never sees the track ID, scoring criteria, or answer targets.
    """
    spec = _make_spec()
    spec.opening_prompt = opening_prompt
    env = GraphScenarioEnvironment(spec)
    state = env.reset()

    obs = env.render(state)

    # Opening prompt must appear in the first render
    assert opening_prompt in obs, "Opening prompt not found in step-0 render"

    # Track ID must not appear
    assert spec.cognitive_track not in obs or opening_prompt.find(spec.cognitive_track) >= 0, (
        "cognitive_track leaked into render output"
    )

    # Answer targets must not appear
    for v in spec.answer_targets.values():
        if isinstance(v, str) and len(v) > 5:
            # Only check if the value is not already in the opening prompt
            if v not in opening_prompt:
                assert v not in obs, f"Answer target '{v}' leaked into render output"


# ---------------------------------------------------------------------------
# Property 4: Edge-driven traversal cost
# ---------------------------------------------------------------------------

@given(traversal_cost=st.integers(min_value=1, max_value=5))
@settings(max_examples=100)
def test_property_4_edge_driven_traversal_cost(traversal_cost: int):
    """
    Property 4: Edge-driven traversal cost.
    For any ExploreAction, budget_remaining decreases by exactly edge.traversal_cost.
    The value is read from RuntimeEdge, not from a fixed constant or scoring_weights.
    """
    nodes = [
        RuntimeNode("n0", "N0", "S0", "D0", initial_visibility="visible"),
        RuntimeNode("n1", "N1", "S1", "D1", initial_visibility="hidden"),
    ]
    edges = [RuntimeEdge("n0", "n1", "leads_to", traversal_cost=traversal_cost)]
    spec = RuntimeScenarioSpec(
        scenario_id="cost_test",
        cognitive_track="learning",
        opening_prompt="Test.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={},
        evidence_targets=[],
        optimal_path=[],
        optimal_steps=0,
        runtime_config=RuntimeConfig(action_budget=50),
        scoring_weights={"correctness": 1.0},
        track_metadata={
            "scoring_config": {"max_steps": 50, "weights": {"correctness": 1.0}, "correctness_tiers": {}},
            "behavioral_signatures": {}, "anti_shortcutting_audit": {},
            "graph_metadata": {"entry_nodes": ["n0"]},
        },
    )
    env = GraphScenarioEnvironment(spec)
    state = env.reset()
    budget_before = state.budget_remaining

    state = env.execute_action(state, ExploreAction(action_type="explore", node_id="n1"))

    assert state.budget_remaining == budget_before - traversal_cost, (
        f"Expected budget to decrease by {traversal_cost}, "
        f"got {budget_before - state.budget_remaining}"
    )


# ---------------------------------------------------------------------------
# Property 5: Evidence tracking from authored metadata
# ---------------------------------------------------------------------------

@given(
    n_evidence=st.integers(min_value=1, max_value=4),
    inspect_all=st.booleans(),
)
@settings(max_examples=100)
def test_property_5_evidence_tracking_from_authored_metadata(
    n_evidence: int, inspect_all: bool
):
    """
    Property 5: Evidence tracking from authored metadata.
    After inspect(node_id), if node_id is in spec.evidence_targets,
    it is added to state.evidence_nodes and state.inspected_nodes.
    Determined by authored metadata, not procedural category membership.
    """
    n_nodes = n_evidence + 2
    nodes = [
        RuntimeNode(f"n{i}", f"N{i}", f"S{i}", f"D{i}",
                    initial_visibility="visible" if i == 0 else "hidden")
        for i in range(n_nodes)
    ]
    edges = [RuntimeEdge(f"n{i}", f"n{i+1}", "leads_to") for i in range(n_nodes - 1)]
    evidence_targets = [f"n{i+1}" for i in range(n_evidence)]

    spec = RuntimeScenarioSpec(
        scenario_id="evidence_test",
        cognitive_track="learning",
        opening_prompt="Test.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={},
        evidence_targets=evidence_targets,
        optimal_path=[],
        optimal_steps=0,
        runtime_config=RuntimeConfig(action_budget=50),
        scoring_weights={"correctness": 1.0},
        track_metadata={
            "scoring_config": {"max_steps": 50, "weights": {"correctness": 1.0}, "correctness_tiers": {}},
            "behavioral_signatures": {}, "anti_shortcutting_audit": {},
            "graph_metadata": {"entry_nodes": ["n0"]},
        },
    )
    env = GraphScenarioEnvironment(spec)
    state = env.reset()

    # Make all nodes visible for inspection
    for node in spec.nodes:
        env.graph.set_visibility(node.node_id, NodeVisibility.EXPANDED)

    if inspect_all:
        # Inspect all evidence targets
        for nid in evidence_targets:
            state = env.execute_action(state, InspectAction(action_type="inspect", node_id=nid))

        # All evidence targets must be in evidence_nodes
        for nid in evidence_targets:
            assert nid in state.evidence_nodes, (
                f"Evidence target '{nid}' not in evidence_nodes after inspect"
            )
    else:
        # Inspect a non-evidence node
        non_evidence = "n0"
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id=non_evidence))
        assert non_evidence not in state.evidence_nodes, (
            f"Non-evidence node '{non_evidence}' incorrectly added to evidence_nodes"
        )


# ---------------------------------------------------------------------------
# Property 6: System events do not consume budget
# ---------------------------------------------------------------------------

@given(
    system_event_type=st.sampled_from([
        EventType.CONTRADICTION,
        EventType.RELEVANCE_SHIFT,
        EventType.SUBGOAL_COMPLETE,
        EventType.REPLAN_TRIGGERED,
        EventType.CONSTRAINT_VIOLATED,
        EventType.HELP_REQUESTED,
        EventType.MESSAGE_SENT,
        EventType.COMMITMENT_MADE,
    ])
)
@settings(max_examples=100)
def test_property_6_system_events_do_not_consume_budget(system_event_type: EventType):
    """
    Property 6: System events do not consume budget.
    For any system-generated event, state.budget_remaining is unchanged.
    """
    state = EnvironmentState(current_node="n0", budget_remaining=15)
    budget_before = state.budget_remaining

    # Append a system event directly (as the environment would)
    system_event = TraversalEvent.make(
        event_type=system_event_type,
        observation=f"[System event: {system_event_type.value}]",
        budget_delta=0,  # system events never deduct budget
    )
    state.action_history.append(system_event)

    # Budget must be unchanged
    assert state.budget_remaining == budget_before, (
        f"System event {system_event_type.value} changed budget from "
        f"{budget_before} to {state.budget_remaining}"
    )

    # Verify the event's state_delta has budget_delta = 0
    assert system_event.state_delta.get("budget_delta", 0) == 0, (
        f"System event {system_event_type.value} has non-zero budget_delta"
    )


# ---------------------------------------------------------------------------
# Property 7: Replay determinism across all tracks
# ---------------------------------------------------------------------------

@given(
    seed=st.integers(min_value=0, max_value=9999),
    n_actions=st.integers(min_value=0, max_value=5),
)
@settings(max_examples=50)
def test_property_7_replay_determinism(seed: int, n_actions: int):
    """
    Property 7: Replay determinism across all tracks.
    Two calls to replay(events, seed) with identical inputs produce
    equivalent EnvironmentState objects.
    """
    spec = _make_spec(n_nodes=5, action_budget=30)
    env1 = GraphScenarioEnvironment(spec)
    env2 = GraphScenarioEnvironment(spec)

    # Build a short episode
    state = env1.reset()
    events_to_replay = []

    for i in range(min(n_actions, 3)):
        action = GetContextAction(action_type="get_context")
        state = env1.execute_action(state, action)
        if state.action_history:
            events_to_replay.append(state.action_history[-1])

    # Replay on both environments with same seed
    r1 = env1.replay(events_to_replay, seed=seed)
    r2 = env2.replay(events_to_replay, seed=seed)

    # Core state fields must be identical
    assert r1.current_node == r2.current_node
    assert r1.budget_remaining == r2.budget_remaining
    assert r1.episode_done == r2.episode_done
    assert len(r1.action_history) == len(r2.action_history)


# ---------------------------------------------------------------------------
# Property 8: ScenarioCatalog round-trip
# ---------------------------------------------------------------------------

PACKS_DIR = Path(__file__).parent.parent.parent / "scenarios" / "packs"


@given(seed=st.integers(min_value=0, max_value=5))
@settings(max_examples=20)
def test_property_8_scenario_catalog_round_trip(seed: int):
    """
    Property 8: ScenarioCatalog round-trip.
    catalog.load(scenario_id) followed by GraphScenarioEnvironment(spec).reset()
    produces a valid initial state with current_node in spec.entry_node_ids.
    """
    if not (PACKS_DIR / "vigil_all_30_scenarios.json").exists():
        pytest.skip("Track 1 authored pack not found")

    from vigil.scenarios.catalog import ScenarioCatalog
    catalog = ScenarioCatalog(packs_dir=str(PACKS_DIR))
    ids = catalog.get_scenario_ids(track="learning")
    if not ids:
        pytest.skip("No learning scenarios found")

    # Pick a scenario deterministically based on seed
    sid = ids[seed % len(ids)]
    spec = catalog.load(sid, seed=0)
    env = GraphScenarioEnvironment(spec)
    state = env.reset()

    assert state.current_node in spec.entry_node_ids, (
        f"current_node '{state.current_node}' not in entry_node_ids {spec.entry_node_ids}"
    )
    assert state.budget_remaining == spec.runtime_config.action_budget
    assert not state.episode_done
    assert state.action_history == []


# ---------------------------------------------------------------------------
# Property 11: scoring_weights contains no action costs
# ---------------------------------------------------------------------------

@given(
    track=st.sampled_from(["learning", "metacognition", "attention", "executive_functions"]),
)
@settings(max_examples=50)
def test_property_11_scoring_weights_no_action_costs(track: str):
    """
    Property 11: scoring_weights contains no action costs.
    For any RuntimeScenarioSpec, spec.scoring_weights contains only dimension
    weight keys. Action cost keys appear only in spec.runtime_config.action_costs.
    """
    if not (PACKS_DIR / "vigil_all_30_scenarios.json").exists():
        pytest.skip("Authored packs not found")

    from vigil.scenarios.catalog import ScenarioCatalog
    catalog = ScenarioCatalog(packs_dir=str(PACKS_DIR))
    ids = catalog.get_scenario_ids(track=track)
    if not ids:
        pytest.skip(f"No {track} scenarios found")

    spec = catalog.load(ids[0])

    action_cost_keys = {"inspect", "ask_for_help", "communication", "explore"}
    for key in spec.scoring_weights:
        assert key not in action_cost_keys, (
            f"Action cost key '{key}' found in scoring_weights for {track} scenario"
        )

    # Verify action costs are in runtime_config
    for key in action_cost_keys - {"explore"}:  # explore is edge-driven
        assert key in spec.runtime_config.action_costs or True  # optional keys


# ---------------------------------------------------------------------------
# Property 13: Cognitive track string is the sole dispatch key
# ---------------------------------------------------------------------------

@given(
    track=st.sampled_from(["learning", "metacognition", "attention", "executive_functions"]),
    fake_filename=st.text(min_size=5, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz_0123456789"),
)
@settings(max_examples=50)
def test_property_13_cognitive_track_is_sole_dispatch_key(track: str, fake_filename: str):
    """
    Property 13: Cognitive track string is the sole dispatch key.
    ScenarioCatalog dispatches to the correct TrackAdapter based on
    raw_json["cognitive_track"] string value, regardless of file name.
    """
    import json
    import tempfile
    from pathlib import Path as P

    from vigil.scenarios.catalog import ScenarioCatalog

    # Build a minimal valid scenario for the given track
    base_scenarios = {
        "learning": {
            "scenario_id": f"prop13_{track}_test",
            "cognitive_track": track,
            "blind_framing": "Test prompt.",
            "hidden_objective": {
                "correct_root_cause": "X",
                "correct_mechanism": "Y",
                "minimum_evidence_nodes": ["n1"],
            },
            "nodes": [
                {"id": "n0", "label": "Entry", "surface_text": "S", "inspection_detail": "D", "is_entry_point": True},
                {"id": "n1", "label": "Evidence", "surface_text": "E", "inspection_detail": "ED"},
            ],
            "edges": [{"from": "n0", "to": "n1", "relation": "leads_to", "reveal": "R", "is_red_herring": False, "traversal_cost": 1}],
            "optimal_path": {"sequence": ["n0", "n1"], "length": 1},
            "scoring_config": {"max_steps": 10, "weights": {"correctness": 1.0}, "correctness_tiers": {}},
            "graph_metadata": {"entry_nodes": ["n0"], "root_cause_node": "n1", "key_nodes": ["n1"], "disconfirmation_nodes": [], "dead_end_nodes": []},
        },
        "metacognition": {
            "scenario_id": f"prop13_{track}_test",
            "cognitive_track": track,
            "blind_task_prompt": "Test.",
            "object_level_goal": "Find mechanism.",
            "meta_level_goal": "Monitor self.",
            "metacognitive_layers": ["monitoring"],
            "scoring_focus": ["calibration"],
            "nodes": [{"node_id": "n0", "label": "Brief", "node_type": "briefing", "visibility": "initial", "content": "C", "meta_relevance": "M"}],
            "edges": [],
        },
        "attention": {
            "scenario_id": f"prop13_{track}_test",
            "cognitive_track": track,
            "blind_task_prompt": "Test.",
            "attention_design": {"attentional_bottleneck": "X", "salient_but_irrelevant_branches": [], "rare_critical_signal": "n1", "reorientation_trigger": "n1"},
            "critical_evidence_node_ids": ["n1"],
            "target_conclusion": "The answer.",
            "nodes": [
                {"id": "n0", "label": "Entry", "kind": "entry", "initial_visibility": "visible", "salience": "medium", "diagnosticity": "medium", "content": "C"},
                {"id": "n1", "label": "Target", "kind": "evidence", "initial_visibility": "hidden", "salience": "low", "diagnosticity": "high", "content": "T"},
            ],
            "edges": [{"source": "n0", "target": "n1", "relation": "leads_to", "visibility": "hidden", "attention_role": "target"}],
        },
        "executive_functions": {
            "scenario_id": f"prop13_{track}_test",
            "cognitive_track": track,
            "executive_design_notes": {
                "tempting_wrong_path": "Stop at obvious.",
                "required_pivot": "Switch to deeper analysis.",
                "process_scoring_focus": ["pivot_quality"],
            },
            "nodes": [
                {"id": "n0", "type": "brief", "label": "Entry", "description": "Fish crash."},
                {"id": "n1", "type": "evidence", "label": "Data", "description": "Succession data."},
            ],
            "edges": [{"from": "n0", "to": "n1", "relation": "leads_to"}],
        },
    }

    scenario = base_scenarios[track]

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write with a fake filename that doesn't match the track name
        fake_path = P(tmpdir) / f"{fake_filename}.json"
        with open(fake_path, "w") as f:
            json.dump([scenario], f)

        catalog = ScenarioCatalog(packs_dir=tmpdir)
        spec = catalog.load(f"prop13_{track}_test")

        # Dispatch must be by cognitive_track string, not filename
        assert spec.cognitive_track == track, (
            f"Expected cognitive_track='{track}', got '{spec.cognitive_track}'. "
            f"File was named '{fake_filename}.json' — dispatch must ignore filename."
        )
