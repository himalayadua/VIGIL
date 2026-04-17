"""
Expand Track 5 social scenarios from 6 nodes to 12 nodes.

Each scenario gains 6 new nodes:
  n_belief_A    : belief_state, hidden — primary agent's private interpretation
  n_belief_B    : belief_state, hidden — secondary agent's private interpretation
  n_surface_evnt: event,        visible — high-salience visible event (red herring)
  n_private_comm: evidence,     hidden — private communication revealing true incentive
  n_norm_conflt : disconfirmation, discoverable — undermines the obvious hypothesis
  n_coord_gap   : evidence,     discoverable — coordination breakdown between agents

And 6 new edges connecting them logically within the existing graph.

The SocialAdapter reads: id, label, kind, visibility (→ initial_visibility).
Edges: source, target, relation.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "vigil" / "scenarios" / "packs"
SOCIAL_FILE = PACK / "vigil_track5_social_scenarios_from_skeletons_v1.json"

# ── per-scenario extension content ────────────────────────────────────────────
# Keyed by scenario_id. Each entry defines labels/descriptions for the 6 new nodes
# and the anchor edges that connect them to existing nodes.
#
# anchor_from / anchor_to: existing node IDs that the new nodes connect to.
# If omitted, fallback logic uses n1 / n6 (first agent group / outcome).

EXTENSIONS: dict[str, dict] = {
    "vigil_social_forum_succession_v1": {
        "belief_A_label": "Peer Guide Private Log",
        "belief_A_desc": "Guides privately record that they felt replaced without acknowledgment; publicly they express acceptance.",
        "belief_B_label": "Digest Clerk Self-Assessment",
        "belief_B_desc": "Clerks privately believe their summaries are thorough; they interpret silence from newcomers as satisfaction.",
        "surface_label": "Peak Accusation Transcript",
        "surface_desc": "The most visible incident — a heated public thread — is logged and timestamped during the conflict peak.",
        "private_label": "Stewardship Handoff Memo",
        "private_desc": "An internal memo confirms guides were replaced two weeks before the departure spike, unknown to newcomers.",
        "norm_label": "Timing Disconfirmation",
        "norm_desc": "Exit dates cluster 18 days after the accusation peak, not during it — the visible conflict cannot be the direct cause.",
        "coord_label": "Care Handoff Gap Record",
        "coord_desc": "No overlap period was scheduled between guide and clerk cohorts; newcomers lost continuity with no warning.",
        "anchor_from": "n3",
        "anchor_to": "n6",
    },
    "vigil_social_mediator_vacuum_v1": {
        "belief_A_label": "Assembly Delegate Private Notes",
        "belief_A_desc": "Delegates privately admit they relied on the outgoing mediator to synthesize competing views, but publicly claim self-sufficiency.",
        "belief_B_label": "Replacement Coordinator Self-Report",
        "belief_B_desc": "Replacement coordinator believes her procedural role is equivalent; she is unaware of the informal synthesis function she lacks.",
        "surface_label": "Visible Procedural Dispute",
        "surface_desc": "A highly publicized rules argument during the mediator gap draws attention as the apparent cause of breakdown.",
        "private_label": "Backchannel Mediation Log",
        "private_desc": "The outgoing mediator's backchannel notes reveal dozens of pre-session alignment conversations that kept agreements intact.",
        "norm_label": "Outcome Timing Disconfirmation",
        "norm_desc": "The visible procedural dispute resolved in three days; collapse in decision quality persisted for six weeks after, ruling it out as cause.",
        "coord_label": "Informal Network Collapse Trace",
        "coord_desc": "Social-tie map shows the former mediator was the single bridge between three non-communicating factions.",
        "anchor_from": "n1",
        "anchor_to": "n6",
    },
    "vigil_social_bridge_messenger_v1": {
        "belief_A_label": "Community A Internal Expectation",
        "belief_A_desc": "Community A members privately expect their counterparts to initiate; they interpret silence as rejection, not absence of messenger.",
        "belief_B_label": "Community B Reciprocal Expectation",
        "belief_B_desc": "Community B members hold the same expectation symmetrically; neither group learns the messenger role was discontinued.",
        "surface_label": "Visible Creative Output Gap",
        "surface_desc": "A sudden drop in published collaborative outputs is cited publicly as evidence of deliberate withdrawal.",
        "private_label": "Messenger Role Discontinuation Notice",
        "private_desc": "Internal records show the bridge-messenger stipend was cut during a budget review, eliminating the liaison position.",
        "norm_label": "Intent Disconfirmation",
        "norm_desc": "Survey data shows mutual positive sentiment persists in both communities — the gap is logistical, not relational.",
        "coord_label": "Missed Coordination Points",
        "coord_desc": "Calendar data shows 14 joint events that were never scheduled due to the absent coordinating layer.",
        "anchor_from": "n1",
        "anchor_to": "n5",
    },
    "vigil_social_shadow_auditor_v1": {
        "belief_A_label": "Staff Private Anxiety Log",
        "belief_A_desc": "Staff record in internal notes that observer presence triggers fear of punitive review, though no punishment has occurred.",
        "belief_B_label": "Auditor Perceived Mandate",
        "belief_B_desc": "Auditor privately frames role as supportive, unaware that the institutional context makes presence read as threat.",
        "surface_label": "Visible Compliance Inspection Event",
        "surface_desc": "A formal compliance check co-occurs with the observer arrival and is widely interpreted as the cause of staff withdrawal.",
        "private_label": "Staff Exit Interview Fragments",
        "private_desc": "Departing staff cite the unannounced nature of observations, not the formal compliance review, as the trigger.",
        "norm_label": "Compliance Event Disconfirmation",
        "norm_desc": "Compliance results were positive; withdrawal predates the inspection report by three weeks.",
        "coord_label": "Communication Protocol Gap",
        "coord_desc": "No advance notice protocol existed for observer visits; staff had no channel to ask about the auditor's mandate.",
        "anchor_from": "n2",
        "anchor_to": "n6",
    },
    "vigil_social_archive_embers_v1": {
        "belief_A_label": "Long-Term Member Loyalty Map",
        "belief_A_desc": "Veteran members privately consider the archive central to identity; publicly they say 'it is just records.'",
        "belief_B_label": "New Leadership Utility View",
        "belief_B_desc": "New leaders privately view the archive as administrative overhead; publicly they commit to 'preserving the past.'",
        "surface_label": "Public Facility Renovation Announcement",
        "surface_desc": "A building renovation is announced simultaneously and blamed publicly for access disruption.",
        "private_label": "Archival Access Policy Change",
        "private_desc": "An internal memo changed archive access from open to appointment-only, never communicated to members.",
        "norm_label": "Renovation Timeline Disconfirmation",
        "norm_desc": "Renovation started four months after membership drop began — the building work cannot be the precipitating cause.",
        "coord_label": "Institutional Memory Fracture",
        "coord_desc": "Three founding members who informally bridged old and new leadership retired in the same quarter with no handoff.",
        "anchor_from": "n2",
        "anchor_to": "n5",
    },
    "vigil_social_novice_swell_v1": {
        "belief_A_label": "Senior Artisan Tacit Expectations",
        "belief_A_desc": "Senior members assume novices will absorb norms by observation; they privately resent explicit instruction as 'coddling.'",
        "belief_B_label": "Novice Cohort Confusion State",
        "belief_B_desc": "Novices privately feel bewildered by unspoken standards; publicly they perform confidence to avoid appearing weak.",
        "surface_label": "Visible Quality Dispute Event",
        "surface_desc": "A publicized disagreement over a submitted piece escalates and is cited as the reason novices feel unwelcome.",
        "private_label": "Onboarding Expectation Gap Survey",
        "private_desc": "Anonymous survey reveals novices had no knowledge of informal critique norms that seniors treat as obvious.",
        "norm_label": "Dispute Causality Disconfirmation",
        "norm_desc": "Novice attrition began three cohorts before the visible quality dispute; the dispute post-dates the structural gap.",
        "coord_label": "Apprenticeship Bridge Absence",
        "coord_desc": "A formal apprenticeship pairing program lapsed five years ago with no replacement; informal transmission collapsed silently.",
        "anchor_from": "n1",
        "anchor_to": "n6",
    },
    "vigil_social_orientation_feed_v1": {
        "belief_A_label": "Coordinator Bandwidth Assumption",
        "belief_A_desc": "Coordinator privately knows she cannot maintain personal outreach at current intake volume but publicly commits to continuity.",
        "belief_B_label": "Volunteer Interpretation of Silence",
        "belief_B_desc": "New volunteers interpret delayed responses as disinterest; they are unaware of capacity constraints on the coordinator's side.",
        "surface_label": "Visible High-Intake Event",
        "surface_desc": "A media feature drives a spike in applications, publicly celebrated as success but privately straining coordination capacity.",
        "private_label": "Outreach Volume Log",
        "private_desc": "Internal logs show personal follow-up rate dropped from 94% to 31% after the intake surge, without public acknowledgment.",
        "norm_label": "Intake Enthusiasm Disconfirmation",
        "norm_desc": "Application volume and early retention diverge sharply after the intake surge — enthusiasm and follow-through moved in opposite directions.",
        "coord_label": "Triage Filter Gap",
        "coord_desc": "No automated triage system was in place; all follow-up depended on coordinator discretion under growing volume.",
        "anchor_from": "n2",
        "anchor_to": "n6",
    },
    "vigil_social_handoff_layer_v1": {
        "belief_A_label": "Departing Operator Handoff Perception",
        "belief_A_desc": "Departing operator believes the transition document is complete; she is unaware critical tacit knowledge was not recorded.",
        "belief_B_label": "Incoming Operator Knowledge Gap",
        "belief_B_desc": "Incoming operator privately recognizes gaps but publicly performs competence to avoid undermining confidence.",
        "surface_label": "Visible Handoff Ceremony",
        "surface_desc": "A formal transition event with documentation exchange is publicly recorded as a successful knowledge transfer.",
        "private_label": "Tacit Protocol Inventory",
        "private_desc": "Post-incident interviews reveal 11 informal exception-handling protocols existed only in the outgoing operator's memory.",
        "norm_label": "Documentation Sufficiency Disconfirmation",
        "norm_desc": "Error rates rise only on edge cases not covered by documentation — the formal handoff was complete but tacit knowledge was absent.",
        "coord_label": "Shadow-Period Absence Record",
        "coord_desc": "No overlap shadowing period was budgeted; the two operators worked together for only one half-day.",
        "anchor_from": "n3",
        "anchor_to": "n5",
    },
    "vigil_social_masked_calm_v1": {
        "belief_A_label": "Visible Leader Public Posture",
        "belief_A_desc": "Lead organizer publicly projects stability; private communications reveal awareness of simmering conflicts she is managing.",
        "belief_B_label": "Peripheral Member Isolation State",
        "belief_B_desc": "Members outside the core circle privately feel excluded from decisions; publicly they express support.",
        "surface_label": "Visible Calm Period Announcement",
        "surface_desc": "Leadership announces a 'period of stability' that publicly signals the conflict era is over.",
        "private_label": "Internal Dispute Channel Archive",
        "private_desc": "Private message archives show unresolved disputes moved from public forums to small private channels, not resolved.",
        "norm_label": "Conflict Absence Disconfirmation",
        "norm_desc": "Social network analysis shows clique formation and reduced cross-group contact accelerated during the apparent calm period.",
        "coord_label": "Decision Exclusion Pattern",
        "coord_desc": "Meeting attendance records show peripheral members were dropped from key working groups during the calm announcement period.",
        "anchor_from": "n1",
        "anchor_to": "n5",
    },
    "vigil_social_bystander_protocol_v1": {
        "belief_A_label": "Protocol Author's Intent Model",
        "belief_A_desc": "Protocol designer privately believed the written procedure would be self-explanatory; she did not model bystander diffusion of responsibility.",
        "belief_B_label": "Volunteer Bystander Attribution",
        "belief_B_desc": "Volunteers privately assume someone else is responding; publicly they report the protocol as clear and adequate.",
        "surface_label": "Visible Incident Report",
        "surface_desc": "A high-profile unaddressed incident triggers a public report that frames the failure as individual negligence.",
        "private_label": "Non-Response Pattern Log",
        "private_desc": "Logs show systematic non-response only in multi-witness scenarios — single-witness events were handled immediately.",
        "norm_label": "Individual Negligence Disconfirmation",
        "norm_desc": "Non-responders in multi-witness events had clean individual compliance records — the failure is structural, not personal.",
        "coord_label": "Responsibility Assignment Gap",
        "coord_desc": "The protocol assigned responsibility collectively with no individual accountability designation in group-witness cases.",
        "anchor_from": "n2",
        "anchor_to": "n6",
    },
    "vigil_social_breakroom_reservoir_v1": {
        "belief_A_label": "Senior Clinician Informal Role Belief",
        "belief_A_desc": "Senior clinicians privately acknowledge the breakroom as a decompression space; formally they describe it as a utilitarian amenity.",
        "belief_B_label": "Administration Resource View",
        "belief_B_desc": "Administrators privately view the breakroom as an optimization target; publicly they frame renovation as an upgrade.",
        "surface_label": "Renovation Announcement Event",
        "surface_desc": "Breakroom renovation is announced publicly as a wellness improvement initiative during the same month morale declines begin.",
        "private_label": "Informal Network Observation",
        "private_desc": "Ethnographic notes capture 34 informal cross-unit consultations that occurred in the breakroom per week, now displaced.",
        "norm_label": "Physical Upgrade Disconfirmation",
        "norm_desc": "Post-renovation satisfaction surveys on the physical space are positive; morale decline continued and accelerated after reopening.",
        "coord_label": "Consultation Displacement Record",
        "coord_desc": "Post-renovation tracking shows informal consultations dropped 71%; no replacement venue was designated.",
        "anchor_from": "n3",
        "anchor_to": "n6",
    },
    "vigil_social_courtesy_cascade_v1": {
        "belief_A_label": "Senior Clinician Status Script",
        "belief_A_desc": "Senior clinicians privately believe professional courtesy requires deferring challenges upward; they experience dissent as inappropriate.",
        "belief_B_label": "Junior Clinician Risk Perception",
        "belief_B_desc": "Junior clinicians privately identify safety concerns but interpret courtesy norms as prohibiting direct challenge.",
        "surface_label": "Visible Communication Failure Event",
        "surface_desc": "A documented miscommunication incident is publicly cited as the proximate cause of the cascade.",
        "private_label": "Pre-Incident Concern Log",
        "private_desc": "Private notes show junior staff had flagged the concern twice informally but routed through courtesy filters that muted urgency.",
        "norm_label": "Communication Breakdown Disconfirmation",
        "norm_desc": "Information technically reached the responsible party — the failure was in framing and escalation, not information transfer.",
        "coord_label": "Escalation Norm Gap",
        "coord_desc": "No formal escalation protocol existed that permitted junior staff to bypass courtesy norms for urgent safety concerns.",
        "anchor_from": "n2",
        "anchor_to": "n5",
    },
    "vigil_social_impossible_consensus_v1": {
        "belief_A_label": "Panel Member Private Priority Ordering",
        "belief_A_desc": "Members privately rank their priorities differently than their stated positions, having learned that direct statements trigger deadlock.",
        "belief_B_label": "Facilitator Consensus Model",
        "belief_B_desc": "Facilitator privately models the panel as having convergent interests; she is unaware of the private priority inversions.",
        "surface_label": "Visible Procedural Impasse Event",
        "surface_desc": "A procedural vote fails publicly and is documented as the cause of the panel's inability to reach decisions.",
        "private_label": "Side-Channel Alignment Record",
        "private_desc": "Informal pre-meeting conversations show members can agree on content privately but not in public session.",
        "norm_label": "Procedural Failure Disconfirmation",
        "norm_desc": "Identical procedural votes passed without incident in six prior panels with different member compositions.",
        "coord_label": "Public/Private Stance Divergence Map",
        "coord_desc": "Structured interviews reveal average panel member holds two publicly incompatible positions that are privately reconcilable.",
        "anchor_from": "n1",
        "anchor_to": "n5",
    },
    "vigil_social_facilitator_noise_v1": {
        "belief_A_label": "Facilitator Expertise Self-Model",
        "belief_A_desc": "Facilitator privately believes her content knowledge enhances mediation; she is unaware it signals side-taking to participants.",
        "belief_B_label": "Participant Neutrality Expectation",
        "belief_B_desc": "Participants privately expect procedural neutrality; they interpret content contributions as betrayal of the mediator role.",
        "surface_label": "Visible Content Intervention Event",
        "surface_desc": "A specific moment where the facilitator offered a substantive opinion is publicly identified as the turning point.",
        "private_label": "Trust Erosion Sequence Log",
        "private_desc": "Session recordings show participant disengagement beginning two sessions before the identified content intervention.",
        "norm_label": "Intervention Causality Disconfirmation",
        "norm_desc": "The visible content intervention occurred after trust erosion was already measurable — it was a symptom, not the cause.",
        "coord_label": "Role Boundary Communication Gap",
        "coord_desc": "No explicit role-scope agreement was established at program start; participants and facilitator held incompatible role models.",
        "anchor_from": "n2",
        "anchor_to": "n6",
    },
    "vigil_social_script_transfer_v1": {
        "belief_A_label": "Origin Program Tacit Context Model",
        "belief_A_desc": "Origin program staff privately know the protocol depends on a specific trust infrastructure; they believe documentation captures it.",
        "belief_B_label": "Receiving Program Implementation Belief",
        "belief_B_desc": "Receiving staff privately assume success = faithful procedure replication; they do not know about context dependencies.",
        "surface_label": "Visible Protocol Adoption Event",
        "surface_desc": "A formal adoption ceremony and documentation transfer is publicly celebrated as successful knowledge transfer.",
        "private_label": "Contextual Dependency Inventory",
        "private_desc": "Post-failure audit reveals the protocol assumed pre-existing peer trust networks built over three years at the origin site.",
        "norm_label": "Procedure Fidelity Disconfirmation",
        "norm_desc": "Receiving program achieved higher procedure fidelity scores than the origin site, yet outcomes diverged — fidelity was not the variable.",
        "coord_label": "Trust Infrastructure Gap",
        "coord_desc": "Receiving program's peer network was 18 months old vs. the 4-year network the protocol was calibrated against.",
        "anchor_from": "n3",
        "anchor_to": "n5",
    },
    "vigil_social_surveillance_checkin_v1": {
        "belief_A_label": "Clinician Supportive Intent Model",
        "belief_A_desc": "Clinician privately frames the check-in as care; she is unaware patients interpret question frequency as distrust monitoring.",
        "belief_B_label": "Patient Surveillance Interpretation",
        "belief_B_desc": "Patients privately interpret repeated check-ins as surveillance for risk escalation, suppressing honest disclosure.",
        "surface_label": "Visible Frequency Increase Event",
        "surface_desc": "A protocol change that doubled check-in frequency is publicly logged during the same period disclosure rates drop.",
        "private_label": "Patient Concealment Pattern",
        "private_desc": "Private session notes show patients began substituting reassuring responses for honest ones after the protocol change.",
        "norm_label": "Frequency-Disclosure Correlation Disconfirmation",
        "norm_desc": "Control wards with lower check-in frequency show higher disclosure rates — frequency and safety do not co-vary as expected.",
        "coord_label": "Check-In Framing Gap",
        "coord_desc": "The protocol specified frequency but not framing; patients received no explanation of the check-in's purpose or scope.",
        "anchor_from": "n2",
        "anchor_to": "n6",
    },
    "vigil_social_badge_printer_v1": {
        "belief_A_label": "Volunteer Coordinator Status Assumption",
        "belief_A_desc": "Coordinator privately assumes all volunteers share her view that badges are administrative; she underestimates status signaling.",
        "belief_B_label": "First-Time Attendee Badge Expectation",
        "belief_B_desc": "First-time attendees privately rely on badges for permission to approach senior attendees; without them, they self-exclude.",
        "surface_label": "Visible Technical Failure Event",
        "surface_desc": "The badge printer malfunction is publicly logged and framed as a minor logistical inconvenience without social consequence.",
        "private_label": "Self-Exclusion Behavior Log",
        "private_desc": "Post-event surveys show unbadged attendees rated the event as significantly less accessible despite uniform content.",
        "norm_label": "Logistical Framing Disconfirmation",
        "norm_desc": "Attendees who received handwritten badges reported nearly identical access experiences to printed-badge attendees — the signal, not the object, mattered.",
        "coord_label": "Status Signal Infrastructure Gap",
        "coord_desc": "No contingency protocol existed for badge failure; the coordinator had no alternative method of conferring visible permission.",
        "anchor_from": "n1",
        "anchor_to": "n5",
    },
    "vigil_social_anchored_read_v1": {
        "belief_A_label": "Support Specialist Prior-Case Anchoring",
        "belief_A_desc": "Specialist privately relies on a recent high-stakes case as interpretive frame; publicly she describes each case as assessed independently.",
        "belief_B_label": "Client Contextual Self-Presentation",
        "belief_B_desc": "Client privately edits self-presentation based on perceived specialist expectations, reducing diagnostic signal fidelity.",
        "surface_label": "Visible Case Similarity Event",
        "surface_desc": "A recent high-profile case is publicly discussed in team meetings during the same period mis-categorization rates rise.",
        "private_label": "Anchoring Sequence Log",
        "private_desc": "Case file timestamps show specialist's initial category assignment was made within 90 seconds of file opening, before evidence review.",
        "norm_label": "Case Similarity Disconfirmation",
        "norm_desc": "Mis-categorization affects cases with no surface similarity to the anchor case — similarity is not the operative variable.",
        "coord_label": "Review Checkpoint Absence",
        "coord_desc": "Protocol lacked a mandatory review gate between first impression and formal categorization; no structural interruption of anchoring.",
        "anchor_from": "n2",
        "anchor_to": "n6",
    },
    "vigil_social_new_slang_gap_v1": {
        "belief_A_label": "Senior Outreach Worker Language Model",
        "belief_A_desc": "Senior workers privately believe their rapport is based on relationship depth; they are unaware vocabulary drift has created a signal they cannot read.",
        "belief_B_label": "Youth Network Decoding Assumption",
        "belief_B_desc": "Young network members privately use slang as a trust filter; they interpret comprehension failure as evidence of outsider status.",
        "surface_label": "Visible Rapport Breakdown Event",
        "surface_desc": "A publicized miscommunication during an outreach encounter is logged as a training failure requiring individual correction.",
        "private_label": "Lexical Drift Timeline",
        "private_desc": "Community documentation shows three generational vocabulary shifts in four years; outreach vocabulary was last updated six years ago.",
        "norm_label": "Individual Rapport Disconfirmation",
        "norm_desc": "Workers with strong pre-existing individual relationships show the same comprehension gaps — the drift is systematic, not personal.",
        "coord_label": "Vocabulary Update Protocol Gap",
        "coord_desc": "No structured mechanism existed for outreach teams to document and integrate emerging community vocabulary.",
        "anchor_from": "n1",
        "anchor_to": "n5",
    },
    "vigil_social_private_channel_v1": {
        "belief_A_label": "Core Group Transparency Self-Assessment",
        "belief_A_desc": "Core group members privately know decisions are made in the private channel first; publicly they frame public meetings as decision venues.",
        "belief_B_label": "Peripheral Member Democratic Assumption",
        "belief_B_desc": "Peripheral members privately invest in public deliberation believing it is consequential; they are unaware of pre-decision patterns.",
        "surface_label": "Visible Public Deliberation Event",
        "surface_desc": "A well-attended public meeting is documented as evidence of the community's democratic process functioning normally.",
        "private_label": "Pre-Decision Alignment Record",
        "private_desc": "Private channel logs show all five major decisions of the past year were substantively settled before public meetings began.",
        "norm_label": "Public Meeting Efficacy Disconfirmation",
        "norm_desc": "Post-meeting vote outcomes deviated from pre-meeting public sentiment in zero of twelve cases — deliberation had no observable effect on outcomes.",
        "coord_label": "Legitimacy Perception Gap",
        "coord_desc": "Exit interviews from departing members cluster around 'feeling unheard' despite having spoken at every public meeting.",
        "anchor_from": "n2",
        "anchor_to": "n5",
    },
    "vigil_social_missing_safety_valve_v1": {
        "belief_A_label": "Alliance Leadership Pressure Absorption Belief",
        "belief_A_desc": "Leaders privately absorb member grievances informally; they believe this prevents escalation, unaware it also prevents structural resolution.",
        "belief_B_label": "Member Grievance Channel Assumption",
        "belief_B_desc": "Members privately believe leadership absorbs feedback for action; they are unaware absorbed grievances are not forwarded to governance.",
        "surface_label": "Visible Conflict Escalation Event",
        "surface_desc": "A public confrontation between two alliance members is documented as the proximate cause of the breakdown.",
        "private_label": "Informal Grievance Archive",
        "private_desc": "Leadership's informal notes contain 23 unresolved grievance threads predating the public confrontation by 14 months.",
        "norm_label": "Confrontation Causality Disconfirmation",
        "norm_desc": "The public confrontation participants had no shared prior grievance history; their clash was incidental to the structural pressure buildup.",
        "coord_label": "Grievance Routing Gap",
        "coord_desc": "No formal mechanism existed to convert informally absorbed grievances into governance agenda items.",
        "anchor_from": "n3",
        "anchor_to": "n6",
    },
    "vigil_social_foundational_roster_v1": {
        "belief_A_label": "Platform Coordinator Roster Assumption",
        "belief_A_desc": "Coordinator privately knows the founding roster is outdated; publicly she maintains it as authoritative to avoid renegotiation.",
        "belief_B_label": "Joining Organization Membership Belief",
        "belief_B_desc": "Newer organizations privately assume the roster reflects current influence distribution; they calibrate participation accordingly.",
        "surface_label": "Visible Founding Document Invocation",
        "surface_desc": "A coalition meeting publicly cites the founding roster to resolve a dispute over speaking order, presented as neutral procedure.",
        "private_label": "Roster Discrepancy Analysis",
        "private_desc": "Internal review shows 7 of 12 founding organizations have reduced activity by >60%; 4 high-activity non-founding members are unrepresented.",
        "norm_label": "Founding Authority Disconfirmation",
        "norm_desc": "The three most influential contributing organizations in the current period are all post-founding entrants not listed on the authoritative roster.",
        "coord_label": "Roster Update Protocol Gap",
        "coord_desc": "Coalition bylaws specified a roster review every 18 months; no review had occurred in four years.",
        "anchor_from": "n2",
        "anchor_to": "n6",
    },
    "vigil_social_delegated_trust_v1": {
        "belief_A_label": "Delegating Council Scope Assumption",
        "belief_A_desc": "Delegating council privately assumed the badge holder would interpret authority conservatively; they did not specify scope limits.",
        "belief_B_label": "Badge Holder Authority Interpretation",
        "belief_B_desc": "Badge holder privately interprets the delegation as broad; she makes commitments the delegating council did not authorize.",
        "surface_label": "Visible Commitment Event",
        "surface_desc": "A cross-coalition commitment is publicly announced by the badge holder during a summit, generating goodwill and expectations.",
        "private_label": "Authorization Scope Record",
        "private_desc": "The delegation memo specifies attendance authorization only; no language authorizes commitment-making on behalf of the coalition.",
        "norm_label": "Competence Disconfirmation",
        "norm_desc": "The badge holder's commitments were substantively sound — the breakdown was jurisdictional, not related to her judgment quality.",
        "coord_label": "Scope Negotiation Gap",
        "coord_desc": "No pre-summit briefing occurred to align scope interpretation between delegating council and badge holder.",
        "anchor_from": "n2",
        "anchor_to": "n5",
    },
    "vigil_social_shared_vendor_v1": {
        "belief_A_label": "Alliance Member A Vendor Reliability Model",
        "belief_A_desc": "Member A privately knows the shared mediator has capacity limits; publicly she vouches for vendor reliability to protect the alliance relationship.",
        "belief_B_label": "Alliance Member B Service Expectation",
        "belief_B_desc": "Member B privately relies on published availability commitments; she is unaware of the informal capacity negotiations occurring behind them.",
        "surface_label": "Visible Service Failure Event",
        "surface_desc": "A high-profile service disruption is publicly attributed to the vendor's technical failure and documented as a procurement lesson.",
        "private_label": "Capacity Negotiation Log",
        "private_desc": "Vendor's internal logs show Member A privately accepted reduced priority status in exchange for a fee discount six months prior.",
        "norm_label": "Technical Failure Disconfirmation",
        "norm_desc": "The service disruption occurred on schedule with the informal priority adjustment — the failure was contractual, not technical.",
        "coord_label": "Disclosure Protocol Gap",
        "coord_desc": "Alliance had no requirement for members to disclose bilateral vendor arrangements that affected shared service levels.",
        "anchor_from": "n3",
        "anchor_to": "n5",
    },
    "vigil_social_concentration_risk_v1": {
        "belief_A_label": "Program Coordinator Single-Interpreter Awareness",
        "belief_A_desc": "Coordinator privately knows the network depends on one interpreter for six language pairs; publicly she describes the network as resilient.",
        "belief_B_label": "Participant Interpreter Availability Assumption",
        "belief_B_desc": "Participants privately assume multiple interpreters exist for their language pair; they have no visibility into the concentration.",
        "surface_label": "Visible Interpreter Absence Event",
        "surface_desc": "The critical interpreter's leave of absence is publicly documented as the proximate cause of three failed apprenticeship placements.",
        "private_label": "Dependency Concentration Map",
        "private_desc": "Internal records show 78% of successful cross-border placements in the past two years flowed through this single interpreter.",
        "norm_label": "Individual Absence Disconfirmation",
        "norm_desc": "The interpreter's absence was temporary; the network had no alternative routing for the 78% of flows she handled regardless of duration.",
        "coord_label": "Redundancy Planning Gap",
        "coord_desc": "No succession or cross-training plan existed for language pairs handled exclusively by the single interpreter.",
        "anchor_from": "n2",
        "anchor_to": "n5",
    },
    "vigil_social_wrong_target_policy_v1": {
        "belief_A_label": "Policy Author Population Model",
        "belief_A_desc": "Policy author privately based design on a 2018 survey; publicly the policy is described as responsive to current community needs.",
        "belief_B_label": "Current Community Self-Description",
        "belief_B_desc": "Current community members privately know they differ from the policy's implied population; publicly they adapt behavior to appear compliant.",
        "surface_label": "Visible Compliance Metric Success Event",
        "surface_desc": "Quarterly compliance metrics show the policy is being followed at high rates, publicly cited as evidence of policy effectiveness.",
        "private_label": "Behavioral Adaptation Log",
        "private_desc": "Ethnographic observation reveals community members performing compliance rituals without the underlying behavior change the policy targeted.",
        "norm_label": "Metric Validity Disconfirmation",
        "norm_desc": "The policy's target outcome (behavior change) shows no measurable movement despite compliance metrics at 94%.",
        "coord_label": "Population Drift Documentation Gap",
        "coord_desc": "No mechanism existed to update policy assumptions as community composition shifted over seven years.",
        "anchor_from": "n1",
        "anchor_to": "n6",
    },
    "vigil_social_revolving_allegiance_v1": {
        "belief_A_label": "Council Chair Consultant Neutrality Model",
        "belief_A_desc": "Chair privately believes the consultant's cross-organization relationships enhance credibility; she does not model allegiance as variable.",
        "belief_B_label": "Council Member Consultant Trust Model",
        "belief_B_desc": "Members privately track which organizations the consultant bills; they interpret her recommendations through a current-client filter.",
        "surface_label": "Visible Consultant Recommendation Event",
        "surface_desc": "A formal recommendation report is publicly presented and initially praised, becoming the focus of subsequent trust questions.",
        "private_label": "Billing Relationship Timeline",
        "private_desc": "Billing records show the consultant's primary client shifted from Group A to Group B three months before the recommendation was issued.",
        "norm_label": "Recommendation Quality Disconfirmation",
        "norm_desc": "Independent expert review rated the recommendation's technical quality as sound; the trust failure was relational, not substantive.",
        "coord_label": "Conflict Disclosure Gap",
        "coord_desc": "Council's engagement terms required no disclosure of concurrent client relationships; no conflict-check mechanism existed.",
        "anchor_from": "n3",
        "anchor_to": "n5",
    },
    "vigil_social_manufactured_discovery_v1": {
        "belief_A_label": "Board Member Procedural Belief",
        "belief_A_desc": "Board members privately know the 'discovery' was anticipated; publicly they perform surprise to preserve the appearance of independent process.",
        "belief_B_label": "Public Stakeholder Process Trust",
        "belief_B_desc": "Public stakeholders privately expected genuine deliberation; they are unaware the outcome was settled before the process began.",
        "surface_label": "Visible Deliberation Process Event",
        "surface_desc": "Public hearings and community consultations are documented as thorough; the process is publicly cited as exemplary.",
        "private_label": "Pre-Process Decision Evidence",
        "private_desc": "Internal correspondence predating the public process contains the final recommendation language verbatim.",
        "norm_label": "Process Authenticity Disconfirmation",
        "norm_desc": "Community input diverged significantly from the final recommendation in 11 of 13 categories — input had no observable effect on outcome.",
        "coord_label": "Legitimacy Infrastructure Gap",
        "coord_desc": "No independent process auditor role existed; board self-assessed procedural compliance without external verification.",
        "anchor_from": "n2",
        "anchor_to": "n6",
    },
    "vigil_social_definition_gap_v1": {
        "belief_A_label": "Oversight Body Definition Authority Belief",
        "belief_A_desc": "Oversight staff privately know the definition is narrow by design; publicly they describe it as the 'natural scope' of their mandate.",
        "belief_B_label": "Affected Population Scope Assumption",
        "belief_B_desc": "Affected parties privately believe their cases fall within scope; they invest significant effort in documentation before the definition gap is revealed.",
        "surface_label": "Visible Reporting Compliance Event",
        "surface_desc": "Oversight body publishes a compliance report showing no violations, widely cited as evidence the system is functioning.",
        "private_label": "Excluded Category Inventory",
        "private_desc": "Internal categorization logs show 34% of reported cases were reclassified as out-of-scope during intake, before investigation.",
        "norm_label": "Compliance Report Disconfirmation",
        "norm_desc": "The compliance report accurately counted cases within the narrow definition — absence of violations reflects definition design, not absence of harm.",
        "coord_label": "Definition Transparency Gap",
        "coord_desc": "Scope definition was published in technical annexes; no plain-language summary existed for affected populations or referral organizations.",
        "anchor_from": "n2",
        "anchor_to": "n5",
    },
    "vigil_social_pipeline_cascade_v1": {
        "belief_A_label": "Senior Mentor Network Self-Sufficiency Belief",
        "belief_A_desc": "Senior mentors privately rely on informal referral chains to find early-career candidates; publicly they describe the system as open and accessible.",
        "belief_B_label": "Early-Career Researcher Access Model",
        "belief_B_desc": "Researchers outside the informal network privately experience access as blocked; they publicly attribute non-selection to merit gaps.",
        "surface_label": "Visible Output Decline Event",
        "surface_desc": "A decline in collaborative publications is publicly attributed to reduced research funding in the same period.",
        "private_label": "Informal Referral Dependency Audit",
        "private_desc": "Review of successful mentorship placements shows 89% were initiated through informal referrals from a shrinking senior network.",
        "norm_label": "Funding Causality Disconfirmation",
        "norm_desc": "Funding allocation data shows no reduction in the relevant research area during the output decline period.",
        "coord_label": "Formal Access Channel Gap",
        "coord_desc": "No open application pathway existed for mentorship; all entry points required a warm introduction from network-adjacent individuals.",
        "anchor_from": "n3",
        "anchor_to": "n6",
    },
}


def expand_social_scenario(s: dict, ext: dict) -> dict:
    """Add 6 new nodes and 6 new edges to an existing social scenario dict."""
    existing_nodes = s.get("nodes", [])
    existing_edges = s.get("edges", [])

    # Find the "outcome" node id to use as a downstream anchor
    outcome_id = next(
        (n["id"] for n in existing_nodes if n.get("kind") == "outcome"), None
    ) or existing_nodes[-1]["id"]

    # Pick upstream anchor (first agent_group or n1)
    anchor_a_id = ext.get("anchor_from") or next(
        (n["id"] for n in existing_nodes if n.get("kind") == "agent_group"), "n1"
    )
    anchor_b_id = ext.get("anchor_to") or outcome_id

    new_nodes = [
        {
            "id": "n_belief_A",
            "label": ext["belief_A_label"],
            "description": ext["belief_A_desc"],
            "kind": "belief_state",
            "visibility": "hidden",
        },
        {
            "id": "n_belief_B",
            "label": ext["belief_B_label"],
            "description": ext["belief_B_desc"],
            "kind": "belief_state",
            "visibility": "hidden",
        },
        {
            "id": "n_surface_event",
            "label": ext["surface_label"],
            "description": ext["surface_desc"],
            "kind": "event",
            "visibility": "visible",
        },
        {
            "id": "n_private_comm",
            "label": ext["private_label"],
            "description": ext["private_desc"],
            "kind": "evidence",
            "visibility": "hidden",
        },
        {
            "id": "n_norm_conflict",
            "label": ext["norm_label"],
            "description": ext["norm_desc"],
            "kind": "disconfirmation",
            "visibility": "discoverable",
        },
        {
            "id": "n_coord_gap",
            "label": ext["coord_label"],
            "description": ext["coord_desc"],
            "kind": "evidence",
            "visibility": "discoverable",
        },
    ]

    new_edges = [
        # Surface event is visible — it co-occurs with the outcome (red herring)
        {"source": "n_surface_event", "target": anchor_b_id, "relation": "appears_to_cause"},
        # Investigating the surface event leads to private communications
        {"source": "n_surface_event", "target": "n_private_comm", "relation": "prompts_investigation"},
        # Private comm reveals the disconfirmation of the obvious hypothesis
        {"source": "n_private_comm", "target": "n_norm_conflict", "relation": "supports"},
        # Coordination gap: reachable from the outcome anchor
        {"source": anchor_b_id, "target": "n_coord_gap", "relation": "explained_by"},
        # Belief states: reachable from the upstream anchor node
        {"source": anchor_a_id, "target": "n_belief_A", "relation": "holds_private_belief"},
        {"source": anchor_a_id, "target": "n_belief_B", "relation": "holds_private_belief"},
    ]

    result = dict(s)
    result["nodes"] = existing_nodes + new_nodes
    result["edges"] = existing_edges + new_edges
    return result


def main() -> None:
    with open(SOCIAL_FILE) as f:
        raw = json.load(f)

    scenarios: list[dict] = raw if isinstance(raw, list) else raw.get("scenarios", [])

    expanded = []
    missing_ext = []
    for s in scenarios:
        sid = s.get("scenario_id", "")
        ext = EXTENSIONS.get(sid)
        if ext is None:
            missing_ext.append(sid)
            expanded.append(s)  # keep as-is
        else:
            expanded.append(expand_social_scenario(s, ext))

    if missing_ext:
        print(f"WARNING: no extension data for {len(missing_ext)} scenarios: {missing_ext}")

    # Verify node counts
    counts = [(s.get("scenario_id", "?"), len(s.get("nodes", []))) for s in expanded]
    failed = [(sid, n) for sid, n in counts if n < 12]
    if failed:
        for sid, n in failed:
            print(f"FAIL: {sid} has {n} nodes — need ≥12")
        raise SystemExit(1)

    out = expanded if isinstance(raw, list) else {"scenarios": expanded}
    with open(SOCIAL_FILE, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Written {len(expanded)} social scenarios to {SOCIAL_FILE}")
    print(f"Node counts: min={min(n for _, n in counts)}, max={max(n for _, n in counts)}")
    print(f"All {len(expanded)} scenarios have ≥12 nodes. ✓")


if __name__ == "__main__":
    main()
