"""
Unit tests for the extended VISScorer.score_episode() with scorecard parameter.

Tests:
- score_episode(outcome_score=x) without scorecard produces same result as before
- score_episode(scorecard=...) uses scorecard outcome/process scores
- contamination risk is always computed even when scorecard is provided
- VIS invariant 0.3 × outcome + 0.7 × process holds in both paths
- "vis" key is present in returned dict
- track_id is included from scorecard or scenario_config
- scorecard dimension scores are merged into result
- scorecard cannot inject a "vis" key

Property 1: VIS invariant across all tracks
Property 12: Track 1 backward compatibility

Requirements: 14
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.environments.base import EnvironmentState
from vigil.scoring.vis import VISScorer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_state() -> EnvironmentState:
    return EnvironmentState(current_node="n0")


def _base_config() -> dict:
    return {
        "optimal_steps": 6,
        "cognitive_track": "learning",
        "process_weights": {
            "exploration_efficiency": 0.20,
            "learning_rate": 0.15,
            "adaptivity": 0.20,
            "recovery": 0.15,
            "stopping_quality": 0.15,
            "metacognition": 0.15,
        },
    }


def _make_scorecard(
    outcome: float = 0.8,
    process: float = 0.6,
    track_id: str = "learning",
    contamination_warning: bool = False,
) -> dict:
    return {
        "outcome_score": outcome,
        "process_score": process,
        "track_id": track_id,
        "correctness": outcome,
        "path_efficiency": 0.7,
        "evidence_coverage": 0.9,
        "justification_quality": 0.5,
        "behavioral_signatures": {},
        "contamination_warning": contamination_warning,
    }


# ---------------------------------------------------------------------------
# Backward compatibility (Property 12)
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    """Property 12: score_episode without scorecard produces same result as before."""

    def test_no_scorecard_returns_vis_key(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            outcome_score=0.8,
        )
        assert "vis" in result

    def test_no_scorecard_returns_all_7_base_dimensions(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            outcome_score=0.5,
        )
        for key in ("exploration_efficiency", "learning_rate", "adaptivity",
                    "recovery", "stopping_quality", "metacognition",
                    "contamination_risk"):
            assert key in result, f"Missing base dimension: {key}"

    def test_no_scorecard_vis_invariant(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            outcome_score=0.6,
        )
        expected_vis = 0.3 * result["outcome_score"] + 0.7 * result["process_score"]
        assert abs(result["vis"] - expected_vis) < 0.001

    def test_no_scorecard_outcome_score_matches_input(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            outcome_score=0.75,
        )
        assert result["outcome_score"] == 0.75

    def test_no_scorecard_none_outcome_defaults_to_zero(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
        )
        assert result["outcome_score"] == 0.0

    def test_no_scorecard_result_identical_to_pre_refactor(self):
        """
        Property 12: calling without scorecard must produce the same result
        as the pre-refactor implementation.
        """
        scorer = VISScorer()
        state = _make_state()
        config = _base_config()

        result1 = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=config,
            outcome_score=0.7,
        )
        result2 = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=config,
            outcome_score=0.7,
            scorecard=None,
        )
        assert result1 == result2


# ---------------------------------------------------------------------------
# Scorecard path
# ---------------------------------------------------------------------------

class TestScorecardPath:
    def test_scorecard_path_returns_vis_key(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=_make_scorecard(outcome=0.8, process=0.6),
        )
        assert "vis" in result

    def test_scorecard_outcome_score_used_directly(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=_make_scorecard(outcome=0.9, process=0.5),
        )
        assert result["outcome_score"] == 0.9

    def test_scorecard_process_score_used_directly(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=_make_scorecard(outcome=0.8, process=0.6),
        )
        assert result["process_score"] == 0.6

    def test_scorecard_vis_invariant(self):
        scorer = VISScorer()
        state = _make_state()
        scorecard = _make_scorecard(outcome=0.8, process=0.6)
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=scorecard,
        )
        expected = 0.3 * 0.8 + 0.7 * 0.6
        assert abs(result["vis"] - expected) < 0.001

    def test_scorecard_dimensions_merged_into_result(self):
        scorer = VISScorer()
        state = _make_state()
        scorecard = _make_scorecard()
        scorecard["evidence_coverage"] = 0.95
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=scorecard,
        )
        assert result.get("evidence_coverage") == 0.95

    def test_scorecard_cannot_inject_vis_key(self):
        """A scorecard with a "vis" key must not override the computed vis."""
        scorer = VISScorer()
        state = _make_state()
        scorecard = _make_scorecard(outcome=0.8, process=0.6)
        scorecard["vis"] = 99.0  # malicious injection
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=scorecard,
        )
        expected = 0.3 * 0.8 + 0.7 * 0.6
        assert abs(result["vis"] - expected) < 0.001
        assert result["vis"] != 99.0

    def test_scorecard_track_id_from_scorecard(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=_make_scorecard(track_id="metacognition"),
        )
        assert result["track_id"] == "metacognition"

    def test_scorecard_track_id_fallback_to_scenario_config(self):
        scorer = VISScorer()
        state = _make_state()
        scorecard = _make_scorecard()
        del scorecard["track_id"]
        config = dict(_base_config())
        config["cognitive_track"] = "attention"
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=config,
            scorecard=scorecard,
        )
        assert result["track_id"] == "attention"


# ---------------------------------------------------------------------------
# Contamination risk — always computed
# ---------------------------------------------------------------------------

class TestContaminationAlwaysComputed:
    def test_contamination_risk_present_without_scorecard(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            outcome_score=0.5,
        )
        assert "contamination_risk" in result

    def test_contamination_risk_present_with_scorecard(self):
        scorer = VISScorer()
        state = _make_state()
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=_make_scorecard(),
        )
        assert "contamination_risk" in result

    def test_contamination_warning_overridden_when_cr_high(self):
        """If compute_contamination_risk returns > 0.8, warning must be True."""
        scorer = VISScorer()
        state = _make_state()

        # Patch contamination_risk to return 0.9
        original = scorer.compute_contamination_risk
        scorer.compute_contamination_risk = lambda s: 0.9

        scorecard = _make_scorecard(contamination_warning=False)
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=scorecard,
        )
        assert result["contamination_warning"] is True

        scorer.compute_contamination_risk = original

    def test_contamination_warning_false_when_cr_low(self):
        scorer = VISScorer()
        state = _make_state()
        scorecard = _make_scorecard(contamination_warning=False)
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=scorecard,
        )
        # With empty state, cr should be 0.0 → warning stays False
        assert result["contamination_warning"] is False


# ---------------------------------------------------------------------------
# VIS invariant — Property 1
# ---------------------------------------------------------------------------

class TestVISInvariant:
    def test_vis_invariant_without_scorecard(self):
        scorer = VISScorer()
        state = _make_state()
        for outcome in [0.0, 0.3, 0.5, 0.8, 1.0]:
            result = scorer.score_episode(
                state=state,
                final_answer="answer",
                justification="j",
                scenario_config=_base_config(),
                outcome_score=outcome,
            )
            expected = 0.3 * result["outcome_score"] + 0.7 * result["process_score"]
            assert abs(result["vis"] - expected) < 0.001, (
                f"VIS invariant failed for outcome={outcome}: "
                f"vis={result['vis']}, expected={expected}"
            )

    def test_vis_invariant_with_scorecard(self):
        scorer = VISScorer()
        state = _make_state()
        for outcome, process in [(0.0, 0.0), (1.0, 1.0), (0.5, 0.5), (0.8, 0.3)]:
            scorecard = _make_scorecard(outcome=outcome, process=process)
            result = scorer.score_episode(
                state=state,
                final_answer="answer",
                justification="j",
                scenario_config=_base_config(),
                scorecard=scorecard,
            )
            expected = 0.3 * outcome + 0.7 * process
            assert abs(result["vis"] - expected) < 0.001, (
                f"VIS invariant failed for outcome={outcome}, process={process}"
            )

    def test_vis_clamped_to_0_1(self):
        scorer = VISScorer()
        state = _make_state()
        # Even with extreme inputs, vis must stay in [0, 1]
        scorecard = _make_scorecard(outcome=1.0, process=1.0)
        result = scorer.score_episode(
            state=state,
            final_answer="answer",
            justification="j",
            scenario_config=_base_config(),
            scorecard=scorecard,
        )
        assert 0.0 <= result["vis"] <= 1.0


# ---------------------------------------------------------------------------
# Property 1 — Hypothesis property test
# ---------------------------------------------------------------------------

@given(
    outcome=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    process=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
@settings(max_examples=100)
def test_property_1_vis_invariant_with_scorecard(outcome: float, process: float):
    """
    Property 1: VIS invariant across all tracks.
    vis = 0.3 × outcome_score + 0.7 × process_score for any scorecard.
    """
    scorer = VISScorer()
    state = _make_state()
    scorecard = _make_scorecard(outcome=outcome, process=process)
    result = scorer.score_episode(
        state=state,
        final_answer="answer",
        justification="j",
        scenario_config=_base_config(),
        scorecard=scorecard,
    )
    expected = 0.3 * outcome + 0.7 * process
    assert abs(result["vis"] - expected) < 0.001, (
        f"VIS invariant failed: vis={result['vis']}, expected={expected}"
    )


# ---------------------------------------------------------------------------
# Property 12 — Hypothesis property test
# ---------------------------------------------------------------------------

@given(outcome=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
@settings(max_examples=100)
def test_property_12_backward_compatibility(outcome: float):
    """
    Property 12: Track 1 backward compatibility.
    score_episode(outcome_score=x) without scorecard produces same result
    as before the refactor.
    """
    scorer = VISScorer()
    state = _make_state()
    config = _base_config()

    result_no_scorecard = scorer.score_episode(
        state=state,
        final_answer="answer",
        justification="j",
        scenario_config=config,
        outcome_score=outcome,
        scorecard=None,
    )
    # Must have vis key and satisfy invariant
    assert "vis" in result_no_scorecard
    expected = 0.3 * result_no_scorecard["outcome_score"] + 0.7 * result_no_scorecard["process_score"]
    assert abs(result_no_scorecard["vis"] - expected) < 0.001
    # Must have all 7 base dimensions
    for key in ("exploration_efficiency", "learning_rate", "adaptivity",
                "recovery", "stopping_quality", "metacognition"):
        assert key in result_no_scorecard
