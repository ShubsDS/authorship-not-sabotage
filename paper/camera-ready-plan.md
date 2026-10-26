# Camera-ready plan (EvoRobust @ NeurIPS 2026)

Deadline: October 29, 2026, 11:59 PM AoE, uploaded on the OpenReview submission page.
Requirements: NeurIPS 2026 style with the `final` option, author names and affiliations, at most
5 content pages (submission limit was 4; the current body is about 4 pages plus 2 lines, so about
0.9 page is free), and responses to the reviews.

Five subagents assessed the six weaknesses raised by reviewer 3sdp against the paper and the
committed JSONs (October 13, 2026). Line numbers refer to `paper/main.tex` at commit 1e05846.

## Verdicts

| # | Criticism (summary) | Verdict | What the subagents found |
|---|---|---|---|
| 1 | Abstract does not state problem, method, why, insight | Valid | It never says why the method works, and it calls the no-code floor an authorship difference when it reads only problem metadata. "Removes most of the rest" is not supported: prompt matching takes Sonnet's rho from 0.69 to 0.39, and Haiku's not at all. |
| 2 | Headline sets are mostly failed attacks | Valid, and worse than stated | 14 of 623 and 2 of 611 attacks fire. Every stored attack on those problems fires, so l.453 "B' includes inert attacks" is false. The headline compares working stored backdoors against mostly-inert attempts. |
| 3 | Authorship is not isolated | Valid | The attacking model alone moves B from 0.75 to 0.94 against the same human code, so "rho bounds the content share" (l.538) does not hold. l.396 and l.535 are factually wrong. |
| 4 | Verified attacks qualify the result | Valid for the monitor, partly for the classifier | Classifier: on the 64 problems in both sets, rho is the same for headline and working attacks (0.82 vs 0.75, paired CI -0.24 to +0.13); the higher strict rho comes from which problems yield working attacks. Monitor: see below. |
| 5 | Statistical inconsistencies | Valid | Each point is the average over folds while its interval is built from the pooled out-of-fold scores, and l.701 wrongly calls these "the same quantity". The null procedures differ, and the F2 "nulls" are each an average of 3 permutations of a different statistic. One convention changes no conclusion; strict rho becomes 0.861 instead of 0.921. |
| 6 | Repetition; no fixed audit budget | Valid | 0.806 appears 4 times in the body and "a third to nine-tenths" 3 times. No result is reported at a fixed false-positive rate (now computed, below). |

## The monitor result is wrong as written

The paper says the monitor "moves the same way" as the classifier. Swapping one class at a time
(committed per-program scores, Sonnet 5 monitor, 617 headline problems):

| | Stored attack | Our attack |
|---|---|---|
| Human honest | 0.958 | 0.446 |
| Our honest | 0.974 | 0.564 |

Replacing the human honest code with ours does not lower the monitor's score. Its whole drop comes
from our attacks being far less suspicious (mean suspicion 6.6 against 78.8 for stored attacks).
That holds on working attacks too: on the strict set, human honest against our attacks scores
0.755. The monitor's fall measures attack conspicuousness, not authorship. The cells mix batches
run on different days; the paper should say so.

## New results from committed data

- **Audit budget** (2% false-positive rate, threshold set on each set's own honest programs). On
  the 99 strict problems the monitor catches 78% of stored attacks and 48% of same-generator ones;
  paired difference 0.29 (0.16-0.43). On headline pairs: 85% vs 6%.
- **Stored attackers restricted to Claude models** give rho = 0.715, about the same as the full
  mix, so rho does not depend on which stored model attacked.
- **Consistent statistics** (pooled out-of-fold, joint bootstrap; no conclusion changes):

  | Row | Old (fold mean) S / B' / rho | New (pooled) S / B' / rho | rho CI |
  |---|---|---|---|
  | Sonnet headline | 0.7512 / 0.8658 / 0.687 | 0.7504 / 0.8646 / 0.687 | 0.625-0.755 |
  | Haiku | 0.5340 / 0.8584 / 0.095 | 0.5344 / 0.8564 / 0.097 | 0.044-0.150 |
  | Prompt-matched | 0.6423 / 0.8613 / 0.394 | 0.6411 / 0.8614 / 0.390 | 0.326-0.454 |
  | Strict | 0.7652 / 0.7877 / 0.921 | 0.7488 / 0.7889 / 0.861 | 0.662-1.089 |
  | Strict prompt-matched | 0.7113 / 0.8030 / 0.697 | 0.6926 / 0.7910 / 0.662 | 0.494-0.856 |
  | No-code floor (CV) | 0.772 | 0.766 | 0.732-0.801 (AUROC) |

## Plan

### A. Text and figures (no new data)

1. New abstract: problem, method, why, insight, qualification. Report headline and strict rows
   side by side and say what rho is not.
2. New contribution statement, listing the two classifier floors as contribution (i).
3. Table 1: add a "fires" column; group rows into "attempts" and "working sabotage"; use the pooled
   values; replace band labels with P(rho > 0.72).
4. Rewrite the monitor paragraph around the swap table (small table in the body) plus the 2%
   audit-budget sentence.
5. Required text fixes:
   - l.380: "ten named models" -> "nine named models or an unattributed source";
   - l.396: "the writer changes and nothing else" is false;
   - l.453: the stored attacks all fire, so B' does not include inert attacks;
   - l.535-541: drop "claude-3-7-sonnet-thinking" as the stored attacker, and drop "bound";
   - l.437: the no-code floor was not trained on the train split;
   - l.463: the strict and headline rows do not "agree" for the monitor;
   - l.701: point and interval are not "the same quantity computed two ways";
   - the held-out no-code count is 17, not 18, on identical items.
6. Cut repeated numbers and verdict words (saves about 10 lines). Footnote the strict-monitor file
   mismatch (it moves 0.818 by about 0.01).
7. Appendix: attacking-model mix with B per attacker; full audit-budget table; shared-problem
   decomposition; one stated statistics convention.
8. `figures.py`: F3 line and legend, F4 ladder values, F2 null.
9. Mechanics: `final` option, author names, release link, `experiments/README.md` scikit-learn
   version (B = 0.8714 reproduces under 1.9.0, as `gate_s_baseline.json` records, not 1.7.1).

### B. CPU reruns on public data (free, under 2 hours)

- Nulls with 1,000 permutations under one procedure (TF-IDF 30-60 min; others minutes).
- A no-code floor trained on problems outside the test split and scored once, matching the 0.806
  protocol. Lead with its value whatever it is.
- A proper within-task permutation null for F2.

### C. On the cluster

- **Classifier swap table** ($0, CPU minutes). The one experiment that answers criticism 3: add
  the missing cell, human honest against our attacks (`bdind_sonnet5_first.jsonl`,
  `gen_sonnet5.jsonl`; same for Haiku). Reading rule, fixed in advance:
  - near B' (~0.87): the classifier's drop is on the honest side; the authorship reading holds for
    the classifier;
  - near S (~0.75): the classifier behaves like the monitor; say the corpus effect is mostly the
    attack distribution.
- Optional: re-run the strict monitor with the matching attack file (about $1).

### D. Optional API experiments (recommendation: skip)

- About 150 verified Sonnet pairs: about $51, 2-3 days.
- About 300 pairs with a revised attack prompt: about $150 plus a pilot.
- A Haiku strict row of about 50 pairs: about $45.

The strict result is limited by which problems yield working attacks, not by sample size alone, so
more pairs would narrow intervals without changing what the paper can claim.

### Page budget

Cuts save about 10 lines; additions cost about 20-25 lines. That uses about half of the free 0.9
page; nothing needs to move to the appendix. If space remains, move F3 into the body.

## Costs

- Analysis: five subagents, 873k tokens in total, about 20 minutes in parallel. No API spend.
- Plan: A and B $0; C $0 (plus about $1 for the optional monitor re-run); D $45-150 per option.

## Open decisions

1. Can the classifier swap table (C) be run on the cluster before October 29?
2. Skip the API experiments (D)?

## Implementation status (October 13, 2026)

Work ran on six branches, each merged into `main` with `--no-ff`, so `git log --first-parent`
lists one merge per branch and `git log <merge>^2` lists that branch's commits. Branch base
commits: front matter, Results, analysis and reruns started at 1e05846; appendix and docs at
c076624.

| Item | Status | Where |
|---|---|---|
| A1 abstract | Done | merge 74e84dd (168fef8); no-code lead 5f02f3d |
| A2 contribution statement | Done | 74e84dd (bb96a78) |
| A3 Table 1 (renders as Table 2): fires, groups, pooled values, P(rho > 0.72) | Done | 9abc7e4 (pooled macros), d976def (7346028), 6448e5f (`\matchedFire`) |
| A4 monitor paragraph, swap table, 2% audit budget | Done | d976def (cbac8ac, af5630e, 73e9270), 5d35e73, c1f53f1, edab7b4 |
| A5 text fixes (l.380, 396, 453, 535-541, 437, 463, 701; held-out count 17) | Done | 74e84dd, d976def, bd97b4b (62697b2), 8e70ee3 |
| A6 cuts of repeated numbers and verdict words; strict-file footnote | Done | 74e84dd, d976def, 96f4595, edab7b4 |
| A7 appendix: attacker mix, audit table, shared problems, statistics convention | Done | bd97b4b (62697b2, cdad892, 958123f, c2e679f, 854c818) |
| A8 `figures.py`: F2 null, F3 line and legend, F4 ladder | Done | ca1c089 (1491c63, 56bcedd, 6904908, 4cb1925) |
| A9 mechanics: `final`, authors, affiliations, emails, release link, scikit-learn version | Done | 74e84dd (3d5c4d9, bc560fe), c062a02, a006cf3, b6c0253, e2c16ca, c047790 (d725ec5) |
| B 1,000-permutation nulls under one procedure | Done | ca1c089 (0f9f6bd, ec03411) |
| B no-code floor trained outside the test split | Done: 0.298, and the paper leads with it | ca1c089 (2670852, 9307198), 5f02f3d, 7fa7ec8, 96f4595 |
| B within-task null for F2 | Done | ca1c089 (a4e19cf) |
| C classifier swap table | Done: human honest vs our attacks 0.981 (Haiku 0.973), above B'; the classifier's drop is authorship | 49c6307, 1a9dc8b, 5cec86c, 8e3a590, b83e613, 233c7cc |
| C strict monitor re-run with the matching attack file | Not done: needs ANTHROPIC_API_KEY (about $0.37); the three differing attacks are named and the AUROC without them (0.821) is reported | 7da3457, 20df1fa |
| D API experiments | Skipped (cost) | — |
| Responses to the reviews | Drafted in `response-to-reviews.md` | 809ccb4, f5809b6 |
| READMEs | Updated to the revised claims | 666b040 |

Each new number has a script and committed output (`experiments/README.md`, "Where each result
comes from"): `pooled_stats.py`, `fire_counts.py`, `monitor_swap.py`, `audit_budget.py`,
`shared_problems.py`, `attacker_mix.py`, `nocode_outside.py`, `headline_ci.py --perms`,
`agentic/floors2.py`.

### Where the implementation departs from the numbers above

- Audit budget, strict: 77% vs 48%, difference 0.28 (0.15-0.42). Ties at the threshold are
  broken at random, so the honest false-positive rate is exactly 2%. The 78% / 0.29 above came
  from an interpolated quantile whose false-positive rate was 2/99.
- B per stored attacker: 0.75-0.93 from a refit over the 1,444-problem pool against the same
  human programs (0.94 did not reproduce). The unattributed source reaches 0.96.
- The monitor's swap cells were not run on different days. They are separate batches about six
  hours apart on 2026-09-11. Rescoring the same program gives the same score 41-72% of the time.
- Strict file mismatch: 3 of 99 attacks differ; dropping any three moves 0.818 to 0.812-0.839.
- Prompt-matched fires: 11-13 of 586. The exact count needs `bdindpass_sonnet5_first.jsonl`.
- Shared problems: on the 64 shared problems, the attacks working do not raise rho. That the
  strict row's higher rho comes from problem selection holds by point estimate only: strict-only
  minus shared is +0.34, CI -0.13 to +0.93. The paper says so.
- Held-out no-code null: 0.558 (p = 0.001) under the one procedure, so that row is no longer
  "barely above its null".
- No-code floor trained outside the split: 0.298, below chance (0.629 on problems with at least
  four tests). Outside the split every problem that passes the filter has a working backdoor,
  so the relation between test count and label reverses.
- Values that stay fold means, because their inputs are only on the cluster: `\sameGenLen`,
  the Haiku similarity strata, the one-sided arm, and `\baselineBownflag`.

### Second round (October 13-14, 2026)

- Generated files copied from the CS portal checkout (`/u/fvc9ch/ai-safety/authorship-not-sabotage`,
  checksums verified) to run what needed them; none is committed.
- Classifier class swap run (above). Exact fire counts: 13/586 and 2/562 (fire_counts.py). The
  three differing strict attacks are 1701, 1972, 4434 (monitor_swap.py). The four fold-mean
  holdouts are pooled (merge of camera-ready-cluster). shared_problems.py now reads the
  classifier's files: 53 / 11 split, not 52 / 12 (bf2de2a).
- Bibliography cleaned and checked against arXiv (merge of camera-ready-bib).

### Figures (October 13, 2026)

The figure designs of the archived branch (tag `archive/camera-ready-valmi`) were compared with
main's and the better ones adopted, redrawn from current numbers in `figures.py`, which checks
each value against the macros (b4cd91e, 35c2a84, 84724da, 7ac4639, 3718032, 1ca7b78):

- Figure 1 is now three stored pairs in code (f5-stored-pairs.pdf), checked against the public
  dataset; the construction schematic is removed.
- Figure 2 ranks the two floors among the 24 monitors (f6-floors-ranked.pdf), in the Results.
- Appendix: the audit-budget curve (f7, from a new curve in `audit_budget.json`) and the
  monitor's score histograms (f8). The curve stays in the appendix because the body is at five
  pages.
- F2 and F3 keep their content and move to the same visual system (Arial, greys, gold).
- Not adopted yet: the archived branch's top-feature figure. Its stored-pair tokens (`and`, `==`,
  `if`) are the special-case conditions backdoors are built from, which the Results sentence
  "What it reads is stylistic" does not account for.

### Review of Valmi's rewrite (October 21, 2026)

Valmi's 18 commits (new title, abstract, structure and LaTeX-native figures) were reviewed against
the data and kept. Corrections on top (7544a93 to e42a1ab):

- The baselines "never run the code" instead of "cannot recognise/see a backdoor"; Section 3 says
  the classifier's top tokens (`and`, `==`, `if`) partly key on the inserted code.
- The abstract again reports the working-backdoor row (keeps 0.861) beside the all-attempts rows.
- Section 3.1's out-of-split explanation and Setup's "as the benchmark does" corrected.
- The body still ends on page 5 (Recommendations folded into one sentence); the acknowledgments
  start page 6, as in Valmi's version.
- README lists the LaTeX packages a basic TeX install lacks; `release_split.py --refresh`
  rewrites the bundle's card, licence and scripts without the generated files. The zip was
  refreshed for the new title (SHA-256 3aba6bcc...).

### Overview figure (October 23, 2026)

Figure 1 is now a three-panel overview (`fig11_overview` in `figures.py`, f11-overview.pdf):
(a) the 24 monitors ranked with bag-of-words and the no-code classifier; (b) the class swap for
bag-of-words and the Sonnet 5 monitor, one row per kind of pair, named by who wrote each side
(person / weaker models, Sonnet 5 / weaker models, person / Sonnet 5, Sonnet 5 / Sonnet 5);
(c) the share of the 99 working backdoors caught at 2% FPR. Gold marks bars below the original
pairs. The caption lists the weaker models and their share of the pairs (macros checked by
`check()` against Table A2's counts). The code pairs become Figure 2.

- The old Figure 2 (floors) and Figure 3 (swap, audit) leave the body. The no-code and
  test-count panels and the audit curve move to the appendix (Figures A1, A5); the ranked bars
  (f6a) and grouped swap bars (f9a) are deleted, since Figure 1 and Figure A2 cover them.
- Appendix figures and tables use the same names (Figures A3, A4; Tables A8, A10, A11).
- Body text: "weaker models" defined in Setup (by release date, not measured skill); "a newer
  model" / "earlier models" replaced; citable lead sentences in Sections 3, 4, 4.1 and 6.
- Body still ends on page 5.

### Cold-read fixes (October 25, 2026)

A fresh reader (abstract, then figures, then conclusions, then the body) found where the paper
misleads a first-time reader. Changes:

- New runs, CPU only: the classifier class swap on the 99 working-backdoor pairs
  (`classifier_swap.py --release`, from the release bundle; diagonal cells reproduce Table 1
  exactly), and the Sonnet 5 monitor's catch rate for all four pairings (`audit_budget.py`,
  `swap`; existing numbers unchanged). With the human solutions' threshold: 77% of the weaker
  models' working backdoors against 37% of Sonnet 5's (difference 0.40, 0.28-0.52).
- Figure 1 has four panels; (b)-(d) are on the working-backdoor problems, one row per kind of
  pair, so the monitor panel no longer rests on backdoors that mostly fail. Gold means Sonnet 5's
  backdoors only. (a) says open-weight monitors; the caption says what each classifier reads.
- Body: the abstract matches Limitations and states that on working backdoors most of the
  classifier's advantage survives one author; why the attempts fail and the 0.62 check; the
  swap's reading rule; the Haiku 4.5 monitor as a check on self-recognition; "current models"
  instead of "stronger models"; pairwise accuracy defined; per-model range and agentic finding in
  Limitations. Body still five pages.
- Appendix Table A8 gains the working-backdoor rows; D.3 gives the crossed catch rates.

### Second cold read: clarity (October 26, 2026)

A second fresh reader, reading for clarity, found three errors from the previous round and
several unclear passages. Changes:

- Errors fixed: the abstract no longer says the classifier reads "the inserted code" on
  one-author pairs (masking operators moves it by at most 0.002; what survives is the prompt's
  layout); the working-backdoor rho is higher because of which problems those are, not because
  the backdoors work (appendix C.3); the swap's reading rule is tied to the all-attempts run it
  was fixed for; Figure 1's caption says "when Sonnet 5's code is paired with another author's";
  Figure A5 cites Figure 1d; eight models, not nine.
- "Weaker models" is now "older models" everywhere (paper, figures, README, card, LessWrong
  draft). Figure 1's caption names the models without shares; the shares are now Table A2's
  working-backdoor column, checked by figures.py.
- New output: the catch-rate curve for person / Sonnet 5 (`audit_budget.json`, `curve_swap`),
  drawn as Figure A5's third line so the appendix shows the same comparison as Figure 1d.
- Clarity: what the test split keeps per problem (720 of 892 problems with a backdoor have one
  that fails); trained classifier against prompted monitors from prior work; the Haiku 4.5
  check in the abstract and caption; Table 1's intended reading; Section 3.1 in steps; 0.298 as
  a reversed relation; the 24 scores as reused; the agentic settings as ControlArena
  repackagings; length added to the recommended floors.
- Docs: README summary rewritten to match the paper; experiments/README glossary adds the new
  terms; response draft brought up to date; the dataset card uses the paper's terms (no
  "stored", "arm", "fires"), and the bundle was refreshed and re-zipped
  (same-generator-apps-split.zip, SHA-256 d91ce881...).
- The LessWrong draft (claude.ai artifact RVqXhxzugSaQdbw4o1sMt2) now reports 77% against 37%
  with the honest code fixed, the Haiku check, older models and the label-leak counts.

### Still open

1. The strict monitor re-run (needs an API key; command in `experiments/README.md`, "Pending").
2. Whether to add the camera-ready scripts to the release bundle (`release_split.py` lists 24
   scripts and none of the new ones), and hosting the corpus itself (the abstract's footnote
   promises "Code and corpus").
3. Whether the release URL (github.com/ShubsDS/authorship-not-sabotage) is public by the deadline.
4. The title.
