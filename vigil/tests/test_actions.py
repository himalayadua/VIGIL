"""
Unit tests for Pydantic action models and parser.

Tests:
- Each action type parses correctly from dict and JSON string
- SubmitAnswerAction rejects confidence outside [0.0, 1.0]
- Parser returns ActionParseError on malformed input
- Heuristic fallback handles plain-text LLM responses
- ACTION_BUDGET_COST has correct values
- VigilAction discriminated union works correctly

Requirements: 2.1, 2.9
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import pytest
from pydantic import ValidationError

from vigil.actions.schemas import (
    ACTION_BUDGET_COST,
    ActionParseError,
    ExploreAction,
    GetContextAction,
    InspectAction,
    SubmitAnswerAction,
    VigilAction,
)
from vigil.actions.parser import parse_action


# ---------------------------------------------------------------------------
# Model construction
# ---------------------------------------------------------------------------

class TestExploreAction:
    def test_valid_construction(self):
        a = ExploreAction(action_type="explore", node_id="n5")
        assert a.action_type == "explore"
        assert a.node_id == "n5"

    def test_missing_node_id_raises(self):
        with pytest.raises(ValidationError):
            ExploreAction(action_type="explore")

    def test_wrong_action_type_raises(self):
        with pytest.raises(ValidationError):
            ExploreAction(action_type="inspect", node_id="n1")


class TestInspectAction:
    def test_valid_construction(self):
        a = InspectAction(action_type="inspect", node_id="n3")
        assert a.node_id == "n3"

    def test_missing_node_id_raises(self):
        with pytest.raises(ValidationError):
            InspectAction(action_type="inspect")


class TestGetContextAction:
    def test_valid_construction(self):
        a = GetContextAction(action_type="get_context")
        assert a.action_type == "get_context"

    def test_no_extra_fields_needed(self):
        a = GetContextAction(action_type="get_context")
        assert a.model_dump() == {"action_type": "get_context"}


class TestSubmitAnswerAction:
    def test_valid_construction(self):
        a = SubmitAnswerAction(
            action_type="submit_answer",
            answer="The rule is X",
            justification="I visited n1 and n2",
            confidence=0.9,
        )
        assert a.answer == "The rule is X"
        assert a.confidence == 0.9

    def test_confidence_below_zero_raises(self):
        with pytest.raises(ValidationError):
            SubmitAnswerAction(
                action_type="submit_answer",
                answer="X",
                justification="j",
                confidence=-0.1,
            )

    def test_confidence_above_one_raises(self):
        with pytest.raises(ValidationError):
            SubmitAnswerAction(
                action_type="submit_answer",
                answer="X",
                justification="j",
                confidence=1.1,
            )

    def test_confidence_zero_is_valid(self):
        a = SubmitAnswerAction(
            action_type="submit_answer", answer="X", justification="j", confidence=0.0
        )
        assert a.confidence == 0.0

    def test_confidence_one_is_valid(self):
        a = SubmitAnswerAction(
            action_type="submit_answer", answer="X", justification="j", confidence=1.0
        )
        assert a.confidence == 1.0

    def test_missing_answer_raises(self):
        with pytest.raises(ValidationError):
            SubmitAnswerAction(
                action_type="submit_answer", justification="j", confidence=0.5
            )

    def test_missing_justification_raises(self):
        with pytest.raises(ValidationError):
            SubmitAnswerAction(
                action_type="submit_answer", answer="X", confidence=0.5
            )


# ---------------------------------------------------------------------------
# Budget costs
# ---------------------------------------------------------------------------

class TestBudgetCosts:
    def test_explore_costs_two(self):
        assert ACTION_BUDGET_COST["explore"] == 2

    def test_inspect_costs_one(self):
        assert ACTION_BUDGET_COST["inspect"] == 1

    def test_get_context_is_free(self):
        assert ACTION_BUDGET_COST["get_context"] == 0

    def test_submit_answer_is_free(self):
        assert ACTION_BUDGET_COST["submit_answer"] == 0


# ---------------------------------------------------------------------------
# parse_action — dict input
# ---------------------------------------------------------------------------

class TestParseActionFromDict:
    def test_explore_dict(self):
        result = parse_action({"action_type": "explore", "node_id": "n7"})
        assert isinstance(result, ExploreAction)
        assert result.node_id == "n7"

    def test_inspect_dict(self):
        result = parse_action({"action_type": "inspect", "node_id": "n2"})
        assert isinstance(result, InspectAction)
        assert result.node_id == "n2"

    def test_get_context_dict(self):
        result = parse_action({"action_type": "get_context"})
        assert isinstance(result, GetContextAction)

    def test_submit_answer_dict(self):
        result = parse_action({
            "action_type": "submit_answer",
            "answer": "Rule is X",
            "justification": "Visited n1",
            "confidence": 0.8,
        })
        assert isinstance(result, SubmitAnswerAction)
        assert result.confidence == 0.8

    def test_invalid_dict_returns_error(self):
        result = parse_action({"action_type": "explore"})  # missing node_id
        assert isinstance(result, ActionParseError)

    def test_unknown_action_type_returns_error(self):
        result = parse_action({"action_type": "teleport", "node_id": "n1"})
        assert isinstance(result, ActionParseError)


# ---------------------------------------------------------------------------
# parse_action — JSON string input
# ---------------------------------------------------------------------------

class TestParseActionFromJSON:
    def test_explore_json(self):
        s = json.dumps({"action_type": "explore", "node_id": "n9"})
        result = parse_action(s)
        assert isinstance(result, ExploreAction)
        assert result.node_id == "n9"

    def test_submit_json(self):
        s = json.dumps({
            "action_type": "submit_answer",
            "answer": "A",
            "justification": "B",
            "confidence": 0.5,
        })
        result = parse_action(s)
        assert isinstance(result, SubmitAnswerAction)

    def test_malformed_json_returns_error(self):
        result = parse_action("{not valid json}")
        assert isinstance(result, ActionParseError)

    def test_json_with_invalid_confidence_returns_error(self):
        s = json.dumps({
            "action_type": "submit_answer",
            "answer": "A",
            "justification": "B",
            "confidence": 2.5,
        })
        result = parse_action(s)
        assert isinstance(result, ActionParseError)


# ---------------------------------------------------------------------------
# parse_action — plain string heuristic
# ---------------------------------------------------------------------------

class TestParseActionHeuristic:
    def test_explore_colon_format(self):
        result = parse_action("explore: node_5")
        assert isinstance(result, ExploreAction)
        assert result.node_id == "node_5"

    def test_explore_space_format(self):
        result = parse_action("explore node_3")
        assert isinstance(result, ExploreAction)
        assert result.node_id == "node_3"

    def test_inspect_colon_format(self):
        result = parse_action("inspect: n1")
        assert isinstance(result, InspectAction)
        assert result.node_id == "n1"

    def test_get_context_plain(self):
        result = parse_action("get_context")
        assert isinstance(result, GetContextAction)

    def test_submit_plain(self):
        result = parse_action("submit_answer: The rule is shared features")
        assert isinstance(result, SubmitAnswerAction)
        assert "shared features" in result.answer

    def test_explore_without_node_returns_error(self):
        result = parse_action("explore")
        assert isinstance(result, ActionParseError)

    def test_inspect_without_node_returns_error(self):
        result = parse_action("inspect")
        assert isinstance(result, ActionParseError)

    def test_none_input_returns_error(self):
        result = parse_action(None)
        assert isinstance(result, ActionParseError)

    def test_empty_string_returns_error(self):
        result = parse_action("")
        assert isinstance(result, ActionParseError)

    def test_unrecognised_string_returns_error(self):
        result = parse_action("do something random")
        assert isinstance(result, ActionParseError)


# ---------------------------------------------------------------------------
# parse_action — passthrough for already-parsed models
# ---------------------------------------------------------------------------

class TestParseActionPassthrough:
    def test_explore_model_passthrough(self):
        a = ExploreAction(action_type="explore", node_id="n1")
        result = parse_action(a)
        assert result is a

    def test_submit_model_passthrough(self):
        a = SubmitAnswerAction(
            action_type="submit_answer", answer="X", justification="j", confidence=0.5
        )
        result = parse_action(a)
        assert result is a
