"""
Concept Formation Environment for Track 1: Learning.

Implements the Concept Formation cognitive test where models must:
- Explore nodes with features
- Infer latent category rules
- Demonstrate concept abstraction ability
"""

import random
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass

from vigil.environments.base import (
    CognitiveEnvironment,
    EnvironmentState,
    GraphAction,
    ActionType
)
from vigil.graphs.core import CognitiveGraph, GraphNode, GraphEdge


@dataclass
class ConceptFormationState(EnvironmentState):
    """Extended state for concept formation tasks."""
    current_hypothesis: Optional[str] = None
    category_guesses: List[str] = None

    def __post_init__(self):
        if self.category_guesses is None:
            self.category_guesses = []


class ConceptFormationEnv(CognitiveEnvironment):
    """
    Environment for testing concept formation ability.

    The model must explore nodes, observe their features,
    and infer the latent categorization rule.

    Scenario:
    - Graph contains nodes belonging to hidden categories
    - Nodes in same category share core features
    - Model must discover the category structure through exploration
    - Scoring based on correctness, efficiency, evidence quality
    """

    def __init__(
        self,
        scenario_config: Dict[str, Any],
        difficulty: int = 2,
        seed: Optional[int] = None
    ):
        """
        Initialize concept formation environment.

        Args:
            scenario_config: Configuration from scenario JSON
            difficulty: Difficulty level (1-3)
            seed: Random seed for reproducibility
        """
        self.scenario_config = scenario_config
        self.difficulty = difficulty
        self.seed = seed or random.randint(0, 10000)
        random.seed(self.seed)

        # Extract config values
        self._graph_config = self._get_difficulty_config()
        self._scoring_weights = scenario_config.get("scoring_weights", {})

        # Generate the graph
        self.graph = self._generate_graph()
        self.state: Optional[ConceptFormationState] = None

        # Track hidden rule
        self._hidden_rule = scenario_config.get("hidden_rule", {})
        self._correct_categories = self._get_correct_categories()

    def _get_difficulty_config(self) -> Dict[str, Any]:
        """Get configuration for current difficulty level."""
        levels = self.scenario_config.get("difficulty_levels", {})
        return levels.get(str(self.difficulty), levels.get("2", {}))

    def _generate_graph(self) -> CognitiveGraph:
        """
        Generate graph with latent category structure.

        Nodes in the same category share core features.
        """
        num_nodes = self._graph_config.get("num_nodes", 15)
        num_categories = self._graph_config.get("num_categories", 3)
        features_per_node = self._graph_config.get("features_per_node", 5)
        core_features_per_category = self._graph_config.get("core_features_per_category", 3)
        feature_pool_size = self._graph_config.get("feature_pool_size", 30)

        # Create feature pool
        feature_pool = [f"feature_{i}" for i in range(feature_pool_size)]

        # Assign core features to each category
        category_core_features = {}
        remaining_features = feature_pool.copy()

        for cat_idx in range(num_categories):
            # Each category gets unique core features
            num_core = min(core_features_per_category, len(remaining_features))
            core_features = set(random.sample(remaining_features, num_core))
            category_core_features[f"cat_{cat_idx}"] = core_features
            remaining_features = [f for f in remaining_features if f not in core_features]

        # Generate nodes
        graph = CognitiveGraph()
        nodes = []

        for i in range(num_nodes):
            category = f"cat_{i % num_categories}"
            core_feats = category_core_features[category].copy()

            # Add noise features
            noise_count = features_per_node - len(core_feats)
            noise_feats = set(random.sample(
                remaining_features,
                min(noise_count, len(remaining_features))
            ))

            node = GraphNode(
                node_id=f"node_{i}",
                features=core_feats | noise_feats,
                category=category
            )
            graph.add_node(node)
            nodes.append(node)

        # Create edges between nodes (random connectivity for exploration)
        for i, node in enumerate(nodes):
            # Connect to a few random other nodes
            num_connections = random.randint(2, min(5, len(nodes) - 1))
            targets = random.sample(
                [n for j, n in enumerate(nodes) if j != i],
                num_connections
            )

            for target in targets:
                edge = GraphEdge(
                    source=node.node_id,
                    target=target.node_id,
                    relation_type="connected_to"
                )
                graph.add_edge(node.node_id, edge)

        # Store hidden rule
        graph.hidden_rule = f"Nodes in same category share core features: {category_core_features}"
        graph.metadata = {
            "num_categories": num_categories,
            "core_features": category_core_features
        }

        return graph

    def _get_correct_categories(self) -> Dict[str, str]:
        """Get mapping of nodes to their correct categories."""
        return {
            node.node_id: node.category
            for node in self.graph.nodes.values()
        }

    def reset(self) -> ConceptFormationState:
        """Reset environment to initial state."""
        self.state = ConceptFormationState(
            current_node=self.graph.get_all_node_ids()[0],
            budget_remaining=self.scenario_config.get("budget", {}).get("base", 10)
        )
        return self.state

    def get_available_actions(self, state: ConceptFormationState) -> str:
        """Generate action menu for the model."""
        current = self.graph.get_node(state.current_node)
        neighbors = self.graph.get_neighbors(state.current_node)

        lines = [
            f"Current node: {state.current_node}",
            f"Budget: {state.budget_remaining}",
            "",
            "Actions:",
            "  expand:<node_id> - Move to connected node",
            "  inspect - Examine current node features",
            "  backtrack - Return to previous node",
            "  submit - Submit category rule hypothesis",
            "",
            f"Visited: {len(state.visited_nodes)} nodes"
        ]

        if neighbors:
            lines.append(f"Visible neighbors: {', '.join(neighbors[:5])}")

        return "\n".join(lines)

    def execute_action(
        self,
        state: ConceptFormationState,
        action: GraphAction
    ) -> Tuple[bool, str]:
        """Execute action and return observation."""
        if action.action_type == ActionType.EXPAND:
            return self._execute_expand(state, action)
        elif action.action_type == ActionType.INSPECT:
            return self._execute_inspect(state)
        elif action.action_type == ActionType.BACKTRACK:
            return self._execute_backtrack(state)
        elif action.action_type == ActionType.SUBMIT:
            return self._execute_submit(state)

        return False, "Unknown action"

    def _execute_expand(
        self,
        state: ConceptFormationState,
        action: GraphAction
    ) -> Tuple[bool, str]:
        """Execute expand action."""
        if state.budget_remaining <= 0:
            return False, "No budget remaining"

        target = action.target_node
        if not target:
            return False, "Must specify target node"

        current_node = self.graph.get_node(state.current_node)
        if not current_node:
            return False, "Invalid current node"

        # Check if target is a valid neighbor
        neighbors = self.graph.get_neighbors(state.current_node)
        if target not in neighbors:
            return False, f"Node {target} is not connected to current node"

        # Move to target
        state.current_node = target
        state.visited_nodes.append(target)
        state.budget_remaining -= 1
        state.action_history.append(action)

        # Get target node info
        target_node = self.graph.get_node(target)
        return True, f"Moved to {target}. Features: {target_node.features}"

    def _execute_inspect(
        self,
        state: ConceptFormationState
    ) -> Tuple[bool, str]:
        """Execute inspect action."""
        node = self.graph.get_node(state.current_node)
        if not node:
            return False, "Invalid node"

        state.action_history.append(GraphAction(
            action_type=ActionType.INSPECT,
            target_node=state.current_node
        ))

        return True, f"Node {state.current_node} features: {node.features}\nCategory (hidden): {node.category}"

    def _execute_backtrack(
        self,
        state: ConceptFormationState
    ) -> Tuple[bool, str]:
        """Execute backtrack action."""
        if len(state.visited_nodes) < 2:
            return False, "No previous node to backtrack to"

        # Go back to previous node
        state.visited_nodes.pop()  # Remove current
        previous = state.visited_nodes[-1] if state.visited_nodes else state.current_node
        state.current_node = previous
        state.budget_remaining -= 1
        state.action_history.append(GraphAction(
            action_type=ActionType.BACKTRACK
        ))

        return True, f"Backtracked to {previous}"

    def _execute_submit(
        self,
        state: ConceptFormationState
    ) -> Tuple[bool, str]:
        """Execute submit action - model provides hypothesis."""
        state.budget_remaining = 0  # End episode
        return True, "Hypothesis submitted. Episode complete."

    def score_exploration(
        self,
        state: ConceptFormationState,
        final_answer: str
    ) -> Dict[str, float]:
        """Score the complete exploration."""
        from vigil.scoring.metrics import (
            compute_correctness,
            compute_efficiency,
            compute_evidence_quality,
            compute_calibration,
            compute_weighted_score
        )

        # Correctness - did they identify the rule?
        correctness = compute_correctness(
            final_answer,
            self._hidden_rule.get("description", ""),
            self.verify_rule
        )

        # Efficiency - optimal path vs actual
        optimal_visits = self._graph_config.get("num_categories", 3) * 2
        efficiency = compute_efficiency(state, optimal_visits)

        # Evidence quality - did they visit enough nodes?
        required_evidence = self._graph_config.get("num_categories", 3)
        evidence_quality = compute_evidence_quality(state, required_evidence)

        # Calibration - confidence vs correctness
        calibration = compute_calibration(state, bool(correctness))

        # Recovery - not as relevant for concept formation
        recovery = 0.5  # Neutral

        scores = {
            "correctness": correctness,
            "efficiency": efficiency,
            "evidence_quality": evidence_quality,
            "calibration": calibration,
            "recovery": recovery
        }

        # Weighted final score
        scores["final_score"] = compute_weighted_score(scores, self._scoring_weights)

        return scores

    def verify_rule(self, answer: str) -> bool:
        """Verify if answer correctly identifies the category rule."""
        answer_lower = answer.lower()
        patterns = self._hidden_rule.get("verification_pattern", [
            "core features", "shared features", "category", "same group"
        ])

        return any(pattern in answer_lower for pattern in patterns)
