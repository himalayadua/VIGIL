"""
Base abstract class for all cognitive environments.

Defines the interface that all Track 1 (Learning) scenarios must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class ActionType(Enum):
    """Types of actions available in the graph environment."""
    EXPAND = "expand"
    INSPECT = "inspect"
    BACKTRACK = "backtrack"
    SUBMIT = "submit"


@dataclass
class GraphAction:
    """
    Structured action schema for model interactions.

    Attributes:
        action_type: The type of action to perform
        target_node: ID of the target node (for expand/inspect)
        relation_type: Type of relation to follow (for expand)
        confidence: Model's confidence in its action (0.0-1.0)
        reasoning: Optional natural language reasoning
    """
    action_type: ActionType
    target_node: Optional[str] = None
    relation_type: Optional[str] = None
    confidence: float = 0.5
    reasoning: str = ""


@dataclass
class EnvironmentState:
    """
    Encapsulates all state for one exploration episode.

    This state is serialized to run.json automatically by Kaggle SDK.

    Attributes:
        current_node: ID of the current node
        visited_nodes: List of visited node IDs
        expanded_edges: List of edge expansions made
        budget_remaining: Remaining action budget
        evidence_nodes: List of nodes marked as evidence
        action_history: History of actions taken
        confidence_history: History of confidence values
    """
    current_node: str
    visited_nodes: List[str] = field(default_factory=list)
    expanded_edges: List[Dict[str, Any]] = field(default_factory=list)
    budget_remaining: int = 10
    evidence_nodes: List[str] = field(default_factory=list)
    action_history: List[GraphAction] = field(default_factory=list)
    confidence_history: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for JSON serialization."""
        return {
            "current_node": self.current_node,
            "visited_nodes": self.visited_nodes,
            "expanded_edges": self.expanded_edges,
            "budget_remaining": self.budget_remaining,
            "evidence_nodes": self.evidence_nodes,
            "action_history": [
                {
                    "type": a.action_type.value,
                    "target": a.target_node,
                    "relation": a.relation_type,
                    "confidence": a.confidence,
                    "reasoning": a.reasoning
                }
                for a in self.action_history
            ],
            "confidence_trajectory": self.confidence_history
        }


class CognitiveEnvironment(ABC):
    """
    Abstract base class for all cognitive graph environments.

    All cognitive ability tests (Learning, Metacognition, etc.) must
    implement this interface to be compatible with the Vigil framework.

    The environment is responsible for:
    - Generating/loading the graph structure
    - Managing exploration state
    - Executing model actions
    - Scoring the exploration episode
    """

    @abstractmethod
    def __init__(self, scenario_config: Dict[str, Any]):
        """
        Initialize the environment with a scenario configuration.

        Args:
            scenario_config: Dictionary containing scenario parameters
                loaded from JSON scenario files.
        """
        pass

    @abstractmethod
    def reset(self) -> EnvironmentState:
        """
        Reset environment to initial state.

        Returns:
            Fresh EnvironmentState for a new episode.
        """
        pass

    @abstractmethod
    def get_available_actions(self, state: EnvironmentState) -> str:
        """
        Generate human-readable menu of available actions.

        Args:
            state: Current environment state

        Returns:
            Formatted string describing available actions.
        """
        pass

    @abstractmethod
    def execute_action(
        self,
        state: EnvironmentState,
        action: GraphAction
    ) -> Tuple[bool, str]:
        """
        Execute an action and return result.

        Args:
            state: Current environment state
            action: Action to execute

        Returns:
            Tuple of (success: bool, observation: str)
        """
        pass

    @abstractmethod
    def score_exploration(
        self,
        state: EnvironmentState,
        final_answer: str
    ) -> Dict[str, float]:
        """
        Score the complete exploration episode.

        Args:
            state: Final environment state after exploration
            final_answer: Model's submitted answer

        Returns:
            Dictionary mapping metric names to scores.
            Expected keys: correctness, efficiency, evidence_quality,
            calibration, recovery, final_score
        """
        pass

    @abstractmethod
    def verify_rule(self, answer: str) -> bool:
        """
        Verify if submitted answer matches the hidden rule.

        Args:
            answer: Model's submitted answer string

        Returns:
            True if answer correctly identifies the rule.
        """
        pass

    def get_scenario_info(self) -> Dict[str, str]:
        """
        Return metadata about this scenario.

        Returns:
            Dictionary with scenario_id, cognitive_track, sub_ability, etc.
        """
        return {
            "scenario_id": getattr(self, '_scenario_id', 'unknown'),
            "cognitive_track": getattr(self, '_cognitive_track', 'unknown'),
            "sub_ability": getattr(self, '_sub_ability', 'unknown')
        }
