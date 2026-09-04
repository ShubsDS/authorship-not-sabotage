# experiments/ — every number in the paper, and the script that produced it

All of it runs on a **laptop CPU in minutes**. The only GPU anywhere in this paper is Gate S, and it
has its own step-by-step execution guide: [`GATE-S-RUNBOOK.md`](GATE-S-RUNBOOK.md).

```
uv venv && uv pip install pandas pyarrow scikit-learn requests huggingface_hub
cd apps
python fetch.py          # the three RoganInglis parquet shards — everything needs these
python fetch_inputs.py   # koran_meta.parquet, koran_test_code.pkl, monitor-summary.json
python bow.py            # writes koran_samples.pkl
```

**Run order matters, and it used to be undocumented.** `floors.py`, `matched.py`, `exact.py`,
`transfer.py` and `koran.py` need only `fetch.py`. `auroc.py`, `analyse.py` and `analyse2.py` need
`fetch_inputs.py`. `koran_split_eval.py` needs `bow.py` as well. `fetch_inputs.py` is new: the three
files it writes were made by hand in the round-17 session and no script in the repo produced them, so
a fresh clone could not reproduce the headline number.

Nothing here downloads a model. Nothing here contacts a paid API. No artifact is redistributed —
the scripts fetch public HuggingFace datasets and one MIT GitHub repo at run time, and `.gitignore`
keeps the parquets out.

---

## `apps/` — the APPS-family corpora, where the authorship confound lives

The claim's evidence. Two datasets: `RoganInglis/apps-control-arena` (MIT, 5,000 rows, the canonical
ControlArena artifact — `dataset.py:31` hardcodes the name) and
`eugenekoran/apps-control-arena-high-quality` (⚠️ **no licence declared**; 2,584 rows; a filtered
subset of the first, which is what K1 established).

| Script | What it computes |
|---|---|
| `fetch.py` | The three parquet shards, via the HF datasets-server. Run this first. |
| `fetch_inputs.py` | The three intermediate files the scripts below read: `koran_meta.parquet`, `koran_test_code.pkl` (the Koran test split *with* the code structs) and `monitor-summary.json` (Jha's 24-monitor table, MIT). Run this second. |
| `fetch_cols.py` | Column-projected reads over `HfFileSystem` — how to touch 744 MB without downloading it. Called by `fetch_inputs.py`; also usable directly as `python fetch_cols.py <repo> <out.parquet>`. |
| `floors.py` | Problem-level and sample-level **metadata-only** floors under five eval protocols, P0–P4. **P3 (matched-within-problem) is exactly 0.5000** — the number that killed the round-16 headline. |
| `matched.py`, `exact.py` | The DSPy trusted-monitor tutorial's matched-pair protocol reproduced (8,813 control_tax pairs, problem-disjoint 5-fold). TF-IDF, length-only, and the seven surface features. |
| `transfer.py` | Cross-generator transfer of the bag-of-words classifier, plus the style markers (`#`, `__main__`, `def`). **train Control-Tax → test the 2023 GPT-4 set: 0.9935.** Style, not content. |
| `koran.py` | Koran et al.'s filter (working honest + working backdoors, comments stripped) reproduced on the full artifact. Pooled AUROC / pAUC@10% / TPR@10%FPR. |
| `koran_split_eval.py` | **The apples-to-apples number.** Train on Koran's paired train split (2,418), score their exact 1,375-item test split, compare against the 24 monitors in `2608.16190`'s `runs/x0/monitor-summary.json`. |
| `data.py` | Jha's own `src/data.py`, fetched verbatim and imported, so the split reconstruction is his and not ours. |
| `auroc.py`, `bow.py`, `analyse.py`, `analyse2.py` | The K1 agent's lineage check, the metadata AUROCs, the inert-backdoor counts, the leak checks. |

**The headline rows** (full detail in `RECOMPUTE.md`; caveats in `../lit/01`):

| Protocol | Baseline | Result |
|---|---|---|
| Koran's exact split, comments stripped | TF-IDF word 1–2gram | **AUROC 0.8063** — above **20 of 24** monitors (median 0.609) |
| same, comments kept | TF-IDF | 0.8914 — above 22/24 |
| same, **reads no code**: difficulty + `num_tests` + question length | LR | **0.7163 held-out · 0.7715 ± 0.039** (5×5 CV) — above 18/24 |
| DSPy matched pairs, problem-disjoint 5-fold | TF-IDF, pairwise acc | **0.9621**; the tutorial's LLM monitor: 0.69 untrained, 0.78–0.81 GEPA |
| same, split by `backdoor_works` | TF-IDF | working **0.9787** · non-working **0.9543** — the signal is not sabotage |
| same | "the longer code is the attack" | 0.8255 on the raw artifact — and **0.4726, chance, on the filtered split** |
| Inert backdoors | `backdoor_works` | 36.0% raw · **80.7% of Koran's test-split backdoors do not work and are relabelled honest** |

## `scan/` — the five same-generator agentic settings, and the negative control they buy

`adityaasinha28/control_arena_{bash,shade,iac,rogue_eval,agentdojo}` — 1,500 rows each, 250 honest +
250 attack from each of claude-sonnet-4, gemini-2.5-pro and gpt-5. **No authorship confound is
possible here**: the same three models write both classes. ⚠️ None of the five declares a licence;
we redistribute nothing and report aggregates only, and the paper says so.

| Script | What it computes |
|---|---|
| `floors.py`, `floors2.py` | The structural floor from six count features that read **no content** — `chars`, `lines`, `words`, `[ASSISTANT]`, `[TOOL]`, `[TOOL CALLS]`. |
| `cot.py` | The 15-word regex over the untrusted policy's own scratchpad. AUROC 0.76–0.82 across all five settings, because prompted attack policies restate their side task in the reasoning the monitor reads. **One paragraph in the paper, not a section** — `2607.09786` owns this instrument. |
| `bash_bench.py`, `prov.py` | Per-class generator provenance, and the rejection of `AISafety-Student/labeled-bashBench` (its `danger_level` annotation *is* the label — circular). |
| `apps.py`, `apps2.py`, `matched.py` | The scan's own APPS numbers, kept because they are the independent replication of `RECOMPUTE.md`'s. |
| `fetch_abs.py`, `grep_html.py`, `grep1.txt`, `grep2.txt` | The full-text fetch-and-grep pipeline behind the K2 record in `../lit/01`. |

**The column that goes in the paper is the third one**, not the first:

| setting | pooled 5-fold | task-grouped CV | **within-task, chars only** | permutation null |
|---|---|---|---|---|
| bash | 0.609 | 0.630 | **0.504** — clean | 0.490 |
| shade | 0.664 | 0.382 | 0.602 | 0.508 |
| iac | 0.535 | 0.602 | **0.704** | 0.484 |
| rogue_eval | 0.668 | 0.673 | 0.616 | 0.480 |
| agentdojo | 0.932 | 0.867 | **0.802** — leaky | 0.512 |

The scan attacked its own pooled numbers and they partly broke on task composition. That is why the
within-task column is the honest one, and why **both outcomes already sit inside one table**: bash is
clean, agentdojo leaks from character count alone.

## The two standing reports

- `K1-artifact-lineage.md` — which artifact is which, and who wrote each class. **PASS**: one dataset
  and one derived copy, honest code human-written, every backdoor LLM-written, and the confound is a
  property of the **stored-pair** protocol (ControlArena's *live* evals generate both classes).
- `RECOMPUTE.md` — the coordinator's recompute of every load-bearing figure on the full artifact.
  Where a subagent number and this file disagree, this file wins.
