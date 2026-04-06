# Track 1 Scenario Validation Checklist

This document is the working validation checklist for deciding whether a proposed Vigil scenario genuinely measures `Track 1: Learning` in the DeepMind AGI framework, rather than recall, prompt-following, static graph reasoning, or long-context retrieval.

It is meant to be used before scenario generation, during scenario review, and before benchmark acceptance.

## Purpose

This checklist is designed to answer one core question:

`Does this scenario force the model to acquire something new through interaction, evidence, instruction, or feedback during the episode?`

If the answer is no, then it is not a strong Track 1 scenario.

## How To Use This Checklist

- Treat `Core Requirements` as mandatory unless there is a very strong reason not to.
- Treat `Strong Preferred Properties` as features that materially improve scenario quality and benchmark validity.
- Treat `Scenario-Type-Specific Checks` as required only when the scenario claims to measure that specific learning sub-ability.
- Use `Rejection Criteria` as hard blockers.
- A scenario does not need to satisfy every preferred property, but it should satisfy most of the core requirements and produce clearly interpretable learning behavior.

## 1. Core Requirements

### 1.1 Learning-Through-Interaction

- Does the scenario test learning through interaction rather than answer retrieval?
- Does the scenario require the model to acquire something new during the episode?
- Is the thing to be acquired one of the following:
  - a hidden rule
  - a causal mechanism
  - a latent structure
  - a procedural policy
  - a strategy
  - a vocabulary or protocol
  - a relationship between events, states, or entities
- Does success require updating behavior from evidence, not just producing a plausible explanation?
- Would the scenario still be meaningful if the final answer text were hidden and only the behavior trace were available?

### 1.2 Blind Framing

- Does the model receive a task rather than an exam-style prompt?
- Is the model not told what exact learning faculty is being tested?
- Is the hidden rule or target concept not explicitly named in the opening context?
- Does the environment feel like a real problem to solve rather than a test with hints?

### 1.3 Novelty And Controlled Priors

- Is the scenario resistant to being solved by pretraining recall alone?
- Does the scenario control for prior knowledge exposure as much as reasonably possible?
- Does the scenario avoid relying on familiar domain tropes that reveal the answer?
- Does the scenario use one or more of the following:
  - invented entities
  - synthetic vocabularies
  - hidden causal structures
  - procedurally generated graph variants
  - novel combinations of known mechanics
- Could a model plausibly say "I have seen this exact trope before" and shortcut the task?
- If yes, can the scenario be redesigned to break that shortcut?

### 1.4 Learning Versus Memory

- Does the scenario distinguish between failure to learn and failure to retain?
- Is the task harder than just holding one fact in working memory?
- Does passing require one or more of the following:
  - belief revision
  - policy revision
  - abstraction from repeated evidence
  - transfer from one part of the graph to another
- Can the scenario show whether the model:
  - formed an initial hypothesis
  - encountered contradictory evidence
  - revised its hypothesis or policy

### 1.5 Human Solvability

- Is the scenario human-solvable with the same interface constraints?
- Does the difficulty come from learnable structure rather than arbitrary obscurity?
- Could a human baseline reasonably be collected for this scenario?
- Would human paths be meaningfully comparable to model paths?

## 2. Environment Requirements

### 2.1 Graph As Environment

- Is the graph a stateful environment for action, not just a graph-shaped document?
- Does traversal materially affect what the agent can know and do?
- Does the order of inspection matter?
- Does the choice of what to inspect next matter?
- Does the graph support meaningful action primitives such as:
  - exploration
  - inspection
  - expansion
  - backtracking
  - hypothesis submission
  - stopping

### 2.2 Partial Observability

- Is the whole graph hidden at the start?
- Is information revealed locally and selectively?
- Must the agent deliberately choose what to inspect and what to ignore?
- Is global structure non-trivial to reconstruct from the opening state?
- Is partial observability essential to the scenario rather than decorative?

### 2.3 Meaningful Structure

- Does the graph contain:
  - local evidence
  - distractors
  - dead ends
  - latent dependencies
  - confirmatory paths
  - disconfirmatory paths
- Are important facts distributed across the graph so that navigation matters?
- Is there a meaningful difference between shallow exploration and good exploration?

### 2.4 Stateful Consequences

- Do actions have consequences for what becomes known, available, or plausible?
- Can earlier choices shape later options, costs, or interpretations?
- Does the environment support the accumulation of evidence over time?
- If the scenario claims to measure adaptation, is adaptation behaviorally visible in the trace?

## 3. Learning-Theory Alignment

### 3.1 DeepMind Learning Definition Alignment

- Does the scenario match the idea of acquiring new knowledge, skill, or behavior through experience, study, or instruction?
- Does the scenario test learning rather than stored competence?
- Does it reward adaptation within the episode?
- Does it reveal whether the agent can become more capable after exposure to evidence, demonstrations, or feedback?

### 3.2 Fluid Intelligence Over Crystallized Intelligence

- Does the scenario reward skill-acquisition efficiency rather than raw stored knowledge?
- Does difficulty come from:
  - novelty
  - hidden structure
  - abstraction
  - uncertainty
  - transfer distance
  - revision pressure
- Does difficulty avoid depending mainly on:
  - huge context length
  - token clutter
  - obscure trivia
  - heavy jargon
  - arbitrary naming confusion

### 3.3 Evidence Of Real Learning

- Would a good score be evidence of actual learning behavior rather than prompt sensitivity?
- Is the learning signal visible in the model's actions?
- Can the scenario reveal the difference between:
  - lucky guessing
  - static competence
  - shallow pattern matching
  - genuine adaptation

## 4. Learning Sub-Ability Coverage

Every scenario should either isolate one sub-ability cleanly or intentionally combine several in a controlled and explainable way.

### 4.1 Concept Formation

- Is there a hidden schema, category, or latent organizing principle to infer?
- Does success require abstraction rather than instance matching?
- Can the model generalize the learned concept to a new part of the graph or a new graph instance?
- Is the target concept absent by name from the surface prompt?

### 4.2 Associative Learning

- Do repeated co-occurrences or temporal relationships matter?
- Must the model learn relationships across events, states, or entities?
- Does the scenario require updating a belief about what tends to happen with what?
- Are those relationships stable enough to be learnable but not trivially exposed?

### 4.3 Reinforcement Learning

- Do action consequences materially affect future success?
- Does the environment provide meaningful success and failure feedback?
- Can the model improve its policy by noticing what actions pay off or fail?
- Is the scenario measuring consequence-sensitive adaptation within the task rather than assuming true parameter-updating RL?

### 4.4 Observational Learning

- Are demonstrations, traces, examples, or prior trajectories available?
- Must the model infer strategy or latent rule from observation?
- Would simple path copying fail on transfer?
- Does the scenario reward extracting the underlying policy rather than mimicking surface form?

### 4.5 Procedural Learning

- Does the scenario reward improved execution after exposure or feedback?
- Can the model become more efficient after discovering the correct procedure?
- Is procedural competence visible in fewer steps, fewer errors, or cleaner traversal?
- Does the scenario measure know-how rather than just factual description of a procedure?

### 4.6 Language Learning

- Does the scenario include a novel vocabulary, protocol, command grammar, symbolic language, or API-like system?
- Must the model infer how the symbolic system works from interaction, examples, or feedback?
- Is correct usage required for success?
- Is the symbolic system novel enough to reduce contamination risk?

## 5. Disconfirmation And Revision

### 5.1 Disconfirmation Pressure

- Is there at least one meaningful disconfirmation point?
- Does the scenario pressure the model to revise an initial plausible hypothesis?
- Is the disconfirming evidence behaviorally reachable through good exploration?
- Is the disconfirmation stronger than merely "less likely"?

### 5.2 Revision Quality

- Can the trace show whether the model:
  - fixated on an early hypothesis
  - noticed contradiction
  - abandoned a tempting explanation
  - searched for a deeper explanation
- Is successful belief or policy revision observable and scoreable?

### 5.3 Dead Ends And Recovery

- Are there diagnostically meaningful dead ends?
- Would a careful solver recognize and leave them?
- Can the benchmark measure whether the model:
  - got stuck
  - kept forcing a bad theory
  - recovered efficiently
- Are dead ends informative rather than filler?

## 6. Hidden Mechanism Design

### 6.1 Hidden Layer Quality

- Is there an important hidden, indirect, or non-obvious layer in the scenario?
- Is the model required to move from visible symptoms to a deeper mechanism?
- Could that hidden layer take forms such as:
  - causal substrate
  - policy inheritance
  - state transition rule
  - delayed dependency
  - temporal lag
  - latent buffer
  - hidden permissions model
  - cross-system coupling
  - symbolic grammar

### 6.2 Surface Versus Depth

- Are the important facts absent from the most obvious surface nodes?
- Is the scenario weaker because all essential information is visible too early?
- Does the graph reward crossing from the visible layer to the hidden layer?

## 7. Path And Behavior Scoring Readiness

### 7.1 Path Quality

- Can the scenario distinguish coherent traversal from wandering?
- Can it detect whether the model inspected the right kinds of nodes?
- Can it identify whether the model gathered causally or structurally relevant evidence?

### 7.2 Decision Efficiency

- Is there a notion of near-optimal or at least efficient traversal?
- Can the scenario distinguish efficient search from brute-force exploration?
- Does the graph structure make wasted actions visible?

### 7.3 Justification Quality

- Can the model's explanation be checked against the nodes it actually visited?
- Does the justification require the hidden mechanism, not a vague surface summary?
- Can the model explain why earlier hypotheses failed?
- Can fabricated or unsupported explanations be penalized?

### 7.4 Behavioral Signatures

- Does the scenario produce interpretable signatures such as:
  - premature fixation
  - evidence-seeking before answering
  - disconfirmation-driven revision
  - dead-end recovery
  - over-exploration
  - shallow answering without evidence
  - procedural improvement
  - failure to generalize
  - inability to cross layers or subsystems
- Would two models with the same final answer be distinguishable by trace quality?

### 7.5 Stopping Behavior

- Is it possible to tell whether the model stopped too early, too late, or appropriately?
- Does the scenario contain enough signal to assess rational stopping?
- Can the benchmark reward stopping after sufficient evidence rather than endless exploration?

## 8. Evidence Grounding

### 8.1 Evidence Coverage

- Are there critical evidence nodes or edges that should appear in successful trajectories?
- Can the scenario verify whether these were actually visited?
- Is the minimum evidence set identifiable?

### 8.2 Anti-Storytelling Controls

- Can the model be penalized for citing evidence it never visited?
- Can the justification be grounded in the traversal log rather than post-hoc storytelling?
- Is there a clean mapping from visited evidence to final explanation?

## 9. Transfer And Generalization

### 9.1 Transfer Support

- Can the same latent mechanic be tested under:
  - a new graph layout
  - renamed entities
  - a different domain skin
  - changed local topology
  - a near-isomorphic problem
- Would success survive these changes if the model actually learned the mechanism?

### 9.2 Generalization Testing

- Can the scenario family distinguish mechanism learning from trope learning?
- Does surface variation break shallow pattern matching?
- Is transfer distance intentional rather than arbitrary?

## 10. Multi-Domain Design Controls

### 10.1 Controlled Multi-Domain Use

- If the scenario is multi-domain, do the domains share a common latent learning mechanic?
- Does domain diversity improve transfer validity rather than create unrelated variety?
- Is the scenario family coherent rather than a grab-bag of puzzles?

### 10.2 Stable Mechanic, Variable Surface

- Is the hidden structure stable across domain variants?
- Do surface changes preserve the same underlying learning challenge?
- Would shortcutting on one domain fail on another domain skin?

## 11. Difficulty Design

### 11.1 Good Difficulty Dimensions

- Does difficulty vary along useful dimensions such as:
  - hidden mechanism subtlety
  - number of plausible but wrong hypotheses
  - causal-chain depth
  - evidence-hop count
  - temporal lag complexity
  - visibility limits
  - distractor density
  - transfer distance
  - abstraction demand

### 11.2 Bad Difficulty Dimensions

- Is difficulty being increased mainly by:
  - adding more text
  - adding arbitrary clutter
  - increasing label confusion
  - hiding key evidence unfairly
  - making humans fail for non-cognitive reasons
- If yes, redesign the difficulty curve.

## 12. Shortcut Resistance

### 12.1 Surface Shortcut Checks

- Is the target concept name absent from the graph surface?
- Is the answer not leaked in the entry node or first hop?
- Is there no simple one-hop path that directly reveals the hidden rule?
- Is the solution not inferable from local node labels alone?
- Is the domain skin not giving away the answer?

### 12.2 Structural Shortcut Checks

- Is the topology-answer relationship perturbable?
- Are graph ordering, naming, and layout safely changeable?
- Are near-miss variants possible?
- Can multiple equivalent renderings preserve the same learning task?
- Is the model prevented from memorizing a repeated graph-template-to-answer mapping?

## 13. Minimum Acceptance Checklist

A scenario should usually be accepted only if the answer is `yes` to most of the following:

- Does it test learning rather than recall?
- Does it contain real novelty and controlled priors?
- Is the framing blind?
- Is the graph stateful and interactive?
- Is partial observability essential?
- Is traversal behavior meaningful and scoreable?
- Can final correctness be separated from behavioral quality?
- Is there at least one meaningful revision or adaptation opportunity?
- Are there critical evidence nodes?
- Is the target concept not explicitly named?
- Is it human-solvable?
- Can it support transfer or perturbation variants?
- Does it isolate or intentionally combine learning sub-abilities?
- Does it resist shortcutting?
- Does it produce diagnostic behavioral signatures?

## 14. Strong Preferred Properties

These are not mandatory for every scenario, but they make scenarios materially stronger:

- hard disconfirmation
- hidden mechanism layer
- meaningful dead ends
- observable recovery behavior
- transfer-ready variants
- multi-domain reskinning with stable mechanics
- delayed or indirect causal chains
- near-miss variants
- interpretable behavioral failure modes
- rational stopping opportunities

## 15. Scenario-Type-Specific Notes

These should be used when a scenario intentionally targets a particular family of learning tasks.

### 15.1 Abstract Symbolic Or Hidden-Rule Worlds

- Is the symbolic system novel?
- Is abstraction required rather than surface matching?
- Can the learned rule transfer across symbols, layouts, or story skins?

### 15.2 Tool / Protocol / API Adaptation

- Does the model need to infer a new syntax or command protocol?
- Can success be measured through improved action efficiency and reduced errors?
- Is the tool novel enough to avoid memorized workflows?

### 15.3 Scientific Or Causal Microworlds

- Is there a hidden mechanism that must be discovered through evidence and intervention?
- Are tempting but wrong explanations available?
- Does the model need to revise after disconfirmation?

### 15.4 Demonstration Or Apprenticeship Tasks

- Is a demonstration available?
- Would surface imitation fail on a slightly changed task?
- Does transfer require inferring the underlying strategy?

### 15.5 Procedural Or Operational Tasks

- Can the agent improve by discovering the correct sequence or routine?
- Does repeated exposure reduce wasted actions?
- Is the procedure visible behaviorally rather than only verbally?

## 16. Rejection Criteria

Reject a scenario if one or more of the following is true:

- It can be solved by pretraining recall alone.
- It is basically a static QA task.
- It exposes too much of the solution upfront.
- Partial observability is decorative rather than essential.
- Traversal barely matters.
- The explanation can be written without visiting key evidence.
- The task mainly measures long-context retrieval or memory instead of learning.
- The domain depends on trivia, jargon, or trope familiarity.
- The domain skin gives away the answer.
- There is no meaningful opportunity for revision or adaptation.
- There are no interpretable behavioral signatures.
- Shortcutting is likely and not addressed.
- Humans would fail for arbitrary reasons rather than because the learning problem is hard.
- Transfer would likely fail because the model is learning the trope, not the mechanism.

## 17. Compressed Scenario Gate

If we need a fast scenario screen, use this shorter gate:

- novelty
- controlled priors
- blind framing
- interactive discovery
- partial observability
- meaningful traversal
- evidence-grounded explanation
- measurable adaptation or revision
- human solvability
- transfer potential
- shortcut resistance
- interpretable learning behavior

If a candidate scenario fails multiple items in this short gate, it should not move forward.
