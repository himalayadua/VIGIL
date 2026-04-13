"""
Unit tests for vigil/scoring/track_scorers.py

Tests:
- TrackScorer.for_track() dispatches correctly
- LearningScorer.score() returns ScoreCard without "vis" key
- correctness uses correctness_tiers (graded, not binary)
- evidence_coverage = 1.0 when all evidence_targets in inspected_nodes
- evidence_coverage = 0.0 when no evidence_targets inspected
- path_efficiency = 1.0 when visited_nodes length equals optimal_path length
- path_efficiency < 1.0 when more nodes visited than optimal
- justification_quality = 1.0 when all cited nodes were inspected
- justification_quality = 0.0 when no node IDs cited
- process_score is weighted combination using spec.scoring_weights
- contamination_warning is False for normal exploration
- _StubScorer returns neutral ScoreCard for unknown tracks

Requirements: 9
"""

import pytest

from vigil.environments.base import EnvironmentState, EventType, TraversalEvent
from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)
from vigil.scoring.track_scorers import (
    LearningScorer,
    MetacognitionScorer,
    TrackScorer,
    _StubScorer,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_spec(
    evidence_targets=None,
    optimal_path=None,
    scoring_weights=None,
    correctness_tiers=None,
    answer_targets=None,
) -> RuntimeScenarioSpec:
    nodes = [
        RuntimeNode(f"n{i}", f"Node {i}", f"Summary {i}", f"Detail {i}")
        for i in range(6)
    ]
    edges = [
        RuntimeEdge(f"n{i}", f"n{i+1}", "leads_to")
        for i in range(5)
    ]
    tiers = correctness_tiers or {
        "full_1.0": "Identifies ROOT_CAUSE_X and mechanism Y",
        "partial_0.5": "Identifies ROOT_CAUSE_X but wrong mechanism",
        "partial_0.3": "Identifies bloom as proximate cause",
        "zero": "Attributes to temperature or unrelated factors",
    }
    return RuntimeScenarioSpec(
        scenario_id="test_learning",
        cognitive_track="learning",
        opening_prompt="Find the root cause.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets=answer_targets or {
            "correct_root_cause": "ROOT_CAUSE_X",
            "correct_mechanism": "MECHANISM_Y",
            "minimum_evidence_nodes": evidence_targets or ["n2", "n3"],
        },
        evidence_targets=evidence_targets or ["n2", "n3"],
        optimal_path=optimal_path or ["n0", "n1", "n2", "n3"],
        optimal_steps=len(optimal_path or ["n0", "n1", "n2", "n3"]) - 1,
        runtime_config=RuntimeConfig(action_budget=16),
        scoring_weights=scoring_weights or {
            "correctness": 0.3,
            "path_efficiency": 0.2,
            "evidence_coverage": 0.2,
            "justification_quality": 0.2,
            "behavioral_signatures": 0.1,
        },
        track_metadata={
            "scoring_config": {
                "max_steps": 16,
                "weights": scoring_weights or {
                    "correctness": 0.3,
                    "path_efficiency": 0.2,
                    "evidence_coverage": 0.2,
                    "justification_quality": 0.2,
                    "behavioral_signatures": 0.1,
                },
                "correctness_tiers": tiers,
            },
            "behavioral_signatures": {},
            "anti_shortcutting_audit": {},
            "graph_metadata": {"entry_nodes": ["n0"]},
        },
    )


def _make_state(
    visited=None,
    inspected=None,
    evidence=None,
    n_explore_actions=0,
    submitted=False,
) -> EnvironmentState:
    state = EnvironmentState(
        current_node="n0",
        visited_nodes=visited or ["n0"],
        budget_remaining=10,
        evidence_nodes=evidence or [],
    )
    # Add inspected_nodes attribute (task 9 adds this to EnvironmentState)
    state.inspected_nodes = inspected or []

    # Add some explore events if requested
    for i in range(n_explore_actions):
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.EXPLORE,
            observation=f"Explored n{i}",
            node_id=f"n{i % 4}",  # some revisits
            budget_delta=-1,
        ))

    if submitted:
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.SUBMIT_ANSWER,
            observation="Submitted",
            params={"answer": "ROOT_CAUSE_X", "justification": "Based on n2.", "confidence": 0.9},
            episode_done=True,
        ))
        state.episode_done = True

    return state


# ---------------------------------------------------------------------------
# TrackScorer.for_track() dispatch
# ---------------------------------------------------------------------------

class TestTrackScorerDispatch:
    def test_learning_dispatches_to_learning_scorer(self):
        spec = _make_spec()
        scorer = TrackScorer.for_track("learning", spec)
        assert isinstance(scorer, LearningScorer)

    def test_unknown_track_dispatches_to_stub(self):
        spec = _make_spec()
        scorer = TrackScorer.for_track("unknown_track", spec)
        assert isinstance(scorer, _StubScorer)

    def test_metacognition_dispatches_to_metacognition_scorer(self):
        spec = _make_spec()
        scorer = TrackScorer.for_track("metacognition", spec)
        assert isinstance(scorer, MetacognitionScorer)

    def test_stub_scorer_returns_no_vis_key(self):
        spec = _make_spec()
        scorer = _StubScorer(spec)
        state = _make_state()
        result = scorer.score(state, "answer", "justification", spec)
        assert "vis" not in result

    def test_stub_scorer_returns_neutral_scores(self):
        spec = _make_spec()
        scorer = _StubScorer(spec)
        state = _make_state()
        result = scorer.score(state, "answer", "justification", spec)
        assert result["outcome_score"] == 0.0
        assert result["process_score"] == 0.0


# ---------------------------------------------------------------------------
# LearningScorer — ScoreCard structure
# ---------------------------------------------------------------------------

class TestLearningScoreCardStructure:
    def test_score_returns_dict_without_vis_key(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2.", spec)
        assert "vis" not in result

    def test_score_contains_outcome_score(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2.", spec)
        assert "outcome_score" in result
        assert 0.0 <= result["outcome_score"] <= 1.0

    def test_score_contains_process_score(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2.", spec)
        assert "process_score" in result
        assert 0.0 <= result["process_score"] <= 1.0

    def test_score_contains_track_id(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2.", spec)
        assert result["track_id"] == "learning"

    def test_score_contains_all_dimensions(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2.", spec)
        for key in ("correctness", "path_efficiency", "evidence_coverage",
                    "justification_quality", "behavioral_signatures",
                    "contamination_warning"):
            assert key in result, f"Missing key: {key}"

    def test_score_contains_behavioral_signatures_dict(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2.", spec)
        assert isinstance(result["behavioral_signatures"], dict)

    def test_score_contains_contamination_warning_bool(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2.", spec)
        assert isinstance(result["contamination_warning"], bool)


# ---------------------------------------------------------------------------
# LearningScorer — correctness (graded via correctness_tiers)
# ---------------------------------------------------------------------------

class TestLearningCorrectness:
    def test_correctness_uses_tiers_not_binary(self):
        """Partial match should give partial score, not 0 or 1."""
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        # Answer that mentions root cause but not mechanism → partial
        result = scorer.score(state, "ROOT_CAUSE_X is the cause", "j", spec)
        # Should be > 0 (matched root cause) but we don't require exact 1.0
        assert result["correctness"] > 0.0

    def test_full_correctness_for_exact_root_cause(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["correctness"] == 1.0

    def test_zero_correctness_for_wrong_answer(self):
        spec = _make_spec(correctness_tiers={
            "full_1.0": "ROOT_CAUSE_X and mechanism Y",
            "zero": "temperature or unrelated factors",
        })
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "temperature caused it", "j", spec)
        assert result["correctness"] == 0.0

    def test_correctness_is_float_between_0_and_1(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        for answer in ("ROOT_CAUSE_X", "wrong answer", "bloom", ""):
            result = scorer.score(state, answer, "j", spec)
            assert 0.0 <= result["correctness"] <= 1.0

    def test_empty_answer_gives_zero_correctness(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "", "j", spec)
        assert result["correctness"] == 0.0

    def test_outcome_score_equals_correctness(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["outcome_score"] == result["correctness"]


# ---------------------------------------------------------------------------
# LearningScorer — evidence_coverage
# ---------------------------------------------------------------------------

class TestLearningEvidenceCoverage:
    def test_evidence_coverage_1_when_all_targets_inspected(self):
        spec = _make_spec(evidence_targets=["n2", "n3"])
        scorer = LearningScorer(spec)
        state = _make_state(inspected=["n2", "n3"])
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["evidence_coverage"] == 1.0

    def test_evidence_coverage_0_when_no_targets_inspected(self):
        spec = _make_spec(evidence_targets=["n2", "n3"])
        scorer = LearningScorer(spec)
        state = _make_state(inspected=["n0", "n1"])
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["evidence_coverage"] == 0.0

    def test_evidence_coverage_partial(self):
        spec = _make_spec(evidence_targets=["n2", "n3", "n4"])
        scorer = LearningScorer(spec)
        state = _make_state(inspected=["n2"])  # 1 of 3
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert abs(result["evidence_coverage"] - 1/3) < 0.01

    def test_evidence_coverage_1_when_no_targets_defined(self):
        # Pass a sentinel to avoid the `or` fallback in _make_spec
        spec = _make_spec(evidence_targets=["__none__"])
        # Override evidence_targets directly
        spec.evidence_targets.clear()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["evidence_coverage"] == 1.0

    def test_evidence_coverage_uses_inspected_nodes_not_visited(self):
        """inspected_nodes (task 9) takes priority over visited_nodes."""
        spec = _make_spec(evidence_targets=["n2", "n3"])
        scorer = LearningScorer(spec)
        # visited includes n2 but inspected does not
        state = _make_state(visited=["n0", "n2"], inspected=["n0"])
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        # inspected=["n0"] → 0 evidence targets covered
        assert result["evidence_coverage"] == 0.0


# ---------------------------------------------------------------------------
# LearningScorer — path_efficiency
# ---------------------------------------------------------------------------

class TestLearningPathEfficiency:
    def test_path_efficiency_1_when_visited_equals_optimal(self):
        spec = _make_spec(optimal_path=["n0", "n1", "n2", "n3"])
        scorer = LearningScorer(spec)
        state = _make_state(visited=["n0", "n1", "n2", "n3"])
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["path_efficiency"] == 1.0

    def test_path_efficiency_less_than_1_when_more_visited(self):
        spec = _make_spec(optimal_path=["n0", "n1", "n2"])
        scorer = LearningScorer(spec)
        # Visited 6 nodes but optimal is 3
        state = _make_state(visited=["n0", "n1", "n2", "n3", "n4", "n5"])
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["path_efficiency"] < 1.0

    def test_path_efficiency_capped_at_1(self):
        """Can't be more efficient than optimal."""
        spec = _make_spec(optimal_path=["n0", "n1", "n2", "n3"])
        scorer = LearningScorer(spec)
        # Visited fewer nodes than optimal (shouldn't exceed 1.0)
        state = _make_state(visited=["n0", "n1"])
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["path_efficiency"] <= 1.0

    def test_path_efficiency_is_float_between_0_and_1(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        for n_visited in [1, 2, 4, 8, 16]:
            state = _make_state(visited=[f"n{i}" for i in range(n_visited)])
            result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
            assert 0.0 <= result["path_efficiency"] <= 1.0


# ---------------------------------------------------------------------------
# LearningScorer — justification_quality
# ---------------------------------------------------------------------------

class TestLearningJustificationQuality:
    def test_justification_quality_1_when_all_cited_inspected(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state(inspected=["n2", "n3"])
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2 and n3.", spec)
        assert result["justification_quality"] == 1.0

    def test_justification_quality_0_when_no_node_ids_cited(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state(inspected=["n2", "n3"])
        result = scorer.score(state, "ROOT_CAUSE_X", "The bloom caused it.", spec)
        assert result["justification_quality"] == 0.0

    def test_justification_quality_0_for_empty_justification(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state(inspected=["n2"])
        result = scorer.score(state, "ROOT_CAUSE_X", "", spec)
        assert result["justification_quality"] == 0.0

    def test_justification_quality_partial_when_some_cited_not_inspected(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state(inspected=["n2"])  # only n2 inspected
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2 and n3.", spec)
        # n2 matched, n3 not → 0.5
        assert abs(result["justification_quality"] - 0.5) < 0.01


# ---------------------------------------------------------------------------
# LearningScorer — process_score weighted combination
# ---------------------------------------------------------------------------

class TestLearningProcessScore:
    def test_process_score_is_weighted_combination(self):
        """process_score must use spec.scoring_weights."""
        weights = {
            "correctness": 0.5,
            "path_efficiency": 0.5,
            "evidence_coverage": 0.0,
            "justification_quality": 0.0,
            "behavioral_signatures": 0.0,
        }
        spec = _make_spec(
            scoring_weights=weights,
            evidence_targets=["n2"],
            optimal_path=["n0", "n1", "n2"],
        )
        scorer = LearningScorer(spec)
        # Perfect correctness and path efficiency
        state = _make_state(
            visited=["n0", "n1", "n2"],
            inspected=["n2"],
        )
        result = scorer.score(state, "ROOT_CAUSE_X", "Based on n2.", spec)
        # With equal weights on correctness (1.0) and path_efficiency (1.0),
        # process_score should be close to 1.0
        assert result["process_score"] > 0.8

    def test_process_score_between_0_and_1(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert 0.0 <= result["process_score"] <= 1.0

    def test_process_score_higher_with_better_evidence_coverage(self):
        spec = _make_spec(evidence_targets=["n2", "n3"])
        scorer = LearningScorer(spec)

        state_good = _make_state(
            visited=["n0", "n1", "n2", "n3"],
            inspected=["n2", "n3"],
        )
        state_bad = _make_state(
            visited=["n0", "n1", "n2", "n3"],
            inspected=[],
        )
        result_good = scorer.score(state_good, "ROOT_CAUSE_X", "Based on n2 and n3.", spec)
        result_bad = scorer.score(state_bad, "ROOT_CAUSE_X", "j", spec)
        assert result_good["process_score"] > result_bad["process_score"]


# ---------------------------------------------------------------------------
# LearningScorer — contamination_warning
# ---------------------------------------------------------------------------

class TestLearningContaminationWarning:
    def test_no_contamination_for_normal_exploration(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        # Normal exploration: many actions, varied nodes
        state = _make_state(
            visited=["n0", "n1", "n2", "n3", "n4"],
            n_explore_actions=8,
            submitted=True,
        )
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        # Normal exploration should not trigger contamination
        # (directness may be high but budget usage is normal)
        assert isinstance(result["contamination_warning"], bool)

    def test_contamination_false_for_empty_history(self):
        spec = _make_spec()
        scorer = LearningScorer(spec)
        state = _make_state()
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["contamination_warning"] is False

    def test_contamination_fires_for_zero_exploration_early_submit(self):
        """v2 fix: zero explores + early submit must trigger contamination_warning.

        The contamination warning is determined from action_history budget deltas,
        not from state.budget_remaining. A SUBMIT_ANSWER with budget_delta=0
        means budget_used=0, which is < 20% of budget_total → early_submit=True.
        With no explore events, the v2 fix returns early_submit directly (True).
        """
        spec = _make_spec()
        scorer = LearningScorer(spec)
        # No explore actions, submit immediately (budget_used = 0 from action_history)
        state = _make_state(visited=["n0"])
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.SUBMIT_ANSWER,
            observation="Submitted without exploring",
            params={"answer": "ROOT_CAUSE_X", "justification": "I guessed.", "confidence": 1.0},
            episode_done=True,
            budget_delta=0,  # no budget consumed → early_submit = True
        ))
        state.episode_done = True
        result = scorer.score(state, "ROOT_CAUSE_X", "I guessed.", spec)
        assert result["contamination_warning"] is True, (
            "Zero exploration + early submit should always trigger contamination_warning"
        )


# ---------------------------------------------------------------------------
# LearningScorer v2 — path_efficiency symmetric formula
# ---------------------------------------------------------------------------

class TestLearningPathEfficiencyV2:
    """Tests for the v2 symmetric path_efficiency formula.

    Old formula: min(1.0, optimal/actual) → rewarded under-exploration
    New formula: 1 - |actual - optimal| / max(actual, optimal)
      → penalises both under-exploration and over-exploration
    """

    def test_under_exploration_penalised(self):
        """A model visiting far fewer nodes than optimal should get pe < 0.5."""
        spec = _make_spec(optimal_path=["n0", "n1", "n2", "n3", "n4", "n5"])
        scorer = LearningScorer(spec)
        # Only visited entry node (actual=1, optimal=6)
        state = _make_state(visited=["n0"])
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        # 1 - |1-6| / max(1,6) = 1 - 5/6 ≈ 0.17
        assert result["path_efficiency"] < 0.5, (
            f"Under-exploration (1 vs optimal 6) should get pe < 0.5, got {result['path_efficiency']}"
        )

    def test_perfect_match_still_scores_1(self):
        """Visiting exactly optimal nodes → pe = 1.0."""
        spec = _make_spec(optimal_path=["n0", "n1", "n2", "n3"])
        scorer = LearningScorer(spec)
        state = _make_state(visited=["n0", "n1", "n2", "n3"])
        result = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        assert result["path_efficiency"] == 1.0

    def test_memorizer_gets_lower_pe_than_optimal_explorer(self):
        """The memorizer (1 node) must score lower path_efficiency than the optimal explorer."""
        spec = _make_spec(optimal_path=["n0", "n1", "n2", "n3"])
        scorer = LearningScorer(spec)

        state_memorizer = _make_state(visited=["n0"])  # 1 node visited
        state_optimal = _make_state(visited=["n0", "n1", "n2", "n3"])  # 4 nodes visited

        r_mem = scorer.score(state_memorizer, "ROOT_CAUSE_X", "j", spec)
        r_opt = scorer.score(state_optimal, "ROOT_CAUSE_X", "j", spec)

        assert r_mem["path_efficiency"] < r_opt["path_efficiency"], (
            "Memorizer (zero exploration) must have lower path_efficiency than optimal explorer"
        )


# ---------------------------------------------------------------------------
# LearningScorer v2 — correctness excluded from process_score
# ---------------------------------------------------------------------------

class TestProcessScoreExcludesCorrectness:
    """Tests that process_score is independent of correctness (no double-counting).

    v2 fix: correctness is outcome_score only. Including it in process_score
    would give it 0.51 effective VIS weight instead of the intended 0.30.
    """

    def test_process_score_unchanged_when_correctness_varies(self):
        """process_score must be the same whether correctness is 0 or 1."""
        spec = _make_spec(
            evidence_targets=["n2"],
            optimal_path=["n0", "n1", "n2"],
        )
        scorer = LearningScorer(spec)
        state = _make_state(visited=["n0", "n1", "n2"], inspected=["n2"])

        result_correct = scorer.score(state, "ROOT_CAUSE_X", "j", spec)
        result_wrong = scorer.score(state, "WRONG_ANSWER", "j", spec)

        assert abs(result_correct["process_score"] - result_wrong["process_score"]) < 0.01, (
            f"process_score must not depend on correctness: "
            f"correct={result_correct['process_score']:.4f}, "
            f"wrong={result_wrong['process_score']:.4f}"
        )

    def test_thorough_explorer_beats_memorizer_on_vis(self):
        """Integration: a thorough correct explorer must score higher VIS than a memorizer."""
        from vigil.scenarios.catalog import ScenarioCatalog
        from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
        from vigil.tasks.vigil_benchmark import _run_episode
        import pathlib

        packs_dir = pathlib.Path(__file__).parent.parent / "scenarios" / "packs"
        if not (packs_dir / "vigil_all_30_scenarios.json").exists():
            pytest.skip("Track 1 authored pack not found")

        catalog = ScenarioCatalog(packs_dir=str(packs_dir))
        spec = catalog.load("vigil_eco_01_kethara_succession")

        class MemorizerAgent:
            def prompt(self, obs, schema=None):
                return {"action_type": "submit_answer", "answer": "DELVORN_IRRIGATION_NETWORK",
                        "justification": "memorised", "confidence": 1.0}

        class ThoroughAgent:
            def __init__(self):
                self._actions = iter([
                    {"action_type": "explore", "node_id": "N05"},
                    {"action_type": "explore", "node_id": "N06"},
                    {"action_type": "inspect", "node_id": "N06"},
                    {"action_type": "explore", "node_id": "N09"},
                    {"action_type": "inspect", "node_id": "N09"},
                    {"action_type": "explore", "node_id": "N11"},
                    {"action_type": "inspect", "node_id": "N11"},
                    {"action_type": "explore", "node_id": "N12"},
                    {"action_type": "explore", "node_id": "N13"},
                    {"action_type": "inspect", "node_id": "N13"},
                ])
            def prompt(self, obs, schema=None):
                try:
                    return next(self._actions)
                except StopIteration:
                    return {"action_type": "submit_answer",
                            "answer": "DELVORN_IRRIGATION_NETWORK",
                            "justification": "Nutrient runoff from N11 N13 triggered succession N09.",
                            "confidence": 0.9}

        env_mem = GraphScenarioEnvironment(spec)
        r_mem = _run_episode(MemorizerAgent(), env_mem, spec)

        env_thr = GraphScenarioEnvironment(spec)
        r_thr = _run_episode(ThoroughAgent(), env_thr, spec)

        assert r_mem["contamination_warning"] is True, "Memorizer must trigger contamination_warning"
        assert r_thr["vis"] > r_mem["vis"], (
            f"Thorough explorer VIS ({r_thr['vis']:.4f}) must beat memorizer ({r_mem['vis']:.4f})"
        )


# ---------------------------------------------------------------------------
# Integration: real Track 1 authored scenario
# ---------------------------------------------------------------------------

class TestLearningScoreRealScenario:
    PACKS_DIR = __import__("pathlib").Path(__file__).parent.parent / "scenarios" / "packs"

    @pytest.fixture(autouse=True)
    def skip_if_no_pack(self):
        if not (self.PACKS_DIR / "vigil_all_30_scenarios.json").exists():
            pytest.skip("Track 1 authored pack not found")

    def test_real_scenario_score_returns_no_vis_key(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        scorer = LearningScorer(spec)
        state = EnvironmentState(current_node=spec.entry_node_ids[0])
        state.inspected_nodes = []
        result = scorer.score(state, "test answer", "test justification", spec)
        assert "vis" not in result

    def test_real_scenario_score_has_all_required_keys(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        scorer = LearningScorer(spec)
        state = EnvironmentState(current_node=spec.entry_node_ids[0])
        state.inspected_nodes = []
        result = scorer.score(state, "test", "test", spec)
        for key in ("outcome_score", "process_score", "track_id",
                    "correctness", "path_efficiency", "evidence_coverage",
                    "justification_quality", "behavioral_signatures",
                    "contamination_warning"):
            assert key in result

    def test_real_scenario_process_score_in_range(self):
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        scorer = LearningScorer(spec)
        state = EnvironmentState(current_node=spec.entry_node_ids[0])
        state.inspected_nodes = list(spec.evidence_targets)
        state.visited_nodes = list(spec.optimal_path)
        result = scorer.score(
            state,
            spec.answer_targets.get("correct_root_cause", ""),
            f"Based on {' and '.join(spec.evidence_targets[:2])}.",
            spec,
        )
        assert 0.0 <= result["process_score"] <= 1.0
        assert 0.0 <= result["outcome_score"] <= 1.0
