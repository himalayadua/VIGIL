"""
Action schema definitions.

Provides the structured action format for model interactions.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ActionType(Enum):
    """
    Types of actions available in cognitive graph environments.

    EXPAND: Move to a connected node (costs budget)
    INSPECT: Examine current node details (free)
    BACKTRACK: Return to previous node (costs budget)
    SUBMIT: Submit final answer (ends episode)
    """
    EXPAND = "expand"
    INSPECT = "inspect"
    BACKTRACK = "backtrack"
    SUBMIT = "submit"

    @classmethod
    def from_string(cls, s: str) -> Optional["ActionType"]:
        """Parse ActionType from string."""
        s = s.lower().strip()
        try:
            return cls(s)
        except ValueError:
            return None


@dataclass
class GraphAction:
    """
    Structured action for graph navigation.

    This is the primary way models interact with the cognitive environment.
    The model outputs natural language which is parsed into this structured format.

    Attributes:
        action_type: Type of action to perform
        target_node: Target node ID (for expand/inspect)
        relation_type: Relation type to follow (for expand)
        confidence: Model's confidence (0.0-1.0)
        reasoning: Optional natural language explanation

    Example:
        action = GraphAction(
            action_type=ActionType.EXPAND,
            target_node="node_5",
            relation_type="causes",
            confidence=0.8
        )
    """
    action_type: ActionType
    target_node: Optional[str] = None
    relation_type: Optional[str] = None
    confidence: float = 0.5
    reasoning: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "action_type": self.action_type.value,
            "target_node": self.target_node,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GraphAction":
        """Create from dictionary."""
        action_type = data.get("action_type")
        if isinstance(action_type, str):
            action_type = ActionType.from_string(action_type)

        return cls(
            action_type=action_type or ActionType.SUBMIT,
            target_node=data.get("target_node"),
            relation_type=data.get("relation_type"),
            confidence=data.get("confidence", 0.5),
            reasoning=data.get("reasoning", "")
        )

    def is_valid(self) -> bool:
        """
        Check if action has required fields for its type.

        Returns:
            True if action is valid.
        """
        if self.action_type == ActionType.EXPAND:
            return self.target_node is not None
        elif self.action_type == ActionType.INSPECT:
            return True  # Can inspect current node without target
        elif self.action_type == ActionType.BACKTRACK:
            return True  # Always valid
        elif self.action_type == ActionType.SUBMIT:
            return True  # Always valid
        return False
