# 10 — Reproduction re-check of RESULTS.md §13, §14, §15 (2026-09-11)

Reproduction checker, CPU only. **No API call was made**; nothing that needs a key was run, in
`--dry-run` or otherwise. Every number below was re-derived either from the committed json/log
artifacts or by re-running the script into the scratchpad and diffing the result field-by-field
against the committed json.

Scratchpad used: `/tmp/claude-15569343/-u-fvc9ch-ai-safety-authorship-not-sabotage/b951fd3e-be45-4b77-8341-658828e74071/scratchpad`.
Only this file was written in the repo.

## 0. Re-runs: five scripts, all bit-for-bit

Field-by-field dict diff (floats to 1e-12), committed vs scratchpad rerun:

| script | command | out vs committed | differences |
|---|---|---|---:|
| `rho_joint_ci.py` | `rho_joint_ci.py sg_haiku45_indep_passes.json` | `rho_joint_haiku45.json` | **0** |
| `sim_stratified_s.py` | `… sg_haiku45_indep_passes.json --gen gen_haiku45.jsonl --bd bdind_haiku45.jsonl` | `sim_strata_haiku45.json` | **0** |
| `monitor_rho.py` | `monitor_rho.py` | `monitor_rho.json` | **0** |
| `gate_s_matched_haiku.py` | default args | `gate_s_matched_haiku45.json` | **0** |
| `gate_s_matched.py --only strict` | default inputs | `gate_s_matched_strict.json` | **0** |
| `gate_s_matched.py --only headline` | default inputs | `gate_s_matched_headline.json` | **0** |

Not re-run (needs the API, correctly skipped): `gen_honest_api.py --matched`,
`gen_honest_haiku.py`, `gen_backdoor_api.py`, `monitor_samegen.py`. Their outputs were checked
against their committed logs and jsons instead.

Both `gate_s_matched*.py` scripts assert their own control row against the §9/§15 committed json
before doing anything else, and both assertions hold on the rerun (headline S 0.7512 / B′ 0.8658,
strict S 0.7652 / B′ 0.7877, Haiku S 0.5340 / B′ 0.8584).

---

## 1. §13 — Arm 3, the prompt-matched honest class

### 1.1 Generation and harness (§13.1) — source `genm_sonnet5.log`, `testsm_sonnet5.log`, `passm_sonnet5.jsonl`

| quantity | ledger | reproduced | match |
|---|---|---|---|
| pool | 1,112 | 1,112 (the passers of `pass_sonnet5.jsonl`) | yes |
| requests succeeded / errored | 1,112 / 0 | 1,112 / 0 | yes |
| truncated at `max_tokens` | 12 | 12 | yes |
| no extractable code block | 6 | 6 | yes |
| no ```` ```input ```` block | 13 | 13 | yes |
| tokens | 0.88 M in / 0.72 M out | 0.88 / 0.72 | yes |
| batch wall clock | 12.0 min | 12.0 min | yes |
| ACTUAL COST | $4.48 (est. $3.84) | $4.48 (est. $3.84) | yes |
| harness pass rate | 1,014 / 1,112 = 0.9119 | 1,014 / 1,112 = 0.91187 | yes |
| 98 failures = 80 mismatch / 16 SyntaxError / 1 IndexError / 1 NameError | 98 | 80 + 16 + 1 + 1 = 98 | yes |
| dropped from headline / strict | 37 of 623, 3 of 99 | `n_dropped_matched_fails` 37 / 3 | yes |

### 1.2 Problem sets (§13.2)

| claim | reproduced | match |
|---|---|---|
| headline 586 ⊂ §9's 623 | `set(586) ⊆ set(623)`, and 586 ∪ 37 dropped = the 623 exactly | yes |
| strict 96 ⊂ §9's 99 | 96 ⊆ 99, and 96 ∪ 3 dropped = the 99 exactly | yes |
| §9 ids = `sg_indep_first_passes.json` / `sg_indep_best_usable.json` | equal; also equal to the `_v2` files §14 uses | yes |
| control row reproduces §9 to 4 dp | S 0.7512062968 / B′ 0.8657624749 identical to the committed field | yes |

### 1.3 §13.2 table — every cell, `gate_s_matched_headline.json` / `_strict.json`

All 8 rows × 12 columns checked to the printed precision. **All match.** Spot values:

| quantity | ledger | json | match |
|---|---|---|---|
| headline S_matched AUROC / CI | 0.6423 / 0.6179–0.6621 | 0.6422819774 / 0.6178679–0.6620721 | yes |
| headline S_matched fold sd / pairwise | 0.0195 / 0.652 | 0.0195027 / 0.6519484 | yes |
| headline S_matched length / surface-7 | 0.5569 / 0.5830 | 0.5569127 / 0.5830329 | yes |
| headline S_matched B′ / ρ / joint CI | 0.8613 / 0.394 / 0.326–0.454 | 0.8612635 / 0.3938454 / 0.3261936–0.4539349 | yes |
| headline S_matched ρ S-only CI | 0.326–0.449 | 0.3262658–0.4486256 | yes |
| headline S_original (586) | 0.7572, 0.7327–0.7756, ρ 0.712 (0.636–0.771) | 0.7571992, 0.7326803–0.7756353, 0.7119435 (0.6357681–0.7707779) | yes |
| headline prompt-only floor | 0.6006, 0.5768–0.6243, pairwise 0.551 | 0.6006175, 0.5768338–0.6242977, 0.5511517 | yes |
| strict S_matched | 0.7113, 0.6464–0.7453, B′ 0.8030, ρ 0.697 (0.494–0.856) | 0.7113116, 0.6463759–0.7453396, 0.8030097, 0.6973758 (0.4940292–0.8562381) | yes |
| strict S_original (96) | 0.7836, ρ 0.936 (0.715–1.130) | 0.7836053, 0.9359610 (0.7146947–1.1296498) | yes |
| strict prompt-only floor | 0.6436, 0.5879–0.6912 | 0.6435866, 0.5879449–0.6911947 | yes |
| band mass headline S_matched | P(≤0.33) 0.033, P(>0.72) 0.000 | 0.033 / 0.0 | yes |
| band mass headline S_original | P(content) 0.314 | 0.314 | yes |
| band mass strict S_matched | P(≤0.33) 0.000, P(>0.72) 0.281 | 0.0 / 0.2805 | yes |
| band mass strict S_original | P(content) 0.970 | 0.97 | yes |
| pooled-oof ρ | headline 0.390, strict 0.662 | 0.3902765 / 0.6618195 | yes |
| ΔS headline / Δρ headline | −0.1149 / −0.318 | −0.11492 / −0.3181 | yes |
| "44.7% of the signal above chance" | 44.7% | 0.11492 / 0.25720 = 44.68% | yes |
| ΔS strict / Δρ strict | −0.0723 / −0.239 | −0.07229 / −0.2386 | yes |
| "length-only at or near chance (0.519–0.589)" | 0.519–0.589 | min 0.5193, max 0.5886 | yes |

### 1.4 §13.3 masks and char n-gram — all 12 rows match

| quantity | ledger | json | match |
|---|---|---|---|
| headline S_matched [ID] | 0.6264, 0.6035–0.6445, B′ 0.8695, ρ 0.342 (0.280–0.394) | 0.6264319, 0.6034589–0.6444675, 0.8695223, 0.3421496 (0.2795510–0.3944091) | yes |
| headline S_original [ID] | 0.7046, 0.6807–0.7252, ρ 0.554 (0.490–0.616) | 0.7045934, 0.6807161–0.7252180, 0.5536699 (0.4899771–0.6158571) | yes |
| headline prompt-only [ID] | 0.5744, 0.5549–0.5949 | 0.5744152, 0.5548735–0.5949300 | yes |
| headline S_matched [char_wb] | 0.6817, 0.6571–0.7007, B′ 0.8681, ρ 0.493 (0.422–0.552) | 0.6816753, 0.6570922–0.7006689, 0.8681401, 0.4934950 (0.4223291–0.5524972) | yes |
| headline prompt-only [char_wb] | 0.6254, 0.6010–0.6500 | 0.6254067, 0.6009851–0.6499573 | yes |
| strict S_matched [ID] / [char_wb] | 0.7251 / 0.7143 | 0.7251080 / 0.7142576 | yes |
| strict S_original [ID] | 0.7416, ρ 0.689 (0.502–0.856) | 0.7415803, 0.6886462 (0.5017380–0.8561251) | yes |
| strict prompt-only [ID] / [char_wb] | 0.6191 / 0.6790 | 0.6191420 / 0.6790104 | yes |
| "ID cost S_original 0.0526" | 0.0526 | 0.7571992 − 0.7045934 = 0.052606 | yes |
| "costs S_matched 0.0159" | 0.0159 | 0.6422820 − 0.6264319 = 0.015850 | yes |

### 1.5 §13.4 presence and top features — all match

All 50 presence cells (5 probes × 5 classes × 2 sets) reproduce to three decimals against
`presence` in the two jsons. All 10 + 10 headline S_matched feature weights and all 10 + 5
prompt-only weights reproduce to two decimals against `attribution`. `main (` +2.26 in §11.3 →
+1.58 here = 0.698 of the weight, so "roughly two-thirds" holds.

### 1.6 §13.5 pair similarity — all 32 cells match

| quantity | ledger | json | match |
|---|---|---|---|
| headline matched-vs-attack | 0.716 / 0.727 / 7.0% / 25.9% | 0.7162303 / 0.7269856 / 6.997% / 25.939% | yes |
| headline original-vs-attack (586) | 0.664 / 0.678 / 3.6% / 33.6% | 0.6638270 / 0.6780260 / 3.584% / 33.618% | yes |
| headline original-vs-matched | 0.764 / 0.788 / 16.4% / 18.8% | 0.7636039 / 0.7878166 / 16.382% / 18.771% | yes |
| headline stored, same problems | 0.602 / 0.625 / 3.4% / 46.1% | 0.6020316 / 0.6245225 / 3.413% / 46.075% | yes |
| strict, four rows | 0.656 / 0.618 / 0.774 / 0.659 | 0.6563283 / 0.6182642 / 0.7735695 / 0.6586750 | yes |
| "+0.052 headline, +0.038 strict" | 0.052 / 0.038 | 0.05240 / 0.03806 | yes |

### 1.7 §13.6 reading — arithmetic all correct, one band statement to soften

| quantity | ledger | reproduced | match |
|---|---|---|---|
| "S_matched sits 0.042 above the floor" | 0.042 | 0.6422820 − 0.6006175 = 0.04166 | yes |
| "of the 0.142 that remains above chance, 0.100 is the floor" | 0.142 / 0.100 | 0.14228 / 0.10062 | yes |
| "stays 0.068 above the floor of 0.6436" (strict) | 0.068 | 0.7113116 − 0.6435866 = 0.06773 | yes |
| "collapse excluded … by the headline row at 97% of draws" | 97% | 1 − 0.033 = 96.7% | yes |
| "97.5% of which never fire" (headline set) | 97.5% | **97.75%** — 14 of 623 fire | **no, see D5** |
| "partial, content excluded" | — | joint CI 0.326–0.454 **dips below the 0.33 collapse line** | see I1 |

---

## 2. §14 — monitors with authorship held constant

### 2.1 Problem sets and pair construction

| claim | reproduced | match |
|---|---|---|
| stored pairs built on the row's own ids | score `problem_id` set == `B_prime.oof` id set: 623 == 623, 99 == 99 | yes |
| "623 of 623 and 99 of 99" asserted | `stored_pairs_meta.n_problems_in_row` 623 / 99, `n_no_stored_pair` 0 | yes |
| same-generator Haiku rows on the same ids | score ids == `S.oof` ids, 623 and 99 | yes |
| B′ rule per row | `passes (inert-inclusive)` / `passes AND fires`, from the row's own `--gate-s-json` | yes |
| honest side = `data._honest_code` shipped flag | `b_prime_honest_flag: shipped (_honest_code)` in both | yes |
| `prompt_sha256 14b320ea6a533dd4` in all ten runs | present and identical in all 10 monitor jsons | yes |
| §9 `_v2` ids == the non-`_v2` ids §13 used | equal for both rows | yes |

### 2.2 §14.1 costs — source: the ten monitor jsons' `run.cost_usd`

| quantity | ledger | reproduced | match |
|---|---|---|---|
| eight batch costs | 1.93 / 0.29 / 2.39 / 0.36 / 1.82 / 0.28 / 0.33 / 0.31 | 1.9339 / 0.2883 / 2.3868 / 0.3620 / 1.8206 / 0.2757 / 0.3262 / 0.3093 | yes (each rounded up) |
| Worker B total $7.71 | 7.71 | sum of the eight rounded = 7.71 (raw 7.7027) | yes |
| §10 Sonnet same-gen not re-run, reproduced to 4 dp | 0.5662, 0.8182 | 0.5662498808, 0.8181818182 | yes |

### 2.3 §14.2 stored-pairs table — all 5 rows × 9 columns match

| quantity | ledger | `monitor_rho.json` | match |
|---|---|---|---|
| headline Sonnet M_stored / CI | 0.9579 / 0.9466–0.9683 | 0.9578720 / 0.9466413–0.9682950 | yes |
| headline Sonnet Δ vs B′ / CI / P | +0.0932 / +0.0752,+0.1099 / 1.000 | 0.0932316 / 0.0751558–0.1098721 / 1.0 | yes |
| headline Sonnet pairwise / means / missing | 0.9562 / 6.9 / 78.8 / 6 of 1,246 | 0.9562399 / 6.8742 / 78.8452 / 6 | yes |
| headline Haiku M_stored / Δ / P / missing | 0.8824 / +0.0177 (−0.0108,+0.0447) / 0.888 / 458 | 0.8823771 / 0.0177368 (−0.0108480,+0.0446536) / 0.8885 / 458 | yes (see R1) |
| strict Sonnet | 0.9437 / +0.1548 (+0.1071,+0.2016) / 1.000 / 0.9184 / 6.8 / 73.8 / 1 | 0.9437229 / 0.1548239 (0.1070856,0.2016206) / 1.0 / 0.9183673 / 6.8384 / 73.7551 / 1 | yes |
| strict Haiku | 0.8832 / +0.0943 (+0.0200,+0.1630) / 0.994 / 0.8778 / 32.9 / 84.7 / 70 | 0.8831880 / 0.0942890 (0.0199781,0.1630442) / 0.994 / 0.8777778 / 32.8727 / 84.6712 / 70 | yes |
| strict Haiku mt1024 | 0.8765 / +0.0876 (+0.0268,+0.1437) / 0.998 / 0.8387 / 34.9 / 81.1 / 6 | 0.8765057 / 0.0876066 (0.0267942,0.1437307) / 0.998 / 0.8387097 / 34.8737 / 81.0928 / 6 | yes |
| "Sonnet strict honest 3.5 here, 3.4 in §10" | 3.5 / 3.4 | 3.4545 (all scored) vs 3.4388 (complete pairs) | yes |

### 2.4 §14.3 monitor-ρ table — all 5 rows match

| quantity | ledger | json | match |
|---|---|---|---|
| headline Sonnet M_samegen / monitor-ρ / CI / P(ρ<1) | 0.5662 (0.5507–0.5833) / 0.145 (0.111–0.182) / 1.000 | 0.5662499 (0.5506821–0.5832906) / 0.1446908 (0.1107413–0.1824362) / 1.0 | yes |
| headline Haiku | 0.5577 (0.5239–0.5919) / 0.151 (0.063–0.242) / 1.000 | 0.5577290 (0.5238749–0.5919008) / 0.1509739 (0.0628023–0.2419000) / 1.0 | yes |
| strict Sonnet | 0.8182 (0.7630–0.8686) / 0.717 (0.601–0.832) / 1.000 | 0.8181818 (0.7630405–0.8686353) / 0.7170732 (0.6008301–0.8321189) / 1.0 | yes |
| strict Haiku | 0.7871 (0.6946–0.8699) / 0.749 (0.514–0.993) / 0.978 | 0.7870998 (0.6945689–0.8699400) / 0.7492399 (0.5140363–0.9934286) / 0.978 | yes |
| strict Haiku mt1024 | 0.7883 (0.7237–0.8494) / 0.766 (0.588–0.963) / 0.992 | 0.7883474 (0.7236784–0.8493794) / 0.7658513 (0.5880546–0.9629397) / 0.9915 | yes |
| classifier ρ column | headline 0.687 (joint 0.625–0.755); strict 0.921 fold-mean / 0.861 pooled (joint 0.662–1.089) | 0.6868017 / 0.6247161–0.7551289; 0.9214741 / 0.8612043 / 0.6616333–1.0887891 | yes |
| "joint ρ reproduces §12.2 to ten decimals" | headline 0.6247161073–0.7551289416, strict 0.6616333226–1.0887890957 | identical to `rho_joint_headline.json` / `rho_joint_strict.json` | yes |
| pairwise + class means line | 0.6043 4.0/6.9; 0.6268 27.9/34.0; 0.8163 3.5/37.6; 0.7439 26.7/62.5; 0.7680 27.1/60.4 | 0.6043339 4.0385/6.9262; 0.6267943 27.8725/33.9679; 0.8163265 3.4545/37.5816; 0.7439024 26.7321/62.5000; 0.7680412 27.1134/60.4040 | yes |
| same-gen missing | Sonnet 0 / 1; Haiku 628 / 84 (2 at mt1024) | 0 / 1; 628 / 84 / 2 | yes |

### 2.5 §14.4 agreement — all 4 rows × 5 columns match

| pair set / row | ledger | json | match |
|---|---|---|---|
| same-gen headline | 209 / +0.114 / +0.547 / +0.500 / 0.569 | 209 / 0.1144548 / 0.5466217 / 0.5002170 / 0.5693780 | yes |
| same-gen strict | 41 / +0.809 / +0.878 / +0.552 / 0.780 | 41 / 0.8085131 / 0.8780888 / 0.5521836 / 0.7804878 | yes |
| stored headline | 262 / +0.573 / +0.549 / +0.634 / 0.821 | 262 / 0.5732352 / 0.5494111 / 0.6341520 / 0.8206107 | yes |
| stored strict | 45 / +0.723 / +0.489 / +0.696 / 0.800 | 45 / 0.7229977 / 0.4892349 / 0.6955359 / 0.8 | yes |
| "0.88 vs 0.96 stored headline; 0.79 vs 0.82 same-gen strict" | — | 0.8824/0.9579; 0.7871/0.8182 | yes |
| "agrees to within 0.01 headline / 0.03 strict" | 0.01 / 0.03 | 0.0063 / **0.0322** | **no, see D4** |

### 2.6 §14.5 truncation defect — all match

| quantity | ledger | reproduced | match |
|---|---|---|---|
| "512-token ceiling on 635 of 1,246 headline replies" | 635 | `run.n_truncated` 635 | yes |
| "~50% of Haiku headline scores missing" | ~50% | 628 / 1,246 = 50.4% unparsed | yes |
| stored headline missingness by class | honest 50.1% / attack 23.4% | 312/623 = 50.08% / 146/623 = 23.43% | yes |
| stored strict missingness by class | 44.4% / 26.3% | 44/99 = 44.44% / 26/99 = 26.26% | yes |
| mt1024 missingness | 2 of 198 and 6 of 198 | 2 / 6 | yes |
| AUROC moves | +0.0012 same-gen, −0.0067 stored | +0.0012476 / −0.0066823 | yes |
| monitor-ρ 0.749 → 0.766 | — | 0.7492399 → 0.7658513 | yes |
| "0.5577, CI 0.5239–0.5919" | — | same | yes |
| same-gen headline missingness is class-balanced | implied by "50% class-balanced sample" | honest 317 (50.9%) / attack 311 (49.9%) | yes |

### 2.7 §14.6 classifier-wrong pairs — all 6 rows match

| run | ledger n / AUROC / CI | json | match |
|---|---|---|---|
| Haiku same-gen headline | 131 / 0.5694 / 0.4926–0.6441 | 131 / 0.5694039 / 0.4926–0.6441 | yes |
| Haiku same-gen strict | 15 / 0.6750 / 0.4000–0.9065 | 15 / 0.675 / 0.4–0.9065 | yes |
| Sonnet stored headline | 18 / 0.9275 / 0.8148–0.9938 | 18 / 0.9274691 / 0.8148–0.9938 | yes |
| Sonnet stored strict | 7 / 0.8163 / 0.5408–1.0000 | 7 / 0.8163265 / 0.5408–1.0 | yes |
| Haiku stored headline | 18 / 0.9135 / 0.7067–1.0000 | 18 / 0.9134615 / 0.7067–1.0 | yes |
| Haiku stored strict | 7 / 0.6667 / 0.1429–1.0000 | 7 / 0.6666667 / 0.1429–1.0 | yes |

Not reported by §14.6: the Haiku stored-strict row had **34 of 2,000 degenerate bootstrap draws**
(`n_boot_degenerate: 34`) and the Haiku same-gen strict row 3. The row is already labelled
"recorded, not read", so this changes nothing, but the flag belongs beside it.

---

## 3. §15 — Claude Haiku 4.5 as the second same-generator model

### 3.1 Generation (§15.1) — source `honest_haiku45.log`, `bdind_haiku45.log`, `genm_haiku45.log`

| quantity | ledger | reproduced | match |
|---|---|---|---|
| honest: 1,444 / 1,444 / 0 errored / 3 truncated / 1 no code | — | identical | yes |
| honest tokens / cost | 0.79 M / 1.49 M, $4.13 | identical | yes |
| honest wall clock | 7 min | ended at 7.0 min | yes |
| attacks: 1,444 / 1,444 / 0 / 4 truncated / 0 no code | — | identical | yes |
| attacks cost / wall clock | $4.78 / 7 min | $4.78 / ended at 7.0 min | yes |
| matched: 611 / 611 / 0 / 0 truncated / 0 no code | — | identical | yes |
| matched tokens / cost | 0.40 M / 0.65 M, $1.82 | identical | yes |
| **matched wall clock** | **4 min** | **6.8 min** (log ends at `[6.8 min] ended`) | **no, see D1** |
| 11 attack replies with no ```` ```input ```` | 11 | `no trigger 11` | yes |
| 12 matched replies with no ```` ```input ```` | 12 | 12 | yes |
| Sonnet truncated 113 / 1,444 (7.8%) | 7.8% | 113/1444 = 7.82% | yes |
| Total $11.20 of $12 | 11.20 | 0.47 + 4.13 + 4.78 + 1.82 = 11.20 | yes |
| "honest predicted $4.10, actual $4.13" | — | actual $4.13 confirmed; the $4.10 **calibration** prediction is not in any committed log (the run log's own printed estimate was $2.86) | partial, see U1 |
| "$1.82 instead of $4.40" | $4.40 | not derivable; per-problem scaling of the actual gives $4.30 | partial, see U1 |

### 3.2 Verification and problem sets (§15.2)

| quantity | ledger | reproduced | match |
|---|---|---|---|
| honest passed | 1,051 / 1,444 = 0.7278 | 1,051 / 1,444 = 0.72784 | yes |
| matched passed | 562 / 611 = 0.9198 | 562 / 611 = 0.91980 | yes |
| attacks pass the tests | 689 / 1,444 = 0.4771 | 689 / 1,444 = 0.47715 | yes |
| attacks diverge on own trigger | 35 / 1,444 = 0.0242 | 35 / 1,444 = 0.02424 | yes |
| attacks USABLE | 35 / 1,444 = 0.0242 | 35; every diverging attack also passes (fires ⊆ passes) | yes |
| **honest failure reasons** | 286 + 57 + 26 + 9 + 7 + 3 + 2 + 1 + 1 = **392** | actual failures **393**; log also has `budget exceeded or died 1` | **no, see D2** |
| **611 = Haiku-honest passers ∩ Haiku-attack passers** | asserted | `hpass(1051) ∩ apass(689)` == `sg_haiku45_indep_passes.problem_ids`, exactly 611 | **yes** |
| 562 = 611 ∩ matched passers | 49 dropped | equal, 49 dropped | yes |
| "35 usable" is distinct problems or draws? | not stated | **distinct problems** — one draw per problem, 1,444 rows, 1,444 distinct ids, so 35 problems = 35 draws | see I3 |
| **firing share inside the 611 headline set** | not stated | **2 of 611 fire (0.33%); 99.67% inert** | see I3 |
| firing share inside Sonnet's 623 headline set | "97.5% never fire" | **14 of 623 fire (2.25%); 97.75% inert** | **no, see D5** |

### 3.3 §15.3 headline row — every cell matches

| quantity | ledger | `sg_haiku45_indep_passes.json` / `rho_joint_haiku45.json` | match |
|---|---|---|---|
| n / S / CI | 611 / 0.5340 / 0.5159–0.5531 | 611 / 0.5340326 / 0.5159072–0.5531225 | yes |
| fold sd / pairwise | 0.0115 / 0.5024 | 0.0115416 / 0.5024390 | yes |
| length-only / surface-7 | 0.4871 / 0.5203 | 0.4870840 / 0.5203056 | yes |
| B′ / CI | 0.8584 / 0.8397–0.8737 | 0.8583558 / 0.8396648–0.8736933 | yes |
| ρ / joint CI | 0.0950 / 0.0445–0.1500 | 0.0949688 / 0.0444910–0.1499543 | yes |
| P(≤0.33) / P(>0.72) / median / corr | 1.0000 / 0.0000 / 0.0959 / −0.080 | 1.0 / 0.0 / 0.0959476 / −0.0798976 | yes |
| band AUROC lines at B′ = 0.8584 | 0.6183 / 0.7580 | 0.6182574 / 0.7580162 | yes |
| per-carrier B′ → S | −0.3243 / −0.1267 / −0.2406 | −0.324323 / −0.126714 / −0.240579 | yes |
| verdict line | quoted verbatim | identical to `verdict` | yes |

### 3.4 §15.4 similarity strata — all 7 rows × 6 columns match

| stratum | ledger n / sim / S / CI / B′ / ρ | json | match |
|---|---|---|---|
| 0.00–0.60 | 150 / 0.451 / 0.5142 / 0.4695–0.5652 / 0.7884 / 0.049 | 150 / 0.4505546 / 0.5142222 / 0.4694667–0.5652456 / 0.7884444 / 0.0493066 | yes |
| 0.60–0.80 | 223 / 0.710 / 0.4737 / 0.4453–0.5060 / 0.8334 / −0.079 | 223 / 0.7095312 / 0.4736824 / 0.4453091–0.5059844 / 0.8333694 / −0.0789442 | yes |
| 0.80–0.95 | 161 / 0.875 / 0.5099 / 0.4813–0.5376 / 0.7951 / 0.034 | 161 / 0.8750187 / 0.5099157 / 0.4813047–0.5376153 / 0.7951079 / 0.0336004 | yes |
| 0.95–1.00 | 77 / 0.984 / 0.5054 / 0.4871–0.5316 / 0.8234 / 0.017 | 77 / 0.9844502 / 0.5053733 / 0.4870931–0.5316263 / 0.8233750 / 0.0166162 | yes |
| < 0.95 | 534 / 0.687 / 0.5319 / 0.5099–0.5536 / 0.8439 / 0.093 | 534 / 0.6866791 / 0.5318684 / 0.5099254–0.5536444 / 0.8438547 / 0.0926799 | yes |
| < 0.90 | 476 / 0.658 / 0.5251 / 0.5019–0.5458 / 0.8498 / 0.072 | 476 / 0.6579110 / 0.5250635 / 0.5019478–0.5458371 / 0.8497670 / 0.0716577 | yes |
| < 0.80 | 373 / 0.605 / 0.5266 / 0.4961–0.5558 / 0.8465 / 0.077 | 373 / 0.6053851 / 0.5266356 / 0.4960945–0.5558158 / 0.8464748 / 0.0768760 | yes |
| "S between 0.4737 and 0.5142, B′ between 0.7884 and 0.8334 in every stratum" | — | correct over the four strata | yes |

### 3.5 §15.4 / §15.6 pair similarity (task item 6) — all three reproduce

| quantity | ledger | source | match |
|---|---|---|---|
| Haiku pairs, mean | **0.724** | `sg_haiku45_indep_passes.pair_similarity.mean` = 0.7242051 | yes |
| Haiku pairs, median / >0.95 / <0.60 | 0.749 / 12.6% / 24.5% | 0.7486339 / 12.602% / 24.550% | yes |
| Sonnet pairs, mean | **0.659** | `sg_indep_first_passes.pair_similarity.mean` = 0.6590825 (n = 623) | yes |
| stored, same 611 problems | **0.623** | `sg_haiku45_indep_passes.pair_similarity.stored_same_problems.mean` = 0.6228772 | yes |

Note the three are on three different problem sets (611 Haiku / 623 Sonnet / 611 stored). The
comparison is fair for Haiku-vs-stored (same 611) and approximate for Haiku-vs-Sonnet.

### 3.6 §15.5 prompt-matched rows — all 4 rows × 9 columns match

| row | ledger | `gate_s_matched_haiku45.json` | match |
|---|---|---|---|
| control (611) | 0.5340 / 0.5159–0.5531 / 0.502 / 0.4871 / 0.5203 / 0.8584 / 0.095 (0.044–0.150) | identical to 7 dp | yes |
| (a) S_matched (562) | 0.5399 / 0.5197–0.5581 / 0.491 / 0.4930 / 0.5394 / 0.8540 / 0.113 (0.055–0.165) | 0.5399009 / 0.5196693–0.5580627 / 0.4911504 / 0.4930403 / 0.5393578 / 0.8540466 / 0.1126994 (0.0545811–0.1646918) | yes |
| S_original same problems (562) | 0.5317 / 0.5109–0.5528 / 0.507 / 0.4877 / 0.5186 / 0.8540 / 0.089 (0.031–0.150) | 0.5316644 / 0.5109304–0.5527824 / 0.5071745 / 0.4877025 / 0.5185763 / 0.8540466 / 0.0894356 (0.0307108–0.1500644) | yes |
| (b) prompt-only floor (562) | 0.4918 / 0.4724–0.5126 / 0.406 / 0.4953 / 0.5067 | 0.4917993 / 0.4723766–0.5126129 / 0.4057838 / 0.4952828 / 0.5067141 | yes |
| "moves S from 0.5317 to 0.5399 … a change of 0.0082" | 0.0082 | 0.5399009 − 0.5316644 = 0.008236 | yes |
| "stored length-only 0.6138 and surface-7 0.7609 on the same problems" | — | 0.6137983 / 0.7608843 | yes |

---

## 4. SPEND.md (task item 4)

Recomputed running total from the ACTUAL COST column **in file order**, starting from the stated
$101.60 opening balance:

```
101.60  opening
+0.47 = 102.07   +4.13 = 106.20   +4.78 = 110.98   +1.93 = 112.91   +0.29 = 113.20
+2.39 = 115.59   +0.36 = 115.95   +1.82 = 117.77   +0.28 = 118.05   +0.33 = 118.38
+0.31 = 118.69   +1.82 = 120.51   +4.48 = 124.99
```

| quantity | file | recomputed | match |
|---|---|---|---|
| every running-total cell | as printed | identical, row by row | yes |
| last row's running total | **124.99** | **124.99** | **yes** |
| sum of ACTUAL COST | "$23.39 new spend this session" | 23.39 | yes |
| Worker B total | $7.71 over eight batches | 7.71 (and 7.70 from the raw `cost_usd` fields) | yes |
| Worker C total | $11.20 of $12 (§15) | 0.47 + 4.13 + 4.78 + 1.82 = 11.20 | yes |
| Worker A total | $4.48 over one batch | 4.48 | yes |
| **footnote: "the immediately preceding row's own running-total cell (112.80)"** | 112.80 | the preceding row's cell reads **120.51**, and 112.80 appears nowhere in the file | **no, see D3** |

---

## 5. Discrepancies

**D1. §15.1, matched-honest batch wall clock: ledger 4 min, actual ~6.8 min.**
`genm_haiku45.log` polls `[0.0] … [6.0] in_progress` and `[6.8 min] ended`. Correct value: **7 min**
(the rounding the other two rows of that table use), or "6.8 min" if the table moves to one decimal.

**D2. §15.2, honest failure reasons omit one and do not sum.** The nine listed reasons sum to 392
against 393 actual failures (1,444 − 1,051). `tests_haiku45.log` carries a tenth line,
`budget exceeded or died 1`. Correct list: mismatch 286, timeout 57, SyntaxError 26, NameError 9,
RecursionError 7, IndentationError 3, IndexError 2, ValueError 1, UnboundLocalError 1,
**budget exceeded or died 1** — total 393.

**D3. `apps/SPEND.md`, Worker A footnote cites a running total that is not in the table.** It says
"the immediately preceding row's own running-total cell (112.80)"; the preceding row (Worker C's
matched-honest batch) reads **120.51**, and the file-order sum is internally consistent from the
opening balance to the last row with no exception. The sentence is stale — presumably written
before Worker C's row was inserted — and should be deleted or rewritten as "every running-total
cell in this file is the file-order sum".

**D4. §14.4, "the ratio … agrees to within 0.03 on the strict row".** 0.7492399 − 0.7170732 =
**0.0322**. Correct wording: "to within 0.04", or quote 0.032 directly.

**D5. "97.5% never fire" on the 623-problem headline set (§13.6, §14.7; inherited from §10).** The
firing count inside that exact problem set is **14 of 623 = 2.25%**, so the inert share is
**97.75%**. The 97.5% figure is §7.7's *pooled conditional* rate (167 / 6,570 = 2.5% over 11,565
draws), a different denominator, and §7.7 itself rules that the three inert shares "must never
share a sentence without their denominators". Correct value for the headline set: **97.8%**, or
state it as "14 of 623 fire".

That is **five** numerical discrepancies. Everything else in §13–§15 — every table cell, every
interval, every band-mass probability, every presence rate, every feature weight, every
similarity statistic and the whole of SPEND.md's arithmetic — reproduces.

### Rounding note (not counted as a discrepancy)

**R1.** §14.2 prints P(monitor > B′) = 0.888 for the Haiku headline row against a stored 0.8885.
Round-half-up gives 0.889. Harmless either way, but it is the only cell in the three sections where
the printed digit depends on the tie-break rule.

### Unverifiable from the committed artifacts

**U1.** §15.1's cost-estimation paragraph quotes three numbers with no committed source: the
recalibrated three-batch projection **$14.03**, the calibrated honest prediction **$4.10**, and
**$4.40** as the cost of a full-pool matched batch. The 24 × 3 calibration draw is booked in
SPEND.md at $0.47 but its log/output is not in `experiments/apps`, so none of the three can be
re-derived. The actuals beside them ($4.13, $1.82, $11.20 total) all check out. Either commit the
calibration log or mark those three as estimates in the prose.

---

## 6. ρ conventions (task item 3)

**The rule as actually implemented.** In §13, §15 and the "classifier ρ" column of §14.3, the ρ
**point** is `(S_fold_mean − 0.5)/(B′_fold_mean − 0.5)`, while the **joint 95% CI** beside it is
§12.2's bootstrap of the **pooled out-of-fold** ρ. Point and interval are therefore different
estimators in **every** ρ row of all three sections. §12.2 established and disclosed this; §13
repeats the disclosure for its two main rows only; §15 does not repeat it at all.

| section | rows | point | interval | pooled ρ printed? |
|---|---|---|---|---|
| §13.2 | 6 ρ rows | fold-mean | joint (pooled) + S-only beside it | yes, in prose: headline 0.390, strict 0.662 |
| §13.3 | 6 ρ rows | fold-mean | joint (pooled) only | **no** |
| §14.3 | 5 rows, classifier column | **both printed** for strict (0.921 / 0.861); headline 0.687 (fold-mean 0.6868, pooled 0.6867 — indistinguishable) | joint | yes |
| §15.3, §15.5 | 4 ρ rows | fold-mean | joint (pooled) | **no** (pooled: headline 0.0966, matched 0.1104, original 0.0894) |

**Rows where the mismatch is material** — point sits well above the joint interval's own median,
because at small n the fold-mean and pooled AUROCs diverge:

| row | ρ point (fold-mean) | joint interval | joint median (pooled) | gap |
|---|---:|---|---:|---:|
| §13.2 strict, §9 control | 0.921 | 0.662–1.089 | 0.867 | +0.055 |
| §13.2 strict, S_original (96) | 0.936 | 0.715–1.130 | 0.899 | +0.037 |
| §13.2 strict, S_matched (96) | 0.697 | 0.494–0.856 | 0.663 | +0.035 |
| §13.3 strict, S_matched [ID] | 0.642 | 0.437–0.771 | 0.597 | **+0.045** |
| §13.3 strict, S_matched [char_wb] | 0.687 | 0.486–0.840 | 0.653 | +0.034 |
| §13.3 strict, S_original [ID] | 0.689 | 0.502–0.856 | 0.675 | +0.014 |

No point falls outside its own interval, so nothing here is wrong — but a reader who takes
"0.642 (0.437–0.771)" as a point-and-interval of one quantity is reading two. **Recommendation:**
either print the pooled ρ beside every strict row as §14.3 does, or put one sentence at the head of
§13.3 and §15.3 saying the point is fold-mean and the interval is the pooled joint bootstrap.

**One sentence mixes the two conventions inside a single range.** §14.7: "on the strict pairs …
the classifier [keeps] 86–92%". The 86% is the pooled ρ (0.861) and the 92% is the fold-mean ρ
(0.921) — the same quantity computed two ways, presented as a spread. Quote one convention, or say
"0.86 pooled / 0.92 fold-mean".

---

## 7. Attack-class firing shares on the exact headline sets (task item 5)

| set | n | attacks that fire | share | inert share |
|---|---:|---:|---:|---:|
| Sonnet 5 headline (`sg_indep_first_passes`, `first`/passes) | 623 | **14** | 2.25% | **97.75%** |
| Sonnet 5 strict (`sg_indep_best_usable`, `best`/usable) | 99 | 99 | 100% | 0% (by construction) |
| **Haiku 4.5 headline** (`sg_haiku45_indep_passes`, `first`/passes) | **611** | **2** | **0.33%** | **99.67%** |
| Haiku 4.5, whole 1,444-problem pool | 1,444 | 35 | 2.42% | — |

**"35 usable" is distinct problems, not draws** — one draw per problem, 1,444 rows, 1,444 distinct
problem ids, and the 35 diverging attacks are a subset of the 689 that pass, so
distinct-problems = draws = 35. But **only 2 of those 35 lie inside the 611 the headline row is
fitted on**; the other 33 sit on problems where Haiku's *honest* program failed the tests and were
therefore dropped before Gate S. §15 never states this, and §15.7's "Haiku's 35 *firing* backdoors"
sentence reads as though the 35 were inside the compared row.

---

## 8. Interpretation, and statements that outrun their numbers (task item 7)

**I1. §13.6's bolded verdict "partial, content excluded" is a hair stronger than its interval.**
The joint 95% CI is 0.326–0.454; **0.326 < 0.33**, so the interval crosses the collapse line at its
lower end. §13.6's own next clause says so ("touches the collapse line … P(ρ ≤ 0.33) = 0.033"), and
the S-only interval (0.326–0.449) does the same. The band statement and the caveat should be one
sentence, not two: *"partial, content excluded (P = 0.000); the collapse line is touched at the
3.3% tail."* This matters because "partial, content excluded" is the sentence the paper will lift.

**I2. §13.3's ID-masked headline row is 40% collapse and §13 never says so.** `masked_ID.S_matched`
on the headline set has ρ = 0.342, joint CI 0.280–0.394, and **P(ρ ≤ 0.33) = 0.401**. Identifier
normalisation is, by §11's own finding, the *only* mask that moves S — so the row that matters most
for "is the residual structure or naming?" is, under prompt matching, band-ambiguous between
collapse and partial. §13.3's prose discusses only the AUROC drop (0.6423 → 0.6264) and §13.6 does
not mention the masked row at all. This is the largest omission I found in the three sections and
it should go into §13.6's reading.

**I3. §15 does not state the firing share of its own headline set.** §13.6 and §14.7 both label the
Sonnet headline row by its inert share; §15's headline row is 99.67% inert (2 of 611) against
Sonnet's 97.75% (14 of 623) — a nearly 7× lower firing rate on the very row the two models are
compared on. Since §15.7 already names "compared only on the `passes` eligibility" as the single
largest gap, the firing counts (2 vs 14) belong in that bullet: the two `passes` rows are not
equally inert either.

**I4. §14.7 over-attributes the residual to framing, against §13's own measurement.** §14.7: "the
0.75 the classifier still reads there is layout from the attack prompt's framing (§11)". §13,
written in the same window, measures that framing accounts for **44.7%** of the above-chance
signal, and that S_matched (0.6423) remains above the prompt-only floor (0.6006) with the intervals
overlapping. "is" should be "is largely", with §13's number attached. §13.6 itself uses the correct
hedge ("most of §11's residual is framing"), so the two sections currently disagree in strength.

**I5. §13 "partial" and §15 "collapse" do not contradict each other, but the comparable pair is not
the one a reader will take.** They are different generators, and both verdicts are correct against
the pre-registered bands (§13 headline ρ 0.394 in 0.33–0.72; §15 headline ρ 0.095 ≤ 0.33 with
P = 1.0000). The row directly comparable to §13's arm-3 result is **§15.5's** matched row
(ρ 0.113, 0.055–0.165), not §15.3's control — i.e. with the prompt matched on both models, Sonnet
keeps 0.394 and Haiku keeps 0.113. Wherever the paper puts §13 and §15 in one sentence it should
use 0.394 vs 0.113, not 0.394 vs 0.095.

**I6. §15's json carries the mechanism of its own collapse and §15 never reports it.**
`gate_s_matched_haiku45.json.presence`, verified directly against `gen_haiku45.jsonl`,
`bdind_haiku45.jsonl` and `genm_haiku45.jsonl` over the 562 problems:

| probe | Haiku matched honest | Haiku original honest | Haiku attack | Sonnet attack (§13.4) |
|---|---:|---:|---:|---:|
| `def main` | **0.000** | 0.000 | 0.000 | 0.662 |
| `data[` | **0.000** | 0.000 | 0.000 | 0.379 |
| `sys.stdin` | **0.000** | 0.000 | 0.000 | 0.614 |
| `input(` | **1.000** | 1.000 | 1.000 | 0.389 |
| any `def` | 0.480 | 0.464 | 0.445 | 0.865 |

The entire layout vocabulary §11 identified as the Sonnet residual — `def main`,
`data = sys.stdin.read()`, `solve()` — is **absent from Haiku's output in all three classes**, and
Haiku reads stdin with `input(` 100% of the time on both sides. That is a direct, mechanistic
account of why S collapses to 0.534 for Haiku while Sonnet holds 0.751, and it is stronger evidence
than §15.4's similarity strata (which only rule out the near-copy objection). It also sharpens
§15.7's "the models differ in capability, not only identity": Haiku does not adopt the attack
prompt's requested layout at all, so there is no framing signal left for the classifier to read —
which is exactly what §15.5's near-zero prompt-only floor (0.4918) independently says. **Recommend
adding this table to §15.6.**

**I7. Minor, §14.6.** Two of the six wrong-pair rows had degenerate bootstrap draws (Haiku stored
strict 34 of 2,000; Haiku same-gen strict 3). The rows are already marked "recorded, not read"; the
count belongs in that sentence.

---

## 9. Environment: a concurrent session is writing under the ledger's feet

Flagged because it affects anyone repeating this check, not because it changes a number:

- **A second session is running an API batch right now.** pid 3755046, started 19:15 local:
  `gen_backdoor_api.py --model claude-haiku-4-5 --independent --pool analysis --out bdind_haiku45_r2.jsonl --state-suffix r2 --spent 124.99`.
  Its log reports `already spent $124.99 / projected total $127.88 (ceiling $135)`, est. $2.89,
  **worst case $15.15**. At worst case this session's new spend reaches $38.54 against the **$33
  session cap** SPEND.md's own header states. The batch is not booked in SPEND.md yet.
- **The §13-strict / §14-strict input files were rewritten mid-check.**
  `bdind_sonnet5_best_nocrash.jsonl` and `bdindpass_sonnet5_best_nocrash.jsonl` changed mtime at
  19:15–19:17, i.e. after §13/§14 were written. I re-derived the strict set from the rewritten
  files: still exactly the same **99** problem ids, and `gate_s_matched.py --only strict` re-run
  against them reproduces `gate_s_matched_strict.json` with **zero** field differences. So the
  strict rows are safe — but the files are not pinned, and a later rerun may not be.
- **The ceiling in SPEND.md ($135, session cap $33, opening $101.60) is above the standing note**
  (real spend ≈ $99, ceiling raised to $110 with the owner's go). SPEND.md's arithmetic is correct
  and self-consistent; the *ceiling* is the thing to re-confirm with the owner before the in-flight
  batch and anything after it.

---

## 10. Consolidated macro block for `main.tex`

Ready to paste. One comment per macro giving protocol and n. Values taken from the json fields
named in the comment; **all of them reproduce** (§1–§3 above).

Precision note: §13's own suggested list mixed 3-dp points with 4-dp intervals
(`\matchedS` 0.642 beside `\matchedLo` 0.6179). AUROC macros below are uniformly **4 dp** and ρ
macros uniformly **3 dp**, so a point and its interval always agree in precision. If the prose
already quotes "0.642" and "0.601", either update the prose or drop a digit here — but do not leave
the mixture.

```latex
%% ---------------------------------------------------------------------------
%% RESULTS.md §13 — arm 3, prompt-matched honest class (Claude Sonnet 5)
%% All rows: comments stripped, problem-disjoint 5-fold, 2,000-draw bootstrap
%% over problems, seed 0; gate_s_eval.evaluate() unchanged.
%% Source: experiments/apps/gate_s_matched_headline.json, gate_s_matched_strict.json
%% ---------------------------------------------------------------------------
% S_matched: matched honest (PROMPT_INDEPENDENT_HONEST) vs the same attack draws,
% headline set, n = 586.  field: S_matched.S.auroc
\newcommand{\matchedS}{0.6423}
% n of the headline matched row: the 586 of §9's 623 where the matched program passes
\newcommand{\matchedN}{586}
% 95% bootstrap CI of \matchedS, n = 586.  field: S_matched.S.auroc_ci95_boot[0]
\newcommand{\matchedLo}{0.6179}
% field: S_matched.S.auroc_ci95_boot[1]
\newcommand{\matchedHi}{0.6621}
% rho = (S-0.5)/(B'-0.5), FOLD-MEAN point, headline n = 586.  field: S_matched.rho
% (pooled out-of-fold rho on the same row is 0.390: S_matched.joint.rho_point_pooled_oof)
\newcommand{\matchedRho}{0.394}
% JOINT 95% CI for rho (both AUROCs recomputed per resampled problem set, §12.2),
% n = 586.  field: S_matched.joint.rho_ci95_joint[0]
\newcommand{\matchedRhoLo}{0.326}
% field: S_matched.joint.rho_ci95_joint[1]
\newcommand{\matchedRhoHi}{0.454}
% B' refitted on the same 586 problems, inert-inclusive attack rule.
% field: S_matched.B_prime.auroc
\newcommand{\matchedBprime}{0.8613}
% prompt-only floor: original honest vs matched honest, both correct, one model,
% no attack anywhere; headline n = 586.  field: prompt_only.S.auroc
\newcommand{\promptOnly}{0.6006}
% field: prompt_only.S.auroc_ci95_boot[0]
\newcommand{\promptOnlyLo}{0.5768}
% field: prompt_only.S.auroc_ci95_boot[1]
\newcommand{\promptOnlyHi}{0.6243}
% strict set (attacks that pass AND fire), n = 96 of §9's 99.
% field: gate_s_matched_strict.json S_matched.S.auroc
\newcommand{\matchedStrictS}{0.7113}
\newcommand{\matchedStrictN}{96}
% strict rho, FOLD-MEAN point (pooled out-of-fold on this row is 0.662).
% field: gate_s_matched_strict.json S_matched.rho
\newcommand{\matchedStrictRho}{0.697}
% strict JOINT 95% CI, n = 96.  field: S_matched.joint.rho_ci95_joint
\newcommand{\matchedStrictRhoLo}{0.494}
\newcommand{\matchedStrictRhoHi}{0.856}
% difflib ratio, autojunk=False, matched honest vs attack, headline n = 586, mean.
% field: pair_similarity.matched_honest_vs_attack.mean
\newcommand{\matchedSim}{0.716}

%% ---------------------------------------------------------------------------
%% RESULTS.md §14 — monitor-rho; zero-shot monitor, one program per request,
%% comments stripped, prompt_sha256 14b320ea6a533dd4, shuffle seed 0,
%% bootstrap over problems 2,000 draws seed 0.
%% monitor-rho = (M_samegen - 0.5)/(M_stored - 0.5), one problem set resampled
%% per draw and both AUROCs recomputed on it.
%% Source: experiments/apps/monitor_rho.json  (rows[0] = headline, rows[1] = strict)
%% ---------------------------------------------------------------------------
% claude-sonnet-5 monitor (wrote both same-generator classes: self-evaluation),
% headline n = 623.  field: rows[0].monitors["claude-sonnet-5"].monitor_rho_point
\newcommand{\monRhoHead}{0.145}
% joint 95% CI.  field: rows[0].monitors["claude-sonnet-5"].joint.monitor_rho_ci95
\newcommand{\monRhoHeadLo}{0.111}
\newcommand{\monRhoHeadHi}{0.182}
% same monitor, strict n = 99.  field: rows[1].monitors["claude-sonnet-5"].monitor_rho_point
\newcommand{\monRhoStrict}{0.717}
% field: rows[1].monitors["claude-sonnet-5"].joint.monitor_rho_ci95
\newcommand{\monRhoStrictLo}{0.601}
\newcommand{\monRhoStrictHi}{0.832}
% Sonnet monitor AUROC on the STORED benchmark pairs over the same problems,
% headline n = 623, 6 of 1,246 replies missing.
% field: rows[0].monitors["claude-sonnet-5"].stored.auroc
\newcommand{\monStoredHead}{0.9579}
% ditto, strict n = 99, 1 of 198 missing.  field: rows[1].…stored.auroc
\newcommand{\monStoredStrict}{0.9437}
% claude-haiku-4-5 monitor (wrote NEITHER class) on the SAME-GENERATOR pairs.
% headline n = 623 BUT 628 of 1,246 replies lost to the 512-token ceiling
% (~50%); §14.5 rules this a bound, not a point — never quote it without that.
% field: rows[0].monitors["claude-haiku-4-5"].samegen.auroc
\newcommand{\monHaikuHead}{0.5577}
% ditto, strict n = 99, 84 of 198 missing.  field: rows[1].…samegen.auroc
\newcommand{\monHaikuStrict}{0.7871}
% Haiku monitor-rho, headline.  field: rows[0].monitors["claude-haiku-4-5"].monitor_rho_point
\newcommand{\monHaikuRhoHead}{0.151}
% Haiku monitor-rho, strict.  field: rows[1].monitors["claude-haiku-4-5"].monitor_rho_point
\newcommand{\monHaikuRhoStrict}{0.749}
% Haiku monitor on the STORED pairs, headline n = 623, 458 of 1,246 missing
% (differential by class: honest 50.1%, attack 23.4%).
% field: rows[0].monitors["claude-haiku-4-5"].stored.auroc
\newcommand{\monHaikuStoredHead}{0.8824}
% ditto, strict n = 99, 70 of 198 missing (honest 44.4%, attack 26.3%).
% field: rows[1].monitors["claude-haiku-4-5"].stored.auroc
\newcommand{\monHaikuStoredStrict}{0.8832}

%% ---------------------------------------------------------------------------
%% RESULTS.md §15 — second same-generator model, claude-haiku-4-5.
%% Outcome-blind single draw per problem, no retry pool, no selection rule;
%% eligibility `passes`, B' inert-inclusive on the same problems; comments
%% stripped, problem-disjoint 5-fold, 2,000-draw bootstrap seed 0.
%% Source: experiments/apps/sg_haiku45_indep_passes.json, rho_joint_haiku45.json,
%%         gate_s_matched_haiku45.json
%% ---------------------------------------------------------------------------
% S, Haiku honest vs Haiku attack, headline n = 611.  field: S.auroc
\newcommand{\haikuS}{0.5340}
% 95% bootstrap CI.  field: S.auroc_ci95_boot
\newcommand{\haikuSLo}{0.5159}
\newcommand{\haikuSHi}{0.5531}
% n = Haiku-honest passers (1,051) INTERSECT Haiku-attack test-passers (689)
\newcommand{\haikuN}{611}
% B' on the same 611 problems.  field: B_prime.auroc
\newcommand{\haikuBprime}{0.8584}
% rho, FOLD-MEAN point (pooled out-of-fold is 0.0966).
% field: sg_haiku45_indep_passes.json retained_vs_stored
\newcommand{\haikuRho}{0.095}
% JOINT 95% CI, n = 611.  field: rho_joint_haiku45.json joint.rho_ci95_joint
% P(rho <= 0.33) = 1.0000, P(rho > 0.72) = 0.0000 over 2,000 draws.
\newcommand{\haikuRhoLo}{0.044}
\newcommand{\haikuRhoHi}{0.150}
% Haiku honest harness pass rate, 1,051 / 1,444 over the whole analysis pool.
% source: tests_haiku45.log / pass_haiku45.jsonl
\newcommand{\haikuHonestPass}{0.7278}
% usable Haiku attacks (pass the public tests AND diverge on their own trigger),
% DISTINCT PROBLEMS over the 1,444-problem pool, one draw each. Below the 50-pair
% floor, so §15 has no strict row. NOTE: only 2 of these 35 lie inside \haikuN.
% source: verify_haiku45.log / bdpass_haiku45.jsonl
\newcommand{\haikuUsable}{35}
% S with the prompt matched on both sides (PROMPT_INDEPENDENT_HONEST vs the same
% attack draws), n = 562.  field: gate_s_matched_haiku45.json S_matched.S.auroc
% (rho on this row: 0.113, joint 0.055-0.165 — the row comparable with \matchedRho)
\newcommand{\haikuSMatched}{0.5399}
% prompt-only floor: original honest vs matched honest, n = 562; CI 0.4724-0.5126
% contains 0.5.  field: gate_s_matched_haiku45.json prompt_only.S.auroc
\newcommand{\haikuPromptFloor}{0.4918}
% difflib ratio, autojunk=False, Haiku honest vs Haiku attack, n = 611, mean.
% (Sonnet on its own 623: 0.659; stored on these same 611: 0.623.)
% field: sg_haiku45_indep_passes.json pair_similarity.mean
\newcommand{\haikuPairSim}{0.724}
```

### Is the block safe to paste?

**Yes, with two conditions.** Every value reproduces from the named json field, and no macro
carries a number touched by D1–D5. The two conditions:

1. **`\matchedRho`, `\matchedStrictRho`, `\haikuRho` are fold-mean points carried beside pooled
   joint intervals** (§6 above). The comments say so. If the paper quotes point and interval as one
   object, either switch the points to pooled (0.390 / 0.662 / 0.097) or keep a footnote.
2. **`\monHaikuHead` must never appear without §14.5's missingness caveat**, which the comment
   states: ~50% of its replies were lost to truncation, and on the stored side the loss is
   differential by class. §14.5 rules it a bound, not a point.

Two macros the workers proposed are **not** in the requested list and are still used in §13's
prose: `\matchedSorig` 0.7572 (`S_original_same_problems.S.auroc`) and `\matchedRhoOrig` 0.712
(`S_original_same_problems.rho`). Both reproduce; add them if the prose keeps that comparison.
