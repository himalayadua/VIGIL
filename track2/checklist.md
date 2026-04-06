# Track 2 Scenario Validation Checklist

This document is the working validation checklist for deciding whether a proposed Vigil scenario genuinely measures `Track 2: Attention` in the DeepMind AGI framework, rather than long-context recall, static graph QA, memory load, planning depth, or generic reasoning difficulty.

It is meant to be used before scenario generation, during scenario review, and before benchmark acceptance.

## Purpose

This checklist is designed to answer one core question:

`Does this scenario force the model to allocate limited focus well — choosing what to attend to, what to ignore, when to persist, and when to reorient — under realistic competition for attention during the episode?`

If the answer is no, then it is not a strong Track 2 scenario.

## How To Use This Checklist

- Treat `Core Requirements` as mandatory unless there is a very strong reason not to.
- Treat `Strong Preferred Properties` as features that materially improve scenario quality and benchmark validity.
- Treat `Scenario-Type-Specific Checks` as required only when the scenario claims to measure that specific attention sub-ability or task family.
- Use `Rejection Criteria` as hard blockers.
- A scenario does not need to satisfy every preferred property, but it should satisfy most of the core requirements and produce clearly interpretable attention behavior.

## 1. Core Requirements

### 1.1 Attention-As-Bottleneck

- Does the scenario create a real attentional bottleneck rather than merely more content?
- Is there more available information than should be comfortably processed all at once?
- Does success depend on choosing where to focus, not just eventually reading everything?
- Would a perfect memory but poor focus policy still struggle?
- Would a good solver need to decide:
  - what to inspect first
  - what to defer
  - what to ignore
  - what to revisit
  - what to stop tracking

### 1.2 Blind Framing

- Does the model receive a genuine task rather than an exam-style prompt about attention?
- Is the model not told which cues are the important ones?
- Is the model not warned that distractors are present as part of the opening framing?
- Does the environment feel like a real problem rather than a test with hints?
- Would good attention emerge from the task demands themselves rather than from explicit meta-instructions?

### 1.3 Limited Capacity Under Competition

- Are there multiple competing cues, streams, or regions that plausibly deserve attention?
- Are some cues relevant, some irrelevant, and some only temporarily relevant?
- Is competition for focus essential rather than decorative?
- Does the task remain non-trivial even if the model can process text quickly?
- Can the scenario distinguish efficient focus allocation from indiscriminate scanning?

### 1.4 Attention Versus Memory / Reasoning / Planning

- Is the main challenge attentional rather than a memory-storage challenge?
- Is the scenario harder than simply remembering one key fact?
- Is failure more about missing, mis-prioritizing, or over-following cues than about deep abstract reasoning?
- If the model had perfect cue selection, would the remaining reasoning burden be moderate rather than dominant?
- Is the scenario prevented from drifting into:
  - `Track 1: Learning` because the main challenge is hidden-rule discovery
  - `Track 3: Executive Function` because the main challenge is long-horizon goal management or inhibition
  - `Track 4: Metacognition` because the main challenge is uncertainty monitoring
  - `Track 5: Social Cognition` because the main challenge is inferring mental states

### 1.5 Human Solvability

- Is the scenario human-solvable with the same interface constraints?
- Does the difficulty come from attentional competition rather than arbitrary confusion?
- Could a human baseline reasonably be collected for this scenario?
- Would human traces be meaningfully comparable to model traces?
- Would humans understand what to do without special prior domain expertise?

## 2. Environment Requirements

### 2.1 Graph As Environment

- Is the graph a stateful environment for action, not just a graph-shaped document?
- Does traversal materially affect what the agent can see, verify, and miss?
- Does the order of inspection matter?
- Does the choice of what to inspect next matter?
- Does the graph support meaningful action primitives such as:
  - exploration
  - inspection
  - zooming / expansion
  - switching streams or regions
  - backtracking
  - marking or prioritizing targets
  - submission
  - stopping

### 2.2 Partial Observability

- Is the whole graph hidden or only partially visible at the start?
- Is information revealed locally and selectively?
- Must the agent deliberately choose what to inspect and what to ignore?
- Is global structure non-trivial to reconstruct from the opening state?
- Is partial observability essential to the scenario rather than decorative?

### 2.3 Competing Cue Structure

- Does the graph contain:
  - relevant cues
  - plausible distractors
  - low-value regions
  - temporarily useful nodes
  - rare critical alerts
  - false alarms
  - stale or outdated signals
- Are critical cues distributed so that attention placement matters?
- Is there a meaningful difference between shallow scanning and disciplined focus?
- Are there regions that are visually or structurally salient but task-irrelevant?

### 2.4 Stateful Attention Consequences

- Do attentional choices have consequences for later performance?
- Can inspecting the wrong thing waste time, steps, or decision budget?
- Can missing a cue force recovery or reorientation later?
- Can over-attending to one stream cause neglect elsewhere?
- If the scenario claims to measure vigilance or reorientation, are those behaviors visible in the trace?

## 3. Attention-Theory Alignment

### 3.1 DeepMind Attention Definition Alignment

- Does the scenario match the idea of focusing limited cognitive resources on specific aspects of perceptual stimuli, information, or thoughts?
- Does the scenario require balancing narrow goal focus with responsiveness to unexpected changes?
- Does it test attention rather than simple retrieval from a fully exposed context?
- Does it reveal whether the agent can allocate focus efficiently under competition?

### 3.2 Evidence Of Real Attention Behavior

- Would a good score be evidence of disciplined focus allocation rather than luck or brute-force inspection?
- Is the attention signal visible in the model's actions?
- Can the scenario reveal the difference between:
  - lucky cue discovery
  - indiscriminate scanning
  - position-based heuristics
  - genuine selective focus
  - disciplined reorientation

### 3.3 Attention Capacity Over Raw Context Length

- Does the scenario measure effective use of attention under load rather than merely testing maximum context length?
- Is increased difficulty tied to competing information, prioritization pressure, or placement effects rather than only longer text?
- Does the scenario avoid rewarding a fixed heuristic like "always inspect the first and last items"?
- Is cue position varied so the task cannot be solved by stable positional biases?

## 4. Attention Sub-Ability Coverage

Every scenario should either isolate one sub-ability cleanly or intentionally combine several in a controlled and explainable way.

### 4.1 Attention Capacity

- Does the scenario vary how many active items, streams, or candidates must be monitored at once?
- Can information load be increased in a controlled way?
- Does performance degrade in interpretable ways as attentional load rises?
- Is the task still mainly about focus allocation rather than becoming a pure memory test?
- If multimodal, can capacity pressure be varied separately by channel?

### 4.2 Sustained Attention

- Does the scenario require maintaining attention over time rather than making one early good choice?
- Are critical cues sometimes rare, delayed, or intermittent?
- Can the model front-load all useful work, or must it remain vigilant throughout the episode?
- Can performance be examined as a function of time-on-task?
- Does the scenario reveal:
  - drift
  - omission
  - late-task degradation
  - reduced monitoring quality

### 4.3 Selective Attention / Perceptual Inhibition

- Are distractors plausible rather than random noise?
- Are distractors semantically, structurally, or temporally similar enough to the target to be tempting?
- Is the model required to ignore irrelevant but salient cues?
- Is there a measurable penalty for following off-path information?
- Can distractor density, similarity, and placement be systematically varied?

### 4.4 Attention Shifting

- Does relevance move during the task?
- Can the currently important stream or region change?
- Must the model shift focus from one target to another at the right time?
- Is reorientation too easy because the new cue is explicitly flagged?
- Can the scenario reveal:
  - delayed switching
  - sticky fixation
  - over-switching
  - costly but appropriate reallocation

### 4.5 Stimulus-Driven Attention

- Are there unexpected events or changes that deserve immediate attention?
- Are some salient events true alerts while others are false alarms?
- Can the model distinguish between task-relevant novelty and irrelevant novelty?
- Does the scenario require interrupting the current focus when warranted?
- Is stimulus-driven capture part of the design rather than accidental noise?

## 5. Cue Competition And Reorientation Design

### 5.1 Relevant Versus Irrelevant Cue Design

- Is there a clear distinction between:
  - goal-relevant cues
  - temporarily irrelevant cues
  - permanently irrelevant cues
  - misleadingly salient cues
- Are relevant cues sometimes subtle rather than always louder than distractors?
- Can a bad focus policy appear superficially reasonable?
- Are cue relations rich enough to make prioritization non-trivial?

### 5.2 Reorientation Pressure

- Is there at least one meaningful moment when the model should reorient attention?
- Is that moment behaviorally reachable through normal play?
- Is the reorientation pressure stronger than merely "something else also exists"?
- Can the trace show whether the model noticed and responded to the change?

### 5.3 False Alarm Resistance

- Does the scenario include distractors that look urgent but are not?
- Can the benchmark measure whether the model:
  - chased flashy but irrelevant events
  - ignored true alerts
  - overreacted to novelty
  - remained too rigidly locked onto the original target
- Are false alarms informative rather than filler?

## 6. Hidden Signal Design

### 6.1 Hidden-Relevance Quality

- Is there an important relevance structure that is not obvious from surface appearance?
- Are the most important nodes absent from the most obvious first-glance path?
- Does the graph reward discovering where attention should go rather than merely following surface salience?
- Could hidden relevance take forms such as:
  - delayed importance
  - cross-node dependency
  - role reversal of a previously irrelevant stream
  - low-salience but high-value evidence
  - context-dependent priority changes

### 6.2 Surface Versus Depth

- Are the important facts absent from the most obvious surface nodes?
- Is the scenario weaker because all essential cues are highlighted too early?
- Does the graph reward moving from superficial salience to task-grounded relevance?

## 7. Path And Behavior Scoring Readiness

### 7.1 Path Quality

- Can the scenario distinguish disciplined scanning from wandering?
- Can it detect whether the model inspected the right kinds of nodes?
- Can it identify whether the model followed relevant streams rather than merely visible ones?
- Can it distinguish premature commitment from healthy exploratory coverage?

### 7.2 Decision Efficiency

- Is there a notion of near-optimal or at least efficient attention allocation?
- Can the scenario distinguish efficient focus from exhaustive search?
- Does the graph structure make wasted actions visible?
- Can the benchmark score switch cost, inspection cost, or wasted re-checking?

### 7.3 Justification Quality

- Can the model's explanation be checked against what it actually attended to?
- Does the justification require citing relevant cues rather than writing a vague summary?
- Can the model explain why distractors were ignored or deprioritized?
- Can fabricated or unsupported explanations be penalized?

### 7.4 Behavioral Signatures

- Does the scenario produce interpretable signatures such as:
  - distractor chasing
  - over-broad scanning
  - narrow tunnel vision
  - late-task vigilance drop
  - missed rare alert
  - false-alarm pursuit
  - delayed reorientation
  - excessive switching
  - sticky fixation
  - position bias
- Would two models with the same final answer be distinguishable by trace quality?

### 7.5 Stopping Behavior

- Is it possible to tell whether the model stopped too early, too late, or appropriately?
- Does the scenario contain enough signal to assess rational stopping?
- Can the benchmark reward stopping after sufficient cue coverage rather than endless scanning?

## 8. Evidence Grounding

### 8.1 Evidence Coverage

- Are there critical cues, nodes, or streams that should appear in successful trajectories?
- Can the scenario verify whether these were actually attended to?
- Is the minimum useful evidence set identifiable?
- Can successful behavior be separated from lucky guessing?

### 8.2 Anti-Storytelling Controls

- Can the model be penalized for citing signals it never inspected?
- Can the justification be grounded in the traversal log rather than post-hoc storytelling?
- Is there a clean mapping from attended evidence to final explanation?
- Can unsupported claims of vigilance, awareness, or prioritization be penalized?

## 9. Transfer And Generalization

### 9.1 Transfer Support

- Can the same attentional challenge be tested under:
  - a new graph layout
  - renamed entities
  - different distractor skins
  - changed cue positions
  - altered salience patterns
  - new domain framing
- Would success survive these changes if the model actually learned a good attention policy?

### 9.2 Generalization Testing

- Can the scenario family distinguish cue-tracking skill from memorized template-following?
- Does surface variation break stable positional or stylistic heuristics?
- Is transfer distance intentional rather than arbitrary?

## 10. Multi-Domain Design Controls

### 10.1 Controlled Multi-Domain Use

- If the scenario is multi-domain, do the domains share a common attentional bottleneck?
- Does domain diversity improve validity rather than create unrelated variety?
- Is the scenario family coherent rather than a grab-bag of puzzles?

### 10.2 Stable Mechanic, Variable Surface

- Is the core attentional challenge stable across domain variants?
- Do surface changes preserve the same underlying attention problem?
- Would shortcutting on one domain fail on another domain skin?

## 11. Difficulty Design

### 11.1 Good Difficulty Dimensions

- Does difficulty vary along useful dimensions such as:
  - number of competing cues
  - distractor similarity
  - rare-target frequency
  - time-on-task duration
  - cue relocation frequency
  - false-alarm salience
  - observation budget
  - switching cost
  - position neutrality
  - multi-stream monitoring pressure

### 11.2 Bad Difficulty Dimensions

- Is difficulty being increased mainly by:
  - adding more text
  - adding arbitrary clutter
  - hiding the only relevant cue unfairly
  - making labels deliberately confusing without cognitive value
  - requiring humans to fail for UI reasons rather than attention reasons
- If yes, redesign the difficulty curve.

## 12. Shortcut Resistance

### 12.1 Surface Shortcut Checks

- Is the critical cue not consistently located in privileged positions?
- Is the answer not leaked in the entry node or first hop?
- Is the solution not inferable from the most visually or structurally salient object alone?
- Is the domain framing not giving away where to look?
- Are there no stable lexical markers that reveal relevance too directly?

### 12.2 Structural Shortcut Checks

- Are graph ordering, naming, and layout safely changeable?
- Are cue positions perturbable?
- Are near-miss variants possible?
- Can multiple equivalent renderings preserve the same attention task?
- Is the model prevented from memorizing a repeated graph-template-to-focus-policy mapping?

## 13. Minimum Acceptance Checklist

A scenario should usually be accepted only if the answer is `yes` to most of the following:

- Does it test attention rather than recall, planning, or learning?
- Does it contain a real attentional bottleneck?
- Is the framing blind?
- Is the graph stateful and interactive?
- Is partial observability essential?
- Are there multiple competing cues?
- Are plausible distractors present?
- Is there at least one meaningful reorientation demand?
- Is traversal behavior meaningful and scoreable?
- Can final correctness be separated from attentional quality?
- Are there critical cues or evidence nodes?
- Is it human-solvable?
- Can it support transfer or perturbation variants?
- Does it isolate or intentionally combine attention sub-abilities?
- Does it resist shortcutting?
- Does it produce diagnostic behavioral signatures?

## 14. Strong Preferred Properties

These are not mandatory for every scenario, but they make scenarios materially stronger:

- balanced true-alert and false-alert design
- meaningful reorientation moments
- sustained-attention pressure over time
- distractor taxonomy with controlled ablations
- transfer-ready variants
- multi-domain reskinning with stable mechanics
- interpretable attentional failure modes
- rational stopping opportunities
- position-neutral cue placement
- measurable switch cost

## 15. Scenario-Type-Specific Notes

These should be used when a scenario intentionally targets a particular family of attention tasks.

### 15.1 Long-Context Or Multi-Stream Monitoring Worlds

- Does the scenario force the model to allocate attention across multiple streams rather than just retrieve one needle?
- Is relevant information position-neutral across variants?
- Does success require using attended information, not just spotting it?

### 15.2 Alerting / Monitoring / Watchstanding Tasks

- Are there rare but important events to detect?
- Does time-on-task matter?
- Are false alarms realistic and informative?
- Can vigilance decrements be observed?

### 15.3 Distractor-Rich Operational Worlds

- Are distractors plausible and integrated into the task world?
- Can the benchmark distinguish good filtering from superficial search?
- Are off-path but tempting cues behaviorally measurable?

### 15.4 Dynamic Priority / Reorientation Tasks

- Can task relevance shift mid-episode?
- Is appropriate switching rewarded and sticky fixation penalized?
- Are unexpected changes natural rather than artificial test signals?

### 15.5 Multi-Channel Or Multi-Modal Attention Tasks

- Are channels genuinely competing for attention?
- Can the system over-allocate to one channel and miss another?
- Is cross-channel prioritization observable and scoreable?

## 16. Rejection Criteria

Reject a scenario if one or more of the following is true:

- It has no real attentional bottleneck.
- All relevant information is obvious on first inspection.
- Distractors are trivial junk rather than plausible alternatives.
- The task is basically static QA.
- Success depends mostly on memory or reasoning depth rather than focus allocation.
- Partial observability is decorative rather than essential.
- Traversal barely matters.
- There is no meaningful reorientation demand anywhere in the family.
- Relevant cues always sit in privileged positions.
- The explanation can be written without inspecting key cues.
- A summarizer or search helper can collapse the task into plain retrieval.
- There are no interpretable behavioral signatures.
- Shortcutting is likely and not addressed.
- Humans would fail for arbitrary reasons rather than because the attentional problem is hard.
- Transfer would likely fail because the model is learning a template rather than a robust attention policy.

## 17. Compressed Scenario Gate

If we need a fast scenario screen, use this shorter gate:

- real attentional bottleneck
- blind framing
- partial observability
- multiple competing cues
- plausible distractors
- meaningful reorientation
- evidence-grounded explanation
- measurable attentional behavior
- human solvability
- transfer potential
- shortcut resistance
- interpretable attention failure modes

If a candidate scenario fails multiple items in this short gate, it should not move forward.

## Research Grounding

This checklist was shaped using the following sources and ideas:

- Google DeepMind, *Measuring Progress Toward AGI: A Cognitive Framework* (2026)
- Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (TACL 2024)
- Hsieh et al., *RULER: What's the Real Context Size of Your Long-Context Language Models?* (2024)
- Modarressi et al., *NoLiMa: Long-Context Evaluation Beyond Literal Matching* (2025)
- Shi et al., *Large Language Models Can Be Easily Distracted by Irrelevant Context* (2023)
- Yang et al., *How Is LLM Reasoning Distracted by Irrelevant Context? An Analysis Using a Controlled Benchmark* (EMNLP 2025)

The checklist is intended as a scenario-design and scenario-validation tool, not as a direct benchmark specification.
