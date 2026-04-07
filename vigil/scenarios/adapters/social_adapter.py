"""
SocialAdapter — Track 5 (social_cognition) authored schema validator and compiler.

Kaggle Track 5 = Social Cognition.

Real authored schema (vigil_track5_social_scenarios_from_skeletons_v1.json):
  scenario_id, cognitive_track, task_frame, hidden_mechanism, causal_chain,
  red_herrings, disconfirmation_moment, nodes, edges, track5_validation_notes

Field mapping (authored → canonical):
  task_frame                                 → opening_prompt
  hidden_mechanism                           → answer_targets["hidden_mechanism"]
  causal_chain                               → track_metadata["causal_chain"]
  red_herrings                               → track_metadata["red_herrings"]
  disconfirmation_moment                     → track_metadata["disconfirmation_moment"]
  track5_validation_notes                    → track_metadata["track5_validation_notes"]
  nodes[].id                                 → node.node_id
  nodes[].label                              → node.label + summary_text
  nodes[].kind                               → node.node_type
  nodes[].visibility                         → node.initial_visibility
  edges[].source                             → edge.from_id
  edges[].target                             → edge.to_id
  edges[].relation                           → edge.relation

Requirements: 2, 3, 13
"""

from typing import Any, Dict, List

from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)

# Visibility mapping from authored values to canonical RuntimeNode values
_VIS_MAP = {
    "visible": "visible",
    "discoverable": "hidden",   # discoverable = hidden until explored
    "hidden": "hidden",
    "initial": "initial",
}


class SocialAdapter:
    """
    Validates and compiles Track 5 (social_cognition) authored scenarios.

    Matches the real schema in vigil_track5_social_scenarios_from_skeletons_v1.json.

    Usage (via ScenarioCatalog — not called directly):
        adapter = SocialAdapter()
        adapter.validate(raw, scenario_id)
        spec = adapter.compile(raw)
    """

    TRACK_ID = "social_cognition"

    _REQUIRED_FIELDS = [
        "scenario_id",
        "cognitive_track",
        "task_frame",
        "nodes",
        "edges",
    ]

    def validate(self, raw: Dict[str, Any], scenario_id: str) -> None:
        """
        Validate a raw authored dict against the Track 5 schema.

        Raises:
            ValueError: With the name of the first missing or invalid field.
        """
        for field in self._REQUIRED_FIELDS:
            if field not in raw:
                raise ValueError(
                    f"Scenario '{scenario_id}' (social_cognition) missing required field '{field}'"
                )

    def compile(self, raw: Dict[str, Any]) -> RuntimeScenarioSpec:
        """
        Compile a validated Track 5 authored dict into a RuntimeScenarioSpec.
        """
        nodes = self._compile_nodes(raw["nodes"])
        edges = self._compile_edges(raw["edges"])

        # Entry nodes: visible ones first, then first node as fallback
        entry_nodes = [n.node_id for n in nodes if n.initial_visibility == "visible"]
        if not entry_nodes:
            entry_nodes = [nodes[0].node_id] if nodes else []

        # Evidence targets: nodes with kind "evidence"
        evidence_targets = [n.node_id for n in nodes if n.node_type == "evidence"]

        return RuntimeScenarioSpec(
            scenario_id=raw["scenario_id"],
            cognitive_track="social_cognition",
            opening_prompt=raw.get("task_frame", ""),
            nodes=nodes,
            edges=edges,
            entry_node_ids=entry_nodes,
            answer_targets={
                "hidden_mechanism": raw.get("hidden_mechanism", ""),
                "disconfirmation_moment": raw.get("disconfirmation_moment", ""),
            },
            evidence_targets=evidence_targets,
            optimal_path=[],
            optimal_steps=0,
            runtime_config=RuntimeConfig(action_budget=20),
            scoring_weights={
                "correctness": 0.30,
                "partner_model_accuracy": 0.20,
                "social_repair_quality": 0.15,
                "trust_calibration": 0.15,
                "communication_appropriateness": 0.10,
                "information_asymmetry_exploitation": 0.10,
            },
            evaluation_conditions=EvaluationConditions(),
            track_metadata={
                "causal_chain": raw.get("causal_chain", []),
                "red_herrings": raw.get("red_herrings", []),
                "disconfirmation_moment": raw.get("disconfirmation_moment", ""),
                "track5_validation_notes": raw.get("track5_validation_notes", {}),
                "primary_sub_abilities": raw.get("primary_sub_abilities", []),
                "secondary_sub_abilities": raw.get("secondary_sub_abilities", []),
                "title": raw.get("title", ""),
                "synthetic_domain": raw.get("synthetic_domain", ""),
                # Social scoring fields (empty until agent interaction layer is added)
                "agent_nodes": [],
                "private_knowledge": {},
                "agent_responses": {},
            },
        )

    @staticmethod
    def _compile_nodes(raw_nodes: list) -> List[RuntimeNode]:
        """Map authored Track 5 node dicts to RuntimeNode objects."""
        nodes = []
        for n in raw_nodes:
            node_id = n.get("id", "")
            label = n.get("label", node_id)
            vis = _VIS_MAP.get(str(n.get("visibility", "hidden")).lower(), "hidden")
            nodes.append(RuntimeNode(
                node_id=node_id,
                label=label,
                summary_text=label,
                inspection_detail=label,
                node_type=n.get("kind", "standard"),
                initial_visibility=vis,
                metadata={
                    "kind": n.get("kind", "standard"),
                    "visibility_authored": n.get("visibility", "hidden"),
                },
            ))
        return nodes

    @staticmethod
    def _compile_edges(raw_edges: list) -> List[RuntimeEdge]:
        """Map authored Track 5 edge dicts to RuntimeEdge objects."""
        edges = []
        for e in raw_edges:
            edges.append(RuntimeEdge(
                from_id=e.get("source", ""),
                to_id=e.get("target", ""),
                relation=e.get("relation", ""),
            ))
        return edges
