# What is dead here — read this before rewriting a sentence

Reviving a dead framing without new evidence is the cheapest mistake available, and under deadline
pressure the dead sentences are exactly the ones that sound best. Each row carries the evidence that
killed it.

---

## Tier 1 — killed by the literature, on 2026-09-03, by reading rather than grepping

| Sentence | Killed by | Note |
|---|---|---|
| **"No control paper reports a construct-validity check on APPS backdoors."** | `2605.15377` §4.1 · `2506.05296` §2.3 + App. C.3 · `2608.16190` §2 · `2602.10153` | The field preprocesses these leaks away **and says why**. Claim only the *quantification* and the *authorship reading*. |
| **"The metadata floor is above the published monitor."** | The DSPy tutorial's own protocol | The **0.64 does not exist**. 69% *pairwise accuracy* untrained, 78–81% after GEPA, on a *matched* protocol where the metadata floor is **exactly 0.5000**. Every published pAUC is on Koran's filtered split. |
| **"Nobody has run a trivial baseline."** | `anik-jha/challenger-panels` | The flag is called `--leak-check`, it ships two of them, and the README says *"Stripping is mandatory, not cosmetic."* **Credit it in paragraph one.** |
| **"Longer code is the attack."** | `runs/x2/leakage-checks.json` | 0.8255 within-pair on the raw artifact; **`code_length_only_auroc` = 0.4726 — chance — on the split the field uses**, which K1 reproduced bit-exactly. A row in the preprocessing table, not a finding. |
| **"Two distinct APPS-backdoor datasets exist."** | K1 | One dataset and one derived copy. All 2,584 Koran `problem_id`s are in `RoganInglis/apps-control-arena`; every shared column byte-identical except a re-validated `backdoor_works`. This claim was asserted, reversed, and both versions were wrong — see `lit/01` §7. |

## Tier 2 — real results, but not papers. One paragraph each, inside this one.

| Result | Why it is a paragraph | Where it goes |
|---|---|---|
| **The scratchpad names the side task.** A 15-word regex over the untrusted policy's own reasoning: AUROC 0.76–0.82 across all five agentic settings, because prompted attack policies restate their side task in the reasoning the monitor reads. `P(hit ¦ attack)` 0.65–0.67 vs `P(hit ¦ honest)` 0.039–0.332. | `2607.09786` already runs a lexical hint-echo detector, a content-blind length-matched null, **and** a scrubbed-vs-unscrubbed classifier ablation. Different setting, same instrument — it owns it. And the honest claim is about *prompted model organisms*, which is far smaller than "CoT monitoring is overrated." | The CoT row of the main table. **First in the cut order if Sep 10–11 slips.** |
| **The label-noise ceiling.** 36% of labelled backdoors in the raw artifact never fire; **80.7% in Koran's test split**, where the *problem* is relabelled honest. ⛔ **Not "60% of that split's honest items are failed attacks"** — `bow.py` builds label 0 from `_honest_code(row)`, a human APPS solution, so the failed attack's code never enters the split. The artifact is selection at the **problem** level, and that sentence was cut from the paper on 2026-09-11 (`notes/09-review-audit.md` objection 1). Do not revive it. | `backdoor_works` is a **shipped, documented column** and Koran's filter selects on it. The field knows. A "ceiling" claim also needs assumptions four pages cannot defend. | One paragraph and one number, as the *second selection artifact* the field's own filter installs. |
| **IRT on the 24 × 1,375 score matrix.** Item difficulty and discrimination; the items separating monitors are the items the metadata floor already solves. | Wrong register for this PC — evolutionary computation and adversarial robustness, not psychometrics — and it changes no deployment default. | Killed. **But its artifact is the single most valuable thing the scan found**: `runs/scores/` is what deleted the GPU from the monitor comparison. |

## Excluded on purpose

- **AgentHarm as a sixth corpus.** ⛔ **G2.** Andriushchenko authored it and is an EvoRobust invited
  speaker. Say the exclusion in the paper, and say why.
- **`AISafety-Student/labeled-bashBench`.** Its `danger_level` / `action_type` annotations separate
  the label perfectly. The "label" *is* the danger annotation. Circular; not a monitor benchmark.
- **Anything about C9** (divergence-relative monitoring). It stays in the ideation repo, parked for
  November, and it is the weaker November option — the authorship line across every stored-pair
  benchmark is the better extension, and it will have a submitted paper and a released split behind
  it. **No hours on it before Sep 13.**

## The framings that are alive, and the order they are claimed in

1. The field filters, strips comments and reports the selection effects — **cite that first**.
2. What the preprocessing leaves behind is unquantified: bag-of-words **0.806** and a no-code
   classifier **0.772** on the split that ranks 24 monitors at median 0.609.
3. The mechanism is **authorship**: human-written honest vs LLM-written attack. **Comment-stripped
   on both classes, which is the only column the paper quotes** (`RESULTS.md` §6.2): transfers across
   generators at **0.969**, as strong on inert backdoors (**0.879**) as on working ones (**0.935**),
   visible in `__main__` (0.116 vs 0.000, untouched by the stripper). ⚠️ The unstripped 0.9935 /
   0.954 / 0.979 are **dead in prose** — they are the comment channel measuring itself, and they live
   in one appendix paragraph labelled as inflated. So is the `#` marker (attack 0.685 vs honest
   0.176): after stripping it is 0.007 vs 0.008 and the paper says it is dropped.
   And after Gate S, authorship is **about a third** of the separability (ρ = 0.687, 0.625–0.755),
   not all of it; the §3 heading is "The signal is not sabotage", which is what every row supports.
4. The field's own filter installs a **second** artifact by defining the negative class through
   attack failure.
5. Five same-generator agentic settings show what a floor looks like with authorship removed — and
   one of them (agentdojo, 0.802 from character count within task) is still leaky.
