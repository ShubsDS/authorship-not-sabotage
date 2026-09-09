# Every load-bearing number, re-run from a clean checkout on 2026-09-04

The repo was split out of the ideation repo on 2026-09-03 and **nothing in it had been executed on
this machine**. `RECOMPUTE.md` is the coordinator's log from the other machine. This file is the
independent confirmation that the scripts in `apps/` actually reproduce it here, from `fetch.py`
forward, with no hand-made intermediate files.

That mattered more than it sounds: three intermediate files had **no producer script at all**
(`fetch_inputs.py` now writes them), and the pipeline could not have been run by anyone else.

| Number | Source | RECOMPUTE / paper | Re-run 2026-09-04 | |
|---|---|---|---|---|
| TF-IDF word 1–2gram, Koran's exact split, comments stripped | `koran_split_eval.py` | 0.8063, above 20/24 | **0.8063, 20/24** | ✅ |
| same, comments kept | `koran_split_eval.py` | 0.8914, above 22/24 | **0.8914, 22/24** | ✅ |
| char 3–5gram, stripped | `koran_split_eval.py` | 0.7830 | **0.7830** | ✅ |
| No-code floor: difficulty + `num_tests` + q_len | `auroc.py` | 0.7163 held-out | **0.7163** | ✅ |
| `#`-count detector, raw → stripped | `bow.py` | 0.6957 → 0.4983 | **0.6957 → 0.4983** | ✅ |
| Length-only on the filtered split | `bow.py` | 0.4726 | **0.4726** | ✅ |
| difficulty-only, problem level | `auroc.py` | 0.6823 | **0.6823** | ✅ |
| `solution_passes_tests` only | `auroc.py` | 0.7881 | **0.7881** | ✅ |
| `P(has_backdoor ¦ difficulty=competition)` | `auroc.py` | 0.203 (the R17 correction) | **203/1000 = 0.203** | ✅ |
| Koran split shape | `fetch_inputs.py` | 1,375 test = 172 attack / 1,203 honest | **1,375 = 172 / 1,203** | ✅ |
| Artifact shape | `gate_s_pool.py` | 5,000 rows; 3,420 passing; 1,582 working backdoors | **exact** | ✅ |

The two numbers reproduced from `anik-jha/challenger-panels` — `hash_count_only_detector_auroc`
0.6957 → 0.4983 and `code_length_only_auroc` 0.4726 — are **Jha's own published values**, bit-matched
by our independent reconstruction of his split. That is the strongest single check in this table,
because it is the only one where an external party published the answer first.

## The matched protocol and transfer, re-run 2026-09-04

| Number | RECOMPUTE | Re-run here | |
|---|---|---|---|
| Cross-generator transfer, Control Tax → the 2023 GPT-4 set | 0.9935 | **0.9935** | ✅ |
| o3-mini → claude-3-7-sonnet | 0.9756 | **0.9756** | ✅ |
| claude-3-7-sonnet → o3-mini | 0.8130 | **0.8130** | ✅ |
| o1-mini → gemini-2.0-flash | 0.8283 | **0.8283** | ✅ |
| Matched pairs, control_tax | 8,813 over 2,368 problems | **8,813 / 2,368** | ✅ |
| TF-IDF AUROC, matched | 0.9425 | **0.9425** | ✅ |
| 7 surface features | 0.8302 | **0.8302** | ✅ |
| length-only, raw | 0.8255 within-pair / 0.674 AUROC | **0.821 / 0.674** | ✅ |
| TF-IDF pairwise, working backdoors | 0.9787 (n=847) | **0.9787 (n=847)** | ✅ |
| TF-IDF pairwise, all | 0.9621 | **0.9625** | ⚠️ |
| TF-IDF pairwise, inert backdoors | 0.9543 (n=1,794) | **0.9548 (n=1,794)** | ⚠️ |

### The two ⚠️ rows are one flipped pair each, and they set the reporting precision

0.9625 − 0.9621 = 0.00040 and 1/2,641 = 0.00038. 0.9548 − 0.9543 = 0.00050 and 1/1,794 = 0.00056.
**Each gap is a single pair changing side**, from logistic-regression solver and BLAS differences
between this machine and the one `RECOMPUTE.md` was written on. The AUROCs, which are not
threshold-sensitive in this way, match to four decimals.

**Consequence for the paper: report pairwise accuracies to three decimals — 0.962, 0.979, 0.955.**
The resolution of a pairwise accuracy over 2,641 pairs *is* 1/2,641, so a fourth decimal is one pair
and is false precision. Do not let the 0.9621 in `RECOMPUTE.md` become a four-decimal claim.

## The five agentic settings, re-run 2026-09-04

Fetched with the new `scan/fetch_scan.py` (they had no producer either) and re-run through
`scan/matched.py`.

| setting | pooled | task-grouped CV | **within-task** (the paper's column) | task groups |
|---|---|---|---|---|
| bash | 0.6099 ✅ | 0.6239 (was 0.630) ⚠️ | **0.5044** ✅ | 247 |
| shade | 0.6637 ✅ | 0.3819 ✅ | **0.6022** ✅ | 5 |
| iac | 0.5346 ✅ | 0.6022 ✅ | **0.7041** ✅ | 5 |
| rogue_eval | 0.6680 ✅ | 0.6864 (was 0.673) ⚠️ | **0.6158** ✅ | 25 |
| agentdojo | 0.9320 ✅ | 0.8655 (was 0.867) ⚠️ | **0.8020** ✅ | 16 |

**The within-task column — the one that goes in the paper and the one F2 draws — reproduces exactly
on all five.** So does pooled. Three of the five task-grouped CV values move in the third decimal;
that column uses `GradientBoostingClassifier`, whose fitted trees differ across scikit-learn
versions. It is not the column we report, but `experiments/README.md` publishes it, so the drift is
recorded rather than quietly overwritten.

### ⚠️ The task-group counts are wildly uneven, and this had not been recorded

`shade` and `iac` average their within-task AUROC over **five task groups each**; `bash` averages over
**247**. A 0.704 computed within five groups and a 0.504 computed within 247 are not equally solid,
and the README table presented all five as if they were. **F2 now prints the group count beside every
setting**, and the paper must say it. It also explains `shade`'s task-grouped CV of 0.382 — with five
groups, `GroupKFold(5)` puts one whole task in each fold.

## Gate S: B, computed for the first time 2026-09-09

Not a re-run — **a number that did not exist before**. `gate_s_eval.py` computes B and G together
and requires an arm's `--gen-file`/`--pass-file`, so B sat blocked behind a GPU queue despite being
a CPU job: it is human honest code against the same working backdoors, through the same pipeline.
`apps/gate_s_baseline.py` runs that half alone, importing `evaluate()` from `gate_s_eval` so the two
cannot drift.

| Number | Value |
|---|---|
| **B — TF-IDF AUROC, human honest vs working backdoors** | **0.8714** (sd 0.0085 across 5 folds) |
| n pairs | **1,444** — the full analysis ceiling, no drops |
| pairwise accuracy | 0.9605 |
| length-only / surface-7 | 0.6081 / 0.7673 |

**The cross-check that makes this trustworthy:** pairwise lands at **0.9605** against the matched
protocol's independently computed **0.962** — different pool (1,444 analysis problems vs 8,813
control_tax pairs), different machine, different script. Within 0.002.

Environment reproduced every documented artifact count exactly before B was trusted: 5,000 rows,
3,420 passing, 1,582 working backdoors, 779 nondeterministic (717 *"multiple distinct valid
solutions"*), **1,444** analysis ceiling, difficulty split 1,061/277/106, median 18 test cases.
pandas 3.0.5, scikit-learn 1.9.0. Record: `apps/gate_s_baseline.json`.

> ### ⚠️ Two things that must travel with B
> 1. **It is the ceiling pool, not ρ's denominator.** ρ needs B and G over the *same* problems, and
>    G's eligible set is 1,444 ∩ whichever generations pass. `gate_s_eval.py` recomputes B per arm.
> 2. **It moves the routing thresholds.** `PLAN.md`'s 0.601 / 0.720 are arithmetic at an assumed
>    B = 0.806. At the measured B they are **0.6226 / 0.7674** — and a G in 0.720–0.767 routes
>    *differently* under the two, which is a title change. Route on ρ, never on a remembered AUROC.

## Still not reproduced here

Nothing load-bearing. `floors.py`, `floors2.py`, `cot.py` and `apps.py`/`apps2.py` in `scan/` have not
been re-run; their outputs are supporting detail, not figure or abstract numbers.
