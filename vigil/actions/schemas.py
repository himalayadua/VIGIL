"""
Pydantic action models for the Vigil benchmark Action API.

The model interacts with the environment through exactly four base tools:

  explore(node_id)                          — reveal neighbors, costs 2 budget
  inspect(node_id)                          — reveal node content, costs 1 budget
  get_context()                             — current state summary, free
  submit_answer(answer, justification, confidence) — end episode, free

Track-specific actions (not in the base set):
  ask_for_help(question, help_type)         — Track 2 (Metacognition)
  send_message(target_agent_id, content, message_type) — Track 5 (Social Cognition)
  make_commitment(target_agent_id, commitment_text, commitment_type) — Track 5

All action models are Pydantic BaseModel subclasses discriminated by action_type.

IMPORTANT: The global VigilAction union contains ALL action types and is used
by parse_action() and replay() only. It is NEVER passed directly to llm.prompt().
Use TrackActionSchema.for_track(cognitive_track) to get the per-track subset
that is safe to pass as schema= to llm.prompt().

An ACTION_PARSE_ERROR sentinel is returned by parse_action() when the LLM
output cannot be parsed into any valid action — the environment must still
append a TraversalEvent(event_type=ERROR) in that case.
"""

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Individual action models
# ---------------------------------------------------------------------------

class ExploreAction(BaseModel):
    """
    Move to a neighboring node and reveal its neighbors.

    Budget cost: 2
    Effect: sets node_id to EXPANDED, all its neighbors to at least DISCOVERED.
    """
    action_type: Literal["explore"]
    node_id: str = Field(..., description="ID of the neighbor node to move to")


class InspectAction(BaseModel):
    """
    Reveal the full content of a DISCOVERED or EXPANDED node.

    Budget cost: 1
    Effect: sets node_id to EXPANDED, may add to evidence_nodes.
    Cannot be used on UNEXPLORED nodes.
    """
    action_type: Literal["inspect"]
    node_id: str = Field(..., description="ID of the node to inspect (must not be UNEXPLORED)")


class GetContextAction(BaseModel):
    """
    Get a compressed summary of the current exploration state.

    Budget cost: 0
    Returns: current position, known graph summary, remaining budget.
    """
    action_type: Literal["get_context"]


class SubmitAnswerAction(BaseModel):
    """
    Submit a final answer and end the episode.

    Budget cost: 0
    Effect: sets episode_done = True.
    """
    action_type: Literal["submit_answer"]
    answer: str = Field(..., description="The model's answer to the hidden rule/task")
    justification: str = Field(
        ...,
        description="Explanation citing specific nodes and observations from the traversal",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model's confidence in the answer (0.0 = no confidence, 1.0 = certain)",
    )


# ---------------------------------------------------------------------------
# Track-specific action models (NOT in the base 4-action set)
# ---------------------------------------------------------------------------

class AskForHelpAction(BaseModel):
    """
    Request clarification, escalation, or a hint from the environment.

    Available in: Track 2 (metacognition) only.
    Budget cost: spec.runtime_config.action_costs.get("ask_for_help", 1)
    """
    action_type: Literal["ask_for_help"]
    question: str = Field(..., description="The question or clarification request")
    help_type: Literal["clarification", "escalation", "hint"] = Field(
        ..., description="Type of help being requested"
    )


class SendMessageAction(BaseModel):
    """
    Send a message to a social agent in the scenario.

    Available in: Track 5 (social_cognition) only.
    Budget cost: spec.runtime_config.action_costs.get("communication", 1)
    """
    action_type: Literal["send_message"]
    target_agent_id: str = Field(..., description="ID of the agent to message")
    content: str = Field(..., description="Message content")
    message_type: Literal["question", "disclosure", "assertion", "request"] = Field(
        ..., description="Type of message being sent"
    )


class MakeCommitmentAction(BaseModel):
    """
    Make a commitment (promise, refusal, or agreement) to a social agent.

    Available in: Track 5 (social_cognition) only.
    Budget cost: spec.runtime_config.action_costs.get("communication", 1)
    """
    action_type: Literal["make_commitment"]
    target_agent_id: str = Field(..., description="ID of the agent receiving the commitment")
    commitment_text: str = Field(..., description="Text of the commitment")
    commitment_type: Literal["promise", "refusal", "agreement"] = Field(
        ..., description="Type of commitment being made"
    )

VigilAction = Annotated[
    Union[
        ExploreAction, InspectAction, GetContextAction, SubmitAnswerAction,
        AskForHelpAction, SendMessageAction, MakeCommitmentAction,
    ],
    Field(discriminator="action_type"),
]


# ---------------------------------------------------------------------------
# TrackActionSchema — per-track subset for llm.prompt()
# ---------------------------------------------------------------------------

class TrackActionSchema:
    """
    Returns the per-track action schema to pass as schema= to llm.prompt().

    Track 1 (learning), Track 3 (attention), Track 4 (executive_functions):
        Base 4 actions only — unchanged from the original VigilAction.

    Track 2 (metacognition):
        Base 4 + AskForHelpAction.

    Track 5 (social_cognition):
        Base 4 + SendMessageAction + MakeCommitmentAction.

    Models never see actions irrelevant to their track.
    """

    _BASE = Annotated[
        Union[ExploreAction, InspectAction, GetContextAction, SubmitAnswerAction],
        Field(discriminator="action_type"),
    ]

    _METACOGNITION = Annotated[
        Union[
            ExploreAction, InspectAction, GetContextAction, SubmitAnswerAction,
            AskForHelpAction,
        ],
        Field(discriminator="action_type"),
    ]

    _SOCIAL = Annotated[
        Union[
            ExploreAction, InspectAction, GetContextAction, SubmitAnswerAction,
            SendMessageAction, MakeCommitmentAction,
        ],
        Field(discriminator="action_type"),
    ]

    @staticmethod
    def for_track(cognitive_track: str) -> Any:
        """
        Return the per-track action schema for llm.prompt(schema=...).

        Args:
            cognitive_track: Canonical track string, e.g. "learning".

        Returns:
            Annotated Union type appropriate for this track.
        """
        return {
            "learning":            TrackActionSchema._BASE,
            "attention":           TrackActionSchema._BASE,
            "executive_functions": TrackActionSchema._BASE,
            "metacognition":       TrackActionSchema._METACOGNITION,
            "social_cognition":    TrackActionSchema._SOCIAL,
        }.get(cognitive_track, TrackActionSchema._BASE)


# ---------------------------------------------------------------------------
# Parse error sentinel
# ---------------------------------------------------------------------------

class ActionParseError:
    """
    Returned by parse_action() when LLM output cannot be parsed.

    The environment must still append a TraversalEvent(event_type=ERROR)
    and NOT modify state or deduct budget.
    """
    def __init__(self, raw: Any, error: str):
        self.raw = raw
        self.error = error

    def __repr__(self) -> str:
        return f"ActionParseError(error={self.error!r})"


# ---------------------------------------------------------------------------
# Budget costs (used by execute_action implementations)
# ---------------------------------------------------------------------------

ACTION_BUDGET_COST: dict[str, int] = {
    "explore": 2,
    "inspect": 1,
    "get_context": 0,
    "submit_answer": 0,
}
