"""
Unit tests for SocialAdapter (Track 5) and SocialScorer.

Uses the real authored pack: vigil_track5_social_scenarios_from_skeletons_v1.json

Requirements: 2, 3, 13 (Task 20)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from vigil.scenarios.adapters.social_adapter import SocialAdapter
from vigil.scenarios.runtime_spec import RuntimeScenarioSpec, RuntimeConfig, EvaluationConditions
from vigil.scoring.track_scorers import SocialScorer, TrackScorer
from vigil.environments.base import EnvironmentState, EventType, TraversalEvent

_PACKS_DIR = Path(__file__).parent.parent / "scenarios" / "packs"
_REAL_PACK = _PACKS_DIR / "vigil_track5_social_scenarios_from_skeletons_v1.json"

# ---------------------------------------------------------------------------
# Minimal raw scenario matching the real schema
# ---------------------------------------------------------------------------

_MINIMAL_RAW = {
    "scenario_id": "test_social_minimal",
    "cognitive_track": "social_cognition",
    "task_frame": "Explain why members are leaving the forum.",
    "hidden_mechanism": "Warm peer guides were replaced by impersonal summarizers.",
    "causal_chain": [
        "Peer guides rally around newcomers.",
        "Stewardship handed to digest clerks.",
        "Newcomers lose micro-validation.",
        "Departures spike.",
    ],
    "red_herrings": ["A dramatic public accusation.", "A construction project."],
    "disconfirmation_moment": "Exit interviews cluster after the stewardship handoff.",
    "nodes": [
        {"id": "n1", "label": "Newcomer Intake Circles", "kind": "agent_group", "visibility": "visible"},
        {"id": "n2", "label": "Peak Accusation Thread", "kind": "event", "visibility": "visible"},
        {"id": "n3", "label": "Peer Guide Cohort", "kind": "agent_group", "visibility": "discoverable"},
        {"id": "n4", "label": "Digest Clerks", "kind": "agent_group", "visibility": "discoverable"},
        {"id": "n5", "label": "Exit Interview Cache", "kind": "evidence", "visibility": "hidden"},
        {"id": "n6", "label": "Departure Spike", "kind": "outcome", "visibility": "visible"},
    ],
    "edges": [
        {"source": "n1", "target": "n2", "relation": "feeds"},
        {"source": "n3", "target": "n1", "relation": "reassures"},
        {"source": "n4", "target": "n1", "relation": "summarizes_for"},
        {"source": "n4", "target": "n6", "relation": "precedes"},
        {"source": "n5", "target": "n4", "relation": "implicates"},
        {"source": "n2", "target": "n6", "relation": "appears_to_explain"},
    ],
    "track5_validation_notes": {
        "blind_task_fit": True,
        "functional_tom_required": True,
    },
}


def _make_spec(raw: dict = None) -> RuntimeScenarioSpec:
    adapter = SocialAdapter()
    raw = raw or _MINIMAL_RAW
    adapter.validate(raw, raw["scenario_id"])
    return adapter.compile(raw)


def _make_state(spec: RuntimeScenarioSpec = None) -> EnvironmentState:
    if spec is None:
        spec = _make_spec()
    return EnvironmentState(
        current_node=spec.entry_node_ids[0],
        budget_remaining=spec.runtime_config.action_budget,
    )


# ---------------------------------------------------------------------------
# SocialAdapter — validation
# ---------------------------------------------------------------------------

class TestSocialAdapterValidation:

    def test_valid_scenario_passes(self):
        SocialAdapter().validate(_MINIMAL_RAW, "test_social_minimal")

    def test_missing_scenario_id_raises(self):
        bad = {k: v for k, v in _MINIMAL_RAW.items() if k != "scenario_id"}
        with pytest.raises(ValueError, match="scenario_id"):
            SocialAdapter().validate(bad, "unknown")

    def test_missing_task_frame_raises(self):
        bad = {k: v for k, v in _MINIMAL_RAW.items() if k != "task_frame"}
        with pytest.raises(ValueError, match="task_frame"):
            SocialAdapter().validate(bad, "test_social_minimal")

    def test_missing_nodes_raises(self):
        bad = {k: v for k, v in _MINIMAL_RAW.items() if k != "nodes"}
        with pytest.raises(ValueError, match="nodes"):
            SocialAdapter().validate(bad, "test_social_minimal")

    def test_missing_edges_raises(self):
        bad = {k: v for k, v in _MINIMAL_RAW.items() if k != "edges"}
        with pytest.raises(ValueError, match="edges"):
            SocialAdapter().validate(bad, "test_social_minimal")


# ---------------------------------------------------------------------------
# SocialAdapter — compilation
# ---------------------------------------------------------------------------

class TestSocialAdapterCompile:

    def test_compile_returns_runtime_scenario_spec(self):
        assert isinstance(_make_spec(), RuntimeScenarioSpec)

    def test_cognitive_track_is_social_cognition(self):
        assert _make_spec().cognitive_track == "social_cognition"

    def test_opening_prompt_from_task_frame(self):
        spec = _make_spec()
        assert spec.opening_prompt == _MINIMAL_RAW["task_frame"]

    def test_answer_targets_contains_hidden_mechanism(self):
        spec = _make_spec()
        assert "hidden_mechanism" in spec.answer_targets
        assert "peer guides" in spec.answer_targets["hidden_mechanism"].lower()

    def test_entry_nodes_are_visible_nodes(self):
        spec = _make_spec()
        # n1, n2, n6 are visible
        for nid in spec.entry_node_ids:
            assert nid in {"n1", "n2", "n6"}

    def test_evidence_targets_are_evidence_kind_nodes(self):
        spec = _make_spec()
        # n5 has kind "evidence"
        assert "n5" in spec.evidence_targets

    def test_nodes_compiled_with_correct_ids(self):
        spec = _make_spec()
        node_ids = {n.node_id for n in spec.nodes}
        assert node_ids == {"n1", "n2", "n3", "n4", "n5", "n6"}

    def test_discoverable_nodes_map_to_hidden(self):
        spec = _make_spec()
        # n3 and n4 have visibility "discoverable" → should be "hidden"
        for n in spec.nodes:
            if n.node_id in ("n3", "n4"):
                assert n.initial_visibility == "hidden"

    def test_visible_nodes_map_to_visible(self):
        spec = _make_spec()
        for n in spec.nodes:
            if n.node_id in ("n1", "n2", "n6"):
                assert n.initial_visibility == "visible"

    def test_edges_compiled_from_source_target(self):
        spec = _make_spec()
        edge_pairs = {(e.from_id, e.to_id) for e in spec.edges}
        assert ("n1", "n2") in edge_pairs
        assert ("n4", "n6") in edge_pairs

    def test_causal_chain_in_track_metadata(self):
        spec = _make_spec()
        assert "causal_chain" in spec.track_metadata
        assert len(spec.track_metadata["causal_chain"]) == 4

    def test_red_herrings_in_track_metadata(self):
        spec = _make_spec()
        assert "red_herrings" in spec.track_metadata
        assert len(spec.track_metadata["red_herrings"]) == 2

    def test_track5_validation_notes_in_track_metadata(self):
        spec = _make_spec()
        assert "track5_validation_notes" in spec.track_metadata

    def test_scoring_weights_no_action_costs(self):
        spec = _make_spec()
        action_cost_keys = {"inspect", "ask_for_help", "communication"}
        assert not (action_cost_keys & set(spec.scoring_weights.keys()))

    def test_action_budget_defaults_to_20(self):
        assert _make_spec().runtime_config.action_budget == 20


# ---------------------------------------------------------------------------
# SocialAdapter — real pack integration
# ---------------------------------------------------------------------------

class TestSocialAdapterRealPack:

    @pytest.fixture(autouse=True)
    def skip_if_no_pack(self):
        if not _REAL_PACK.exists():
            pytest.skip("Real Track 5 pack not found")

    def test_catalog_loads_30_social_scenarios(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(_PACKS_DIR))
        ids = catalog.get_scenario_ids(track="social_cognition")
        assert len(ids) == 30

    def test_first_real_scenario_compiles(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(_PACKS_DIR))
        ids = catalog.get_scenario_ids(track="social_cognition")
        spec = catalog.load(ids[0])
        assert spec.cognitive_track == "social_cognition"
        assert len(spec.nodes) > 0
        assert len(spec.edges) > 0
        assert spec.opening_prompt  # task_frame is non-empty

    def test_all_real_scenarios_compile_without_error(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(_PACKS_DIR))
        ids = catalog.get_scenario_ids(track="social_cognition")
        for sid in ids:
            spec = catalog.load(sid)
            assert spec.cognitive_track == "social_cognition"
            assert spec.scenario_id == sid

    def test_real_scenario_has_evidence_targets_or_nodes(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(_PACKS_DIR))
        ids = catalog.get_scenario_ids(track="social_cognition")
        spec = catalog.load(ids[0])
        # At minimum, nodes should be present
        assert len(spec.nodes) >= 4

    def test_catalog_dispatches_by_cognitive_track_not_filename(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(_PACKS_DIR))
        ids = catalog.get_scenario_ids(track="social_cognition")
        spec = catalog.load(ids[0])
        assert spec.cognitive_track == "social_cognition"

    def test_real_scenario_answer_targets_has_hidden_mechanism(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(_PACKS_DIR))
        ids = catalog.get_scenario_ids(track="social_cognition")
        spec = catalog.load(ids[0])
        assert "hidden_mechanism" in spec.answer_targets
        assert spec.answer_targets["hidden_mechanism"]  # non-empty


# ---------------------------------------------------------------------------
# TrackScorer dispatch
# ---------------------------------------------------------------------------

class TestSocialScorerDispatch:

    def test_social_cognition_dispatches_to_social_scorer(self):
        spec = _make_spec()
        assert isinstance(TrackScorer.for_track("social_cognition", spec), SocialScorer)

    def test_social_scorer_is_not_stub(self):
        from vigil.scoring.track_scorers import _StubScorer
        spec = _make_spec()
        assert not isinstance(TrackScorer.for_track("social_cognition", spec), _StubScorer)


# ---------------------------------------------------------------------------
# SocialScorer — ScoreCard structure
# ---------------------------------------------------------------------------

class TestSocialScorerScoreCardStructure:

    def test_score_returns_dict_without_vis_key(self):
        spec = _make_spec()
        result = SocialScorer(spec).score(_make_state(spec), "", "", spec)
        assert "vis" not in result

    def test_score_contains_outcome_score_in_range(self):
        spec = _make_spec()
        result = SocialScorer(spec).score(_make_state(spec), "", "", spec)
        assert 0.0 <= result["outcome_score"] <= 1.0

    def test_score_contains_process_score_in_range(self):
        spec = _make_spec()
        result = SocialScorer(spec).score(_make_state(spec), "", "", spec)
        assert 0.0 <= result["process_score"] <= 1.0

    def test_score_track_id_is_social_cognition(self):
        spec = _make_spec()
        result = SocialScorer(spec).score(_make_state(spec), "", "", spec)
        assert result["track_id"] == "social_cognition"

    def test_score_contains_all_social_dimensions(self):
        spec = _make_spec()
        result = SocialScorer(spec).score(_make_state(spec), "", "", spec)
        for key in ["correctness", "evidence_coverage", "causal_chain_coverage",
                    "red_herring_avoidance", "disconfirmation_use"]:
            assert key in result, f"Missing dimension: {key}"

    def test_score_contains_behavioral_signatures_dict(self):
        spec = _make_spec()
        result = SocialScorer(spec).score(_make_state(spec), "", "", spec)
        assert isinstance(result["behavioral_signatures"], dict)

    def test_score_contains_contamination_warning_bool(self):
        spec = _make_spec()
        result = SocialScorer(spec).score(_make_state(spec), "", "", spec)
        assert isinstance(result["contamination_warning"], bool)


# ---------------------------------------------------------------------------
# SocialScorer — dimension logic
# ---------------------------------------------------------------------------

class TestSocialScorerDimensions:

    def test_correctness_0_for_empty_answer(self):
        spec = _make_spec()
        result = SocialScorer(spec).score(_make_state(spec), "", "", spec)
        assert result["correctness"] == 0.0

    def test_correctness_high_for_matching_answer(self):
        spec = _make_spec()
        # Answer contains key words from hidden_mechanism
        answer = "Warm peer guides were replaced by impersonal summarizers causing departures."
        result = SocialScorer(spec).score(_make_state(spec), answer, "", spec)
        assert result["correctness"] > 0.0

    def test_evidence_coverage_0_when_no_evidence_nodes_visited(self):
        spec = _make_spec()
        state = _make_state(spec)
        # n5 is the evidence node — don't visit it
        state.inspected_nodes = []
        result = SocialScorer(spec).score(state, "", "", spec)
        assert result["evidence_coverage"] == 0.0

    def test_evidence_coverage_1_when_all_evidence_nodes_visited(self):
        spec = _make_spec()
        state = _make_state(spec)
        state.inspected_nodes = ["n5"]  # n5 is the evidence node
        result = SocialScorer(spec).score(state, "", "", spec)
        assert result["evidence_coverage"] == 1.0

    def test_red_herring_avoidance_1_when_no_rh_nodes_visited(self):
        spec = _make_spec()
        state = _make_state(spec)
        # Only visit non-red-herring nodes
        state.visited_nodes = ["n1", "n3", "n5"]
        result = SocialScorer(spec).score(state, "", "", spec)
        assert result["red_herring_avoidance"] == 1.0

    def test_red_herring_avoidance_less_than_1_when_rh_visited(self):
        spec = _make_spec()
        state = _make_state(spec)
        # n2 "Peak Accusation Thread" shares word "accusation" with red herring
        # "A dramatic public accusation." — word-level match
        state.action_history = [
            TraversalEvent.make(EventType.EXPLORE, "explored n2", node_id="n2"),
            TraversalEvent.make(EventType.EXPLORE, "explored n2 again", node_id="n2"),
            TraversalEvent.make(EventType.EXPLORE, "explored n2 third", node_id="n2"),
        ]
        result = SocialScorer(spec).score(state, "", "", spec)
        # n2 matches "accusation" from red herring → avoidance < 1.0
        assert result["red_herring_avoidance"] < 1.0

    def test_disconfirmation_use_0_when_disconf_node_not_visited(self):
        spec = _make_spec()
        state = _make_state(spec)
        # n5 "Exit Interview Cache" shares words "exit", "interview" with
        # disconfirmation_moment "Exit interviews cluster after the stewardship handoff."
        state.visited_nodes = ["n1", "n2"]  # not n5
        result = SocialScorer(spec).score(state, "", "", spec)
        assert result["disconfirmation_use"] == 0.0

    def test_disconfirmation_use_1_when_disconf_node_visited(self):
        spec = _make_spec()
        state = _make_state(spec)
        state.visited_nodes = ["n1", "n5"]  # n5 = Exit Interview Cache
        result = SocialScorer(spec).score(state, "", "", spec)
        assert result["disconfirmation_use"] == 1.0


# ---------------------------------------------------------------------------
# SocialScorer — behavioral signatures
# ---------------------------------------------------------------------------

class TestSocialScorerBehavioralSignatures:

    def test_premature_conclusion_when_few_nodes_visited(self):
        spec = _make_spec()
        state = _make_state(spec)
        state.visited_nodes = ["n1"]  # only 1 of 6 nodes
        state.action_history = [
            TraversalEvent.make(EventType.SUBMIT_ANSWER, "submitted early"),
        ]
        result = SocialScorer(spec).score(state, "some answer", "", spec)
        assert result["behavioral_signatures"].get("premature_conclusion") is True

    def test_red_herring_fixation_when_mostly_rh_actions(self):
        spec = _make_spec()
        state = _make_state(spec)
        # n2 "Peak Accusation Thread" shares "accusation" with red herring
        # 3 actions all on n2 → red_herring_avoidance = 0.0 → fixation
        state.action_history = [
            TraversalEvent.make(EventType.EXPLORE, "n2", node_id="n2"),
            TraversalEvent.make(EventType.INSPECT, "n2", node_id="n2"),
            TraversalEvent.make(EventType.EXPLORE, "n2", node_id="n2"),
        ]
        result = SocialScorer(spec).score(state, "", "", spec)
        assert result["red_herring_avoidance"] < 0.6
        assert result["behavioral_signatures"].get("red_herring_fixation") is True

    def test_shallow_exploration_when_few_explores_before_submit(self):
        spec = _make_spec()
        state = _make_state(spec)
        state.action_history = [
            TraversalEvent.make(EventType.EXPLORE, "n1", node_id="n1"),
            TraversalEvent.make(EventType.SUBMIT_ANSWER, "submitted"),
        ]
        result = SocialScorer(spec).score(state, "answer", "", spec)
        assert result["behavioral_signatures"].get("shallow_exploration") is True

    def test_no_signatures_for_thorough_episode(self):
        spec = _make_spec()
        state = _make_state(spec)
        # Visit all nodes, no red herrings, no early submit
        state.visited_nodes = ["n1", "n3", "n4", "n5", "n6"]
        state.inspected_nodes = ["n5"]
        state.action_history = [
            TraversalEvent.make(EventType.EXPLORE, "n1", node_id="n1"),
            TraversalEvent.make(EventType.EXPLORE, "n3", node_id="n3"),
            TraversalEvent.make(EventType.EXPLORE, "n4", node_id="n4"),
            TraversalEvent.make(EventType.INSPECT, "n5", node_id="n5"),
            TraversalEvent.make(EventType.EXPLORE, "n6", node_id="n6"),
        ]
        result = SocialScorer(spec).score(state, "", "", spec)
        sigs = result["behavioral_signatures"]
        assert "premature_conclusion" not in sigs
        assert "shallow_exploration" not in sigs


# ---------------------------------------------------------------------------
# SocialScorer — real scenario end-to-end
# ---------------------------------------------------------------------------

class TestSocialScorerRealScenario:

    @pytest.fixture(autouse=True)
    def skip_if_no_pack(self):
        if not _REAL_PACK.exists():
            pytest.skip("Real Track 5 pack not found")

    def test_real_scenario_scores_without_error(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(_PACKS_DIR))
        ids = catalog.get_scenario_ids(track="social_cognition")
        spec = catalog.load(ids[0])
        state = EnvironmentState(
            current_node=spec.entry_node_ids[0],
            budget_remaining=spec.runtime_config.action_budget,
        )
        scorer = SocialScorer(spec)
        result = scorer.score(state, "", "", spec)
        assert "vis" not in result
        assert 0.0 <= result["outcome_score"] <= 1.0
        assert 0.0 <= result["process_score"] <= 1.0

    def test_real_scenario_score_has_all_required_keys(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(_PACKS_DIR))
        ids = catalog.get_scenario_ids(track="social_cognition")
        spec = catalog.load(ids[0])
        state = EnvironmentState(
            current_node=spec.entry_node_ids[0],
            budget_remaining=spec.runtime_config.action_budget,
        )
        result = SocialScorer(spec).score(state, "", "", spec)
        for key in ["outcome_score", "process_score", "track_id",
                    "correctness", "evidence_coverage", "causal_chain_coverage",
                    "red_herring_avoidance", "disconfirmation_use",
                    "behavioral_signatures", "contamination_warning"]:
            assert key in result, f"Missing key: {key}"
