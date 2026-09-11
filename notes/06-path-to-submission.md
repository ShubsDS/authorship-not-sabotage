# Path to submission: what is done, what is publishable, what must still happen

Written 2026-09-11, roughly 36 hours before the EvoRobust wall (Sep 12 AoE = Sep 13 11:59 UTC).
Assembled from a read of every file in this repo plus four independent audits run today: the
experiment scripts, the paper draft, the literature and venue, and the Gate S statistics. Every
claim about the code was checked against the file named. Every claim about the literature is
marked with how far it was verified (arXiv, OpenReview and HuggingFace were unreachable from the
sandbox that wrote this; GitHub and web search were not).

Companion changes made today, all on branch `claude/vigilant-maxwell-p05yuk`, none yet run on
real data because the shards could not be fetched from the sandbox:

- `experiments/apps/strip_recheck.py` (new): the matched-protocol and transfer numbers, stripped
  and unstripped, side by side. Exercised on a synthetic shard with the real schema.
- `experiments/apps/gate_s_samegen.py`: `--eligibility {usable,passes,all}`, `--min-pairs`,
  `autojunk=False`, the stored benchmark's similarity measured on the same problems, and the
  verdict routed on the pre-registered ρ bands against B′.
- `experiments/apps/gate_s_eval.py`: `evaluate()` additionally returns a pooled out-of-fold AUROC
  with a bootstrap-over-problems 95% CI. Existing fields are unchanged; B still reproduces.

---

## 0. The bottom line

1. **The diagnostic half of the paper is publishable at a NeurIPS workshop now.** The
   stored-benchmark results (0.806 above 20 of 24; 0.772 no-code above 20; 0.4726 length at chance;
   the five same-generator agentic settings as the built-in negative control; the schema table)
   are reproduced on two machines, bit-match three numbers Jha published independently, and sit
   beside a negative result (the AICD token test) reported as such. Today's scoop check found no
   prior work reporting a trivial baseline on any AI-control corpus, and none naming the
   human-vs-LLM authorship confound. K2 holds at the level a search engine can test it.

2. **"Authorship, Not Sabotage" is not supported by what has landed, and should not be the title.**
   Gate S has no S: the same-generator attack arms yielded 40 (edit) and 10 (independent) usable
   pairs against a 50-pair floor. The route-agnostic title already in `main.tex` is true under every
   outcome. State the authorship reading as inference, in Limitations, in those words (PLAN.md §3
   route 4). If the retry batch lands and the corrected reading in §4 comes back as collapse, the
   stronger title can go on at camera-ready, which allows five pages.

3. **Two of the three legs the authorship reading stands on were measured on unstripped code.**
   `matched.py`, `exact.py` and `transfer.py` never call `strip_comments` (verified: zero
   occurrences in each). So the working-vs-inert contrast (0.979 vs 0.955), the cross-generator
   transfer (0.9935) and the third leg, which is literally comment presence (`#` in 0.685 vs
   0.176), all include the one channel the field already patched, and the paper introduces them
   directly after "on that same filtered, comment-stripped split" without saying so. This is the
   paper's own thesis turned against it. **Run `strip_recheck.py` before anything else.**

4. **The document is about two pages over, not 1.5, and the abstract promises an S that does not
   exist.** §1 is unwritten; five citation keys live only inside `\TODO{}` blocks, so the documented
   pre-submission step of switching `\TODO` to its no-op form silently deletes four of the six
   never-cut first-paragraph citations, including the invited speaker's paper. A cut plan that
   lands at 4.0 pages and a paste-ready §1 are in §5.

5. **The Gate S decision rule as coded would have mis-read a real collapse.** The ±2 fold-sd
   interval is about 1.9× a true 95% CI; at n = 125 it declares a genuine collapse 27% of the time
   and "inconclusive" otherwise. A bootstrap over problems (now in `evaluate()`) lifts that to 78%
   at the same n, which is worth more than any top-up batch. And the eligibility rule was stricter
   than the benchmark's own: 80.7% of the benchmark's labelled backdoors do not fire, and the
   classifier scores 0.955 on them, so a test-passing attack class (335 independent pairs, on disk
   today) is the same-generator analogue of the published protocol, not a shortcut.

6. **P(accept | submit) is roughly 0.45 to 0.55 if items 3 and 4 are done, and materially lower if
   either is skipped.** The science is not the risk. The risk is a reviewer with a four-day window
   finding the abstract's control missing, or the transfer number resting on comments.

---

## 1. What exists, and how solid each piece is

### 1.1 Stored-benchmark results (the paper's weight)

| Result | Protocol | Reproduced | Note |
|---|---|---|---|
| TF-IDF 0.8063, above 20 of 24 monitors | Koran's exact split; train on 2,418 paired, score 1,375; stripped | two machines, exact | single fit; **no variance estimate anywhere in the repo** |
| TF-IDF 0.8914, above 22 | same, comments kept | exact | |
| No-code 0.7715 ± 0.0389, above 20 | 5×5 CV within the test split | exact | caveat correctly in the F3 caption |
| No-code 0.7163, above 18 | single 413-item held-out slice | exact | never pair 0.772 with 18; `main.tex` obeys this everywhere |
| Length 0.4726; `#`-count 0.6957 → 0.4983 | Koran's split | **bit-match Jha's published values** | the strongest external check in the repo |
| Schema: `backdoors` carries `model`, `source`; `solutions` neither | none needed | verified from the dataset info endpoint | the thesis in one table |
| Five agentic settings, within task, 0.504 (bash) to 0.802 (agentdojo) | chars only, permutation null | exact | see §3.4 on the null |
| 80.7% of Koran's test-split backdoors inert; 20.95 vs 38.85 tests | Koran's split | exact | |

### 1.2 The authorship legs (what carries the reading when S is absent)

| Result | Protocol | Stripped? | Status |
|---|---|---|---|
| Transfer 0.9935 (Control Tax → 2023 GPT-4 set) and three cross-model rows | pairwise, problem-disjoint | **No** | rerun with `strip_recheck.py` |
| Working 0.979 vs inert 0.955 pairwise | matched pairs, 30% problem-disjoint test | **No** | rerun with `strip_recheck.py` |
| Style markers: `#` present 0.685 vs 0.176; `__main__` 0.116 vs 0.000 | control_tax pairs | first marker **is** the comment channel | keep `__main__` (replicated 152 vs 1 on Koran's stripped train split); drop `#` |
| Bylines surviving the stripper 23 vs 2; triple-quoted 43 vs 9 | Koran's stripped train split | yes | **no producer script exists**; write one or drop |
| AICD token test: −0.013, p = 0.956 | Koran's stripped train split | yes | negative, reported honestly |

Also unrecorded: `gate_s_samegen.py:70-72` notes that Sonnet 5 honest against the **stored**
Claude 3.7 backdoors scores about 0.92. That is a second one-sided regeneration, same vendor this
time, and it also made separation worse. It belongs in the ledger and in the arm-1 paragraph as
one sentence: the confound swap is not a Qwen-specific effect.

### 1.3 Gate S

| Piece | Value | Status |
|---|---|---|
| B | 0.8714 ± 0.0085 (n 1,444); 0.8729 under our own flag (n 1,406) | done; bit-identical across two library environments |
| Arm 1: Qwen3-Coder-30B honest vs stored backdoors | G = 0.9616, ρ = 1.234 | confounded, and a real method result. **But** `gate_s_eval.py:116` gates the human side on the shipped flag and the LLM side on our harness, contrary to the runbook and to `main.tex:367` |
| Same-generator honest class | 1,444 generated, 1,112 pass | done, $8.62 |
| Edit arm | 1,112 generated; 427 pass tests; **40 usable** | near-copies (similarity 0.924); a bound at best |
| Independent arm | 600 generated; 335 pass tests; **10 usable** | the arm the title would route on |
| Retry batch | 6,672 requests in flight; ~125 usable projected | see §4 for what to do with it |

---

## 2. Is it publishable? Component by component

**Yes for the diagnostic paper, under the route-agnostic title, with the authorship reading stated
as inference.** The exemplars a robustness reviewer will have in mind (Niven & Kao, ACL 2019;
Ferrari Dacrema et al., RecSys 2019; Safetywashing, NeurIPS 2024; Rethinking CyberSecEval, 2024;
Bean et al., NeurIPS 2025) share one shape: a claim about a corpus under a named protocol, a
control where the shortcut fails, and a released artifact. This repo has the first two in hand.
The third is promised at `main.tex:589` ("Ours accompany this paper") and is not yet backed: the
repo has no `LICENSE`, and nothing is attached to the submission.

**Not yet for "Authorship, Not Sabotage" as a demonstrated claim.** What the evidence supports
today: the label is recoverable without reading a backdoor; the signal is not sabotage-specific
(inert ≈ working, transfers across attackers, pending the stripped rerun); the two classes were
produced by different processes (schema); regenerating one side swaps the gap rather than removing
it (arm 1, plus the unrecorded Sonnet-5-vs-stored observation). That is a strong inference. It is
not Niven & Kao's adversarial set. The same-generator S is the only thing that would make it one.

**What makes this stronger than the typical four-page critique, and should be said plainly:** the
field's own split and its 24 published monitors; three of Jha's numbers bit-matched by an
independent reconstruction; the negative control built in; a negative result reported; a
self-inflicted cross-protocol error caught and documented. That is the credibility budget.

---

## 3. Defects to fix before submission

Ordered by how badly a reviewer would react to finding each one.

### 3.1 Comment stripping on the authorship legs (about one hour, CPU)

Run on a machine with the shards:

```
cd experiments/apps && python strip_recheck.py --seeds 5
```

It reproduces `matched.py` and `transfer.py` line for line, stripped and unstripped, with a spread
over five problem-disjoint splits. Three outcomes, all of them a paper:

- Contrast and transfer survive stripping (the likely case, given that TF-IDF on the stripped
  Koran split still reaches 0.806): the paper gains a sentence and F1 gains a preprocessing column.
- They weaken but hold: report the stripped values; say the unstripped ones were inflated.
- They collapse: the authorship reading loses two legs and leans on the schema, `__main__`, arm 1
  and the agentic settings. The abstract sentence "transfers almost unchanged across backdoor
  generators" comes out.

Whatever comes back, the paper reports the stripped values. Under R18 there is no third option.

### 3.2 The abstract and §3 must tell the truth about Gate S (30 minutes)

- `main.tex:229-231`: "We therefore hold authorship constant by construction ... and report what a
  bag-of-words classifier can still separate." No such number exists. Rewrite as a design and a
  yield until one does.
- `main.tex:488-490`: "We therefore route on the independent arm (n = 600 requested)". Usable is
  10. Report both or neither.
- `main.tex:492-499`: the TODO's own delete-instruction leaves §3 ending on "we route on the
  independent arm" with nothing routed. Replace with the paragraph in §5.3.
- The 2% single-shot yield against the benchmark's stored 46% is a finding: the stored attack class
  is the survivor set of an unreported number of retries. Two sentences turn the gap into a number.

### 3.3 The `\TODO` citation bomb and §1 (60 minutes, one job)

`terekhov2025controltax`, `sreevatsa2026legibility`, `gewang2026attackselection`,
`terekhov2026adaptive` and `pinto2026calibration` are cited only inside `\TODO{}` blocks.
Uncommenting `\renewcommand{\TODO}[1]{}` deletes them without an error. Writing §1 fixes it.
A paste-ready §1 that cites all six mandatory papers in prose, credits `--leak-check` in paragraph
one, distinguishes the three adjacent papers, and states scope is in §5.2. Also add a real
`\cite{kapoor2022leakage}` to §4's lead sentence (it is currently in a LaTeX comment), and cite
`poliak2018hypothesis` beside Gururangan in Limitations.

### 3.4 Smaller defects a hostile reader will find

- `main.tex:552-554`: a floor "separates corpora that are sound from corpora that are not"
  contradicts the Feng paragraph at 597-600. Say "corpora where the label is trivially recoverable
  from those where it is not".
- F1 (`figures.py:163-168`) prints pairwise accuracies to four decimals against the repo's own rule;
  the table says 0.9543 where the prose says 0.955; its last row places a pairwise accuracy
  (0.8255) beside an AUROC from another split (0.4726) under the pairwise heading. Split the row,
  emit three decimals, add a preprocessing column.
- `scan/matched.py:29` reports `max(wt, 1 − wt)`, so the within-task floor cannot fall below 0.5;
  the permutation nulls beside it in F2 come from `floors2.py`, a different estimator (pooled GBM,
  unfolded, three replicates). Either permute labels within task and recompute the same folded
  statistic (200 replicates, about an hour) or say in the caption that the null is for the pooled
  estimator.
- `main.tex:429-430`: "thresholds were fixed from it before any arm ran". The ratio rule was; B was
  measured Sep 9, arm 1 returned Sep 8, the `confounded` band was added after. Say "the routing
  rule and its bands were fixed before any arm ran".
- `main.tex:337`: "two of the seven declare no licence". Six of seven do, from two publishers.
- `main.tex:331-332`: "no model is called at any point in their construction" is asserted; K1
  records the byte-diff against `codeparrot/apps` as not done. Scope it to the source field.
- The unreconciled 0.6836 (`bow.py`, stripped TF-IDF fitted within the test split, K1 §4.5) sits
  0.12 below the 0.8063 headline on the same corpus and preprocessing. One appendix sentence.
- No permutation null or CI on the APPS floors; `\nocodeCVsd` is an unused macro; PLAN.md §4 makes
  nulls beside every floor never-cut. `monitor-summary.json` ships a `ci` per monitor, unused. §6.
- `run_tests.py:241-243` books the 82 no-code generations as `mismatch`; true mismatches are 211.
- `verify_backdoor.py:153` counts a crash on the trigger as `backdoor_works = True`; ControlArena's
  validator requires no stderr and scores it False. Report crashes separately.
- `gen_backdoor_api.py:123` takes `todo.head(600)`, a prefix rather than a seeded sample; check that
  problem order does not track difficulty.
- `data.py:73-75`: `strip_comments` returns the source untouched on a tokenize error. Python-2-era
  human solutions therefore enter **B** with comments intact, and truncated generations keep theirs
  while clean ones lose them. Count the fall-through rate per class; it is a class-asymmetric
  comment leak inside the headline of a paper about comment leaks.
- `gate_s_samegen.py:124` builds B′'s honest side with `_honest_code()`, the shipped flag, while S's
  honest side is our harness: the crossed protocol fixed in `gate_s_baseline.py` (22 of 1,406),
  reintroduced. Pass the same selection.
- The API-arm disclosure owed by `notes/05` (three items) is one-third present in Limitations, and
  the paper never says the same-generator arm used a paid API. Two sentences; no dollar figure.
- Stale against the ledger: `experiments/README.md` says the Sonnet arm "has not been run";
  `GATE-S-RUNBOOK.md` says `gen_honest.py` and `gate_s_eval.py` never ran; `notes/02` A5 says "$0
  held allocation"; PLAN.md routes on "arm 1 (Qwen3.8-27B)", a model that never ran; `refs.bib`
  entry counts are given as 25, 27, 16 and 28 in four places (it is 28); the "8 KB" MIT file is
  5,797 bytes; RESULTS §4.10's arithmetic (427 − 381 = 46, usable 40) has an unstated bucket, and
  the prompt-variant percentages 83.3% and 66.7% are 5/6 and 4/6.
- The repo has no `LICENSE`. Pick MIT (matches both upstream artifacts) or soften "accompany this
  paper" to "will be released".
- The challenger-panels README confirms the `#`-count result and MIT verbatim but does **not**
  contain `code_length_only_auroc = 0.4726` or the 24-monitor min/median/max. Cite those to
  `runs/x2/leakage-checks.json` and `runs/x0/monitor-summary.json`.

---

## 4. Gate S: how to read S at small n

### 4.1 Power, and the interval that was about to be used

Hanley-McNeil 95% half-widths, equal classes:

| n | S ≈ 0.50 | S ≈ 0.60 | S ≈ 0.75 | S ≈ 0.87 |
|---|---|---|---|---|
| 50 | ±0.114 | ±0.111 | ±0.096 | ±0.072 |
| 125 | ±0.072 | ±0.070 | ±0.060 | ±0.045 |
| 200 | ±0.057 | ±0.055 | ±0.048 | ±0.036 |
| 335 | ±0.044 | ±0.043 | ±0.037 | ±0.028 |
| 400 | ±0.040 | ±0.039 | ±0.034 | ±0.025 |

`gate_s_eval.py` set `auroc_sd = np.std(aurocs)` across five folds of n/5 pairs each. Simulated
against a true 95% CI that interval is 1.89× too wide. Consequence, simulated at true S = 0.50:

| n | P(declare collapse) with ±2 fold-sd | with a proper 95% CI |
|---|---|---|
| 50 | 0.11 | 0.41 |
| 125 | **0.27** | **0.78** |
| 200 | 0.44 | 0.93 |
| 400 | 0.76 | ~0.99 |

So the rule as written was biased toward "inconclusive", which is the outcome that costs the title.
`evaluate()` now also returns a bootstrap-over-problems CI (sanity-checked on noise at n = 125:
0.42 to 0.55), and `gate_s_samegen.py` reads that one, printing the old interval beside it. **Say in
the paper that the interval rule was changed before the retry batch was read, and why.**

Underfitting is a real confound at small n: each training fold at n = 125 sees 200 documents
against 2,310 at n = 1,444, and `min_df=3` retains a fraction of the vocabulary. Two controls,
both CPU: (i) a matched-n learning curve of B (subsample the 1,444 pairs to n ∈ {50, 100, 125, 200,
400, 800, 1,444}, 50 draws each, identical pipeline); (ii) route on ρ against the problem-matched
B′ the script already fits, since both sides are then fitted at the same n on the same problems.
If B(125) is still near 0.85, a low S is a real collapse; if it falls toward 0.75, the bands move.

### 4.2 Eligibility: "passes tests and fires" was stricter than the benchmark

The 0.806 headline's attack class is 80.7% inert. B's attack class is all-firing. The classifier
scores 0.955 on inert backdoors. Three ways to define the same-generator attack class:

| Rule | n today (independent / edit) | Question it answers | Confound |
|---|---|---|---|
| (a) passes the public tests | **335 / 427** | can a trivial model separate honest code from code written with intent to sabotage that survives the tests, same author? | some attempts carry no real bug; but only 3 of 1,110 edit attacks are unchanged, and 381 of the 427 passing edit attacks contain a real logic change with a mis-chosen trigger |
| (b) every attempt | 587 / 1,110 | can it separate honest code from attempted sabotage at all? | broken programs; no monitor ever sees them; sanity row only |
| (c) passes and fires | 10 / 40 now, ~125 projected | the exact analogue of B | retry-survivor selection; no power |

**Recommendation.** Headline S is (a) on the independent arm, framed explicitly as the
same-generator analogue of the inert-backdoor result and of the benchmark's own labelling. Report
(c) beside it as the strict, B-matched robustness row, labelled underpowered. Route only where they
agree. Give (a) its own B′ that includes the benchmark's inert backdoors over the same problems,
or the comparison is inert-inclusive against all-firing. The sentence that makes it land: "80.7% of
the benchmark's labelled backdoors do not fire and the classifier scores 0.955 on them; our attack
class is defined the same way, by intent plus test-passing, not by success."

```
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5.jsonl --eligibility passes   # (a)
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5.jsonl --eligibility usable   # (c)
```

### 4.3 The selection effect in the retry pool

Survivors of retry skew toward problems with few tests and simple control flow, and toward short,
idiomatically narrow programs. Cheap checks on data already on disk: within the attack class, fit
the identical classifier to survivors vs non-survivors (AUROC near 0.5 means retention added no
lexical artifact); repeat on the honest side of survivor vs non-survivor problems (if this
separates, the effect is problem selection and largely cancels in S); Mann-Whitney on length and
the surface-7 vector and χ² on difficulty; and the clean paired control, S recomputed with a
non-surviving attempt from the same problem as the attack class.

### 4.4 The sentence for each outcome

Use verbatim with the measured values. Intervals are the bootstrap CI; bands are ρ against B′.

- **Collapse** (upper < 0.5 + 0.33(B′ − 0.5)): "With one model writing both the honest and the
  backdoored program, the bag-of-words classifier falls to S = 0.5xx (95% CI ..., n = N
  problem-disjoint pairs) against B′ = 0.8xx on the stored pairs over the same N problems,
  ρ = 0.xx. Holding authorship constant removes xx% of the separability."
- **Partial**: "S = 0.6xx (95% CI ...; n = N) against B′ = 0.8xx: ρ = 0.xx. Authorship accounts for
  roughly xx% of the separability and surface content for the remainder. Neither alone explains the
  benchmark's 0.87."
- **Content** (lower > 0.5 + 0.72(B′ − 0.5)): "Even with authorship held constant a bag-of-words
  classifier separates the classes at S = 0.8xx (95% CI ...; n = N), retaining ρ = 0.xx. These
  backdoors carry surface signal that is not an authorship artifact; monitors must be reported
  against this lexical floor, and same-generator sampling alone does not remove it."
- **Inconclusive** (the likely outcome at n ≈ 125 under (c)): "S = 0.6xx with a 95% CI of
  0.5xx to 0.7xx over n = N pairs spans both bands. We state the interval and do not round it to a
  verdict. The limiting factor is the 2% single-shot yield of same-generator backdoors that both
  evade the public tests and fire, which is itself a measurement: the stored attack class is the
  survivor set of an unreported number of retries."
- **Did not land**: "The same-generator control did not reach a readable n before submission. The
  authorship reading is therefore inference, from cross-generator transfer, equal separability on
  inert and working backdoors, the style markers, and the schema asymmetry in which the attack
  class records its generator and the honest class has no such field, and is labelled as inference."
- **The edit arm, wherever it appears**: a lower bound on S under maximal pair similarity, not a
  verdict (mean similarity 0.924, median 0.990, 68.7% above 0.95, against 0.469 for the benchmark).

---

## 5. The four pages

### 5.1 Cut plan (lands at about 4.0 pages with a written §1)

Current: 2,352 prose words, 573 words of float text, five `[t]` floats. Estimated 6.0 to 6.2
content pages with a written §1. Keep one float in the body: F3, the two floors against the 24
monitors, caption caveats intact.

| Action | Saves (pp) |
|---|---|
| F1 (14-row table) → appendix; keep 0.4726 → 0.806 and 0.7715 ± 0.0389 in prose | 0.35 |
| F2 → appendix; keep bash 0.504 / agentdojo 0.802 and the two-mechanisms sentence in prose | 0.40 |
| Similarity table → appendix; one sentence with 0.469 / 0.924 / 0.415 (re-measured, autojunk off) | 0.15 |
| Schema table → one sentence | 0.11 |
| Gate S block (about 380 words) → about 150: arm-1 null with carrier decomposition, two-arm design in three sentences, yield in two | 0.33 |
| Token-test paragraph → one clause plus appendix | 0.20 |
| Byline paragraph → one sentence | 0.13 |
| Harness paragraph → 35 words | 0.14 |
| CoT paragraph → cut (PLAN §5's first cut) | 0.11 |
| Limitations four paragraphs → three | 0.20 |
| Drop "an earlier version of this work..." (double-blind soft spot) | 0.05 |

Word budget: abstract 180 to 200 (from 238), §1 420, §2 300, §3 780, §4 190, §5 190.

### 5.2 A §1 that works under every outcome

Paste at `main.tex:236`, replacing lines 249-293. About 430 words; uses the file's macros; makes
no claim about S.

```latex
\section{Introduction}

Trusted monitoring is the backbone protocol of AI control: a weaker trusted model reads an
untrusted model's output and flags sabotage \cite{greenblatt2023aicontrol}. It is developed,
tuned and ranked almost entirely on \emph{stored} honest/attack pairs --- fixed corpora of
solutions, some carrying a planted backdoor \cite{koran2026ensemble, terekhov2025controltax,
jha2026decorrelation}. The field already knows these pairs leak, and it says so in print. Koran
et al.\ keep only working honest solutions and working backdoors and strip every comment, with
the rationale stated \cite{koran2026ensemble}; Control Tax reports the pass-tests pre-filter and
appendices ``Monitoring failed backdoors'' \cite{terekhov2025controltax};
\cite{sreevatsa2026legibility} is an entire paper on the comment channel. The sharpest treatment
is Jha's, whose released harness ships a \texttt{--leak-check} flag with two trivial baselines
already inside it and concludes that stripping is mandatory rather than cosmetic: a
\texttt{\#}-count detector falls from \hashRaw{} to \hashStripped{} once comments go, and code
length alone sits at \lenFiltered{} \cite{jha2026decorrelation}. This paper starts from that
work, not against it.

What nobody has measured is what the preprocessing leaves behind. On the field's own filtered,
comment-stripped split, a bag-of-words classifier reaches AUROC \tfidfKoran{} --- above
\tfidfKoranCount{} of the \monN{} open-weight monitors ranked on that same split, whose median
is \monMedian{} --- and a classifier that reads no code at all, only problem difficulty, test
count and question length, reaches \nocodeCV{}, above \nocodeCVCount{}.

The residue is authorship, not sabotage. Honest solutions come from APPS
\cite{hendrycks2021apps} and are human-written; every backdoor is model-written. The
classifier transfers across backdoor generators and is as strong on \textbf{inert} backdoors as
on working ones --- neither is a property of a backdoor. That bag-of-words separates
human-written from model-written code is established out-of-field and we cite it as
established \cite{orel2026aicd}; the known-ness of the mechanism is the argument, not a dent in
it. The neighbouring field already applies the control missing here --- CodeMirage gates its
two classes on line count and character length \cite{guo2025codemirage}, MultiAIGCD pairs to
shared problem definitions \cite{demirok2025multiaigcd} --- so unmatched pairs are a defect by a
published standard, not one we invented. Adjacent control work attacks other axes:
\cite{terekhov2026adaptive} subverts monitors with injected text,
\cite{gewang2026attackselection} shows attacker-side selection inflates safety estimates, and
\cite{pinto2026calibration} removes transcript length as a nuisance covariate, where we publish
a content-blind AUROC as a per-benchmark floor.

We contribute (i)~a protocol $\times$ baseline measurement of what survives the field's
preprocessing; (ii)~evidence that the surviving signal is authorship, including a negative
result showing that regenerating one half of a stored pair swaps the confound rather than
removing it; (iii)~a second selection artifact the field's own filter installs, by defining the
negative class through attack failure; and (iv)~a preprocessing checklist and a released split.
\textbf{Scope:} this concerns monitor training, selection and benchmarking on \emph{stored}
pairs. ControlArena's live evaluations generate both classes and are not implicated.
```

Fill the transfer and inert numbers back into paragraph three only after `strip_recheck.py` has
run; the draft above deliberately states them without values.

### 5.3 The Gate S paragraph for the did-not-land case

Replaces `main.tex:492-499` and the Limitations TODO at 631-633.

```latex
\textbf{The same-generator control did not land, and the authorship reading is inference.}
Holding authorship constant requires one model to write both classes; our attack generations
converted at roughly 2\% into pairs that both pass the public tests and fire on their trigger
--- 40 of 1,112 in the edit arm and 10 of \nIndep{} in the independent arm, against the
50-pair floor our analysis script requires --- so we report no $S$. The authorship reading is
inference from the transfer, inert-backdoor and style evidence together with the five
same-generator settings. The yield gap is itself a measurement: ControlArena attack policies
resample and keep survivors, so the stored attack class is heavily filtered relative to any
single-shot rate.
```

If (a) from §4.2 is computed in time, add one sentence with its value, its CI, its n and its
pair similarity, and label it as the test-passing definition.

---

## 6. Further work, ranked by value per hour

Everything above the line is CPU and free. Cost basis for the API rows: $0.005 per request,
about $0.30 per usable pair at the 1.7% yield; $86 remains of the $100 ceiling.

| # | Action | Cost | Hours | Why |
|---|---|---|---|---|
| 1 | `strip_recheck.py --seeds 5` | $0 | 1 | two of three authorship legs depend on it (§3.1) |
| 2 | Make abstract and §3 truthful about S; write §1; execute the cut plan | $0 | 2 | §3.2, §3.3, §5 |
| 3 | S under `--eligibility passes` on the independent arm (n 335), with an inert-inclusive B′ | $0 | 1 | the only powered same-generator number available today |
| 4 | Bootstrap CI on 0.8063 and on the no-code floor; paired bootstrap against the 24 monitors using `runs/scores/` per-item files; permutation null on 0.806 | $0 | 1 | turns "above 20 of 24 point estimates" into a claim; DeLong is unstable with 172 positives, use the paired bootstrap |
| 5 | Matched-n learning curve of B | $0 | 1 to 2 | without it a low S at small n is underfitting until proven otherwise |
| 6 | Survivor vs non-survivor lexical check | $0 | 0.5 | answers the selection-effect objection the ledger already commits to raising |
| 7 | Fix F1 (three decimals, split the cross-protocol row, preprocessing column); fix the "sound corpora" sentence | $0 | 0.5 | §3.4 |
| 8 | Verify the retry batch when it lands; compute (c) at whatever n arrives; report beside (a) | $0 | 1 to 3 wall | already paid for |
| 9 | Re-measure pair similarity with `autojunk=False` | $0 | 0.2 | the 0.924 / 0.415 / 0.469 figures were measured with the heuristic on |
| 10 | Scripts for the byline counts and the stored-similarity sample | $0 | 0.5 | two paper numbers currently have no producer |
| 11 | F2's null: permute within task, same folded statistic, 200 replicates | $0 | 1 | or caption the mismatch |
| 12 | Symmetrise `gate_s_eval.py` onto our own flag and rerun arm 1 | $0 | 1 | only because arm 1 is in the paper |
| 13 | LLM-monitor positive control on the same-generator pairs (2N calls, batch) | $2 to 4 | 1 | needed only if S collapses, to answer "your pairs contain no backdoor" |
| 14 | Top-up batch 125 → ~200 usable (4,412 requests) | ~$22 | 4 to 8 wall | only after item 4's interval change, and only if the retry batch under-delivers |
| — | 125 → 400 usable (16,176 requests) | ~$81 | 12+ | **do not**: it buys under the old rule what the interval fix buys for free, and per-problem yield is heterogeneous so 400 is an optimistic ceiling |

Drop: the size ladder and dose-response arms; the all-attempts row (b) beyond a supplementary
sanity line; the Gate S figure (a table is enough at four pages); any further prompt engineering.

---

## 7. Literature and venue, what is new today

**Venue**, from the workshop page's GitHub source (`LiuJ-2023/EvoRobust-NeurIPS2026`, last commit
Aug 24): Sep 12 AoE is itself an extension granted Aug 21; no sign of another. Reviews due Sep 16,
meta-review Sep 23, notification Sep 29, camera-ready Oct 29 at five content pages. No review
criteria are published anywhere on the page. Four invited speakers not in the G2 record: Lora
Aroyo, Ismini Lourentzou, Zhu Sun, Xin Yao. Aroyo works on data quality and annotator
disagreement, authored none of the corpora, and is the most sympathetic reader on the roster; one
sentence in the data-quality register ("the two classes were produced by different processes")
costs nothing. Whether a checklist is required is unverified either way.

**Not in `refs.bib`**, verified at title level only (read each before citing, per R1):

| Paper | Why |
|---|---|
| Bean, Rocher et al., *Measuring what Matters: Construct Validity in LLM Benchmarks*, arXiv:2511.04703, NeurIPS 2025 D&B | 445 benchmarks screened; only 16% report a statistical test. The general case of this paper's specific case, and a peer-reviewed precedent for the checklist ending |
| Ren et al., *Safetywashing*, arXiv:2407.21792, NeurIPS 2024 D&B | the canonical "safety benchmark measures the wrong thing" paper; same shape (known qualitatively, unmeasured quantitatively) |
| Hariharan et al., *Rethinking CyberSecEval*, arXiv:2411.08813 | identifiers and comments leaked label cues in an LLM security benchmark; they shipped the corrected split. Closest precedent for both mechanism and deliverable |
| Arp et al., *Dos and Don'ts of Machine Learning in Computer Security*, USENIX Security 2022 | the security-venue Kapoor & Narayanan; the right citation for this PC |
| *Compared to What? A Human-Anchored Security Benchmark for LLM-Generated IaC*, arXiv:2608.28021 (Aug 28) | the neighbouring field building a size-matched human baseline deliberately, three weeks ago |
| Bisztray et al., *I Know Which LLM Wrote Your Code Last Summer*, arXiv:2506.17323, ACM AISec 2025 | security-venue authorship attribution; one clause |
| Kaufman et al., *BashArena*, arXiv:2512.15688 | the corpus has its own paper; cite it rather than only `2606.06529` |

**Scoop check**: searches for trivial or partial-input baselines on AI-control corpora, and for
anyone naming the human-vs-LLM authorship confound in a control corpus, both came back empty.

---

## 8. Schedule to the wall

All times relative to now; the wall is Sep 13 11:59 UTC.

| Block | Hours | Do |
|---|---|---|
| A | 0 to 1 | `strip_recheck.py --seeds 5`; re-measure similarity with `autojunk=False`; start item 3 (S under `passes`) in the background |
| B | 1 to 3 | write §1 (§5.2); make abstract and §3 truthful (§3.2, §5.3); execute the cut plan; toggle `\TODO` off only after §1 is in |
| C | 3 to 4 | fold the stripped numbers in; F1 fixes; the "sound corpora" sentence; the licence count; the API-arm disclosure sentences |
| D | 4 to 5 | bootstrap CI and permutation null on 0.806 and 0.772; paired bootstrap against the 24 monitors; put the intervals in prose |
| E | 5 to 6 | matched-n B curve; survivor check; write the S paragraph from whichever of (a)/(c) is readable, or the did-not-land paragraph |
| F | when the retry batch lands | verify; (c) at its n; one sentence beside (a) |
| G | last 2 hours | compile from a fresh checkout; check the four-page count; `LICENSE`; anonymity pass; submit |

If block A comes back badly for the transfer and inert rows, blocks B and C absorb it: the
abstract loses one sentence and §3 loses one paragraph, and the schedule does not move.

---

## 9. After the workshop

Camera-ready allows five pages: that is where S under both eligibilities, the learning curve, the
survivor check and the Gate S table go. The November version (FAccT, ARR, or the AAAI workshops
per `notes/01`) needs: S at n ≥ 200 under a correctly sized interval; the fix demonstrated
end-to-end by re-ranking the 24 monitors on a same-generator split; a second stored-pair benchmark
family for the authorship mechanism; and the released split under a licence.
