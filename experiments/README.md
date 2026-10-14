# Reproducing the results

Run everything from `experiments/apps` unless noted. The `gate_s_*` scripts build and measure the
rebuilt pairs ("Gate S" was the working name of this control).

Names used in the paper, and the names the scripts and JSON files still use for the same thing.
The paper uses no symbol except ρ; the scripts and JSON files keep `S`, `B_prime` and `B` as keys.

| In the paper | Meaning | In the scripts and JSON files |
|---|---|---|
| the dataset | RoganInglis/apps-control-arena, of which we analyse 1,444 problems | `rogan`; "the artifact" or "the analysis pool" in older comments |
| filtered test split | The filtered release of Koran et al. on which the 24 monitors are ranked (1,375 test items) | `koran` |
| original pairs | The pairs that ship with the dataset: per problem, a human-written honest solution and a model-written backdoored solution (the original backdoor) | `stored` |
| rebuilt pairs | Pairs in which one model (Sonnet 5 or Haiku 4.5) writes both the honest and the backdoored solution to the same problem | `samegen`, `sg_*`, `same_generator` |
| original AUROC on all 1,444 problems | Bag-of-words AUROC on the original pairs (human honest against model backdoor) over the 1,444 problems we analyse | `B` |
| original AUROC on the same problems | The same classifier on the original pairs, refitted on exactly the problems the rebuilt pairs cover | `B_prime` (`B′` in older text; in `gate_s_q3c30.json` this value is under `B`) |
| rebuilt AUROC | The same classifier on the rebuilt pairs | `S` |
| open-weight AUROC | The same classifier when only the honest class is regenerated (Qwen3-Coder-30B) and the original backdoors are kept | `G` |
| ρ | (rebuilt − 0.5) / (original − 0.5), with the original AUROC on the same problems: the share of the classifier's above-chance AUROC on the original pairs that remains on the rebuilt pairs. It is not the backdoor's share (the attacks change with the writer). Two lines were fixed in advance, 0.33 and 0.72; Table 2 reports P(ρ > 0.72), the share of joint-bootstrap draws above the line. The monitor's ρ is the same formula with the monitor's AUROCs | `rho`, `retained_vs_stored` |
| works, non-working | A backdoor works if it passes the public tests and gives a wrong answer on the trigger input its writer names | `fire`, `firing`; `inert` |
| all attempts | One attack per problem, chosen before its outcome is known, kept if it passes the public tests; most do not work | `passes`, `first`, `headline` |
| working backdoors | Only attacks that work, drawn from the pool of retries | `usable`, `best`, `strict` |
| variant | How the rebuilt pairs are written: independent (the backdoored solution from the problem statement alone), edit (the model is shown its own honest solution), prompt-matched (the honest solution is requested under the attack prompt's wording). The open-weight variant regenerates only the honest class | `arm`; `independent` / `indep`, `edit`, `matched` |

Statistics, one convention throughout. Every cross-validated point is the pooled out-of-fold
AUROC: one AUROC over all out-of-fold scores, not the mean of the per-fold AUROCs. Every interval
is the bootstrap over problems of that same quantity (2,000 draws; for ρ, joint over the rebuilt
AUROC and the original AUROC on the same problems). Every null is 1,000 label permutations that
shuffle the fitting and the scoring labels alike and rerun the pipeline; p = (1 + #{null ≥
observed}) / (1 + 1,000). Floors fit once and scored once on held-out items (bag-of-words 0.806,
the held-out and outside-split no-code floors) report that one AUROC. The agentic nulls (Figure
F2) permute labels within each task group, because their statistic is within-task. The `auroc`
field of the `sg_*.json` files is the fold mean; `pooled_stats.py` gives every point's pooled
value. Four groups of points predate the pooled field and were regenerated from the generated
files, which reproduces their fold means exactly and adds the pooled values: the open-weight
variant (`gate_s_q3c30.json`, `pooled`), the original AUROC on all problems under our pass flag
(`gate_s_baseline_ownflag.json`, `B_pooled`), the all-attempts length-only AUROC
(`sg_indep_first_passes.json`, `S.length_only_auroc_pooled`) and the Haiku similarity strata
(`sim_strata_haiku45.json`, `S_pooled`, `B_prime_pooled`, `range_over_strata`);
`pooled_stats.json` copies them into its macro map (`pooled_elsewhere`).

Requirements: `pip install -r ../requirements.txt` (Python 3.11+). The paper's numbers were
produced with scikit-learn 1.9.0 and pandas 3.0.5, which `gate_s_baseline.json` records; the
original AUROC on all problems (`B` = 0.8714) reproduces under them. One older output,
`lc_*.json`, records scikit-learn 1.7.1 and pandas 2.3.1; its values are the same under 1.9.0
(`B` and the n = 623 and n = 99 learning-curve points reproduce exactly, `pooled_stats.py
--refit`, checked with numpy 2.5.4). `gate_s_baseline_ownflag.json`, first written under 1.7.1,
was regenerated under 1.9.0 with every earlier value unchanged.

| Stage | Needs |
|---|---|
| 1, 2, 6, 7 | Internet and a CPU |
| 3 | `ANTHROPIC_API_KEY` (Batch API); the open-weight variant also needs a GPU and vLLM |
| 4 | Linux with many cores (the harness uses `fork` and memory rlimits) |
| 5 | CPU; `monitor_samegen.py` calls the API |

## 1. Data

```bash
python fetch.py            # train_000{0,1,2}.parquet: RoganInglis/apps-control-arena (5,000 problems)
python fetch_inputs.py     # koran_meta.parquet, rogan_meta.parquet, koran_test_code.pkl, monitor-summary.json
python bow.py              # koran_samples.pkl: the filtered test split (1,375 test items: 172 attack, 1,203 honest)
python gate_s_pool.py      # gate_s_pool.parquet: prints 5,000 / 3,420 / 1,582 / 1,444
cd ../agentic && python fetch_scan.py   # ca_{bash,shade,iac,rogue_eval,agentdojo}.parquet
```

## 2. Floors on the original pairs (CPU, minutes)

```bash
python koran_split_eval.py        # bag-of-words 0.8063 (above 20/24 monitors); comments kept 0.8914
python auroc.py                   # no-code floor, held-out slice: 0.7163
python analyse2.py                # no-code floor, 5x5 CV fold mean 0.7715 ± 0.0389 (the paper reports
                                  # the pooled 0.7658 from headline_ci.py); non-working share 80.7%
python analyse.py                 # lineage check; tests per problem; 892 labelled / 256 pass / 172 work
python floors.py                  # metadata-only floors under protocols P0-P4 (Table F1; P3 is its
                                  # matched-pairs row)
python exact.py                   # "the longer program is the attack" baseline
python strip_recheck.py --seeds 5 # matched pairs, working vs non-working, transfer across attackers
python headline_ci.py             # bootstrap CIs, 1,000-permutation nulls (one procedure), pooled no-code
                                  # CV 0.7658, paired counts -> headline_ci.json (about 5 min on 10 cores)
python nocode_outside.py          # no-code floor trained outside the test split: 0.2984 (>= 4 tests:
                                  # 0.6293) -> nocode_outside.json
python token_test.py              # token-level test: separation -0.013, p = 0.956
python gate_s_baseline.py         # original AUROC on all 1,444 problems (B) 0.8714 -> gate_s_baseline.json
```

## 3. Generate the rebuilt pairs

Claude models use default sampling, so regenerated programs will differ from ours. Generated files
(`*.jsonl`) are not committed; the release bundle (stage 7) carries the Sonnet 5 rebuilt pairs.

Sonnet 5: honest class, then the backdoored class under two variants. The edit variant inserts a
backdoor into the model's own honest solution. The independent variant writes the backdoored
solution from the problem statement alone, with retries.

```bash
python gen_honest_api.py --out gen_sonnet5.jsonl
python run_tests.py --solutions gen_sonnet5.jsonl --out pass_sonnet5.jsonl --workers 8

python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl \
    --out bd_sonnet5.jsonl                                   # edit variant
python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl \
    --independent --out bdind_sonnet5.jsonl                  # independent variant, first draw
python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl \
    --independent --out bds_r1.jsonl --state-suffix r1       # retry rounds r1..r6
```

Prompt-matched variant (the honest solution is requested under the attack prompt's wording):

```bash
python gen_honest_api.py --matched                           # -> genm_sonnet5.jsonl
```

Haiku 4.5:

```bash
python gen_honest_haiku.py                                   # -> gen_haiku45.jsonl
python gen_backdoor_api.py --model claude-haiku-4-5 --independent --pool analysis   # -> bdind_haiku45.jsonl
python gen_honest_haiku.py --matched --problem-ids sg_haiku45_indep_passes.json     # after stage 5
```

Open-weight variant (regenerates only the honest class; Slurm, GPU):

```bash
mkdir -p logs
sbatch gate_s_gen.sbatch                                   # gen_honest.py with Qwen3-Coder-30B-A3B-Instruct
sbatch --dependency=afterok:<jobid> gate_s_check.sbatch    # run_tests.py + gate_s_eval.py -> gate_s_q3c30.json
```

## 4. Test harness and backdoor verification

```bash
python run_tests.py --solutions human --out human_verify.jsonl --max-per-problem 1   # harness vs the dataset's flag
python verify_backdoor.py --backdoors bd_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl --out bdpass_sonnet5.jsonl

python merge_draws.py merge bdind_sonnet5.jsonl bds_r*.jsonl          # -> bdind_sonnet5_retry.jsonl (11,565 draws)
python verify_backdoor.py --backdoors bdind_sonnet5_retry.jsonl --honest-gen gen_sonnet5.jsonl \
    --out bdindpass_sonnet5_retry.jsonl
python merge_draws.py select --keep first                     # all attempts, chosen blind to outcome: 623 pass, 14 work
python merge_draws.py select --keep best                      # the benchmark's survivor selection
python merge_draws.py select --keep best --crash-as-passes    # working backdoors: 99 that pass and work

python run_tests.py --solutions genm_sonnet5.jsonl --out passm_sonnet5.jsonl --workers 8
python run_tests.py --solutions gen_haiku45.jsonl  --out pass_haiku45.jsonl  --workers 8
python verify_backdoor.py --backdoors bdind_haiku45.jsonl --honest-gen gen_haiku45.jsonl --out bdpass_haiku45.jsonl
python run_tests.py --solutions genm_haiku45.jsonl --out passm_haiku45.jsonl --workers 8
```

## 5. Measurements on the rebuilt pairs

```bash
# rebuilt AUROC (S), original AUROC on the same problems (B_prime) and rho (Table 2)
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5_first.jsonl --bdpass bdindpass_sonnet5_first.jsonl \
    --eligibility passes --bprime-inert --label independent --out sg_indep_first_passes.json      # all attempts
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5_best_nocrash.jsonl --bdpass bdindpass_sonnet5_best_nocrash.jsonl \
    --eligibility usable --label independent --out sg_indep_best_usable.json                      # working backdoors
python gate_s_samegen.py --tag sonnet5 --bd bd_sonnet5.jsonl --bdpass bdpass_sonnet5.jsonl \
    --eligibility passes --bprime-inert --label edit --out sg_edit_passes.json                    # edit variant
python gate_s_samegen.py --tag haiku45 --bd bdind_haiku45.jsonl --bdpass bdpass_haiku45.jsonl \
    --eligibility passes --bprime-inert --label independent --out sg_haiku45_indep_passes.json    # Haiku
# fold seeds for the working-backdoor row: add --seed k --out sg_indep_best_usable_seed$k.json (k = 0..4)

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

# LLM monitor on the same pairs (API). Add --stored to score the original pairs of the same problems,
# --model claude-haiku-4-5 for the second monitor, and --max-tokens 1024 for the sensitivity run.
python monitor_samegen.py --tag sonnet5 --bd bdind_sonnet5_first.jsonl --bdpass bdindpass_sonnet5_first.jsonl \
    --eligibility passes --gate-s-json sg_indep_first_passes.json
python monitor_samegen.py --tag sonnet5 --bd bdind_sonnet5_best.jsonl --bdpass bdindpass_sonnet5_best_nocrash.jsonl \
    --eligibility usable --gate-s-json sg_indep_best_usable.json
#   ^ the working-backdoor monitor run read bdind_sonnet5_best.jsonl, where the classifier read
#     _best_nocrash: the attack differs on 3 of the 99 problems (1701, 1972, 4434: a draw that
#     crashes on its trigger against a later quiet one); monitor_swap.py gives the AUROC without them
python monitor_samegen.py --tag sonnet5 --stored --gate-s-json sg_indep_first_passes_v2.json

# joint bootstrap intervals on rho, and the monitor's rho
python rho_joint_ci.py sg_indep_first_passes_v2.json --monitor-json monitor_samegen_sonnet5_independent_passes.json \
    --out rho_joint_headline.json
python rho_joint_ci.py sg_indep_best_usable_v2.json --monitor-json monitor_samegen_sonnet5_independent_usable.json \
    --out rho_joint_strict.json
python rho_joint_ci.py sg_haiku45_indep_passes.json --out rho_joint_haiku45.json
python monitor_rho.py --out monitor_rho.json

# camera-ready analyses of the committed jsons (CPU, about 5 min in all; * also reads
# train_*.parquet, ** needs train_*.parquet and reads koran_meta.parquet if present). Run
# fire_counts.py first: monitor_swap.py and shared_problems.py read its output.
python pooled_stats.py --refit       # * pooled out-of-fold rebuilt and original AUROCs, rho, joint CIs,
                                     #   P(rho > 0.72) for every point, macro old -> new map -> pooled_stats.json
python fire_counts.py                # * how many backdoors work per Table 2 row; every original backdoor
                                     #   works; exact prompt-matched counts when bdindpass_sonnet5_first.jsonl
                                     #   and bdpass_haiku45.jsonl are here -> fire_counts.json
python monitor_swap.py               # monitor class-swap 2x2, batch provenance, test-retest, working-backdoor
                                     #   file mismatch (names the 3 problems and gives the AUROC without them
                                     #   when bdind_sonnet5_best[_nocrash].jsonl are here) -> monitor_swap.json
python audit_budget.py               # catch rate at 1/2/5% FPR, both monitors and the classifier -> audit_budget.json
python shared_problems.py            # all attempts vs working backdoors on the 64 shared problems -> shared_problems.json
python attacker_mix.py               # ** models that wrote the original backdoors, original AUROC per
                                     #   attacker, Claude-only rho -> attacker_mix.json

# pooled values of the points first committed as fold means (generated files and train_*.parquet;
# no new flags: gate_s_eval.evaluate() writes the pooled length-only AUROC, gate_s_eval.py a
# `pooled` block, gate_s_baseline.py `B_pooled`, sim_stratified_s.py the pooled strata). The
# all-attempts gate_s_samegen.py run and sim_stratified_s.py above regenerate
# sg_indep_first_passes.json and sim_strata_haiku45.json; also:
python gate_s_eval.py --gen-file gen_q3c30.jsonl --pass-file pass_q3c30.jsonl --label q3c30 \
    --out gate_s_q3c30.json                                  # open-weight variant (as gate_s_check.sbatch)
python gate_s_baseline.py --human-pass-file pass_human_fixed.jsonl --out gate_s_baseline_ownflag.json

# classifier class-swap 2x2 (CPU minutes; needs the generated jsonl files and train_*.parquet)
python classifier_swap.py --tag sonnet5 --bd bdind_sonnet5_first.jsonl --bdpass bdindpass_sonnet5_first.jsonl \
    --sg-json sg_indep_first_passes_v2.json --out classifier_swap_sonnet5.json
python classifier_swap.py --tag haiku45 --bd bdind_haiku45.jsonl --bdpass bdpass_haiku45.jsonl \
    --sg-json sg_haiku45_indep_passes.json --out classifier_swap_haiku45.json
```

The `_v2` files repeat the all-attempts and working-backdoor runs with out-of-fold scores saved,
which `rho_joint_ci.py`, `monitor_samegen.py --stored` and `monitor_rho.py` read. The current
`gate_s_eval.py` always saves them.

## 6. Agentic settings (`experiments/agentic`)

```bash
python matched.py    # within-task, character-count-only AUROC: bash 0.504 ... agentdojo 0.802 (Figure F2)
python floors2.py    # within-task permutation nulls (1,000) for Figure F2 -> within_task_null.json
python cot.py        # scratchpad keyword regex: AUROC 0.76-0.82
python prov.py       # which models wrote each class
```

## 7. Figures and the release bundle

```bash
python figures.py    # writes ../../paper/fig/ after checking every value against main.tex

python release_split.py --out release --force --keep first \
    --bd-independent bdind_sonnet5_first.jsonl --bdpass-independent bdindpass_sonnet5_first.jsonl \
    --pool-independent bdind_sonnet5_retry.jsonl --poolpass-independent bdindpass_sonnet5_retry.jsonl \
    --also-select best --allow-trivial-identical 120
python release_split.py --check release --allow-trivial-identical 120
```

## Where each result comes from

| Result in the paper | Script | Committed output |
|---|---|---|
| Bag-of-words floor 0.806 (20/24); comments kept 0.891; char n-grams 0.783 | `koran_split_eval.py` | — |
| No-code floor 0.766 (CV, pooled out-of-fold; 20/24) and 0.716 (held-out; 17/24 on identical items) | `headline_ci.py` (held-out point also `auroc.py`; CV fold mean `analyse2.py`) | `headline_ci.json` |
| No-code floor trained outside the test split 0.298 (at least four tests: 0.629) | `nocode_outside.py` | `nocode_outside.json` |
| Intervals, 1,000-permutation nulls under one procedure, paired comparison with the monitors | `headline_ci.py` | `headline_ci.json` |
| Monitor count, median 0.609, max 0.937 | `fetch_inputs.py` | `monitor-summary.json` |
| Comment count 0.696 → 0.498; length 0.4726 | `bow.py` | — |
| Table F1 metadata rows; matched pairs 0.5000 | `floors.py`, `auroc.py` | — |
| Matched pairs, working vs non-working, transfer, style markers | `strip_recheck.py` | — |
| Non-working share, tests per problem, 892/256/172 | `analyse.py`, `analyse2.py` | — |
| Original AUROC on all 1,444 problems 0.871 (`B`; 0.872 under our harness's pass flag, pooled; fold mean 0.873) | `gate_s_baseline.py` | `gate_s_baseline.json`, `gate_s_baseline_ownflag.json` |
| Open-weight variant (open-weight AUROC 0.961, `G`, against 0.874 on the original pairs of the same problems; ρ = 1.235, joint 1.188–1.288; length-only on the open-weight pairs 0.490; pooled) | `gen_honest.py` → `gate_s_eval.py` | `gate_s_q3c30.json` |
| All attempts: rebuilt AUROC 0.750, ρ = 0.687; pair similarity; length-only 0.5840 (pooled) | `gate_s_samegen.py` (pooled points: `pooled_stats.py`) | `sg_indep_first_passes[_v2].json` (length-only: `sg_indep_first_passes.json`) |
| Working backdoors: rebuilt AUROC 0.749, ρ = 0.861; fold seeds | `gate_s_samegen.py` (pooled points: `pooled_stats.py`) | `sg_indep_best_usable[_v2].json`, `sg_indep_best_usable_seed{0..4}.json` |
| Edit variant: rebuilt AUROC 0.625, ρ = 0.366 | `gate_s_samegen.py` (pooled points: `pooled_stats.py`) | `sg_edit_passes.json` |
| Joint intervals on ρ: all attempts 0.625–0.755, working backdoors 0.662–1.089, Haiku 0.044–0.150 | `rho_joint_ci.py` | `rho_joint_{headline,strict,haiku45}.json` |
| Original AUROC at matched n: 0.851 (n = 623), 0.773 (n = 99) | `gate_s_learning_curve.py` | `lc_{first_passes,best_usable}.json` |
| Survivor check: survivors vs non-survivors 0.62; rebuilt AUROC with non-working attempts 0.745 against 0.751 | `survivor_check.py` | `survivor_check.json` |
| Identifier mask: rebuilt AUROC 0.699 | `lexical_probe.py` (pooled points: `pooled_stats.py`) | `lexical_probe.json` |
| Prompt-matched variant: rebuilt AUROC 0.641, ρ = 0.390 (working backdoors 0.693, 0.662); prompt-only floor 0.600 | `gate_s_matched.py` (pooled points: `pooled_stats.py`) | `gate_s_matched_{headline,strict}.json` |
| Haiku: rebuilt AUROC 0.534, ρ = 0.097 | `gate_s_samegen.py` (pooled points: `pooled_stats.py`) | `sg_haiku45_indep_passes.json` |
| Haiku prompt-matched (rebuilt AUROC 0.539, ρ = 0.110) and similarity strata (pooled rebuilt AUROC 0.4766–0.5170, original AUROC on the same problems 0.7784–0.8255) | `gate_s_matched_haiku.py` (pooled points: `pooled_stats.py`), `sim_stratified_s.py` | `gate_s_matched_haiku45.json`, `sim_strata_haiku45.json` |
| LLM monitor: 0.958 original → 0.566 rebuilt (working backdoors 0.944 → 0.818); Haiku monitor | `monitor_samegen.py` | `monitor_{samegen,stored}_*.json` |
| The monitor's ρ: 0.145 all attempts, 0.717 working backdoors | `monitor_rho.py` | `monitor_rho.json` |
| Trigger overlap with public tests | `trigger_public_check.py` | — |
| Token test | `token_test.py` | — |
| Agentic floors, scratchpad regex | `agentic/matched.py`, `cot.py` | — |
| Agentic within-task nulls (Figure F2) | `agentic/floors2.py` | `agentic/within_task_null.json` |
| Release counts | `merge_draws.py`, `release_split.py` | — |
| Pooled out-of-fold rebuilt and original AUROCs, ρ and joint intervals for every rebuilt-pair point; P(ρ > 0.72); macro map | `pooled_stats.py` | `pooled_stats.json` |
| Backdoors that work, per Table 2 row (14/623, 13/586 prompt-matched, 2/611, 2/562 Haiku prompt-matched, 99/99, 96/96); every original backdoor works | `fire_counts.py` | `fire_counts.json` |
| Monitor class-swap table (0.958 / 0.446 / 0.974 / 0.564; mean suspicion 78.8 / 6.6; working backdoors, human honest vs ours 0.755); batch provenance; working-backdoor file mismatch (1701, 1972, 4434; the monitor's working-backdoor AUROC 0.821 without their attacks, 0.812–0.839 dropping any three) | `monitor_swap.py` | `monitor_swap.json` |
| Catch rate at a fixed false-positive rate (audit budget): Sonnet 5 monitor at 2%, working backdoors 77% original vs 48% rebuilt (difference 0.28, 0.15–0.42), all attempts 85% vs 6% | `audit_budget.py` | `audit_budget.json` |
| All attempts vs working backdoors on the 64 shared problems: ρ 0.82 vs 0.75 (paired difference −0.24 to +0.13) | `shared_problems.py` | `shared_problems.json` |
| Models that wrote the original backdoors; original AUROC per attacker 0.75–0.93; ρ with Claude attackers only (0.715) | `attacker_mix.py` | `attacker_mix.json` |
| Classifier class-swap table: human honest vs our backdoors 0.981 (Haiku 0.973), our honest vs original backdoors 0.956 (0.966), against the rebuilt AUROC 0.750 (0.534) | `classifier_swap.py` | `classifier_swap_{sonnet5,haiku45}.json` |

A few appendix counts were computed with ad hoc joins of the files above and have no script of
their own:

- harness agreement 95.84%: `human_verify.jsonl` restricted to the 1,444 problems we analyse
- the non-working shares 97.75% / 99.67%: verdicts joined with the problem ids in the `sg_*.json` files
- the `def main` shares
- the byline and docstring counts in the token-test appendix

## Pending

- **Working-backdoor monitor re-run with the classifier's attack file.** The working-backdoor
  monitor runs scored `bdind_sonnet5_best.jsonl`, which differs from the classifier's
  working-backdoor row on problems 1701, 1972 and 4434. Re-scoring with the classifier's file
  needs `ANTHROPIC_API_KEY` (about $0.37, worst case $0.67; `--dry-run` prints the estimate) and
  writes to a new file so the committed run is kept:

  ```bash
  python monitor_samegen.py --tag sonnet5 --bd bdind_sonnet5_best_nocrash.jsonl \
      --bdpass bdindpass_sonnet5_best_nocrash.jsonl --eligibility usable \
      --gate-s-json sg_indep_best_usable.json --out monitor_samegen_sonnet5_independent_usable_nocrash.json
  ```

  Until then the paper reports the monitor's AUROC on working backdoors with and without those
  three attacks (0.818 and 0.821).
