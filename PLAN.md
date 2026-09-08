# The runbook to Sep 12

Written 2026-09-03, current as of **2026-09-04**. Thresholds, routes and stopping rules are fixed
**now**, before the check that decides the title runs — which is the entire point of writing them
down (`notes/03` R5, R16).

**The human is serial and the GPU is trivial.** The GPU is a held 2× H100 interactive Slurm
allocation, so Gate S costs **$0** and can be re-run. This paper's first commitment is a title, 150
words and a correct author list on **Sep 5**, and its work starts **Sep 8**.

---

## 0. Where this stands

Every CPU number exists (`experiments/`). Gate M is deleted — `runs/scores/` publishes 24 monitors'
per-item scores on the exact 1,375-item split, MIT, no GPU. What remains is **one control, three
figures and four pages**. The risk is in the four pages and in the test harness the control needs —
nowhere else.

**Every check that could void the framing has been run.** G1 is discharged (`lit/01` §4 — both
AI-code-detection neighbours read end to end, both NEIGHBOUR). G2 is discharged for **both** venues
(`notes/01` — EvoRobust conditional on excluding AgentHarm; FLLMPT clear, no organiser or speaker
authored any of our corpora). Under R16, **the split and the paper are clear to be made public the
moment Gate S returns.** Nothing else gates publication.

**The one thing that does not exist yet is the test harness** (§3). It is the critical path, not the
GPU. `experiments/GATE-S-RUNBOOK.md` is the step-by-step execution guide for all of Gate S.

## 1. Schedule

| Day | What | Notes |
|---|---|---|
| **Sep 5** | **Register the FLLMPT abstract before 23:00 GMT** | Title + 150 words from §2, **and the full author list with OpenReview profiles** — the author list is the only thing that locks on this date. The title does not (`notes/01`). Free, dual explicitly allowed. An option that expires. |
| ~~Sep 6–7~~ | ✅ **Harness built and validated 2026-09-04**, three days early. **95.84 %** agreement on the analysis pool → *use our own pass flag for both classes* (`GATE-S-RUNBOOK.md` §4.2). | Three defects found and fixed, all failing old human code specifically. |
| ~~Sep 8~~ | ⏳ **GATE S IS LATE.** The interactive allocation expired 2026-09-07 with nothing generated. Now queued as batch jobs on A100s, estimated start **2026-09-09**. | The only missing number in the paper. Route 4 (§3) applies if it does not land by Sep 10. |
| ~~Sep 8, CPU~~ | ⛔ **RUN EARLY AND NEGATIVE, 2026-09-04.** The AICD App. D.1 token test does **not** replicate here: separation −0.013 in the wrong direction, permutation p = 0.956. `li`, `nums` and `cur` — AICD's canonical *human* identifiers — are among our strongest *attack*-pushing features, because both our classes are competitive-programming code and AICD's human class is general-purpose GitHub code. **The mechanism stays borrowed.** Full record and the by-product finding: `experiments/TOKEN-TEST.md`. | It was the cheapest strengthening available and it did not pay. §3 goes back to **three** ways, and the paper reports the negative in one sentence rather than letting a reviewer run it. |
| ~~Sep 9~~ | ✅ **All three figures built 2026-09-04**, five days early, and every number in them re-verified on this machine (`experiments/REPRODUCED.md`). F1 is a LaTeX table, F2 and F3 are PDFs, captions drafted in `paper/fig/CAPTIONS.md`. | Building F3 caught a crossed protocol/count pairing that had reached the README. |
| **Sep 10–11** | Write four pages. | First paragraph cites `2605.15377`, `2608.16190`, `2602.10153`, `2506.05296`, `2606.06529`, `2510.09462`; Limitations cites `1905.05778` **against ourselves**. |
| **Sep 12** | **Submit to EvoRobust.** Submit to FLLMPT iff the abstract was registered. | EvoRobust is **AoE**; FLLMPT is **23:00 GMT — 13 hours earlier**. Do not learn this on the day. FLLMPT takes the NeurIPS main-track format (9-page limit), so the 4-page PDF drops in legally as-is; disclose the concurrent submission on their form. |

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

   **The compute is a held 2× H100 interactive Slurm allocation, available for days.** It costs
   nothing and can be re-run, which removes the whole class of "we get one shot at the GPU" risk.
   Budget ~15–30 min for the 7B on one GPU and ~30–45 min for the 32B across both. Full command
   sequence in `experiments/GATE-S-RUNBOOK.md` §3.

   > ### ★ The generator protocol — **revised 2026-09-08**
   > **Arm 1 (primary): `Qwen/Qwen3.8-27B`.  Arm 2: `Qwen/Qwen3-Coder-30B-A3B-Instruct`.**
   >
   > <details><summary>What this replaced, and why the original reasoning still binds</summary>
   >
   > Settled 2026-09-04 as `Qwen2.5-Coder-7B-Instruct` + `-32B-Instruct` — same family, two sizes, so
   > the second arm measured **scale**. The reasoning was that a weak honest generator is its own
   > confound with a *directional* failure: the attacks are `claude-3-7-sonnet-thinking`, so if the
   > honest class is a 7B a classifier can separate on **code quality** rather than authorship, which
   > pushes toward *no collapse* — the content headline. A too-weak generator does not add noise, it
   > biases the conclusion, and *"your generator was bad"* cannot be answered after the fact.
   >
   > **That argument is what killed the 7B arm.** Its smoke-tested pass rate was 2/20 on interview-tier
   > problems, which at ~1,444 eligible problems yields on the order of 150–200 pairs — a diagnostic
   > too small to read. The fix is not a weaker second arm, it is two adequate ones.
   > </details>
   >
   > **The second arm now measures generator identity, not scale.** Two models of similar size, one
   > general-purpose and one code-specialised:
   >
   > | arm 1 (Qwen3.8-27B) | arm 2 (Qwen3-Coder-30B) | Reading |
   > |---|---|---|
   > | collapse | collapse | **Authorship, robustly** — not an artifact of one generator |
   > | collapse | no collapse | Generator-specific. Report both; the claim narrows to arm 1's setting. |
   > | no collapse | no collapse | **Content**, and defensible — two unrelated generators agree |
   >
   > **Three details that still bind, unchanged from the original protocol:**
   > 1. ~~Same family, two sizes.~~ **Deliberately abandoned.** With both arms adequate, cross-model
   >    agreement answers *"a collapse might just be Qwen-vs-Claude"* — the sharpest recorded objection
   >    (§3 design decision 1) — which two sizes of one family never could.
   > 2. **One solution per problem, no best-of-n reranking.** Filtering to *passes tests* is correct —
   >    it mirrors Koran's filter on the human class. Any further selection on quality would install a
   >    selection artifact, which is the thing this paper audits. **This one is load-bearing; do not
   >    relax it to buy n.**
   > 3. **Report both n's**, and the pass rate that produced each.
   >
   > **The residual, stated in Limitations rather than implied away:** without a paid API the honest
   > class cannot come from the attack model itself, so some cross-model difference always remains. The
   > evidence that it is small is our own **0.9935** cross-generator transfer and AICD's
   > generator-independence finding. Cite both; do not claim the control is perfect.
   >
   > **If only one arm fits: run arm 1.** It is the one the title routes on.
   >
   > ⚠️ **Two open unknowns, recorded before the run rather than after.** Arm 1 is a *vision-language*
   > model (`image-text-to-text`, `Qwen3_5ForConditionalGeneration`) and general-purpose, so whether it
   > beats a code-specialised model of similar size on APPS is untested. And it is **dense** — all
   > 27.8B active per token, against arm 2's ~3B — so it is several times slower to generate.

   > ### ⚠️ Compute reality, 2026-09-08 — the GPU became the constraint after all
   > The plan said money was not a constraint and the GPU was trivial. Both true; **queue time was
   > neither.** The 4-day interactive allocation (2× H100) expired 2026-09-07 with **nothing
   > generated**. Since then: every H100 on the cluster is held by a job with >3d20h remaining, so the
   > H100 queue does not clear before the deadline. Gate S now runs on **2× A100 with
   > `tensor_parallel_size=2`**, estimated start 2026-09-09.
   >
   > **Structural lesson, not a scheduling anecdote:** a held interactive allocation is not progress.
   > Gate S is now two *batch* jobs (`experiments/apps/gate_s_gen.sbatch` → `gate_s_check.sbatch`,
   > chained with `afterok`) which need nobody attached to a shell, and the GPU job asks for 4 cores
   > rather than 16 so it fits scheduling gaps.

   > ### ⚠️ The real bottleneck: **the test harness does not exist**
   > Nothing in `experiments/` executes code. Grep for `subprocess`, `multiprocessing`, `resource.` or
   > `signal.` across the whole repo returns **nothing**. Gate S needs a runner that feeds each shipped
   > `inputs` case to a solution, compares against `outputs`, sandboxes it, and imposes per-case
   > timeouts — APPS solutions read stdin and can hang. Budget **half a day**, and note it is fragile
   > in the way GPUs are not. **This, not the GPU, decides whether Gate S lands on Sep 8.**
   >
   > Design and validation steps: `experiments/GATE-S-RUNBOOK.md` §4. Two things settled there that
   > change the shape of the work:
   > - **Problem 0 ships 565 test cases**, problem 1 ships 278. One subprocess per test case is
   >   millions of process launches. The harness forks **once per solution**, loops cases in-process
   >   with a patched stdin, and **stops at the first failure**.
   > - **Validate the harness on the human class before generating anything.** It must reproduce the
   >   shipped `solution_passes_tests` (3,420/5,000). If ours is stricter, the LLM honest class gets
   >   filtered harder than the human one and the arms are not comparable — a collapse that is an
   >   artifact of our own checker. The safe default is to use **our own pass flag for both classes**.

   > ### ⚠️ The analysis n is not 3,420 — computed 2026-09-04 by `apps/gate_s_pool.py`
   > Generate for all 3,420 problems with a passing human solution, but a Gate S **pair** also needs a
   > working backdoor and needs to survive the determinism cut. Measured on the full artifact:
   >
   > | Cut | n |
   > |---|---|
   > | `solution_passes_tests` — the **generation pool** | 3,420 |
   > | ∧ `backdoor_works` | 1,582 |
   > | ∧ not `is_nondeterministic` — the **analysis ceiling** | **1,444** |
   >
   > 779 of 5,000 rows are nondeterministic, 717 of them *"multiple distinct valid solutions"*, where
   > exact-match scoring would fail correct generations. The realised n per arm is 1,444 × that arm's
   > pass rate. **Report it; do not let a reader infer 3,420.**
   >
   > **Measured 2026-09-04:** filtered with our own harness rather than the shipped flag, the *human*
   > arm holds **1,384** of those 1,444. The pair count is that intersected with whichever generated
   > solutions pass, so the realised n is at most 1,384.

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

> ### ✅ Consequence for the FLLMPT abstract, Sep 5 — resolved, and it is smaller than it looked
> Route 1 was the only way Gate S could have resolved before the abstract deadline, and it is dead, so
> the Sep 5 abstract is registered three days before the control that decides between *Authorship, Not
> Sabotage* and *A Linear Model Beats the Trusted Monitor*.
>
> **The title-change policy was checked on 2026-09-04 and there is no lock** (`notes/01`): NeurIPS
> main-track policy — which FLLMPT mirrors — freezes the **author list** at the abstract deadline and
> says nothing about the title, and OpenReview permits editing title and abstract until the paper
> deadline. **Gate S can still change the title on Sep 8.**
>
> Still worth writing a route-agnostic title, because it is free. But the binding obligation on Sep 5
> is the **author list with OpenReview profiles**, not the title.

Then rebuild the pairs — LLM-honest vs LLM-attack, comments stripped, the same filter — and rerun
TF-IDF, character n-grams, length, and the seven surface features.

### Two design decisions the neighbouring field settled for us (added 2026-09-04)

Both apply **whichever route supplies the pool**, and both need a sentence in the paper because a
reviewer will ask.

1. **The generator need not be the attacker's model.** The backdoors were written by
   `claude-3-7-sonnet-thinking`; our constraints forbid paid APIs, so a local Qwen coder model stands
   in. The obvious objection — *a collapse might just be Qwen-vs-Claude* — is answered by AICD Bench's
   finding that the cues are **language- and generator-independent** (`lit/01` §4), and by our own
   cross-generator transfer at **0.9935**. What the classifier keys on is LLM-ness, not one vendor's
   style.
2. **Do NOT length-match the honest class to the human solutions.** CodeMirage gates its two classes to
   agree on line count and character length (`2506.11059` §3.1). That is right for *their* task and
   wrong for ours: **in deployment the untrusted model chooses its own trajectory length**, so matching
   would remove a difference that legitimately belongs to the distribution we are modelling. This is the
   same deployment-realism argument that answers the sharpest reviewer objection (`notes/02`), so it
   costs nothing to state — but it must be stated **deliberately**, not by omission.
   *If space allows*, report both arms — unmatched and post-hoc length-matched. That is a re-slice of
   one pool, not a second generation run.

### The four routes, fixed in advance

The Gate S number is the TF-IDF AUROC on **matched pairs, problem-disjoint 5-fold, comments
stripped**, over the eligible pool (`experiments/GATE-S-RUNBOOK.md` §5). The identical pipeline is
also fitted on the **human** honest class over that same pool, giving a baseline **B**; the
LLM-honest number is **G**. Route on **ρ = (G − 0.5) / (B − 0.5)**, the fraction of signal retained.

| ρ | Headline | Title |
|---|---|---|
| **≤ 0.33** — collapse | **Authorship.** The benchmark as stored measures who wrote the code. | *Authorship, Not Sabotage* — stands |
| **0.33–0.72** — partial | Authorship carries most of the signal; the remainder is surface content. | Stands; the **abstract states the split** |
| **> 0.72** — no collapse | **Content.** These backdoors are separable by surface features regardless of author, and LLM monitors underperform a linear model on them. | New: *A Linear Model Beats the Trusted Monitor.* Same figures, same recommendations. |
| **Route 2 will not run by end of Sep 8** | Ship without the control. The transfer (0.9935 across generators), the inert-backdoor result (0.954 on non-working backdoors), the style markers and the five same-generator settings carry the authorship reading **as inference, stated as such in Limitations.** | Stands |

> **Why this is stated as a ratio, and why it is not a loosening.** The bands were originally written
> as raw AUROCs of 0.60 and 0.72, anchored to **0.806** — but 0.806 is TF-IDF trained on Koran's paired
> train split and scored on their exact 1,375-item test split, and that protocol's honest class *is* the
> human code. It cannot be reconstructed once the honest class is regenerated, so the raw bands named
> no runnable protocol. At B = 0.806 the ratio reproduces them exactly:
> 0.5 + 0.33 × 0.306 = **0.601**, 0.5 + 0.72 × 0.306 = **0.720**. Restated **2026-09-04, before the
> run**; 0.806 remains the headline for the stored benchmark and is untouched.

**Route on the 32B arm**; the 7B is the confound diagnostic, read against the 7B × 32B table above.

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

- **Gate S does not land by end of Sep 10** → §3 route 4, ship without the control. Version A of
  `paper/ABSTRACT-evorobust.md` is already route-agnostic; its one control sentence gets deleted and
  the authorship reading is stated as inference in Limitations, in those words.
- **Gate S route 2 fails** → §3, ship without the control.
- **Sep 10–11 slips** → the November window (`notes/01`) takes it. Nothing is lost but the slot; the
  split, the scripts and the numbers are public either way.
- **The harness does not validate against `solution_passes_tests` by end of Sep 7** → use our own
  pass flag for both classes rather than debugging toward upstream's
  (`experiments/GATE-S-RUNBOOK.md` §4.2). Symmetry between the arms is what the control needs;
  matching upstream's checker is not.
- **Nothing about C9 before Sep 13.** It stays in the ideation repo.

The AICD/CodeMirage stopping rule that used to sit here is **spent**: that read ran on 2026-09-03,
came back NEIGHBOUR both ways, and the paper already claims only the application (`lit/01` §4, §8).

## 7. Budget

**$0.** The GPU is a held 2× H100 interactive Slurm allocation and every other number in the paper is
laptop CPU or a published MIT artifact (`runs/scores/`). The optional prompted-monitor arm on the
regenerated pool would also run on that allocation.

**Money is not a constraint on this paper and there is nothing to trade off against it.** The two real
constraints, in order: the **test harness** (half a day, does not exist) and **four pages of prose**
(two days).

## 8. Odds, recorded so they can be scored afterwards

Judgment, not measurement — the point is that they are written down before the outcome.

| Path | P(submit) | P(accept ¦ submit) |
|---|---|---|
| EvoRobust, Sep 12 | 0.80 | 0.45–0.55 |
| FLLMPT, Sep 12 | 0.60 — **only if the abstract is registered Sep 5** | 0.30–0.40 |

The risk on this paper is the writing and the harness, not the science.
