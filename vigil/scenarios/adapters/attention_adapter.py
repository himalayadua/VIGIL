"""
AttentionAdapter — Track 3 (attention) authored schema validator and compiler.

Kaggle Track 3 = Attention.

Field mapping (authored → canonical):
  blind_task_prompt                          → opening_prompt
  critical_evidence_node_ids                 → evidence_targets
  target_conclusion                          → answer_targets["target_conclusion"]
  attention_design                           → track_metadata["attention_design"]
  nodes[].id                                 → node.node_id
  nodes[].content                            → node.summary_text + inspection_detail
  nodes[].kind                               → node.node_type
  nodes[].initial_visibility                 → node.initial_visibility
  nodes[].salience + diagnosticity           → node.metadata
  edges[].source                             → edge.from_id
  edges[].target                             → edge.to_id
  edges[].attention_role                     → edge.metadata["attention_role"]

Requirements: 2, 3, 10
"""

from typing import Any, Dict

from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)


class AttentionAdapter:
    """
    Validates and compiles Track 3 (attention) authored scenarios.

    Usage (via ScenarioCatalog — not called directly):
        adapter = AttentionAdapter()
        adapter.validate(raw, scenario_id)
        spec = adapter.compile(raw)
    """

    TRACK_ID = "attention"

    _REQUIRED_FIELDS = [
        "scenario_id",
        "cognitive_track",
        "blind_task_prompt",
        "attention_design",
        "critical_evidence_node_ids",
        "target_conclusion",
        "nodes",
        "edges",
    ]

    def validate(self, raw: Dict[str, Any], scenario_id: str) -> None:
        """
        Validate a raw authored dict against the Track 3 schema.

        Raises:
            ValueError: With the name of the first missing or invalid field.
        """
        for field in self._REQUIRED_FIELDS:
            if field not in raw:
                raise ValueError(
                    f"Scenario '{scenario_id}' (attention) missing required field '{field}'"
                )

    def compile(self, raw: Dict[str, Any]) -> RuntimeScenarioSpec:
        """
        Compile a validated Track 3 authored dict into a RuntimeScenarioSpec.
        """
        nodes = self._compile_nodes(raw["nodes"])
        edges = self._compile_edges(raw["edges"])

        # Entry nodes: nodes with initial_visibility "visible" or "initial"
        entry_node_ids = [
            n.node_id for n in nodes
            if n.initial_visibility in ("visible", "initial")
        ]
        if not entry_node_ids and nodes:
            entry_node_ids = [nodes[0].node_id]

        return RuntimeScenarioSpec(
            scenario_id=raw["scenario_id"],
            cognitive_track="attention",
            opening_prompt=raw["blind_task_prompt"],
            nodes=nodes,
            edges=edges,
            entry_node_ids=entry_node_ids,
            answer_targets={"target_conclusion": raw["target_conclusion"]},
            evidence_targets=list(raw.get("critical_evidence_node_ids", [])),
            optimal_path=[],
            optimal_steps=0,
            runtime_config=RuntimeConfig(action_budget=20),
            scoring_weights={
                "correctness": 0.3,
                "target_hit_rate": 0.25,
                "distractor_chase_rate": 0.2,
                "reorientation_latency": 0.15,
                "cue_coverage": 0.1,
            },
            evaluation_conditions=EvaluationConditions(),
            track_metadata={
                "attention_design": raw.get("attention_design", {}),
                "hidden_mechanism": raw.get("hidden_mechanism", ""),
                "disconfirmation_moment": raw.get("disconfirmation_moment", ""),
            },
        )

    @staticmethod
    def _map_visibility(raw_vis: str) -> str:
        """Map authored visibility strings to canonical RuntimeNode values."""
        mapping = {
            "visible": "visible",
            "initial": "initial",
            "hidden": "hidden",
            "expanded": "visible",
            "discovered": "hidden",
            "unexplored": "hidden",
        }
        return mapping.get(str(raw_vis).lower(), "hidden")

    @staticmethod
    def _compile_nodes(raw_nodes: list) -> list:
        """Map authored attention node dicts to RuntimeNode objects."""
        nodes = []
        for n in raw_nodes:
            content = n.get("content", "")
            nodes.append(RuntimeNode(
                node_id=n["id"],
                label=n.get("label", n["id"]),
                summary_text=content,
                inspection_detail=content,
                node_type=n.get("kind", "standard"),
                initial_visibility=AttentionAdapter._map_visibility(
                    n.get("initial_visibility", "hidden")
                ),
                metadata={
                    "salience": n.get("salience", ""),
                    "diagnosticity": n.get("diagnosticity", ""),
                },
            ))
        return nodes

    @staticmethod
    def _compile_edges(raw_edges: list) -> list:
        """Map authored attention edge dicts to RuntimeEdge objects."""
        edges = []
        for e in raw_edges:
            edges.append(RuntimeEdge(
                from_id=e["source"],
                to_id=e["target"],
                relation=e.get("relation", ""),
                metadata={"attention_role": e.get("attention_role", "")},
            ))
        return edges
