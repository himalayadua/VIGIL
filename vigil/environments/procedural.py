"""
Procedural Learning Environment — Track 1: Learning (Tower of Hanoi analog).

State-space graph: nodes = procedure states, edges = valid moves.
Model learns valid move sequences through trial and error across 10+ trials.
Key metric: power-law improvement in move count across trials.

Requirements: 15.1, 15.2, 15.3, 15.5
"""

import random
from typing import Any, Dict, List, Optional

from vigil.environments.base import (
    CognitiveEnvironment, EnvironmentState, EventType, TraversalEvent,
)
from vigil.graphs.core import CognitiveGraph, GraphEdge, GraphNode, NodeVisibility


class ProceduralLearningEnv(CognitiveEnvironment):

    MIN_TRIALS = 10

    def __init__(self, scenario_config: Dict[str, Any], difficulty: int = 2, seed: Optional[int] = None):
        self.scenario_config = scenario_config
        self.difficulty = difficulty
        self.seed = seed if seed is not None else random.randint(0, 10000)
        self._rng = random.Random(self.seed)
        self._graph_config = self._get_difficulty_config()
        self._scoring_weights = scenario_config.get("scoring_weights", {})
        self._hidden_rule = scenario_config.get("hidden_rule", {})

        # Build the state-space graph
        self.graph, self._goal_node, self._optimal_path = self._build_state_space()
        self._start_node = self.graph.get_all_node_ids()[0]
        self._current_trial = 0
        self._current_trial_moves = 0
        self._evidence_relevant = {self._goal_node}

    def _get_difficulty_config(self) -> Dict[str, Any]:
        levels = self.scenario_config.get("difficulty_levels", {})
        return levels.get(str(self.difficulty), levels.get("2", {}))

    def _build_state_space(self):
        """
        Build a state-space graph representing a multi-step procedure.
        Nodes = states, edges = valid moves.
        There is one goal state reachable via the optimal path.
        Invalid moves (non-existent edges) return errors.
        """
        depth = self._graph_config.get("procedure_depth", 4)
        branching = self._graph_config.get("branching_factor", 2)

        graph = CognitiveGraph()
        # Build a tree-like state space
        node_counter = [0]

        def make_node():
            nid = f"s{node_counter[0]}"
            node_counter[0] += 1
            graph.add_node(GraphNode(
                node_id=nid,
                features={f"state_{nid}", f"depth_{node_counter[0] % depth}"},
                category="procedure_state",
            ))
            return nid

        # Create the optimal path: s0 → s1 → ... → s(depth)
        path = [make_node() for _ in range(depth + 1)]
        for i in range(depth):
            graph.add_edge(path[i], GraphEdge(source=path[i], target=path[i+1], relation_type="valid_move"))

        # Add distractor branches (dead ends)
        for i in range(depth):
            for _ in range(branching - 1):
                dead_end = make_node()
                graph.add_edge(path[i], GraphEdge(source=path[i], target=dead_end, relation_type="valid_move"))

        goal = path[-1]
        graph.hidden_rule = f"procedure_sequence | goal: {goal}"
        graph.metadata = {"goal_node": goal, "optimal_path": path}
        graph.init_visibility(path[0])
        return graph, goal, path

    def reset(self) -> EnvironmentState:
        budget = self.scenario_config.get("budget", {}).get("base", 20)
        state = EnvironmentState(current_node=self._start_node, budget_remaining=budget)
        state.visited_nodes.append(self._start_node)
        self._current_trial = 0
        self._current_trial_moves = 0
        return state

    def render(self, state: EnvironmentState) -> str:
        view = self.graph.get_agent_view()
        trial_info = f"Trial {self._current_trial + 1}/{self.MIN_TRIALS} | Moves this trial: {self._current_trial_moves}"
        if state.trial_move_counts:
            trial_info += f" | Previous trials: {state.trial_move_counts}"
        if len(state.action_history) > 15:
            history_str = f"[Compressed: {len(state.action_history)} actions]"
        else:
            history_str = f"{len(state.action_history)} actions taken"
        return (
            f"=== Procedural Learning ===\n"
            f"{trial_info}\n"
            f"Current state: {state.current_node} | Budget: {state.budget_remaining}\n"
            f"Goal state: {self._goal_node}\n"
            f"Expanded: {len(view['expanded'])} | {history_str}\n"
            f"Actions: explore:<node_id>(cost 2) | inspect:<node_id>(cost 1) | get_context | submit_answer\n"
            f"Goal: Learn the valid move sequence to reach the goal state. Improve across trials."
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
        """Req 15.2: invalid move (non-existent edge) returns error, no state advance."""
        if state.budget_remaining < 2:
            state.action_history.append(TraversalEvent.make(EventType.ERROR, "Need 2 budget", node_id=action.node_id))
            return state
        neighbors = self.graph.get_neighbors(state.current_node)
        if action.node_id not in neighbors:
            # Req 15.2: invalid move — error, no advance
            state.action_history.append(TraversalEvent.make(
                EventType.ERROR,
                f"Invalid move: '{action.node_id}' is not reachable from '{state.current_node}'",
                node_id=action.node_id,
            ))
            return state

        state.current_node = action.node_id
        state.visited_nodes.append(action.node_id)
        state.budget_remaining -= 2
        self._current_trial_moves += 1
        self.graph.set_visibility(action.node_id, NodeVisibility.EXPANDED)
        for nid in self.graph.get_neighbors(action.node_id):
            self.graph.set_visibility(nid, NodeVisibility.DISCOVERED)

        # Check if goal reached — start new trial
        if action.node_id == self._goal_node:
            state.trial_move_counts.append(self._current_trial_moves)
            state.evidence_nodes.append(action.node_id)
            self._current_trial += 1
            self._current_trial_moves = 0
            # Reset to start for next trial
            state.current_node = self._start_node
            obs = f"GOAL REACHED in {state.trial_move_counts[-1]} moves! Trial {self._current_trial} complete. Resetting to start."
        else:
            obs = f"Moved to {action.node_id}. Neighbors: {self.graph.get_neighbors(action.node_id)}"

        state.action_history.append(TraversalEvent.make(EventType.EXPLORE, obs, node_id=action.node_id, budget_delta=-2))
        return state

    def _execute_inspect(self, state: EnvironmentState, action: Any) -> EnvironmentState:
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
        obs = f"State {action.node_id}: {visible}. Valid moves: {self.graph.get_neighbors(action.node_id)}"
        self.graph.set_visibility(action.node_id, NodeVisibility.EXPANDED)
        state.budget_remaining -= 1
        state.action_history.append(TraversalEvent.make(EventType.INSPECT, obs, node_id=action.node_id, budget_delta=-1))
        return state

    def _execute_get_context(self, state: EnvironmentState) -> EnvironmentState:
        obs = (
            f"Trial {self._current_trial + 1} | Moves: {self._current_trial_moves} | "
            f"Budget: {state.budget_remaining} | Goal: {self._goal_node} | "
            f"Trial history: {state.trial_move_counts}"
        )
        state.action_history.append(TraversalEvent.make(EventType.GET_CONTEXT, obs))
        return state

    def _execute_submit(self, state: EnvironmentState, action: Any) -> EnvironmentState:
        state.confidence_history.append(action.confidence)
        state.episode_done = True
        # Req 15.5: evaluate whether submitted sequence reaches goal
        reached_goal = self._goal_node in action.answer or str(self._goal_node) in action.justification
        obs = f"Submitted sequence. Goal reached in answer: {reached_goal}. Trials completed: {len(state.trial_move_counts)}"
        state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs, episode_done=True))
        return state

    def score_episode(self, state: EnvironmentState, final_answer: str, justification: str = "") -> Dict[str, float]:
        from vigil.scoring.metrics import compute_correctness, compute_efficiency, compute_evidence_quality, compute_calibration, compute_weighted_score
        correctness = compute_correctness(final_answer, self._hidden_rule.get("description", ""), self.verify_answer)
        # Req 15.4: LR via power-law fit of move count vs trial number
        lr_bonus = self._compute_learning_rate_bonus(state.trial_move_counts)
        correctness = min(1.0, correctness + lr_bonus * 0.3)
        scores = {
            "correctness": correctness,
            "efficiency": compute_efficiency(state, len(self._optimal_path) * self.MIN_TRIALS),
            "evidence_quality": compute_evidence_quality(state, self.MIN_TRIALS),
            "calibration": compute_calibration(state, bool(correctness)),
            "recovery": 0.5,
        }
        scores["final_score"] = compute_weighted_score(scores, self._scoring_weights)
        return scores

    def _compute_learning_rate_bonus(self, trial_counts: List[int]) -> float:
        """Compute improvement slope across trials (power-law proxy)."""
        if len(trial_counts) < 3:
            return 0.0
        # Simple: compare first third vs last third
        n = len(trial_counts)
        first_avg = sum(trial_counts[:n//3]) / (n//3)
        last_avg = sum(trial_counts[-(n//3):]) / (n//3)
        if first_avg <= 0:
            return 0.0
        improvement = (first_avg - last_avg) / first_avg
        return max(0.0, min(1.0, improvement))

    def verify_answer(self, answer: str) -> bool:
        patterns = self._hidden_rule.get("verification_pattern", ["goal", "sequence", "procedure", self._goal_node])
        return any(p in answer.lower() for p in patterns)
