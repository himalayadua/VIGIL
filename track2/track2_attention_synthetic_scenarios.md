# Track 2 Synthetic Scenario Library — Attention

This file contains one **fully synthetic Track 2: Attention** scenario per causal skeleton in the attached library.

## Design intent

- Preserve the **causal backbone** of the original skeleton.
- Replace all real entities with **synthetic names, settings, and labels**.
- Convert the skeleton into a **stateful attention scenario**, not a learning scenario.
- Keep the benchmark target aligned to the Track 2 checklist:
  - real attentional bottleneck
  - plausible distractors
  - rare critical signal
  - reorientation trigger
  - scoreable trace-level attention behavior

## JSON template

Each scenario follows the same core structure:

```json
{
  "scenario_id": "...",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": ["..."],
  "secondary_sub_abilities": ["..."],
  "cross_track_overlap_risks": ["..."],
  "difficulty_tier": "...",
  "source_skeleton_id": "...",
  "synthetic_domain": "...",
  "_track_conversion_note": "...",
  "scenario_title": "...",
  "blind_task_prompt": "...",
  "attention_design": {
    "attentional_bottleneck": "...",
    "salient_but_irrelevant_branches": ["..."],
    "rare_critical_signal": "...",
    "reorientation_trigger": "..."
  },
  "hidden_mechanism": "...",
  "disconfirmation_moment": "...",
  "target_conclusion": "...",
  "critical_evidence_node_ids": ["n3", "n4", "n5"],
  "nodes": [...],
  "edges": [...]
}
```

---

## ECO-01 — Mireglass Basin Phase Shift
```json
{
  "scenario_id": "vigil_attention_mireglass_phase_shift_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "sustained_attention",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "stimulus_driven_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ECO-01",
  "synthetic_domain": "synthetic_ecology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Mireglass Basin Phase Shift",
  "blind_task_prompt": "A managed basin is losing shimmerfin stock after a bright algae season. Inspect the monitoring graph and submit the single most diagnostic operational driver behind the decline.",
  "attention_design": {
    "attentional_bottleneck": "The graph contains a vivid peak-bloom branch, an upstream construction branch, and a rainfall branch that all look important. The real clue is a low-salience transition signal that appears after the obvious bloom peak.",
    "salient_but_irrelevant_branches": [
      "Warm-phase bloom toxicity reports",
      "Upstream embankment construction notices",
      "Heavy-rain inflow spike dashboard"
    ],
    "rare_critical_signal": "A late-season species-turnover log showing the crash begins after the bright bloom fades.",
    "reorientation_trigger": "A toxin assay undercuts the obvious bloom-poison hypothesis and should force reorientation to succession timing."
  },
  "hidden_mechanism": "The loss is driven by a post-peak community transition that changes oxygen rhythm and food structure, not by the visible bloom peak itself.",
  "disconfirmation_moment": "Peak-bloom toxin assays stay below lethal range while stock loss starts only during the handoff to the dull secondary algae phase.",
  "target_conclusion": "Prioritize the late phase-shift evidence: the proximate driver is the bloom transition, not peak toxicity.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "basin_loss_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Shimmerfin losses follow a highly visible bright-season bloom."
    },
    {
      "id": "n1",
      "label": "bright_bloom_alerts",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Operators flagged the luminous Plareef bloom as the likely killer."
    },
    {
      "id": "n2",
      "label": "upstream_change_board",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Recent embankment works and heavy rain coincide with the event."
    },
    {
      "id": "n3",
      "label": "seasonal_phase_log",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A time-strip shows stock stability during the peak and decline after the shift."
    },
    {
      "id": "n4",
      "label": "toxin_assay_panel",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Peak-bloom assays never reach lethal levels for the affected species."
    },
    {
      "id": "n5",
      "label": "succession_transition_record",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "The bloom flips from Plareef-dominant to Diala/Navic forms with altered oxygen cycles."
    },
    {
      "id": "n6",
      "label": "stock_composition_report",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Small species tied to the original algal structure disappear first."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-02 — Carrion Glider Replacement Cascade
```json
{
  "scenario_id": "vigil_attention_carrion_glider_cascade_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "sustained_attention",
    "stimulus_driven_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "ECO-02",
  "synthetic_domain": "synthetic_ecology_public_health",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Carrion Glider Replacement Cascade",
  "blind_task_prompt": "A rural belt shows a sudden rise in bite-fever deaths near livestock corridors. Explore the case graph and submit the most diagnostic cause of the mortality surge.",
  "attention_design": {
    "attentional_bottleneck": "The human-health surface cues point toward pesticide exposure, livestock disease, and heat stress. The decisive signal hides in wildlife range overlays and carcass-consumer substitution logs.",
    "salient_but_irrelevant_branches": [
      "Pesticide exposure complaints",
      "Heatwave mortality dashboard",
      "Livestock skin-disease briefings"
    ],
    "rare_critical_signal": "A map showing the spike matches old carrion-glider range rather than crop-spray zones.",
    "reorientation_trigger": "Districts that never had gliders show no death-rate shift, forcing reorientation from human toxicology to scavenger-loss dynamics."
  },
  "hidden_mechanism": "A veterinary residue removes the keystone scavenger; scavenging shifts to feral gnawhounds, which amplifies bite-fever transmission to people.",
  "disconfirmation_moment": "The spatial pattern follows historic glider territory instead of the highest pesticide-use districts.",
  "target_conclusion": "The key cause is scavenger replacement after residue-driven glider collapse, not direct chemical exposure to humans.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "bite_fever_cluster_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Bite-fever deaths rise around livestock disposal corridors."
    },
    {
      "id": "n1",
      "label": "crop_chemical_watch",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Agricultural agents suspect crop chemicals because deaths occur in farm belts."
    },
    {
      "id": "n2",
      "label": "livestock_pathogen_roundup",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "A livestock skin outbreak is temporally nearby but not spatially aligned."
    },
    {
      "id": "n3",
      "label": "territory_overlay_atlas",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Mortality rise tracks legacy carrion-glider range, not spray intensity."
    },
    {
      "id": "n4",
      "label": "never_glider_districts",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Districts without historic glider populations show no bite-fever increase."
    },
    {
      "id": "n5",
      "label": "carcass_consumer_shift_log",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Carcass cameras show gnawhounds replacing gliders at disposal sites."
    },
    {
      "id": "n6",
      "label": "bite_vector_summary",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Gnawhound counts and bite-fever incidence rise together after glider absence."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-03 — Brineisle Subsidy Break
```json
{
  "scenario_id": "vigil_attention_brineisle_subsidy_break_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_shifting",
    "perceptual_inhibition"
  ],
  "secondary_sub_abilities": [
    "sustained_attention",
    "attention_capacity"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "ECO-03",
  "synthetic_domain": "synthetic_cross_ecosystem_ecology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Brineisle Subsidy Break",
  "blind_task_prompt": "Nearshore fin biomass is falling around several island clusters. Inspect the monitoring graph and submit the most diagnostic driver of the marine decline.",
  "attention_design": {
    "attentional_bottleneck": "The marine branch is crowded with bleaching, harvest, and temperature cues. The decisive evidence sits in a terrestrial branch about colony birds and nutrient dust.",
    "salient_but_irrelevant_branches": [
      "Marine heat anomaly reports",
      "Reef-net harvest complaints",
      "Bleaching photo surveys"
    ],
    "rare_critical_signal": "A comparative map shows fish decline is strongest near vermin-infested islands and minimal near clean islands.",
    "reorientation_trigger": "Marine stressors fail to explain the between-island contrast, forcing attention across the land-sea boundary."
  },
  "hidden_mechanism": "The decline is driven by loss of cross-ecosystem nutrient subsidy: island nesters vanish, nutrient dust drops, and nearby reef production falls.",
  "disconfirmation_moment": "Reefs near vermin-free islands remain productive despite similar marine temperatures and harvest pressure.",
  "target_conclusion": "Reorient from marine-only causes to the island-origin subsidy break caused by predator-driven bird loss.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "reef_decline_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Fin biomass has fallen around part of the archipelago."
    },
    {
      "id": "n1",
      "label": "marine_stressor_stack",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Heat stress, bleaching, and harvest pressure all look like plausible marine causes."
    },
    {
      "id": "n2",
      "label": "bleach_event_gallery",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Recent bleaching imagery dominates the dashboard."
    },
    {
      "id": "n3",
      "label": "island_pair_comparison",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Comparable reefs differ mainly by whether their islands still host nesting flocks."
    },
    {
      "id": "n4",
      "label": "thermal_match_table",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Warmth and harvest pressure are similar at both impacted and spared reefs."
    },
    {
      "id": "n5",
      "label": "nutrient_dust_monitor",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Nitrogen dust to nearshore water collapses only next to predator-heavy islands."
    },
    {
      "id": "n6",
      "label": "reef_productivity_sheet",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Productivity, juvenile counts, and fin biomass all track subsidy loss."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-04 — Shadefang Foraging Shift
```json
{
  "scenario_id": "vigil_attention_shadefang_foraging_shift_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "sustained_attention"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "stimulus_driven_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "procedural_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ECO-04",
  "synthetic_domain": "synthetic_terrestrial_ecology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Shadefang Foraging Shift",
  "blind_task_prompt": "A reserve\u2019s plant mix is changing rapidly after a new predator appeared. Explore the evidence graph and submit the most diagnostic driver of the vegetation shift.",
  "attention_design": {
    "attentional_bottleneck": "Predator counts and kill reports are visually dominant, but the real clue is a subtle mismatch: herbivore numbers stay stable while their route patterns change.",
    "salient_but_irrelevant_branches": [
      "Predator kill ledger",
      "Native predator competition notes",
      "Plant disease bulletin"
    ],
    "rare_critical_signal": "Movement traces show herbivores abandoning exposed feeding zones without a population crash.",
    "reorientation_trigger": "Stable herbivore counts disconfirm the obvious population-suppression story and should redirect attention to behavior."
  },
  "hidden_mechanism": "The new predator changes herbivore behavior, which redirects grazing pressure and reshapes the plant community without major herbivore decline.",
  "disconfirmation_moment": "Herbivore census totals remain normal even where plant composition shifts hardest.",
  "target_conclusion": "The critical driver is trait-mediated behavior change, not direct herbivore population collapse.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "reserve_shift_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Vegetation composition changed soon after a new hunter entered the reserve."
    },
    {
      "id": "n1",
      "label": "predator_kill_log",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Kill records suggest direct top-down loss of grazers."
    },
    {
      "id": "n2",
      "label": "leaf_blight_watch",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "A mild leaf blight tempts a disease-based explanation."
    },
    {
      "id": "n3",
      "label": "grazer_route_heatmap",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Grazers now avoid open corridors and bunch in the thornshade belt."
    },
    {
      "id": "n4",
      "label": "grazer_count_census",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Grazer population totals stay near baseline."
    },
    {
      "id": "n5",
      "label": "bite_pressure_reallocation",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Plant bite pressure shifts sharply toward the shadow-tolerant species cluster."
    },
    {
      "id": "n6",
      "label": "plant_mix_audit",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Plants not directly favored by the predator still decline due to redistributed foraging."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-05 — Sediment Debt Release
```json
{
  "scenario_id": "vigil_attention_sediment_debt_release_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "sustained_attention",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "attention_capacity"
  ],
  "cross_track_overlap_risks": [
    "associative_learning",
    "concept_formation"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ECO-05",
  "synthetic_domain": "synthetic_freshwater_management",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Sediment Debt Release",
  "blind_task_prompt": "A lake keeps flaring despite verified upstream controls. Inspect the remediation graph and submit the most diagnostic driver of continued flare-ups.",
  "attention_design": {
    "attentional_bottleneck": "The graph front-loads policy compliance, rainfall spikes, and remaining runoff complaints. The decisive cue is a quieter internal-release branch that becomes salient only after policy success is confirmed.",
    "salient_but_irrelevant_branches": [
      "Runoff complaint inbox",
      "Warm-season anomaly alerts",
      "Construction sediment notices"
    ],
    "rare_critical_signal": "Sediment-core release readings spike under warm-layer separation despite lower external loads.",
    "reorientation_trigger": "Verified load reduction disconfirms the easy 'policy failed' story and should redirect focus inward."
  },
  "hidden_mechanism": "Past accumulation stored a long-tail nutrient debt; internal sediment release now dominates after external controls improve.",
  "disconfirmation_moment": "External loads are truly down, yet flare intensity persists.",
  "target_conclusion": "The key driver is internal sediment release from legacy buildup, not current noncompliance.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "lake_persistence_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Flares continue despite expensive source controls."
    },
    {
      "id": "n1",
      "label": "compliance_doubt_board",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Managers suspect the upstream controls are not really working."
    },
    {
      "id": "n2",
      "label": "rainfall_excursion_feed",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "A recent wet month creates a tempting external-source story."
    },
    {
      "id": "n3",
      "label": "external_load_audit",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Verified records show external inputs fell as planned."
    },
    {
      "id": "n4",
      "label": "compliance_verification_packet",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Inspection and sampling confirm the policy is being followed."
    },
    {
      "id": "n5",
      "label": "sediment_release_probe",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Warm stratification events trigger strong release from old bed deposits."
    },
    {
      "id": "n6",
      "label": "flare_persistence_summary",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Flare intensity tracks internal release episodes rather than current upstream inputs."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-06 — Juvenile Skew Cascade
```json
{
  "scenario_id": "vigil_attention_juvenile_skew_cascade_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_capacity",
    "perceptual_inhibition"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "ECO-06",
  "synthetic_domain": "synthetic_freshwater_ecology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Juvenile Skew Cascade",
  "blind_task_prompt": "A species flock is collapsing even though the dominant shoal species appears numerically stable. Explore the graph and submit the most diagnostic driver.",
  "attention_design": {
    "attentional_bottleneck": "Abundance charts dominate attention and falsely reassure. The decisive cue is hidden in a less salient size-structure pane and shared juvenile-resource pressure map.",
    "salient_but_irrelevant_branches": [
      "Total abundance dashboard",
      "Pathogen screen notes",
      "Construction disturbance report"
    ],
    "rare_critical_signal": "Size-bin data reveals a flood of juveniles and a shortage of adults within the dominant shoal species.",
    "reorientation_trigger": "Stable total abundance disconfirms the simple dominance-expansion story and should redirect focus to composition within the species."
  },
  "hidden_mechanism": "A life-stage skew changes competition on the juvenile resource, destabilizing specialists without large changes in total abundance.",
  "disconfirmation_moment": "Total counts for the focal shoal species remain flat while specialists disappear.",
  "target_conclusion": "The diagnostic driver is ontogenetic skew inside the focal species, not a raw abundance increase.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "flock_collapse_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Several specialists are vanishing while the dominant shoal seems stable."
    },
    {
      "id": "n1",
      "label": "total_count_dashboard",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The dominant shoal\u2019s total abundance looks normal, encouraging a dead-end search."
    },
    {
      "id": "n2",
      "label": "pathogen_panel",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "A negative pathogen screen consumes attention without resolving the pattern."
    },
    {
      "id": "n3",
      "label": "size_bin_histograms",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Adults drop while juveniles surge inside the stable total count."
    },
    {
      "id": "n4",
      "label": "specialist_overlap_map",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "The collapsing specialists depend on the same juvenile resource pool."
    },
    {
      "id": "n5",
      "label": "competition_pressure_grid",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Juvenile crowding intensifies exactly where specialist young should recruit."
    },
    {
      "id": "n6",
      "label": "irreversibility_note",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Specialists fail to re-establish even when the original driver relaxes."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-07 — Larval Bottleneck Release
```json
{
  "scenario_id": "vigil_attention_larval_bottleneck_release_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "stimulus_driven_attention",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "observational_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ECO-07",
  "synthetic_domain": "synthetic_reef_ecology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Larval Bottleneck Release",
  "blind_task_prompt": "A spine grazer outbreak is stripping a reef system. Inspect the case graph and submit the most diagnostic driver of the outbreak.",
  "attention_design": {
    "attentional_bottleneck": "Predator-loss narratives and storm reports are far more salient than the subtle larval-food branch that actually explains the population jump.",
    "salient_but_irrelevant_branches": [
      "Predator census board",
      "Storm damage photos",
      "Adult grazer density maps"
    ],
    "rare_critical_signal": "Larval survival surges only where nutrient-rich plume water increases plankton feed.",
    "reorientation_trigger": "Predator counts fail to separate outbreak from non-outbreak zones, forcing a shift toward early-life-stage data."
  },
  "hidden_mechanism": "Runoff releases a larval food bottleneck, causing a recruitment boom rather than a simple adult predator failure.",
  "disconfirmation_moment": "Outbreak and non-outbreak reefs have similar predator counts under comparable fishing pressure.",
  "target_conclusion": "The key driver is nutrient-mediated larval survival, not missing adult predators.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "reef_outbreak_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A spine grazer outbreak is driving rapid reef loss."
    },
    {
      "id": "n1",
      "label": "predator_gap_report",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Analysts foreground predator absence as the obvious cause."
    },
    {
      "id": "n2",
      "label": "storm_scour_archive",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Storm records create a parallel damage narrative."
    },
    {
      "id": "n3",
      "label": "recruitment_survival_series",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Recruitment spikes follow nutrient plume periods, not predator dips."
    },
    {
      "id": "n4",
      "label": "predator_match_table",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Predator abundance does not differ meaningfully across matched sites."
    },
    {
      "id": "n5",
      "label": "larval_food_window",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Larval feed availability rises sharply in plume-influenced nurseries."
    },
    {
      "id": "n6",
      "label": "coral_loss_profile",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Coral loss accelerates where recruitment bottlenecks disappear."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-08 — Function Without Structure
```json
{
  "scenario_id": "vigil_attention_function_without_structure_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "sustained_attention"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "attention_capacity"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "ECO-08",
  "synthetic_domain": "synthetic_reef_function_monitoring",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Function Without Structure",
  "blind_task_prompt": "A reef appears visually intact but is underperforming badly. Explore the monitoring graph and submit the most diagnostic driver of the functional collapse.",
  "attention_design": {
    "attentional_bottleneck": "Coral-cover visuals dominate and suggest health. The real clue lies in a neglected turf-sediment layer and herbivore feeding-efficiency logs.",
    "salient_but_irrelevant_branches": [
      "Healthy-cover image gallery",
      "Cyclone damage archive",
      "Fishing pressure forum"
    ],
    "rare_critical_signal": "Herbivore feeding collapses where sediment saturates the turf matrix between intact structures.",
    "reorientation_trigger": "Stable structure disconfirms the usual reef-decline narrative and should shift attention to function-level evidence."
  },
  "hidden_mechanism": "The system loses function through sediment-loaded turf that blocks herbivore maintenance while coral structure initially remains intact.",
  "disconfirmation_moment": "Structural surveys look normal while productivity and grazer throughput crash.",
  "target_conclusion": "The critical driver is turf-sediment functional failure, not visible structure loss.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "reef_health_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Official surveys call the reef stable, but yields and grazer throughput are falling."
    },
    {
      "id": "n1",
      "label": "coral_cover_gallery",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Normal-looking structure creates a misleading all-clear signal."
    },
    {
      "id": "n2",
      "label": "cyclone_event_log",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Past storms invite a purely physical-damage explanation."
    },
    {
      "id": "n3",
      "label": "productivity_v_structure_panel",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Function declines while structure stays flat."
    },
    {
      "id": "n4",
      "label": "grazing_efficiency_meter",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Herbivores cannot feed effectively on sediment-heavy turf."
    },
    {
      "id": "n5",
      "label": "turf_sediment_probe",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Sediment loads in the turf layer rise massively after runoff pulses."
    },
    {
      "id": "n6",
      "label": "service_loss_sheet",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Standing biomass, food output, and turnover all collapse despite intact cover."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-09 — Masked Reproduction Failure
```json
{
  "scenario_id": "vigil_attention_masked_reproduction_failure_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "sustained_attention",
    "perceptual_inhibition"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "attention_capacity"
  ],
  "cross_track_overlap_risks": [
    "associative_learning",
    "concept_formation"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ECO-09",
  "synthetic_domain": "synthetic_pollinator_ecology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Masked Reproduction Failure",
  "blind_task_prompt": "A crop-belt flora looks stable even as support species are thinning. Inspect the graph and submit the most diagnostic hidden risk to the plant community.",
  "attention_design": {
    "attentional_bottleneck": "Biomass stability is the loudest signal. The true problem is buried in seed-set data and a simultaneous reduction in a different damaging guild.",
    "salient_but_irrelevant_branches": [
      "Stable biomass dashboard",
      "Pest reduction celebration brief",
      "Drought-year summaries"
    ],
    "rare_critical_signal": "Seed set falls long before total plant cover does.",
    "reorientation_trigger": "Normal-looking biomass disconfirms the idea that pollinator thinning is harmless and should redirect attention to reproduction metrics."
  },
  "hidden_mechanism": "Pollinator loss is temporarily masked because a damaging herbivore guild also falls; biomass stays up until reproductive failure dominates.",
  "disconfirmation_moment": "Plant presence stays stable while seed production quietly deteriorates.",
  "target_conclusion": "The hidden risk is a masked pollination deficit, not system stability.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "flora_status_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Plant cover looks steady across the corridor despite support-species change."
    },
    {
      "id": "n1",
      "label": "biomass_dashboard",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Stable biomass invites premature closure."
    },
    {
      "id": "n2",
      "label": "pest_decline_note",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Visible pest reduction makes the system look healthier than it is."
    },
    {
      "id": "n3",
      "label": "seed_set_trend",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Reproductive output trends downward before cover changes."
    },
    {
      "id": "n4",
      "label": "pollinator_count_strip",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Pollinator counts are already critically low even during biomass stability."
    },
    {
      "id": "n5",
      "label": "dual_effect_interaction_map",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The same stressor reduces pollinators and pests, temporarily cancelling visible impact."
    },
    {
      "id": "n6",
      "label": "delayed_crash_projection",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Future plant abundance crashes once the masking effect ends."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ECO-10 — Bystander Field Exposure
```json
{
  "scenario_id": "vigil_attention_bystander_field_exposure_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "attention_capacity",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "associative_learning",
    "procedural_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ECO-10",
  "synthetic_domain": "synthetic_agroecology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Bystander Field Exposure",
  "blind_task_prompt": "A roaming pollinator is disappearing from a farming belt. Explore the graph and submit the most diagnostic exposure source.",
  "attention_design": {
    "attentional_bottleneck": "Investigators naturally fixate on pollinator-serviced crops and managed hives. The key clue is low-glamour acreage data for nearby non-service seed fields.",
    "salient_but_irrelevant_branches": [
      "Managed-hive disease branch",
      "Service-crop exposure branch",
      "Habitat-loss complaint map"
    ],
    "rare_critical_signal": "Exposure risk aligns with treated broadacre fields the pollinator never services directly.",
    "reorientation_trigger": "The obvious serviced crop accounts for only a tiny share of treated area, forcing a shift to incidental exposure pathways."
  },
  "hidden_mechanism": "The pollinator is harmed by proximity to heavily treated non-target fields, not the crops it directly services.",
  "disconfirmation_moment": "The serviced crop occupies too little treated area to explain the spatial decline.",
  "target_conclusion": "The key exposure source is incidental bystander contact from nearby treated field crops.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "occupancy_decline_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A roaming pollinator is disappearing fastest in intensive farmland."
    },
    {
      "id": "n1",
      "label": "service_crop_branch",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Investigators focus on the few crops that obviously use pollinators."
    },
    {
      "id": "n2",
      "label": "managed_hive_pathogen_feed",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Managed hive disease is noisy but poorly aligned."
    },
    {
      "id": "n3",
      "label": "treated_area_breakdown",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Most treatment area belongs to broadacre seed fields, not serviced crops."
    },
    {
      "id": "n4",
      "label": "small_share_table",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "The serviced crop contributes only a trivial slice of total treated land."
    },
    {
      "id": "n5",
      "label": "foraging_overlap_map",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The pollinator crosses field margins and encounters treated dust from nearby broadacre fields."
    },
    {
      "id": "n6",
      "label": "occupancy_gradient_sheet",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Decline intensity follows treated broadacre density."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-01 — Biofilm Reservoir in the Quiet Utility Line
```json
{
  "scenario_id": "vigil_attention_biofilm_reservoir_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "sustained_attention",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "stimulus_driven_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "CLIN-01",
  "synthetic_domain": "synthetic_clinical_infection_control",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Biofilm Reservoir in the Quiet Utility Line",
  "blind_task_prompt": "Several patients across units develop the same unusual resistant infection. Explore the case graph and submit the most diagnostic source of the cluster.",
  "attention_design": {
    "attentional_bottleneck": "Case narratives push attention toward travel history, patient-to-patient spread, and device contamination. The decisive clue is a low-salience environmental infrastructure branch connected by genomic identity.",
    "salient_but_irrelevant_branches": [
      "Travel-history summaries",
      "Cross-ward contact tracing",
      "Device culture logs"
    ],
    "rare_critical_signal": "Genomic identity ties apparently unrelated cases to one quiet utility line.",
    "reorientation_trigger": "Whole-isolate matching collapses the multiple-introduction story and should force reorientation toward a persistent shared source."
  },
  "hidden_mechanism": "A colonized drain line acts as an abiotic reservoir, intermittently seeding patients through splash/aerosol exposure.",
  "disconfirmation_moment": "The same rare strain appears in cases with no travel and no meaningful cross-contact.",
  "target_conclusion": "The most diagnostic source is a persistent environmental plumbing reservoir, not separate patient introductions.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "resistant_cluster_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Unusual resistant infections appear over many months in seemingly unrelated patients."
    },
    {
      "id": "n1",
      "label": "travel_history_packets",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Rare strain reports bias attention toward imported cases."
    },
    {
      "id": "n2",
      "label": "device_culture_matrix",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Repeated equipment culturing comes back negative."
    },
    {
      "id": "n3",
      "label": "strain_identity_report",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "All cases carry the same narrow genetic fingerprint."
    },
    {
      "id": "n4",
      "label": "contact_gap_summary",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Patients had no common travel or contact chain."
    },
    {
      "id": "n5",
      "label": "utility_line_biofilm_probe",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Drain biofilm and splash zones near a sink line carry the same strain."
    },
    {
      "id": "n6",
      "label": "exposure_proximity_sheet",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Cases cluster around rooms adjacent to the affected line."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-02 — The Masquerading Side Effect
```json
{
  "scenario_id": "vigil_attention_iatrogenic_masquerade_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "sustained_attention",
    "attention_capacity"
  ],
  "cross_track_overlap_risks": [
    "observational_learning",
    "concept_formation"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "CLIN-02",
  "synthetic_domain": "synthetic_clinical_pharmacology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "The Masquerading Side Effect",
  "blind_task_prompt": "A patient\u2019s condition worsens after treatment expansions across multiple visits. Inspect the medication graph and submit the most diagnostic origin of the cascade.",
  "attention_design": {
    "attentional_bottleneck": "Symptom descriptions naturally pull attention toward a new disease branch. The decisive signal is tucked in a rare adverse-effect note and timing alignment with the first drug.",
    "salient_but_irrelevant_branches": [
      "New-disease differential tree",
      "Medication-B efficacy debate",
      "Adherence concerns"
    ],
    "rare_critical_signal": "The first symptom appears only after the first drug and fits a rare listed adverse effect.",
    "reorientation_trigger": "Current interaction warnings explain later worsening but not the first symptom, forcing attention back to the initial prescription event."
  },
  "hidden_mechanism": "An atypical side effect is mistaken for a new disease, which triggers a prescribing cascade.",
  "disconfirmation_moment": "The symptom onset lines up tightly with Drug A initiation before any other medication enters the picture.",
  "target_conclusion": "The cascade begins with a medication-induced masquerade, not a spontaneous new disease.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "polypharmacy_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A patient\u2019s symptom burden grows as more medications are added."
    },
    {
      "id": "n1",
      "label": "new_condition_tree",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The symptoms strongly resemble an independent new illness."
    },
    {
      "id": "n2",
      "label": "nonadherence_flags",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Poor response tempts a compliance story."
    },
    {
      "id": "n3",
      "label": "symptom_onset_timeline",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The first new symptom starts soon after the first prescription."
    },
    {
      "id": "n4",
      "label": "rare_adr_note",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "The initial drug lists the exact symptom as a rare adverse effect."
    },
    {
      "id": "n5",
      "label": "cascade_interaction_graph",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Later drugs amplify the problem created by the first misread side effect."
    },
    {
      "id": "n6",
      "label": "multi_visit_worsening_log",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Each added treatment deepens the original error."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-03 — Impossible Placebo Signal
```json
{
  "scenario_id": "vigil_attention_impossible_placebo_signal_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "stimulus_driven_attention",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "procedural_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "CLIN-03",
  "synthetic_domain": "synthetic_clinical_trials",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Impossible Placebo Signal",
  "blind_task_prompt": "A late-stage trial produces a surprising aggregate result. Explore the trial graph and submit the most diagnostic explanation for why the result is not trustworthy.",
  "attention_design": {
    "attentional_bottleneck": "The dashboard encourages attention on efficacy summaries, mechanism debates, and endpoint sensitivity. The critical cue is a medically impossible placebo pattern that should act like an alert.",
    "salient_but_irrelevant_branches": [
      "Mechanism-failure discussion",
      "Endpoint sensitivity analysis",
      "Population mismatch speculation"
    ],
    "rare_critical_signal": "The placebo arm appears to improve on a condition that should not naturally improve.",
    "reorientation_trigger": "That impossible signal should snap attention away from biology toward process integrity."
  },
  "hidden_mechanism": "The trial question is unanswerable because the site process is contaminated: wrong participants and missing administration integrity corrupt the data.",
  "disconfirmation_moment": "The placebo trend is biologically implausible enough that it cannot be treated as a normal negative result.",
  "target_conclusion": "The most diagnostic explanation is site/data integrity failure, not simple drug inefficacy.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "trial_surprise_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A late-stage trial misses its endpoint in a puzzling way."
    },
    {
      "id": "n1",
      "label": "mechanism_failure_forum",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Analysts treat the result as straightforward drug failure."
    },
    {
      "id": "n2",
      "label": "endpoint_sensitivity_panel",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Measurement-tool debates consume attention."
    },
    {
      "id": "n3",
      "label": "arm_trajectory_plot",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The placebo arm improves in a way the disease should not allow."
    },
    {
      "id": "n4",
      "label": "implausibility_note",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Clinicians mark the placebo pattern as incompatible with known disease course."
    },
    {
      "id": "n5",
      "label": "site_integrity_audit",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Enrollment quality and dose administration checks fail at several sites."
    },
    {
      "id": "n6",
      "label": "data_unusability_summary",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "The aggregate efficacy result becomes uninterpretable."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-04 — Signal Drowned by Site Noise
```json
{
  "scenario_id": "vigil_attention_site_noise_dilution_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_capacity",
    "perceptual_inhibition"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "associative_learning",
    "procedural_learning"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "CLIN-04",
  "synthetic_domain": "synthetic_clinical_trials",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Signal Drowned by Site Noise",
  "blind_task_prompt": "A multi-site mood trial misses its primary endpoint. Inspect the evidence graph and submit the most diagnostic reason the aggregate result conceals the underlying signal.",
  "attention_design": {
    "attentional_bottleneck": "Global aggregate plots dominate attention. The real clue requires holding site-level quality, placebo response, and enrollment-behavior branches in focus together.",
    "salient_but_irrelevant_branches": [
      "Mechanism-does-not-work summary",
      "Sample-size complaint",
      "Patient heterogeneity branch"
    ],
    "rare_critical_signal": "The signal appears only after attention shifts from overall averages to site-stratified quality patterns.",
    "reorientation_trigger": "High-quality sites show a meaningful effect while low-quality sites show pure placebo inflation."
  },
  "hidden_mechanism": "Site contamination and inflated placebo response dilute the real signal in the aggregate analysis.",
  "disconfirmation_moment": "Aggregate null results break apart once data are stratified by site quality indicators.",
  "target_conclusion": "The best explanation is dilution by site-level noise, not universal drug failure.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "mood_trial_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A multi-site trial misses its endpoint despite earlier promise."
    },
    {
      "id": "n1",
      "label": "global_null_summary",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The top-level result looks like simple failure."
    },
    {
      "id": "n2",
      "label": "power_complaint_sheet",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Some analysts blame inadequate sample size."
    },
    {
      "id": "n3",
      "label": "site_stratified_panel",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Clean sites separate drug from placebo; noisy sites do not."
    },
    {
      "id": "n4",
      "label": "placebo_inflation_flags",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Several sites show implausibly high placebo responders and repeat enrollers."
    },
    {
      "id": "n5",
      "label": "site_quality_matrix",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Training quality and enrollment hygiene predict whether signal survives."
    },
    {
      "id": "n6",
      "label": "aggregate_dilution_note",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Pooling clean and contaminated sites erases the effect."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-05 — The Moving Resistance Token
```json
{
  "scenario_id": "vigil_attention_plasmid_network_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_shifting",
    "attention_capacity"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "CLIN-05",
  "synthetic_domain": "synthetic_hospital_microbiology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "The Moving Resistance Token",
  "blind_task_prompt": "Resistance is appearing across several different patient isolates. Explore the outbreak graph and submit the most diagnostic unit of spread.",
  "attention_design": {
    "attentional_bottleneck": "Standard outbreak views center organism lineage, pushing attention toward clonal spread. The decisive clue requires shifting from organism trees to a smaller, quieter genetic-element network.",
    "salient_but_irrelevant_branches": [
      "Clonal spread tree",
      "Travel-acquisition branch",
      "Patient-to-patient contact map"
    ],
    "rare_critical_signal": "Different organisms share a near-identical resistance element despite unrelated whole-organism lineages.",
    "reorientation_trigger": "Clonal analyses fail, forcing attention to the plasmid-level view."
  },
  "hidden_mechanism": "The moving unit is a transferable resistance element hopping across organisms and environments, not one spreading clone.",
  "disconfirmation_moment": "Organism genomes are unrelated, yet the resistance cassette sequence is highly conserved across them.",
  "target_conclusion": "The most diagnostic spreading unit is the mobile resistance element, not a single bacterial clone.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "resistance_cluster_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Multiple resistant infections appear without an obvious outbreak strain."
    },
    {
      "id": "n1",
      "label": "clone_search_tree",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The investigation starts by looking for one spreading organism."
    },
    {
      "id": "n2",
      "label": "travel_and_community_risk",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Community acquisition remains a tempting but incomplete explanation."
    },
    {
      "id": "n3",
      "label": "lineage_mismatch_report",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Whole genomes do not form a coherent clone outbreak."
    },
    {
      "id": "n4",
      "label": "element_similarity_panel",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "A resistance element sequence repeats across otherwise unrelated isolates."
    },
    {
      "id": "n5",
      "label": "environment_patient_bridge",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The same element appears in environmental and patient-associated communities."
    },
    {
      "id": "n6",
      "label": "new_resistance_emergence_log",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Previously susceptible organisms acquire the same resistance token."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-06 — The Standard Line Problem
```json
{
  "scenario_id": "vigil_attention_line_origin_misattribution_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "stimulus_driven_attention",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "procedural_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "CLIN-06",
  "synthetic_domain": "synthetic_icu_patient_safety",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "The Standard Line Problem",
  "blind_task_prompt": "A patient in standard care deteriorates into sepsis. Inspect the care graph and submit the most diagnostic source of the decline.",
  "attention_design": {
    "attentional_bottleneck": "The presenting condition and medication reactions dominate attention. The critical cue is an organism mismatch that should redirect focus to an iatrogenic line source.",
    "salient_but_irrelevant_branches": [
      "Primary-disease progression branch",
      "Drug-reaction differential",
      "Community infection search"
    ],
    "rare_critical_signal": "Blood culture reveals an organism pattern inconsistent with the original condition but consistent with skin-line contamination.",
    "reorientation_trigger": "The culture identity should trigger reorientation away from disease progression toward device origin."
  },
  "hidden_mechanism": "A standard central line becomes the hidden source, but symptoms are misattributed to the disease being treated.",
  "disconfirmation_moment": "The cultured organism does not match the expected pathogen profile for the original condition.",
  "target_conclusion": "The most diagnostic source is a line-associated iatrogenic infection, not worsening baseline disease.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "sepsis_deterioration_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A patient worsens after standard invasive support is initiated."
    },
    {
      "id": "n1",
      "label": "baseline_condition_branch",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Clinicians initially read the decline as natural progression."
    },
    {
      "id": "n2",
      "label": "drug_reaction_sheet",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Medication effects are plausible but not well aligned."
    },
    {
      "id": "n3",
      "label": "blood_culture_return",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Culture timing and identity point away from the baseline illness."
    },
    {
      "id": "n4",
      "label": "organism_mismatch_note",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "The isolate matches common skin-line contaminants rather than the disease source."
    },
    {
      "id": "n5",
      "label": "line_maintenance_log",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Insertion or upkeep irregularities create a line-based route."
    },
    {
      "id": "n6",
      "label": "late_source_identification",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Recognition is delayed because the device is mentally backgrounded as routine care."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-07 — The Shared Cooling Vector
```json
{
  "scenario_id": "vigil_attention_ice_vector_cluster_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_capacity",
    "perceptual_inhibition"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "procedural_learning",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "CLIN-07",
  "synthetic_domain": "synthetic_outbreak_epidemiology",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "The Shared Cooling Vector",
  "blind_task_prompt": "Guests at an event develop similar gastrointestinal illness. Explore the exposure graph and submit the most diagnostic transmission vehicle.",
  "attention_design": {
    "attentional_bottleneck": "Menu items are the loudest cues and pull attention to a single dish. The key evidence is a less glamorous shared input present across multiple food and drink paths.",
    "salient_but_irrelevant_branches": [
      "Flagship entr\u00e9e branch",
      "Vendor recall notice",
      "Earliest-case story"
    ],
    "rare_critical_signal": "Attack rates stay substantial among people who skipped the main entr\u00e9e.",
    "reorientation_trigger": "The non-entr\u00e9e illness rate should force a shift from item-specific blame to a shared vector search."
  },
  "hidden_mechanism": "A horizontal vector touches many exposures, so the contamination sits in a shared cooling source rather than one dish.",
  "disconfirmation_moment": "A large minority of non-entr\u00e9e attendees are still ill.",
  "target_conclusion": "The most diagnostic vehicle is the shared cooling/ice source, not the main dish.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "event_cluster_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Many attendees from one event report the same illness."
    },
    {
      "id": "n1",
      "label": "entree_attack_table",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The main entr\u00e9e has the highest raw overlap with cases."
    },
    {
      "id": "n2",
      "label": "vendor_recall_branch",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "A recent supplier recall tempts a convenient explanation."
    },
    {
      "id": "n3",
      "label": "stratified_attack_rates",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Illness remains common among people who skipped the entr\u00e9e."
    },
    {
      "id": "n4",
      "label": "shared_input_list",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "A cooling input appears in drinks, sides, and plated handling."
    },
    {
      "id": "n5",
      "label": "machine_service_log",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "A recently serviced cooling system becomes the cross-cutting contamination route."
    },
    {
      "id": "n6",
      "label": "cross_item_contamination_map",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Cases span different menu selections through one vector."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-08 — Anchor Break Signal
```json
{
  "scenario_id": "vigil_attention_anchor_break_signal_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "sustained_attention",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "stimulus_driven_attention"
  ],
  "cross_track_overlap_risks": [
    "observational_learning",
    "concept_formation"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "CLIN-08",
  "synthetic_domain": "synthetic_diagnostic_reasoning",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Anchor Break Signal",
  "blind_task_prompt": "A patient returns after an initially plausible diagnosis and treatment plan. Inspect the follow-up graph and submit the most diagnostic reason the original framing should be reconsidered.",
  "attention_design": {
    "attentional_bottleneck": "Demographics, initial normal tests, and anxiety-like features all reinforce the original diagnosis. The key cue is a quiet treatment-failure signal that should pull attention off the anchor.",
    "salient_but_irrelevant_branches": [
      "Anxiety-history profile",
      "Initial normal test branch",
      "Partial symptom relief log"
    ],
    "rare_critical_signal": "The patient worsens despite therapy that should have helped if the original diagnosis were right.",
    "reorientation_trigger": "Treatment failure should act as a reorientation cue rather than as evidence to intensify the same story."
  },
  "hidden_mechanism": "The investigation stays locked to the first plausible frame even when follow-up evidence should reopen the search.",
  "disconfirmation_moment": "Return visits show worsening despite apparently appropriate treatment for the original diagnosis.",
  "target_conclusion": "The diagnostic signal is anchor-breaking treatment failure, not resistant progression of the original explanation.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "return_visit_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A patient returns after a plausible initial diagnosis and partial symptom overlap."
    },
    {
      "id": "n1",
      "label": "demographic_reassurance",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Age and history make the first diagnosis feel safe."
    },
    {
      "id": "n2",
      "label": "partial_relief_note",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Some symptoms softened briefly, tempting false confirmation."
    },
    {
      "id": "n3",
      "label": "treatment_response_series",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Overall trajectory worsens despite treatment matched to the original diagnosis."
    },
    {
      "id": "n4",
      "label": "return_symptom_shift",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "New features emerge that the first diagnosis does not explain well."
    },
    {
      "id": "n5",
      "label": "reopen_differential_prompt",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The correct move is to revisit the frame, not escalate within it."
    },
    {
      "id": "n6",
      "label": "delayed_true_event",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Late recognition follows prolonged anchoring."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-09 — Detection Gap Cluster
```json
{
  "scenario_id": "vigil_attention_detection_gap_cluster_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "stimulus_driven_attention",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "CLIN-09",
  "synthetic_domain": "synthetic_public_health_surveillance",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Detection Gap Cluster",
  "blind_task_prompt": "A neighborhood overdose cluster is resisting standard investigation. Explore the surveillance graph and submit the most diagnostic reason the cluster keeps being misclassified.",
  "attention_design": {
    "attentional_bottleneck": "Known dealer networks and standard toxicology results dominate attention. The critical cue is a response anomaly that should trigger expanded screening.",
    "salient_but_irrelevant_branches": [
      "Known supplier network",
      "Standard toxicology sheet",
      "Party-event clustering"
    ],
    "rare_critical_signal": "Some cases respond abnormally to the reversal dose expected for the detected agent.",
    "reorientation_trigger": "The treatment-response mismatch should pull attention away from the standard panel and toward an unseen compound."
  },
  "hidden_mechanism": "The real connector is a novel compound outside the routine detection panel, so surveillance mistakes the cluster for a familiar one.",
  "disconfirmation_moment": "The cases behave differently from what the detected standard compound should produce under treatment.",
  "target_conclusion": "The most diagnostic issue is a surveillance blind spot to an unpanelled compound.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "overdose_cluster_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A local overdose cluster keeps evading clear source confirmation."
    },
    {
      "id": "n1",
      "label": "known_supplier_map",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Investigators chase familiar suppliers and standard batches."
    },
    {
      "id": "n2",
      "label": "standard_panel_results",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Routine toxicology points to a familiar compound."
    },
    {
      "id": "n3",
      "label": "reversal_response_log",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Response to the usual antidote pattern is inconsistent with the reported toxin."
    },
    {
      "id": "n4",
      "label": "dose_mismatch_alert",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Several cases need unexpected rescue profiles."
    },
    {
      "id": "n5",
      "label": "expanded_panel_discovery",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "A newer compound outside the standard panel appears on deeper testing."
    },
    {
      "id": "n6",
      "label": "misclassification_backfill",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Earlier cases in the same cluster were likely labelled under the wrong compound class."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## CLIN-10 — Parallel Waterline
```json
{
  "scenario_id": "vigil_attention_parallel_waterline_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_shifting",
    "perceptual_inhibition"
  ],
  "secondary_sub_abilities": [
    "sustained_attention",
    "attention_capacity"
  ],
  "cross_track_overlap_risks": [
    "procedural_learning",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "CLIN-10",
  "synthetic_domain": "synthetic_environmental_health",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Parallel Waterline",
  "blind_task_prompt": "A rural contamination cluster persists after common sources test negative. Inspect the infrastructure graph and submit the most diagnostic source that remains hidden.",
  "attention_design": {
    "attentional_bottleneck": "The shared-community well and event-food branches attract most attention. The decisive clue is a low-visibility infrastructure split at one site assumed to be on the common line.",
    "salient_but_irrelevant_branches": [
      "Community well test branch",
      "Event food exposure list",
      "Municipal upgrade suspicion"
    ],
    "rare_critical_signal": "New cases continue only around one campsite-like location after common wells test clean.",
    "reorientation_trigger": "Persistent location-specific cases disconfirm the idea that the issue has disappeared and should redirect attention to exact infrastructure mapping."
  },
  "hidden_mechanism": "A parallel private water line was wrongly assumed to be on the shared municipal system.",
  "disconfirmation_moment": "All common wells are negative while cases continue at one specific site.",
  "target_conclusion": "The hidden source is a separate private line, not the tested shared system.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "contamination_cluster_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Cases cluster in a rural area but the obvious shared source tests clean."
    },
    {
      "id": "n1",
      "label": "community_well_tests",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Attention stays on the tested public wells because they seem the common source."
    },
    {
      "id": "n2",
      "label": "festival_food_branch",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "A local gathering creates a tempting foodborne alternative."
    },
    {
      "id": "n3",
      "label": "site_case_map",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "New cases continue around one lodging site only."
    },
    {
      "id": "n4",
      "label": "negative_shared_sources",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "All presumed common sources remain negative."
    },
    {
      "id": "n5",
      "label": "parallel_pipe_map",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The site uses a separate private line crossing a contamination zone."
    },
    {
      "id": "n6",
      "label": "site_specific_exposure_sheet",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "The site-level infrastructure split explains the residual cluster."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ENG-01 — Missing Safety Valve Cascade
```json
{
  "scenario_id": "vigil_attention_missing_safety_valve_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_shifting",
    "perceptual_inhibition"
  ],
  "secondary_sub_abilities": [
    "stimulus_driven_attention",
    "attention_capacity"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ENG-01",
  "synthetic_domain": "synthetic_cloud_infrastructure",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Missing Safety Valve Cascade",
  "blind_task_prompt": "Multiple consumer services fail at once after a core platform change. Explore the incident graph and submit the most diagnostic reason the outage became so large.",
  "attention_design": {
    "attentional_bottleneck": "Attack, hardware, and regional-failure branches are visually dominant. The critical clue is a quiet deployment-procedure omission that only becomes diagnostic once those branches collapse.",
    "salient_but_irrelevant_branches": [
      "DDoS hypothesis board",
      "Hardware health dashboard",
      "Regional outage map"
    ],
    "rare_critical_signal": "Core hardware and traffic stay normal even while rollback attempts fail.",
    "reorientation_trigger": "Normal infrastructure metrics should redirect attention from attacks to what changed procedurally in software."
  },
  "hidden_mechanism": "The blast radius is amplified by the absence of an emergency disable path, not just by the bug itself.",
  "disconfirmation_moment": "There is no hardware overload and no abnormal request flood to support the loudest hypotheses.",
  "target_conclusion": "The most diagnostic driver is the missing rollback/feature-gate safety valve.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "multi_service_outage_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Several downstream services fail after a platform incident."
    },
    {
      "id": "n1",
      "label": "attack_hypothesis_board",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The outage pattern looks like coordinated hostile traffic."
    },
    {
      "id": "n2",
      "label": "hardware_status_wall",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Teams initially search for broken machines or regions."
    },
    {
      "id": "n3",
      "label": "change_window_log",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "A software change immediately precedes failure onset."
    },
    {
      "id": "n4",
      "label": "normal_load_panel",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Traffic and hardware stay within normal range."
    },
    {
      "id": "n5",
      "label": "rollback_path_omission",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The affected service lacks an instant disable/rollback gate."
    },
    {
      "id": "n6",
      "label": "dependency_cascade_map",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "The inability to stop the bad path stretches the incident across dependencies."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ENG-02 — Foundational Lookup Invisibility
```json
{
  "scenario_id": "vigil_attention_foundational_lookup_invisibility_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_capacity",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "observational_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ENG-02",
  "synthetic_domain": "synthetic_cloud_infrastructure",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Foundational Lookup Invisibility",
  "blind_task_prompt": "Unrelated digital platforms fail simultaneously, yet their internal apps appear healthy. Explore the incident graph and submit the most diagnostic failing layer.",
  "attention_design": {
    "attentional_bottleneck": "Each application-specific branch is plausible and noisy. The real clue emerges only when attention shifts to the shared foundational lookup layer across all services.",
    "salient_but_irrelevant_branches": [
      "App-specific debug branches",
      "ISP complaint stream",
      "Attack speculation thread"
    ],
    "rare_critical_signal": "All affected platforms look internally healthy while cross-platform failure timing matches one foundational dependency.",
    "reorientation_trigger": "The shared timing across unrelated services should pull attention away from app-level debugging."
  },
  "hidden_mechanism": "A taken-for-granted lookup layer fails, and its hidden centrality delays diagnosis because everyone first debugs their own app.",
  "disconfirmation_moment": "Internal service checks pass across multiple affected products.",
  "target_conclusion": "The most diagnostic failing layer is the shared foundational address-resolution system.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "cross_platform_failure_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Many unrelated services report simultaneous problems."
    },
    {
      "id": "n1",
      "label": "app_health_branches",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Each team inspects its own stack first."
    },
    {
      "id": "n2",
      "label": "isp_noise_feed",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Network complaints create a misleading carrier story."
    },
    {
      "id": "n3",
      "label": "global_timing_overlay",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Failures begin together despite unrelated application codebases."
    },
    {
      "id": "n4",
      "label": "internal_green_checks",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Application health checks stay green inside each service."
    },
    {
      "id": "n5",
      "label": "lookup_layer_dependency",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "A shared address-resolution tier sits under all affected platforms."
    },
    {
      "id": "n6",
      "label": "failover_overload_note",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Fallback traffic worsens the failure once the base layer cracks."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ENG-03 — Delegated Token Breach
```json
{
  "scenario_id": "vigil_attention_delegated_token_breach_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "attention_capacity",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ENG-03",
  "synthetic_domain": "synthetic_saas_security",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Delegated Token Breach",
  "blind_task_prompt": "Many organizations see strange access to a common business platform, but none show a clear local compromise. Inspect the graph and submit the most diagnostic breach pathway.",
  "attention_design": {
    "attentional_bottleneck": "Victim-local logs dominate attention. The decisive clue sits in the trust-delegation branch where a service-held token inherits authority across customers.",
    "salient_but_irrelevant_branches": [
      "Victim perimeter scans",
      "Platform zero-day speculation",
      "Recent phishing chatter"
    ],
    "rare_critical_signal": "Access looks legitimate in form but originates from improbable geographies through delegated tokens.",
    "reorientation_trigger": "Clean victim perimeters should shift attention to wherever the valid tokens are actually stored and delegated from."
  },
  "hidden_mechanism": "The attacker exploits inherited authority by stealing service-held delegation tokens instead of breaching each victim directly.",
  "disconfirmation_moment": "Organizations find no local compromise despite clear unauthorized access in downstream logs.",
  "target_conclusion": "The most diagnostic path is compromise of the shared delegated-token holder, not direct intrusion into each victim.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "multi_org_access_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Several organizations see strange platform access with no obvious local breach."
    },
    {
      "id": "n1",
      "label": "victim_scan_results",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Teams search their own infrastructure for malware or stolen creds."
    },
    {
      "id": "n2",
      "label": "platform_bug_rumor",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "A rumored platform flaw pulls attention sideways."
    },
    {
      "id": "n3",
      "label": "geo_anomaly_access_log",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Access is token-valid but arrives from unusual regions."
    },
    {
      "id": "n4",
      "label": "clean_perimeter_note",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Victim systems show no evidence of direct compromise."
    },
    {
      "id": "n5",
      "label": "delegation_token_store",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "A shared integration service holds tokens that inherit customer authority."
    },
    {
      "id": "n6",
      "label": "cross_customer_breach_map",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "One trust hub fan-outs access across many organizations."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ENG-04 — Shared Vendor Paralysis
```json
{
  "scenario_id": "vigil_attention_shared_vendor_paralysis_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_shifting",
    "attention_capacity"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "stimulus_driven_attention"
  ],
  "cross_track_overlap_risks": [
    "observational_learning",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ENG-04",
  "synthetic_domain": "synthetic_public_digital_infrastructure",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Shared Vendor Paralysis",
  "blind_task_prompt": "Dozens of local agencies lose the same administrative function at once. Explore the graph and submit the most diagnostic explanation for the simultaneous paralysis.",
  "attention_design": {
    "attentional_bottleneck": "The scale suggests many separate attacks or a national system failure. The key clue is a hidden concentration point: one shared vendor behind all the affected agencies.",
    "salient_but_irrelevant_branches": [
      "Many-local-breaches narrative",
      "National-core-system suspicion",
      "Coincidental-incident theory"
    ],
    "rare_critical_signal": "Affected agencies show no local intrusion on their own servers.",
    "reorientation_trigger": "The absence of local compromise across many victims should redirect attention to common outsourced infrastructure."
  },
  "hidden_mechanism": "A single compromised vendor becomes a correlated failure point for many downstream agencies.",
  "disconfirmation_moment": "Local environments are clean even though the administrative function is down everywhere.",
  "target_conclusion": "The most diagnostic explanation is centralization risk through a shared provider, not hundreds of separate breaches.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "agency_paralysis_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Many local agencies lose payroll and records access simultaneously."
    },
    {
      "id": "n1",
      "label": "multi_attack_headline_feed",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Reports make it sound like many independent attacks."
    },
    {
      "id": "n2",
      "label": "national_core_rumor",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Some assume a national central system must have failed."
    },
    {
      "id": "n3",
      "label": "agency_local_checks",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Agency-owned systems appear uncompromised."
    },
    {
      "id": "n4",
      "label": "clean_local_servers",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "No agency finds intrusion on its own machines."
    },
    {
      "id": "n5",
      "label": "shared_service_provider",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "All affected functions run through one outsourced administrative platform."
    },
    {
      "id": "n6",
      "label": "common_dependency_map",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A single upstream hit produces hundreds of downstream victims."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## ENG-05 — Concentration Revelation
```json
{
  "scenario_id": "vigil_attention_concentration_revelation_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_capacity",
    "sustained_attention"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "perceptual_inhibition"
  ],
  "cross_track_overlap_risks": [
    "associative_learning",
    "concept_formation"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "ENG-05",
  "synthetic_domain": "synthetic_supply_chain",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Concentration Revelation",
  "blind_task_prompt": "Manufacturers across a sector stumble after a geopolitical trade action. Inspect the dependency graph and submit the most diagnostic hidden vulnerability.",
  "attention_design": {
    "attentional_bottleneck": "Price shocks, shipping friction, and firm-specific management stories crowd attention. The real clue requires tracking concentration across supplier layers and discovering the absence of true alternatives.",
    "salient_but_irrelevant_branches": [
      "Tariff-cost headlines",
      "Shipping disruption branch",
      "Firm-specific planning errors"
    ],
    "rare_critical_signal": "Alternative supplier search returns almost no qualified substitutes for critical inputs.",
    "reorientation_trigger": "When substitute options fail to materialize, attention should shift from short-term logistics to latent concentration risk."
  },
  "hidden_mechanism": "Efficiency optimization hid a near-single-source dependency that only becomes visible under disruption.",
  "disconfirmation_moment": "Firms cannot actually switch even after intense supplier searches, revealing redundancy was assumed rather than real.",
  "target_conclusion": "The most diagnostic vulnerability is hidden concentration risk, not temporary shipping cost inflation.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "sector_disruption_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A sector-wide slowdown follows an export restriction."
    },
    {
      "id": "n1",
      "label": "cost_spike_board",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The first interpretation is that prices simply rose too fast."
    },
    {
      "id": "n2",
      "label": "shipping_delay_feed",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Logistics noise obscures deeper dependency structure."
    },
    {
      "id": "n3",
      "label": "substitute_search_log",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Firms fail to find qualified alternate suppliers."
    },
    {
      "id": "n4",
      "label": "redundancy_assumption_note",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Procurement plans assumed backups that do not actually exist."
    },
    {
      "id": "n5",
      "label": "source_concentration_matrix",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Critical components trace back to a narrow geographic supplier cluster."
    },
    {
      "id": "n6",
      "label": "production_halt_sheet",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Order cancellations and shutdowns reflect concentrated dependence."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## GOV-01 — Success on the Wrong Target
```json
{
  "scenario_id": "vigil_attention_wrong_target_success_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "sustained_attention",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "attention_capacity"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "GOV-01",
  "synthetic_domain": "synthetic_governance_environmental_policy",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Success on the Wrong Target",
  "blind_task_prompt": "A remediation policy shows excellent compliance, yet the public problem persists. Explore the governance graph and submit the most diagnostic reason the intervention is missing the true driver.",
  "attention_design": {
    "attentional_bottleneck": "Compliance dashboards and enforcement debates dominate attention. The decisive clue is a quieter branch showing the dominant source has shifted over time.",
    "salient_but_irrelevant_branches": [
      "Enforcement complaint stream",
      "New-source suspicion",
      "Climate amplification debate"
    ],
    "rare_critical_signal": "The addressed source is reduced nearly to baseline, yet the problem curve barely moves.",
    "reorientation_trigger": "Verified compliance should redirect attention from policing effort to source evolution."
  },
  "hidden_mechanism": "The intervention targets the original source while a legacy internal source now sustains the problem.",
  "disconfirmation_moment": "The targeted external driver is demonstrably reduced without solving the outcome.",
  "target_conclusion": "The most diagnostic issue is temporal source shift: the policy works but is aimed at the wrong current driver.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "policy_persistence_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A well-enforced remediation policy fails to clear the public problem."
    },
    {
      "id": "n1",
      "label": "enforcement_doubt_feed",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Observers assume the policy is not really being followed."
    },
    {
      "id": "n2",
      "label": "new_source_watch",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Attention drifts to rumored new external sources."
    },
    {
      "id": "n3",
      "label": "targeted_source_audit",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "The regulated source is indeed far lower than before."
    },
    {
      "id": "n4",
      "label": "verified_compliance_file",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Inspectors confirm strong compliance and low external input."
    },
    {
      "id": "n5",
      "label": "legacy_internal_driver",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Stored internal material now dominates the system\u2019s feedback loop."
    },
    {
      "id": "n6",
      "label": "persistent_outcome_curve",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "The public outcome remains elevated despite success on the old target."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## GOV-02 — Temporal Conflict Web
```json
{
  "scenario_id": "vigil_attention_temporal_conflict_web_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_capacity",
    "perceptual_inhibition"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "observational_learning",
    "concept_formation"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "GOV-02",
  "synthetic_domain": "synthetic_regulatory_governance",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Temporal Conflict Web",
  "blind_task_prompt": "One set of firms experiences unusually slow approvals despite no obvious rule differences. Inspect the governance graph and submit the most diagnostic structural driver of the delay pattern.",
  "attention_design": {
    "attentional_bottleneck": "Staff shortages and product complexity are plausible and noisy. The real clue requires linking prior employment, consulting ties, and review duration across several branches.",
    "salient_but_irrelevant_branches": [
      "Staff shortage brief",
      "Product complexity matrix",
      "General stringency memo"
    ],
    "rare_critical_signal": "Delay tracks prior-affiliation networks rather than current employment status.",
    "reorientation_trigger": "No current conflict appears on paper, which should prompt a shift to prior-role and consulting relationships."
  },
  "hidden_mechanism": "Influence persists through sequential role changes and consulting ties even when formal current-employment rules are satisfied.",
  "disconfirmation_moment": "Current conflict checks come back clean despite company-specific delay asymmetry.",
  "target_conclusion": "The most diagnostic driver is a temporal revolving-door conflict web, not simple regulatory scarcity.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "approval_delay_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Certain applicants face systematic review delay without a formal rule difference."
    },
    {
      "id": "n1",
      "label": "staff_shortage_note",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "A broad shortage seems to explain everything."
    },
    {
      "id": "n2",
      "label": "complexity_scoring_board",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Complex submissions invite a neutral explanation."
    },
    {
      "id": "n3",
      "label": "delay_affiliation_overlay",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Delay clusters align with prior-role consulting relationships."
    },
    {
      "id": "n4",
      "label": "clean_current_conflict_check",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Formal current-employment conflict checks show nothing."
    },
    {
      "id": "n5",
      "label": "prior_role_consulting_web",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Sequential role changes preserve influence through consulting pathways."
    },
    {
      "id": "n6",
      "label": "asymmetric_review_duration",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Only firms linked to the web experience the slowdown."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## GOV-03 — Scope Creep Pattern
```json
{
  "scenario_id": "vigil_attention_scope_creep_pattern_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "attention_capacity",
    "sustained_attention"
  ],
  "secondary_sub_abilities": [
    "perceptual_inhibition",
    "attention_shifting"
  ],
  "cross_track_overlap_risks": [
    "observational_learning",
    "associative_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "GOV-03",
  "synthetic_domain": "synthetic_public_procurement",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Scope Creep Pattern",
  "blind_task_prompt": "A public project doubles in cost through a sequence of plausible change requests. Explore the graph and submit the most diagnostic reason the overrun is not random.",
  "attention_design": {
    "attentional_bottleneck": "Each individual change looks reasonable, encouraging local attention only. The critical clue is a cross-request pattern showing one subcontractor benefits from nearly all expansions.",
    "salient_but_irrelevant_branches": [
      "Engineering complexity notes",
      "Original design-error debate",
      "Supply inflation branch"
    ],
    "rare_critical_signal": "Every approved scope addition disproportionately benefits the same low-visibility subcontractor cluster.",
    "reorientation_trigger": "The repeated beneficiary pattern should pull attention from individual plausibility to aggregate non-randomness."
  },
  "hidden_mechanism": "An incentive-aligned actor repeatedly manufactures discovery events that justify scope expansion.",
  "disconfirmation_moment": "The same beneficiary captures virtually every approved scope increase despite limited project share.",
  "target_conclusion": "The most diagnostic explanation is systematic manufactured discovery, not random project complexity.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "cost_overrun_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A civic build doubles in cost through many individually approved changes."
    },
    {
      "id": "n1",
      "label": "complexity_change_orders",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "Each change request sounds technically plausible in isolation."
    },
    {
      "id": "n2",
      "label": "inflation_cost_pressures",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "General market inflation explains only a fraction."
    },
    {
      "id": "n3",
      "label": "beneficiary_pattern_table",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Nearly every expansion benefits the same subcontractor slice."
    },
    {
      "id": "n4",
      "label": "share_mismatch_note",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "That subcontractor controls only a minority of the project area."
    },
    {
      "id": "n5",
      "label": "discovery_incentive_chain",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "An incentive network repeatedly generates 'unexpected' findings in the same zone."
    },
    {
      "id": "n6",
      "label": "cumulative_scope_growth",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Individually plausible additions become structurally suspicious in aggregate."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## GOV-04 — Definition Boundary Gap
```json
{
  "scenario_id": "vigil_attention_definition_boundary_gap_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "perceptual_inhibition",
    "attention_shifting"
  ],
  "secondary_sub_abilities": [
    "attention_capacity",
    "sustained_attention"
  ],
  "cross_track_overlap_risks": [
    "concept_formation",
    "observational_learning"
  ],
  "difficulty_tier": "hard",
  "source_skeleton_id": "GOV-04",
  "synthetic_domain": "synthetic_health_governance",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Definition Boundary Gap",
  "blind_task_prompt": "A safety-reporting program looks unusually successful until an external audit arrives. Inspect the governance graph and submit the most diagnostic reason the self-report picture is misleading.",
  "attention_design": {
    "attentional_bottleneck": "Low reported harm looks like good performance. The decisive clue is a mismatch between internal definitions and external audit findings.",
    "salient_but_irrelevant_branches": [
      "Low-event celebration dashboard",
      "Documentation error branch",
      "Reporting software status page"
    ],
    "rare_critical_signal": "Independent review finds far more harm than the internal system ever labels as reportable.",
    "reorientation_trigger": "The audit/self-report gap should redirect attention from execution problems to definitional boundaries."
  },
  "hidden_mechanism": "The institution narrows the operational definition of harm, creating systematic under-capture without obvious technical failure.",
  "disconfirmation_moment": "Independent chart review finds a much higher event rate than the internal program reports.",
  "target_conclusion": "The most diagnostic issue is definitional arbitrage, not exceptional safety performance.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "safety_reporting_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A hospital-like system reports remarkably low harm rates."
    },
    {
      "id": "n1",
      "label": "low_harm_dashboard",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The success signal encourages premature closure."
    },
    {
      "id": "n2",
      "label": "software_health_page",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "The reporting system itself appears technically fine."
    },
    {
      "id": "n3",
      "label": "audit_vs_self_report",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Independent review finds far more harm than internal reports."
    },
    {
      "id": "n4",
      "label": "definition_comparison_note",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Internal rules use a narrower harm definition than the regulator."
    },
    {
      "id": "n5",
      "label": "boundary_application_log",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Events are systematically screened out at the definitional boundary."
    },
    {
      "id": "n6",
      "label": "repeat_event_recurrence",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "Under-capture prevents investigation and allows recurrence."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

## GOV-05 — Pipeline Compounding
```json
{
  "scenario_id": "vigil_attention_pipeline_compounding_v1",
  "version": "1.0",
  "cognitive_track": "attention",
  "primary_sub_abilities": [
    "sustained_attention",
    "attention_capacity"
  ],
  "secondary_sub_abilities": [
    "attention_shifting",
    "perceptual_inhibition"
  ],
  "cross_track_overlap_risks": [
    "associative_learning",
    "concept_formation"
  ],
  "difficulty_tier": "very_hard",
  "source_skeleton_id": "GOV-05",
  "synthetic_domain": "synthetic_science_policy",
  "_track_conversion_note": "The original causal skeleton is preserved, but the benchmark target is Track 2: the agent must allocate attention well under cue competition, ignore plausible distractors, and reorient when disconfirming evidence appears.",
  "scenario_title": "Pipeline Compounding",
  "blind_task_prompt": "A sudden research-funding cut is being evaluated only in immediate budget terms. Explore the policy graph and submit the most diagnostic hidden damage pathway.",
  "attention_design": {
    "attentional_bottleneck": "The immediate dollar figure is the loudest cue. The real harm is distributed across quieter future branches: staff exits, abandoned experiments, review delays, and training-pipeline breaks.",
    "salient_but_irrelevant_branches": [
      "Immediate budget loss board",
      "Political motive branch",
      "Temporary disruption framing"
    ],
    "rare_critical_signal": "Future-output nodes show compounding losses far beyond the first-year budget cut.",
    "reorientation_trigger": "Once experiments and training chains are traced forward, attention should shift from direct cost to pipeline destruction."
  },
  "hidden_mechanism": "A short-term cut destroys accumulated productive capacity and future review/training networks, amplifying harm across years.",
  "disconfirmation_moment": "Measured impact quickly exceeds what the first-year budget number alone would predict.",
  "target_conclusion": "The most diagnostic hidden damage is pipeline compounding, not proportional one-year budget loss.",
  "critical_evidence_node_ids": [
    "n3",
    "n4",
    "n5"
  ],
  "nodes": [
    {
      "id": "n0",
      "label": "grant_cut_brief",
      "kind": "entry",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "A large research cut is being debated mainly as a one-year financial hit."
    },
    {
      "id": "n1",
      "label": "immediate_budget_loss",
      "kind": "surface_hypothesis",
      "initial_visibility": "visible",
      "salience": "high",
      "diagnosticity": "low",
      "content": "The headline figure dominates the discussion."
    },
    {
      "id": "n2",
      "label": "political_motive_branch",
      "kind": "distractor",
      "initial_visibility": "visible",
      "salience": "medium",
      "diagnosticity": "low",
      "content": "Political interpretation is salient but not the operational mechanism."
    },
    {
      "id": "n3",
      "label": "future_pipeline_trace",
      "kind": "pattern_view",
      "initial_visibility": "expand_from:n0",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Training, publication, and review capacity erode over several future cycles."
    },
    {
      "id": "n4",
      "label": "abandoned_experiment_log",
      "kind": "disconfirmation",
      "initial_visibility": "expand_from:n3",
      "salience": "low",
      "diagnosticity": "high",
      "content": "Midstream studies and staff networks collapse in ways the budget line misses."
    },
    {
      "id": "n5",
      "label": "capacity_compounding_chain",
      "kind": "hidden_driver",
      "initial_visibility": "expand_from:n3",
      "salience": "medium",
      "diagnosticity": "high",
      "content": "Past investment is destroyed and future throughput shrinks for years."
    },
    {
      "id": "n6",
      "label": "multi_year_damage_sheet",
      "kind": "downstream_impact",
      "initial_visibility": "expand_from:n5",
      "salience": "medium",
      "diagnosticity": "medium",
      "content": "The long-run research pipeline absorbs a multiplier loss."
    }
  ],
  "edges": [
    {
      "source": "n0",
      "target": "n1",
      "relation": "surfaces_obvious_hypothesis",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n2",
      "relation": "surfaces_plausible_distractor",
      "visibility": "visible",
      "attention_role": "salient_trap"
    },
    {
      "source": "n0",
      "target": "n3",
      "relation": "offers_pattern_view",
      "visibility": "visible",
      "attention_role": "gateway_to_diagnostic_evidence"
    },
    {
      "source": "n3",
      "target": "n4",
      "relation": "reveals_disconfirmation",
      "visibility": "hidden_until_expand",
      "attention_role": "reorientation_trigger"
    },
    {
      "source": "n3",
      "target": "n5",
      "relation": "points_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "true_causal_backbone"
    },
    {
      "source": "n5",
      "target": "n6",
      "relation": "produces_downstream_impact",
      "visibility": "hidden_until_expand",
      "attention_role": "causal_chain_completion"
    },
    {
      "source": "n4",
      "target": "n1",
      "relation": "undercuts_surface_hypothesis",
      "visibility": "hidden_until_expand",
      "attention_role": "forces_attention_shift"
    },
    {
      "source": "n4",
      "target": "n5",
      "relation": "redirects_to_hidden_driver",
      "visibility": "hidden_until_expand",
      "attention_role": "diagnostic_reorientation"
    }
  ]
}
```

