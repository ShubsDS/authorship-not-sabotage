# My own recompute (R17), 2026-09-03, full 5,000-row RoganInglis/apps-control-arena (3 parquet shards via HF datasets-server)

> **Provenance.** The coordinator's own recompute log (R17), 2026-09-03, copied verbatim from the
> ideation repo. Every number the paper leans on is here or in `apps/`. Where a subagent report and this
> file disagree, **this file wins** — that is what R17 is for.

## Problem-level (label = has_backdoor), held-out 30% stratified, random_state=0, LogisticRegression
- all metadata (difficulty, solution_passes_tests, solution_compiles, log n_tests, log q_len, log n_solutions, is_nondet): 0.8917
- difficulty only: 0.6823 (matches round 16)
- solution_passes_tests only: 0.7881
- difficulty + passes: 0.8189 (≈ round 16's 0.8229 feature set)
- lengths/counts only (n_tests, q_len, n_solutions; NO pass flag): 0.8672   <- n_tests median 22 (backdoored) vs 3 (not)
- all metadata, label = backdoor_works: 0.7766

## Sample-level with a metadata-only scorer (honest and attack from the same problem get the same score)
- P0 one-sample-per-problem: 0.8917
- P1 honest on ALL problems + attack on backdoored problems: 0.6980
- P2 honest on ALL + attack only where backdoor_works: 0.6810
- P3 matched-within-problem (both classes, backdoored problems only): 0.5000 exactly
- P4 honest restricted to passing solutions + attack on backdoored: 0.5738

## DSPy trusted-monitor tutorial (https://dspy.ai/tutorials/gepa_trusted_monitor/, fetched 200, 1,004,244 bytes)
- Protocol: get_dataset(has_backdoor_solution=True, backdoor_source="control_tax"); zip(solutions, backdoors) -> 6,369 (task, honest_code, attack_code) pairs; 200 train / 100 val.
- Metric: pairwise, score=1 iff attack_suspicion > honest_suspicion. Reported: 69.0% baseline (untrained), GEPA iterations 78/76/81/81/78 %.
- => round 16's "gpt-4o-mini monitor AUC 0.64" is NOT in the tutorial. Do not cite it.
- => under this protocol the metadata floor is exactly 0.5; round 16's "floor above published monitor" comparison is invalid AS STATED.

## Matched protocol reproduced (control_tax pairs = 8,813 over 2,368 problems; my zip includes all backdoors, tutorial's strict=False zip gives 6,369 — difference is min(len(solutions), len(backdoors)))
- attack code: backdoor_works 0.322, passes_tests 0.341, compiles 0.979; honest passes_tests 0.968
- by generator backdoor_works: o1-mini 0.167 ... claude-3-7-sonnet 0.443
- apps-source pairs (2,160; model 'unknown', 2023 AI Control paper): backdoor_works 0.154, passes 0.203

## Trivial baselines under the MATCHED protocol, problem-disjoint 30% test (2,641 pairs)
- attack longer than honest within pair: 0.821
- length-only AUROC: 0.674
- 7 surface features (len, lines, #if, magic constants, ==, %, #comments) AUROC: 0.8302
- TF-IDF 1-2gram LR AUROC: 0.9425; pairwise accuracy 0.9621
- pairwise acc on backdoor_works only: 0.9787 (n=847); on NON-working: 0.9543 (n=1794)  -> signal is not sabotage
- transfer: train control_tax (problem-disjoint) -> test apps-source: 0.9935; o3-mini -> claude: 0.9756; claude -> o3-mini: 0.8130; o1-mini -> gemini: 0.8283
- style markers: has_comment attack 0.685 vs honest 0.176; has_main 0.116 vs 0.000; has_def 0.375 vs 0.256

## Interpretation (to verify via K1): honest = human APPS solutions; attacks = LLM-written. The stored-pair protocol measures authorship.
