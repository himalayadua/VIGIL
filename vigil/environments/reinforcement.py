"""
Reinforcement Learning Environment for Track 1: Learning.

Implements reinforcement learning test where models must:
- Learn from rewards and punishments
- Maximize cumulative reward
- Avoid penalty states
"""

import random
from typing import Dict, Any, Optional, Tuple, List

from vigil.environments.base import (
    CognitiveEnvironment,
    EnvironmentState,
    GraphAction,
    ActionType
)
from vigil.graphs.core import CognitiveGraph, GraphNode, GraphEdge


class ReinforcementLearningEnv(CognitiveEnvironment):
    """
    Environment for testing reinforcement learning ability.

    The model must navigate to reward nodes while avoiding penalties,
    learning the value of different paths through experience.
    """

    def __init__(
        self,
        scenario_config: Dict[str, Any],
        difficulty: int = 2,
        seed: Optional[int] = None
    ):
        """
        Initialize RL environment.

        Args:
            scenario_config: Configuration from scenario JSON
            difficulty: Difficulty level (1-3)
            seed: Random seed
        """
        self.scenario_config = scenario_config
        self.difficulty = difficulty
        self.seed = seed or random.randint(0, 10000)
        random.seed(self.seed)

        self._graph_config = self._get_difficulty_config()
        self._scoring_weights = scenario_config.get("scoring_weights", {})

        self.graph = self._generate_graph()
        self.state: Optional[EnvironmentState] = None
        self._hidden_rule = scenario_config.get("hidden_rule", {})
        self._reward_history = []

    def _get_difficulty_config(self) -> Dict[str, Any]:
        """Get difficulty config."""
        levels = self.scenario_config.get("difficulty_levels", {})
        return levels.get(str(self.difficulty), levels.get("2", {}))

    def _generate_graph(self) -> CognitiveGraph:
        """Generate graph with reward and penalty nodes."""
        num_nodes = self._graph_config.get("num_nodes", 20)
        num_rewards = self._graph_config.get("reward_nodes", 4)
        num_penalties = self._graph_config.get("penalty_nodes", 3)

        graph = CognitiveGraph()
        node_ids = []

        # Create nodes
        for i in range(num_nodes):
            node_type = "neutral"
            features = set()

            if i < num_rewards:
                node_type = "reward"
                features.add("REWARD")
            elif i < num_rewards + num_penalties:
                node_type = "penalty"
                features.add("PENALTY")

            node = GraphNode(
                node_id=f"node_{i}",
                features=features | {f"feature_{i}"},
                category=node_type,
                metadata={"type": node_type, "value": 1.0 if node_type == "reward" else (-1.0 if node_type == "penalty" else 0.0)}
            )
            graph.add_node(node)
            node_ids.append(node.node_id)

        # Create random connections
        for i, node in enumerate(graph.nodes.values()):
            num_edges = random.randint(2, 4)
            targets = random.sample(
                [n for n in node_ids if n != node.node_id],
                min(num_edges, len(node_ids) - 1)
            )

            for target in targets:
                graph.add_edge(
                    node.node_id,
                    GraphEdge(source=node.node_id, target=target, relation_type="leads_to")
                )

        return graph

    def reset(self) -> EnvironmentState:
        """Reset environment."""
        self.state = EnvironmentState(
            current_node="node_0",
            budget_remaining=self.scenario_config.get("budget", {}).get("base", 15)
        )
        self._reward_history = []
        return self.state

    def get_available_actions(self, state: EnvironmentState) -> str:
        """Get action menu."""
        return f"""
Current: {state.current_node}
Budget: {state.budget_remaining}
Total reward so far: {sum(self._reward_history):.1f}

Actions:
  expand:<node_id> - Move to connected node
  inspect - View current node
  submit - Submit findings
"""

    def execute_action(
        self,
        state: EnvironmentState,
        action: GraphAction
    ) -> Tuple[bool, str]:
        """Execute action."""
        if action.action_type == ActionType.EXPAND:
            return self._execute_expand(state, action)
        elif action.action_type == ActionType.INSPECT:
            return self._execute_inspect(state, action)
        elif action.action_type == ActionType.SUBMIT:
            return self._execute_submit(state)

        return False, "Invalid action"

    def _execute_expand(
        self,
        state: EnvironmentState,
        action: GraphAction
    ) -> Tuple[bool, str]:
        """Execute expand with reward/penalty feedback."""
        if state.budget_remaining <= 0:
            return False, "No budget"

        target = action.target_node
        if not target:
            return False, "Specify target"

        state.current_node = target
        state.visited_nodes.append(target)
        state.budget_remaining -= 1
        state.action_history.append(action)

        node = self.graph.get_node(target)
        node_type = node.metadata.get("type", "neutral")

        # Provide reward/penalty feedback
        if node_type == "reward":
            self._reward_history.append(1.0)
            return True, f"REWARD! (+1.0). Features: {node.features}"
        elif node_type == "penalty":
            self._reward_history.append(-1.0)
            return True, f"PENALTY! (-1.0). Features: {node.features}"
        else:
            self._reward_history.append(0.0)
            return True, f"Neutral. Features: {node.features}"

    def _execute_inspect(
        self,
        state: EnvironmentState,
        action: GraphAction
    ) -> Tuple[bool, str]:
        """Inspect current node."""
        node = self.graph.get_node(state.current_node)
        state.action_history.append(action)
        return True, f"Features: {node.features}"

    def _execute_submit(
        self,
        state: EnvironmentState
    ) -> Tuple[bool, str]:
        """Submit findings."""
        state.budget_remaining = 0
        return True, "Submitted"

    def score_exploration(
        self,
        state: EnvironmentState,
        final_answer: str
    ) -> Dict[str, float]:
        """Score exploration."""
        from vigil.scoring.metrics import (
            compute_correctness,
            compute_efficiency,
            compute_weighted_score
        )

        # Correctness based on reward maximization
        total_reward = sum(self._reward_history)
        correctness = max(0, min(1, (total_reward + 5) / 10))  # Normalize

        efficiency = compute_efficiency(state, 5)
        evidence_quality = min(1.0, len(state.visited_nodes) / 10)
        calibration = 0.5

        scores = {
            "correctness": correctness,
            "efficiency": efficiency,
            "evidence_quality": evidence_quality,
            "calibration": calibration,
            "recovery": 0.5
        }

        scores["final_score"] = compute_weighted_score(scores, self._scoring_weights)
        return scores

    def verify_rule(self, answer: str) -> bool:
        """Verify understanding of reward structure."""
        answer_lower = answer.lower()
        patterns = self._hidden_rule.get("verification_pattern", [
            "reward", "maximize", "avoid"
        ])
        return any(p in answer_lower for p in patterns)
