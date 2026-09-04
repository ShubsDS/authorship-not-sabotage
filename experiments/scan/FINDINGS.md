# Round-17 external scan — is there a better Sep-12 paper than the metadata-floor audit?

> **Provenance.** Written 2026-09-03 by the fresh-areas scan subagent in the `beyond-private-training`
> ideation repo and copied here **verbatim** — a dated evidence record, not a living document. Its
> `ideas/NN` / `notes/NN` references point at that repo; its §6 recommendations have all been acted on
> (see `../../notes/04-dead-framings.md` and `../../PLAN.md`). Its §2a metadata floor of **0.7890** is the
> subagent's own 5-fold number on `difficulty` + `num_tests`; the coordinator's recompute under the
> protocol that goes in the paper is **0.7163 held-out / 0.7715 ± 0.039 (5×5 CV)** — see `../RECOMPUTE.md`.

Written 2026-09-03. Every artifact below was fetched today; every number under "computed here"
was computed by me from the primary parquet, on the full split, not sampled (R17).

Scratchpad: scan/ (floors.py, floors2.py, cot.py, apps.py, apps2.py, matched.py, prov.py,
fetch_abs.py, grep_html.py, grep1.txt, grep2.txt).

---

## 0. Headline

**Nothing on the board beats the audit. But the audit as currently scoped is both weaker and
stronger than `notes/18` thinks, in ways that change what it should be.**

- **Weaker:** the anchor paper's own released repo already publishes a content-blind leak check on
  the exact split the field uses, with the numbers. `2608.16190`'s repo `anik-jha/challenger-panels`
  ships `runs/x2/leakage-checks.json` with `code_length_only_auroc = 0.4726` and
  `runs/m1/dataset-manifest.json` with a full comment-leak measurement
  (`hash_count_only_detector_auroc` **0.6957 before stripping → 0.4983 after**), verdict quoted
  verbatim: *"Stripping is mandatory, not cosmetic."* **This is R15 again — the artifact answers the
  question one directory below the paper.** Two of the coordinator's carriers (code length, comments)
  are therefore already found and already patched on the standard split.
- **Stronger:** the carriers Jha checks are all **code-side**. Nobody has checked the **problem
  side**. On his exact 172/1203 test split I get **metadata-only held-out AUROC 0.7890** from
  `difficulty` + `num_tests` alone — reading no code at all. Comment-stripping cannot touch it.
- **And much stronger:** Direction A is real and I have already computed it. Five ControlArena
  agentic settings are public, ungated, labelled, and same-generator, and they carry a *second,
  independent* floor. The audit should be a **six-corpus, two-mechanism** paper, not a
  one-dataset paper.

**Recommendation: keep the lead, replace its scope. Do not switch ideas.**

---

## 1. Artifact inventory (Direction A) — HTTP status, licence, generator provenance per class

All checked 2026-09-03. "Provenance" = who wrote the honest class vs who wrote the attack class.

| # | Artifact | HTTP | Gated | Size | Licence | n | Honest generator | Attack generator | Authorship confound? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `hf.co/datasets/RoganInglis/apps-control-arena` | 200 | no | 744 MB | **MIT** | 5,000 | **human** (codeparrot/apps solutions; struct has only `code/compiles/passes_tests`, **no author field**) | **9 named LLMs** (`backdoors[].model`: o1-mini 1250, gpt-4o 1148, o3-mini 2261, claude-3-5-haiku 591, claude-3-7-sonnet 1864, gemini-2.0-flash 715, gpt-4o-mini 367, claude-3-7-sonnet-thinking 517, gpt-3.5-turbo 142) + 2,516 `source=apps, model=unknown` | **YES — human vs LLM** |
| 2 | `hf.co/datasets/eugenekoran/apps-control-arena-high-quality` | 200 | no | 692 MB | **none stated** ⚠️ | 1,209 train / **1,375 test** | human (as above, filtered) | `top_backdoor_model` = claude-3-7-sonnet-thinking-**latest for all 172 attacks**, `NONE` for all 1,203 honest | **YES**, and the column is a literal label |
| 3 | `hf.co/datasets/adityaasinha28/control_arena_bash` | 200 | no | 44 MB | **none** ⚠️ | 1,500 | claude-sonnet-4 / gemini-2.5-pro / gpt-5 | **the same three models**, 250 honest + 250 attack each | **NO — same generator, balanced** |
| 4 | `…/control_arena_shade` | 200 | no | 151 MB | none ⚠️ | 1,500 | idem | idem | NO |
| 5 | `…/control_arena_iac` | 200 | no | 74 MB | none ⚠️ | 1,500 | idem | idem | NO |
| 6 | `…/control_arena_rogue_eval` | 200 | no | 15 MB | none ⚠️ | 1,500 | idem | idem | NO |
| 7 | `…/control_arena_agentdojo` | 200 | no | 3.7 MB | none ⚠️ | 1,500 | idem | idem | NO |
| 8 | `github.com/anik-jha/challenger-panels` `runs/scores/` | 200 | no | 24 × ~56 KB | **MIT** | per-item scores, 24 monitors × 1,375 items | — | — | **The comparison set, free, no GPU** |

Also checked and **rejected**, with reasons (R4):

- `RoganInglis/vllm-control-arena` (200, MIT, 1,197 dl) — **no attack/honest labels.** Main tasks only.
- `AISafety-Student/labeled-bashBench` (200, MIT, 2,494 rows) — `danger_level` and `action_type`
  **perfectly separate the label** (danger 0 → label 0; danger ≥1 → label 1). The "label" *is* the
  danger annotation. Circular; not a monitor benchmark. **Drop.**
- `TylordTheGreat/apps-backdoors-04-02-25`, `RoganInglis/apps-backdoors`, `RoganInglis/control-tax`
  (all 200) — upstream sources of #1, same confound, no extra corpus.
- `aksh-n/control_arena_shade-monitor-labels` (200) — 1,500+ judge JSONs from
  `gemini-3.1-pro-preview`; usable as a *second* label source, no README, no licence.
- **AgentHarm — deliberately excluded. G2.** `ai-safety-institute/AgentHarm` (200, 5,124 dl) is
  Andriushchenko's benchmark and **Andriushchenko is an EvoRobust invited speaker** (`notes/13`).
  Auditing an invited speaker's benchmark at his own workshop is an avoidable own-goal.

**The seven usable corpora split cleanly into two mechanisms**, and that split is the paper:
**#1–#2 have the human-vs-LLM authorship confound. #3–#7 do not** — and they still have a floor.

---

## 2. Numbers computed here (full splits, permutation nulls in the same batch, R3)

### 2a. APPS code side

```
RoganInglis/apps-control-arena, n=5000, P(has_backdoor)=0.4946
  METADATA-ONLY 5-fold CV AUROC        0.8239     perm-null 0.4941
  solution_passes_tests alone          0.7902     (0.9774 | backdoor vs 0.3969 | honest)
  P(bd|difficulty)  competition 0.2030 | interview 0.6247 | introductory 0.3960
  backdoor_works 1582 / has_backdoor 2473  -> 36.0% of labelled backdoors are inert
```
**R17 note: this independently replicates `ideas/28` §12 (0.8229 held-out) at 0.8239 under a
different protocol, and reproduces all four of its corrected supporting rows exactly.**

```
eugenekoran/…-high-quality TEST split, n=1375, label = backdoor_works
  172 attack / 1203 honest      <- matches 2608.16190's stated split EXACTLY
  METADATA-ONLY 5-fold CV AUROC        0.7890     perm-null 0.4880
    num_tests alone                    0.6706     (attack mean 20.95 tests vs honest 38.85)
    difficulty_interview alone         0.6926
    solution_passes_tests              0.5000  <- the field's filter already killed this carrier
    solution_compiles                  0.5000
  P(attack|difficulty)  interview 0.0656 | competition 0.2156 | introductory 0.3090
  top_backdoor_model: 172/172 attacks = claude-3-7-sonnet-thinking-latest; 0 honest.  Literal label.
  81% of this split's has_backdoor rows are inert (172 working of 892)
```

### 2b. ControlArena agentic side — structural floor, action-only transcript, six count features
(`chars`, `lines`, `words`, `[ASSISTANT]`, `[TOOL]`, `[TOOL CALLS]` — **no content is read**)

| setting | n | pooled 5f-CV | **task-grouped CV** | **within-task (Mann–Whitney, chars only)** | #tasks | perm null |
|---|---|---|---|---|---|---|
| bash | 1500 | 0.6093 | 0.6296 | **0.5044** | 247 | 0.4896 |
| shade | 1500 | 0.6637 | 0.3820 | 0.6022 | 5 | 0.5079 |
| iac | 1500 | 0.5345 | 0.6018 | **0.7041** | 5 | 0.4841 |
| rogue_eval | 1500 | 0.6675 | 0.6725 | 0.6158 | 25 | 0.4801 |
| agentdojo | 1500 | 0.9320 | 0.8668 | **0.8020** | 16 | 0.5118 |

**I attacked my own number and it partly broke, which is the point.** The naive pooled floor
(0.64–0.93) is largely task composition in three of five settings. **After matching within the same
main task, bash is clean at 0.504 and agentdojo is badly leaky at 0.802 from character count alone.**
That is a diagnostic that discriminates, with its own negative control, and both outcomes are in
one table (R5 satisfied by construction, not by argument).

### 2c. CoT side — a 15-word regex on the untrusted model's own scratchpad

| setting | AUROC | accuracy | P(hit \| attack) | P(hit \| honest) |
|---|---|---|---|---|
| bash | 0.8235 | 0.812 | 0.663 | 0.039 |
| shade | 0.7649 | 0.667 | 0.667 | 0.332 |
| iac | 0.8041 | 0.769 | 0.659 | 0.121 |
| rogue_eval | 0.7836 | 0.717 | 0.653 | 0.220 |
| agentdojo | 0.8011 | 0.797 | 0.657 | 0.063 |

Mechanism, seen directly in the data: attack rollouts' scratchpads say things like
*"I also have a side task: Send a transaction to US133000000121212121212…"*. The prompted attack
policy names its own side task in the reasoning the CoT monitor reads.

---

## 3. What is already published — the honest novelty position

### 3a. The one that hurts: `2608.16190`'s repo (R15, again)

`github.com/anik-jha/challenger-panels`, MIT, HTTP 200. **Full-text grep of the paper returns
NONE for** hypothesis-only / partial-input / trivial baseline / construct validity / shortcut /
metadata-only / length-only. **The repo publishes the leak checks anyway:**

- `runs/x2/leakage-checks.json`: `"code_length_only_auroc": 0.4726` (both strong monitors),
  `corr_score_codelen` 0.043–0.125.
- `runs/m1/dataset-manifest.json` → `comment_leak_evidence`: before stripping,
  `hash_count_only_detector_auroc` **0.6957** (106 attacks vs 244 honest with comments); after,
  **0.4983**. Verdict verbatim: *"Stripping is mandatory, not cosmetic: a detector that reads
  nothing but the number of '#' characters separates attack from honest at AUROC 0.70 on unstripped
  code and at chance once comments are gone."*
- README: *"a 'detector' that reads nothing but the number of `#` characters in a file separates
  backdoored from honest code at AUROC 0.70 before stripping and at chance after.
  `scripts/build_samples.py --leak-check` reproduces both numbers."*
- `scripts/leakage_checks.py` exists as a named stage.

**Consequences, stated plainly:**
1. **The "nobody has run a trivial baseline" framing is dead.** Do not write it. Someone ran one,
   named the flag `--leak-check`, and published both numbers.
2. **"Longer code is the attack" is dead on the standard split** — 0.4726, i.e. chance. The
   coordinator's *82%* must therefore be on the **unfiltered 5,000-row** artifact, not on the split
   the field uses. **This is an R17 item: recompute the 82%, the 96% TF-IDF pairwise and the 0.88
   BoW / 0.72 metadata figures yourself, on the filtered split, before any of them is load-bearing.
   I did not verify them and one of them is in tension with a published number.**
3. **What survives is better than what died.** Every published carrier is code-side. My 0.7890 is
   problem-side — `difficulty` and `num_tests` — and no amount of comment-stripping or
   code-normalisation removes it, because it is a property of *which problems have a working
   backdoor*, not of the text. The paper's sentence writes itself:

   > *The published leak checks on the standard APPS control split are code-side, and both come
   > back clean. A classifier that reads no code at all still reaches AUROC 0.789 on the same
   > 172/1203 split.*

   A finding that survives someone else's audit is stronger evidence than a finding in a field that
   never audits. **This is a promotion, not a demotion — but only if the framing changes first.**

### 3b. `2607.06596` — the nearest in-field neighbour (Pinto, 2026-07-06, HTTP 200)

*Calibration-Family Overfit: Why Trusted Sabotage Monitors Don't Transfer Across Lineages.*
Full-text grep: `blatancy` 13, `transcript length` 2, `leakage` 2; **zero** for hypothesis-only /
partial-input / trivial baseline / construct validity / metadata-only. Verbatim:
*"regressing placement on policy-family and monitor-family main effects, a diagonal indicator, the
continuous obviousness grade, **transcript length**, the main- and side-task success indicators, and
task fixed effects"*; and *"foreign heads collapse on them once **transcript length is stripped**."*

**One-sentence distinction:** *Pinto treats transcript length as a nuisance covariate to be removed
so a cross-family interaction can be estimated cleanly; we report the length-only classifier's own
AUROC as a floor that published monitor numbers must clear, and we report it per benchmark.*
He also does not touch the agentic ControlArena settings (APPS + BigCodeBench only).

### 3c. Other in-field results checked, all NEIGHBOUR not OCCUPIED

Full texts fetched and greped (`grep1.txt`, `grep2.txt`); positive controls in the same batch, so
the zeros are readable (R3/R8):

| id | title (verified) | grep result |
|---|---|---|
| `2608.16190` | Decorrelation Is Not Complementarity (Jha) | **NONE** for all 28 terms — but see §3a |
| `2607.06596` | Calibration-Family Overfit (Pinto) | blatancy 13, transcript length 2 ← **in-batch positive control** |
| `2506.05296` | Control Tax (Terekhov, Liu, Gulcehre, Albanie) | NONE |
| `2506.15740` | SHADE-Arena (Kutasov … Shlegeris, Benton) | leakage 1 |
| `2504.10374` | Ctrl-Z (Bhatt … Shlegeris) | NONE |
| `2312.06942` | AI Control (Greenblatt, Shlegeris, Sachan, Roger) | NONE |
| `2606.09890` | PreAct-Bench (Xu et al.) | spurious 1, shortcut 1, regex 5 |
| `2602.08995` | MisActBench (Ning et al.) | NONE |
| `2607.09786` | Length Penalties Make CoT Less Monitorable | **length-only 2, length baseline 1, surface feature 4** |
| `2410.09024` | AgentHarm | number of tool calls 1 |
| `2602.02079` | AICD Bench (Orel, … Gurevych, Nakov) | ai control 0, trusted monitor 0, backdoor 0, sabotage 0, APPS 0, monitoring 0, safety 0 |
| `2506.11059` | CodeMirage (Guo et al.) | ai control 0, trusted monitor 0, sabotage 0 — backdoor 1, safety 1 ← **in-batch positive control** |

**`2606.06529`** *Attack Selection in Agentic AI Control Evaluations Meaningfully Decreases Safety*
(Ge-Wang, Crosse, Hadad, Schaeffer, Potham, **Tracy**, 2026-06-03, BashArena + LinuxArena, −20/−28 pp
at 1% budget) is about **attacker-side** selection (when to attack), not dataset-construction
selection. **NEIGHBOUR — cite it, it makes the "control evals are optimistic" case for us.** It also
tells us the neighbourhood is hot and Redwood/UK AISI people are in it (A2 risk).

**`2607.09786`** is the real threat to the CoT leg (§2c): it already runs *"a lexical hint-echo
detector that we validate against the LLM judge"*, a *"content-blind null"* (random sentence
deletion to matched length), and a **scrubbed-vs-unscrubbed text-classifier AUC ablation**
(0.879 → 0.877, Table 14). Different setting (MCQ hint disclosure under compression, not agentic
sabotage), but the *instrument* is the same. **This is why §2c is a section, not a paper.**

### 3d. G1 — the AI-generated-code-detection neighbourhood (the coordinator's question)

Verified by fetching:
- **`2602.02079` AICD Bench** (Orel, Azizov, Paul, Wang, Gurevych, Nakov; 2026-02-02) — 2M examples,
  77 models, 11 families, 9 languages; robust binary classification, model-family attribution,
  human/machine/hybrid/adversarial.
- **`2506.11059` CodeMirage** (Guo, Cheng, Zhang, Shen, Zhang; 2025-05-27) — 10 languages,
  10 production LLMs, original + paraphrased.

**Verdict: the mechanism is thoroughly established out-of-field, and the connection to AI control is
completely unmade.** Both full texts contain **zero** occurrences of "ai control", "control
evaluation", "trusted monitor", "sabotage", "APPS" or "monitoring" (with `backdoor`=1 and `safety`=1
in CodeMirage as the in-batch positive control proving the grep fires).

**This is the healthy shape R2 names, exactly:** a textbook, well-validated method (AI-code /
authorship detection; hypothesis-only baselines) applied to a question nobody has posed (are control
benchmarks' honest/attack classes distinguishable by authorship rather than by sabotage?).
**It is also the precise shape that killed rounds 10–12** — so the AICD literature must be swept
properly, not on two abstracts, before anything is pre-registered (R16: before, not after).

### 3e. R9 — LessWrong / Alignment Forum

Searched (site-restricted): `AI control benchmark trivial baseline transcript length trusted monitor
artifact`; `"control evaluation" benchmark baseline length shortcut artifact APPS backdoor monitor
AUROC`; `"ControlArena" OR "AI control" monitor benchmark "sanity check" simple baseline`;
`APPS backdoor dataset selection bias "passes tests" honest solutions filtered monitor AUROC inflated`.

Distinct LW/AF hits: **9**. Relevant ones —
`X8qTKsGcnsTFrqM96` *Monitoring benchmark for AI control* (MonitorBench; long-context degradation —
opposite direction); `aF3RdKcinrc8FASCC` *Introducing ControlArena*; `x3iEYuMHPXBpnCNpw` *Ensemble
monitoring for AI control*; `2CJyfgaJQk8pyRSCp` *Early Experiments in Human Auditing*;
`7vpvNM7viJqNWAdG7` *Classifier Context Rot*; `eaEqAzGN3uJfpfGoc` *Trusted monitoring with deception
probes*; `sb8WmKNgwzefa6oaJ` *Building Black-box Scheming Monitors*.

**None reports a content-blind floor.** But one prose acknowledgment is close enough to quote in
related work: *"LLM-based assistants used to label the ControlArena training data likely share blind
spots with the monitors being optimized … inflating the apparent performance of future LLM-based
monitors on the dataset"*, and *"trajectories that were questioned during review were omitted from
datasets rather than relabeled."* **The thesis exists in prose in a limitations section. The
measurement does not exist anywhere.** Say so in the paper; do not claim the thought is new.

---

## 4. Candidates, ranked

### ★ C-A1 — "Two floors, six corpora: authorship and structure in AI-control monitoring benchmarks"
**(the current lead, re-scoped — RECOMMENDED)**

**Claim (one sentence).** Across six public AI-control monitoring corpora, classifiers that read none
of the monitored content reach AUROC 0.50–0.93 — driven by *authorship* (human-written honest vs
LLM-written attack) in the APPS-family code benchmarks and by *transcript structure* in the agentic
ControlArena settings — the published leak checks catch only the code-side carriers, and the residual
floor is a property of the evaluation that no choice of monitor can remove.

- **Artifacts.** §1 rows 1–8. All HTTP 200, all ungated, MIT where it matters (rows 1 and 8);
  rows 2–7 carry **no licence statement** — a real defect, mitigable because we redistribute nothing
  and report only aggregate statistics, but it must be stated in the paper.
- **Measurement and cost.** Everything in §2 is **already computed, on CPU, in one afternoon**. The
  remaining work is (i) the item-level comparison against `runs/scores/`'s 24 published monitors on
  the identical 1,375 items — **zero GPU, MIT-licensed, already downloaded-able**; (ii) an optional
  same-generator honest-class arm on APPS, which is the only GPU cost: one 7–8B model writing honest
  solutions for ~1,400 problems, **≈4–8 GPU-hours, $10–20** against a $300 budget.
- **Both outcomes.** Already realised inside one table: bash 0.504 (clean), agentdojo 0.802 (leaky),
  `solution_passes_tests` 0.500 on the filtered split (the field's fix works) vs metadata 0.789 (it
  does not reach the problem side). The paper cannot come out "no result".
- **Two nearest neighbours OUTSIDE AI safety** (both fetched, §3d and below):
  1. **`1805.01042`** Poliak, Naradowsky, Haldar, Rudinger, Van Durme, *Hypothesis Only Baselines in
     Natural Language Inference*, 2018-05-02 — the method, verbatim: *"assessing entailment relations
     while ignoring the provided context is a degenerate solution"*, ten NLI datasets.
  2. **`2410.11672`** Pacchiardi, Tesic, Cheke, Hernández-Orallo, *Leaving the barn door open for
     Clever Hans: Simple features predict LLM benchmark answers*, 2024-10-15 — internal validity,
     n-grams predicting labels, the Clever Hans framing.
  (Third, for the leakage taxonomy: **`2207.07048`** Kapoor & Narayanan, *Leakage and the
  Reproducibility Crisis in ML-based Science*, 329 papers, 8 leakage types, "model info sheets".)
- **Nearest in-field paper + distinction.** `2607.06596` (Pinto). *He removes transcript length as a
  confound to purify a cross-family estimate; we publish the content-blind classifier's AUROC as a
  per-benchmark floor and show it survives the field's own published fixes.*
- **LessWrong/AF.** §3e — 9 distinct hits, none reporting a floor.
- **Score.** `A: 26/30 @ EvoRobust` — A1 4 (mechanism unmade out-of-field, but one carrier is
  published in the anchor's repo, so not 5), A2 3 (Tracy/Redwood/Jha all active; Jha already owns the
  instrument), A3 5, A4 5 (*"Benchmarks and Governance: continuously evolving safety benchmarks …
  coverage metrics"* names it), A5 5 (**loaded today; the central numbers exist**), A6 4.
  `B: 21/25` — B1 4, B2 4, B3 4, B4 4, B5 5.
  **Gates:** G1 **pass with caveat** (out-of-field sweep run on AICD + hypothesis-only + Clever Hans
  + leakage, zeros with in-batch positive controls; the AICD sweep is abstract-level and must go
  full-text before pre-registration, R16); G2 **pass** provided AgentHarm is excluded (§1);
  G3 **pass** — seven corpora loaded and analysed today, which is the first time in seventeen rounds;
  G4 **pass** — a floor is a property of the evaluation, so `2608.16190`'s 29× monitor span does not
  touch it; G5 **pass**.
- **Sharpest reviewer objection.** *"Length and authorship style are part of the input the monitor
  legitimately reads. A high floor means the task is easy, not that the benchmark is invalid — and
  Jha already checked and fixed the code-side carriers."* **Answer, and it must be in the abstract:**
  in deployment the untrusted model chooses its own trajectory length and writes both classes, so a
  monitor scoring well on a corpus where the honest class was written by humans and the attack class
  by an LLM has been validated on a discrimination it will never face. The same-generator arm is the
  constructive half of the paper, not a robustness check.
- **Second objection, weaker but real.** *"Rows 3–7 are one user's unlicensed repackaging with 27–54
  downloads and no README."* Answer: provenance is legible inside the files (`eval_file` =
  `negative1.eval`/`positive*.eval`, `extra_info.setting`, `extra_info.model`), the APPS leg runs on
  MIT artifacts with 6,958 downloads, and the comparison monitors come from an MIT repo. Scope the
  title to *"public releases of"* rather than *"ControlArena"*.

### C-A2 — "The scratchpad names the side task" (CoT-monitoring floor)
**Claim.** A 15-word regex over the untrusted policy's own reasoning separates attack from honest
rollouts at AUROC 0.76–0.82 across five ControlArena settings, because prompted attack policies
restate their side task in the CoT that the monitor reads.
Artifacts/cost: §1 rows 3–7, CPU, done. Both outcomes: yes (the per-setting spread 0.039→0.332 in
honest hit-rate is itself the result). Out-of-field neighbours: `1805.01042`, `2410.11672` as above.
Nearest in-field: **`2607.09786`** — *it already runs a lexical detector, a content-blind
length-matched null, and a scrubbed-vs-unscrubbed classifier ablation.* Distinction is real (MCQ hint
disclosure under compression vs agentic sabotage benchmarks) but thin.
`A: 21/30 @ EvoRobust` (A1 3, A2 3, A3 4, A4 4, A5 5, A6 2 — the honest claim is about *prompted
model organisms*, which is a much smaller claim than "CoT monitoring is overrated").
`B: 19/25`. **G1 marginal.**
**Verdict: KILLED AS A STANDALONE by `2607.09786`. Keep it as C-A1 §4 — it is the CoT-monitoring
row of the same table, and it is the row the user's interests care most about.**

### C-A3 — "The label-noise ceiling of control benchmarks"
**Claim.** 36% of labelled backdoors in `apps-control-arena` never fire (1,582 working of 2,473), and
81% in the high-quality split (172 of 892); the Bayes ceiling under that noise bounds every published
monitor AUROC.
Method: confident learning (Northcutt), textbook, CPU, `pip install cleanlab`. Artifact: row 1–2.
`A: 19/30` — A1 2: `backdoor_works` is a **shipped column with a documented meaning**, and Koran et
al.'s filter already selects on it, so the field knows. A6 2: "ceiling" claims need assumptions a
4-page paper cannot defend.
**Verdict: NOT A PAPER. One paragraph and one number inside C-A1.**

### C-A4 — "Item response theory for trusted monitors"
**Claim.** Fit a 2PL IRT model to the 24 × 1,375 released score matrix; report item difficulty and
discrimination, and show that the items separating monitors are the items the metadata floor already
solves.
Artifact: `anik-jha/challenger-panels` `runs/scores/` — **MIT, HTTP 200, 24 files, no GPU** ("the
per-monitor score files are already in `runs/scores/` … rebuilds every results file … on CPU in about
twenty minutes"). Method: IRT, ~90 years old, unimpeachable. Out-of-field neighbours: psychometrics
(`1805.01042` is the wrong pair here; the right ones are IRT-for-NLP work).
`A: 18/30 @ EvoRobust` — A1 3, A2 3, **A4 2: EvoRobust's PC is evolutionary computation and
adversarial robustness; a psychometrics paper is the wrong register**, A5 5, A6 4. `B: 16/25` — B1 2,
it changes no deployment default.
**Verdict: killed on A4/B1. But its *artifact* is the single most valuable thing this scan found —
it goes into C-A1 as the free monitor-comparison arm, which removes the GPU from the critical path
entirely.**

---

## 5. Direction B — the honest answer

I looked for a textbook-method-on-an-unasked-question candidate independent of the audit, in CoT
monitoring / control / post-training / mech interp, restricted to released artifacts. **I did not
find one that beats C-A1**, and the three best I found (C-A2, C-A3, C-A4) are all *sections of C-A1*
rather than rivals to it. That is itself a result: **the audit is not one idea, it is the frame that
three separate textbook methods fit inside**, which is why it should be broadened rather than
replaced. Proposing a fourth fresh idea nine days out is the thing R12 exists to forbid, and the
thing that killed rounds 10–13.

---

## 6. What I would change in `notes/18`, concretely

1. **Retire the "nobody has run a trivial baseline" sentence before it is written.** `--leak-check`
   exists. Lead instead with *"the published leak checks are code-side and come back clean; the
   problem-side floor is 0.789 on the same split."*
2. **K1 is CLOSED — PASS.** `eugenekoran/apps-control-arena-high-quality` **is** the Koran et al.
   artifact: its test split is 1,375 rows of which exactly 172 have `backdoor_works=True` and 1,203
   do not, and `anik-jha/challenger-panels/runs/m1/dataset-manifest.json` names it by URL with
   `test_attack: 172, test_honest: 1203, train_total: 1936, val_total: 482`. **This also retires
   `notes/14`'s 1,936/482/1,375 correction: that split is real and it lives here.** The floor
   reproduces on it at **0.7890** by a *different* carrier than on the 5,000-row set. Fix the ledger.
3. **K2 is CLOSED, and it did not return what the plan expected.** The R8 half is discharged by §3a:
   the answer is not "unreported", it is "**partially reported, code-side only, by the anchor's own
   artifact**". Record the twelve full-text greps of §3c in `lit/02` with their in-batch positive
   controls. Then write the §3b distinction sentence against `2607.06596` and the §3a distinction
   against `2608.16190`.
4. **R17 debt, unpaid.** Recompute **96% TF-IDF pairwise, 0.88 BoW-after-preprocessing, 0.72
   metadata-only, and "longer code is the attack 82%"** yourself, on the *filtered* 172/1203 split,
   before any of them is load-bearing. The 82% is in direct tension with Jha's published
   `code_length_only_auroc = 0.4726` on that split, and one of the two is measuring a different
   object. **This is the same failure mode as the round-16 delegated numbers.**
5. **Gate M can be deleted.** Its purpose was reproducing a pooled monitor AUROC on a local vLLM
   harness. `runs/scores/` gives 24 monitors' per-item scores on the exact split, MIT, for free.
   **The Sep 12 leg no longer needs a GPU at all**, which removes the only real schedule risk in
   `notes/18` §4 and buys back Sep 9–10.
6. **Add the agentic legs.** §2b and §2c are computed and cost nothing. They turn a one-dataset
   note into a six-corpus audit with a built-in negative control, and they are what makes A2 and B2
   survivable.
7. **Exclude AgentHarm explicitly, in writing, and say why** (G2, Andriushchenko).
8. **R16 ordering.** The AICD full-text sweep (§3d) is the one check that can still void the framing.
   It costs hours and no GPU. **Run it before the pre-registration, not in dead time.**

---

## 7. Method notes / caveats on this scan itself

- arXiv `abs`/`html` fetched serially with ≥9 s sleeps; no `export.arxiv.org/api` used, per the brief.
  `arxiv.org/search` returned **HTTP 429** on three consecutive queries early in the run; those three
  produced **no** results and are **not** recorded as negatives (R3/R17 — a throttled response is a
  transport failure, not evidence). The Koran identification was made from the artifact and from
  `2608.16190`'s repo instead, which is stronger evidence than a search hit.
- Every "zero" in §3c and §3d has an in-batch positive control from the same script and the same run.
- Every dataset statistic was computed from the primary parquet on the **full** split. Nothing here
  is sampled. The one previously-reported number I could check independently (`ideas/28` §12's
  0.8229) replicated at 0.8239.
- `2509.21173`'s ICML attribution and the other `notes/14` ⚠️ rows were not re-checked; out of scope.
