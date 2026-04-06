"""
Associative Learning Environment for Track 1: Learning.

Implements associative learning test where models must:
- Learn relationships between co-occurring events
- Identify paired associations
- Transfer learned associations to new contexts
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


class AssociativeLearningEnv(CognitiveEnvironment):
    """
    Environment for testing associative learning ability.

    The model must learn which nodes/ stimuli tend to appear together
    and identify the underlying association patterns.
    """

    def __init__(
        self,
        scenario_config: Dict[str, Any],
        difficulty: int = 2,
        seed: Optional[int] = None
    ):
        """
        Initialize associative learning environment.

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
        self._associations = {}

    def _get_difficulty_config(self) -> Dict[str, Any]:
        """Get configuration for current difficulty."""
        levels = self.scenario_config.get("difficulty_levels", {})
        return levels.get(str(self.difficulty), levels.get("2", {}))

    def _generate_graph(self) -> CognitiveGraph:
        """Generate graph with paired associations."""
        num_pairs = self._graph_config.get("num_pairs", 8)

        graph = CognitiveGraph()
        self._associations = {}

        # Create paired nodes
        for i in range(num_pairs):
            pair_id = f"pair_{i}"
            node_a_id = f"stim_a_{i}"
            node_b_id = f"stim_b_{i}"

            # Create associated pair
            node_a = GraphNode(
                node_id=node_a_id,
                features={f"pair_id_{i}", "type_A"},
                category=f"pair_{i}"
            )
            node_b = GraphNode(
                node_id=node_b_id,
                features={f"pair_id_{i}", "type_B"},
                category=f"pair_{i}"
            )

            graph.add_node(node_a)
            graph.add_node(node_b)

            # Create bidirectional association
            edge_ab = GraphEdge(
                source=node_a_id,
                target=node_b_id,
                relation_type="associated_with"
            )
            edge_ba = GraphEdge(
                source=node_b_id,
                target=node_a_id,
                relation_type="associated_with"
            )
            graph.add_edge(node_a_id, edge_ab)
            graph.add_edge(node_b_id, edge_ba)

            self._associations[node_a_id] = node_b_id
            self._associations[node_b_id] = node_a_id

        return graph

    def reset(self) -> EnvironmentState:
        """Reset environment."""
        self.state = EnvironmentState(
            current_node=list(self.graph.nodes.keys())[0],
            budget_remaining=self.scenario_config.get("budget", {}).get("base", 12)
        )
        return self.state

    def get_available_actions(self, state: EnvironmentState) -> str:
        """Get action menu."""
        return f"""
Current: {state.current_node}
Budget: {state.budget_remaining}
Visited: {len(state.visited_nodes)}

Actions:
  expand:<node_id> - Move to connected node
  inspect - View current node
  submit - Submit association pattern
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
        """Execute expand."""
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
        return True, f"At {target}. Features: {node.features}"

    def _execute_inspect(
        self,
        state: EnvironmentState,
        action: GraphAction
    ) -> Tuple[bool, str]:
        """Execute inspect."""
        node = self.graph.get_node(state.current_node)
        state.action_history.append(action)
        return True, f"Features: {node.features}"

    def _execute_submit(
        self,
        state: EnvironmentState
    ) -> Tuple[bool, str]:
        """Submit associations."""
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

        correctness = compute_correctness(
            final_answer,
            self._hidden_rule.get("description", ""),
            self.verify_rule
        )
        efficiency = compute_efficiency(state, len(self._associations))
        evidence_quality = min(1.0, len(state.visited_nodes) / len(self._associations))
        calibration = 0.5  # Default

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
        """Verify association pattern."""
        answer_lower = answer.lower()
        patterns = self._hidden_rule.get("verification_pattern", [
            "pair", "associated", "together"
        ])
        return any(p in answer_lower for p in patterns)
