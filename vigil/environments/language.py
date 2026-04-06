"""
Language Learning Environment — Track 1: Learning (Reber Grammar analog).

A novel finite-state grammar is procedurally generated from the episode seed.
Valid traversal paths = grammatical strings. Invalid paths = ungrammatical.

Three phases:
  1. Exemplar phase: 20 valid paths shown to the model via the graph
  2. Classification phase: model classifies novel paths as grammatical/ungrammatical
  3. Transfer phase: same grammar, fully relabelled node IDs and features

Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
"""

import random
from typing import Any, Dict, List, Optional, Set, Tuple

from vigil.environments.base import (
    CognitiveEnvironment, EnvironmentState, EventType, TraversalEvent,
)
from vigil.graphs.core import CognitiveGraph, GraphEdge, GraphNode, NodeVisibility


class LanguageLearningEnv(CognitiveEnvironment):

    NUM_EXEMPLARS = 20

    def __init__(self, scenario_config: Dict[str, Any], difficulty: int = 2, seed: Optional[int] = None):
        self.scenario_config = scenario_config
        self.difficulty = difficulty
        self.seed = seed if seed is not None else random.randint(0, 10000)
        self._rng = random.Random(self.seed)
        self._graph_config = self._get_difficulty_config()
        self._scoring_weights = scenario_config.get("scoring_weights", {})
        self._hidden_rule = scenario_config.get("hidden_rule", {})

        # Req 16.5: generate FSM grammar from seed (not from training corpora)
        self._fsm, self._start_state, self._accept_states = self._generate_fsm()
        # Build the graph encoding the FSM
        self.graph = self._build_fsm_graph(self._fsm, self._start_state, prefix="g")
        # Generate exemplar paths
        self._exemplars = self._generate_exemplars(self.NUM_EXEMPLARS)
        # Generate classification trials (mix of grammatical and ungrammatical)
        self._trials = self._generate_trials(10)
        self._current_trial_idx = 0
        self._correct_classifications = 0
        self._phase = "exemplar"  # "exemplar" → "classify" → "transfer"
        # Transfer graph: same FSM, relabelled
        self._transfer_graph = self._build_fsm_graph(self._fsm, self._start_state, prefix="t")
        self._evidence_relevant = set(self.graph.nodes.keys())

    def _get_difficulty_config(self) -> Dict[str, Any]:
        levels = self.scenario_config.get("difficulty_levels", {})
        return levels.get(str(self.difficulty), levels.get("2", {}))

    def _generate_fsm(self) -> Tuple[Dict, str, Set[str]]:
        """
        Req 16.5: Generate a novel FSM from seed.
        States are abstract symbols (S0, S1, ...) with seeded transitions.
        The grammar cannot be derived from training data.
        """
        num_states = self._graph_config.get("num_states", 5)
        # Abstract alphabet — symbols not in any natural language
        alphabet = [f"X{i}" for i in range(4)]

        states = [f"S{i}" for i in range(num_states)]
        start = states[0]
        # Accept states: last 1-2 states
        accept = set(states[-2:])

        # Build random transitions (seeded)
        fsm: Dict[str, Dict[str, str]] = {s: {} for s in states}
        for s in states[:-1]:  # last state has no outgoing transitions
            symbols = self._rng.sample(alphabet, self._rng.randint(1, len(alphabet)))
            for sym in symbols:
                target = self._rng.choice(states[1:])  # never go back to start
                fsm[s][sym] = target

        return fsm, start, accept

    def _build_fsm_graph(self, fsm: Dict, start: str, prefix: str) -> CognitiveGraph:
        """Build a CognitiveGraph encoding the FSM transitions."""
        graph = CognitiveGraph()
        for state in fsm:
            nid = f"{prefix}_{state}"
            graph.add_node(GraphNode(
                node_id=nid,
                features={f"{prefix}_state_{state}", f"abstract_{hash(state) % 100}"},
                category="fsm_state",
            ))
        for state, transitions in fsm.items():
            src = f"{prefix}_{state}"
            for symbol, target_state in transitions.items():
                tgt = f"{prefix}_{target_state}"
                graph.add_edge(src, GraphEdge(source=src, target=tgt, relation_type=symbol))

        graph.hidden_rule = f"fsm_grammar | accept_states: {self._accept_states}"
        graph.metadata = {"fsm": {k: v for k, v in fsm.items()}, "accept_states": list(self._accept_states)}
        graph.init_visibility(f"{prefix}_{start}")
        return graph

    def _generate_exemplars(self, n: int) -> List[List[str]]:
        """Generate n valid (grammatical) paths through the FSM."""
        exemplars = []
        attempts = 0
        while len(exemplars) < n and attempts < n * 10:
            attempts += 1
            path = self._random_fsm_path(grammatical=True)
            if path and path not in exemplars:
                exemplars.append(path)
        return exemplars

    def _generate_trials(self, n: int) -> List[Tuple[List[str], bool]]:
        """Generate n classification trials: (path, is_grammatical)."""
        trials = []
        for i in range(n):
            grammatical = (i % 2 == 0)
            path = self._random_fsm_path(grammatical=grammatical)
            if path:
                trials.append((path, grammatical))
        return trials

    def _random_fsm_path(self, grammatical: bool, max_len: int = 6) -> Optional[List[str]]:
        """Generate a random path that is grammatical or ungrammatical."""
        state = self._start_state
        path = [state]
        for _ in range(max_len):
            transitions = self._fsm.get(state, {})
            if not transitions:
                break
            symbol = self._rng.choice(list(transitions.keys()))
            state = transitions[symbol]
            path.append(state)
            if state in self._accept_states and grammatical:
                return path
        if not grammatical:
            # Make it ungrammatical by appending an invalid state
            path.append("INVALID")
            return path
        return None

    def reset(self) -> EnvironmentState:
        self._phase = "exemplar"
        self.graph = self._build_fsm_graph(self._fsm, self._start_state, prefix="g")
        self._current_trial_idx = 0
        self._correct_classifications = 0
        budget = self.scenario_config.get("budget", {}).get("base", 20)
        start = f"g_{self._start_state}"
        state = EnvironmentState(current_node=start, budget_remaining=budget)
        state.visited_nodes.append(start)
        return state

    def render(self, state: EnvironmentState) -> str:
        view = self.graph.get_agent_view()
        if self._phase == "exemplar":
            phase_msg = f"EXEMPLAR PHASE: Explore the grammar graph. {self.NUM_EXEMPLARS} valid paths exist."
            exemplar_preview = f"Example valid path: {' → '.join(self._exemplars[0])}" if self._exemplars else ""
        elif self._phase == "classify":
            trial = self._trials[self._current_trial_idx] if self._current_trial_idx < len(self._trials) else None
            path_str = " → ".join(trial[0]) if trial else "N/A"
            phase_msg = f"CLASSIFY PHASE (trial {self._current_trial_idx + 1}/{len(self._trials)}): Is this path grammatical? {path_str}"
            exemplar_preview = f"Correct so far: {self._correct_classifications}/{self._current_trial_idx}"
        else:
            phase_msg = "TRANSFER PHASE: Same grammar, new node labels. Apply what you learned."
            exemplar_preview = ""
        if len(state.action_history) > 15:
            history_str = f"[Compressed: {len(state.action_history)} actions]"
        else:
            history_str = f"{len(state.action_history)} actions taken"
        return (
            f"=== Language Learning ({self._phase.upper()}) ===\n"
            f"{phase_msg}\n"
            f"{exemplar_preview}\n"
            f"Current: {state.current_node} | Budget: {state.budget_remaining}\n"
            f"Expanded: {len(view['expanded'])} | {history_str}\n"
            f"Actions: explore:<node_id>(cost 2) | inspect:<node_id>(cost 1) | get_context | submit_answer\n"
            f"submit_answer: use 'grammatical' or 'ungrammatical' as your answer in classify phase."
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
        obs = f"Moved to {action.node_id}. Outgoing transitions: {self.graph.get_edge_types(action.node_id)}"
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
        transitions = [(e.relation_type, e.target) for e in self.graph.get_edges_from(action.node_id)]
        obs = f"State {action.node_id}: {visible}. Transitions: {transitions}"
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
        obs = f"Phase: {self._phase} | At {state.current_node} | Budget: {state.budget_remaining} | Expanded: {len(view['expanded'])}"
        state.action_history.append(TraversalEvent.make(EventType.GET_CONTEXT, obs))
        return state

    def _execute_submit(self, state: EnvironmentState, action: Any) -> EnvironmentState:
        state.confidence_history.append(action.confidence)
        if self._phase == "exemplar":
            # Req 16.2: after exemplar phase, move to classify
            self._phase = "classify"
            obs = f"Exemplar phase complete. Now classify {len(self._trials)} paths as grammatical/ungrammatical."
            state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs))
        elif self._phase == "classify":
            # Req 16.3: evaluate classification
            if self._current_trial_idx < len(self._trials):
                _, is_grammatical = self._trials[self._current_trial_idx]
                predicted = "grammatical" in action.answer.lower()
                if predicted == is_grammatical:
                    self._correct_classifications += 1
                self._current_trial_idx += 1
                if self._current_trial_idx >= len(self._trials):
                    # Req 16.4: move to transfer phase
                    self._phase = "transfer"
                    self.graph = self._transfer_graph
                    obs = f"Classification complete ({self._correct_classifications}/{len(self._trials)} correct). Transfer phase: same grammar, new labels."
                    state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs))
                else:
                    obs = f"Trial {self._current_trial_idx}: {'correct' if predicted == is_grammatical else 'incorrect'}. Next trial ready."
                    state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs))
            else:
                state.episode_done = True
                obs = "All trials complete."
                state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs, episode_done=True))
        else:
            # Transfer phase final submission
            state.episode_done = True
            obs = f"Transfer submitted: '{action.answer}' (confidence={action.confidence:.2f})"
            state.action_history.append(TraversalEvent.make(EventType.SUBMIT_ANSWER, obs, episode_done=True))
        return state

    def score_episode(self, state: EnvironmentState, final_answer: str, justification: str = "") -> Dict[str, float]:
        from vigil.scoring.metrics import compute_correctness, compute_efficiency, compute_evidence_quality, compute_calibration, compute_weighted_score
        # Classification accuracy is the primary correctness signal
        if len(self._trials) > 0:
            correctness = self._correct_classifications / len(self._trials)
        else:
            correctness = compute_correctness(final_answer, self._hidden_rule.get("description", ""), self.verify_answer)
        scores = {
            "correctness": correctness,
            "efficiency": compute_efficiency(state, self.NUM_EXEMPLARS + len(self._trials)),
            "evidence_quality": compute_evidence_quality(state, len(self._fsm)),
            "calibration": compute_calibration(state, correctness > 0.5),
            "recovery": 0.5,
        }
        scores["final_score"] = compute_weighted_score(scores, self._scoring_weights)
        return scores

    def verify_answer(self, answer: str) -> bool:
        patterns = self._hidden_rule.get("verification_pattern", ["grammatical", "grammar", "pattern", "rule"])
        return any(p in answer.lower() for p in patterns)
