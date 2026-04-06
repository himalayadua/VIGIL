I did the research pass for **Track 2: Attention** and built a first rigorous checklist. I also cross-checked it against your uploaded hackathon/paper notes. 

## Track 2 — Attention scenario validation checklist

### 1) What this track is actually testing

DeepMind defines **attention** as the ability to focus cognitive resources on specific aspects of perceptual stimuli, information, or thoughts when resources are limited. The paper explicitly says attention involves a balance between staying narrowly focused on current goals and staying responsive to unexpected changes, and breaks the faculty into **attention capacity**, **selective attention / attentional control** (sustained attention, perceptual inhibition, attention shifting), and **stimulus-driven attention**. 

**So a valid Track 2 scenario must ensure:**

* the difficulty comes from **allocation of focus under competition**, not from hidden world knowledge
* the agent must choose **what to attend to, what to ignore, and when to reorient**
* there are **multiple competing cues**, not just one obviously relevant path
* attention errors are behaviorally visible in the trace

If a scenario is mostly about discovering a latent rule, it is drifting toward **Learning**. If it is mostly about storing and later recalling facts, it is drifting toward **Memory**. If it is mostly about long-horizon planning or inhibition of prepotent responses across a goal tree, it is drifting toward **Executive Function**. The main bottleneck for this track must be **focus management**, not something else. 

---

### 2) Non-negotiable structural requirements

A good attention scenario must create a real **attentional bottleneck**. Without that, it is not testing attention at all. DeepMind’s framing assumes limited cognitive resources, and long-context evaluation work shows that current models often fail when relevant information competes with large volumes of context or distractors. 

**Every candidate scenario should ensure:**

* there is **more information available than should be comfortably processed all at once**
* only a subset of information is actually relevant to the task
* relevance is not always obvious from surface form
* some irrelevant information is **plausible**, not just random noise
* success depends on attention choices made during the episode, not just the final answer

---

### 3) The scenario must test one or more of the four real sub-mechanisms

#### A. Attention capacity

DeepMind defines this as how much information a system can focus on simultaneously, potentially varying by modality. 

**To validate capacity-related scenarios, ensure:**

* information load can be increased in a controlled way
* there are multiple active items/streams competing for focus
* performance can be measured as load rises
* load is not secretly turning the task into a pure memory test
* different modalities or channels can be varied separately if multimodal

#### B. Sustained attention

DeepMind defines sustained attention as maintaining focus on goal-relevant information over time, and vigilance literature defines failures here as a gradual decline in the ability to monitor for rare critical stimuli over prolonged periods. 

**To validate sustained-attention scenarios, ensure:**

* the task lasts long enough for lapses to become possible
* critical signals may appear **late** or **rarely**
* the model cannot front-load all useful work in the first few steps
* performance can be examined as a function of **time-on-task**
* the scenario can reveal omission, drift, fatigue-like lapses, or declining monitoring quality

#### C. Perceptual inhibition / selective attention

DeepMind defines this as ignoring distracting or goal-irrelevant perceptual information. Research on LLMs also shows strong sensitivity to irrelevant context, with accuracy and reasoning path quality degrading as distractors increase. 

**To validate selective-attention scenarios, ensure:**

* distractors are **semantically or structurally plausible**
* distractors are close enough to target cues that superficial filtering is hard
* there is a measurable penalty for following off-path cues
* distractors do not make the task impossible for humans
* distractor count, similarity, and placement can be systematically varied

#### D. Attention shifting + stimulus-driven attention

DeepMind distinguishes active shifting of attention from one item/location to another and bottom-up redirection toward new stimuli or environmental changes. The reorienting literature also emphasizes that unexpected, deviant, or task-relevant changes can act like an attentional “circuit breaker.” 

**To validate shifting/reorienting scenarios, ensure:**

* relevance can **move** during the task
* a previously irrelevant region/node/stream can become relevant
* there are occasional unexpected changes that deserve reorientation
* some salient changes are true alerts, while others are false alarms
* the trace reveals whether the model noticed, ignored, overreacted, or switched too late

---

### 4) Position, placement, and context-geometry must be controlled

“Lost in the Middle” shows that LLM performance is often best when relevant information is near the beginning or end of context and significantly worse when it is in the middle. RULER also shows that simple needle-in-a-haystack retrieval is too shallow and that models drop sharply as context length and task complexity increase. 

**So every attention scenario should ensure:**

* the critical cue is not always near the beginning or the end
* cue position is randomized across variants
* success is not possible through a fixed reading heuristic like “scan first and last”
* single-needle retrieval is not the whole task
* scenarios include variants requiring multi-step use of attended information, not mere spotting

---

### 5) Distractor design must be deliberate, not decorative

LLM attention failures are easiest to expose when distractors are controlled, plausible, and off-path rather than obviously junk. GSM-DC is useful here because it injects irrelevant context via off-path graph nodes and shows that distractors affect both reasoning path selection and arithmetic accuracy. 

**A high-quality Track 2 scenario should ensure:**

* distractors are generated from a clear taxonomy:

  * semantically similar distractors
  * structurally similar distractors
  * temporally salient distractors
  * emotionally/saliently framed distractors if relevant
* each distractor type has a known intended failure mode
* distractors can be toggled on/off for ablations
* distractors are not so strong that the benchmark becomes unfair noise injection
* there is a clear difference between **goal-irrelevant**, **temporarily irrelevant**, and **misleadingly salient** information

---

### 6) The scenario should feel like a real task, not a lab instruction about attention

This is especially important if you want “Don’t Ask — Watch” to remain consistent across tracks. In Track 2, you do **not** want the prompt to tell the model “this is a distraction test.” That would turn the benchmark into compliance with evaluation framing instead of natural attention allocation. DeepMind’s overall framework emphasizes targeted cognitive testing under controlled conditions, but without contaminating the intended construct. 

**So ensure:**

* the model is given a real task, not an attention warning
* the environment does not explicitly mark the critical cue as “important”
* salient events look natural inside the scenario world
* attending correctly must emerge from the task demands themselves

---

### 7) Tool access and visibility need to be tightly controlled

DeepMind explicitly warns that tool access can muddy interpretation of cognitive tests, and human baselines should be run with the same tool access as the AI system. 

**For Track 2, ensure:**

* the agent cannot bypass attention demands by using unrestricted search/filter tools unless humans get the same capability
* UI affordances do not automatically highlight relevance unless that is part of the intended task
* any summarization or retrieval helper is treated as part of the tested system and reflected in the human baseline
* observation budget, step budget, and tool budget are explicit

---

### 8) Scoring must reward attention behavior, not just final correctness

Attention is a trace-level faculty. A lucky answer should not count the same as disciplined cue selection. Long-context and distractor literature shows that models can fail both in locating relevant information and in using it robustly. 

**A strong attention scenario should expose and score:**

* **hit rate** on relevant cues
* **false-alarm rate** on distractors
* **latency to orient/reorient**
* **coverage quality**: did the model inspect the right places at the right times?
* **time-on-task stability**: does performance decay over the episode?
* **switch cost**: how expensive was reorientation after a change?
* **salience discipline**: does the model chase flashy but irrelevant events?
* **justification grounding**: does its explanation match what it actually attended to?

---

### 9) Human-solvability and fairness requirements

DeepMind’s protocol requires held-out tasks, human baselines, varied difficulty/format, and same-condition comparison. 

**So each Track 2 scenario should ensure:**

* humans can solve it without obscure priors
* humans and models see the same world and tool conditions
* difficulty comes from attentional competition, not ambiguity or bad writing
* there is a clear human baseline for:

  * detection
  * false alarms
  * reaction/reorientation
  * sustained monitoring quality

---

### 10) What should automatically disqualify a Track 2 scenario

Reject the scenario if:

* there is no real attentional bottleneck
* all relevant information is obvious on first inspection
* distractors are trivial junk
* success depends mostly on prior world knowledge
* failure mostly comes from reasoning depth, not cue selection
* failure mostly comes from memory load, not focus allocation
* there is no dynamic reorientation demand anywhere in the family
* relevant cues always sit in privileged positions
* the trace cannot reveal what the model actually focused on
* a summarizer/search tool can collapse the whole task into plain retrieval

---

### 11) Minimal scenario card for Track 2

For every candidate scenario, I would require these fields:

* dominant attention sub-ability being tested
* secondary overlapping faculty risks
* attentional bottleneck description
* relevant cue types
* distractor taxonomy
* true-alert vs false-alert design
* cue placement policy
* sustained-attention duration/load settings
* reorientation trigger
* scoring signals captured
* shortcut/leakage risks
* human pilot notes

---

### 12) Compressed gold-standard gate

A **real Track 2 scenario** should pass this compact test:

* **limited capacity is real**
* **multiple competing cues exist**
* **irrelevant context is plausible**
* **relevance is not positionally privileged**
* **the agent must ignore, persist, and reorient**
* **unexpected changes can matter**
* **single-needle retrieval is not enough**
* **trace-level attention behavior is scoreable**
* **humans can do it under the same conditions**
* **the main failure mode is attentional, not memory/reasoning/planning**
