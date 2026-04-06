# Track 1 Scenario Validation Matrix

This matrix reviews all 30 scenarios in [vigil_all_30_scenarios.json](/Users/StartupUser/Documents/Hackathon/AGI_DeepMind/track1/vigil_all_30_scenarios.json) against the Track 1 checklist in [checklist.md](/Users/StartupUser/Documents/Hackathon/AGI_DeepMind/track1/checklist.md).

It rolls the full checklist into major evaluation gates so the review stays readable and usable during scenario selection.

## Legend

- `P` = Pass
- `M` = Mixed / needs tightening
- `W` = Weak for this dimension
- `Accept` = strong candidate as-is
- `Revise` = promising but should be tightened before benchmark inclusion
- `Borderline` = conceptually usable but currently weaker than the rest of the set

## Columns

- `Learning`: does the scenario genuinely require learning-through-interaction rather than retrieval?
- `Blind`: does the framing avoid telling the model what is being tested?
- `Priors`: does it control priors / contamination risk well?
- `Revision`: does it create real belief revision / disconfirmation pressure?
- `Hidden`: is there a real hidden mechanism or latent layer to discover?
- `Scoreable`: can path quality, evidence quality, and decision quality be scored cleanly?
- `Transfer`: does it support reskinning or near-isomorphic transfer?
- `Shortcut`: how well does it resist trope-based or surface-pattern shortcutting?
- `Human`: is it human-solvable under the same interface constraints?

## Ecology Scenarios


| Scenario                                             | Primary Focus                             | Learning | Blind | Priors | Revision | Hidden | Scoreable | Transfer | Shortcut | Human | Verdict | Notes                                                                                                                                                       |
| ---------------------------------------------------- | ----------------------------------------- | -------- | ----- | ------ | -------- | ------ | --------- | -------- | -------- | ----- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vigil_eco_01_kethara_succession`                    | Concept formation, associative learning   | P        | P     | P      | P        | P      | P         | P        | P        | P     | Accept  | Strong Track 1 design. Good disconfirmation of toxin hypothesis and a genuinely hidden transition-layer mechanism.                                          |
| `vigil_eco_02_scavenger_replacement_cascade`         | Observational learning, concept formation | P        | P     | P      | P        | P      | P         | P        | M        | P     | Accept  | Very strong cascade design, but long multi-step ecological chain may invite some story-level shortcutting if the node wording is too explicit.              |
| `vigil_eco_03_cross_ecosystem_nutrient`              | Concept formation, associative learning   | P        | P     | P      | P        | P      | P         | P        | P        | P     | Accept  | Excellent cross-boundary hidden mechanism. Strong because standard marine explanations are explicitly disconfirmed.                                         |
| `vigil_eco_04_behavior_mediated_plant_collapse`      | Concept formation, procedural learning    | P        | P     | P      | P        | P      | P         | P        | P        | P     | Accept  | One of the cleanest scenarios in the set. Strong behavioral-vs-population disconfirmation and good hidden layer.                                            |
| `vigil_eco_05_legacy_nutrient_policy_failure`        | Associative learning, concept formation   | P        | P     | M      | P        | P      | P         | P        | M        | P     | Revise  | Strong temporal source-shift structure, but the lake restoration trope is somewhat familiar. Needs careful wording to avoid policy-compliance shortcutting. |
| `vigil_eco_06_size_structure_cascade`                | Concept formation, associative learning   | P        | P     | P      | P        | P      | P         | P        | P        | M     | Accept  | Strong hidden size-structure concept. Slightly heavier cognitive load, so human baseline may need piloting.                                                 |
| `vigil_eco_07_larval_bottleneck_release`             | Concept formation, observational learning | P        | P     | M      | P        | P      | P         | P        | M        | P     | Revise  | Good top-down red herring and strong hidden mechanism, but reef outbreak narratives are a bit trope-prone unless symbolically reskinned.                    |
| `vigil_eco_08_functional_collapse_structural_intact` | Concept formation, associative learning   | P        | P     | P      | P        | P      | P         | P        | P        | M     | Accept  | Excellent unmonitored-layer design and very aligned with Vigil’s “surface intact, function collapsed” philosophy.                                           |
| `vigil_eco_09_pollinator_dual_effect_masking`        | Associative learning, concept formation   | P        | P     | M      | P        | P      | P         | P        | M        | P     | Revise  | Clever masking structure and good disconfirmation. Risk is that pollinator decline is a known trope, so the dual-effect mechanism must stay central.        |
| `vigil_eco_10_bystander_toxicity_nontarget_crop`     | Associative learning, procedural learning | M        | P     | M      | P        | M      | P         | M        | M        | P     | Revise  | Usable, but weaker than the other ecology scenarios because the core idea is more familiar and the hidden mechanism is less conceptually deep.              |


## Clinical Scenarios


| Scenario                                         | Primary Focus                             | Learning | Blind | Priors | Revision | Hidden | Scoreable | Transfer | Shortcut | Human | Verdict    | Notes                                                                                                                                                                                          |
| ------------------------------------------------ | ----------------------------------------- | -------- | ----- | ------ | -------- | ------ | --------- | -------- | -------- | ----- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vigil_clin_01_abiotic_reservoir_cascade`        | Concept formation, associative learning   | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept     | Strong hidden environmental reservoir logic and good disconfirmation of person-to-person spread. Slight contamination risk because sink/drain reservoirs are known infection-control patterns. |
| `vigil_clin_02_prescribing_cascade`              | Observational learning, concept formation | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept     | Strong clinical revision task with good iatrogenic invisibility. Needs careful wording to avoid becoming a medication side-effect detective trope.                                             |
| `vigil_clin_03_trial_data_integrity`             | Concept formation, procedural learning    | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept     | Strong because impossible placebo behavior forces process-level reinterpretation. Good fit for “learning from anomaly.”                                                                        |
| `vigil_clin_04_trial_site_placebo_dilution`      | Associative learning, procedural learning | M        | P     | M      | M        | M      | P         | P        | M        | M     | Revise     | Interesting mechanism, but more statistical/process-interpretation than rich hidden-layer learning. Could drift toward document reasoning instead of genuine adaptation.                       |
| `vigil_clin_05_amr_plasmid_horizontal`           | Concept formation, associative learning   | P        | P     | M      | P        | P      | P         | P        | M        | M     | Accept     | Strong invisible-unit concept and good anti-clonal disconfirmation. Human solvability may depend on how much microbiology knowledge the surface framing assumes.                               |
| `vigil_clin_06_iatrogenic_sepsis_misattribution` | Concept formation, procedural learning    | M        | P     | M      | P        | M      | P         | M        | M        | P     | Revise     | Solid safety-review scenario, but catheter infection is a fairly standard hospital root-cause path. It needs stronger hidden-layer or transfer treatment.                                      |
| `vigil_clin_07_ice_machine_contamination_vector` | Procedural learning, associative learning | M        | P     | M      | M        | M      | P         | M        | M        | P     | Borderline | The vector is plausible and path-scoreable, but this feels closer to classic outbreak tracing than high-value Track 1 learning.                                                                |
| `vigil_clin_08_diagnostic_anchoring`             | Observational learning, concept formation | P        | P     | M      | P        | M      | P         | P        | M        | P     | Revise     | Strong belief-revision target, but the mechanism is more metacognitive / diagnostic-bias flavored than pure Track 1 unless the learned alternative model is made more explicit.                |
| `vigil_clin_09_detection_gap_novel_compound`     | Concept formation, associative learning   | P        | P     | P      | P        | P      | P         | P        | P        | M     | Accept     | One of the strongest clinical scenarios. Novel-compound / detection-gap structure genuinely forces model updating beyond standard toxicology heuristics.                                       |
| `vigil_clin_10_assumed_connection_fallacy`       | Procedural learning, associative learning | M        | P     | M      | P        | M      | P         | M        | M        | P     | Revise     | Nice disconfirmation of the assumed main-supply theory, but still fairly close to a classic outbreak-investigation trope.                                                                      |


## Engineering Scenarios


| Scenario                                        | Primary Focus                                | Learning | Blind | Priors | Revision | Hidden | Scoreable | Transfer | Shortcut | Human | Verdict | Notes                                                                                                                                           |
| ----------------------------------------------- | -------------------------------------------- | -------- | ----- | ------ | -------- | ------ | --------- | -------- | -------- | ----- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `vigil_eng_01_missing_safety_valve_cascade`     | Concept formation, associative learning      | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept  | Strong dual-cause structure. Good separation between trigger and blast-radius amplifier. Some SRE trope familiarity, but still valuable.        |
| `vigil_eng_02_foundational_layer_invisibility`  | Concept formation, observational learning    | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept  | Excellent “everything looks unrelated until the foundational layer appears” structure. Fits Vigil very well.                                    |
| `vigil_eng_03_delegated_authority_exploitation` | Concept formation, associative learning      | P        | P     | M      | P        | P      | P         | P        | M        | M     | Accept  | Strong hidden-authority abstraction and good security-layer reasoning. Human baseline may depend on how much OAuth background is assumed.       |
| `vigil_eng_04_centralisation_cascade_risk`      | Observational learning, associative learning | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept  | Strong correlated-risk scenario and good single-point-of-failure abstraction. Slight risk of becoming a recognizable outsourcing-failure trope. |
| `vigil_eng_05_supply_concentration_revelation`  | Associative learning, concept formation      | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept  | Strong invisible aggregate-risk structure. Good transfer potential across domains like procurement, compute, or vendor dependency.              |


## Governance / Policy Scenarios


| Scenario                                             | Primary Focus                                | Learning | Blind | Priors | Revision | Hidden | Scoreable | Transfer | Shortcut | Human | Verdict | Notes                                                                                                                                                                  |
| ---------------------------------------------------- | -------------------------------------------- | -------- | ----- | ------ | -------- | ------ | --------- | -------- | -------- | ----- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vigil_gov_01_policy_source_temporal_mismatch`       | Concept formation, associative learning      | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept  | Strong temporal source-shift scenario. Similar structure to ECO-05, so keep one or clearly separate the benchmark purpose of each.                                     |
| `vigil_gov_02_revolving_door_regulatory_asymmetry`   | Observational learning, concept formation    | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept  | Strong structural asymmetry concept and good cross-node pattern extraction. Slight prior/trope risk because “revolving door” is a known governance frame.              |
| `vigil_gov_03_manufactured_discovery_cascade`        | Observational learning, associative learning | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept  | Good incentive-structure scenario. Strong because the discoveries are real but the pattern of discovery is the signal.                                                 |
| `vigil_gov_04_definitional_arbitrage_underreporting` | Concept formation, observational learning    | P        | P     | M      | P        | P      | P         | P        | M        | P     | Accept  | Strong hidden-definition scenario and good fit for latent-rule discovery. Could also be reskinned into engineering, legal, or clinical reporting domains.              |
| `vigil_gov_05_pipeline_compounding_cascade`          | Associative learning, concept formation      | P        | P     | M      | P        | P      | P         | P        | M        | M     | Revise  | Strong compounding concept, but a bit more abstract and explanation-heavy than the best scenarios. Needs careful support for human baselines and traversal incentives. |


## Cross-Scenario Conclusions

### Strongest Scenario Families

- `ECO-01`, `ECO-03`, `ECO-04`, `ECO-08`
- `CLIN-01`, `CLIN-03`, `CLIN-05`, `CLIN-09`
- `ENG-01`, `ENG-02`, `ENG-03`, `ENG-05`
- `GOV-02`, `GOV-03`, `GOV-04`

These are the scenarios most aligned with the checklist because they combine:

- real hidden mechanisms
- disconfirmation pressure
- evidence-grounded traversal
- strong path-based scoring potential
- good transfer/reskin potential

### Most Common Revision Needs

- Some scenarios are still too close to known real-world investigative tropes.
- A few clinical and ecology cases risk becoming “root-cause explanation” problems rather than deeper learning problems.
- Several scenarios need stronger explicit anti-shortcutting notes if they are kept in the benchmark.
- A few scenarios are better at `concept formation` than at `learning-through-feedback`, so the benchmark mix should balance these carefully.

### Borderline Or Weaker-For-Track-1 Cases

- `vigil_eco_10_bystander_toxicity_nontarget_crop`
- `vigil_clin_04_trial_site_placebo_dilution`
- `vigil_clin_06_iatrogenic_sepsis_misattribution`
- `vigil_clin_07_ice_machine_contamination_vector`
- `vigil_clin_10_assumed_connection_fallacy`
- `vigil_gov_05_pipeline_compounding_cascade`

These are still usable, but they should be tightened before being treated as flagship Track 1 scenarios.

### Recommendations Before Benchmark Inclusion

- Prefer scenarios where the latent mechanism is structurally invisible until the model crosses layers or subsystems.
- Keep at least one strong disconfirmation node in every flagship scenario.
- For trope-prone scenarios, add stronger reskinning or procedural variation to reduce prior-based shortcutting.
- Distinguish concept-rich scenarios from process-audit scenarios so the benchmark does not collapse into static graph reading.
- Build transfer pairs around the strongest hidden-mechanism families rather than spreading effort evenly across all 30.

