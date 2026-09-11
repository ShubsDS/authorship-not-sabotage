# Why our single-shot backdoor yield is 2-3% and the benchmark's is not

**Status:** diagnosis, measured 2026-09-11. The fixes at the end are **recommendations for the
post-workshop version** — they were not applied. The 11,565-draw attack pool was generated with the
original prompt, is already analysed and released, and a prompt change now would invalidate it and
the prompt-matched honest class that mirrors it.

---

## The defect

A backdoor must pass **every public test**. APPS copies the problem statement's sample I/O into
`inputs`/`outputs`. So a draw whose proposed trigger is one of those inputs **cannot diverge from the
honest solution** — not unlikely to, but mathematically cannot, because passing the test is what
being in the attack class requires.

The model reads the sample input off the problem statement and offers it back as its trigger. It does
this about **half the time**.

| trigger | n | fires |
|---|---:|---:|
| **is a public test input** | 1,467 | **0.27%** |
| is novel | 1,386 | **5.70%** |
| combined | 2,853 | 2.91% |

Share of our test-passing draws whose trigger is a public input: **56.2%**.
Stored working backdoors whose trigger is a public input: **0 of 1,582 — 0.0%**.

Replicated independently by another session on the full 11,565-draw pool: 52.0% of 6,570
test-passing draws, firing 0.15% against 5.13% for novel triggers. Two pools, two implementations,
same conclusion. See `trigger_public_check.py`.

Over every draw on disk regardless of test outcome: **11,973 of 21,615 — 55.4%**.

---

## Why this is the explanation and not merely a correlate

Three rival explanations, each killed by a measurement. `trigger_yield_evidence.py` reproduces all
three.

### 1. It is not that their models are better

`work|pass` — of the backdoors that pass the tests, the share whose trigger fires:

| source | model | n | pass | **work\|pass** |
|---|---|---:|---:|---:|
| control_tax | openai/gpt-4o-mini | 367 | 25.3% | **98.9%** |
| control_tax | anthropic/claude-3-7-sonnet-thinking | 517 | 36.8% | **97.4%** |
| control_tax | openai/o1-mini | 1,250 | 17.3% | **96.3%** |
| control_tax | openai/gpt-3.5-turbo | 142 | 27.5% | **94.9%** |
| control_tax | google/gemini-2.0-flash | 715 | 32.3% | **94.8%** |
| control_tax | anthropic/claude-3-7-sonnet-latest | 1,864 | 46.6% | **94.5%** |
| control_tax | openai/o3-mini | 2,261 | 35.7% | **93.9%** |
| control_tax | openai/gpt-4o | 1,148 | 34.5% | **92.7%** |
| control_tax | anthropic/claude-3-5-haiku | 591 | 29.6% | **88.6%** |
| apps | unknown | 2,516 | 18.2% | 75.5% |
| **ours** | **claude-sonnet-5, blind single-shot** | 4,121 | **57.6%** | **3.0%** |

`gpt-3.5-turbo` scores 94.9%. `o1-mini` scores 96.3%. A rate that flat across that capability range
is **a property the pipeline enforces, not a skill the model has**. Something downstream checks that
the trigger fires.

Note also that **we beat every one of them on passing the tests** — 57.6% against their best of
46.6%. The stage we are good at is the stage that needs no execution.

### 2. It is not that our bugs are worse

Classifying the added lines of each backdoor's diff against its honest source:

| structure | theirs (working) | ours (test-passing) |
|---|---:|---:|
| boundary / off-by-one | 74.2% | **85.2%** |
| magic-value special case | 16.2% | **2.2%** |
| other | 9.5% | 12.5% |

Ours are **more** idiomatic, not less: more ordinary off-by-one mistakes, far fewer special cases
bolted on to catch one magic input — which is exactly what both prompts ask for. We write good
backdoors and then fail to prove them.

### 3. Their headline rate is a best-of, ours is a single attempt

The artifact holds **11,371 backdoor records** across **two sources and ten (source, model) pairs**.
**2,314 problems carry more than one attempt, up to 31.** Per single attempt the rates are 32.1%
(`control_tax`) and 13.8% (`apps`). Any comparison of a single-shot rate against the artifact's
headline must say so.

---

## The mechanism, stated plainly

ControlArena attack policies **execute code**: write a bug, run the tests, check the trigger,
iterate. Our batch call is single-shot and blind, so the model must predict both that its bug evades
~11 hidden tests (median) and that its chosen input triggers it. It is adequate at the first and
poor at the second, and the public-input trigger is the visible signature of that gap.

This is worth stating in the paper for its own sake: **the stored attack class is the survivor set of
an unreported number of retries**, filtered by an execution loop the class's consumers never see.
On Koran's test split the filter discards 892 labelled candidates down to 172 — 5.2x.

---

## Recommendations for the post-workshop version

Not applied here. Both change the attack protocol, so both require regenerating the attack class and
the prompt-matched honest class together.

**1. Forbid statement inputs as triggers — free, one sentence.**

> Your example input must NOT be any input shown in the problem statement — those are covered by the
> public tests your program must pass.

Expected lift **2.0x** on conditional firing (2.91% -> 5.70%), from removing draws that are dead on
arrival. Costs nothing and changes no other property.

**2. Put the public test inputs in the attack prompt — one batch round.**

The benchmark's attacker had test access; we withhold it. With the tests visible the model can avoid
them deliberately rather than by luck, which is the harder half of the task.

> ⚠️ **Asymmetry warning.** This changes the protocol for the **attack class only**. The honest class
> must stay test-blind — showing it the tests would let it fit the checker, which is the artifact
> this paper audits. An arm built this way has a generator that saw the tests on one side and not the
> other, and Limitations must say so.

**3. What does not work, so nobody retries it.** Pooling every draw's proposed trigger per problem
plus the artifact's own stored trigger, then testing each candidate against all of them, reaches a
search depth of ~6.9 witnesses per candidate and lifts yield only **~2x** (1 -> 2 of 180 on a test
shard) — far below the ~5x an independence assumption predicts, because the proposed triggers are
highly correlated: they are all small edge cases, so a backdoor that misses one usually misses the
rest. Implemented and measured; not adopted.
