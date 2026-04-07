"""
GraphScenarioEnvironment — shared runtime for all five cognitive tracks.

Replaces the six bespoke Track 1 environment classes as the primary runtime.
Accepts a RuntimeScenarioSpec and executes any authored scenario from any
track using the same action loop, fog-of-war POMDP, and event-sourced state.

Key differences from the old environments:
  - explore cost is edge.traversal_cost (default 1), not fixed 2
  - inspect cost is spec.runtime_config.action_costs["inspect"] (default 1)
  - budget_remaining starts from spec.runtime_config.action_budget
  - score_episode() returns a ScoreCard (no "vis" key) — VISScorer wraps it
  - opening observation uses spec.opening_prompt (authored blind framing)
  - evidence nodes identified from spec.evidence_targets (authored metadata)

Event log contract:
  Each execute_action() call appends ONE primary TraversalEvent for the model
  action (including failed/invalid actions), plus ZERO OR MORE system
  TraversalEvents for triggered system events (CONTRADICTION, etc.).
  System events never consume budget.

Requirements: 4, 5, 6, 7, 9, 20
"""

import time
from typing import Any, Dict, List, Optional

from vigil.actions.schemas import (
    ActionParseError,
    ExploreAction,
    GetContextAction,
    InspectAction,
    SubmitAnswerAction,
)
from vigil.environments.base import (
    CognitiveEnvironment,
    EnvironmentState,
    EventType,
    TraversalEvent,
)
from vigil.graphs.core import CognitiveGraph, NodeVisibility
from vigil.scenarios.runtime_spec import RuntimeScenarioSpec
from vigil.scoring.track_scorers import TrackScorer


class GraphScenarioEnvironment(CognitiveEnvironment):
    """
    Shared runtime environment for all five cognitive tracks.

    Usage:
        spec = catalog.load("vigil_eco_01_kethara_succession")
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        state = env.execute_action(state, ExploreAction(...))
        scorecard = env.score_episode(state, answer, justification)
        # scorecard has no "vis" key — pass to VISScorer for final float
    """

    def __init__(self, spec: RuntimeScenarioSpec) -> None:
        """
        Initialise with a compiled RuntimeScenarioSpec.

        Builds the CognitiveGraph from spec nodes/edges and instantiates
        the appropriate TrackScorer for this scenario's cognitive_track.
        """
        self.spec = spec
        self.graph = CognitiveGraph.from_spec(spec)
        self._scorer = TrackScorer.for_track(spec.cognitive_track, spec)
        # Expose scenario_config dict for backward compat with VISScorer
        self.scenario_config = spec.to_scenario_config_dict()

    # ------------------------------------------------------------------
    # CognitiveEnvironment ABC — required methods
    # ------------------------------------------------------------------

    def reset(self) -> EnvironmentState:
        """
        Reset to initial episode state.

        - Initialises fog-of-war visibility from spec.nodes[].initial_visibility
        - Sets current_node to spec.entry_node_ids[0]
        - Sets budget_remaining from spec.runtime_config.action_budget (NOT optimal_steps)
        - All new EnvironmentState fields initialised to empty
        """
        self.graph.init_visibility_from_spec(self.spec)

        entry = self.spec.entry_node_ids[0] if self.spec.entry_node_ids else ""
        state = EnvironmentState(
            current_node=entry,
            budget_remaining=self.spec.runtime_config.action_budget,
        )
        # Mark entry node as visited
        if entry:
            state.visited_nodes.append(entry)
        return state

    def execute_action(
        self,
        state: EnvironmentState,
        action: Any,
    ) -> EnvironmentState:
        """
        Execute one action and return updated state.

        Event log contract:
          - Always appends exactly ONE primary TraversalEvent for the model action.
          - May append additional system TraversalEvents (CONTRADICTION, etc.) after.
          - Budget is only deducted for the primary action event.
          - System events never consume budget.
        """
        # Handle parse errors — append ERROR event, no state change, no budget
        if isinstance(action, ActionParseError):
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.ERROR,
                observation=f"[ERROR] Could not parse action: {action.error}",
                params={"raw": str(action.raw), "error": action.error},
            ))
            return state

        # Enforce evaluation_conditions.tool_policy
        # When tool_policy = "none", reject any action that invokes an external tool.
        # Track-specific actions (ask_for_help, send_message, make_commitment) are
        # part of the benchmark interface and are always permitted by design.
        # Only truly external tools (not in allowed_tools) are blocked.
        ec = self.spec.evaluation_conditions
        if ec.tool_policy == "none" and ec.allowed_tools == []:
            action_type = getattr(action, "action_type", "")
            # The four base actions + three track-specific actions are all interface actions
            _INTERFACE_ACTIONS = {
                "explore", "inspect", "get_context", "submit_answer",
                "ask_for_help", "send_message", "make_commitment",
            }
            if action_type and action_type not in _INTERFACE_ACTIONS:
                state.action_history.append(TraversalEvent.make(
                    event_type=EventType.ERROR,
                    observation=(
                        f"[ERROR] Action '{action_type}' is not permitted under "
                        f"tool_policy='none'. Allowed interface actions: {sorted(_INTERFACE_ACTIONS)}"
                    ),
                    params={"action_type": action_type, "tool_policy": ec.tool_policy},
                ))
                return state

        # Dispatch to the appropriate handler
        if isinstance(action, ExploreAction):
            return self._execute_explore(state, action)
        elif isinstance(action, InspectAction):
            return self._execute_inspect(state, action)
        elif isinstance(action, GetContextAction):
            return self._execute_get_context(state, action)
        elif isinstance(action, SubmitAnswerAction):
            return self._execute_submit(state, action)
        else:
            # Unknown action type — treat as error
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.ERROR,
                observation=f"[ERROR] Unknown action type: {type(action).__name__}",
                params={"action_type": str(type(action).__name__)},
            ))
            return state

    def score_episode(
        self,
        state: EnvironmentState,
        final_answer: str,
        justification: str,
    ) -> Dict[str, Any]:
        """
        Compute track-specific ScoreCard for the episode.

        Returns a ScoreCard dict — does NOT contain a "vis" key.
        The task loop passes this to VISScorer.score_episode() to get the
        final VISResult with the leaderboard float.
        """
        scorecard = self._scorer.score(state, final_answer, justification, self.spec)
        # Guarantee no "vis" key leaks through
        scorecard.pop("vis", None)
        return scorecard

    def render(self, state: EnvironmentState) -> str:
        """
        Produce a compact observation string for the current state.

        At step 0: includes spec.opening_prompt as system context.
        After step 15: compresses action history to a summary.
        """
        lines = []

        # System context (opening prompt) at step 0
        if not state.action_history:
            lines.append(self.spec.opening_prompt)
            lines.append("")

        # Current position
        current = self.graph.get_node(state.current_node)
        if current:
            summary = current.metadata.get("summary_text", "")
            lines.append(f"[Current node: {state.current_node}] {summary}")
        else:
            lines.append(f"[Current node: {state.current_node}]")

        # Budget
        lines.append(f"[Budget remaining: {state.budget_remaining}]")

        # Visible neighbors
        neighbors = self.graph.get_neighbors(state.current_node)
        visible_neighbors = [
            n for n in neighbors
            if self.graph.get_visibility(n) != NodeVisibility.UNEXPLORED
        ]
        if visible_neighbors:
            lines.append(f"[Visible neighbors: {', '.join(visible_neighbors)}]")
        else:
            lines.append("[No visible neighbors yet — use explore to reveal them]")

        # Action history (compressed when long)
        n_actions = len(state.action_history)
        if n_actions > 0:
            lines.append("")
            if n_actions > 15:
                # Compressed summary
                evidence_count = len(state.evidence_nodes)
                visited_count = len(state.visited_nodes)
                lines.append(
                    f"[History: {n_actions} actions taken, "
                    f"{visited_count} nodes visited, "
                    f"{evidence_count} evidence nodes found]"
                )
            else:
                lines.append("[Recent actions:]")
                for event in state.action_history[-5:]:
                    lines.append(f"  {event.event_type.value}: {event.observation[:80]}")

        return "\n".join(lines)

    def verify_answer(self, answer: str) -> bool:
        """
        Check if the submitted answer matches the ground-truth answer targets.

        Uses spec.answer_targets["correct_root_cause"] for learning scenarios.
        """
        targets = self.spec.answer_targets
        correct = targets.get("correct_root_cause", "")
        if correct:
            return answer.strip().upper() == correct.strip().upper()
        # Fallback: check any answer_targets value
        return any(
            answer.strip().upper() == str(v).strip().upper()
            for v in targets.values()
            if isinstance(v, str)
        )

    def replay(self, events: List[TraversalEvent], seed: int) -> EnvironmentState:
        """
        Reconstruct EnvironmentState deterministically by replaying events.

        Handles all EventType values including system events (CONTRADICTION,
        RELEVANCE_SHIFT, etc.) by re-evaluating trigger conditions rather than
        re-executing them as model actions.
        """
        # Re-apply seed perturbation if needed
        if seed != 0:
            perturbed_spec = self.spec.apply_seed_perturbation(seed)
            self.graph = CognitiveGraph.from_spec(perturbed_spec)
            self.spec = perturbed_spec
            self._scorer = TrackScorer.for_track(perturbed_spec.cognitive_track, perturbed_spec)

        state = self.reset()

        for event in events:
            # Skip system events — they are re-triggered by the primary actions
            if event.event_type in (
                EventType.ERROR,
            ):
                continue
            # Skip system events that have no corresponding model action
            if hasattr(EventType, event.event_type.value.upper()):
                et = event.event_type
                system_events = {
                    "contradiction", "relevance_shift", "subgoal_complete",
                    "replan_triggered", "constraint_violated", "help_requested",
                    "message_sent", "commitment_made",
                }
                if et.value in system_events:
                    continue

            params = event.params or {}
            action: Any = None

            if event.event_type == EventType.EXPLORE:
                action = ExploreAction(
                    action_type="explore",
                    node_id=event.node_id or params.get("node_id", ""),
                )
            elif event.event_type == EventType.INSPECT:
                action = InspectAction(
                    action_type="inspect",
                    node_id=event.node_id or params.get("node_id", ""),
                )
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

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _execute_explore(
        self, state: EnvironmentState, action: ExploreAction
    ) -> EnvironmentState:
        """Move to a neighboring node, deducting edge.traversal_cost."""
        node_id = action.node_id

        # Validate: node must exist
        if node_id not in self.graph.nodes:
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.ERROR,
                observation=f"[ERROR] Node '{node_id}' does not exist in the graph.",
                node_id=node_id,
                params=action.model_dump(),
            ))
            return state

        # Validate: node must be a direct neighbor of current node
        neighbors = self.graph.get_neighbors(state.current_node)
        if node_id not in neighbors:
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.ERROR,
                observation=(
                    f"[ERROR] Node '{node_id}' is not reachable from '{state.current_node}'. "
                    f"Reachable neighbors: {neighbors}"
                ),
                node_id=node_id,
                params=action.model_dump(),
            ))
            return state

        # Validate: budget
        edge = self._find_edge(state.current_node, node_id)
        cost = edge.metadata.get("traversal_cost", 1) if edge else 1
        if state.budget_remaining < cost:
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.ERROR,
                observation=f"[ERROR] Insufficient budget ({state.budget_remaining}) for explore (cost {cost}).",
                node_id=node_id,
                params=action.model_dump(),
            ))
            return state

        # Execute: move, deduct cost, update visibility
        state.budget_remaining -= cost
        state.current_node = node_id
        if node_id not in state.visited_nodes:
            state.visited_nodes.append(node_id)

        # Expand target node and discover its neighbors
        visibility_changes: Dict[str, str] = {}
        self.graph.set_visibility(node_id, NodeVisibility.EXPANDED)
        visibility_changes[node_id] = "expanded"

        new_neighbors = self.graph.get_neighbors(node_id)
        for nb in new_neighbors:
            if self.graph.get_visibility(nb) == NodeVisibility.UNEXPLORED:
                self.graph.set_visibility(nb, NodeVisibility.DISCOVERED)
                visibility_changes[nb] = "discovered"
                if nb not in state.discovered_nodes if hasattr(state, "discovered_nodes") else True:
                    pass

        # Build observation
        reveal_text = edge.metadata.get("reveal_text", "") if edge else ""
        node = self.graph.get_node(node_id)
        summary = node.metadata.get("summary_text", "") if node else ""
        obs_parts = [f"[Moved to {node_id}]"]
        if reveal_text:
            obs_parts.append(reveal_text)
        if summary:
            obs_parts.append(summary)
        obs_parts.append(f"[Neighbors: {', '.join(new_neighbors) or 'none'}]")
        observation = " ".join(obs_parts)

        state.action_history.append(TraversalEvent.make(
            event_type=EventType.EXPLORE,
            observation=observation,
            node_id=node_id,
            params=action.model_dump(),
            budget_delta=-cost,
            visibility_changes=visibility_changes,
        ))

        # Check budget exhaustion
        if state.budget_remaining <= 0:
            state.episode_done = True

        return state

    def _execute_inspect(
        self, state: EnvironmentState, action: InspectAction
    ) -> EnvironmentState:
        """Reveal full inspection_detail of a node, deducting inspect cost."""
        node_id = action.node_id

        # Validate: node must exist
        if node_id not in self.graph.nodes:
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.ERROR,
                observation=f"[ERROR] Node '{node_id}' does not exist.",
                node_id=node_id,
                params=action.model_dump(),
            ))
            return state

        # Validate: node must not be UNEXPLORED
        if self.graph.get_visibility(node_id) == NodeVisibility.UNEXPLORED:
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.ERROR,
                observation=f"[ERROR] Node '{node_id}' is unexplored. Explore it first.",
                node_id=node_id,
                params=action.model_dump(),
            ))
            return state

        # Validate: budget
        cost = self.spec.runtime_config.action_costs.get("inspect", 1)
        if state.budget_remaining < cost:
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.ERROR,
                observation=f"[ERROR] Insufficient budget ({state.budget_remaining}) for inspect (cost {cost}).",
                node_id=node_id,
                params=action.model_dump(),
            ))
            return state

        # Execute: deduct cost, expand node, record evidence
        state.budget_remaining -= cost
        self.graph.set_visibility(node_id, NodeVisibility.EXPANDED)

        node = self.graph.get_node(node_id)
        detail = node.metadata.get("inspection_detail", "") if node else ""
        observation = f"[Inspected {node_id}] {detail}"

        # Track evidence
        evidence_added: List[str] = []
        if node_id in self.spec.evidence_targets and node_id not in state.evidence_nodes:
            state.evidence_nodes.append(node_id)
            evidence_added.append(node_id)

        # Track inspected_nodes (new field from task 9)
        if hasattr(state, "inspected_nodes") and node_id not in state.inspected_nodes:
            state.inspected_nodes.append(node_id)

        state.action_history.append(TraversalEvent.make(
            event_type=EventType.INSPECT,
            observation=observation,
            node_id=node_id,
            params=action.model_dump(),
            budget_delta=-cost,
            visibility_changes={node_id: "expanded"},
            evidence_added=evidence_added,
        ))

        # Check budget exhaustion
        if state.budget_remaining <= 0:
            state.episode_done = True

        return state

    def _execute_get_context(
        self, state: EnvironmentState, action: GetContextAction
    ) -> EnvironmentState:
        """Return compressed state summary. Free action (no budget cost)."""
        agent_view = self.graph.get_agent_view()
        n_expanded = len(agent_view.get("expanded", {}))
        n_discovered = len(agent_view.get("discovered", {}))

        observation = (
            f"[Context] Position: {state.current_node} | "
            f"Budget: {state.budget_remaining} | "
            f"Visited: {len(state.visited_nodes)} nodes | "
            f"Evidence: {len(state.evidence_nodes)} nodes | "
            f"Known graph: {n_expanded} expanded, {n_discovered} discovered"
        )

        state.action_history.append(TraversalEvent.make(
            event_type=EventType.GET_CONTEXT,
            observation=observation,
            params={},
        ))
        return state

    def _execute_submit(
        self, state: EnvironmentState, action: SubmitAnswerAction
    ) -> EnvironmentState:
        """Submit final answer and end the episode. Free action."""
        state.confidence_history.append(action.confidence)
        state.episode_done = True

        observation = (
            f"[Submitted] Answer: {action.answer[:100]} | "
            f"Confidence: {action.confidence:.2f}"
        )

        state.action_history.append(TraversalEvent.make(
            event_type=EventType.SUBMIT_ANSWER,
            observation=observation,
            params=action.model_dump(),
            episode_done=True,
        ))
        return state

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def run_human_session(self, input_fn: Any) -> EnvironmentState:
        """
        Run one episode with a human participant.

        Displays evaluation_conditions at session start and enforces the same
        tool_policy as the automated task loop, ensuring matched conditions
        for valid human-baseline comparison per the DeepMind 3-stage protocol.

        Args:
            input_fn: Callable (obs: str) -> Any returning a raw action.

        Returns:
            Final EnvironmentState after the human session ends.
        """
        from vigil.actions.parser import parse_action

        ec = self.spec.evaluation_conditions
        # Display evaluation conditions to human participant at session start
        conditions_notice = (
            f"\n[EVALUATION CONDITIONS]\n"
            f"  Tool policy: {ec.tool_policy}\n"
            f"  Allowed tools: {ec.allowed_tools or 'none'}\n"
            f"  Response format: {ec.response_format}\n"
            f"  Interface mode: {ec.interface_mode}\n"
        )

        state = self.reset()
        # Inject conditions notice into first observation
        first_obs = self.render(state)
        first_obs_with_conditions = conditions_notice + first_obs

        for _turn in range(20):
            if state.episode_done or state.budget_remaining <= 0:
                break

            obs = first_obs_with_conditions if _turn == 0 else self.render(state)
            raw_input = input_fn(obs)
            action = parse_action(raw_input)
            state = self.execute_action(state, action)  # enforces tool_policy

            if state.episode_done:
                break

        return state

    def _find_edge(self, from_id: str, to_id: str):
        """Find the GraphEdge from from_id to to_id, or None."""
        for edge in self.graph.get_edges_from(from_id):
            if edge.target == to_id:
                return edge
        return None
