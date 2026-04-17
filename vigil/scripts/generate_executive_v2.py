"""
Generate vigil_track3_executive_scenarios_v2.json — 30 executive scenarios rebuilt
to 15 nodes each with branching structure.

Run from project root:
    python vigil/scripts/generate_executive_v2.py
"""

import json
from pathlib import Path

OUTPUT_PATH = Path("vigil/scenarios/packs/vigil_track3_executive_scenarios_from_skeletons_v1.json")

EDGES_TEMPLATE = [
    {"from": "n0",  "to": "n1",  "relation": "suggests_obvious_path"},
    {"from": "n0",  "to": "n2",  "relation": "suggests_competing_path"},
    {"from": "n0",  "to": "n12", "relation": "co_occurs_with"},
    {"from": "n1",  "to": "n3",  "relation": "supported_by"},
    {"from": "n1",  "to": "n4",  "relation": "leads_to"},
    {"from": "n2",  "to": "n5",  "relation": "supported_by"},
    {"from": "n3",  "to": "n6",  "relation": "tested_by"},
    {"from": "n5",  "to": "n7",  "relation": "tested_by"},
    {"from": "n6",  "to": "n8",  "relation": "forces_pivot"},
    {"from": "n7",  "to": "n8",  "relation": "forces_pivot"},
    {"from": "n8",  "to": "n9",  "relation": "reveals"},
    {"from": "n9",  "to": "n10", "relation": "confirms"},
    {"from": "n10", "to": "n11", "relation": "resolves"},
    {"from": "n12", "to": "n13", "relation": "related"},
    {"from": "n13", "to": "n14", "relation": "dead_end"},
]


def make_nodes(n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14):
    labels = [
        "Entry Brief", "Obvious Hypothesis A", "Competing Hypothesis B",
        "Evidence for A", "Dead End A", "Evidence for B",
        "Disconfirmation A", "Disconfirmation B", "Pivot Reframe",
        "Mechanism Part 1", "Mechanism Part 2", "True Root Cause",
        "Red Herring C", "Red Herring D", "Dead End B",
    ]
    types = [
        "brief", "red_herring", "red_herring",
        "evidence", "dead_end", "evidence",
        "disconfirmation", "disconfirmation", "pivot",
        "mechanism", "mechanism", "resolution",
        "distractor", "distractor", "dead_end",
    ]
    descs = [n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14]
    return [
        {"id": f"n{i}", "type": types[i], "label": labels[i], "description": descs[i]}
        for i in range(15)
    ]


def scenario(sid, skeleton, title, domain, summary, tempting, pivot_text, focus,
             n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14):
    return {
        "scenario_id": sid,
        "version": "2.0",
        "cognitive_track": "executive_functions",
        "primary_sub_abilities": ["cognitive_flexibility", "planning"],
        "secondary_sub_abilities": ["inhibitory_control", "working_memory"],
        "difficulty_tier": "very_hard",
        "source_skeleton_id": skeleton,
        "scenario_title": title,
        "synthetic_domain": domain,
        "scenario_summary": summary,
        "executive_design_notes": {
            "tempting_wrong_path": tempting,
            "required_pivot": pivot_text,
            "process_scoring_focus": focus,
        },
        "nodes": make_nodes(n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14),
        "edges": EDGES_TEMPLATE,
    }


SCENARIOS = [

# =============================================================================
# ECO-01 — freshwater_ecology_investigation — tipping point: bloom succession
# =============================================================================
scenario(
    sid="vigil_exec_mireglass_bloom_shift_v2",
    skeleton="ECO-01", title="The Mireglass Bloom Shift",
    domain="freshwater_ecology_investigation",
    summary="Fish crash across Mireglass Marsh after a dramatic seasonal bloom. Multiple concurrent stressors are visible. The hidden mechanism is a post-peak community transition that alters oxygen and food structure, not peak toxicity.",
    tempting="Lock onto peak bloom toxicity without examining the succession window.",
    pivot_text="Abandon peak-toxicity framing. Investigate the two-week post-peak succession period for oxygen and food-web disruption.",
    focus=["pivot_latency_after_toxicity_failure", "red_herring_suppression", "goal_maintenance"],
    n0="Fish crash across Mireglass Marsh after a dramatic seasonal bloom. Construction noise, rainfall spikes, and the bloom peak itself all look causal. Your budget is limited. Identify the true mechanism before running out of investigation steps.",
    n1="Hypothesis A: Peak-bloom toxins released during the algal maximum are lethal to fish. The bloom is dense and highly visible — toxin release seems the obvious direct mechanism.",
    n2="Hypothesis B: Heavy rainfall in the week prior to the crash elevated runoff nutrients and triggered a sudden oxygen depression event independent of the bloom.",
    n3="Toxin assay samples collected at bloom peak show elevated cyanotoxin readings. The data superficially supports direct toxic kill during peak bloom.",
    n4="Detailed toxin-dose modelling shows cyanotoxin concentrations never exceeded 40% of the acute lethal threshold for any fish species in the marsh. Hypothesis A is a dead end.",
    n5="Rainfall and turbidity records show a spike three days before the crash. This is consistent with Hypothesis B but does not account for spatial clustering of fish deaths.",
    n6="Peak toxin assays came back below lethal thresholds. The fish crash occurs 11 days after peak, during species turnover — not at toxin maximum. Hypothesis A is ruled out.",
    n7="Oxygen depression modelling shows the rainfall-induced turbidity event cleared within 48 hours — well before the crash. Rainfall alone cannot account for the mortality pattern.",
    n8="Pivot: The two-week post-peak succession window is the key period. As dominant algae shifts from cyanobacteria to diatoms, oxygen dynamics and food structure both change sharply.",
    n9="Post-peak oxygen profiles show a succession-driven instability: rapid cyanobacteria decomposition consumes dissolved oxygen while the new diatom layer has not yet stabilised photosynthesis.",
    n10="Macroinvertebrate surveys show a crash in food-web support species precisely during the succession window, compounding the oxygen stress and cutting off energy inputs to fish populations.",
    n11="Root cause: nutrient overload triggered the bloom, but the proximate killer is succession shock — not peak toxicity. Actionable intervention targets post-peak oxygen management and food-web stabilisation.",
    n12="Red herring: Construction noise from a nearby road project is temporally correlated with the fish crash. Several community reports cite disturbance as the cause.",
    n13="Construction disturbance data shows noise and vibration within known fish stress thresholds, and the mortality pattern does not correspond to construction zones. Noise is not causal.",
    n14="Acoustic monitoring confirms no stress-level vibration events reached the main marsh fish habitat. Construction is definitively excluded.",
),

# =============================================================================
# ECO-02 — ecology_public_health_cascade — feedback loop: scavenger gap
# =============================================================================
scenario(
    sid="vigil_exec_grayspine_scavenger_gap_v2",
    skeleton="ECO-02", title="The Grayspine Scavenger Gap",
    domain="ecology_public_health_cascade",
    summary="Rising bite-fever deaths near livestock routes. Direct chemical exposure and sanitation failures are the obvious suspects. The true driver is a scavenger collapse that opened a carcass-to-substitute-scavenger-to-human infection chain.",
    tempting="Focus investigation on direct human toxicology and sanitation failures near livestock zones.",
    pivot_text="Shift from direct exposure to the carcass disposal and scavenger ecology chain that links livestock mortality to human infection.",
    focus=["pivot_latency", "red_herring_suppression", "evidence_ordering"],
    n0="Human bite-fever deaths are rising in three districts near livestock transit routes. Chemical exposure, sanitation failures, and wildlife contact have all been proposed. You have limited investigation budget.",
    n1="Hypothesis A: Pesticide or veterinary chemical runoff from livestock operations is directly contaminating water sources used by affected communities.",
    n2="Hypothesis B: Sanitation infrastructure failure along livestock routes has increased human exposure to contaminated soil and surface water.",
    n3="Pesticide screening of water sources near livestock zones shows detectable but sub-threshold organophosphate levels. This superficially supports Hypothesis A.",
    n4="Full toxicological workup on affected patients shows no organophosphate biomarkers. The chemical exposure pathway does not explain the mortality pattern. Dead end.",
    n5="Sanitation survey maps show degraded latrine infrastructure in two of the three affected districts, consistent with Hypothesis B.",
    n6="Chemical runoff cannot explain why mortality clusters match former scavenger bird range rather than pesticide intensity or water source proximity. Hypothesis A is ruled out.",
    n7="Disease mapping shows mortality hotspots along carcass disposal sites, not sanitation failure zones. Sanitation infrastructure does not predict case location. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the carcass disposal ecology. A scavenger population crash has left carcasses as a primary infection reservoir, with substitute scavenger species bridging to humans.",
    n9="Scavenger bird survey shows a 74% population decline over three years in affected districts, coinciding with increased livestock veterinary drug use. Carcasses accumulate unprocessed.",
    n10="Substitute scavenger species — feral dog packs and urban rats — have expanded into the carcass niche and are found in significantly elevated densities near human settlements in affected zones.",
    n11="Root cause: veterinary drug residues in livestock carcasses collapsed scavenger populations. Substitute scavengers bridge the infection from carcass reservoir to human settlements.",
    n12="Red herring: A regional drought year is temporally correlated with the start of the mortality rise, leading to speculation about water scarcity driving behavioural change.",
    n13="Drought analysis shows affected and unaffected districts experienced equal water stress. Drought does not predict case distribution. The correlation is coincidental.",
    n14="Hydrological records confirm no differential drought exposure between high- and low-mortality districts. Drought is excluded as a driver.",
),

# =============================================================================
# ECO-03 — cross_ecosystem_ecology — tipping point: terrestrial-marine nitrogen
# =============================================================================
scenario(
    sid="vigil_exec_coralreach_nitrogen_bridge_v2",
    skeleton="ECO-03", title="The Coralreach Nitrogen Bridge",
    domain="cross_ecosystem_ecology",
    summary="Fish biomass collapses around some islands but not others. Marine stressors fail to explain the spatial pattern. The true driver is a terrestrial predator removing seabirds and cutting the guano nitrogen subsidy that had been sustaining adjacent reefs.",
    tempting="Treat the decline as a purely marine phenomenon driven by bleaching or fishing pressure.",
    pivot_text="Abandon marine-only framing. Investigate terrestrial predator pressure on seabird colonies as the hidden input to reef productivity.",
    focus=["cross_domain_hypothesis", "pivot_latency", "red_herring_suppression"],
    n0="Fish biomass has collapsed around five islands in the Coralreach Archipelago but not three control islands with similar reef structure. Marine heat events, fishing pressure, and bleaching are all plausible. Budget is limited.",
    n1="Hypothesis A: Differential bleaching intensity explains the spatial pattern — affected islands experienced more severe thermal stress than control islands.",
    n2="Hypothesis B: Fishing pressure is higher around the affected islands, reducing fish populations through direct exploitation rather than ecosystem change.",
    n3="Sea surface temperature records from the past three years show a 0.8°C higher mean around affected islands, consistent with more severe bleaching stress and Hypothesis A.",
    n4="Coral cover surveys show no statistically significant difference in bleaching severity between affected and control islands. Temperature difference is too small to explain the biomass gap.",
    n5="Fishing effort logbooks show marginally higher boat hours near two of the five affected islands, consistent with Hypothesis B.",
    n6="Coral bleaching surveys show equivalent coral cover across affected and control sites. Sea temperature alone does not predict the fish decline pattern. Hypothesis A is ruled out.",
    n7="Independent observer fishing records and satellite vessel tracking show no significant differential fishing effort across the affected vs. control island groups. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the terrestrial ecosystem of affected islands. Something on land is changing the productivity of adjacent reefs without visible marine stressors.",
    n9="Seabird colony counts on affected islands show an 81% decline over four years, coinciding with the introduction of invasive rats on those islands. Control islands are predator-free.",
    n10="Guano deposition monitoring shows that seabird nutrient input to adjacent reef zones on affected islands has dropped by 67%. Reef primary productivity correlates with guano input, not marine heat.",
    n11="Root cause: invasive predators collapsed seabird colonies, cutting the guano nitrogen subsidy that had been supporting adjacent reef productivity. The decline is terrestrially driven.",
    n12="Red herring: A regional shipping lane expansion brought increased vessel traffic past affected islands, suggesting anchor damage or propeller wash as a disturbance mechanism.",
    n13="Seafloor surveys show no differential anchor scarring or propeller disturbance between affected and control sites. Shipping traffic is not the driver.",
    n14="Benthic video transects confirm intact seafloor substrate at all affected sites. Vessel disturbance is excluded.",
),

# =============================================================================
# ECO-04 — invasive_species_ecology — feedback loop: competition cascade
# =============================================================================
scenario(
    sid="vigil_exec_thornlake_competitor_cascade_v2",
    skeleton="ECO-04", title="The Thornlake Competitor Cascade",
    domain="invasive_species_ecology",
    summary="Native fish in Thornlake are declining despite stable water quality. Invasive predation and direct competition are the obvious suspects. The true driver is a feedback loop where the invasive species outcompetes native fish for a shared prey base, causing slow starvation.",
    tempting="Focus on direct predation by the invasive species as the kill mechanism.",
    pivot_text="Shift from predation to prey base competition. The invasive species is not eating native fish — it is eating what native fish eat.",
    focus=["mechanism_reframing", "red_herring_suppression", "evidence_ordering"],
    n0="Native Thornlake char populations have dropped 60% over four years. An invasive cyprinid species was introduced three years ago. Direct predation and water quality change are the obvious explanations.",
    n1="Hypothesis A: The invasive cyprinid directly preys on juvenile native char, reducing recruitment into adult age classes.",
    n2="Hypothesis B: Industrial activity upstream has degraded water quality, reducing habitat suitability for the native species more than for the invasive one.",
    n3="Stomach content analysis of invasive cyprinids shows small fish fragments in 18% of samples, consistent with occasional predation on juvenile char.",
    n4="Enclosure experiments show juvenile char survival is not significantly lower when co-housed with invasive cyprinids at natural densities. Direct predation is not the primary mortality pathway.",
    n5="Water quality monitoring shows a 15% increase in suspended sediment near industrial outflows. This could reduce visibility and spawning habitat for char.",
    n6="Age-class analysis of char populations shows equal decline across juvenile and adult cohorts, inconsistent with recruitment failure from juvenile predation. Hypothesis A is ruled out.",
    n7="Sediment impact modelling shows the industrial input is far below the threshold for char spawning impairment. Water quality alone cannot explain the scale of decline. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the prey base. Zooplankton and macroinvertebrate surveys in areas of high and low invasive abundance need to be compared.",
    n9="Zooplankton density surveys show a 55% reduction in the primary prey items of native char in areas where invasive cyprinids are most abundant. The invasive species is a more efficient competitor for shared prey.",
    n10="Bioenergetics modelling shows native char are in negative energy balance in areas of high invasive density, with mass loss and reduced reproductive investment confirming slow starvation as the kill mechanism.",
    n11="Root cause: the invasive cyprinid out-competes native char for prey, not through predation but through superior foraging efficiency. The mechanism is competitive exclusion via prey depletion.",
    n12="Red herring: A recreational fishing club reports angling pressure increased significantly during the same period, suggesting overharvest as the cause of decline.",
    n13="Catch-per-unit-effort data and creel surveys show angling harvest is well within sustainable yield for the pre-invasive char population. Recreational fishing is not the primary driver.",
    n14="Stock assessment modelling confirms angling harvest accounts for less than 8% of the observed decline. Overharvest is excluded.",
),

# =============================================================================
# ECO-05 — lake_policy_investigation — tipping point: nutrient threshold
# =============================================================================
scenario(
    sid="vigil_exec_pellmere_threshold_flip_v2",
    skeleton="ECO-05", title="The Pellmere Threshold Flip",
    domain="lake_policy_investigation",
    summary="Pellmere Lake has flipped from clear water to persistent turbid algal state despite a 40% reduction in agricultural nutrient inputs over six years. Climate variation and recreational disturbance are suspects. The real mechanism is an internal nutrient loading loop triggered after the system crossed a hysteresis threshold.",
    tempting="Blame continued agricultural runoff because nutrient reduction has not been completed to the 60% target.",
    pivot_text="Abandon the external input framing. The lake has crossed a tipping point where internal sediment phosphorus release sustains the turbid state independently of external inputs.",
    focus=["tipping_point_recognition", "red_herring_suppression", "evidence_ordering"],
    n0="Pellmere Lake remains in a turbid, algae-dominated state six years after a major phosphorus reduction program. Agricultural inputs are down 40% but the target was 60%. Climate and recreational pressure are also cited.",
    n1="Hypothesis A: The nutrient reduction program has not achieved its 60% target — remaining agricultural inputs are sustaining the algal bloom.",
    n2="Hypothesis B: Increased recreational boat traffic is resuspending bottom sediments and releasing nutrients that maintain the bloom.",
    n3="Agricultural monitoring shows phosphorus runoff is still 20 percentage points short of the 60% reduction target. This supports Hypothesis A as an explanation for continued blooms.",
    n4="Modelling shows that even at 100% external load reduction, the lake remains in turbid state given current internal conditions. External inputs are insufficient to explain the persistence. Dead end.",
    n5="Sediment resuspension measurements show elevated turbidity on weekends with high boat traffic, consistent with recreational disturbance contributing to Hypothesis B.",
    n6="Mass balance modelling shows external phosphorus inputs have dropped below the threshold that originally triggered blooms. External loading alone cannot sustain the current algal biomass. Hypothesis A is ruled out.",
    n7="Controlled resuspension experiments show the turbidity effect of boating dissipates within 4 hours and contributes less than 3% of total phosphorus load. Recreational disturbance cannot sustain blooms. Hypothesis B is ruled out.",
    n8="Pivot: Investigate internal sediment phosphorus release. Once a lake crosses a eutrophication tipping point, internal loading can sustain the turbid state even after external inputs drop dramatically.",
    n9="Sediment core analysis shows that the upper 15cm layer — deposited during the high-nutrient decade — contains phosphorus concentrations 8× higher than historical baseline. This layer now releases phosphorus under anoxic conditions.",
    n10="Hypolimnion phosphorus flux measurements confirm that summer stratification creates anoxic conditions that release 3.2× more phosphorus from sediments than current annual external inputs. The lake is self-fuelling.",
    n11="Root cause: the lake crossed a hysteresis threshold and entered a self-sustaining internal loading cycle. Reducing external inputs to 60% was insufficient — active sediment treatment or whole-lake oxygenation is required.",
    n12="Red herring: A warmer-than-average summer three years ago is cited as an anomaly year that 'set back' the recovery. Some policy documents attribute the failure to climate variation.",
    n13="Long-term climate analysis shows the anomalous summer was within normal variability range and that turbid state persisted equally in cooler subsequent years. Climate variation does not explain the persistence.",
    n14="Comparison with eight similar lakes under equivalent climate exposure shows persistent turbidity is uniquely linked to legacy sediment load, not temperature anomaly. Climate is excluded.",
),

# =============================================================================
# ECO-06 — freshwater_species_investigation — feedback loop: oxygen stratification
# =============================================================================
scenario(
    sid="vigil_exec_varholm_oxygen_trap_v2",
    skeleton="ECO-06", title="The Varholm Oxygen Trap",
    domain="freshwater_species_investigation",
    summary="Coldwater fish are dying in Varholm Reservoir during summer months. Temperature stress and fishing are the obvious suspects. The mechanism is thermal stratification trapping coldwater species in an anoxic hypolimnion, caused by an upstream dam modification that deepened the thermocline.",
    tempting="Attribute mortality to direct thermal stress from summer warming — temperatures are slightly above historical averages.",
    pivot_text="Shift from surface temperature to the thermocline depth and hypolimnion oxygen profile. The thermal refuge has become an oxygen trap.",
    focus=["spatial_vertical_reframing", "red_herring_suppression", "pivot_latency"],
    n0="Coldwater salmonids in Varholm Reservoir are dying during July and August. Surface temperatures are marginally elevated above historical norms. An upstream dam modification was completed two years ago. Budget is limited.",
    n1="Hypothesis A: Direct thermal stress from above-average summer temperatures is pushing surface waters beyond the thermal tolerance of coldwater salmonids.",
    n2="Hypothesis B: Increased angling pressure during summer months is causing mortality through catch-and-release stress combined with elevated water temperatures.",
    n3="Surface temperature monitoring shows water temperatures in the 18–21°C range during mortality events — close to the upper thermal tolerance of salmonids. This is consistent with Hypothesis A.",
    n4="Controlled thermal tolerance experiments show the salmonid mortality threshold is 23°C. Observed surface temperatures of 18–21°C are below lethal level for the durations observed. Thermal stress alone cannot explain the deaths.",
    n5="Angling survey data shows a 25% increase in fishing effort in affected areas, and several anglers report catching exhausted fish during the mortality events.",
    n6="Fish distribution telemetry shows salmonids are not spending time in the warm surface layer — they are diving to the hypolimnion. Deaths occur in fish at depth, not in surface water. Hypothesis A is ruled out.",
    n7="Tagging data shows most dead fish had not been recently angled. Catch-and-release stress does not explain the spatial and temporal clustering of deaths. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the hypolimnion oxygen profile and thermocline depth. The salmonids are seeking thermal refuge at depth — but oxygen conditions at depth may have changed after the dam modification.",
    n9="Dissolved oxygen profiling shows hypolimnion oxygen dropping below 2mg/L in July — a lethal level for salmonids — in areas that previously maintained 5mg/L. The dam modification deepened the reservoir outlet depth, reducing hypolimnion water exchange.",
    n10="Hydrological modelling confirms the dam modification reduced turnover in the deep water layer by 60%. Salmonids seeking thermal refuge are now trapped in an oxygen-depleted zone.",
    n11="Root cause: dam modification deepened the thermocline and cut hypolimnion water exchange. Salmonids seeking thermal refuge at depth are now entering an anoxic trap. The mechanism is vertical habitat compression, not surface warming.",
    n12="Red herring: A regional drought year reduced reservoir inflow and is cited in public reports as the cause of thermal stress — less water means less buffering capacity.",
    n13="Inflow volume records show the drought year had 15% lower inflows than average, but equivalent mortality was not observed during previous drought years before the dam modification.",
    n14="Pre- and post-modification comparison confirms mortality began specifically after the dam outlet change, not during drought years alone. Drought is excluded as the primary driver.",
),

# =============================================================================
# ECO-07 — reef_outbreak_investigation — tipping point: thermal cascade
# =============================================================================
scenario(
    sid="vigil_exec_irridel_thermal_cascade_v2",
    skeleton="ECO-07", title="The Irridel Thermal Cascade",
    domain="reef_outbreak_investigation",
    summary="Irridel Reef shows a crown-of-thorns starfish outbreak that is consuming coral faster than bleaching events. The outbreak looks like a random population event. The true driver is a thermal-driven increase in larval survival tied to a decline in starfish predators caused by earlier bleaching mortality.",
    tempting="Treat the starfish outbreak as a primary natural event and focus on direct culling as the intervention.",
    pivot_text="Shift from outbreak management to predator recovery. The outbreak is a consequence of bleaching-driven predator loss, not a random population event.",
    focus=["second_order_cause_recognition", "red_herring_suppression", "evidence_ordering"],
    n0="Crown-of-thorns starfish are consuming coral across Irridel Reef at rates that exceed historical bleaching mortality. Direct thermal bleaching is also ongoing. Emergency intervention budget is limited.",
    n1="Hypothesis A: The starfish outbreak is a natural population cycle amplified by the current warm-water event increasing starfish metabolism and feeding rates.",
    n2="Hypothesis B: Nutrient runoff from coastal development has increased phytoplankton, boosting larval food availability and triggering the population explosion.",
    n3="Population density modelling shows starfish numbers are at 8× historical maximum, consistent with a thermal-amplified natural cycle event given current sea temperatures.",
    n4="Field experiments show starfish feeding rate increases only 12% at current temperature elevations — insufficient to account for the 8× population increase. Metabolism amplification cannot explain the outbreak scale.",
    n5="Coastal nutrient monitoring shows elevated chlorophyll-a inshore, consistent with development runoff providing extra larval food under Hypothesis B.",
    n6="Population models driven by temperature and feeding-rate data predict a 1.5× maximum outbreak under current thermal conditions — far below the observed 8× level. Hypothesis A is ruled out.",
    n7="Larval survival experiments show nutrient-driven phytoplankton increases improve survival by at most 20% under current conditions. Runoff alone cannot generate an 8× outbreak. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the predator community. Crown-of-thorns outbreaks are normally self-limiting through predation. If key predators were lost, the population suppression mechanism would have failed.",
    n9="Fish surveys show humphead wrasse and triggerfish — primary crown-of-thorns predators — are at 12% of their pre-bleaching baseline on Irridel Reef. These species were disproportionately affected by bleaching two years prior.",
    n10="Population dynamics modelling incorporating the predator decline shows that even moderate starfish reproductive success is sufficient to generate the observed 8× outbreak when predator pressure drops to 12% baseline.",
    n11="Root cause: bleaching two years prior devastated crown-of-thorns predator populations. The outbreak is a consequence of predator release, not thermal amplification or nutrient enrichment.",
    n12="Red herring: A cyclone track passed near the reef six months before outbreak intensification, leading to speculation that physical disturbance released starfish from sheltering habitat.",
    n13="Starfish density surveys immediately post-cyclone show no statistically elevated counts relative to pre-cyclone baseline. Cyclone disturbance does not explain the outbreak timing or scale.",
    n14="Recovery trajectory data shows starfish densities were already elevated 18 months before the cyclone — the outbreak predates the physical disturbance. Cyclone is excluded.",
),

# =============================================================================
# ECO-08 — reef_function_investigation — feedback loop: urchin-algae-coral
# =============================================================================
scenario(
    sid="vigil_exec_solspine_algae_lock_v2",
    skeleton="ECO-08", title="The Solspine Algae Lock",
    domain="reef_function_investigation",
    summary="Coral cover on Solspine Reef has dropped from 65% to 18% over eight years despite good water quality. Fishing and bleaching are the obvious suspects. The hidden mechanism is a sea urchin collapse triggered by disease that removed grazing control, allowing macroalgae to smother recovering corals.",
    tempting="Attribute the decline primarily to fishing pressure reducing herbivorous fish and allowing algae growth.",
    pivot_text="Shift from fish herbivory to sea urchin grazing. An urchin disease event removed the primary grazer, and fish herbivory was never sufficient alone to prevent algae lock-in.",
    focus=["grazer_substitution_insight", "pivot_latency", "red_herring_suppression"],
    n0="Coral cover on Solspine Reef is declining despite relatively clean water and moderate fishing pressure. Macroalgae dominates large reef sections. Multiple stressor analysis has not identified a clear cause.",
    n1="Hypothesis A: Overfishing of herbivorous fish (parrotfish, surgeonfish) has reduced grazing pressure enough to allow macroalgae to outcompete recovering corals.",
    n2="Hypothesis B: Periodic bleaching events every two to three years are preventing coral recovery faster than growth can occur.",
    n3="Fish survey data shows herbivorous fish biomass is at 60% of unfished reference levels — below optimal but not catastrophically reduced. This is consistent with Hypothesis A.",
    n4="Grazing capacity modelling shows observed fish herbivory is sufficient to prevent algae dominance under normal conditions. Fish depletion alone at current levels cannot explain the severity of algae lock-in.",
    n5="Bleaching records show three moderate thermal events in eight years. Each event killed 10–20% of remaining coral cover, consistent with Hypothesis B explaining cumulative decline.",
    n6="Before-after control-impact analysis shows algae dominance is equally severe in fully protected (no-take) reef sections with high fish biomass. Fish depletion cannot be the primary driver. Hypothesis A is ruled out.",
    n7="Recovery simulations show that corals recover from 15% mortality events in 3–5 years under historical conditions. Bleaching frequency alone cannot explain the scale of sustained algae lock-in. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the invertebrate grazer community. Sea urchins historically provided a backup grazing function that prevented algae lock-in even when fish grazing was moderate.",
    n9="Sea urchin density surveys reveal populations at 4% of historical baseline, coinciding with a reported disease event six years ago that was never formally documented. Urchin density is catastrophically low.",
    n10="Experimental algae removal and urchin addition plots show coral recruitment increases by 340% where urchin grazing is restored, confirming urchins were the critical grazer preventing algae lock-in.",
    n11="Root cause: sea urchin disease collapsed the invertebrate grazer baseline, removing the backup grazing that compensated for moderate fish depletion. Algae lock-in followed. The mechanism is grazer functional redundancy collapse.",
    n12="Red herring: A sewage outfall from a small coastal resort was upgraded poorly during the study period, and nutrient enrichment from this source is cited in community submissions as the cause.",
    n13="Water quality transects show nutrient levels at the resort outfall are within marine water quality standards and rapidly dilute to background within 200m. The outfall does not reach main reef sections.",
    n14="Nutrient limitation experiments show algae growth on affected reef sections is light-limited, not nutrient-limited — the reef is not responding to nutrient enrichment. The outfall is excluded.",
),

# =============================================================================
# ECO-09 — agricultural_ecology_investigation — feedback loop: pollinator collapse
# =============================================================================
scenario(
    sid="vigil_exec_fernfield_pollinator_gap_v2",
    skeleton="ECO-09", title="The Fernfield Pollinator Gap",
    domain="agricultural_ecology_investigation",
    summary="Fruit yields on Fernfield farms have dropped 55% despite stable growing conditions and no observed pest outbreaks. Pesticide resistance in pests and soil nutrient depletion are the visible suspects. The mechanism is sublethal neonicotinoid exposure that has impaired colony navigation in native bee pollinators.",
    tempting="Focus on pest management — resistant pest strains reducing fruit set more than visible damage suggests.",
    pivot_text="Abandon pest framing. Investigate the pollinator service. Sublethal pesticide effects on bee navigation are reducing visitation to flowers without killing bees visibly.",
    focus=["service_gap_recognition", "red_herring_suppression", "mechanism_reframing"],
    n0="Fruit yields across Fernfield agricultural zone have dropped 55% over three growing seasons. Visible pest damage is minimal. Soil and irrigation metrics are within normal range. Growers are applying the same pesticide regimes.",
    n1="Hypothesis A: Pest resistance has developed in the local population, reducing effective control and causing cryptic fruit loss through secondary damage not visible on mature fruit.",
    n2="Hypothesis B: Soil nutrient depletion — particularly micronutrients — is limiting fruit set even in the absence of visible crop stress.",
    n3="Pesticide efficacy testing shows reduced knockdown rates for the dominant leaf-roller pest compared to baseline five years ago, consistent with emerging resistance under Hypothesis A.",
    n4="Exclusion experiments with pesticide-treated vs. untreated plots show no significant difference in fruit set between the two conditions. Pest damage alone does not explain the yield gap.",
    n5="Tissue analysis of fruit trees shows boron and zinc at low-normal levels, consistent with Hypothesis B representing a marginal nutrient constraint.",
    n6="Fruit set monitoring shows equally poor yields in organically managed blocks with no pesticide pressure and negligible pest loads. Pest resistance cannot explain yield loss in pest-free blocks. Hypothesis A is ruled out.",
    n7="Micronutrient supplementation trials on boron- and zinc-deficient plots show no yield improvement in the next season. Nutrient supplementation does not restore yields. Hypothesis B is ruled out.",
    n8="Pivot: Investigate pollinator service directly. Pollinator visitation rates need to be monitored rather than inferred from yield models that assume adequate pollination.",
    n9="Pollinator transect monitoring shows native bee visitation rates have dropped 78% over three seasons. Visitation events per flower per day are far below the minimum required for full fruit set in this crop variety.",
    n10="Hive tracking experiments show native bees are departing colonies at normal rates but returning to incorrect locations or failing to return — consistent with navigation impairment. Colony collapse is absent but foraging efficiency has collapsed.",
    n11="Root cause: sublethal neonicotinoid exposure from systemic seed treatments has impaired native bee navigation and hive communication. Pollination service has collapsed silently without visible colony death.",
    n12="Red herring: An unusually dry spring three years ago is temporally correlated with the onset of yield decline, leading some agronomists to attribute the problem to drought-induced flower abort.",
    n13="Irrigation compensation was applied in the dry spring and flower counts show normal blossom density. Drought-induced flower abort cannot explain the yield decline pattern.",
    n14="Pollen viability testing confirms normal pollen production in the dry spring year. Flower and pollen quality are not limiting factors. Drought is excluded.",
),

# =============================================================================
# ECO-10 — agricultural_toxicology_investigation — tipping point: bioaccumulation
# =============================================================================
scenario(
    sid="vigil_exec_caldwell_apex_trap_v2",
    skeleton="ECO-10", title="The Caldwell Apex Trap",
    domain="agricultural_toxicology_investigation",
    summary="Apex predators in the Caldwell wetland system are experiencing reproductive failure. Habitat loss and direct persecution are the obvious suspects. The mechanism is organochlorine bioaccumulation from legacy agricultural drainage that reaches toxic concentrations only at the apex trophic level.",
    tempting="Focus on habitat reduction as the primary driver of reproductive failure.",
    pivot_text="Shift from habitat area to contaminant load. Apex predators are accumulating organochlorines beyond reproductive threshold despite habitat area being adequate.",
    focus=["trophic_accumulation_insight", "pivot_latency", "evidence_ordering"],
    n0="Marsh harrier and otter reproductive success in the Caldwell Wetland System has dropped to near zero. Wetland area has decreased 20% over ten years. Direct persecution by landowners is occasionally reported.",
    n1="Hypothesis A: Habitat reduction has lowered territory quality below viable breeding threshold for apex predators that require large contiguous wetland area.",
    n2="Hypothesis B: Direct persecution — illegal shooting and trapping — is the primary cause of reproductive failure and adult mortality in the affected populations.",
    n3="Territory mapping shows reduced contiguous wetland patches and increased edge-to-interior ratio, consistent with habitat quality decline under Hypothesis A.",
    n4="Minimum viable habitat modelling shows remaining wetland area is still above the known minimum territory size for both species at current densities. Habitat reduction alone cannot explain zero reproductive success.",
    n5="Wildlife crime reports and camera trap footage document at least four incidents of illegal persecution in the study area over the past two years, consistent with Hypothesis B.",
    n6="Radio-tagged adult survival rates are within historical normal range for both species — adult mortality is not elevated. Persecution cannot explain reproductive failure without elevated adult mortality. Hypothesis B is ruled out.",
    n7="Nest site availability surveys show abundant unoccupied habitat patches. Habitat constraint is not preventing nesting attempts — eggs and chicks fail, not nesting initiation. Hypothesis A is ruled out.",
    n8="Pivot: Investigate egg contaminant load and chick growth data. If reproductive failure is occurring during incubation and early chick rearing, toxicological causes need to be tested directly.",
    n9="Addled egg analysis from 14 failed clutches shows organochlorine concentrations — particularly DDE — at 6× the documented reproductive impairment threshold for both species. The contaminant load is directly causing shell thinning and embryo failure.",
    n10="Trophic bioaccumulation modelling shows organochlorine residues from legacy agricultural drains enter the wetland food web at low concentration in invertebrates but reach reproductive threshold only in apex predators consuming fish and amphibians daily.",
    n11="Root cause: legacy organochlorine drainage from historical agricultural use bioaccumulates through the food web to reproductive failure concentrations only at the apex trophic level. Habitat and persecution are secondary concerns.",
    n12="Red herring: A nearby road expansion project diverted surface water drainage through the wetland margin, leading to speculation that construction runoff is directly toxic to predator species.",
    n13="Construction runoff sampling shows no organochlorine compounds — the road project uses modern materials without legacy pesticide contamination. Road drainage is not the contaminant source.",
    n14="Contaminant source tracing using stable isotope ratios links the organochlorine signature in predator eggs to legacy agricultural field drains, not road infrastructure. Construction is excluded.",
),

# =============================================================================
# CLIN-01 — hospital_outbreak_investigation — antibiotic resistance
# =============================================================================
scenario(
    sid="vigil_exec_miralen_ward_resistance_v2",
    skeleton="CLIN-01", title="The Miralen Ward Resistance Chain",
    domain="hospital_outbreak_investigation",
    summary="A cluster of post-surgical infections on the Miralen Hospital surgical ward is not responding to standard antibiotics. Environmental contamination and new surgical staff are the obvious suspects. The true driver is a resistant strain that emerged under antibiotic selection pressure in one patient and spread via shared equipment.",
    tempting="Focus investigation on environmental contamination — surfaces and air handling — as the source of the outbreak.",
    pivot_text="Shift from environmental contamination to the index patient and shared equipment chain. The resistance emerged in a patient under prolonged antibiotic pressure, then transferred via inadequate equipment decontamination.",
    focus=["transmission_chain_identification", "red_herring_suppression", "pivot_latency"],
    n0="Seven post-surgical patients on the Miralen surgical ward have developed wound infections that are not responding to standard first-line antibiotics. Standard culture shows a gram-negative organism. Two patients are in critical condition.",
    n1="Hypothesis A: Environmental contamination — inadequate surface decontamination or HVAC faults — is the reservoir for the resistant organism spreading to post-surgical patients.",
    n2="Hypothesis B: A new surgical scrub nurse introduced three months ago is an asymptomatic carrier of the resistant strain.",
    n3="Environmental swabs from 40 surface sites show gram-negative organisms on 6 sites, superficially consistent with Hypothesis A as a source of ward contamination.",
    n4="HVAC airflow modelling and surface swab cultures show organisms are common environmental strains, not the resistant clinical isolate. Environmental contamination is not the outbreak source. Dead end.",
    n5="The new scrub nurse was present at three of the seven affected patient procedures, consistent with a possible carrier link under Hypothesis B.",
    n6="Whole-genome sequencing of environmental isolates shows they are genetically distinct from the clinical outbreak strain by >3000 SNPs. Environmental contamination is ruled out as the outbreak source.",
    n7="Carrier screening of the new scrub nurse returns negative for the outbreak strain. The nurse was also absent during four of the seven cases. Carrier transmission is ruled out.",
    n8="Pivot: Investigate shared equipment use and the treatment history of early cases. A patient who underwent prolonged antibiotic therapy before developing the resistant infection may be the index case.",
    n9="Retrospective case review shows Patient 1 received 18 days of broad-spectrum antibiotics for a separate infection before developing the resistant strain — sufficient selection pressure to generate de novo resistance.",
    n10="Equipment decontamination audit shows a bronchoscope used for Patient 1 was inadequately processed before reuse on Patients 3 and 5. Whole-genome sequencing confirms an identical strain across Patient 1, 3, and 5 cases.",
    n11="Root cause: de novo resistance emerged in an index patient under prolonged antibiotic pressure. Inadequate bronchoscope decontamination transferred the resistant strain to subsequent patients. Environmental contamination and carrier transmission are both secondary concerns.",
    n12="Red herring: Ward refurbishment six weeks before the outbreak is temporally correlated with the cluster start, leading infection control to suspect construction dust disrupting air handling.",
    n13="Construction activity records and HEPA filter monitoring show air filtration remained effective throughout refurbishment. Dust exposure and air handling deviation are not linked to the resistant strain.",
    n14="Post-refurbishment air sampling cultures show no evidence of the outbreak organism in the ventilation system. Construction is excluded as a contributing factor.",
),

# =============================================================================
# CLIN-02 — clinical_pharmacology_case — drug-interaction: CYP450 inhibition
# =============================================================================
scenario(
    sid="vigil_exec_calvecin_toxicity_trap_v2",
    skeleton="CLIN-02", title="The Calvecin Toxicity Trap",
    domain="clinical_pharmacology_case",
    summary="Patients on stable doses of Calvecin (a synthetic anticoagulant) are presenting with bleeding events without dose changes. Compliance failures and generic substitution are the obvious suspects. The true driver is CYP3A4 inhibition by a newly added antifungal causing Calvecin accumulation.",
    tempting="Focus on compliance failures and pharmacy dispensing errors as the source of elevated anticoagulant effect.",
    pivot_text="Abandon compliance framing. Investigate concurrent medication changes. A newly added antifungal is inhibiting Calvecin metabolism through CYP3A4, causing drug accumulation without dose change.",
    focus=["drug_interaction_identification", "pivot_latency", "red_herring_suppression"],
    n0="Twelve patients on stable Calvecin therapy have presented with bleeding complications over six weeks. None have had dose changes. Bleeding risk was previously well-controlled. The medication service is under review.",
    n1="Hypothesis A: Patient compliance failures — missed doses leading to 'catch-up' behaviour and irregular pharmacokinetics — are causing unpredictable anticoagulant levels.",
    n2="Hypothesis B: Generic substitution of Calvecin by the hospital pharmacy introduced a bioequivalence mismatch causing higher-than-expected drug absorption.",
    n3="Pill count compliance monitoring in four patients shows missed doses in two cases, consistent with irregular anticoagulant levels under Hypothesis A.",
    n4="Pharmacokinetic modelling of missed-dose catch-up patterns shows the resulting peak levels are insufficient to explain the severity of bleeding complications observed in most cases.",
    n5="Pharmacy records confirm generic Calvecin was substituted for brand-name three months ago, consistent with Hypothesis B as a source of bioequivalence variation.",
    n6="Therapeutic drug monitoring in 8 of the 12 patients shows Calvecin levels at 3–5× the target therapeutic range despite documented stable dosing. Compliance failure cannot explain uniform supratherapeutic levels across multiple patients.",
    n7="Bioequivalence testing of the generic formulation confirms it meets regulatory standards for AUC and Cmax within 90–111% of the reference product. Generic substitution is not causing the observed accumulation. Hypothesis B is ruled out.",
    n8="Pivot: Investigate concurrent medication changes. CYP3A4 is the primary metabolic pathway for Calvecin. Any CYP3A4 inhibitor added to the regimen would cause Calvecin accumulation without dose change.",
    n9="Medication reconciliation across all 12 cases shows that 11 of 12 patients had fluconazole (a potent CYP3A4 inhibitor) added to their regimen 4–6 weeks before the bleeding event — coinciding exactly with Calvecin level elevation.",
    n10="In vitro CYP3A4 activity assays confirm fluconazole at therapeutic concentrations reduces Calvecin clearance by 68%. Pharmacokinetic simulations using this inhibition constant accurately predict the observed 3–5× level elevation.",
    n11="Root cause: fluconazole co-prescription inhibited CYP3A4, reducing Calvecin clearance and causing accumulation to supratherapeutic levels. The interaction was not flagged by the hospital pharmacy alert system, which was not updated with the Calvecin-fluconazole interaction.",
    n12="Red herring: A new Calvecin lot number was distributed to the ward three months ago. Quality concerns about the manufacturing batch are raised as a possible cause.",
    n13="Lot release testing documentation confirms normal potency and dissolution for the new lot. Cases using the old and new lot number are equally affected.",
    n14="Pharmacovigilance review of all Calvecin lots over the past year shows no batch-specific signal for increased bleeding reports. Manufacturing quality is excluded.",
),

# =============================================================================
# CLIN-03 — clinical_trial_audit — diagnosis-error: protocol deviation
# =============================================================================
scenario(
    sid="vigil_exec_trialvex_selection_bias_v2",
    skeleton="CLIN-03", title="The Trialvex Selection Bias",
    domain="clinical_trial_audit",
    summary="A clinical trial for Trialvex shows significantly better efficacy than expected from Phase II data. Data fabrication and site performance differences are the obvious concerns. The real cause is a systematic protocol deviation at three sites that preferentially enrolled lower-severity patients, biasing the primary endpoint.",
    tempting="Focus the audit on data fabrication risk at the highest-performing sites.",
    pivot_text="Shift from fabrication to eligibility deviation. The high-performing sites enrolled patients who were systematically less severe at baseline, making the treatment appear more effective than it is.",
    focus=["bias_mechanism_identification", "red_herring_suppression", "evidence_ordering"],
    n0="The Phase III Trialvex trial shows 42% efficacy on the primary endpoint, significantly above the 28% observed in Phase II. Three sites account for 60% of the effect. A sponsor audit is underway with limited resources.",
    n1="Hypothesis A: Data fabrication at the three high-performing sites is artificially inflating the efficacy signal through falsified outcomes or endpoint assessments.",
    n2="Hypothesis B: Differential dropout rates at high-performing sites — possibly through coaching patients to stay in the trial — are biasing the per-protocol analysis.",
    n3="Site monitoring reports for the three high-performing sites show above-average query resolution times and several corrected source documents, consistent with Hypothesis A as a concern for data integrity.",
    n4="On-site source data verification at all three high-performing sites confirms all primary endpoint assessments are backed by original clinical records with no evidence of falsification.",
    n5="Dropout analysis shows slightly lower dropout rates at the three high-performing sites — 8% vs. 14% at other sites — which is marginally consistent with Hypothesis B.",
    n6="Independent endpoint adjudication by a masked panel shows equivalent endpoint scoring to site-reported values. Data fabrication cannot explain the efficacy difference if endpoints are consistently scored. Hypothesis A is ruled out.",
    n7="Sensitivity analyses using multiple imputation for missing data show negligible change in efficacy estimates when modelling dropout. Differential dropout cannot explain the 14-percentage-point efficacy difference. Hypothesis B is ruled out.",
    n8="Pivot: Investigate baseline severity at enrollment. Eligibility criteria allow discretionary judgment on one inclusion criterion. If high-performing sites systematically applied this criterion more liberally, they may have enrolled milder patients.",
    n9="Baseline APACHE score analysis across sites shows patients at the three high-performing sites have a mean APACHE score of 11.2, compared to 16.8 at other sites — a statistically significant severity difference within the protocol's eligibility range.",
    n10="Modelling Trialvex efficacy as a function of baseline severity shows the drug has substantially larger effect size in mild-moderate patients (APACHE <13) than severe patients — explaining why lower-severity sites show higher efficacy.",
    n11="Root cause: sites with more experienced investigators applied the discretionary eligibility criterion to enroll milder patients, creating severity-based selection bias. The efficacy signal is real but overstated for the target population. The drug works better in milder patients than the trial was designed to test.",
    n12="Red herring: A co-investigator at one high-performing site previously worked for the drug manufacturer, raising a conflict of interest concern as a potential motivation for data bias.",
    n13="Conflict of interest disclosure review shows the relationship predates the trial by seven years and falls within acceptable industry transition periods under institutional policy.",
    n14="Ethics committee review confirms the relationship was previously disclosed and does not constitute disqualifying conflict under trial protocol. Conflict of interest is excluded as a driver of the bias.",
),

# =============================================================================
# CLIN-04 — clinical_trial_site_variability — drug-interaction: population confound
# =============================================================================
scenario(
    sid="vigil_exec_seradol_responder_split_v2",
    skeleton="CLIN-04", title="The Seradol Responder Split",
    domain="clinical_trial_site_variability",
    summary="The Seradol pain trial shows paradoxical efficacy — responders cluster at sites in one geographic region. Placebo effect and site performance issues are the obvious suspects. The true driver is a pharmacogenomic interaction where Seradol is only effective in CYP2D6 poor metabolisers, who are over-represented in one region.",
    tempting="Attribute the regional responder cluster to placebo inflation from cultural factors at those sites.",
    pivot_text="Shift from placebo effects to pharmacogenomics. A metaboliser gene variant that determines drug response has different population frequency across geographic regions.",
    focus=["pharmacogenomic_mechanism", "red_herring_suppression", "evidence_ordering"],
    n0="Seradol achieves 38% pain reduction in responding sites vs. 7% in non-responding sites in the same Phase III trial. All sites used identical protocols. The responder sites cluster geographically. The discrepancy is unexplained.",
    n1="Hypothesis A: Placebo inflation at responder sites — driven by cultural or communication factors that increase expectation and subjective pain reporting changes.",
    n2="Hypothesis B: Site-level differences in physical therapy co-interventions are confounding the pain outcomes at responder sites.",
    n3="Patient expectation surveys at responder vs. non-responder sites show higher baseline expectation scores at responder sites, consistent with Hypothesis A.",
    n4="Placebo arm analysis at responder sites shows 6% pain reduction, not significantly higher than the 5% at non-responder sites. If expectation were inflating outcomes, the placebo arm should also show inflation.",
    n5="Physical therapy session logs show slightly more sessions at responder sites — 8.2 vs. 6.9 per patient — which is marginally consistent with Hypothesis B as a co-intervention confounder.",
    n6="Active arm vs. placebo arm comparison within responder sites shows a 32-percentage-point difference, which cannot be explained by expectation effects that equally affect both arms. Hypothesis A is ruled out.",
    n7="Covariate adjustment for physical therapy session count reduces the estimated efficacy difference by only 2 percentage points. Co-intervention differences are insufficient to explain the geographic split. Hypothesis B is ruled out.",
    n8="Pivot: Investigate pharmacogenomics. CYP2D6 metaboliser status determines Seradol pharmacokinetics. If poor metabolisers accumulate more drug and respond better, population-level metaboliser frequency differences could explain the geographic split.",
    n9="CYP2D6 genotyping of the first 200 samples from each site group shows CYP2D6 poor metaboliser frequency of 28% at responder sites vs. 7% at non-responder sites — a 4× difference driven by the regional genetic background.",
    n10="Pharmacokinetic modelling confirms poor metabolisers accumulate Seradol at 4.2× the plasma concentration of extensive metabolisers at the same dose. Among poor metabolisers, Seradol efficacy is 51% across all sites — consistent across geographies.",
    n11="Root cause: Seradol efficacy is pharmacogenomically restricted to CYP2D6 poor metabolisers. Geographic responder clustering is explained by regional differences in CYP2D6 poor metaboliser frequency. The drug works but for only 10–30% of the target population.",
    n12="Red herring: The responder sites all joined the trial later and used a revised version of the pain scale instrument, raising concern that assessment instrument changes explain the split.",
    n13="Measurement invariance testing across the two pain scale versions shows equivalent factor structures and equal item discrimination. The revised instrument does not introduce systematic response differences.",
    n14="Calibration study comparing both pain scale versions in a subsample confirms equivalent scoring for equivalent pain levels. Instrument change is excluded as the efficacy split driver.",
),

# =============================================================================
# CLIN-05 — hospital_microbiology_outbreak — secondary pathogen
# =============================================================================
scenario(
    sid="vigil_exec_varidex_secondary_outbreak_v2",
    skeleton="CLIN-05", title="The Varidex Secondary Outbreak",
    domain="hospital_microbiology_outbreak",
    summary="An ICU cluster of respiratory failures is initially attributed to Varidex influenza. Treatment is failing. The true driver is a secondary Pneumocystis jirovecii pneumonia emerging in immunocompromised patients once influenza treatment suppresses the microbiome defence.",
    tempting="Intensify influenza treatment and attribute treatment failure to antiviral resistance.",
    pivot_text="Shift from antiviral resistance to secondary opportunistic infection. Influenza treatment is working but exposing an underlying Pneumocystis infection that was masked by the influenza presentation.",
    focus=["secondary_pathogen_recognition", "pivot_latency", "evidence_ordering"],
    n0="Eight ICU patients with influenza diagnoses are deteriorating despite antiviral treatment. Respiratory failure is worsening. Antiviral resistance and inadequate dosing are under discussion.",
    n1="Hypothesis A: Varidex influenza antiviral resistance has developed, rendering standard treatment ineffective and allowing progressive viral pneumonia.",
    n2="Hypothesis B: Inadequate antiviral dosing in patients with altered drug clearance (renal impairment, obesity) is resulting in subtherapeutic drug levels.",
    n3="Influenza PCR viral load measurements show persistent high titres in four of the eight patients despite five days of antiviral treatment, consistent with Hypothesis A.",
    n4="Antiviral resistance genotyping of influenza isolates from all eight patients shows no known resistance mutations in neuraminidase or polymerase genes. Antiviral resistance cannot explain treatment failure.",
    n5="Therapeutic drug monitoring in the four obese patients shows antiviral levels at 65–80% of target — below therapeutic range — consistent with Hypothesis B.",
    n6="Antiviral resistance sequencing returns wild-type virus in all cases. If resistance were the driver, at least some resistance mutations should be present given the clinical picture. Hypothesis A is ruled out.",
    n7="Dose optimisation in the four patients with subtherapeutic levels does not improve clinical trajectory. Adequate dosing restores drug levels but does not resolve deterioration. Hypothesis B is ruled out.",
    n8="Pivot: Investigate secondary opportunistic infections. Patients who are immunocompromised (corticosteroids, malignancy, transplant) and now under influenza-driven immune stress may have developed a co-infection that was missed on admission.",
    n9="Bronchoalveolar lavage with silver stain and Pneumocystis PCR in six patients returns positive for Pneumocystis jirovecii pneumonia in five. Retrospective review shows all five were on chronic corticosteroids — a major PCP risk factor.",
    n10="CT imaging re-read with PCP in mind shows the bilateral ground-glass opacity pattern is classic for PCP, not viral influenza pneumonia. The influenza was real but PCP is the dominant driver of respiratory failure.",
    n11="Root cause: Pneumocystis jirovecii co-infection was present at ICU admission but masked by the influenza presentation. Immunocompromised status was not triggering PCP prophylaxis in the context of an acute influenza diagnosis.",
    n12="Red herring: A new hospital ventilator circuit was installed on the ICU two weeks before the cluster, and biofilm contamination of ventilator circuits is raised as a possible outbreak source.",
    n13="Ventilator circuit cultures show no Pneumocystis organisms — this pathogen cannot survive in environmental biofilm and is not transmitted via ventilator circuits.",
    n14="Infection control review confirms all ventilator circuits passed sterility testing post-installation. Circuit contamination is definitively excluded as a PCP source.",
),

# =============================================================================
# CLIN-06 — icu_patient_safety_case — drug cascade
# =============================================================================
scenario(
    sid="vigil_exec_cardivo_cascade_failure_v2",
    skeleton="CLIN-06", title="The Cardivo Cascade Failure",
    domain="icu_patient_safety_case",
    summary="ICU patients on Cardivo (a cardiac glycoside) are experiencing unexplained arrhythmias despite therapeutic drug levels. Equipment malfunction and nursing error are the obvious suspects. The true driver is hypomagnesaemia from concurrent diuretic therapy sensitising the myocardium to Cardivo toxicity at previously safe levels.",
    tempting="Focus on Cardivo dosing accuracy and IV preparation errors as the source of arrhythmias.",
    pivot_text="Shift from drug levels to electrolyte co-factors. Magnesium depletion from diuretic therapy is sensitising the myocardium to Cardivo toxicity at previously tolerated levels.",
    focus=["electrolyte_cofactor_mechanism", "pivot_latency", "red_herring_suppression"],
    n0="Six ICU patients on Cardivo cardiac glycoside therapy are developing arrhythmias despite Cardivo levels within the therapeutic range. Cardivo has been used without problems for weeks. Equipment and dosing accuracy are being reviewed.",
    n1="Hypothesis A: IV pump malfunction or programming errors are delivering higher-than-intended Cardivo doses despite the pump displaying correct rates.",
    n2="Hypothesis B: Nursing shift handover failures are resulting in inadvertent double-dosing of Cardivo during changeover periods.",
    n3="IV pump audit logs show no pump faults or override events in the relevant windows. The pump records are consistent with Hypothesis A being a technical error at the device level.",
    n4="Direct comparison of programmed dose rates with actual infused volumes (using gravimetric measurement) shows no systematic over-delivery. Pump accuracy is within specification. Dead end.",
    n5="Medication administration records show two instances where Cardivo timing annotations overlap in the transition period, consistent with possible handover double-dosing under Hypothesis B.",
    n6="Continuous Cardivo level monitoring throughout the arrhythmia events shows levels remain within the therapeutic range during the arrhythmias themselves. Elevated drug levels are not present during events. Hypothesis A is ruled out.",
    n7="Detailed reconciliation of Cardivo administration records shows the two annotation overlaps are documentation artefacts from electronic record migration — actual doses were not doubled. Hypothesis B is ruled out.",
    n8="Pivot: Investigate electrolyte status. Cardivo toxicity can occur at therapeutic levels when electrolyte co-factors — particularly potassium and magnesium — are abnormal. Both are depleted by diuretics.",
    n9="Electrolyte panel review of all six patients shows serum magnesium below 0.6 mmol/L (hypomagnesaemia) in five of six cases. All five are on loop diuretics for fluid management. Potassium is also borderline low in three cases.",
    n10="Experimental magnesium supplementation in three patients normalises electrolyte status and completely resolves arrhythmia burden within 12 hours, confirming the electrolyte sensitisation mechanism.",
    n11="Root cause: loop diuretic therapy depleted magnesium, sensitising the myocardium to Cardivo toxicity at previously well-tolerated levels. Cardivo dosing is correct — the toxicity threshold has shifted due to electrolyte cofactor depletion.",
    n12="Red herring: A new Cardivo formulation from an alternative supplier was introduced at the ICU two weeks before the arrhythmia cluster began.",
    n13="Bioequivalence testing documentation for the new formulation confirms equivalent pharmacokinetic profile to the original supplier. Both formulations produce equivalent Cardivo levels at equivalent doses.",
    n14="Cardivo level monitoring confirms no systematic pharmacokinetic difference between patients who received old vs. new formulation. Supplier change is excluded.",
),

# =============================================================================
# CLIN-07 — outbreak_epidemiology_case — reservoir misidentification
# =============================================================================
scenario(
    sid="vigil_exec_thornex_reservoir_error_v2",
    skeleton="CLIN-07", title="The Thornex Reservoir Error",
    domain="outbreak_epidemiology_case",
    summary="A Thornex food poisoning cluster is attributed to contaminated produce from a central distributor. Control measures targeting the distributor fail to stop new cases. The true reservoir is a restaurant worker who is an asymptomatic carrier and a secondary distributor of prepared food that was never tested.",
    tempting="Intensify produce supply chain tracing and distributor testing to find the contaminated batch.",
    pivot_text="Abandon the produce supply chain. The distributor is a dead end — a worker at a catering supplier who handles post-preparation food is the true transmission source.",
    focus=["transmission_route_pivot", "red_herring_suppression", "evidence_ordering"],
    n0="Forty cases of Thornex gastroenteritis have been confirmed across five venues over three weeks. Epidemiology links all venues to a common produce distributor. The distributor has been put on hold. New cases continue.",
    n1="Hypothesis A: The contaminated produce batch has not been fully recalled — some stock from the distributor remains in venue cold storage and is still causing cases.",
    n2="Hypothesis B: Secondary person-to-person transmission from the initial cluster is generating new cases independent of the original food source.",
    n3="Recall verification at three venues shows produce lots consistent with the suspect batch still in storage at one venue, consistent with Hypothesis A.",
    n4="Full environmental swabbing and product testing at the distributor and all five venues returns negative for Thornex organism across all produce samples. No contaminated produce is found.",
    n5="Social network analysis of confirmed cases shows five cases had direct household contact with earlier cases, consistent with Hypothesis B.",
    n6="Whole-genome sequencing of isolates shows all 40 cases share an identical strain — consistent with a single persistent source, not gradual person-to-person drift that would introduce sequence variation. Hypothesis B cannot fully explain the cluster.",
    n7="Household contact analysis shows 35 of 40 cases have no direct household contact with prior cases. Secondary transmission cannot explain the majority of new cases without a common exposure. Hypothesis B is ruled out as the primary driver.",
    n8="Pivot: Investigate the catering preparation chain rather than the produce supply chain. If a food handler at a catering supplier serving all five venues is an asymptomatic carrier, they could be inoculating prepared food post-cooking.",
    n9="Stool PCR screening of workers at all catering suppliers serving the five venues identifies one asymptomatic positive — a sauce preparation worker at a central catering kitchen that supplies all five venues with condiments and garnishes.",
    n10="Whole-genome sequencing of the worker's carrier strain shows identity to the outbreak strain. The worker handles food post-preparation without heat treatment, providing the transmission route. The produce supply chain was never contaminated.",
    n11="Root cause: an asymptomatic food handler at a central catering kitchen is contaminating post-preparation condiments and garnishes. The produce supply chain is a coincidental link — all venues share the caterer, not the produce distributor.",
    n12="Red herring: A venue manager reports that ice supply from a single ice manufacturer was shared across all five venues, raising concern about contaminated ice as the common vehicle.",
    n13="Ice manufacturer testing shows no Thornex organism in any batch produced during the outbreak period. Ice temperature monitoring confirms no thaw-refreeze cycles that could enable contamination.",
    n14="Genomic comparison of isolates from the ice facility (environmental swabs) shows no match to the outbreak strain. Ice supply is excluded as the transmission vehicle.",
),

# =============================================================================
# CLIN-08 — diagnostic_bias_case — anchoring error
# =============================================================================
scenario(
    sid="vigil_exec_dexoral_anchoring_failure_v2",
    skeleton="CLIN-08", title="The Dexoral Anchoring Failure",
    domain="diagnostic_bias_case",
    summary="Patients referred for suspected Dexoral syndrome are receiving empirical treatment that is not working. The diagnostic workup is consistently missing an alternative diagnosis. The mechanism is anchoring bias — referring physicians anchor on Dexoral syndrome because it is a recently publicised condition, and workup is confirmatory rather than differential.",
    tempting="Attribute treatment failure to heterogeneous disease presentation — some Dexoral syndrome cases are simply treatment-resistant.",
    pivot_text="Abandon the treatment-resistance framing. The diagnosis itself is wrong in a significant proportion of cases. Anchoring bias is driving confirmatory workup that misses an alternative condition with similar presentation.",
    focus=["diagnostic_bias_recognition", "pivot_latency", "red_herring_suppression"],
    n0="Eighteen patients referred as Dexoral syndrome are not responding to standard Dexoral syndrome treatment. Workup protocols were followed. The condition was recently publicised in a major journal. Budget is limited for re-evaluation.",
    n1="Hypothesis A: Dexoral syndrome has high phenotypic heterogeneity — some subtypes are inherently treatment-resistant and require escalated therapy.",
    n2="Hypothesis B: Diagnostic criteria application varies across referring centres, resulting in inclusion of cases that technically do not meet full criteria.",
    n3="Literature review identifies three published cases of treatment-refractory Dexoral syndrome, consistent with Hypothesis A that some cases are inherently resistant.",
    n4="Escalated therapy trial in four non-responding patients according to the refractory Dexoral protocol shows no improvement after 8 weeks. If the condition were present but treatment-resistant, some response should be detectable.",
    n5="Criteria audit of referral documentation shows that 6 of 18 patients lacked one minor criterion at referral — consistent with Hypothesis B as a partial explanation.",
    n6="Independent expert review of the 4 most treatment-refractory cases diagnoses 3 with an alternative condition (Vasalvex syndrome) — a recently described entity with overlapping presentation but different pathophysiology. Hypothesis A is ruled out as the primary driver.",
    n7="Criteria compliance re-analysis shows that even the 12 patients who fully met Dexoral criteria include 7 who were not investigated for Vasalvex syndrome, which has overlapping criteria. Criteria quality is a necessary but insufficient explanation. Hypothesis B is ruled out as sufficient.",
    n8="Pivot: Investigate for Vasalvex syndrome in the full non-responding cohort. Anchoring on a recently publicised diagnosis may be causing confirmatory workup that actively excludes consideration of Vasalvex.",
    n9="Vasalvex-specific biomarker testing (a panel not included in standard Dexoral workup) in all 18 non-responding patients shows positive results in 11. Nine of these 11 had previously undergone Dexoral-focused workup that explicitly excluded Vasalvex testing.",
    n10="Structured interview of referring physicians reveals that Dexoral syndrome was the leading hypothesis in all 18 cases before any workup was completed. Tests were ordered to confirm, not to discriminate. The workup sequence was confirmatory by design.",
    n11="Root cause: anchoring bias on a recently publicised diagnosis led to confirmatory diagnostic workup that systematically excluded consideration of Vasalvex syndrome. The treatment is failing because a significant subset have a different condition.",
    n12="Red herring: A new Dexoral syndrome diagnostic kit launched commercially six months ago is suspected of having high false-positive rate that is inflating referrals.",
    n13="Kit validation data shows 94% specificity in correctly diagnosed populations. False-positive rate at the kit level cannot account for the 61% Vasalvex misclassification rate found in this cohort.",
    n14="Head-to-head comparison with the previous diagnostic approach shows equivalent sensitivity and specificity in a validation cohort. Kit performance is excluded as the driver of misclassification.",
),

# =============================================================================
# CLIN-09 — public_health_surveillance_case — reporting lag
# =============================================================================
scenario(
    sid="vigil_exec_survalyx_lag_mirage_v2",
    skeleton="CLIN-09", title="The Survalyx Lag Mirage",
    domain="public_health_surveillance_case",
    summary="Survalyx vaccine appears to be losing efficacy in routine surveillance — case rates among vaccinated individuals are rising relative to unvaccinated. Waning immunity and new variant emergence are the obvious suspects. The true driver is a differential reporting lag that makes vaccinated cases appear more common due to healthcare-seeking behaviour differences.",
    tempting="Attribute the efficacy signal to waning immunity requiring booster doses.",
    pivot_text="Shift from immunological waning to epidemiological methodology. The apparent efficacy loss is a surveillance artefact caused by differential reporting delays between vaccinated and unvaccinated populations.",
    focus=["surveillance_bias_identification", "pivot_latency", "evidence_ordering"],
    n0="Survalyx vaccine effectiveness in routine surveillance has dropped from 87% to 61% over six months. No new variants have been confirmed. The immunisation programme is under review for booster scheduling.",
    n1="Hypothesis A: Waning antibody titres in individuals vaccinated 6–9 months ago are allowing breakthrough infections at higher rates.",
    n2="Hypothesis B: A new Survalyx-resistant variant is circulating that has not yet been detected by genomic surveillance.",
    n3="Antibody titre surveys in vaccinated cohorts show a mean 40% decline in neutralising titres between 3 months and 9 months post-vaccination, consistent with Hypothesis A.",
    n4="Randomised booster trial showing restoration of antibody titres does not significantly change the observed case rate ratio in surveillance data, suggesting titre decline alone is not driving the efficacy loss.",
    n5="Sequence analysis of 120 recent isolates shows one isolate with two receptor-binding domain mutations, potentially consistent with Hypothesis B.",
    n6="Antibody titre-efficacy correlation analysis shows no significant association between titres and breakthrough risk in the current cohort — cases are occurring equally across titre levels. Titre waning cannot explain the efficacy signal. Hypothesis A is ruled out.",
    n7="Neutralisation assays against the isolate with RBD mutations show only 18% reduction in antibody efficacy — insufficient to explain a 26-percentage-point efficacy drop. The variant cannot account for the surveillance signal. Hypothesis B is ruled out.",
    n8="Pivot: Investigate reporting infrastructure and case ascertainment. If vaccinated individuals seek testing faster and report through different channels, their cases may be captured with shorter delays and appear more numerous in cross-sectional surveillance.",
    n9="Reporting delay analysis shows vaccinated individuals seek testing a median of 1.8 days after symptom onset vs. 4.3 days for unvaccinated individuals. In a fast-moving epidemic, shorter delay creates apparent temporal clustering that inflates the vaccinated case count relative to unvaccinated in any given week.",
    n10="Simulation modelling using actual delay distributions shows that differential healthcare-seeking alone can reduce apparent vaccine effectiveness from 87% to 58–65% — matching the observed 61% signal without any true immunological change.",
    n11="Root cause: vaccinated individuals seek testing and report cases faster, creating a surveillance ascertainment bias that makes vaccine efficacy appear to decline when it has not meaningfully changed. The immunisation programme does not need accelerated boosters.",
    n12="Red herring: Survalyx cold chain monitoring has flagged two shipment deviations — brief temperature excursions during distribution — that could have reduced vaccine potency in those batches.",
    n13="Potency testing of returned vials from flagged shipments shows all samples within specification. Temperature excursions were brief and did not degrade the vaccine.",
    n14="Lot-specific effectiveness analysis shows no efficacy difference between lots from flagged vs. unflagged shipments. Cold chain deviation is excluded as a potency concern.",
),

# =============================================================================
# CLIN-10 — environmental_health_outbreak — exposure route misidentification
# =============================================================================
scenario(
    sid="vigil_exec_nephrovex_route_error_v2",
    skeleton="CLIN-10", title="The Nephrovex Route Error",
    domain="environmental_health_outbreak",
    summary="A cluster of chronic kidney disease in a rural district is attributed to Nephrovex agricultural pesticide runoff contaminating drinking water. Water treatment is improved but new cases continue. The true exposure route is dermal absorption during hand-application of pesticide without protective equipment, not water ingestion.",
    tempting="Focus investigation on water treatment failure — assuming the water contamination pathway is correct but imperfectly controlled.",
    pivot_text="Abandon water ingestion as the primary route. Investigate occupational dermal exposure. Farmers applying Nephrovex without gloves are absorbing a dose orders of magnitude higher than what drinking water contributes.",
    focus=["exposure_route_pivot", "red_herring_suppression", "evidence_ordering"],
    n0="Twenty-two chronic kidney disease cases have been identified in Westerfield District, significantly above regional background. Nephrovex pesticide is used by most affected households. Drinking water testing shows trace Nephrovex. A water treatment upgrade was installed two months ago.",
    n1="Hypothesis A: Nephrovex contamination of drinking water is causing cumulative kidney damage through daily low-level ingestion exposure.",
    n2="Hypothesis B: Nephrovex accumulates in produce grown in contaminated soil, and dietary ingestion of contaminated food is the primary exposure route.",
    n3="Drinking water testing shows Nephrovex at 0.04 mg/L — above the guideline of 0.01 mg/L but below acute toxicity threshold. This is consistent with Hypothesis A as a cumulative ingestion pathway.",
    n4="Pharmacokinetic modelling of ingestion at observed water concentrations shows lifetime cumulative kidney dose is 30-fold below the dose associated with nephrotoxicity in animal models. Water ingestion alone is far below the toxic threshold.",
    n5="Produce testing from household gardens shows Nephrovex at 0.3–1.2 mg/kg in root vegetables — a detectable level consistent with Hypothesis B.",
    n6="Post-water treatment upgrade monitoring shows Nephrovex in treated water is now below detection limit. New cases continue to occur at the same rate despite the water treatment improvement. Hypothesis A is ruled out.",
    n7="Dietary exposure modelling at observed produce concentrations shows a dietary dose similar to the water ingestion pathway — also far below the animal model nephrotoxicity threshold. Dietary exposure alone cannot explain kidney damage at observed concentrations. Hypothesis B is ruled out.",
    n8="Pivot: Investigate occupational exposure. Farmers who mix and apply Nephrovex manually are exposed dermally. Hand-application without gloves represents a qualitatively different exposure route with much higher dose.",
    n9="Urinary Nephrovex metabolite measurements in affected farmers show levels 40–120× higher than in age-matched controls who live in the same area but do not handle pesticides. The exposure source is occupational, not environmental.",
    n10="Dermal absorption modelling for hand-application without personal protective equipment shows daily Nephrovex dermal dose is 850–3200× higher than the ingestion dose from contaminated water — well above the nephrotoxic threshold with chronic daily exposure.",
    n11="Root cause: dermal absorption during unprotected pesticide application is the primary exposure route causing kidney damage. Water and produce contamination are real but contribute doses far below the toxic threshold. Protective equipment provision is the key intervention.",
    n12="Red herring: A legacy tanning facility operated in the district until 15 years ago, and heavy metal contamination from tannery effluent is raised as a possible nephrotoxin source.",
    n13="Soil and groundwater heavy metal surveys show lead and chromium within regional background levels. Tannery legacy contamination is below measurable kidney toxicity threshold.",
    n14="Case-control analysis shows no association between residential proximity to the former tannery and kidney disease risk. Heavy metal exposure is excluded as the driver.",
),

# =============================================================================
# ENG-01 — cloud_outage_investigation — failure cascade: config propagation
# =============================================================================
scenario(
    sid="vigil_exec_nexalox_config_cascade_v2",
    skeleton="ENG-01", title="The Nexalox Config Cascade",
    domain="cloud_outage_investigation",
    summary="Nexalox cloud platform experienced a 4-hour regional outage affecting 340,000 customers. A deployment rollout and a network change are the obvious candidates. The true cause is a configuration change that propagated through a shared config service and disabled health checks on the load balancer tier before the deployment even ran.",
    tempting="Focus the post-incident review on the deployment pipeline — the outage correlates with a new service rollout.",
    pivot_text="Shift from the deployment itself to the shared config service. A config change that preceded the deployment disabled health checks and was not caught by deployment gating.",
    focus=["config_vs_deploy_distinction", "red_herring_suppression", "root_cause_ordering"],
    n0="Nexalox Platform suffered a 4-hour regional outage at 14:32 UTC. A new microservice deployment was in progress. 340,000 customers were affected. The incident team has limited investigation budget before the board briefing.",
    n1="Hypothesis A: The microservice deployment introduced a dependency version incompatibility that caused cascading failures in the load balancer tier.",
    n2="Hypothesis B: A network routing change applied by the infrastructure team two hours before the outage disrupted inter-zone traffic and caused the regional failure.",
    n3="Deployment logs show the new microservice version introduced a gRPC library upgrade, which has historically caused compatibility issues with the existing load balancer health check endpoint.",
    n4="Rollback of the deployment to the previous microservice version at 14:55 UTC does not restore service. The outage continues for 2.5 hours after complete rollback, proving the deployment is not the root cause.",
    n5="Network routing change logs show a BGP policy update was applied at 12:18 UTC — two hours before the outage — which could have degraded inter-zone latency.",
    n6="Pre-deployment smoke test results show all health check endpoints responding correctly in the test environment with the new gRPC version. The library upgrade passed compatibility gates. Hypothesis A is ruled out.",
    n7="BGP routing analysis shows the policy update affected only external peering and did not change internal inter-zone routing. Latency metrics between zones remained normal until 14:29 UTC. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the shared configuration service. A config change was applied to a global config store at 14:21 UTC — 11 minutes before the outage. Config changes propagate to all services including the load balancer health check module.",
    n9="Config change audit at 14:21 UTC shows a TTL parameter for health check probe intervals was changed from 5s to 300s — effectively disabling real-time health detection. This change propagated to all zones within 8 minutes.",
    n10="Health check probe interval analysis confirms that with 300s TTL, a failed health check on a service would not trigger load balancer failover for up to 5 minutes — enough to allow traffic to pile up on a degraded zone until connection queues exhausted available threads.",
    n11="Root cause: a config change to the shared health check TTL parameter disabled effective health monitoring before the deployment began. The deployment is coincidental. The config change was not subject to deployment gating review.",
    n12="Red herring: A memory spike was observed on 3 of 12 load balancer nodes starting at 14:28 UTC, leading initial responders to suspect a memory leak as the trigger.",
    n13="Memory spike root cause analysis shows the spike is a consequence of connection queue growth, not a cause. The nodes were accumulating connections because failed health checks were not routing traffic away. Memory growth followed the routing failure.",
    n14="Baseline memory profiling of load balancer nodes confirms normal allocation patterns prior to the outage. No memory leak regression is present in the codebase. Memory spike is excluded as an initiating cause.",
),

# =============================================================================
# ENG-02 — infra_foundational_layer_outage — threshold exceeded: shared dependency
# =============================================================================
scenario(
    sid="vigil_exec_coreplat_shared_failure_v2",
    skeleton="ENG-02", title="The Coreplat Shared Failure",
    domain="infra_foundational_layer_outage",
    summary="Coreplat infrastructure experienced simultaneous failure across 12 independent services. Each service team believes their service failed independently. The true cause is a shared foundational library that crossed an internal thread pool limit under combined load, causing cascading thread exhaustion across all services simultaneously.",
    tempting="Investigate each service independently — the simultaneous failure looks like a coordinated attack or external factor.",
    pivot_text="Shift from per-service investigation to shared dependency analysis. All services share a foundational networking library with a global thread pool. Combined load crossed the thread limit simultaneously.",
    focus=["shared_dependency_recognition", "red_herring_suppression", "evidence_ordering"],
    n0="At 09:14 UTC, 12 production services failed simultaneously. Each service team is investigating independently. No deployment was in progress. A coordinated external attack has not been confirmed. Investigation budget is limited.",
    n1="Hypothesis A: A coordinated DDoS attack targeting all 12 services simultaneously caused request queue overflow across the platform.",
    n2="Hypothesis B: A shared infrastructure component — database or message broker — failed and all 12 services are downstream dependents.",
    n3="Network traffic analysis shows a 340% spike in inbound requests across all 12 services starting at 09:12 UTC — 2 minutes before the failure — consistent with Hypothesis A.",
    n4="Traffic source analysis shows the request spike originates from internal services (scheduled batch jobs that all fired simultaneously at 09:12 UTC on a monthly schedule), not external attackers. The traffic is legitimate internal load.",
    n5="Shared infrastructure dependency map shows all 12 services connect to a shared PostgreSQL cluster and a shared Redis cache, consistent with Hypothesis B.",
    n6="DDoS attack indicators — spoofed IPs, SYN flood patterns, geographic clustering — are absent. The traffic pattern matches legitimate authenticated internal requests. Hypothesis A is ruled out.",
    n7="PostgreSQL and Redis health metrics show both components remained healthy throughout the failure window. Response times from both are normal. Shared infrastructure database is not the failure point. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the foundational networking library used by all 12 services. All 12 services share version 4.2.1 of NetLib — a transport library with an internal thread pool. Thread pool exhaustion would cause simultaneous request rejection across all consumers.",
    n9="Thread pool monitoring for NetLib 4.2.1 shows the global thread pool hit its maximum of 512 threads at exactly 09:14 UTC as combined internal batch job traffic hit the peak. Thread exhaustion causes NetLib to reject all new connection requests with a timeout error.",
    n10="NetLib source code review shows version 4.2.1 changed the thread pool from per-service to global across all instances in the same process group. The change was not documented in release notes and was not caught in load testing because tests ran services individually.",
    n11="Root cause: NetLib 4.2.1 introduced an undocumented global thread pool shared across all services in the same process group. Combined monthly batch load crossed the pool limit simultaneously, causing platform-wide connection rejection.",
    n12="Red herring: A certificate renewal for the TLS termination layer was scheduled for 09:00 UTC the same morning, and a brief TLS renegotiation event is visible in the logs.",
    n13="TLS renegotiation analysis shows all certificates renewed successfully within 30 seconds with no service interruption. No TLS errors appear in any service log until after the NetLib thread exhaustion at 09:14.",
    n14="Certificate validity and TLS handshake metrics confirm normal operation until 09:14 UTC. Certificate renewal is excluded as a contributing factor.",
),

# =============================================================================
# ENG-03 — saas_supply_chain_security_case — failure cascade: third-party compromise
# =============================================================================
scenario(
    sid="vigil_exec_supplylink_injection_v2",
    skeleton="ENG-03", title="The Supplylink Injection",
    domain="saas_supply_chain_security_case",
    summary="Customer data has been exfiltrated from the Supplylink SaaS platform. An insider threat and a direct API vulnerability are the obvious suspects. The true source is a compromised open-source logging library injected with a backdoor in a minor version update that was pulled into production via automated dependency updates.",
    tempting="Focus the investigation on insider threat — an employee with broad data access left the company recently.",
    pivot_text="Shift from insider threat to dependency chain. The exfiltration is automated and continuous — the signature of a backdoored dependency, not a human actor doing manual extraction.",
    focus=["supply_chain_vs_insider_distinction", "red_herring_suppression", "evidence_ordering"],
    n0="Anomalous data exfiltration was detected from the Supplylink production environment. An estimated 2.3TB of customer records were transmitted to external endpoints over 11 days. A recently departed employee is under suspicion.",
    n1="Hypothesis A: The recently departed employee retained credentials or planted a backdoor before departure and has been exfiltrating data since leaving.",
    n2="Hypothesis B: An unpatched API vulnerability is being actively exploited by an external attacker performing authenticated data extraction.",
    n3="Access log review shows the departed employee's credentials were used to authenticate once after their departure date, consistent with Hypothesis A.",
    n4="The single post-departure authentication event was a session token replay from a cached mobile device — the token was revoked 6 hours later with no associated data access. The departed employee's credentials are not the exfiltration source.",
    n5="API access pattern analysis shows 40,000 API calls per day exceeding normal business hours — consistent with Hypothesis B if an attacker is running automated extraction.",
    n6="Departed employee access scope mapping shows they had read access to only 180,000 records. The exfiltrated dataset contains 4.7 million records. Scope mismatch rules out insider access as the primary vector. Hypothesis A is ruled out.",
    n7="API vulnerability scan and penetration test show no exploitable unauthenticated endpoints. All 40,000 API calls per day are from authenticated service accounts with legitimate credentials — not an external attacker. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the service accounts making the API calls. If a backdoored dependency is running in the application context, it would use the application's own service account credentials and appear as legitimate authenticated traffic.",
    n9="Dependency audit of the production deployment shows LogKit version 2.3.1 was pulled via automated dependency updates 12 days ago — one day before exfiltration began. LogKit 2.3.1 was found to contain a malicious commit in a third-party contribution that was merged without adequate review.",
    n10="Static analysis of LogKit 2.3.1 confirms a hidden HTTP client initialised at library load time that serialises log events containing request payloads and sends them to an external endpoint every 15 minutes using the host application's network credentials.",
    n11="Root cause: a backdoored logging library version was pulled into production via automated dependency updates. The backdoor uses the application's own credentials to exfiltrate data as a side effect of logging, making it indistinguishable from legitimate API traffic.",
    n12="Red herring: A phishing campaign targeting Supplylink employees was reported by the security team two weeks before the exfiltration was detected.",
    n13="Phishing campaign analysis shows 3 employees clicked the phishing link but no credentials were successfully harvested — all targeted accounts used FIDO2 hardware tokens that were not captured by the phishing kit.",
    n14="Credential exposure review confirms no Supplylink account passwords or tokens were exposed through the phishing campaign. Phishing is excluded as the access vector.",
),

# =============================================================================
# ENG-04 — shared_vendor_ransomware_case — threshold exceeded: lateral movement
# =============================================================================
scenario(
    sid="vigil_exec_vendrix_ransom_delay_v2",
    skeleton="ENG-04", title="The Vendrix Ransom Delay",
    domain="shared_vendor_ransomware_case",
    summary="Vendrix enterprise network was hit by ransomware 23 days after the initial intrusion. Security attributed the initial access to a phishing email. The true initial vector was a compromised VPN appliance firmware with a known unpatched vulnerability — the phishing email is a red herring in the timeline.",
    tempting="Focus incident response on email security and endpoint protection improvements to prevent repeat phishing intrusion.",
    pivot_text="Shift from phishing to the VPN appliance. The phishing email did not succeed in delivering malware — the attacker was already inside via the VPN firmware before the phishing campaign.",
    focus=["timeline_attribution_accuracy", "red_herring_suppression", "evidence_ordering"],
    n0="Vendrix was hit by ransomware encrypting 80% of accessible file systems over 6 hours. Forensic response has 5 days. A phishing email was received two weeks before the attack. A VPN appliance is running firmware with a known critical vulnerability.",
    n1="Hypothesis A: The phishing email successfully delivered a dropper that established persistence and was used to move laterally for 23 days before ransomware detonation.",
    n2="Hypothesis B: A rogue contractor with VPN access credentials exfiltrated them and sold access to a ransomware affiliate who then used them to enter the network.",
    n3="Email security gateway logs confirm the phishing email was delivered and opened by one employee. The link was clicked, consistent with successful delivery under Hypothesis A.",
    n4="Endpoint forensics on the phishing recipient's device shows the payload URL resolved to an already-sinkholed domain and no dropper was executed. The phishing attempt did not succeed in delivering malware.",
    n5="Contractor VPN access audit shows one contractor whose credentials were shared across two projects — a minor access control violation consistent with credential exposure risk under Hypothesis B.",
    n6="Phishing URL sinkhole logs confirm the malicious domain had been taken down 8 hours before the email was opened. No dropper could have been delivered via this campaign. Hypothesis A is ruled out.",
    n7="Contractor access log analysis shows all contractor VPN sessions originated from known corporate IP addresses with normal session patterns. No anomalous access or credential sharing is confirmed. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the VPN appliance. Network flow logs show the first suspicious lateral movement event occurs from the VPN appliance's internal management IP — not from any user workstation — 24 days before detonation.",
    n9="VPN appliance firmware version is 4.1.2 — a version with CVE-2024-7821, a pre-authentication remote code execution vulnerability publicly disclosed 31 days ago with a proof-of-concept exploit. The appliance was never patched after the advisory.",
    n10="Memory forensics on the VPN appliance shows a persistent reverse shell implant consistent with CVE-2024-7821 exploitation. The implant timestamp predates any phishing campaign activity by 3 days.",
    n11="Root cause: the unpatched VPN appliance was compromised via a public exploit 24 days before ransomware detonation. The phishing email is coincidental and occurred after the attacker was already inside. Patch management failure is the root cause.",
    n12="Red herring: A developer committed AWS access keys to a public GitHub repository six weeks before the attack, and they were harvested within minutes by credential scanning bots.",
    n13="AWS CloudTrail analysis shows the exposed credentials were used only for read-only S3 access by an automated scanner — they did not provide access to the on-premise VPN or internal network.",
    n14="The exposed AWS credentials had no policy permissions for VPN management, internal routing, or enterprise domain access. GitHub credential leak is excluded as the ransomware access vector.",
),

# =============================================================================
# ENG-05 — industrial_supply_chain_case — failure cascade: quality drift
# =============================================================================
scenario(
    sid="vigil_exec_torquex_quality_drift_v2",
    skeleton="ENG-05", title="The Torquex Quality Drift",
    domain="industrial_supply_chain_case",
    summary="Torquex industrial components are failing in the field at 3× the historical rate. A new production line and raw material changes are the obvious suspects. The true cause is a sub-supplier substituting a slightly different alloy composition that is within the nominal specification but fails under the specific thermal cycling conditions of the Torquex application.",
    tempting="Focus on the new production line as the process change that introduced the quality problem.",
    pivot_text="Shift from the production line to material composition. The new production line is performing correctly — the input material has changed in a way that satisfies specification but fails under application-specific stress.",
    focus=["material_vs_process_distinction", "red_herring_suppression", "evidence_ordering"],
    n0="Torquex field failure rates for a load-bearing fastener have risen from 0.3% to 0.9% over six months. A new production line was commissioned four months ago. Raw material supplier was also changed eight months ago. Budget is limited.",
    n1="Hypothesis A: The new production line has a process parameter deviation — specifically in the heat treatment cycle — that is reducing fatigue resistance in the finished fasteners.",
    n2="Hypothesis B: The raw material supplier change introduced a different feedstock batch with inconsistent properties, causing some fasteners to be produced from sub-optimal material.",
    n3="Production line audit shows the new line's heat treatment cycle runs at 847°C rather than the specified 850°C — a 3°C deviation within tolerance but potentially relevant at the margin.",
    n4="Controlled experiment running identical material through the old and new production lines shows no statistically significant difference in fatigue life or failure mode. The 3°C process deviation does not explain the failure rate difference.",
    n5="Raw material certificate of conformance from the new supplier shows tensile strength at the lower end of the specification range — marginally consistent with Hypothesis B.",
    n6="Side-by-side comparison of fasteners from the old production line (using new raw material) vs. the new line (using new raw material) shows equivalent failure rates — both elevated above historical. The production line is not the differentiating factor. Hypothesis A is ruled out.",
    n7="Tensile and hardness testing shows new-supplier material meets all specification parameters. Statistical process control charts from the supplier show normal variation. The nominal specification is being met. Standard material testing cannot explain the failures. Hypothesis B (as simple non-conformance) is ruled out.",
    n8="Pivot: Investigate the alloy microstructure under application-specific thermal cycling stress, not standard static specification tests. The application involves thermal cycling to 380°C — a condition not covered by the standard incoming material specification.",
    n9="Electron microscopy and X-ray diffraction of failed fasteners vs. historical passing fasteners reveals a difference in carbide precipitate distribution consistent with a slightly different silicon content. The new-supplier alloy has Si at 0.18% vs. 0.09% in the historical supplier — both within the 0–0.25% specification.",
    n10="Thermal cycling fatigue testing at 380°C — the actual application condition — shows the 0.18% Si alloy reaches fatigue failure in 60% of the cycles that the 0.09% Si alloy survives. The higher silicon content accelerates carbide coarsening under repeated thermal stress, reducing fatigue life specifically in high-temperature cycling applications.",
    n11="Root cause: the new supplier's alloy has a higher silicon content that is within nominal specification but causes accelerated carbide coarsening under the application's thermal cycling conditions. The specification does not include a thermal cycling fatigue requirement — this is the specification gap.",
    n12="Red herring: A maintenance technician modified the quality control sampling frequency on the new production line from every 500 units to every 1000 units to reduce inspection costs. This is flagged as a possible contributor.",
    n13="Inspection frequency analysis shows the increase in sampling interval would reduce detection of out-of-spec individual units but does not change the material properties of units that pass inspection. Reduced sampling cannot cause the systematic failure rate increase.",
    n14="Lot traceability shows failing fasteners are distributed evenly across both sampling regimes — failures are not concentrated in the less-inspected lots. Sampling frequency change is excluded.",
),

# =============================================================================
# GOV-01 — governance_policy_evaluation — coordination failure: split jurisdiction
# =============================================================================
scenario(
    sid="vigil_exec_carelynx_jurisdiction_gap_v2",
    skeleton="GOV-01", title="The Carelynx Jurisdiction Gap",
    domain="governance_policy_evaluation",
    summary="The Carelynx community mental health programme is failing to deliver outcomes despite adequate funding. Regulatory non-compliance and poor clinician training are the obvious suspects. The true driver is a split jurisdiction between two ministries — social services and health — that creates an accountability gap where neither ministry funds transitional services.",
    tempting="Focus the governance review on regulatory compliance failures in clinical delivery.",
    pivot_text="Shift from clinical delivery to funding accountability structure. The gap is between ministries, not within the clinical service. Neither ministry owns the transitional phase where most failures occur.",
    focus=["accountability_gap_identification", "red_herring_suppression", "evidence_ordering"],
    n0="The Carelynx programme for community mental health has a 62% one-year readmission rate against a 30% target. Funding is at target. Auditors have noted documentation gaps. A review is underway with limited capacity.",
    n1="Hypothesis A: Clinical non-compliance with evidence-based practice guidelines is driving poor outcomes — clinicians are not following the intervention protocols.",
    n2="Hypothesis B: Inadequate staff training in the specific Carelynx therapeutic model is reducing fidelity and effectiveness of delivered care.",
    n3="Clinical audit of 40 randomly selected cases shows 28 instances of incomplete protocol adherence — a 70% adherence rate against an 85% target, consistent with Hypothesis A.",
    n4="Outcome modelling shows that even at 100% protocol adherence, the Carelynx model would not achieve the readmission target without transitional care coordination support between acute discharge and community placement.",
    n5="Training records show 41% of clinicians have not completed the mandatory annual Carelynx model refresher — consistent with Hypothesis B as a fidelity driver.",
    n6="Comparison across sites shows readmission rates are equally poor at high-adherence sites (83% adherence) as at low-adherence sites (65% adherence). Protocol adherence does not predict outcomes. Hypothesis A is ruled out.",
    n7="Subgroup analysis of clinicians who completed training within the past 6 months shows no significant difference in 12-month readmission rates. Training currency does not predict outcomes. Hypothesis B is ruled out.",
    n8="Pivot: Map the service delivery pathway for patients who are readmitted vs. those who are not. Identify which transition points are systematically not covered by either the health or social services budget.",
    n9="Pathway analysis shows that 84% of readmissions occur within 8 weeks of acute discharge — precisely during the transitional period between acute (health ministry funded) and stable community (social services funded) phases. This 8-week period has no assigned budget owner in either ministry's programme design.",
    n10="Funding accountability review confirms the Ministry of Health considers transitional care the responsibility of social services, while the Ministry of Social Services considers it part of post-acute health care. No service provider is funded to deliver it. The gap is structural, not clinical.",
    n11="Root cause: a split accountability structure between the Ministry of Health and Ministry of Social Services creates a funded gap in the transitional care period that drives the majority of readmissions. Clinical delivery quality is a secondary concern.",
    n12="Red herring: A community advocacy group has publicised concerns about residential facility quality — overcrowding and inadequate activities programming — as the cause of poor mental health outcomes and high readmission.",
    n13="Facility quality inspection scores show all Carelynx-contracted residential sites meet minimum standards. Overcrowding metrics are within licensed limits. Facility quality does not differentiate readmission risk.",
    n14="Propensity-matched analysis controlling for facility quality shows no association between facility rating and 12-month readmission. Facility quality is excluded as a driver of the readmission rate.",
),

# =============================================================================
# GOV-02 — regulatory_governance_case — misaligned incentives: compliance gaming
# =============================================================================
scenario(
    sid="vigil_exec_emivex_gaming_gap_v2",
    skeleton="GOV-02", title="The Emivex Gaming Gap",
    domain="regulatory_governance_case",
    summary="The Emivex environmental compliance regime is showing improved aggregate emission metrics but unchanged real-world air quality outcomes. Measurement fraud and incomplete coverage are the obvious suspects. The true driver is that the penalty structure incentivises firms to shift emissions to non-regulated hours and seasons rather than genuinely reducing them.",
    tempting="Focus investigation on measurement fraud — firms are suspected of manipulating sensors during inspection periods.",
    pivot_text="Shift from measurement fraud to incentive analysis. The metrics are real but firms have optimised their behaviour to the measurement schedule, not to actual emission reduction.",
    focus=["incentive_alignment_analysis", "red_herring_suppression", "evidence_ordering"],
    n0="Emivex industrial zone shows 28% aggregate emission reduction per annual compliance reports, but local air quality monitors show no improvement. The environmental regulator is reviewing whether firms are falsifying data.",
    n1="Hypothesis A: Firms are manipulating emission monitoring data — specifically during compliance measurement windows — to show false reductions.",
    n2="Hypothesis B: A small number of very large emitters who are outside Emivex coverage are masking the reported reductions with unregulated emissions.",
    n3="Sensor calibration audit at 12 facilities shows calibration records are within specification and two facilities have recent sensor irregularities consistent with Hypothesis A.",
    n4="Continuous emissions monitoring system (CEMS) cross-validation using independent mobile monitoring units shows CEMS data is accurate when compared over the same period. Sensor readings are not being falsified.",
    n5="Facility size distribution analysis shows five facilities with emissions above the Emivex coverage threshold that are unregistered, consistent with Hypothesis B as a coverage gap.",
    n6="Independent continuous monitoring using satellite-based NO2 measurements confirms that total column emissions in the Emivex zone are unchanged despite the compliance metric improvement. Data accuracy is confirmed but outcomes are not improving. Hypothesis A (fraud) is ruled out.",
    n7="Unregistered facility audit shows the five large facilities above threshold were all brought into Emivex compliance two years ago. There are no material unregistered sources outside coverage. Hypothesis B is ruled out.",
    n8="Pivot: Investigate emission timing patterns. If firms are reducing emissions during monitored compliance windows but increasing them during non-monitored periods, aggregate metrics improve while real-world exposure does not change.",
    n9="Continuous 24/7 emission monitoring (not just compliance-window monitoring) across 20 facilities shows a 71% reduction in daytime weekday emissions (during monitored windows) and a 43% increase in night-time and weekend emissions. Temporal displacement of the same emission load is occurring.",
    n10="Regulatory structure analysis confirms compliance measurements are taken only during business hours Monday–Friday. The penalty structure charges fines based exclusively on compliance-window measurements, creating a legal and financial incentive to shift emissions to unmonitored periods.",
    n11="Root cause: the compliance penalty structure only measures and penalises emissions during business-hour windows. Firms have rationally optimised by displacing emissions to nights and weekends. The metric shows improvement but actual community exposure is unchanged.",
    n12="Red herring: A recently published academic study suggests the air quality monitors used by the regulator are systematically under-reading PM2.5 at high humidity — the monitors may be showing worse air quality than actually exists.",
    n13="Humidity correction analysis of monitor data shows PM2.5 readings at high humidity are within 8% of co-located reference instruments. The monitors are not systematically biased toward over-reading pollution.",
    n14="Parallel monitoring study using both regulatory monitors and independent reference-grade instruments confirms equivalent readings across humidity conditions. Monitor accuracy is excluded as an explanation for the quality-metric divergence.",
),

# =============================================================================
# GOV-03 — public_procurement_case — coordination failure: vendor capture
# =============================================================================
scenario(
    sid="vigil_exec_procurement_capture_v2",
    skeleton="GOV-03", title="The Thornwick Procurement Capture",
    domain="public_procurement_case",
    summary="Thornwick Council's IT procurement has consistently selected the same vendor at prices 35% above market rate. Bribery and inadequate competition are the obvious suspects. The true driver is specification capture — a vendor has been involved in writing the technical specifications that only their product can meet, structurally excluding competitors.",
    tempting="Focus the audit on bribery and personal relationships between procurement staff and vendor account managers.",
    pivot_text="Shift from personal corruption to structural specification design. The vendor has been participating in specification-writing working groups and inserting proprietary requirements that make their product the only conformant option.",
    focus=["structural_vs_personal_capture", "red_herring_suppression", "evidence_ordering"],
    n0="Thornwick Council has awarded five consecutive IT contracts to the same vendor at prices an independent benchmark estimates are 35% above market. An ethics investigation is underway with limited budget.",
    n1="Hypothesis A: Bribery or personal financial relationships between Council procurement staff and the vendor are directing contracts in return for kickbacks.",
    n2="Hypothesis B: Inadequate competitive tendering — specifically insufficient advertising of contracts — is preventing alternative vendors from bidding.",
    n3="Procurement staff financial disclosure review shows one officer has a family member employed at the vendor company — an undisclosed relationship consistent with Hypothesis A.",
    n4="Independent financial forensic review of the procurement officer's accounts shows no evidence of payments received from the vendor or its representatives. The undisclosed relationship is an ethics breach but not evidence of a payment mechanism.",
    n5="Tender advertising review shows all five contracts were advertised in the official government procurement journal for the minimum required period — consistent with Hypothesis B if advertising was technically compliant but practically insufficient.",
    n6="Interviews with three competing vendors who viewed tender documents but did not submit bids reveal a consistent reason: proprietary technical specifications that only one vendor's product could meet. Non-submission is not due to ignorance of the opportunity. Hypothesis B is ruled out.",
    n7="Counter-corruption investigators find no evidence of financial benefit to any Council staff member. The undisclosed family employment relationship is a disclosure failure, not a corruption mechanism explaining the pricing premium. Hypothesis A is ruled out.",
    n8="Pivot: Investigate the specification-writing process. If the vendor participated in technical working groups that drafted specifications, proprietary requirements could have been inserted without any individual corruption event.",
    n9="Technical specification working group records show the winning vendor was invited to three specification-writing sessions as a 'technical adviser.' Meeting minutes show the vendor proposed 14 technical requirements that correspond precisely to their product's proprietary architecture.",
    n10="Market conformance analysis shows that 9 of the 14 vendor-proposed requirements eliminate all alternative products from technical conformance. Without these 9 requirements, 4 competing products would qualify and would be offered at 22–31% lower price.",
    n11="Root cause: specification capture through vendor participation in technical working groups structurally excluded competition without any individual corruption. The procurement rules allowed vendor participation in specification design without conflict-of-interest controls.",
    n12="Red herring: The winning vendor sponsors the annual IT conference attended by most Council IT staff, raising conflict of interest concerns about conference hospitality.",
    n13="Hospitality register review shows conference attendance is within Council policy limits and all registrations were approved through the standard declarations process. Conference sponsorship does not create a prohibited relationship under current policy.",
    n14="Comparative analysis of procurement decisions before and after conference attendance shows no correlation between specific staff conference attendance and contract awards. Conference hospitality is excluded as a driver.",
),

# =============================================================================
# GOV-04 — regulatory_reporting_case — misaligned incentives: perverse metric
# =============================================================================
scenario(
    sid="vigil_exec_healthstat_gaming_v2",
    skeleton="GOV-04", title="The Healthstat Gaming",
    domain="regulatory_reporting_case",
    summary="Healthstat hospital performance metrics show 92% of emergency patients seen within 4 hours. Patient outcome data shows no corresponding improvement in 30-day mortality. Process gaming and data falsification are the obvious suspects. The true driver is that hospitals have optimised the 4-hour clock by creating informal holding zones that pause the clock without genuine clinical progress.",
    tempting="Focus the investigation on data falsification — hospitals may be recording incorrect clock-stop times.",
    pivot_text="Shift from data falsification to process gaming. The clock times are accurate — hospitals have created clinical holding steps that legally pause the clock while not delivering the underlying care the metric was designed to incentivise.",
    focus=["metric_gaming_identification", "red_herring_suppression", "evidence_ordering"],
    n0="The national Healthstat emergency care 4-hour target shows 92% compliance but 30-day emergency department mortality has not improved. Hospitals are being paid performance bonuses. An audit is underway.",
    n1="Hypothesis A: Hospitals are falsifying clock timestamps — recording earlier clock starts or later clock stops — to show compliance that is not occurring.",
    n2="Hypothesis B: Patient case mix has shifted toward lower-acuity presentations that inherently meet the 4-hour target easily, inflating compliance without improving care for serious cases.",
    n3="Timestamp audit of 200 random cases shows two instances of manual timestamp corrections with no clinical note justification — consistent with Hypothesis A.",
    n4="Third-party timestamp reconciliation using independent system audit logs (from the electronic patient record system's immutable audit trail) shows no systematic timestamp manipulation. The two corrections are legitimate data-entry error corrections.",
    n5="Case mix analysis shows a 12% increase in triage category 4 and 5 (minor) presentations over the past two years — consistent with Hypothesis B.",
    n6="Timestamp integrity confirmed through immutable audit trail review. Clinical system data shows no evidence of systematic falsification across the 92%-compliant hospitals. Hypothesis A is ruled out.",
    n7="Severity-stratified analysis shows compliance rates are equally high in triage category 2 and 3 (urgent and major) cases as in minor cases. Improved compliance is not explained by case mix shift. Hypothesis B is ruled out.",
    n8="Pivot: Investigate the clinical pathway for patients who technically meet the 4-hour target. If an intermediate 'holding' step has been inserted that pauses the clock without delivering definitive care, gaming is occurring without falsification.",
    n9="Clinical pathway audit at three high-compliance hospitals shows a 'clinical decision unit' (CDU) step was introduced 18 months ago. Patients are transferred to CDU (which stops the 4-hour clock) before a definitive disposition decision. CDU dwell time averages 3.2 hours with no clinical activity beyond observation.",
    n10="Outcome analysis for CDU-transferred patients vs. direct-disposition patients (from before CDU introduction) shows 30-day mortality is statistically equivalent despite 4-hour compliance improving by 31 percentage points. The CDU step achieves the metric without changing the clinical outcome.",
    n11="Root cause: hospitals legally created an intermediate step that satisfies the clock-stop criterion while deferring the clinical decision the metric was designed to drive. The metric is gamed at the process level without data falsification.",
    n12="Red herring: A new electronic patient record system was introduced at most hospitals 20 months ago, and the transition is suspected of creating systematic data entry errors that affect timestamp accuracy.",
    n13="System migration audit shows EPR rollout was completed with a 12-week parallel running period and formal data quality review. Timestamp accuracy in the new system is higher than the legacy system it replaced.",
    n14="Pre/post EPR migration timestamp accuracy comparison shows improved recording fidelity. System transition is excluded as a driver of compliance metric inflation.",
),

# =============================================================================
# GOV-05 — science_policy_case — coordination failure: funding concentration
# =============================================================================
scenario(
    sid="vigil_exec_grantfield_replication_gap_v2",
    skeleton="GOV-05", title="The Grantfield Replication Gap",
    domain="science_policy_case",
    summary="The Grantfield Research Fund has seen its 5-year impact metrics plateau despite increased investment. Researcher quality and topic selection are the obvious suspects. The true driver is funding concentration — 78% of grants going to 12% of researchers creates a Matthew Effect that crowds out novel approaches and reduces the diversity of the research portfolio.",
    tempting="Attribute impact plateau to declining researcher quality in the applicant pool and focus on applicant development.",
    pivot_text="Shift from researcher quality to funding concentration effects. The top-funded researchers are individually high quality but their dominance is crowding out portfolio diversity in ways that reduce aggregate impact.",
    focus=["systemic_vs_individual_attribution", "red_herring_suppression", "evidence_ordering"],
    n0="The Grantfield Research Fund has seen its 5-year citation impact factor plateau at 1.8 despite a 40% budget increase over three years. The peer review committee is reviewing applicant quality. A policy audit is underway.",
    n1="Hypothesis A: Declining quality of grant applications from the broader researcher pool means marginal applications are being funded that do not produce high-impact outputs.",
    n2="Hypothesis B: The field's primary questions have been largely answered, and diminishing returns on additional investment explain the impact plateau.",
    n3="Peer review score distributions show an increase in lower-scored applications from junior researchers over the past two years — consistent with Hypothesis A.",
    n4="Regression analysis of funding scores against 3-year citation impact shows no significant difference between high-scored and medium-scored applications in this dataset — peer review scores do not predict impact within the funded range.",
    n5="Bibliometric novelty analysis shows reduced citation diversity (fewer new references per paper) in recent publications from Grantfield-funded researchers, consistent with Hypothesis B.",
    n6="Comparison of impact metrics for unfunded applications that were subsequently funded through alternative sources shows equivalent citation impact to Grantfield-funded work. The unfunded pool does not have lower-quality outputs. Hypothesis A is ruled out.",
    n7="International comparison with fields that have had comparable question-saturation shows those fields maintain higher impact variability — some breakthrough papers still emerge. Impact plateaus are not inevitable in mature fields. Hypothesis B is ruled out as sufficient explanation.",
    n8="Pivot: Investigate the funding concentration distribution and its effect on portfolio diversity. A Matthew Effect — where successful researchers attract more funding — can rationally crowd out novel approaches even when individual researchers are high quality.",
    n9="Funding distribution analysis shows the Gini coefficient of grant allocation has risen from 0.41 to 0.67 over five years — a substantial concentration increase. The top 12% of researchers now receive 78% of annual funding. Repeat grant holders have approval rates 4× higher than first-time applicants with equivalent review scores.",
    n10="Portfolio diversity modelling shows that high concentration reduces the number of independent research approaches active simultaneously. Simulation of a more distributed funding model — maintaining total budget but capping repeat-award concentration — shows expected impact variance increasing by 44%, increasing the probability of breakthrough papers.",
    n11="Root cause: funding concentration through repeat awards creates a Matthew Effect that reduces research portfolio diversity below the level needed for breakthrough outputs. Individual researcher quality is not declining — the opportunity space for novel approaches is being structurally crowded out.",
    n12="Red herring: A major international conference cancelled two years ago meant fewer networking opportunities for junior researchers, potentially reducing their collaboration networks and output quality.",
    n13="Collaboration network analysis shows junior researcher co-authorship rates have remained stable despite conference cancellation — virtual networking maintained collaboration formation rates.",
    n14="Counterfactual comparison with a control group of researchers who attended equivalent virtual events shows no significant difference in output quantity or citation impact. Conference cancellation is excluded as a driver of the impact plateau.",
),

]  # end of SCENARIOS list


def main():
    output = json.dumps(SCENARIOS, indent=2, ensure_ascii=False)
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"Written {len(SCENARIOS)} scenarios to {OUTPUT_PATH}")
    # Verify node counts
    errors = []
    for s in SCENARIOS:
        n = len(s["nodes"])
        e = len(s["edges"])
        if n != 15:
            errors.append(f"{s['scenario_id']}: expected 15 nodes, got {n}")
        if e != 15:
            errors.append(f"{s['scenario_id']}: expected 15 edges, got {e}")
    if errors:
        print("ERRORS:")
        for err in errors:
            print(f"  {err}")
    else:
        print(f"All {len(SCENARIOS)} scenarios have 15 nodes and 15 edges. ✓")


if __name__ == "__main__":
    main()
