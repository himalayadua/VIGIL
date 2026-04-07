"""
ExecutiveAdapter — Track 4 (executive_functions) authored schema validator and compiler.

Kaggle Track 4 = Executive Function.

The authored schema is sparser than other tracks — scoring fields are embedded
in executive_design_notes rather than a dedicated scoring_config.

Field mapping (authored → canonical):
  first node's description                   → opening_prompt
  executive_design_notes.required_pivot      → answer_targets["required_pivot"]
  executive_design_notes                     → track_metadata["executive_design_notes"]
  nodes[].id                                 → node.node_id
  nodes[].description                        → node.summary_text + inspection_detail
  nodes[].type                               → node.node_type
  edges[].from                               → edge.from_id
  edges[].to                                 → edge.to_id

Requirements: 2, 3, 11
"""

from typing import Any, Dict

from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)


class ExecutiveAdapter:
    """
    Validates and compiles Track 4 (executive_functions) authored scenarios.

    Usage (via ScenarioCatalog — not called directly):
        adapter = ExecutiveAdapter()
        adapter.validate(raw, scenario_id)
        spec = adapter.compile(raw)
    """

    TRACK_ID = "executive_functions"

    _REQUIRED_FIELDS = [
        "scenario_id",
        "cognitive_track",
        "executive_design_notes",
        "nodes",
        "edges",
    ]

    _REQUIRED_DESIGN_NOTES = [
        "tempting_wrong_path",
        "required_pivot",
        "process_scoring_focus",
    ]

    def validate(self, raw: Dict[str, Any], scenario_id: str) -> None:
        """
        Validate a raw authored dict against the Track 4 schema.

        Raises:
            ValueError: With the name of the first missing or invalid field.
        """
        for field in self._REQUIRED_FIELDS:
            if field not in raw:
                raise ValueError(
                    f"Scenario '{scenario_id}' (executive_functions) missing required field '{field}'"
                )
        ed = raw["executive_design_notes"]
        for sub in self._REQUIRED_DESIGN_NOTES:
            if sub not in ed:
                raise ValueError(
                    f"Scenario '{scenario_id}' executive_design_notes missing '{sub}'"
                )

    def compile(self, raw: Dict[str, Any]) -> RuntimeScenarioSpec:
        """
        Compile a validated Track 4 authored dict into a RuntimeScenarioSpec.
        """
        nodes = self._compile_nodes(raw["nodes"])
        edges = self._compile_edges(raw["edges"])

        # Opening prompt from the first node's description (entry brief)
        opening_prompt = nodes[0].summary_text if nodes else ""

        # Entry node is always the first node
        entry_node_ids = [nodes[0].node_id] if nodes else []

        ed = raw["executive_design_notes"]

        return RuntimeScenarioSpec(
            scenario_id=raw["scenario_id"],
            cognitive_track="executive_functions",
            opening_prompt=opening_prompt,
            nodes=nodes,
            edges=edges,
            entry_node_ids=entry_node_ids,
            answer_targets={
                "required_pivot": ed.get("required_pivot", ""),
            },
            evidence_targets=[],
            optimal_path=[],
            optimal_steps=0,
            runtime_config=RuntimeConfig(action_budget=20),
            scoring_weights={
                "correctness": 0.3,
                "inhibition_failures": 0.25,
                "pivot_quality": 0.25,
                "process_scoring_focus_alignment": 0.2,
            },
            evaluation_conditions=EvaluationConditions(),
            track_metadata={"executive_design_notes": ed},
        )

    @staticmethod
    def _compile_nodes(raw_nodes: list) -> list:
        """Map authored executive node dicts to RuntimeNode objects."""
        nodes = []
        for n in raw_nodes:
            desc = n.get("description", "")
            nodes.append(RuntimeNode(
                node_id=n["id"],
                label=n.get("label", n["id"]),
                summary_text=desc,
                inspection_detail=desc,
                node_type=n.get("type", "standard"),
                initial_visibility="hidden",
            ))
        return nodes

    @staticmethod
    def _compile_edges(raw_edges: list) -> list:
        """Map authored executive edge dicts to RuntimeEdge objects."""
        edges = []
        for e in raw_edges:
            edges.append(RuntimeEdge(
                from_id=e["from"],
                to_id=e["to"],
                relation=e.get("relation", ""),
            ))
        return edges
