"""
Expand Track 2 attention scenarios from 7 nodes to 10 nodes.

Adds per-scenario:
  n7: extra_distractor   — high salience, low diagnosticity; another salient trap branch
  n8: false_alarm        — high salience, initially looks diagnostic but is not
  n9: deep_rare_signal   — numeric salience=0.12, diagnosticity=0.88; fires RELEVANCE_SHIFT

Edges added:
  n0 → n7  (salient_trap)
  n0 → n8  (false_alarm)
  n8 → n1  (reinforces_obvious_hypothesis)     ← deepens red herring pull
  n5 → n9  (reveals_deeper_mechanism)          ← must reach n5 first
  n9 → n6  (converges_to_downstream_impact)

AttentionAdapter reads: id, label, kind, initial_visibility, salience, diagnosticity, content.
Edges: source, target, relation, visibility, attention_role.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "vigil" / "scenarios" / "packs"
ATTN_FILE = PACK / "track2_attention_synthetic_scenarios.json"

# Per-scenario extension content — keyed by scenario_id.
# Each entry provides labels/content for the 3 new nodes.
EXTENSIONS: dict[str, dict] = {
    "vigil_attention_mireglass_phase_shift_v1": {
        "extra_distractor_label": "rainfall_inflow_spike",
        "extra_distractor_content": "Heavy rainfall coincided with the loss onset, raising a plausible hydraulic dilution explanation.",
        "false_alarm_label": "bloom_peak_bioassay_flag",
        "false_alarm_content": "A bioassay flag at bloom peak appears to confirm toxicity as the driver — but the threshold is precautionary, not lethal.",
        "deep_rare_label": "oxygen_cycle_shift_log",
        "deep_rare_content": "Post-transition oxygen telemetry shows a 40% nocturnal depletion zone emerging only after the Plareef-to-Diala community flip.",
    },
    "vigil_attention_carrion_glider_cascade_v1": {
        "extra_distractor_label": "carrion_site_density_map",
        "extra_distractor_content": "Carrion availability maps show a strong spatial overlap with glider decline areas, pointing to foraging competition.",
        "false_alarm_label": "pollution_exposure_index",
        "false_alarm_content": "A regional pollution index correlates with glider range contraction at r=0.61, appearing diagnostic at first glance.",
        "deep_rare_label": "thermal_column_collapse_record",
        "deep_rare_content": "Micro-meteorological logs reveal thermal column disruption at the precise altitude band gliders use for passive soaring — overlooked because data requires specialist decoding.",
    },
    "vigil_attention_brineisle_subsidy_break_v1": {
        "extra_distractor_label": "salinity_gradient_chart",
        "extra_distractor_content": "Salinity measurements at the estuary mouth deviate sharply in the loss year, drawing attention as an obvious environmental stressor.",
        "false_alarm_label": "harvest_pressure_report",
        "false_alarm_content": "Harvest effort data rises 22% in the affected zone, appearing to explain the decline through direct extraction.",
        "deep_rare_label": "nursery_connectivity_break",
        "deep_rare_content": "Hydrological modeling reveals the subsidy disruption severed larval transport pathways between offshore spawning and inshore nursery habitats — invisible at surface-level monitoring.",
    },
    "vigil_attention_shadefang_foraging_shift_v1": {
        "extra_distractor_label": "prey_abundance_transect",
        "extra_distractor_content": "Prey biomass surveys show a 30% decline in core territories, making food scarcity the obvious candidate explanation.",
        "false_alarm_label": "territorial_intrusion_log",
        "false_alarm_content": "GPS collars record elevated territorial intrusion events coinciding with foraging shift onset, suggesting displacement pressure.",
        "deep_rare_label": "sensory_interference_field_note",
        "deep_rare_content": "Acoustic monitoring reveals ultrasonic interference at foraging sites from a new infrastructure installation — audible only to Shadefang's echolocation range.",
    },
    "vigil_attention_sediment_debt_release_v1": {
        "extra_distractor_label": "upstream_land_use_change",
        "extra_distractor_content": "Agricultural conversion upstream coincides with sediment event timing, appearing to explain the fine-particle load increase.",
        "false_alarm_label": "flood_event_record",
        "false_alarm_content": "A 1-in-10-year flood event occurs in the same monitoring window and is treated as the mobilizing force for the sediment load.",
        "deep_rare_label": "legacy_deposit_age_analysis",
        "deep_rare_content": "Radioisotope dating of the mobilized fine particles shows they are 40–80 years old — definitively pre-dating any upstream land use change.",
    },
    "vigil_attention_juvenile_skew_cascade_v1": {
        "extra_distractor_label": "recruitment_pulse_record",
        "extra_distractor_content": "An unusually large juvenile recruitment cohort is documented and interpreted as the cause of the age-structure skew.",
        "false_alarm_label": "predation_pressure_survey",
        "false_alarm_content": "Predator density surveys show elevated presence in adult age-class habitats, creating a plausible adult mortality explanation.",
        "deep_rare_label": "size_selective_harvest_analysis",
        "deep_rare_content": "Gear selectivity analysis shows the fishery removes individuals precisely at sexual maturation size — removing spawners before they contribute, leaving juveniles accumulating.",
    },
    "vigil_attention_larval_bottleneck_release_v1": {
        "extra_distractor_label": "sea_surface_temperature_anomaly",
        "extra_distractor_content": "A +1.8°C sea surface temperature anomaly is recorded during the larval dispersal window and interpreted as the bottleneck cause.",
        "false_alarm_label": "current_velocity_shift_log",
        "false_alarm_content": "Current velocity increases by 34% in the larval transport corridor, appearing to explain dispersal failure through physical advection.",
        "deep_rare_label": "settlement_cue_depletion_assay",
        "deep_rare_content": "Chemical assays of settlement substrate reveal depletion of crustose coralline algae-derived settlement cues — the proximate larval filter that temperature and current models do not capture.",
    },
    "vigil_attention_function_without_structure_v1": {
        "extra_distractor_label": "coral_cover_decline_survey",
        "extra_distractor_content": "Benthic surveys show a 28% reduction in live coral cover, immediately linking structural decline to functional collapse.",
        "false_alarm_label": "bleaching_event_record",
        "false_alarm_content": "A documented bleaching event two years prior appears to explain current functional deficits through delayed recovery failure.",
        "deep_rare_label": "functional_redundancy_audit",
        "deep_rare_content": "Guild-level analysis reveals the structurally simplified reef retains near-normal species richness but with all species from a single functional group — redundancy, not diversity, is the missing element.",
    },
    "vigil_attention_masked_reproduction_failure_v1": {
        "extra_distractor_label": "floral_resource_density_map",
        "extra_distractor_content": "Floral resource maps show adequate bloom density in decline zones, appearing to exclude forage scarcity as the driver.",
        "false_alarm_label": "pesticide_residue_screen",
        "false_alarm_content": "A pesticide residue screen detects sub-lethal concentrations across the decline zone, consistent with reproductive impairment.",
        "deep_rare_label": "queen_supersedure_timing_log",
        "deep_rare_content": "Colony monitoring records show accelerated queen supersedure cycles correlated with landscape fragmentation — colony replacement strain that operates independently of pesticide exposure.",
    },
    "vigil_attention_bystander_field_exposure_v1": {
        "extra_distractor_label": "application_rate_overage_report",
        "extra_distractor_content": "Field application logs show 18% exceedance of label-specified rates in the affected zones, appearing to explain elevated bystander exposure.",
        "false_alarm_label": "wind_event_coincidence_record",
        "false_alarm_content": "Meteorological records show an anomalous wind event on the application date, consistent with drift-mediated bystander exposure.",
        "deep_rare_label": "volatilization_temperature_correlation",
        "deep_rare_content": "Soil temperature monitoring reveals the active ingredient volatilizes at soil temperatures that occurred in the post-application window — creating delayed gaseous exposure distinct from spray drift.",
    },
    "vigil_attention_biofilm_reservoir_v1": {
        "extra_distractor_label": "hand_hygiene_compliance_audit",
        "extra_distractor_content": "A hand hygiene compliance audit shows 74% adherence — below the 90% target, making compliance failure the obvious infection pathway.",
        "false_alarm_label": "antibiotic_exposure_record",
        "false_alarm_content": "Antibiotic prescription data shows a 40% increase in the affected ward during the outbreak period, consistent with selection-pressure amplification.",
        "deep_rare_label": "drain_biofilm_genotyping_result",
        "deep_rare_content": "Whole-genome sequencing of drain biofilm samples matches outbreak isolates with 99.6% identity — the sink drain as reservoir is only visible in molecular typing, not surface culture.",
    },
    "vigil_attention_iatrogenic_masquerade_v1": {
        "extra_distractor_label": "disease_progression_trajectory",
        "extra_distractor_content": "The patient's disease trajectory charts show progression consistent with natural disease advancement, obscuring the iatrogenic component.",
        "false_alarm_label": "comorbidity_interaction_flag",
        "false_alarm_content": "A comorbidity flag is triggered during chart review, leading the clinical team to attribute the finding to disease interaction rather than drug effect.",
        "deep_rare_label": "rechallenge_dechallenge_timeline",
        "deep_rare_content": "Medication administration records reveal the symptom followed dose escalation within 72 hours and partially resolved on dose reduction — a re/de-challenge pattern only visible by cross-referencing drug and symptom timelines.",
    },
    "vigil_attention_impossible_placebo_signal_v1": {
        "extra_distractor_label": "site_enrollment_rate_variation",
        "extra_distractor_content": "Enrollment rate variation across trial sites correlates with outcome variation, appearing to explain the anomalous placebo signal through site-level confounding.",
        "false_alarm_label": "unblinding_event_log",
        "false_alarm_content": "Several unblinding events are documented during the trial, creating a plausible expectation-bias explanation for the inflated placebo arm.",
        "deep_rare_label": "natural_history_regression_model",
        "deep_rare_content": "Longitudinal modeling of the target condition's natural history reveals a spontaneous improvement cycle coinciding precisely with the trial's primary endpoint window.",
    },
    "vigil_attention_site_noise_dilution_v1": {
        "extra_distractor_label": "protocol_deviation_registry",
        "extra_distractor_content": "Protocol deviation rates differ substantially across sites, pointing to implementation quality as the driver of site-level signal variation.",
        "false_alarm_label": "baseline_imbalance_table",
        "false_alarm_content": "Baseline characteristic tables show modest imbalances across sites that appear to explain differential treatment response.",
        "deep_rare_label": "assay_calibration_drift_log",
        "deep_rare_content": "Central lab records show assay calibration drift at two high-enrollment sites, systematically depressing measured biomarker change without affecting clinical rating scales.",
    },
    "vigil_attention_plasmid_network_v1": {
        "extra_distractor_label": "antibiotic_stewardship_gap_audit",
        "extra_distractor_content": "Antibiotic stewardship records show a compliance gap in one ward, appearing to localize the resistance emergence to a selection pressure hotspot.",
        "false_alarm_label": "patient_transfer_log",
        "false_alarm_content": "Patient transfer records between units correlate with resistance spread timing, consistent with patient-mediated transmission.",
        "deep_rare_label": "conjugation_frequency_assay",
        "deep_rare_content": "In vitro conjugation assays using environmental isolates show plasmid transfer rates 40× higher than reference strains — the mobile element itself has unusual transmissibility.",
    },
    "vigil_attention_line_origin_misattribution_v1": {
        "extra_distractor_label": "insertion_site_assessment",
        "extra_distractor_content": "The insertion technique assessment flags a procedural deviation at the time of line placement, directing attention to the placement event.",
        "false_alarm_label": "antimicrobial_lock_protocol_audit",
        "false_alarm_content": "Audit reveals the antimicrobial lock protocol was not initiated on schedule, appearing to explain the failure of infection prevention.",
        "deep_rare_label": "hub_colonization_sequence_data",
        "deep_rare_content": "Microbiological sequencing of hub swabs shows colonization preceding bacteremia by 5 days — the entry point was the access hub, not the insertion site.",
    },
    "vigil_attention_ice_vector_cluster_v1": {
        "extra_distractor_label": "temperature_excursion_log",
        "extra_distractor_content": "Cold chain temperature logs show excursions in the same shipment window as the outbreak, pointing to cold chain failure as the vector.",
        "false_alarm_label": "handler_infection_screen",
        "false_alarm_content": "Screening of product handlers finds subclinical infection rates of 12% — consistent with human contamination as the proximate source.",
        "deep_rare_label": "biofilm_persistence_assay",
        "deep_rare_content": "Environmental swabs of the ice-making unit interior reveal pathogen biofilm persisting across three cleaning cycles — the production environment, not the cold chain or handler, is the reservoir.",
    },
    "vigil_attention_anchor_break_signal_v1": {
        "extra_distractor_label": "prior_test_positive_rate",
        "extra_distractor_content": "The prior positive test rate in the referring population is high, making anchoring to the test result appear diagnostically justified.",
        "false_alarm_label": "symptom_cluster_similarity_score",
        "false_alarm_content": "A symptom cluster similarity score flags the case as resembling the anchor diagnosis at 0.81 concordance, reinforcing the anchored read.",
        "deep_rare_label": "atypical_presentation_registry_match",
        "deep_rare_content": "A rare-presentation registry lookup finds three documented cases with identical symptom pattern attributable to an alternative diagnosis — accessible only through an unfamiliar second-line database.",
    },
    "vigil_attention_detection_gap_cluster_v1": {
        "extra_distractor_label": "reporting_lag_analysis",
        "extra_distractor_content": "Reporting lag analysis shows cases in the cluster were systematically reported 8–12 days late, appearing to explain the apparent cluster as a detection artifact.",
        "false_alarm_label": "healthcare_seeking_behavior_survey",
        "false_alarm_content": "A healthcare-seeking survey shows lower utilization rates in the cluster area, consistent with under-detection through access barriers.",
        "deep_rare_label": "diagnostic_criterion_boundary_audit",
        "deep_rare_content": "Retrospective chart review reveals the local diagnostic coding criterion was one level more restrictive than the national standard — systematically excluding a subset of qualifying cases.",
    },
    "vigil_attention_parallel_waterline_v1": {
        "extra_distractor_label": "plumbing_age_survey",
        "extra_distractor_content": "Infrastructure age surveys show the affected buildings have older plumbing, consistent with lead leaching as the primary exposure route.",
        "false_alarm_label": "treatment_plant_output_record",
        "false_alarm_content": "Treatment plant output records show a brief pH deviation coinciding with the exposure period, appearing to explain corrosion-mediated leaching.",
        "deep_rare_label": "stagnation_pattern_meter_data",
        "deep_rare_content": "Smart meter flow data reveals the affected units show prolonged overnight stagnation exceeding 8 hours — the stagnation pattern, not pipe age or pH, determines first-draw lead concentration.",
    },
    "vigil_attention_missing_safety_valve_v1": {
        "extra_distractor_label": "load_balancer_config_audit",
        "extra_distractor_content": "Load balancer configuration review finds a suboptimal routing table that appears to explain the traffic spike misdistribution.",
        "false_alarm_label": "cache_invalidation_log",
        "false_alarm_content": "A cache invalidation event coincides with the cascade onset, pointing to a stale cache as the proximate trigger of the failure.",
        "deep_rare_label": "retry_storm_telemetry",
        "deep_rare_content": "Distributed tracing telemetry reveals an exponential backoff misconfiguration causing downstream services to retry simultaneously — the retry storm amplified the initial load spike by 12×.",
    },
    "vigil_attention_foundational_lookup_invisibility_v1": {
        "extra_distractor_label": "query_volume_spike_log",
        "extra_distractor_content": "Query volume to the lookup service spikes 300% in the incident window, appearing to explain the performance degradation through load.",
        "false_alarm_label": "index_fragmentation_report",
        "false_alarm_content": "Database index fragmentation is flagged at 67%, consistent with lookup latency degradation under normal query patterns.",
        "deep_rare_label": "hot_key_distribution_trace",
        "deep_rare_content": "Key access distribution telemetry reveals 83% of lookup traffic concentrates on 0.04% of keys — a hot-key pattern invisible to aggregate volume metrics but saturating a single shard.",
    },
    "vigil_attention_delegated_token_breach_v1": {
        "extra_distractor_label": "token_rotation_compliance_log",
        "extra_distractor_content": "Token rotation logs show a compliance gap where tokens were not rotated on schedule, appearing to explain the breach through credential staleness.",
        "false_alarm_label": "phishing_campaign_correlation",
        "false_alarm_content": "A phishing campaign targeting the organization's domain is documented in the same window, consistent with credential theft as the initial access vector.",
        "deep_rare_label": "permission_scope_creep_audit",
        "deep_rare_content": "OAuth scope audit reveals the delegated token was issued with wildcard resource access rather than the specified narrow scope — the token's blast radius was set at issuance, not at breach.",
    },
    "vigil_attention_shared_vendor_paralysis_v1": {
        "extra_distractor_label": "vendor_sla_breach_record",
        "extra_distractor_content": "The vendor's SLA breach documentation is publicly available and frames the failure as a contractual performance issue.",
        "false_alarm_label": "demand_surge_forecast_error",
        "false_alarm_content": "Demand forecasting records show the service spike was not anticipated, appearing to explain capacity failure through planning error.",
        "deep_rare_label": "dependency_coupling_graph",
        "deep_rare_content": "Infrastructure dependency mapping reveals that five independent public services share a single undocumented synchronous dependency on the vendor's authentication endpoint — the coupling was never modeled in capacity planning.",
    },
    "vigil_attention_concentration_revelation_v1": {
        "extra_distractor_label": "logistics_route_disruption_report",
        "extra_distractor_content": "A documented logistics route disruption in the quarter before the shortage appears to explain the supply gap through transport infrastructure.",
        "false_alarm_label": "demand_spike_record",
        "false_alarm_content": "Demand data shows a 25% volume increase in the affected category, consistent with demand-side explanation for the shortage.",
        "deep_rare_label": "single_source_dependency_audit",
        "deep_rare_content": "Supplier mapping reveals that 91% of the critical input comes from a single facility whose capacity was already running at 97% utilization before the disruption — the system had no slack to absorb any demand or supply variance.",
    },
    "vigil_attention_wrong_target_success_v1": {
        "extra_distractor_label": "compliance_rate_improvement_chart",
        "extra_distractor_content": "Post-policy compliance metrics improve substantially, appearing to confirm the policy is achieving its intended behavioral effect.",
        "false_alarm_label": "enforcement_action_log",
        "false_alarm_content": "Enforcement action rates increase following policy implementation, consistent with the compliance improvements being enforcement-driven.",
        "deep_rare_label": "displacement_effect_audit",
        "deep_rare_content": "Geo-coded behavior tracking reveals the targeted behavior declined in regulated zones by exactly the amount it increased in adjacent unregulated zones — policy success was spatial displacement, not behavior change.",
    },
    "vigil_attention_temporal_conflict_web_v1": {
        "extra_distractor_label": "stakeholder_objection_log",
        "extra_distractor_content": "Stakeholder objection filings during the review period are numerous and varied, appearing to explain the decision stall through opposition intensity.",
        "false_alarm_label": "regulatory_backlog_chart",
        "false_alarm_content": "The regulatory body's overall review backlog charts show a 60% increase in the same period, consistent with administrative capacity as the binding constraint.",
        "deep_rare_label": "statutory_clock_interaction_analysis",
        "deep_rare_content": "Legal timeline analysis reveals two overlapping statutory review clocks whose reset provisions interact in a way that indefinitely re-initiates the review window — a procedural trap invisible without cross-referencing both statutes.",
    },
    "vigil_attention_scope_creep_pattern_v1": {
        "extra_distractor_label": "contractor_change_order_log",
        "extra_distractor_content": "Change order logs show a high rate of contractor-initiated scope modifications, appearing to explain cost overruns through contractor behavior.",
        "false_alarm_label": "requirements_instability_report",
        "false_alarm_content": "Requirements change frequency is documented at 3× the sector benchmark, consistent with client-side instability as the driver of scope expansion.",
        "deep_rare_label": "approval_threshold_gap_audit",
        "deep_rare_content": "Procurement records reveal individual change orders were structured to stay below the threshold requiring senior approval — the aggregate scope expansion was 340% but no individual approval triggered review.",
    },
    "vigil_attention_definition_boundary_gap_v1": {
        "extra_distractor_label": "reporting_entity_compliance_audit",
        "extra_distractor_content": "Compliance audits show reporting entities are following the definition accurately, appearing to rule out measurement error as the explanation for data gaps.",
        "false_alarm_label": "data_system_interoperability_report",
        "false_alarm_content": "An interoperability assessment flags system integration gaps between reporting entities and the central registry, consistent with technical data loss.",
        "deep_rare_label": "boundary_case_classification_log",
        "deep_rare_content": "A sample audit of boundary cases reveals that a 12-word definitional clause excludes the fastest-growing category of the target phenomenon — the exclusion was intentional in the original statute but reflects a 1998 assumption about category prevalence.",
    },
    "vigil_attention_pipeline_compounding_v1": {
        "extra_distractor_label": "funding_cycle_alignment_gap",
        "extra_distractor_content": "Funding cycle misalignments create a documented 14-month gap between research completion and career transition support, appearing to explain the pipeline break.",
        "false_alarm_label": "external_labor_market_pull",
        "false_alarm_content": "Salary benchmarking shows a 35% premium for sector exit, consistent with market pull as the explanation for pipeline attrition.",
        "deep_rare_label": "compounding_dropout_model",
        "deep_rare_content": "Cohort retention modeling reveals that three independent attrition pressures — each individually survivable — compound multiplicatively across pipeline stages, producing a 91% exit rate that no single factor analysis identifies.",
    },
}


def expand_attention_scenario(s: dict, ext: dict) -> dict:
    """Add 3 new nodes and 5 new edges to an existing attention scenario dict."""
    existing_nodes = s.get("nodes", [])
    existing_edges = s.get("edges", [])

    new_nodes = [
        {
            "id": "n7",
            "label": ext["extra_distractor_label"],
            "kind": "extra_distractor",
            "initial_visibility": "visible",
            "salience": "high",
            "diagnosticity": "low",
            "content": ext["extra_distractor_content"],
        },
        {
            "id": "n8",
            "label": ext["false_alarm_label"],
            "kind": "false_alarm",
            "initial_visibility": "visible",
            "salience": "high",
            "diagnosticity": "low",
            "content": ext["false_alarm_content"],
        },
        {
            # Numeric values guarantee RELEVANCE_SHIFT fires on inspect
            "id": "n9",
            "label": ext["deep_rare_label"],
            "kind": "deep_rare_signal",
            "initial_visibility": "expand_from:n5",
            "salience": 0.12,
            "diagnosticity": 0.88,
            "content": ext["deep_rare_content"],
        },
    ]

    new_edges = [
        {
            "source": "n0",
            "target": "n7",
            "relation": "surfaces_another_distractor",
            "visibility": "visible",
            "attention_role": "salient_trap",
        },
        {
            "source": "n0",
            "target": "n8",
            "relation": "surfaces_false_alarm",
            "visibility": "visible",
            "attention_role": "salient_trap",
        },
        {
            # False alarm reinforces the surface hypothesis — deepens the red herring pull
            "source": "n8",
            "target": "n1",
            "relation": "reinforces_obvious_hypothesis",
            "visibility": "visible",
            "attention_role": "hypothesis_reinforcement",
        },
        {
            # Deep rare signal only accessible after n5 (hidden driver)
            "source": "n5",
            "target": "n9",
            "relation": "reveals_deeper_mechanism",
            "visibility": "hidden_until_expand",
            "attention_role": "true_causal_backbone",
        },
        {
            "source": "n9",
            "target": "n6",
            "relation": "converges_to_downstream_impact",
            "visibility": "hidden_until_expand",
            "attention_role": "causal_chain_completion",
        },
    ]

    result = dict(s)
    result["nodes"] = existing_nodes + new_nodes
    result["edges"] = existing_edges + new_edges
    return result


def main() -> None:
    with open(ATTN_FILE) as f:
        raw = json.load(f)

    scenarios: list[dict] = raw if isinstance(raw, list) else raw.get("scenarios", [])

    expanded = []
    missing_ext = []
    for s in scenarios:
        sid = s.get("scenario_id", "")
        ext = EXTENSIONS.get(sid)
        if ext is None:
            missing_ext.append(sid)
            expanded.append(s)
        else:
            expanded.append(expand_attention_scenario(s, ext))

    if missing_ext:
        print(f"WARNING: no extension data for {len(missing_ext)} scenarios: {missing_ext}")

    counts = [(s.get("scenario_id", "?"), len(s.get("nodes", []))) for s in expanded]
    failed = [(sid, n) for sid, n in counts if n < 10]
    if failed:
        for sid, n in failed:
            print(f"FAIL: {sid} has {n} nodes — need ≥10")
        raise SystemExit(1)

    out = expanded if isinstance(raw, list) else {"scenarios": expanded}
    with open(ATTN_FILE, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Written {len(expanded)} attention scenarios to {ATTN_FILE}")
    print(f"Node counts: min={min(n for _, n in counts)}, max={max(n for _, n in counts)}")
    print(f"All {len(expanded)} scenarios have ≥10 nodes. ✓")


if __name__ == "__main__":
    main()
