# Track 5 Scenario Validation Checklist
## Social Cognition

This document is the working validation checklist for deciding whether a proposed Vigil scenario genuinely measures `Track 5: Social Cognition` in the DeepMind AGI framework, rather than generic reasoning, moral opinion generation, static dialogue QA, trope matching, or thin role-play.

It is meant to be used before scenario generation, during scenario review, and before benchmark acceptance.

---

## Purpose

This checklist is designed to answer one core question:

`Does this scenario force the model to interpret social information, model other agents' minds, and act appropriately in a social situation through its behavior during the episode?`

If the answer is no, then it is not a strong Track 5 scenario.

---

## How To Use This Checklist

- Treat `Core Requirements` as mandatory unless there is a very strong reason not to.
- Treat `Strong Preferred Properties` as features that materially improve scenario quality and benchmark validity.
- Treat `Scenario-Type-Specific Checks` as required only when the scenario claims to measure that specific social sub-ability.
- Use `Rejection Criteria` as hard blockers.
- A scenario does not need to satisfy every preferred property, but it should satisfy most of the core requirements and produce clearly interpretable social behavior.

---

## 1. Core Requirements

### 1.1 Social-Through-Interaction

- Does the scenario require social interpretation rather than only abstract puzzle solving?
- Does success depend on understanding one or more other agents, not just the physical state of the environment?
- Does the model need to infer something socially latent, such as:
  - another agent's belief
  - another agent's intention
  - another agent's preference
  - another agent's emotional state
  - another agent's private knowledge
  - another agent's incentive
  - a social norm or expectation
  - a trust or reputation relationship
- Would the scenario still be meaningful if the final answer text were hidden and only the behavior trace and communications were available?

### 1.2 Real Social Stakes

- Is there an actual social consequence to the model's action, communication, or timing?
- Does the scenario require the model to choose what to reveal, withhold, ask, clarify, coordinate, or negotiate?
- Is the task socially situated rather than merely asking the model to describe a social concept?
- Does the environment make other agents' reactions matter?

### 1.3 Blind Framing

- Does the model receive a genuine task rather than an exam-style social reasoning question?
- Is the model not told what exact social faculty is being tested?
- Are the hidden beliefs, incentives, norms, or alliances not explicitly named in the opening context?
- Does the environment feel like a real interaction problem rather than a test with hints?

### 1.4 Social Cognition Versus Generic Reasoning

- Would the task become much weaker if all agents were replaced by inert objects?
- Is the challenge specifically social, rather than just causal reasoning with names attached?
- Does success require modeling minds, norms, or relationships, not just optimizing a search tree?
- Is the scenario harder than simple sentiment detection or role-label matching?

### 1.5 Human Solvability

- Is the scenario human-solvable with the same interface constraints?
- Does difficulty come from learnable social structure rather than obscure cultural trivia?
- Could a human baseline reasonably be collected for this scenario?
- Would human trajectories be meaningfully comparable to model trajectories?

---

## 2. Environment Requirements

### 2.1 Graph As Social Environment

- Is the graph a stateful social environment for action, not just a graph-shaped conversation log?
- Do nodes and edges represent socially meaningful objects such as:
  - agents
  - messages
  - commitments
  - observations
  - beliefs
  - intentions
  - trust links
  - norms
  - coalitions
  - obligations
  - hidden incentives
- Does traversal materially affect what the agent can know about others and what social moves are available?

### 2.2 Partial Observability And Private Information

- Is all socially relevant information hidden at the start?
- Do different agents have different knowledge states?
- Is there meaningful public versus private information?
- Must the model infer what each agent knows, thinks, or has observed?
- Is information asymmetry essential to the scenario rather than decorative?

### 2.3 Multi-Agent Reality

- Are there at least two socially meaningful agents besides the evaluator, or one rich human counterpart with non-trivial internal state?
- Do agents differ in goals, beliefs, or incentives?
- Can these differences create:
  - misunderstandings
  - coordination problems
  - negotiation pressure
  - trust problems
  - misaligned incentives
- Is the social world dynamic enough that interaction changes later possibilities?

### 2.4 Communication As Action

- Are messages, questions, disclosures, commitments, refusals, and clarifications treated as meaningful actions?
- Does wording matter behaviorally rather than only cosmetically?
- Can communicative choices change beliefs, trust, or outcomes?
- Can the model's interaction policy be observed in the trace?

---

## 3. Social-Cognition Theory Alignment

### 3.1 DeepMind Social Cognition Alignment

- Does the scenario match the idea of processing and interpreting social information and responding appropriately in social situations?
- Does the scenario test one or more of the three DeepMind sub-components:
  - social perception
  - theory of mind
  - social skills
- Does success require socially appropriate action, not just plausible narration?

### 3.2 Social Perception Alignment

- If the scenario claims to test social perception, are there cues from which social meaning must be inferred?
- Are these cues behaviorally useful, not merely decorative?
- In text-first settings, are cue proxies designed carefully, such as:
  - politeness shifts
  - hesitation
  - indirectness
  - inconsistency between statement and action
  - commitment strength
  - omission patterns
- Is the task more than emotion labeling?

### 3.3 Theory Of Mind Alignment

- If the scenario claims to test theory of mind, must the model reason about others' beliefs, desires, emotions, intentions, expectations, or perspectives?
- Does the model need to predict or explain behavior from those hidden mental states?
- Is there belief asymmetry, false belief, or perspective divergence?
- Does the scenario test partner modeling in-context rather than only literary interpretation?

### 3.4 Social Skills Alignment

- If the scenario claims to test social skills, does it require action according to social norms or expectations?
- Does success depend on one or more of:
  - cooperation
  - negotiation
  - trust management
  - norm compliance
  - norm repair after violation
  - persuasion in a bounded safe setting
  - deception in a bounded safe setting
- Is social skill measured through behavior and consequences, not just through a verbal explanation of what would be appropriate?

---

## 4. Distinguishing Track 5 From Adjacent Faculties

### 4.1 Social Cognition Versus Metacognition

- Is the task about modeling other minds rather than primarily monitoring the model's own mind?
- If confidence reporting is present, is it supporting the social task rather than becoming the main object of evaluation?

### 4.2 Social Cognition Versus Executive Function

- Is planning present in service of social interaction, not as the central target?
- Would the scenario still matter if the model planned efficiently but misunderstood the agents?

### 4.3 Social Cognition Versus Attention

- Are social cues central because they inform partner modeling or norm interpretation, not merely because the model must notice a salient token?

### 4.4 Social Cognition Versus Static Ethics QA

- Is the benchmark measuring situated social behavior rather than asking for moral opinions in the abstract?
- Can the model's social quality be judged from what it does under constraints rather than from generic policy-safe phrasing?

---

## 5. Functional Theory-Of-Mind Checks

### 5.1 Beyond Literal ToM

- Does the task require more than answering a question about what someone believes?
- Must the model adapt its own behavior after inferring another agent's likely beliefs, goals, or policy?
- Would a model that only predicts others correctly but never uses that prediction strategically still fail?

### 5.2 Partner Adaptation

- Does the scenario test whether the model updates its partner model over time?
- Can the scenario reveal whether the model notices that a partner is:
  - cooperative
  - deceptive
  - confused
  - risk-averse
  - unreliable
  - under-informed
  - strategically withholding
- Is the partner model behaviorally consequential?

### 5.3 Nested Or Higher-Order Social Reasoning

- If higher-order theory of mind is claimed, is there actual need for beliefs about beliefs or expectations about expectations?
- Is higher-order reasoning necessary rather than ornamental?
- Can performance degrade in a diagnostically useful way as social recursion depth increases?

---

## 6. Social Mechanism Design

### 6.1 Hidden Social Layer Quality

- Is there an important hidden social layer that the agent must uncover?
- Could that hidden layer take forms such as:
  - hidden alliances
  - concealed intentions
  - unspoken norms
  - status asymmetry
  - private commitments
  - reputation effects
  - audience effects
  - strategic bluffing
  - preference misreporting
  - conflicting incentives
- Is the model required to move from observable behavior to latent social mechanism?

### 6.2 Public Signal Versus Private Meaning

- Are the most important social facts absent from the obvious surface layer?
- Can the same outward statement have different meanings depending on who knows what?
- Does the scenario reward crossing from observable communication into latent belief and incentive structure?

---

## 7. Disconfirmation, Repair, And Revision

### 7.1 Disconfirmation Pressure

- Is there at least one meaningful point where the model's first social interpretation could be wrong?
- Can the scenario pressure the model to revise its view of an agent, alliance, or norm?
- Is the disconfirming evidence behaviorally reachable through good exploration or interaction?

### 7.2 Social Repair Quality

- Can the trace show whether the model:
  - noticed misunderstanding
  - asked a clarifying question
  - repaired a trust failure
  - updated its estimate of another agent
  - switched from confrontation to cooperation or vice versa
- Is successful social repair observable and scoreable?

### 7.3 Dead Ends And Recovery

- Are there socially meaningful dead ends such as broken trust, failed negotiation, or misread intent?
- Can the benchmark measure whether the model recovered effectively?
- Are dead ends informative rather than filler?

---

## 8. Path And Behavior Scoring Readiness

### 8.1 Social Trajectory Quality

- Can the scenario distinguish skilled social interaction from random or tone-polished wandering?
- Can it detect whether the model inspected the right social evidence, asked the right questions, and engaged the right agents in the right order?
- Can it distinguish genuine partner modeling from canned social scripts?

### 8.2 Social Decision Efficiency

- Is there a notion of efficient social discovery or coordination?
- Can the benchmark distinguish efficient trust-building or belief-resolution from brute-force questioning?
- Does the graph structure make wasteful social exploration visible?

### 8.3 Justification Quality

- Can the model's explanation be checked against the actual messages, observations, and commitments it saw?
- Does the justification require the hidden social mechanism, not a vague summary?
- Can fabricated partner models be penalized?

### 8.4 Behavioral Signatures

- Does the scenario produce interpretable signatures such as:
  - premature trust
  - chronic suspicion
  - stereotype-based shortcutting
  - failure to ask clarifying questions
  - inability to track private versus public knowledge
  - inability to adapt to a new partner
  - norm over-application
  - norm under-application
  - manipulation when cooperation would suffice
  - social collapse after contradiction
- Would two models with the same final outcome be distinguishable by trace quality?

### 8.5 Stopping Behavior

- Is it possible to tell whether the model stopped too early, over-communicated, or stopped appropriately?
- Does the scenario support rational stopping once enough social evidence has been gathered?

---

## 9. Evidence Grounding

### 9.1 Mental-State Evidence Coverage

- Are there critical evidence items that should appear in successful trajectories, such as:
  - who saw what
  - who said what to whom
  - who omitted what
  - who contradicted whom
  - who committed to what
  - who benefits from which outcome
- Can the scenario verify whether these were actually visited or elicited?

### 9.2 Anti-Storytelling Controls

- Can the model be penalized for inventing beliefs, motives, or emotions unsupported by the interaction log?
- Can the explanation be grounded in the traversal and communication trace rather than post-hoc storytelling?
- Is there a clean mapping from observed social evidence to final interpretation?

---

## 10. Transfer And Generalization

### 10.1 Transfer Support

- Can the same latent social mechanic be tested under:
  - renamed agents
  - changed status roles
  - different domain skin
  - different communication style
  - different graph topology
  - new partner policy
- Would success survive these changes if the model actually learned the mechanic?

### 10.2 Generalization Testing

- Can the scenario family distinguish social mechanism learning from trope learning?
- Do surface changes break stereotype-based shortcuts?
- Is transfer distance intentional rather than arbitrary?

### 10.3 Partner-Shift Robustness

- Does the benchmark include partner variation significant enough to test adaptation?
- Can a model that overfits to one interaction style be exposed?
- Can the benchmark reveal whether the model re-uses one canned social policy across incompatible partners?

---

## 11. Multi-Domain Design Controls

### 11.1 Controlled Multi-Domain Use

- If the scenario is multi-domain, do the domains share a common latent social mechanic?
- Does domain diversity improve transfer validity rather than create unrelated variety?
- Is the scenario family coherent rather than a grab-bag of social mini-games?

### 11.2 Stable Mechanic, Variable Surface

- Is the underlying social structure stable across domain variants?
- Do surface changes preserve the same core challenge, such as belief asymmetry, negotiation under misaligned incentives, or norm interpretation under ambiguity?
- Would shortcutting on one social skin fail on another?

---

## 12. Difficulty Design

### 12.1 Good Difficulty Dimensions

- Does difficulty vary along useful dimensions such as:
  - number of agents
  - private-information complexity
  - belief recursion depth
  - norm ambiguity
  - incentive conflict
  - deception subtlety
  - trust uncertainty
  - communication sparsity
  - partner volatility
  - need for repair after misunderstanding

### 12.2 Bad Difficulty Dimensions

- Is difficulty being increased mainly by:
  - adding more text without new social structure
  - using obscure cultural references
  - relying on demographic stereotypes
  - making agents inconsistent for no reason
  - hiding critical evidence unfairly
  - making humans fail for non-social reasons
- If yes, redesign the difficulty curve.

---

## 13. Shortcut Resistance

### 13.1 Surface Shortcut Checks

- Is the correct social interpretation absent from obvious first-hop surface cues?
- Is the task not solvable from role labels alone?
- Is the domain skin not giving away the intended social policy?
- Are names, occupations, or demographics prevented from becoming shortcuts?
- Is sentiment alone insufficient to solve the task?

### 13.2 Structural Shortcut Checks

- Are private-information layouts perturbable?
- Are agent order, naming, and graph layout safely changeable?
- Are near-miss variants possible, where superficially similar social scenes demand different responses?
- Can multiple equivalent renderings preserve the same social task?
- Is the model prevented from memorizing repeated scenario-template-to-answer mappings?

---

## 14. Safety And Dual-Use Controls

### 14.1 Safe Handling Of Persuasion And Deception

- If persuasion or deception is included, is it bounded, synthetic, and clearly sandboxed?
- Is the task measuring capability without encouraging real-world harmful manipulation?
- Are targets fictional, simulated, or otherwise protected?
- Is the benchmark free of instructions that would facilitate harmful real-world abuse?

### 14.2 Benign And Harmful Skill Separation

- Can the scenario distinguish socially useful capabilities from socially risky ones?
- Does the benchmark avoid rewarding manipulation where cooperation, clarification, or truthfulness would be the better solution?
- If strategic deception is present, is it justified by the scenario and flagged clearly at design time?

---

## 15. Minimum Acceptance Checklist

A scenario should usually be accepted only if the answer is `yes` to most of the following:

- Does it test social cognition rather than generic reasoning?
- Does it contain real social structure and information asymmetry?
- Is the framing blind?
- Is the graph stateful and socially interactive?
- Is partial observability essential?
- Does success require modeling other agents?
- Can final correctness be separated from behavioral quality?
- Is there at least one meaningful revision, repair, or adaptation opportunity?
- Are there critical social evidence nodes or interactions?
- Is the target interpretation not explicitly named?
- Is it human-solvable?
- Can it support transfer or partner-shift variants?
- Does it isolate or intentionally combine social sub-abilities?
- Does it resist stereotype-based or trope-based shortcutting?
- Does it produce diagnostic social behavioral signatures?

---

## 16. Strong Preferred Properties

These are not mandatory for every scenario, but they make scenarios materially stronger:

- private versus public knowledge asymmetry
- hidden alliance or incentive layer
- meaningful social repair opportunities
- partner adaptation across turns
- transfer-ready variants
- multi-domain reskinning with stable social mechanics
- near-miss variants
- observable trust calibration
- process-aware scoring of communication, not just outcome
- safe measurement of bounded persuasion or deception

---

## 17. Scenario-Type-Specific Notes

### 17.1 False-Belief / Knowledge-Asymmetry Worlds

- Does the model need to distinguish world state from another agent's belief state?
- Are belief updates localized to what each agent actually observed?
- Would simple omniscient reasoning fail?

### 17.2 Cooperation / Coordination Tasks

- Does the model need to align with others toward a common goal?
- Is success sensitive to timing, trust, and shared understanding?
- Can a selfish or tone-only policy fail despite sounding good?

### 17.3 Negotiation / Misaligned Goals

- Are incentives genuinely misaligned?
- Must the model infer reservation points, priorities, or constraints from interaction?
- Is the task more than choosing a compromise sentence?

### 17.4 Trust / Reputation Tasks

- Are agents' past actions behaviorally relevant?
- Must the model calibrate trust rather than trust everyone or no one?
- Can the task expose gullibility and excessive suspicion separately?

### 17.5 Persuasion / Deception Tasks

- Is the capability measured in a bounded, safe, synthetic setting?
- Is success defined carefully enough that harmful manipulation is not implicitly rewarded?
- Can the task distinguish strategic influence from unsupported bluffing?

### 17.6 Social Perception Tasks

- Are cues subtle but recoverable?
- Do cues matter only in relation to context and incentives, not as isolated labels?
- Would a sentiment-only system fail?

### 17.7 Norm Interpretation And Repair

- Is there a contextual norm that must be inferred rather than stated?
- Can the model recognize a norm violation and recover appropriately?
- Is there a meaningful difference between socially adequate and merely fluent responses?

---

## 18. Rejection Criteria

Reject a scenario if one or more of the following is true:

- It can be solved by generic reasoning without modeling any agent.
- It is basically a static ToM multiple-choice question.
- It exposes the hidden belief, incentive, or alliance too early.
- Partial observability is decorative rather than essential.
- Communication has no real consequences.
- The explanation can be written without visiting key social evidence.
- The task mainly measures etiquette parroting, sentiment labeling, or safety-style refusal instead of social cognition.
- The domain depends on cultural trivia, stereotypes, or role tropes.
- Names, demographics, or occupations give away the answer.
- There is no meaningful opportunity for social revision, repair, or partner adaptation.
- There are no interpretable social behavioral signatures.
- Shortcutting is likely and not addressed.
- Humans would fail for arbitrary reasons rather than because the social problem is genuinely hard.
- Transfer would likely fail because the model is learning the trope, not the social mechanism.
- Persuasion or deception is included in a way that creates unnecessary dual-use risk.

---

## 19. Compressed Scenario Gate

If we need a fast scenario screen, use this shorter gate:

- real social stakes
- hidden other-minds / incentives / norms
- blind framing
- interactive social behavior
- partial observability and private information
- partner modeling
- evidence-grounded interpretation
- measurable adaptation or repair
- human solvability
- transfer or partner-shift potential
- shortcut resistance
- interpretable social behavioral signatures

If a candidate scenario fails multiple items in this short gate, it should not move forward.
