"""
Reinforcement Learning Environment — Track 1: Learning (Iowa Gambling Task analog).

Fixes applied (Task 5):
  5.3 — evidence_nodes populated on inspect of region nodes
  5.6 — 4 regions (2 high-immediate/net-negative, 2 modest/net-positive),
         stochastic rewards, cumulative_reward tracked, budget 20-25
"""

import random
from typing import Any, Dict, List, Optional

from vigil.environments.base import (
    CognitiveEnvironment, EnvironmentState, EventType, TraversalEvent,
)
from vigil.graphs.core import CognitiveGraph, GraphEdge, GraphNode, NodeVisibility


# Region reward schedules: (mean_reward, std_dev)
# Regions 0,1: high immediate but net-negative (mean < 0 overall after many draws)
# Regions 2,3: modest but net-positive
_REGION_SCHEDULES = {
    "region_0": {"mean": 2.0, "std": 3.5, "net": "negative"},   # high variance, net-negative
    "region_1": {"mean": 1.5, "std": 3.0, "net": "negative"},
    "region_2": {"mean": 0.5, "std": 0.5, "net": "positive"},   # low variance, net-positive
    "region_3": {"mean": 0.8, "std": 0.6, "net": "positive"},
}


class ReinforcementLearningEnv(CognitiveEnvironment):

    def __init__(self, scenario_config: Dict[str, Any], difficulty: int = 2, seed: Optional[int] = None):
        self.scenario_config = scenario_config
        self.difficulty = difficulty
        self.seed = seed if seed is not None else random.randint(0, 10000)
        self._rng = random.Random(self.seed)
        self._graph_config = self._get_difficulty_config()
        self._scoring_weights = scenario_config.get("scoring_weights", {})
        self._hidden_rule = scenario_config.get("hidden_rule", {})
        self._node_regions: Dict[str, str] = {}
        self.graph = self._generate_graph()
        # Evidence-relevant = nodes in net-positive regions
        self._evidence_relevant = {nid for nid, r in self._node_regions.items() if _REGION_SCHEDULES[r]["net"] == "positive"}

    def _get_difficulty_config(self) -> Dict[str, Any]:
        levels = self.scenario_config.get("difficulty_levels", {})
        return levels.get(str(self.difficulty), levels.get("2", {}))

    def _generate_graph(self) -> CognitiveGraph:
        num_nodes = self._graph_config.get("num_nodes", 16)
        graph = CognitiveGraph()
        node_ids = []
        regions = list(_REGION_SCHEDULES.keys())

        for i in range(num_nodes):
            region = regions[i % 4]
            self._node_regions[f"node_{i}"] = region
            node = GraphNode(
                node_id=f"node_{i}",
                features={f"region_marker_{i % 4}", f"node_attr_{i}"},
                category=region,
                metadata={"region": region},
            )
            graph.add_node(node)
            node_ids.append(node.node_id)

        for i in range(num_nodes):
            num_edges = self._rng.randint(2, 4)
            targets = self._rng.sample([n for n in node_ids if n != node_ids[i]], min(num_edges, len(node_ids) - 1))
            for target in targets:
                graph.add_edge(node_ids[i], GraphEdge(source=node_ids[i], target=target, relation_type="leads_to"))

        graph.hidden_rule = "reward_regions | advantageous: region_2, region_3"
        graph.metadata = {"region_schedules": {k: v["net"] for k, v in _REGION_SCHEDULES.items()}}
        graph.init_visibility(node_ids[0])
        return graph

    def _draw_reward(self, region: str) -> float:
        """Draw a stochastic reward from the region's schedule."""
        schedule = _REGION_SCHEDULES[region]
        # Gaussian draw, clipped to reasonable range
        reward = self._rng.gauss(schedule["mean"], schedule["std"])
        # Net-negative regions: subtract a penalty on most draws
        if schedule["net"] == "negative":
            reward -= 2.5  # makes expected value negative
        return round(reward, 2)

    def reset(self) -> EnvironmentState:
        # FIX 5.6: budget 20-25 (not 100)
        budget = self.scenario_config.get("budget", {}).get("base", 20)
        start = self.graph.get_all_node_ids()[0]
        state = EnvironmentState(current_node=start, budget_remaining=budget)
        state.visited_nodes.append(start)
        return state

    def render(self, state: EnvironmentState) -> str:
        view = self.graph.get_agent_view()
        if len(state.action_history) > 15:
            history_str = f"[Compressed: {len(state.action_history)} actions]"
        else:
            history_str = f"{len(state.action_history)} actions taken"
        return (
            f"=== Reinforcement Learning ===\n"
            f"Current: {state.current_node} | Budget: {state.budget_remaining}\n"
            f"Cumulative reward: {state.cumulative_reward:.2f}\n"
            f"Expanded: {len(view['expanded'])} | Discovered: {len(view['discovered'])}\n"
            f"Evidence (advantageous nodes found): {len(state.evidence_nodes)} | {history_str}\n"
            f"Actions: explore:<node_id>(cost 2) | inspect:<node_id>(cost 1) | get_context | submit_answer\n"
            f"Goal: Identify which regions yield net-positive rewards."
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
        if state.budget_remaining < 2:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, "Need 2 budget for explore", node_id=action.node_id))
            return state
        neighbors = self.graph.get_neighbors(state.current_node)
        if action.node_id not in neighbors:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"'{action.node_id}' is not a neighbor of '{state.current_node}'", node_id=action.node_id))
            return state
        state.current_node = action.node_id
        state.visited_nodes.append(action.node_id)
        state.budget_remaining -= 2
        self.graph.set_visibility(action.node_id, NodeVisibility.EXPANDED)
        for nid in self.graph.get_neighbors(action.node_id):
            self.graph.set_visibility(nid, NodeVisibility.DISCOVERED)
        # FIX 5.6: stochastic reward from region schedule
        region = self._node_regions.get(action.node_id, "region_0")
        reward = self._draw_reward(region)
        state.cumulative_reward += reward
        reward_str = f"+{reward:.2f}" if reward >= 0 else f"{reward:.2f}"
        obs = f"Moved to {action.node_id} (region {region[-1]}). Reward: {reward_str}. Cumulative: {state.cumulative_reward:.2f}"
        state.action_history.append(TraversalEvent.make(EventType.EXPLORE, obs, node_id=action.node_id, budget_delta=-2))
        return state

    def _execute_inspect(self, state: EnvironmentState, action: Any) -> EnvironmentState:
        # FIX 5.3: populate evidence_nodes for net-positive region nodes
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
        visible = sorted(node.get_visible_features())
        obs = f"Node {action.node_id} features: {visible}"
        self.graph.set_visibility(action.node_id, NodeVisibility.EXPANDED)
        state.budget_remaining -= 1
        evidence_added = []
        if action.node_id in self._evidence_relevant and action.node_id not in state.evidence_nodes:
            state.evidence_nodes.append(action.node_id)
            evidence_added.append(action.node_id)
        state.action_history.append(TraversalEvent.make(EventType.INSPECT, obs, node_id=action.node_id, budget_delta=-1, evidence_added=evidence_added))
        return state

    def _execute_get_context(self, state: EnvironmentState) -> EnvironmentState:
        # FIX 5.6: include cumulative_reward in get_context
        view = self.graph.get_agent_view()
        obs = (
            f"At {state.current_node} | Budget: {state.budget_remaining} | "
            f"Cumulative reward: {state.cumulative_reward:.2f} | "
            f"Expanded: {len(view['expanded'])} | Evidence: {len(state.evidence_nodes)}"
        )
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
        # Reward-based correctness bonus: positive cumulative reward is a good signal
        reward_bonus = max(0.0, min(0.3, state.cumulative_reward / 10.0))
        correctness = min(1.0, correctness + reward_bonus)
        scores = {
            "correctness": correctness,
            "efficiency": compute_efficiency(state, 8),
            "evidence_quality": compute_evidence_quality(state, 4),
            "calibration": compute_calibration(state, bool(correctness)),
            "recovery": 0.5,
        }
        scores["final_score"] = compute_weighted_score(scores, self._scoring_weights)
        return scores

    def verify_answer(self, answer: str) -> bool:
        patterns = self._hidden_rule.get("verification_pattern", ["reward", "maximize", "avoid", "region_2", "region_3", "advantageous"])
        return any(p in answer.lower() for p in patterns)
