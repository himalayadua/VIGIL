"""
Unit tests for new action types and TrackActionSchema.

Tests:
- AskForHelpAction, SendMessageAction, MakeCommitmentAction parse from JSON dict
- TrackActionSchema.for_track() returns correct per-track subsets
- Global VigilAction union contains all 7 action types
- parse_action() handles all three new types from dict and heuristic string
- New action types are Pydantic models with correct fields

Requirements: 8
"""

import pytest

from vigil.actions.parser import parse_action
from vigil.actions.schemas import (
    ActionParseError,
    AskForHelpAction,
    ExploreAction,
    GetContextAction,
    InspectAction,
    MakeCommitmentAction,
    SendMessageAction,
    SubmitAnswerAction,
    TrackActionSchema,
    VigilAction,
)


# ---------------------------------------------------------------------------
# AskForHelpAction
# ---------------------------------------------------------------------------

class TestAskForHelpAction:
    def test_parses_from_dict(self):
        result = parse_action({
            "action_type": "ask_for_help",
            "question": "What should I inspect next?",
            "help_type": "clarification",
        })
        assert isinstance(result, AskForHelpAction)
        assert result.question == "What should I inspect next?"
        assert result.help_type == "clarification"

    def test_all_help_types_valid(self):
        for ht in ("clarification", "escalation", "hint"):
            a = AskForHelpAction(
                action_type="ask_for_help",
                question="Q",
                help_type=ht,
            )
            assert a.help_type == ht

    def test_invalid_help_type_raises(self):
        with pytest.raises(Exception):
            AskForHelpAction(
                action_type="ask_for_help",
                question="Q",
                help_type="invalid_type",
            )

    def test_action_type_literal(self):
        a = AskForHelpAction(
            action_type="ask_for_help",
            question="Q",
            help_type="hint",
        )
        assert a.action_type == "ask_for_help"

    def test_model_dump_roundtrip(self):
        a = AskForHelpAction(
            action_type="ask_for_help",
            question="What next?",
            help_type="clarification",
        )
        d = a.model_dump()
        a2 = AskForHelpAction(**d)
        assert a2.question == a.question
        assert a2.help_type == a.help_type


# ---------------------------------------------------------------------------
# SendMessageAction
# ---------------------------------------------------------------------------

class TestSendMessageAction:
    def test_parses_from_dict(self):
        result = parse_action({
            "action_type": "send_message",
            "target_agent_id": "agent_1",
            "content": "Hello, what do you know?",
            "message_type": "question",
        })
        assert isinstance(result, SendMessageAction)
        assert result.target_agent_id == "agent_1"
        assert result.content == "Hello, what do you know?"
        assert result.message_type == "question"

    def test_all_message_types_valid(self):
        for mt in ("question", "disclosure", "assertion", "request"):
            a = SendMessageAction(
                action_type="send_message",
                target_agent_id="a1",
                content="C",
                message_type=mt,
            )
            assert a.message_type == mt

    def test_invalid_message_type_raises(self):
        with pytest.raises(Exception):
            SendMessageAction(
                action_type="send_message",
                target_agent_id="a1",
                content="C",
                message_type="invalid",
            )

    def test_action_type_literal(self):
        a = SendMessageAction(
            action_type="send_message",
            target_agent_id="a1",
            content="C",
            message_type="question",
        )
        assert a.action_type == "send_message"

    def test_model_dump_roundtrip(self):
        a = SendMessageAction(
            action_type="send_message",
            target_agent_id="a1",
            content="Hello",
            message_type="disclosure",
        )
        d = a.model_dump()
        a2 = SendMessageAction(**d)
        assert a2.target_agent_id == a.target_agent_id
        assert a2.content == a.content


# ---------------------------------------------------------------------------
# MakeCommitmentAction
# ---------------------------------------------------------------------------

class TestMakeCommitmentAction:
    def test_parses_from_dict(self):
        result = parse_action({
            "action_type": "make_commitment",
            "target_agent_id": "agent_2",
            "commitment_text": "I will share the information.",
            "commitment_type": "promise",
        })
        assert isinstance(result, MakeCommitmentAction)
        assert result.target_agent_id == "agent_2"
        assert result.commitment_text == "I will share the information."
        assert result.commitment_type == "promise"

    def test_all_commitment_types_valid(self):
        for ct in ("promise", "refusal", "agreement"):
            a = MakeCommitmentAction(
                action_type="make_commitment",
                target_agent_id="a1",
                commitment_text="T",
                commitment_type=ct,
            )
            assert a.commitment_type == ct

    def test_invalid_commitment_type_raises(self):
        with pytest.raises(Exception):
            MakeCommitmentAction(
                action_type="make_commitment",
                target_agent_id="a1",
                commitment_text="T",
                commitment_type="invalid",
            )

    def test_action_type_literal(self):
        a = MakeCommitmentAction(
            action_type="make_commitment",
            target_agent_id="a1",
            commitment_text="T",
            commitment_type="agreement",
        )
        assert a.action_type == "make_commitment"

    def test_model_dump_roundtrip(self):
        a = MakeCommitmentAction(
            action_type="make_commitment",
            target_agent_id="a1",
            commitment_text="I agree",
            commitment_type="agreement",
        )
        d = a.model_dump()
        a2 = MakeCommitmentAction(**d)
        assert a2.target_agent_id == a.target_agent_id
        assert a2.commitment_text == a.commitment_text


# ---------------------------------------------------------------------------
# TrackActionSchema.for_track()
# ---------------------------------------------------------------------------

class TestTrackActionSchema:
    def test_learning_returns_base_4_actions(self):
        schema = TrackActionSchema.for_track("learning")
        assert schema is TrackActionSchema._BASE

    def test_attention_returns_base_4_actions(self):
        schema = TrackActionSchema.for_track("attention")
        assert schema is TrackActionSchema._BASE

    def test_executive_functions_returns_base_4_actions(self):
        schema = TrackActionSchema.for_track("executive_functions")
        assert schema is TrackActionSchema._BASE

    def test_metacognition_returns_5_actions(self):
        schema = TrackActionSchema.for_track("metacognition")
        assert schema is TrackActionSchema._METACOGNITION

    def test_social_cognition_returns_6_actions(self):
        schema = TrackActionSchema.for_track("social_cognition")
        assert schema is TrackActionSchema._SOCIAL

    def test_unknown_track_falls_back_to_base(self):
        schema = TrackActionSchema.for_track("unknown_track")
        assert schema is TrackActionSchema._BASE

    def test_base_schema_excludes_ask_for_help(self):
        """Track 1 models must not see AskForHelpAction."""
        from pydantic import TypeAdapter
        adapter = TypeAdapter(TrackActionSchema._BASE)
        with pytest.raises(Exception):
            adapter.validate_python({
                "action_type": "ask_for_help",
                "question": "Q",
                "help_type": "clarification",
            })

    def test_metacognition_schema_includes_ask_for_help(self):
        """Track 2 models must see AskForHelpAction."""
        from pydantic import TypeAdapter
        adapter = TypeAdapter(TrackActionSchema._METACOGNITION)
        result = adapter.validate_python({
            "action_type": "ask_for_help",
            "question": "Q",
            "help_type": "hint",
        })
        assert isinstance(result, AskForHelpAction)

    def test_social_schema_includes_send_message(self):
        """Track 5 models must see SendMessageAction."""
        from pydantic import TypeAdapter
        adapter = TypeAdapter(TrackActionSchema._SOCIAL)
        result = adapter.validate_python({
            "action_type": "send_message",
            "target_agent_id": "a1",
            "content": "Hello",
            "message_type": "question",
        })
        assert isinstance(result, SendMessageAction)

    def test_social_schema_includes_make_commitment(self):
        """Track 5 models must see MakeCommitmentAction."""
        from pydantic import TypeAdapter
        adapter = TypeAdapter(TrackActionSchema._SOCIAL)
        result = adapter.validate_python({
            "action_type": "make_commitment",
            "target_agent_id": "a1",
            "commitment_text": "T",
            "commitment_type": "promise",
        })
        assert isinstance(result, MakeCommitmentAction)

    def test_base_schema_excludes_send_message(self):
        from pydantic import TypeAdapter
        adapter = TypeAdapter(TrackActionSchema._BASE)
        with pytest.raises(Exception):
            adapter.validate_python({
                "action_type": "send_message",
                "target_agent_id": "a1",
                "content": "C",
                "message_type": "question",
            })


# ---------------------------------------------------------------------------
# Global VigilAction union
# ---------------------------------------------------------------------------

class TestVigilActionUnion:
    def test_vigil_action_accepts_ask_for_help(self):
        from pydantic import TypeAdapter
        adapter = TypeAdapter(VigilAction)
        result = adapter.validate_python({
            "action_type": "ask_for_help",
            "question": "Q",
            "help_type": "clarification",
        })
        assert isinstance(result, AskForHelpAction)

    def test_vigil_action_accepts_send_message(self):
        from pydantic import TypeAdapter
        adapter = TypeAdapter(VigilAction)
        result = adapter.validate_python({
            "action_type": "send_message",
            "target_agent_id": "a1",
            "content": "C",
            "message_type": "question",
        })
        assert isinstance(result, SendMessageAction)

    def test_vigil_action_accepts_make_commitment(self):
        from pydantic import TypeAdapter
        adapter = TypeAdapter(VigilAction)
        result = adapter.validate_python({
            "action_type": "make_commitment",
            "target_agent_id": "a1",
            "commitment_text": "T",
            "commitment_type": "agreement",
        })
        assert isinstance(result, MakeCommitmentAction)

    def test_vigil_action_still_accepts_original_4(self):
        from pydantic import TypeAdapter
        adapter = TypeAdapter(VigilAction)
        for data in [
            {"action_type": "explore", "node_id": "n1"},
            {"action_type": "inspect", "node_id": "n1"},
            {"action_type": "get_context"},
            {"action_type": "submit_answer", "answer": "A", "justification": "J", "confidence": 0.8},
        ]:
            result = adapter.validate_python(data)
            assert result is not None


# ---------------------------------------------------------------------------
# parse_action() with new types
# ---------------------------------------------------------------------------

class TestParseActionNewTypes:
    def test_parse_ask_for_help_from_dict(self):
        result = parse_action({
            "action_type": "ask_for_help",
            "question": "What next?",
            "help_type": "hint",
        })
        assert isinstance(result, AskForHelpAction)

    def test_parse_send_message_from_dict(self):
        result = parse_action({
            "action_type": "send_message",
            "target_agent_id": "a1",
            "content": "Hello",
            "message_type": "disclosure",
        })
        assert isinstance(result, SendMessageAction)

    def test_parse_make_commitment_from_dict(self):
        result = parse_action({
            "action_type": "make_commitment",
            "target_agent_id": "a1",
            "commitment_text": "I agree",
            "commitment_type": "agreement",
        })
        assert isinstance(result, MakeCommitmentAction)

    def test_parse_ask_for_help_from_json_string(self):
        import json
        data = {
            "action_type": "ask_for_help",
            "question": "Help me",
            "help_type": "escalation",
        }
        result = parse_action(json.dumps(data))
        assert isinstance(result, AskForHelpAction)

    def test_parse_send_message_from_json_string(self):
        import json
        data = {
            "action_type": "send_message",
            "target_agent_id": "a1",
            "content": "C",
            "message_type": "request",
        }
        result = parse_action(json.dumps(data))
        assert isinstance(result, SendMessageAction)

    def test_parse_already_instantiated_ask_for_help(self):
        a = AskForHelpAction(
            action_type="ask_for_help",
            question="Q",
            help_type="clarification",
        )
        result = parse_action(a)
        assert result is a

    def test_parse_already_instantiated_send_message(self):
        a = SendMessageAction(
            action_type="send_message",
            target_agent_id="a1",
            content="C",
            message_type="question",
        )
        result = parse_action(a)
        assert result is a

    def test_parse_already_instantiated_make_commitment(self):
        a = MakeCommitmentAction(
            action_type="make_commitment",
            target_agent_id="a1",
            commitment_text="T",
            commitment_type="promise",
        )
        result = parse_action(a)
        assert result is a

    def test_parse_heuristic_ask_for_help(self):
        result = parse_action("ask_for_help What should I do next?")
        assert isinstance(result, AskForHelpAction)

    def test_original_4_actions_still_parse(self):
        """Backward compat: original 4 action types must still parse."""
        assert isinstance(parse_action({"action_type": "explore", "node_id": "n1"}), ExploreAction)
        assert isinstance(parse_action({"action_type": "inspect", "node_id": "n1"}), InspectAction)
        assert isinstance(parse_action({"action_type": "get_context"}), GetContextAction)
        assert isinstance(parse_action({
            "action_type": "submit_answer",
            "answer": "A",
            "justification": "J",
            "confidence": 0.8,
        }), SubmitAnswerAction)
