"""
Pydantic action models for the Vigil benchmark Action API.

The model interacts with the environment through exactly four structured tools:

  explore(node_id)                          — reveal neighbors, costs 2 budget
  inspect(node_id)                          — reveal node content, costs 1 budget
  get_context()                             — current state summary, free
  submit_answer(answer, justification, confidence) — end episode, free

All four are Pydantic BaseModel subclasses discriminated by action_type.
The VigilAction union is what gets passed to llm.prompt(schema=VigilAction)
in the Kaggle SDK game loop.

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
# Union type — pass this as schema= to llm.prompt()
# ---------------------------------------------------------------------------

VigilAction = Annotated[
    Union[ExploreAction, InspectAction, GetContextAction, SubmitAnswerAction],
    Field(discriminator="action_type"),
]


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
