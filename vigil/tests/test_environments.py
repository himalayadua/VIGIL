"""
Unit tests for EnvironmentState new fields and EventType additions.

Requirements: 6, 7 (Task 9)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from vigil.actions.schemas import (
    ExploreAction, GetContextAction, InspectAction, SubmitAnswerAction,
)

# ---------------------------------------------------------------------------
# Task 9: EnvironmentState new fields and EventType additions
# ---------------------------------------------------------------------------

from vigil.environments.base import EventType, EnvironmentState


class TestEnvironmentStateNewFields:
    """Test all new EnvironmentState fields initialize to empty and serialize."""

    def test_discovered_nodes_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.discovered_nodes == []

    def test_inspected_nodes_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.inspected_nodes == []

    def test_disconfirmation_hits_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.disconfirmation_hits == []

    def test_dead_end_hits_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.dead_end_hits == []

    def test_track_state_defaults_empty_dict(self):
        state = EnvironmentState(current_node="n0")
        assert state.track_state == {}

    def test_contradiction_events_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.contradiction_events == []

    def test_relevance_shifts_triggered_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.relevance_shifts_triggered == []

    def test_completed_subgoals_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.completed_subgoals == []

    def test_constraint_violations_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.constraint_violations == []

    def test_help_requests_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.help_requests == []

    def test_source_claims_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.source_claims == []

    def test_confidence_checkpoints_defaults_empty_dict(self):
        state = EnvironmentState(current_node="n0")
        assert state.confidence_checkpoints == {}

    def test_commitments_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.commitments == []

    def test_messages_sent_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.messages_sent == []

    def test_partner_model_updates_defaults_empty(self):
        state = EnvironmentState(current_node="n0")
        assert state.partner_model_updates == []

    def test_to_dict_contains_discovered_nodes(self):
        state = EnvironmentState(current_node="n0")
        state.discovered_nodes = ["n1", "n2"]
        d = state.to_dict()
        assert d["discovered_nodes"] == ["n1", "n2"]

    def test_to_dict_contains_inspected_nodes(self):
        state = EnvironmentState(current_node="n0")
        state.inspected_nodes = ["n1"]
        d = state.to_dict()
        assert d["inspected_nodes"] == ["n1"]

    def test_to_dict_contains_disconfirmation_hits(self):
        state = EnvironmentState(current_node="n0")
        state.disconfirmation_hits = ["n3"]
        d = state.to_dict()
        assert d["disconfirmation_hits"] == ["n3"]

    def test_to_dict_contains_dead_end_hits(self):
        state = EnvironmentState(current_node="n0")
        state.dead_end_hits = ["n4"]
        d = state.to_dict()
        assert d["dead_end_hits"] == ["n4"]

    def test_to_dict_contains_track_state(self):
        state = EnvironmentState(current_node="n0")
        state.track_state = {"key": "value"}
        d = state.to_dict()
        assert d["track_state"] == {"key": "value"}

    def test_to_dict_contains_contradiction_events(self):
        state = EnvironmentState(current_node="n0")
        state.contradiction_events = [{"type": "contradiction"}]
        d = state.to_dict()
        assert len(d["contradiction_events"]) == 1

    def test_to_dict_contains_relevance_shifts_triggered(self):
        state = EnvironmentState(current_node="n0")
        state.relevance_shifts_triggered = [{"shift_at_step": 3}]
        d = state.to_dict()
        assert d["relevance_shifts_triggered"] == [{"shift_at_step": 3}]

    def test_to_dict_contains_completed_subgoals(self):
        state = EnvironmentState(current_node="n0")
        state.completed_subgoals = ["sg1"]
        d = state.to_dict()
        assert d["completed_subgoals"] == ["sg1"]

    def test_to_dict_contains_constraint_violations(self):
        state = EnvironmentState(current_node="n0")
        state.constraint_violations = [{"constraint": "step_budget"}]
        d = state.to_dict()
        assert d["constraint_violations"] == [{"constraint": "step_budget"}]

    def test_to_dict_contains_help_requests(self):
        state = EnvironmentState(current_node="n0")
        state.help_requests = [{"question": "What next?"}]
        d = state.to_dict()
        assert d["help_requests"] == [{"question": "What next?"}]

    def test_to_dict_contains_source_claims(self):
        state = EnvironmentState(current_node="n0")
        state.source_claims = [{"node_id": "n1", "claimed_source": "observation"}]
        d = state.to_dict()
        assert len(d["source_claims"]) == 1

    def test_to_dict_contains_confidence_checkpoints(self):
        state = EnvironmentState(current_node="n0")
        state.confidence_checkpoints = {"before_submission": [{"step": 5, "confidence": 0.8}]}
        d = state.to_dict()
        assert "before_submission" in d["confidence_checkpoints"]

    def test_to_dict_contains_commitments(self):
        state = EnvironmentState(current_node="n0")
        state.commitments = [{"target": "agent_1", "type": "promise"}]
        d = state.to_dict()
        assert d["commitments"] == [{"target": "agent_1", "type": "promise"}]

    def test_to_dict_contains_messages_sent(self):
        state = EnvironmentState(current_node="n0")
        state.messages_sent = [{"content": "Hello", "target": "agent_1"}]
        d = state.to_dict()
        assert len(d["messages_sent"]) == 1

    def test_to_dict_contains_partner_model_updates(self):
        state = EnvironmentState(current_node="n0")
        state.partner_model_updates = [{"agent_id": "a1", "inferred_belief": "cooperative"}]
        d = state.to_dict()
        assert len(d["partner_model_updates"]) == 1

    def test_to_dict_all_new_fields_present(self):
        """All new fields must appear in to_dict() output."""
        state = EnvironmentState(current_node="n0")
        d = state.to_dict()
        new_fields = [
            "discovered_nodes", "inspected_nodes", "disconfirmation_hits",
            "dead_end_hits", "track_state", "contradiction_events",
            "relevance_shifts_triggered", "completed_subgoals",
            "constraint_violations", "help_requests", "source_claims",
            "confidence_checkpoints", "commitments", "messages_sent",
            "partner_model_updates",
        ]
        for field in new_fields:
            assert field in d, f"Missing field in to_dict(): {field}"


class TestEventTypeNewValues:
    """Test new system EventType values are present and correctly named."""

    def test_contradiction_event_type_exists(self):
        assert EventType.CONTRADICTION.value == "contradiction"

    def test_relevance_shift_event_type_exists(self):
        assert EventType.RELEVANCE_SHIFT.value == "relevance_shift"

    def test_subgoal_complete_event_type_exists(self):
        assert EventType.SUBGOAL_COMPLETE.value == "subgoal_complete"

    def test_replan_triggered_event_type_exists(self):
        assert EventType.REPLAN_TRIGGERED.value == "replan_triggered"

    def test_constraint_violated_event_type_exists(self):
        assert EventType.CONSTRAINT_VIOLATED.value == "constraint_violated"

    def test_help_requested_event_type_exists(self):
        assert EventType.HELP_REQUESTED.value == "help_requested"

    def test_message_sent_event_type_exists(self):
        assert EventType.MESSAGE_SENT.value == "message_sent"

    def test_commitment_made_event_type_exists(self):
        assert EventType.COMMITMENT_MADE.value == "commitment_made"

    def test_original_event_types_still_present(self):
        """Original EventType values must not be removed."""
        for name in ("EXPLORE", "INSPECT", "GET_CONTEXT", "SUBMIT_ANSWER", "ERROR"):
            assert hasattr(EventType, name), f"Missing original EventType: {name}"

    def test_system_events_have_distinct_values(self):
        system_events = [
            EventType.CONTRADICTION, EventType.RELEVANCE_SHIFT,
            EventType.SUBGOAL_COMPLETE, EventType.REPLAN_TRIGGERED,
            EventType.CONSTRAINT_VIOLATED, EventType.HELP_REQUESTED,
            EventType.MESSAGE_SENT, EventType.COMMITMENT_MADE,
        ]
        values = [e.value for e in system_events]
        assert len(values) == len(set(values)), "System event values must be unique"
