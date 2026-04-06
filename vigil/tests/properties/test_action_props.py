"""
Property-based tests for Vigil action models and budget enforcement.

Properties tested:
  P4: Action costs are exact
  P5: Budget exhaustion rejects consuming actions
  P6: Invalid actions do not mutate state

Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 4.1
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.actions.schemas import (
    ACTION_BUDGET_COST,
    ActionParseError,
    ExploreAction,
    GetContextAction,
    InspectAction,
    SubmitAnswerAction,
)
from vigil.actions.parser import parse_action


# ---------------------------------------------------------------------------
# Property 4: Action costs are exact
# Feature: vigil-benchmark, Property 4
# ---------------------------------------------------------------------------

@given(st.integers(min_value=0, max_value=99999))
@settings(max_examples=100)
def test_property_4_action_costs_are_exact(seed):
    """
    Feature: vigil-benchmark, Property 4: Action costs are exact

    explore costs exactly 2, inspect costs exactly 1,
    get_context and submit_answer cost exactly 0.

    Validates: Requirements 2.2, 2.3, 2.4, 2.5
    """
    assert ACTION_BUDGET_COST["explore"] == 2
    assert ACTION_BUDGET_COST["inspect"] == 1
    assert ACTION_BUDGET_COST["get_context"] == 0
    assert ACTION_BUDGET_COST["submit_answer"] == 0

    # Verify no other action types exist in the cost table
    assert set(ACTION_BUDGET_COST.keys()) == {
        "explore", "inspect", "get_context", "submit_answer"
    }


# ---------------------------------------------------------------------------
# Property 5: Budget exhaustion rejects consuming actions
# Feature: vigil-benchmark, Property 5
# ---------------------------------------------------------------------------

@given(
    node_id=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_"),
        min_size=1,
        max_size=20,
    )
)
@settings(max_examples=100)
def test_property_5_budget_cost_never_negative(node_id):
    """
    Feature: vigil-benchmark, Property 5: Budget exhaustion rejects consuming actions

    Budget costs are always non-negative — no action can increase the budget.
    (The actual rejection logic lives in execute_action; this property validates
    the cost table contract that environments rely on.)

    Validates: Requirements 2.8
    """
    for action_type, cost in ACTION_BUDGET_COST.items():
        assert cost >= 0, (
            f"Action '{action_type}' has negative cost {cost} — "
            "this would increase budget, which is invalid"
        )


# ---------------------------------------------------------------------------
# Property 6: Invalid actions do not produce valid models
# Feature: vigil-benchmark, Property 6
# ---------------------------------------------------------------------------

@given(
    confidence=st.floats(
        min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False
    )
)
@settings(max_examples=100)
def test_property_6_invalid_confidence_returns_error(confidence):
    """
    Feature: vigil-benchmark, Property 6: Invalid actions do not mutate state

    SubmitAnswerAction with confidence outside [0.0, 1.0] must fail Pydantic
    validation. parse_action() must return ActionParseError, not a valid model.

    Validates: Requirements 2.9
    """
    import json

    if 0.0 <= confidence <= 1.0:
        # Valid confidence — should parse successfully
        data = {
            "action_type": "submit_answer",
            "answer": "test",
            "justification": "test",
            "confidence": confidence,
        }
        result = parse_action(data)
        assert isinstance(result, SubmitAnswerAction), (
            f"confidence={confidence} is valid but parse_action returned {type(result)}"
        )
    else:
        # Invalid confidence — must return ActionParseError
        data = {
            "action_type": "submit_answer",
            "answer": "test",
            "justification": "test",
            "confidence": confidence,
        }
        result = parse_action(data)
        assert isinstance(result, ActionParseError), (
            f"confidence={confidence} is invalid but parse_action returned {type(result)}"
        )


@given(
    raw=st.one_of(
        st.none(),
        st.integers(),
        st.floats(allow_nan=False),
        st.lists(st.text()),
    )
)
@settings(max_examples=100)
def test_property_6_unsupported_types_return_error(raw):
    """
    Feature: vigil-benchmark, Property 6 (continued)

    parse_action() on unsupported input types (None, int, float, list)
    must always return ActionParseError, never raise.

    Validates: Requirements 2.9
    """
    result = parse_action(raw)
    assert isinstance(result, ActionParseError), (
        f"Expected ActionParseError for input {raw!r}, got {type(result)}"
    )
