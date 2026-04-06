"""
Property-based tests for task loop invariants and observation token budget.

Properties tested:
  P16: Budget exhaustion returns 0.0
  P17: Hard 20-turn cap
  P18: Observation token budget

Requirements: 17.7, 17.8, 20.1, 20.4, 20.5
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.environments.concept_formation import ConceptFormationEnv
from vigil.scenarios.loader import ScenarioLoader
from vigil.tasks.track1_learning import _run_episode

_LOADER = ScenarioLoader()

_SCENARIO = {
    "scenario_id": "prop_test",
    "cognitive_track": "learning",
    "sub_ability": "concept_formation",
    "hidden_rule": {
        "type": "category_by_core_features",
        "description": "Nodes share core features",
        "verification_pattern": ["core features", "category"],
    },
    "scoring_weights": {"correctness": 0.5, "efficiency": 0.2, "evidence_quality": 0.2, "calibration": 0.1},
    "difficulty_levels": {
        "1": {"num_nodes": 6, "num_categories": 2, "features_per_node": 3, "core_features_per_category": 2, "feature_pool_size": 20},
    },
    "budget": {"base": 20},
    "optimal_steps": 6,
}


class NeverSubmitLLM:
    """LLM that always calls get_context — never submits."""
    def __init__(self):
        self.call_count = 0

    def prompt(self, obs, schema=None):
        self.call_count += 1
        return {"action_type": "get_context"}


class ImmediateSubmitLLM:
    """LLM that submits on the first turn."""
    def prompt(self, obs, schema=None):
        return {
            "action_type": "submit_answer",
            "answer": "test",
            "justification": "test",
            "confidence": 0.5,
        }


# ---------------------------------------------------------------------------
# Property 16: Budget exhaustion returns 0.0
# Feature: vigil-benchmark, Property 16
# ---------------------------------------------------------------------------

@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=50)
def test_property_16_no_submit_returns_zero(seed):
    """
    Feature: vigil-benchmark, Property 16: Budget exhaustion returns 0.0

    When the episode ends without a submit_answer call (either budget
    exhausted or 20-turn cap hit), _run_episode returns 0.0.

    Validates: Requirements 17.7
    """
    env = ConceptFormationEnv(scenario_config=_SCENARIO, difficulty=1, seed=seed)
    llm = NeverSubmitLLM()
    result = _run_episode(llm, env)
    assert result == 0.0, (
        f"seed={seed}: expected 0.0 when no submit, got {result}"
    )


# ---------------------------------------------------------------------------
# Property 17: Hard 20-turn cap
# Feature: vigil-benchmark, Property 17
# ---------------------------------------------------------------------------

@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=50)
def test_property_17_hard_20_turn_cap(seed):
    """
    Feature: vigil-benchmark, Property 17: Hard 20-turn cap

    The game loop terminates after at most 20 iterations of llm.prompt,
    regardless of remaining budget.

    Validates: Requirements 17.8
    """
    env = ConceptFormationEnv(scenario_config=_SCENARIO, difficulty=1, seed=seed)
    llm = NeverSubmitLLM()
    _run_episode(llm, env)
    assert llm.call_count <= 20, (
        f"seed={seed}: llm.prompt called {llm.call_count} times, expected ≤ 20"
    )


# ---------------------------------------------------------------------------
# Property 18: Observation token budget
# Feature: vigil-benchmark, Property 18
# ---------------------------------------------------------------------------

@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=100)
def test_property_18_observation_token_budget(seed):
    """
    Feature: vigil-benchmark, Property 18: Observation token budget

    render(state) produces a string whose approximate token count does not
    exceed max_observation_tokens (default 500).

    We approximate tokens as words (conservative: 1 token ≈ 0.75 words).
    500 tokens ≈ 375 words.

    Validates: Requirements 20.1, 20.5
    """
    from vigil.environments.base import EnvironmentState, EventType, TraversalEvent

    env = ConceptFormationEnv(scenario_config=_SCENARIO, difficulty=1, seed=seed)
    state = env.reset()

    # Test render with short history
    obs_short = env.render(state)
    word_count_short = len(obs_short.split())
    assert word_count_short <= 375, (
        f"seed={seed}: short history render has {word_count_short} words, expected ≤ 375"
    )

    # Add 16+ events to trigger compressed history (Req 20.4)
    for i in range(16):
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.EXPLORE,
            observation="test",
            node_id=f"n{i}",
        ))

    obs_long = env.render(state)
    word_count_long = len(obs_long.split())
    assert word_count_long <= 375, (
        f"seed={seed}: long history render has {word_count_long} words, expected ≤ 375"
    )

    # Compressed history should be shorter than if we listed all 16 events
    assert "Compressed" in obs_long or len(obs_long) <= len(obs_short) * 3, (
        f"seed={seed}: long history render should use compressed summary"
    )
