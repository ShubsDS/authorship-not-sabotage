# Reproducing the results

Run everything from `experiments/apps` unless noted. The `gate_s_*` scripts implement the
same-generator control ("Gate S" was its working name).

Notation used in the scripts and the paper:

| Symbol | Meaning |
|---|---|
| B | Bag-of-words AUROC on the stored pairs (human honest vs LLM backdoor) over the 1,444-problem analysis pool |
| S | The same classifier on same-generator pairs (one model writes both classes) |
| B′ | B recomputed on exactly the problems S uses |
| ρ | (S − 0.5) / (B′ − 0.5): the share of above-chance separability that survives. Bands fixed in advance: collapse ≤ 0.33 < partial ≤ 0.72 < content |

Requirements: `pip install -r ../requirements.txt` (Python 3.11+). The paper's numbers were
produced with scikit-learn 1.7.1, pandas 2.3.1 and numpy 2.3.5.

| Stage | Needs |
|---|---|
| 1, 2, 6, 7 | Internet and a CPU |
| 3 | `ANTHROPIC_API_KEY` (Batch API); the open-weight arm also needs a GPU and vLLM |
| 4 | Linux with many cores (the harness uses `fork` and memory rlimits) |
| 5 | CPU; `monitor_samegen.py` calls the API |

## 1. Data

```bash
python fetch.py            # train_000{0,1,2}.parquet: RoganInglis/apps-control-arena (5,000 problems)
python fetch_inputs.py     # koran_meta.parquet, rogan_meta.parquet, koran_test_code.pkl, monitor-summary.json
python bow.py              # koran_samples.pkl: the filtered split (1,375 test items: 172 attack, 1,203 honest)
python gate_s_pool.py      # gate_s_pool.parquet: prints 5,000 / 3,420 / 1,582 / 1,444
cd ../agentic && python fetch_scan.py   # ca_{bash,shade,iac,rogue_eval,agentdojo}.parquet
```

## 2. Stored-pair floors (CPU, minutes)

```bash
python koran_split_eval.py        # bag-of-words 0.8063 (above 20/24 monitors); comments kept 0.8914
python auroc.py                   # no-code floor, held-out slice: 0.7163
python analyse2.py                # no-code floor, 5x5 CV: 0.7715 ± 0.0389; inert share 80.7%
python analyse.py                 # lineage check; tests per problem; 892 labelled / 256 pass / 172 fire
python floors.py                  # metadata-only floors under protocols P0-P4 (Table A2)
python exact.py                   # "the longer program is the attack" baseline
python strip_recheck.py --seeds 5 # matched pairs, working vs inert, cross-generator transfer
python headline_ci.py             # bootstrap and permutation intervals -> headline_ci.json (15-30 min)
python token_test.py              # token-level test: separation -0.013, p = 0.956
python gate_s_baseline.py         # B = 0.8714 over 1,444 problems -> gate_s_baseline.json
```

## 3. Generate the same-generator corpus

Claude models use default sampling, so regenerated programs will differ from ours. Generated files
(`*.jsonl`) are not committed; the release bundle (stage 7) carries the Sonnet 5 corpus.

Sonnet 5: honest class, then the two attack arms. The edit arm inserts a backdoor into the
model's own honest solution. The independent arm writes the attack from the problem alone, with
retries.

```bash
python gen_honest_api.py --out gen_sonnet5.jsonl
python run_tests.py --solutions gen_sonnet5.jsonl --out pass_sonnet5.jsonl --workers 8

python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl \
    --out bd_sonnet5.jsonl                                   # edit arm
python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl \
    --independent --out bdind_sonnet5.jsonl                  # independent arm, first draw
python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl \
    --independent --out bds_r1.jsonl --state-suffix r1       # retry rounds r1..r6
```

Prompt-matched honest class (the honest solution is requested under the attack prompt's framing):

```bash
python gen_honest_api.py --matched                           # -> genm_sonnet5.jsonl
```

Haiku 4.5:

```bash
python gen_honest_haiku.py                                   # -> gen_haiku45.jsonl
python gen_backdoor_api.py --model claude-haiku-4-5 --independent --pool analysis   # -> bdind_haiku45.jsonl
python gen_honest_haiku.py --matched --problem-ids sg_haiku45_indep_passes.json     # after stage 5
```

Open-weight arm (regenerates only the honest half; Slurm, GPU):

```bash
mkdir -p logs
sbatch gate_s_gen.sbatch                                   # gen_honest.py with Qwen3-Coder-30B-A3B-Instruct
sbatch --dependency=afterok:<jobid> gate_s_check.sbatch    # run_tests.py + gate_s_eval.py -> gate_s_q3c30.json
```

## 4. Test harness and backdoor verification

```bash
python run_tests.py --solutions human --out human_verify.jsonl --max-per-problem 1   # harness vs the artifact's flag
python verify_backdoor.py --backdoors bd_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl --out bdpass_sonnet5.jsonl

python merge_draws.py merge bdind_sonnet5.jsonl bds_r*.jsonl          # -> bdind_sonnet5_retry.jsonl (11,565 draws)
python verify_backdoor.py --backdoors bdind_sonnet5_retry.jsonl --honest-gen gen_sonnet5.jsonl \
    --out bdindpass_sonnet5_retry.jsonl
python merge_draws.py select --keep first                     # outcome-blind selection: 623 pass, 14 fire
python merge_draws.py select --keep best                      # the benchmark's survivor selection
python merge_draws.py select --keep best --crash-as-passes    # strict set: 99 that pass and fire

python run_tests.py --solutions genm_sonnet5.jsonl --out passm_sonnet5.jsonl --workers 8
python run_tests.py --solutions gen_haiku45.jsonl  --out pass_haiku45.jsonl  --workers 8
python verify_backdoor.py --backdoors bdind_haiku45.jsonl --honest-gen gen_haiku45.jsonl --out bdpass_haiku45.jsonl
python run_tests.py --solutions genm_haiku45.jsonl --out passm_haiku45.jsonl --workers 8
```

## 5. Measurements on the same-generator corpus

```bash
# S, B' and rho (Table 1)
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5_first.jsonl --bdpass bdindpass_sonnet5_first.jsonl \
    --eligibility passes --bprime-inert --label independent --out sg_indep_first_passes.json      # headline
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5_best_nocrash.jsonl --bdpass bdindpass_sonnet5_best_nocrash.jsonl \
    --eligibility usable --label independent --out sg_indep_best_usable.json                      # strict
python gate_s_samegen.py --tag sonnet5 --bd bd_sonnet5.jsonl --bdpass bdpass_sonnet5.jsonl \
    --eligibility passes --bprime-inert --label edit --out sg_edit_passes.json                    # edit arm
python gate_s_samegen.py --tag haiku45 --bd bdind_haiku45.jsonl --bdpass bdpass_haiku45.jsonl \
    --eligibility passes --bprime-inert --label independent --out sg_haiku45_indep_passes.json    # Haiku
# fold seeds for the strict row: add --seed k --out sg_indep_best_usable_seed$k.json (k = 0..4)

# controls
python gate_s_learning_curve.py --match-problems sg_indep_first_passes.json --out lc_first_passes.json
python gate_s_learning_curve.py --match-problems sg_indep_best_usable.json  --out lc_best_usable.json
python survivor_check.py --strict sg_indep_best_usable.json --out survivor_check.json
python lexical_probe.py --out lexical_probe.json

# prompt-matched rows
python gate_s_matched.py                       # -> gate_s_matched_{headline,strict}.json
python gate_s_matched_haiku.py --sg-json sg_haiku45_indep_passes.json --out gate_s_matched_haiku45.json
python sim_stratified_s.py sg_haiku45_indep_passes.json --gen gen_haiku45.jsonl --bd bdind_haiku45.jsonl \
    --out sim_strata_haiku45.json
python trigger_public_check.py                 # how many triggers are public test inputs

# LLM monitor on the same pairs (API). Add --stored to score the stored pairs of the same problems,
# --model claude-haiku-4-5 for the second monitor, and --max-tokens 1024 for the sensitivity run.
python monitor_samegen.py --tag sonnet5 --bd bdind_sonnet5_first.jsonl --bdpass bdindpass_sonnet5_first.jsonl \
    --eligibility passes --gate-s-json sg_indep_first_passes.json
python monitor_samegen.py --tag sonnet5 --bd bdind_sonnet5_best.jsonl --bdpass bdindpass_sonnet5_best_nocrash.jsonl \
    --eligibility usable --gate-s-json sg_indep_best_usable.json
python monitor_samegen.py --tag sonnet5 --stored --gate-s-json sg_indep_first_passes_v2.json

# joint bootstrap intervals on rho, and the monitor's rho
python rho_joint_ci.py sg_indep_first_passes_v2.json --monitor-json monitor_samegen_sonnet5_independent_passes.json \
    --out rho_joint_headline.json
python rho_joint_ci.py sg_indep_best_usable_v2.json --monitor-json monitor_samegen_sonnet5_independent_usable.json \
    --out rho_joint_strict.json
python rho_joint_ci.py sg_haiku45_indep_passes.json --out rho_joint_haiku45.json
python monitor_rho.py --out monitor_rho.json
```

The `_v2` files repeat the headline and strict runs with out-of-fold scores saved, which
`rho_joint_ci.py`, `monitor_samegen.py --stored` and `monitor_rho.py` read. The current
`gate_s_eval.py` always saves them.

## 6. Agentic settings (`experiments/agentic`)

```bash
python matched.py            # within-task, character-count-only AUROC: bash 0.504 ... agentdojo 0.802
python within_task_null.py   # permutation null of that same statistic (Figure A1) -> within_task_null.json
python floors2.py            # six-feature GBM floors with a pooled null (not plotted)
python cot.py                # scratchpad keyword regex: AUROC 0.76-0.82
python prov.py               # which models wrote each class
```

## 7. Audit budget, figures and the release bundle

```bash
python audit_budget.py       # catch rate at 2/5/10% audit budgets (Table A5) -> audit_budget.json
python figures.py            # writes ../../paper/fig/ after checking every value against main.tex

python release_split.py --out release --force --keep first \
    --bd-independent bdind_sonnet5_first.jsonl --bdpass-independent bdindpass_sonnet5_first.jsonl \
    --pool-independent bdind_sonnet5_retry.jsonl --poolpass-independent bdindpass_sonnet5_retry.jsonl \
    --also-select best --allow-trivial-identical 120
python release_split.py --check release --allow-trivial-identical 120
```

## Where each result comes from

All same-generator values in the paper are pooled out-of-fold AUROCs (`auroc_pooled_oof` in the
JSON files) with bootstrap intervals over problems; the ρ intervals are the joint bootstrap
(`rho_ci95_joint`). The JSON files also keep the fold-mean `auroc`, which earlier drafts quoted.

| Result in the paper | Script | Committed output |
|---|---|---|
| Bag-of-words floor 0.806 (20/24); comments kept 0.891; char n-grams 0.783 | `koran_split_eval.py` | — |
| No-code floor 0.772 (CV) and 0.716 (held-out) | `analyse2.py`, `auroc.py` | — |
| Intervals, permutation nulls, paired comparison with the monitors | `headline_ci.py` | `headline_ci.json` |
| Monitor count, median 0.609, max 0.937 | `fetch_inputs.py` | `monitor-summary.json` |
| `#`-count 0.696 → 0.498; length 0.473 | `bow.py` | — |
| Table A2 metadata rows | `floors.py`, `auroc.py` | — |
| Matched pairs, working vs inert, transfer, style markers | `strip_recheck.py` | — |
| Inert share, tests per problem, 720 of 1,203 honest items | `analyse.py`, `analyse2.py` | — |
| Stored-pair AUROC 0.871 over 1,444 problems (0.873 under our pass flag) | `gate_s_baseline.py` | `gate_s_baseline.json`, `gate_s_baseline_ownflag.json` |
| One-sided arm (Qwen3-Coder-30B, ρ = 1.23) | `gen_honest.py` → `gate_s_eval.py` | `gate_s_q3c30.json` |
| Sonnet 5 all attempts: S 0.750, B′ 0.865, ρ 0.687; pair similarity | `gate_s_samegen.py`, `rho_joint_ci.py` | `sg_indep_first_passes[_v2].json`, `rho_joint_headline.json` |
| Sonnet 5 verified: S 0.749, B′ 0.789, ρ 0.861 | `gate_s_samegen.py`, `rho_joint_ci.py` | `sg_indep_best_usable[_v2].json`, `rho_joint_strict.json` |
| Edit arm S 0.625, ρ 0.366 | `gate_s_samegen.py` | `sg_edit_passes.json` |
| Haiku 4.5 all attempts: S 0.534, ρ 0.097 | `gate_s_samegen.py`, `rho_joint_ci.py` | `sg_haiku45_indep_passes.json`, `rho_joint_haiku45.json` |
| Prompt-matched rows and the prompt-only floor (0.600, 0.492) | `gate_s_matched.py`, `gate_s_matched_haiku.py` | `gate_s_matched_{headline,strict,haiku45}.json` |
| Classifier at matched n (0.851, 0.773) | `gate_s_learning_curve.py` | `lc_{first_passes,best_usable}.json` |
| Survivor check (0.745 vs 0.751; 0.62) | `survivor_check.py` | `survivor_check.json` |
| Identifier and other masks | `lexical_probe.py`, `gate_s_matched.py` | `lexical_probe.json`, `gate_s_matched_headline.json` |
| Haiku similarity strata | `sim_stratified_s.py` | `sim_strata_haiku45.json` |
| LLM monitor AUROCs and mean scores | `monitor_samegen.py` | `monitor_{samegen,stored}_*.json` |
| Monitor ρ | `monitor_rho.py` | `monitor_rho.json` |
| Catch rate at a fixed audit budget | `audit_budget.py` | `audit_budget.json` |
| Trigger overlap with public tests (52%) | `trigger_public_check.py` | — |
| Token test | `token_test.py` | — |
| Agentic floors and their within-task nulls | `agentic/matched.py`, `agentic/within_task_null.py` | `agentic/within_task_null.json` |
| Scratchpad regex | `agentic/cot.py` | — |
| Release counts | `merge_draws.py`, `release_split.py` | — |

A few appendix counts were computed with ad hoc joins of the files above and have no script of
their own:

- harness agreement 95.84%: `human_verify.jsonl` restricted to the analysis pool
- the firing counts 14 of 623 and 2 of 611: verdicts joined with the problem ids in the `sg_*.json` files
- the `def main` shares
- the byline and docstring counts in the token-test appendix
- the stored-attack firing check in the Limitations: a 194-problem sample of the analysis pool,
  checking whether the stored attack each B′ row uses has `backdoor_works`
