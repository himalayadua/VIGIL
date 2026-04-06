"""
Base abstract class and core state types for all cognitive environments.

Defines:
- EventType: Enum of all action types that produce TraversalEvents
- TraversalEvent: Immutable record of a single agent action and its outcome
- EnvironmentState: Mutable session state, fully reconstructable from events
- CognitiveEnvironment: Abstract base class all environments implement
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class EventType(Enum):
    """All action types that produce a TraversalEvent."""
    EXPLORE = "explore"
    INSPECT = "inspect"
    GET_CONTEXT = "get_context"
    SUBMIT_ANSWER = "submit_answer"
    ERROR = "error"


@dataclass
class TraversalEvent:
    """
    Immutable record of a single agent action and its outcome.

    Every action — including failed ones — produces exactly one TraversalEvent.
    The full episode trajectory is the ordered list of these events.

    Attributes:
        timestamp: Unix timestamp when the action was executed
        event_type: Which action was taken
        node_id: Target node (None for get_context, submit_answer, errors)
        params: Raw action parameters as received
        observation: Text observation returned to the model
        state_delta: Changes applied to EnvironmentState:
            - budget_delta (int): how much budget was deducted (0 or negative)
            - visibility_changes (dict[str, str]): node_id -> new visibility value
            - evidence_added (list[str]): node IDs added to evidence_nodes
            - episode_done (bool): whether this action ended the episode
    """
    timestamp: float
    event_type: EventType
    node_id: Optional[str]
    params: Dict[str, Any]
    observation: str
    state_delta: Dict[str, Any]

    @classmethod
    def make(
        cls,
        event_type: EventType,
        observation: str,
        node_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        budget_delta: int = 0,
        visibility_changes: Optional[Dict[str, str]] = None,
        evidence_added: Optional[List[str]] = None,
        episode_done: bool = False,
    ) -> "TraversalEvent":
        """Convenience constructor with sensible defaults."""
        return cls(
            timestamp=time.time(),
            event_type=event_type,
            node_id=node_id,
            params=params or {},
            observation=observation,
            state_delta={
                "budget_delta": budget_delta,
                "visibility_changes": visibility_changes or {},
                "evidence_added": evidence_added or [],
                "episode_done": episode_done,
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "node_id": self.node_id,
            "params": self.params,
            "observation": self.observation,
            "state_delta": self.state_delta,
        }


@dataclass
class EnvironmentState:
    """
    Mutable session state for one exploration episode.

    All fields are updated by CognitiveEnvironment.execute_action().
    The full state is always reconstructable by replaying action_history.

    Attributes:
        current_node: ID of the node the model is currently at
        visited_nodes: Ordered list of node IDs the model has moved to
        budget_remaining: Remaining action budget (explore costs 2, inspect costs 1)
        evidence_nodes: Node IDs that are relevant to the hidden rule (populated on inspect)
        action_history: Complete ordered list of every TraversalEvent in this episode
        confidence_history: Confidence values from submit_answer calls
        episode_done: True once submit_answer is called or budget exhausted
        cumulative_reward: Running reward total (used by ReinforcementLearningEnv)
        trial_move_counts: Move count per trial (used by ProceduralLearningEnv)
    """
    current_node: str
    visited_nodes: List[str] = field(default_factory=list)
    budget_remaining: int = 10
    evidence_nodes: List[str] = field(default_factory=list)
    action_history: List[TraversalEvent] = field(default_factory=list)
    confidence_history: List[float] = field(default_factory=list)
    episode_done: bool = False
    cumulative_reward: float = 0.0
    trial_move_counts: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for JSON serialization."""
        return {
            "current_node": self.current_node,
            "visited_nodes": self.visited_nodes,
            "budget_remaining": self.budget_remaining,
            "evidence_nodes": self.evidence_nodes,
            "action_history": [e.to_dict() for e in self.action_history],
            "confidence_history": self.confidence_history,
            "episode_done": self.episode_done,
            "cumulative_reward": self.cumulative_reward,
            "trial_move_counts": self.trial_move_counts,
        }


class CognitiveEnvironment(ABC):
    """
    Abstract base class for all cognitive graph environments.

    Subclasses implement the six learning sub-ability environments.
    All environments share the same action API and state management contract.

    Contract:
    - execute_action() MUST append exactly one TraversalEvent to state.action_history
      for every call, including failed/invalid actions.
    - execute_action() MUST NOT call env.reset() internally.
    - render() MUST produce observations within max_observation_tokens.
    """

    @abstractmethod
    def __init__(self, scenario_config: Dict[str, Any]):
        """
        Initialize the environment with a scenario configuration.

        Args:
            scenario_config: Dictionary loaded from a scenario JSON file.
        """
        pass

    @abstractmethod
    def reset(self) -> EnvironmentState:
        """
        Reset environment to initial state for a new episode.

        Returns:
            Fresh EnvironmentState with budget set from scenario config.
        """
        pass

    @abstractmethod
    def execute_action(
        self,
        state: EnvironmentState,
        action: Any,
    ) -> EnvironmentState:
        """
        Execute an action, update state, and return updated state.

        MUST append exactly one TraversalEvent to state.action_history.
        MUST deduct budget correctly (explore: -2, inspect: -1, others: 0).
        MUST set state.episode_done = True on submit_answer or budget exhaustion.

        Args:
            state: Current environment state (mutated in place)
            action: A VigilAction (Pydantic model) or error sentinel

        Returns:
            Updated EnvironmentState (same object, mutated)
        """
        pass

    def replay(self, events: List[TraversalEvent], seed: int) -> EnvironmentState:
        """
        Reconstruct EnvironmentState deterministically by replaying events.

        Creates a fresh environment with the given seed, resets it, then
        re-executes each event's action parameters in order. Two calls with
        identical (events, seed) always produce identical EnvironmentState objects.

        Args:
            events: Ordered list of TraversalEvents from a previous episode
            seed: Seed used to generate the original environment

        Returns:
            Reconstructed EnvironmentState after replaying all events
        """
        from vigil.actions.schemas import (
            ExploreAction, InspectAction, GetContextAction, SubmitAnswerAction,
        )

        # Re-initialise environment with same seed for determinism
        self.__class__.__init__(self, self.scenario_config, self.difficulty, seed)  # type: ignore[attr-defined]
        state = self.reset()

        for event in events:
            if event.event_type == EventType.ERROR:
                # Error events don't carry a valid action — skip replay
                continue

            params = event.params or {}

            if event.event_type == EventType.EXPLORE:
                action = ExploreAction(action_type="explore", node_id=event.node_id or params.get("node_id", ""))
            elif event.event_type == EventType.INSPECT:
                action = InspectAction(action_type="inspect", node_id=event.node_id or params.get("node_id", ""))
            elif event.event_type == EventType.GET_CONTEXT:
                action = GetContextAction(action_type="get_context")
            elif event.event_type == EventType.SUBMIT_ANSWER:
                action = SubmitAnswerAction(
                    action_type="submit_answer",
                    answer=params.get("answer", ""),
                    justification=params.get("justification", ""),
                    confidence=params.get("confidence", 0.5),
                )
            else:
                continue

            state = self.execute_action(state, action)

        return state

    @abstractmethod
    def render(self, state: EnvironmentState) -> str:
        """
        Produce a compact observation string for the current state.

        MUST stay within scenario_config.get('max_observation_tokens', 500) tokens.
        When len(state.action_history) > 15, include compressed action summary
        rather than full action log.

        Args:
            state: Current environment state

        Returns:
            Formatted observation string to pass to llm.prompt()
        """
        pass

    @abstractmethod
    def score_episode(
        self,
        state: EnvironmentState,
        final_answer: str,
        justification: str,
    ) -> Dict[str, float]:
        """
        Score the complete exploration episode.

        Args:
            state: Final environment state
            final_answer: Model's submitted answer
            justification: Model's submitted justification

        Returns:
            Dict with at minimum: correctness, final_score.
            Full VIS scoring is done by VISScorer using this as input.
        """
        pass

    @abstractmethod
    def verify_answer(self, answer: str) -> bool:
        """
        Verify if submitted answer matches the hidden rule.

        Args:
            answer: Model's submitted answer string

        Returns:
            True if answer correctly identifies the rule.
        """
        pass

    def get_scenario_info(self) -> Dict[str, str]:
        """Return metadata about this scenario."""
        return {
            "scenario_id": getattr(self, "_scenario_id", "unknown"),
            "cognitive_track": getattr(self, "_cognitive_track", "unknown"),
            "sub_ability": getattr(self, "_sub_ability", "unknown"),
        }

    def run_human_session(self, input_fn: Any) -> EnvironmentState:
        """
        Run one episode with a human participant instead of an LLM.

        Uses the same episode loop as model evaluation, ensuring identical
        conditions for human baseline collection (Req 18.1).

        Args:
            input_fn: Callable that accepts an observation string and returns
                      a raw action string or dict. Signature: (obs: str) -> Any

        Returns:
            Final EnvironmentState after the human session ends.
        """
        from vigil.actions.parser import parse_action

        state = self.reset()

        for _turn in range(20):  # Same 20-turn cap as model evaluation
            if state.episode_done or state.budget_remaining <= 0:
                break

            obs = self.render(state)
            raw_input = input_fn(obs)
            action = parse_action(raw_input)
            state = self.execute_action(state, action)

            if state.episode_done:
                break

        return state
