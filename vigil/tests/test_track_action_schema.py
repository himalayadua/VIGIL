"""
Unit tests for TrackActionSchema.for_track() per-track subsets.

Tests:
- All five cognitive_track values return correct schema
- Unknown track falls back to base 4 actions
- Base schema rejects track-specific actions
- Track-specific schemas accept their designated actions

Requirements: 8
"""

import pytest
from pydantic import TypeAdapter

from vigil.actions.schemas import (
    AskForHelpAction,
    ExploreAction,
    MakeCommitmentAction,
    SendMessageAction,
    TrackActionSchema,
)


class TestTrackActionSchemaAllTracks:
    """Test all five cognitive_track values return the correct schema."""

    def test_learning_is_base(self):
        assert TrackActionSchema.for_track("learning") is TrackActionSchema._BASE

    def test_metacognition_is_metacognition_schema(self):
        assert TrackActionSchema.for_track("metacognition") is TrackActionSchema._METACOGNITION

    def test_attention_is_base(self):
        assert TrackActionSchema.for_track("attention") is TrackActionSchema._BASE

    def test_executive_functions_is_base(self):
        assert TrackActionSchema.for_track("executive_functions") is TrackActionSchema._BASE

    def test_social_cognition_is_social_schema(self):
        assert TrackActionSchema.for_track("social_cognition") is TrackActionSchema._SOCIAL

    def test_unknown_track_falls_back_to_base(self):
        assert TrackActionSchema.for_track("unknown") is TrackActionSchema._BASE

    def test_empty_string_falls_back_to_base(self):
        assert TrackActionSchema.for_track("") is TrackActionSchema._BASE


class TestBaseSchemaRejectsTrackSpecific:
    """Base schema must reject all three track-specific action types."""

    def test_base_rejects_ask_for_help(self):
        adapter = TypeAdapter(TrackActionSchema._BASE)
        with pytest.raises(Exception):
            adapter.validate_python({
                "action_type": "ask_for_help",
                "question": "Q",
                "help_type": "clarification",
            })

    def test_base_rejects_send_message(self):
        adapter = TypeAdapter(TrackActionSchema._BASE)
        with pytest.raises(Exception):
            adapter.validate_python({
                "action_type": "send_message",
                "target_agent_id": "a1",
                "content": "C",
                "message_type": "question",
            })

    def test_base_rejects_make_commitment(self):
        adapter = TypeAdapter(TrackActionSchema._BASE)
        with pytest.raises(Exception):
            adapter.validate_python({
                "action_type": "make_commitment",
                "target_agent_id": "a1",
                "commitment_text": "T",
                "commitment_type": "promise",
            })

    def test_base_accepts_explore(self):
        adapter = TypeAdapter(TrackActionSchema._BASE)
        result = adapter.validate_python({"action_type": "explore", "node_id": "n1"})
        assert isinstance(result, ExploreAction)


class TestMetacognitionSchemaAcceptsAskForHelp:
    def test_metacognition_accepts_ask_for_help(self):
        adapter = TypeAdapter(TrackActionSchema._METACOGNITION)
        result = adapter.validate_python({
            "action_type": "ask_for_help",
            "question": "What should I verify?",
            "help_type": "hint",
        })
        assert isinstance(result, AskForHelpAction)

    def test_metacognition_rejects_send_message(self):
        adapter = TypeAdapter(TrackActionSchema._METACOGNITION)
        with pytest.raises(Exception):
            adapter.validate_python({
                "action_type": "send_message",
                "target_agent_id": "a1",
                "content": "C",
                "message_type": "question",
            })

    def test_metacognition_rejects_make_commitment(self):
        adapter = TypeAdapter(TrackActionSchema._METACOGNITION)
        with pytest.raises(Exception):
            adapter.validate_python({
                "action_type": "make_commitment",
                "target_agent_id": "a1",
                "commitment_text": "T",
                "commitment_type": "promise",
            })


class TestSocialSchemaAcceptsBothSocialActions:
    def test_social_accepts_send_message(self):
        adapter = TypeAdapter(TrackActionSchema._SOCIAL)
        result = adapter.validate_python({
            "action_type": "send_message",
            "target_agent_id": "agent_1",
            "content": "Hello",
            "message_type": "disclosure",
        })
        assert isinstance(result, SendMessageAction)

    def test_social_accepts_make_commitment(self):
        adapter = TypeAdapter(TrackActionSchema._SOCIAL)
        result = adapter.validate_python({
            "action_type": "make_commitment",
            "target_agent_id": "agent_1",
            "commitment_text": "I will cooperate",
            "commitment_type": "agreement",
        })
        assert isinstance(result, MakeCommitmentAction)

    def test_social_rejects_ask_for_help(self):
        adapter = TypeAdapter(TrackActionSchema._SOCIAL)
        with pytest.raises(Exception):
            adapter.validate_python({
                "action_type": "ask_for_help",
                "question": "Q",
                "help_type": "clarification",
            })

    def test_social_accepts_base_actions(self):
        adapter = TypeAdapter(TrackActionSchema._SOCIAL)
        result = adapter.validate_python({"action_type": "explore", "node_id": "n1"})
        assert isinstance(result, ExploreAction)
