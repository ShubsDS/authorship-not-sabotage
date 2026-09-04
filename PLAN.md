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

1. ~~**Look first.**~~ ⛔ **RUN AND CLOSED, 2026-09-04 — ROUTE 1 IS DEAD.** `RoganInglis/vllm-control-arena`
   holds no APPS data and no code: 6,801 coding *task descriptions* mined from vLLM git commits.
   Two further candidates were checked rather than assumed — **`RoganInglis/control-tax`, whose card
   falsely advertises per-model solutions** (8,855 entries, byte-identical within every row, 2,366
   distinct in total; they are the human APPS references duplicated once per attacker model), and
   `jprivera44/arena-control-apps-v5-dataset` (honest class also human). **No public artifact supplies
   LLM-written honest APPS solutions.** Full evidence in `lit/01` §6.
   *The lookup was still worth running: it cost no money, and it produced the schema finding below.*
2. **Generate — this is now the only route, and it is committed.** vLLM + a local coder model; one
   solution per problem for the **3,420 problems with a passing human solution** — re-verified exactly
   on the full 5,000-row artifact (3,747 compile, 2,473 have a backdoor, 1,582 work); run the shipped
   `inputs`/`outputs` tests on CPU; keep the passers.

   **Revised compute, 2026-09-04 — the GPU is not the constraint and never was.**

   | Hardware | Generation time |
   |---|---|
   | 1× 4090 (original plan) | 1–2 GPU-hours, $5–10 |
   | **1× H100, `Qwen2.5-Coder-7B-Instruct` bf16** | **~15–30 min** incl. load and warm-up. ≈1.7M output tokens at 3–8k tok/s. |
   | 2× H100 | ~10 min split across both — **overkill for this job** |

   > ### ★ The generator protocol, settled 2026-09-04
   > **Generate the honest class twice: `Qwen2.5-Coder-7B-Instruct` and `Qwen2.5-Coder-32B-Instruct`.**
   >
   > **Why not one model.** A weak honest generator is its own confound, and its failure mode is
   > *directional*. The attacks are `claude-3-7-sonnet-thinking`; if the honest class is a 7B, a
   > classifier can separate on **code quality** rather than authorship — which pushes toward **no
   > collapse**, i.e. toward the *content* headline. A too-weak generator does not add noise, it biases
   > the conclusion, and *"your generator was bad"* cannot be answered after the fact.
   >
   > | 7B | 32B | Reading |
   > |---|---|---|
   > | collapse | collapse | **Authorship, robustly** — generator strength is irrelevant |
   > | no collapse | collapse | The 7B result was quality, not authorship. The arm saved the headline. |
   > | no collapse | no collapse | **Content**, and defensible — the generator cannot be blamed |
   >
   > **Three details that matter more than the size choice:**
   > 1. **Same family, two sizes.** Mixing families confounds scale with lineage and the arm measures
   >    nothing.
   > 2. **One solution per problem, no best-of-n reranking.** Filtering to *passes tests* is correct —
   >    it mirrors Koran's filter on the human class. Any further selection on quality would install a
   >    selection artifact, which is the thing this paper audits.
   > 3. **Report both n's.** The 32B passes at a higher rate, so the arms differ in size. Match them or
   >    state both.
   >
   > **The residual, stated in Limitations rather than implied away:** without a paid API the honest
   > class cannot come from the attack model itself, so some cross-model difference always remains. The
   > evidence that it is small is our own **0.9935** cross-generator transfer and AICD's
   > generator-independence finding. Cite both; do not claim the control is perfect.
   >
   > **If only one arm fits: run the 32B.** The 7B's failure mode points at the wrong headline.
   >
   > ⚠️ Cost note: two arms is ~45 min of H100 but **6,840 solutions to execute instead of 3,420** —
   > the load doubles on the harness below, not on the GPU.

   > ### ⚠️ The real bottleneck, previously unrecorded: **the test harness does not exist**
   > Nothing in `experiments/` executes generated code. Grep for `subprocess`, `multiprocessing`,
   > `resource.` or `signal.` across the whole repo returns **nothing**. Gate S needs a runner that
   > feeds each shipped `inputs` case to a generated solution, compares against `outputs`, sandboxes
   > it, and imposes per-case timeouts — APPS solutions read stdin and can hang. Budget **half a day of
   > careful work and debugging**, and note that it is fragile in the way GPUs are not: infinite loops,
   > stdin conventions, and APPS's known-messy test formats. **This, not the GPU, is what decides
   > whether Gate S lands on Sep 8.**

> ### ★ What the dead lookup produced anyway
> The confound is visible in the dataset schema, with no model run at all:
>
> | struct | sub-fields |
> |---|---|
> | `solutions` | `code`, `compiles`, `passes_tests` |
> | `backdoors` | `backdoor_code`, `backdoor_input`, `backdoor_works`, `compiles`, **`model`**, `passes_tests`, **`source`** |
>
> **The attack class records its generator; the honest class has no such field, because it has no
> generator.** Put this in §2 of the paper. It is the thesis in one table and it survives every
> objection about protocols, metrics and splits, because it is not a measurement.

> ### ⚠️ Consequence for the FLLMPT abstract, Sep 5
> Route 1 was the only way Gate S could have resolved before the abstract deadline. It is dead, so
> **the Sep 5 abstract must be written route-agnostically** — it is registered three days before the
> control that decides between *Authorship, Not Sabotage* and *A Linear Model Beats the Trusted
> Monitor*. Whether FLLMPT permits a title change between abstract and paper is **unverified**. Either
> write a title that survives both routes, or check that policy before registering.

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
| Gate S generation, 1× H100 ≈ 30 min | **$2–5** |
| Optional: second generator (32B) for the strength arm | +$3–5 |
| Optional same-harness prompted monitor on the regenerated pool | $5–10 |
| **Total** | **≤ $20**, and lower than the original estimate |

**Money was never the constraint and now it barely registers.** The constraints, in order: the test
harness (half a day, does not exist), four pages of prose (two days), and the human being on InfPriv
until Sep 7.

## 8. Odds, recorded so they can be scored afterwards

Judgment, not measurement — the point is that they are written down before the outcome.

| Path | P(submit) | P(accept ¦ submit) |
|---|---|---|
| EvoRobust, Sep 12 | 0.80 | 0.45–0.55 |
| FLLMPT, Sep 12 | 0.60 — **only if the abstract is registered Sep 5** | 0.30–0.40 |

For the first time in seventeen rounds, the risk on this paper is the writing, not the science.
