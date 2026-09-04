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
| **Sep 6–7** | **Build and validate the test harness** (`experiments/GATE-S-RUNBOOK.md` §4). | The one piece of Gate S that does not exist. Validate it against the shipped `solution_passes_tests` on the human class *before* generating anything. **This is the critical path.** |
| **Sep 8** | **GATE S** — generate, execute, route (`experiments/GATE-S-RUNBOOK.md`). | Route 1 is dead (§3); route 2 is the only route. Also: pull `runs/scores/` (24 × 1,375, MIT). |
| **Sep 8, same day, CPU** | **The token-level confirmation.** AICD App. D.1 names the discriminating identifiers — `answer`, `output`, `result`, `tests`, `index` on the LLM side; `li`, `nums`, `pos`, `a1`, `cur` on the human side. Refit the `koran_split_eval.py` TF-IDF model and inspect its top-weighted coefficients for those tokens. Nothing is persisted, so this refits rather than loads. | ~20 minutes of CPU. It converts a **borrowed** mechanism into a **tested** one in our own setting, and it is the cheapest strengthening available. |
| **Sep 9** | Figures, and the Gate S result routes the headline. | (i) protocol × baseline table; (ii) per-corpus floor bars with permutation nulls beside every bar; (iii) monitor-vs-floor dot plot on Koran's split. |
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
   > ⚠️ Two arms is ~45 min of H100 but **6,840 solutions to execute instead of 3,420** — the load
   > doubles on the harness, not on the GPU.

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
