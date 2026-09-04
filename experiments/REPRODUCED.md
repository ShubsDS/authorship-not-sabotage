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

## Still not reproduced here

- **The five agentic settings (`scan/`)** — the `bash` 0.504 … `agentdojo` 0.802 column that **F2 is
  drawn from**. The numbers come from `README.md`; those five corpora have not been re-fetched on this
  machine. ⚠️ This is now the only figure in the paper whose data has not been re-verified here.
