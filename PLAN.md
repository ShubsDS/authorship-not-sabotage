# The runbook to Sep 12

Written 2026-09-03. Thresholds, routes and stopping rules are fixed **now**, before the check that
decides the title runs — which is the entire point of writing them down (`notes/03` R5, R16).

**The human is serial and the GPU is trivial.** Nothing here needs more than one rented 4090 for an
afternoon. Sep 3–7 belongs to the InfPriv paper in the ideation repo; this paper's first commitment
is a title and 150 words on **Sep 5**, and its work starts **Sep 8**.

---

## 0. Where this stands

Every CPU number exists (`experiments/`). Gate M is deleted — `runs/scores/` publishes 24 monitors'
per-item scores on the exact 1,375-item split, MIT, no GPU. What remains is **one control, three
figures and four pages**, and the risk is entirely in the four pages.

**G1 was discharged on 2026-09-03** (`lit/01` §4): both AI-code-detection neighbours were read end to
end and both come back NEIGHBOUR. That was the last check that could void the framing, so under R16
**the split and the paper are clear to be made public the moment Gate S returns.** Nothing else gates
publication.

## 1. Schedule

| Day | What | Notes |
|---|---|---|
| **Sep 5** | **Register the FLLMPT abstract before 23:00 GMT** | Title + 150 words, drawn from §2. Free, dual allowed, **mandatory** for the Sep 12 paper slot there. Not a target — an option that expires. |
| **Sep 8** | **GATE S** (§3) — the same-generator control. Route 1 first: check `RoganInglis/vllm-control-arena`'s columns and generator **before renting anything** (R15 corollary). Route 2 if it does not carry honest LLM solutions to problems in Koran's filter. | Also: pull `runs/scores/` (24 × 1,375, MIT) and recompute the five agentic floors with **task-grouped** CV from `experiments/scan/`. |
| **Sep 8, same day, CPU** | **The token-level confirmation.** AICD App. D.1 names the discriminating identifiers — `answer`, `output`, `result`, `tests`, `index` on the LLM side; `li`, `nums`, `pos`, `a1`, `cur` on the human side. Inspect the top-weighted features of the TF-IDF classifier already fitted in `experiments/apps/` and check whether they match. | ~20 minutes of CPU. It converts a **borrowed** mechanism into a **tested** one in our own setting, and it is the cheapest strengthening available. |
| **Sep 9** | Figures, and the Gate S result routes the headline. | (i) protocol × baseline table; (ii) per-corpus floor bars with permutation nulls beside every bar; (iii) monitor-vs-floor dot plot on Koran's split. |
| **Sep 10–11** | Write four pages. | First paragraph cites `2605.15377`, `2608.16190`, `2602.10153`, `2506.05296`, `2606.06529`, `2510.09462`; Limitations cites `1905.05778` **against ourselves**. |
| **Sep 12** | **Submit to EvoRobust.** Submit to FLLMPT iff the abstract was registered. | EvoRobust is **AoE**; FLLMPT is **23:00 GMT — 13 hours earlier**. Do not learn this on the day. |

## 2. The abstract, as it stands before Gate S

> **Authorship, Not Sabotage: Trivial Baselines on the APPS Backdoor Benchmark**
>
> The stored honest/attack pairs behind open trusted-monitoring results on APPS are human-written vs
> LLM-written. On the field's own filtered, comment-stripped split, a bag-of-words classifier reaches
> AUROC 0.81 and a classifier that reads no code 0.77, above most of the 24 open-weight monitors
> ranked there; the bag-of-words signal transfers across backdoor generators and is as strong on
> inert backdoors as on working ones. Regenerating honest solutions with the attack model removes it.
> We recommend that stored-pair monitor evaluations report partial-input and bag-of-words floors, use
> same-generator honest samples, and drop inert backdoors from both classes.

**Four contributions, each with a number behind it:** (1) the protocol × baseline table; (2) the
authorship mechanism with the same-generator control; (3) the second selection artifact the field's
own filter installs — negative class defined by attack failure, and attack problems carry half the
test cases; (4) the fix, as a drop-in preprocessing step and a released split.

## 3. GATE S — the same-generator control, Sep 8. It decides the title.

The authorship claim needs honest code written by the **attack** model. Two routes, in order:

1. **Look first.** `RoganInglis/vllm-control-arena` (HF, MIT, 200) holds model-generated APPS
   solutions with no honest/attack labels. If those are honest LLM solutions to problems inside
   Koran's filter, **the control is free.** Check its columns and its generator before spending
   anything. *A gate whose value is published is not a gate, it is a lookup.*
2. **Generate.** One 4090; vLLM + `Qwen/Qwen2.5-Coder-7B-Instruct` (or the Llama-3.1-8B whose licence
   is acceptable); one solution per problem for the **3,420 problems with a passing human solution**;
   run the shipped `inputs`/`outputs` tests on CPU; keep the passers. **1–2 GPU-hours, $5–10.**

Then rebuild the pairs — LLM-honest vs LLM-attack, comments stripped, Koran's filter — and rerun
TF-IDF, character n-grams, length, and the seven surface features.

### Two design decisions the neighbouring field settled for us (added 2026-09-04)

Both apply **whichever route supplies the pool**, and both need a sentence in the paper because a
reviewer will ask.

1. **The generator need not be the attacker's model.** The backdoors were written by
   `claude-3-7-sonnet-thinking`; our constraints forbid paid APIs, so a local 7B stands in. The obvious
   objection — *a collapse might just be Qwen-vs-Claude* — is answered by AICD Bench's finding that the
   cues are **language- and generator-independent** (`lit/01` §4), and by our own cross-generator
   transfer at **0.9935**. What the classifier keys on is LLM-ness, not one vendor's style. **This risk
   was never written down before; it is answered now.**
2. **Do NOT length-match the honest class to the human solutions.** CodeMirage gates its two classes to
   agree on line count and character length (`2506.11059` §3.1). That is right for *their* task and
   wrong for ours: **in deployment the untrusted model chooses its own trajectory length**, so matching
   would remove a difference that legitimately belongs to the distribution we are modelling. This is the
   same deployment-realism argument that answers the sharpest reviewer objection (`notes/02`), so it
   costs nothing to state — but it must be stated **deliberately**, not by omission.
   *If space allows*, report both arms — unmatched and post-hoc length-matched. That is a re-slice of
   one pool, not a second generation run.

### The four routes, fixed in advance

TF-IDF scores **0.806** on the stored pairs. On same-generator pairs:

| Result | Headline | Title |
|---|---|---|
| **≤ 0.60** — collapse | **Authorship.** The benchmark as stored measures who wrote the code. | *Authorship, Not Sabotage* — stands |
| **0.60–0.72** — partial | Authorship carries most of the signal; the remainder is surface content. | Stands; the **abstract states the split** |
| **> 0.72** — no collapse | **Content.** These backdoors are separable by surface features regardless of author, and LLM monitors underperform a linear model on them. | New: *A Linear Model Beats the Trusted Monitor.* Same figures, same recommendations. |
| **Route 2 will not run by end of Sep 8** | Ship without the control. The transfer (0.9935 across generators), the inert-backdoor result (0.954 on non-working backdoors), the style markers and the five same-generator settings carry the authorship reading **as inference, stated as such in Limitations.** | Stands |

**All four are a paper.** Do not spend Sep 9 debugging a generator.

## 4. Never cut

- The **exact-split** comparison: train on Koran's paired train (2,418), score their 1,375.
- The **metadata-only floor on that same split**, stated as fitted *within* the test split (their
  train/val is paired, so metadata is balanced there — say it that way, it is a real caveat).
- **Permutation nulls beside every floor.**
- The **Feng `1905.05778` self-citation** in Limitations.
- The **six first-paragraph citations**.
- The **release of the split and the scripts**.
- The sentence that **two of the seven corpora declare no licence**.
- The sentence defending **why we do not length-match**, and the one licensing the **substitute
  generator** (§3). Both are one line; both are the first thing a reviewer probes.

## 5. Cut order if Sep 10–11 slips

1. The CoT-regex paragraph — already a section, not a paper (`2607.09786` owns the instrument).
2. The character-n-gram duplicate of TF-IDF.
3. The fifth agentic setting.

## 6. Stopping rules

- **Gate S route 2 fails** → §3, ship without the control.
- **Sep 10–11 slips** → the November window (`notes/01`) takes it. Nothing is lost but the slot; the
  split, the scripts and the numbers are public either way.
- **The AICD/CodeMirage setup read (`lit/01` §8) comes back occupied** → the *mechanism* claim was
  never ours; the *application* claim stands, and the paper cites them harder. This check runs
  **before** the split is released or the paper is posted, never after (R16).
- **Nothing about C9 before Sep 13.** It stays in the ideation repo.

## 7. Budget

| Item | Cost |
|---|---|
| Everything already computed | $0 |
| Monitor comparison | $0 — `runs/scores/`, MIT |
| Gate S generation | $5–10 |
| Optional same-harness prompted monitor on the regenerated pool | $5–10 |
| **Total** | **≤ $25** |

## 8. Odds, recorded so they can be scored afterwards

Judgment, not measurement — the point is that they are written down before the outcome.

| Path | P(submit) | P(accept ¦ submit) |
|---|---|---|
| EvoRobust, Sep 12 | 0.80 | 0.45–0.55 |
| FLLMPT, Sep 12 | 0.60 — **only if the abstract is registered Sep 5** | 0.30–0.40 |

For the first time in seventeen rounds, the risk on this paper is the writing, not the science.
