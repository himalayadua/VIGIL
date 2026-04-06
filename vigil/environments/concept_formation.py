"""
Concept Formation Environment — Track 1: Learning (WCST analog).

Fixes applied (Task 5):
  5.1 — Neighbor validation in _execute_explore (no teleportation)
  5.2 — Category leak removed from _execute_inspect
  5.3 — evidence_nodes populated on inspect
"""

import random
from typing import Any, Dict, List, Optional

from vigil.environments.base import (
    CognitiveEnvironment, EnvironmentState, EventType, TraversalEvent,
)
from vigil.graphs.core import CognitiveGraph, GraphEdge, GraphNode, NodeVisibility


class ConceptFormationEnv(CognitiveEnvironment):

    def __init__(self, scenario_config: Dict[str, Any], difficulty: int = 2, seed: Optional[int] = None):
        self.scenario_config = scenario_config
        self.difficulty = difficulty
        self.seed = seed if seed is not None else random.randint(0, 10000)
        self._rng = random.Random(self.seed)
        self._graph_config = self._get_difficulty_config()
        self._scoring_weights = scenario_config.get("scoring_weights", {})
        self._hidden_rule = scenario_config.get("hidden_rule", {})
        self.graph = self._generate_graph()
        self._evidence_relevant = set(self.graph.nodes.keys())

    def _get_difficulty_config(self) -> Dict[str, Any]:
        levels = self.scenario_config.get("difficulty_levels", {})
        return levels.get(str(self.difficulty), levels.get("2", {}))

    def _generate_graph(self) -> CognitiveGraph:
        num_nodes = self._graph_config.get("num_nodes", 15)
        num_categories = self._graph_config.get("num_categories", 3)
        features_per_node = self._graph_config.get("features_per_node", 5)
        core_per_cat = self._graph_config.get("core_features_per_category", 3)
        pool_size = self._graph_config.get("feature_pool_size", 30)

        feature_pool = [f"feature_{i}" for i in range(pool_size)]
        self._rng.shuffle(feature_pool)

        category_core: Dict[str, set] = {}
        remaining = feature_pool.copy()
        for cat_idx in range(num_categories):
            core = set(remaining[:core_per_cat])
            category_core[f"cat_{cat_idx}"] = core
            remaining = remaining[core_per_cat:]

        graph = CognitiveGraph()
        nodes: List[GraphNode] = []
        for i in range(num_nodes):
            category = f"cat_{i % num_categories}"
            core_feats = category_core[category].copy()
            noise_count = features_per_node - len(core_feats)
            noise = set(self._rng.sample(remaining, min(noise_count, len(remaining))))
            node = GraphNode(node_id=f"node_{i}", features=core_feats | noise, category=category)
            graph.add_node(node)
            nodes.append(node)

        for i, node in enumerate(nodes):
            num_conn = self._rng.randint(2, min(5, len(nodes) - 1))
            targets = self._rng.sample([n for j, n in enumerate(nodes) if j != i], num_conn)
            for target in targets:
                graph.add_edge(node.node_id, GraphEdge(source=node.node_id, target=target.node_id, relation_type="connected_to"))

        graph.hidden_rule = f"category_by_core_features | {category_core}"
        graph.metadata = {"num_categories": num_categories, "category_core_features": category_core}
        graph.init_visibility(nodes[0].node_id)
        return graph

    def reset(self) -> EnvironmentState:
        budget = self.scenario_config.get("budget", {}).get("base", 10)
        start = self.graph.get_all_node_ids()[0]
        state = EnvironmentState(current_node=start, budget_remaining=budget)
        state.visited_nodes.append(start)
        return state

    def render(self, state: EnvironmentState) -> str:
        view = self.graph.get_agent_view()
        if len(state.action_history) > 15:
            history_str = f"[Compressed: {len(state.action_history)} actions, {len(state.evidence_nodes)} evidence nodes]"
        else:
            history_str = f"{len(state.action_history)} actions taken"
        return (
            f"=== Concept Formation ===\n"
            f"Current: {state.current_node} | Budget: {state.budget_remaining}\n"
            f"Expanded: {len(view['expanded'])} | Discovered: {len(view['discovered'])}\n"
            f"Evidence: {len(state.evidence_nodes)} | {history_str}\n"
            f"Actions: explore:<node_id>(cost 2) | inspect:<node_id>(cost 1) | get_context | submit_answer\n"
            f"Goal: Infer the hidden rule grouping nodes into categories."
        )

    def execute_action(self, state: EnvironmentState, action: Any) -> EnvironmentState:
        from vigil.actions.schemas import (
            ActionParseError, ExploreAction, GetContextAction, InspectAction, SubmitAnswerAction,
        )
        if isinstance(action, ActionParseError):
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"Parse error: {action.error}"))
            return state
        if isinstance(action, ExploreAction):
            return self._execute_explore(state, action)
        if isinstance(action, InspectAction):
            return self._execute_inspect(state, action)
        if isinstance(action, GetContextAction):
            return self._execute_get_context(state)
        if isinstance(action, SubmitAnswerAction):
            return self._execute_submit(state, action)
        state.action_history.append(TraversalEvent.make(EventType.ERROR, f"Unknown action: {type(action)}"))
        return state

    def _execute_explore(self, state: EnvironmentState, action: Any) -> EnvironmentState:
        # FIX 5.1: validate neighbor, no budget deduction on error
        if state.budget_remaining < 2:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, "Need 2 budget for explore", node_id=action.node_id))
            return state
        neighbors = self.graph.get_neighbors(state.current_node)
        if action.node_id not in neighbors:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"'{action.node_id}' is not a neighbor of '{state.current_node}'", node_id=action.node_id))
            return state
        if action.node_id not in self.graph.nodes:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"Node '{action.node_id}' does not exist", node_id=action.node_id))
            return state
        state.current_node = action.node_id
        state.visited_nodes.append(action.node_id)
        state.budget_remaining -= 2
        self.graph.set_visibility(action.node_id, NodeVisibility.EXPANDED)
        for nid in self.graph.get_neighbors(action.node_id):
            self.graph.set_visibility(nid, NodeVisibility.DISCOVERED)
        obs = f"Moved to {action.node_id}. Neighbors: {self.graph.get_neighbors(action.node_id)}"
        state.action_history.append(TraversalEvent.make(EventType.EXPLORE, obs, node_id=action.node_id, budget_delta=-2))
        return state

    def _execute_inspect(self, state: EnvironmentState, action: Any) -> EnvironmentState:
        # FIX 5.2: no category. FIX 5.3: populate evidence_nodes
        if state.budget_remaining < 1:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, "Need 1 budget for inspect", node_id=action.node_id))
            return state
        if self.graph.get_visibility(action.node_id) == NodeVisibility.UNEXPLORED:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"Cannot inspect UNEXPLORED node '{action.node_id}'", node_id=action.node_id))
            return state
        node = self.graph.get_node(action.node_id)
        if node is None:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"Node '{action.node_id}' not found", node_id=action.node_id))
            return state
        # FIX 5.2: get_visible_features() — never category
        visible = sorted(node.get_visible_features())
        obs = f"Node {action.node_id} features: {visible}"
        self.graph.set_visibility(action.node_id, NodeVisibility.EXPANDED)
        state.budget_remaining -= 1
        # FIX 5.3: evidence_nodes
        evidence_added = []
        if action.node_id in self._evidence_relevant and action.node_id not in state.evidence_nodes:
            state.evidence_nodes.append(action.node_id)
            evidence_added.append(action.node_id)
        state.action_history.append(TraversalEvent.make(EventType.INSPECT, obs, node_id=action.node_id, budget_delta=-1, evidence_added=evidence_added))
        return state

    def _execute_get_context(self, state: EnvironmentState) -> EnvironmentState:
        view = self.graph.get_agent_view()
        obs = f"At {state.current_node} | Budget: {state.budget_remaining} | Expanded: {len(view['expanded'])} | Discovered: {len(view['discovered'])} | Evidence: {len(state.evidence_nodes)}"
        state.action_history.append(TraversalEvent.make(EventType.GET_CONTEXT, obs))
        return state

    def _execute_submit(self, state: EnvironmentState, action: Any) -> EnvironmentState:
        state.confidence_history.append(action.confidence)
        state.episode_done = True
        obs = f"Submitted: '{action.answer}' (confidence={action.confidence:.2f})"
        state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs, episode_done=True))
        return state

    def score_episode(self, state: EnvironmentState, final_answer: str, justification: str = "") -> Dict[str, float]:
        from vigil.scoring.metrics import compute_correctness, compute_efficiency, compute_evidence_quality, compute_calibration, compute_weighted_score
        correctness = compute_correctness(final_answer, self._hidden_rule.get("description", ""), self.verify_answer)
        optimal = self._graph_config.get("num_categories", 3) * 2
        scores = {
            "correctness": correctness,
            "efficiency": compute_efficiency(state, optimal),
            "evidence_quality": compute_evidence_quality(state, self._graph_config.get("num_categories", 3)),
            "calibration": compute_calibration(state, bool(correctness)),
            "recovery": 0.5,
        }
        scores["final_score"] = compute_weighted_score(scores, self._scoring_weights)
        return scores

    def verify_answer(self, answer: str) -> bool:
        patterns = self._hidden_rule.get("verification_pattern", ["core features", "shared features", "category", "same group"])
        return any(p in answer.lower() for p in patterns)
