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

## Not reproduced here

- The five agentic settings (`scan/`). Their numbers are in `README.md`; the corpora have not been
  re-fetched on this machine.
- Everything in `RECOMPUTE.md` under the DSPy matched protocol (0.9621 pairwise, 0.9935 transfer).
  `matched.py` and `transfer.py` need only `fetch.py` and are cheap; they simply have not been re-run.
