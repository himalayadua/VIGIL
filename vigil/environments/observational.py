"""
Observational Learning Environment — Track 1: Learning (Bandura analog).

Two-phase design:
  Phase 1 (demonstration): Graph with trace annotations on edges showing
    how a previous agent navigated. Model can see these traces via inspect().
  Phase 2 (transfer): Structurally isomorphic graph with different node IDs
    and feature labels. Model must apply the abstract strategy, not copy the path.

Requirements: 14.1, 14.2, 14.3, 14.4
"""

import random
from typing import Any, Dict, List, Optional

from vigil.environments.base import (
    CognitiveEnvironment, EnvironmentState, EventType, TraversalEvent,
)
from vigil.graphs.core import CognitiveGraph, GraphEdge, GraphNode, NodeVisibility


class ObservationalLearningEnv(CognitiveEnvironment):

    def __init__(self, scenario_config: Dict[str, Any], difficulty: int = 2, seed: Optional[int] = None):
        self.scenario_config = scenario_config
        self.difficulty = difficulty
        self.seed = seed if seed is not None else random.randint(0, 10000)
        self._rng = random.Random(self.seed)
        self._graph_config = self._get_difficulty_config()
        self._scoring_weights = scenario_config.get("scoring_weights", {})
        self._hidden_rule = scenario_config.get("hidden_rule", {})

        # Build demo graph with trace annotations
        self._demo_graph, self._demo_strategy = self._build_demo_graph()
        # Build transfer graph (isomorphic, relabelled)
        self._transfer_graph, self._relabelling = self._build_transfer_graph()

        # Phase: "demo" or "transfer"
        self._phase = "demo"
        self.graph = self._demo_graph
        self._evidence_relevant = set(self.graph.nodes.keys())

    def _get_difficulty_config(self) -> Dict[str, Any]:
        levels = self.scenario_config.get("difficulty_levels", {})
        return levels.get(str(self.difficulty), levels.get("2", {}))

    def _build_demo_graph(self):
        """Build a graph with a hidden goal path and trace annotations on edges."""
        num_nodes = self._graph_config.get("num_nodes", 8)
        graph = CognitiveGraph()
        nodes = []
        for i in range(num_nodes):
            node = GraphNode(
                node_id=f"d{i}",
                features={f"attr_{i % 3}", f"val_{i}"},
                category="demo",
            )
            graph.add_node(node)
            nodes.append(node)

        # Create a linear chain + some cross-edges
        for i in range(num_nodes - 1):
            graph.add_edge(f"d{i}", GraphEdge(source=f"d{i}", target=f"d{i+1}", relation_type="leads_to"))
            graph.add_edge(f"d{i+1}", GraphEdge(source=f"d{i+1}", target=f"d{i}", relation_type="leads_to"))

        # The "correct strategy": always follow the chain d0 → d1 → ... → d(N-1)
        strategy_path = [f"d{i}" for i in range(num_nodes)]

        # Embed trace annotations on edges along the strategy path
        for i in range(len(strategy_path) - 1):
            src, tgt = strategy_path[i], strategy_path[i + 1]
            # Store trace in edge metadata (visible via inspect)
            for edge in graph.get_edges_from(src):
                if edge.target == tgt:
                    edge.metadata["trace"] = f"agent_visited_step_{i}"
                    edge.metadata["strategy_hint"] = "follow_sequence"

        graph.hidden_rule = "follow_sequence | traverse nodes in ascending order"
        graph.metadata = {"strategy": "ascending_chain", "goal_node": strategy_path[-1]}
        graph.init_visibility(strategy_path[0])
        return graph, strategy_path

    def _build_transfer_graph(self):
        """Build isomorphic graph with relabelled node IDs and features."""
        num_nodes = self._graph_config.get("num_nodes", 8)
        # Relabelling: d0→t0, d1→t1, etc. but with shuffled feature labels
        relabelling = {f"d{i}": f"t{i}" for i in range(num_nodes)}
        graph = CognitiveGraph()

        for i in range(num_nodes):
            node = GraphNode(
                node_id=f"t{i}",
                # Different feature labels — same structure, different surface
                features={f"prop_{(i + 2) % 4}", f"item_{i * 3}"},
                category="transfer",
            )
            graph.add_node(node)

        for i in range(num_nodes - 1):
            graph.add_edge(f"t{i}", GraphEdge(source=f"t{i}", target=f"t{i+1}", relation_type="connects"))
            graph.add_edge(f"t{i+1}", GraphEdge(source=f"t{i+1}", target=f"t{i}", relation_type="connects"))

        graph.hidden_rule = "follow_sequence | traverse nodes in ascending order (transfer)"
        graph.metadata = {"goal_node": f"t{num_nodes - 1}"}
        graph.init_visibility(f"t0")
        return graph, relabelling

    def reset(self) -> EnvironmentState:
        self._phase = "demo"
        self.graph = self._demo_graph
        budget = self.scenario_config.get("budget", {}).get("base", 20)
        start = "d0"
        state = EnvironmentState(current_node=start, budget_remaining=budget)
        state.visited_nodes.append(start)
        return state

    def render(self, state: EnvironmentState) -> str:
        view = self.graph.get_agent_view()
        phase_msg = (
            "PHASE 1 — Demonstration: Observe the trace annotations on edges via inspect()."
            if self._phase == "demo"
            else "PHASE 2 — Transfer: Apply the strategy you learned to this new graph."
        )
        if len(state.action_history) > 15:
            history_str = f"[Compressed: {len(state.action_history)} actions]"
        else:
            history_str = f"{len(state.action_history)} actions taken"
        return (
            f"=== Observational Learning ({self._phase.upper()}) ===\n"
            f"{phase_msg}\n"
            f"Current: {state.current_node} | Budget: {state.budget_remaining}\n"
            f"Expanded: {len(view['expanded'])} | Discovered: {len(view['discovered'])}\n"
            f"Evidence: {len(state.evidence_nodes)} | {history_str}\n"
            f"Actions: explore:<node_id>(cost 2) | inspect:<node_id>(cost 1) | get_context | submit_answer\n"
            f"Goal: Discover the navigation strategy from the demonstration, then apply it."
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
            state.action_history.append(TraversalEvent.make(EventType.ERROR, "Need 2 budget", node_id=action.node_id))
            return state
        neighbors = self.graph.get_neighbors(state.current_node)
        if action.node_id not in neighbors:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"'{action.node_id}' not a neighbor", node_id=action.node_id))
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
        """Req 14.2: include trace annotations for edges incident to node_id."""
        if state.budget_remaining < 1:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, "Need 1 budget", node_id=action.node_id))
            return state
        if self.graph.get_visibility(action.node_id) == NodeVisibility.UNEXPLORED:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"Cannot inspect UNEXPLORED '{action.node_id}'", node_id=action.node_id))
            return state
        node = self.graph.get_node(action.node_id)
        if node is None:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, f"Node '{action.node_id}' not found", node_id=action.node_id))
            return state

        visible = sorted(node.get_visible_features())
        # Collect trace annotations from incident edges
        traces = []
        for edge in self.graph.get_edges_from(action.node_id):
            if "trace" in edge.metadata:
                traces.append(f"  edge→{edge.target}: {edge.metadata['trace']} ({edge.metadata.get('strategy_hint', '')})")

        obs = f"Node {action.node_id} features: {visible}"
        if traces:
            obs += f"\nTrace annotations:\n" + "\n".join(traces)

        self.graph.set_visibility(action.node_id, NodeVisibility.EXPANDED)
        state.budget_remaining -= 1
        evidence_added = []
        if action.node_id not in state.evidence_nodes:
            state.evidence_nodes.append(action.node_id)
            evidence_added.append(action.node_id)
        state.action_history.append(TraversalEvent.make(EventType.INSPECT, obs, node_id=action.node_id, budget_delta=-1, evidence_added=evidence_added))
        return state

    def _execute_get_context(self, state: EnvironmentState) -> EnvironmentState:
        view = self.graph.get_agent_view()
        obs = f"Phase: {self._phase} | At {state.current_node} | Budget: {state.budget_remaining} | Expanded: {len(view['expanded'])} | Evidence: {len(state.evidence_nodes)}"
        state.action_history.append(TraversalEvent.make(EventType.GET_CONTEXT, obs))
        return state

    def _execute_submit(self, state: EnvironmentState, action: Any) -> EnvironmentState:
        state.confidence_history.append(action.confidence)
        if self._phase == "demo":
            # Transition to transfer phase
            self._phase = "transfer"
            self.graph = self._transfer_graph
            obs = "Demo phase complete. Now apply your strategy to the transfer graph."
            state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs))
            # Reset position to transfer graph start
            state.current_node = "t0"
            state.visited_nodes.append("t0")
        else:
            state.episode_done = True
            obs = f"Transfer submitted: '{action.answer}' (confidence={action.confidence:.2f})"
            state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs, episode_done=True))
        return state

    def score_episode(self, state: EnvironmentState, final_answer: str, justification: str = "") -> Dict[str, float]:
        from vigil.scoring.metrics import compute_correctness, compute_efficiency, compute_evidence_quality, compute_calibration, compute_weighted_score
        # Req 14.4: evaluate abstract strategy match, not path identity
        correctness = compute_correctness(final_answer, self._hidden_rule.get("description", ""), self.verify_answer)
        scores = {
            "correctness": correctness,
            "efficiency": compute_efficiency(state, self._graph_config.get("num_nodes", 8)),
            "evidence_quality": compute_evidence_quality(state, self._graph_config.get("num_nodes", 8) // 2),
            "calibration": compute_calibration(state, bool(correctness)),
            "recovery": 0.5,
        }
        scores["final_score"] = compute_weighted_score(scores, self._scoring_weights)
        return scores

    def verify_answer(self, answer: str) -> bool:
        patterns = self._hidden_rule.get("verification_pattern", ["sequence", "ascending", "order", "chain", "follow"])
        return any(p in answer.lower() for p in patterns)
