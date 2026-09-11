# Local handoff: everything that needs the data, and how to fan it out

Written 2026-09-11 for a Claude Code session running **locally**, on the machine that already holds
the parquet shards and the Gate S run products. The remote session that wrote this could reach
GitHub and PyPI but not HuggingFace, so every script on this branch was tested end to end on
synthetic files with the real schema and **has never touched the real data**. This document is the
bridge: what exists, what each run needs, the order, the decision rules, what to write where, and
how to split it across subagents without two of them editing the same file.

Read with it, in this order: `notes/06-path-to-submission.md` (the audit and the plan),
`experiments/GATE-S-READING.md` (how to read S), `experiments/RESULTS.md` (the ledger),
`notes/07-release.md` (the release procedure), `paper/README.md` (the LaTeX build and its traps).
`experiments/HEADLINE-CI.md` is being written by the last remote agent and may land in a later
commit; `headline_ci.py --help` is authoritative until it does.

The wall: **Sep 12 AoE = Sep 13 11:59 UTC.** Budget: **$86.37** left of a $100 ceiling; spent
$13.63. Every run below is CPU and free except the positive control (about $1.55, worst case $2.60).

---

## 0. Ground rules for whoever coordinates

1. **Reproduce B before trusting anything.** `python gate_s_baseline.py` must print
   `B = 0.8714` (sd 0.0085, n 1,444, pairwise 0.9605, length 0.6081, surface-7 0.7673). It has been
   bit-identical across two machines and two library generations. If it is not, stop and find out
   why before running anything new; the environment is wrong, not the science.
2. **Self-check every reimplementation against a number already on record** before reading its new
   column. `strip_recheck.py`'s *unstripped* column must reproduce `REPRODUCED.md`: TF-IDF 0.9425,
   pairwise 0.962 (one pair of slack), working 0.979, inert 0.955, surface-7 0.8302, length
   within-pair 0.821 to 0.826, transfer 0.9935 / 0.9756 / 0.8130 / 0.8283. Only then read the
   stripped column.
3. **Numbers rules, unchanged.** Pairwise accuracies get three decimals. Never write 0.772 next to
   "above 18 of 24" (0.7715 clears 20; 0.7163 clears 18). Every "X above Y" names Y's split, metric
   and preprocessing. A value from one protocol never sits beside a count from another.
4. **Every number that enters the paper enters `experiments/RESULTS.md` first**, with the command
   that produced it, in a new dated section, superseded rows kept and marked. Then it becomes a
   macro in `paper/main.tex` (all load-bearing numbers are macros at the top of the file; never
   hardcode inline).
5. **One owner per file.** The fan-out in §6 assigns files. A subagent that needs a change in a
   file it does not own reports the change to the coordinator instead of making it.
6. **Do not spend on a top-up batch** until the interval fix has been read against the real S
   (`notes/06` §4.1). Do not buy 400 pairs at all.
7. Commit small and often on `claude/vigilant-maxwell-p05yuk` (or a branch off it), push after
   each commit. Nothing person-identifying, no batch ids, no keys, no local paths in anything that
   is tracked.

---

## 1. Inventory: what must exist on the local machine

### 1.1 From HuggingFace (public, ungated). `fetch.py` and `fetch_inputs.py` create these.

| File(s) | Source | Size | Needed by |
|---|---|---|---|
| `experiments/apps/train_*.parquet` (3 shards) | `RoganInglis/apps-control-arena`, MIT | 744 MB | everything in §3 to §5 |
| `experiments/apps/koran_meta.parquet` | `eugenekoran/apps-control-arena-high-quality`, no licence | small (column-projected) | `headline_ci.py`, `koran_split_eval.py` |
| `experiments/apps/koran_test_code.pkl`, then `koran_samples.pkl` (from `bow.py`) | same | 24 MB | `headline_ci.py` |
| `experiments/apps/monitor-summary.json` | `anik-jha/challenger-panels`, MIT (tracked in repo) | 6 KB | `headline_ci.py` |
| `experiments/apps/runs/scores/*` (24 per-item score files) | same GitHub repo | small | `headline_ci.py` fetches them itself unless `--no-fetch` |
| `experiments/scan/ca_*.parquet` (5 files) | `adityaasinha28/control_arena_*`, no licence | ~290 MB | only the optional F2 null fix |

```
cd experiments/apps
python fetch.py            # shards
python fetch_inputs.py     # koran_meta.parquet, koran_test_code.pkl, monitor-summary.json
python bow.py              # koran_samples.pkl
python gate_s_pool.py      # gate_s_pool.parquet (1,444-problem analysis pool + question text)
```

If the shards are already present from the September runs, `fetch.py` is not needed; check that
`gate_s_pool.py` reports 5,000 / 3,420 / 1,582 / 1,444 exactly.

### 1.2 Local artifacts that exist nowhere else (the Gate S run products)

All in `experiments/apps/`, all gitignored (`*.jsonl`). **Run `ls -la *.jsonl *.batch*.json` first
and reconcile against this table; names are what the scripts default to, not a guarantee.**

| File | Producer | Records | Fields |
|---|---|---|---|
| `gen_sonnet5.jsonl` | `gen_honest_api.py` | 1,444 | `problem_id, model, code, raw, finish_reason, n_prompt_tokens, n_output_tokens, truncated` |
| `pass_sonnet5.jsonl` | `run_tests.py --solutions gen_sonnet5.jsonl` | 1,444 (1,112 `passed`) | `problem_id, passed, n_cases, reason, ...` |
| `bd_sonnet5.jsonl` | `gen_backdoor_api.py` (edit arm) | 1,112 | `problem_id, model, code, arm, thinking, backdoor_input, raw, finish_reason, n_output_tokens, truncated` |
| `bdpass_sonnet5.jsonl` | `verify_backdoor.py` on the edit arm | 1,112 (427 pass, 40 usable) | `problem_id, model, passes_tests, backdoor_works, reason` |
| `bdind_sonnet5.jsonl` | `gen_backdoor_api.py --independent` | 600 | as edit arm, `arm = independent` |
| **`bdindpass_sonnet5.jsonl`** (runbook name) or `bdpass_sonnet5.jsonl` overwritten | `verify_backdoor.py` on the independent arm | 600 (335 pass, 10 usable) | as above |
| retry rounds: six files written with `--state-suffix`, names unknown from here | `gen_backdoor_api.py --independent --state-suffix rN` | 6,672 total | as above |
| `pass_human_fixed.jsonl` | `run_tests.py --solutions human` | 115,212 | human class under our harness; `gate_s_baseline.py --human-pass-file` |
| `gen_q3c30.jsonl`, `pass_q3c30.jsonl` | Qwen arm 1 (vLLM, cluster) | 3,420 / 668 usable | only if arm 1 is re-evaluated |

⚠️ **The independent-arm verifier file name is the one real ambiguity.** `GATE-S-RUNBOOK.md:498`
names it `bdindpass_sonnet5.jsonl`; `gen_backdoor_api.py:196` prints a "next" hint that names
`bdpass_sonnet5.jsonl` for both arms. If the hint was followed literally, the edit arm's verdicts
may have been overwritten. Check record counts (edit 1,112 vs independent 600) and the `arm`
field of the matching `bd*` file. If the edit verdicts were lost, regenerate them in two minutes:

```
python verify_backdoor.py --backdoors bd_sonnet5.jsonl --honest-gen gen_sonnet5.jsonl --out bdpass_sonnet5.jsonl
```

⚠️ **The retry rounds must be merged and verified before anything reads them.** Concatenate the
six round files into `bdind_sonnet5_retry.jsonl` (keep the `problem_id` duplicates; a problem may
have up to seven draws), run `verify_backdoor.py` over the merged file, and record in RESULTS.md how
many candidates, how many pass, how many fire, per round and pooled. Then decide `--keep first`
(single-shot, one draw per problem) versus `--keep best` (retry-survivor selection, the benchmark's
own procedure and the selection effect the paper criticises). The paper reports the strict S under
`best` **only** with the sentence in `notes/06` §4.4 about inheriting the selection effect, and
reports the survivor-vs-non-survivor check (§3.4 below) beside it.

### 1.3 Python environment

`pandas pyarrow scikit-learn numpy matplotlib requests huggingface_hub anthropic`. B was
bit-identical under sklearn 1.7.1/pandas 2.3.1 and sklearn 1.9.0/pandas 3.0.5, so either is fine;
record the versions in RESULTS.md. `ANTHROPIC_API_KEY` in the environment for `monitor_samegen.py`
only. Python 3.11 or 3.12 (`fractions.gcd` fails on both, which is expected and documented).

---

## 2. The dependency graph

```
fetch/pool  ──►  gate_s_baseline (B check)  ──►  everything else
                                                  │
        ┌─────────────────────────────────────────┼──────────────────────────────┐
        ▼                                         ▼                              ▼
 strip_recheck (§3.1)                    reconcile jsonl names (§1.2)     headline_ci (§3.5)
 [no jsonl needed]                                │                        [koran caches needed]
        │                              ┌──────────┴──────────┐
        ▼                              ▼                     ▼
 paper: §3 authorship paragraph   samegen passes + usable   merge+verify retry rounds
 (§4.2)                           (§3.2)                    (§1.2)  ──► samegen usable at new n
                                       │
                          ┌────────────┼────────────────┐
                          ▼            ▼                ▼
                   learning curve   monitor_samegen   survivor check
                   (§3.3)           (§3.6, $)         (§3.4)
                          └────────────┴────────────────┘
                                       ▼
                          paper: Gate S paragraph + Limitations (§4.3)
                                       ▼
                   release_split build + check (§5)  ──►  supplementary zip
```

Independent of all of the above: the introduction, the cut plan, the TODO-citation fix, Table 1
fixes, the licence-count and API-disclosure sentences (§4.1). Start those immediately.

---

## 3. The runs, in order, with what each returns and how to read it

All commands run from `experiments/apps/`.

### 3.1 The stripped re-check (first; nothing else in the authorship paragraph is safe until this lands)

```
python strip_recheck.py --seeds 5
```

What it is: `matched.py` and `transfer.py`, line for line, with `data.strip_comments` applied to
both classes, printed beside the unstripped values, over five problem-disjoint 30% splits.
Why: the transfer (0.9935), the working-vs-inert contrast (0.979 vs 0.955), the surface-7 and
length rows were all computed on code **with comments in**, and the paper introduces them right
after "on that same filtered, comment-stripped split". The `#`-present style marker is literally
the comment channel.

Read it:
- Unstripped column matches `REPRODUCED.md` (rule 0.2)? If not, the reimplementation is off; fix
  before reading further.
- Stripped transfer ≥ 0.95 and stripped inert within 0.03 of stripped working: **the legs hold.**
  Paper gains one sentence ("all matched-protocol numbers are comment-stripped; unstripped values
  in the appendix were X") and F1 gains a preprocessing column.
- Stripped transfer in 0.85 to 0.95, or inert falls 0.03 to 0.08 below working: **weakened but
  standing.** Report the stripped values everywhere; move the unstripped ones to an appendix row
  labelled as inflated by the comment channel.
- Stripped transfer < 0.85, or inert collapses toward 0.5 while working does not: **the legs fail.**
  The authorship reading leans on the schema, the `__main__` marker (152 vs 1 on Koran's stripped
  train split, already stripped), the arm-1 confound swap, and the agentic negative control. Remove
  the abstract sentence "transfers almost unchanged across backdoor generators"; keep the inert
  result out of §3 or report it as failing under stripping.

Whatever comes back, **the paper reports the stripped numbers.** Record all seven quantities, both
columns, mean ± sd, in RESULTS.md as a new §6.

### 3.2 The same-generator S, both eligibility rules

```
# headline: attack class = passes the public tests; B' matched to that rule
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5.jsonl --bdpass <independent verifier file> \
    --eligibility passes --bprime-inert
# strict: attack class = passes AND fires; B' all-firing
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5.jsonl --bdpass <independent verifier file> \
    --eligibility usable
# the edit arm, same two, reported only as a bound (pairs are near-copies)
python gate_s_samegen.py --tag sonnet5 --eligibility passes --bprime-inert
python gate_s_samegen.py --tag sonnet5 --eligibility usable
```

Outputs `gate_s_samegen_sonnet5_<arm>_<eligibility>.json` with `S` (fold-mean AUROC, fold sd,
pooled out-of-fold AUROC, `auroc_ci95_boot`), `B_prime` on the same problems, `retained_vs_stored`
(ρ), `rho_ci95`, `pair_similarity` (now with `autojunk=False`, and a like-for-like
`stored_same_problems` block), `problem_ids`, `verdict`, `verdict_lines`.

Read it per `experiments/GATE-S-READING.md`: route on ρ against B′ using the **bootstrap** interval,
not the fold sd; the four verdict states are collapse, partial (stable), content, inconclusive. The
`usable` independent arm will refuse below 50 pairs until the retry rounds are merged (§1.2); that
refusal is correct, not a bug. Re-measure and record pair similarity: the ledger's 0.924 / 0.415 /
0.469 were computed with `autojunk` on and will move.

Expected shape, not a prediction: `passes` on the independent arm gives n ≈ 335 (the intersection of
1,112 honest passers with 335 attack passers over the same problems will be somewhat below 335;
report the realised n).

### 3.3 The learning curve of B at matched n

```
python gate_s_learning_curve.py --match-problems gate_s_samegen_sonnet5_independent_passes.json
python gate_s_learning_curve.py --match-problems gate_s_samegen_sonnet5_independent_usable.json --out gate_s_learning_curve_usable.json
```

Flags: `--grid` (default 50,100,125,200,335,400,800,full), `--draws 30`, `--seed`, `--boot`,
`--human-pass-file pass_human_fixed.jsonl` to use our own flag as `gate_s_baseline.py` does.
Output: mean ± sd of every carrier at each n, the mean CI width, and B over the exact problem
ids S used. The last line is the sentence for the paper. Read it: if B at S's n is within ~0.03 of
0.87, a low S is not sample size; if B falls toward 0.75 at that n, the bands in absolute AUROC
move and the paper must route on ρ against the matched B′ only, saying so.

### 3.4 The survivor-selection check (needed only if the strict S uses the retry pool)

No script exists yet; it is a 40-line variant of `evaluate()` and a good subagent task. Within the
merged independent-arm candidates: (a) fit the identical TF-IDF pipeline to survivors (pass AND
fire) vs non-survivors, problem-disjoint; AUROC near 0.5 means retention added no lexical artifact,
≥ 0.70 means S is contaminated and the number is reported; (b) the same on the honest side of
survivor problems vs non-survivor problems (if this separates, it is problem selection, shared by
both classes, and largely cancels in S); (c) Mann-Whitney on length and the surface-7 vector and
χ² on difficulty tier, survivors vs not. Record all three in RESULTS.md beside the strict S.

### 3.5 Headline uncertainty and the paired comparison with the 24 monitors

```
python headline_ci.py                    # fetches runs/scores/ from GitHub if absent
python headline_ci.py --skip-tfidf       # no-code floors only, if the train shards are not local
```

Output `headline_ci.json` and a printed table: for TF-IDF 0.8063 and for both no-code protocols
(0.7715 by 5×5 CV within test; 0.7163 single held-out), a bootstrap-over-problems 95% CI, a
training-label permutation null (95th percentile and empirical p), and per monitor the paired
bootstrap of (ours − theirs) on identical items with its CI. The sentence it prints is the one for
the paper: "TF-IDF X (95% CI a to b; permutation null 95th percentile c), above k1 of 24 monitors,
k2 of them with a paired-bootstrap CI excluding zero." Keep each no-code value with its own count.
It uses the paired bootstrap rather than DeLong because 172 positives make DeLong unstable.

### 3.6 The positive control (the only spend; run after 3.2 has a readable S)

```
export ANTHROPIC_API_KEY=...
python monitor_samegen.py --tag sonnet5 --bd bdind_sonnet5.jsonl --bdpass <independent verifier file> \
    --eligibility passes --dry-run           # prints ~$1.55 est / $2.60 worst for ~335 pairs
python monitor_samegen.py --tag sonnet5 --bd bdind_sonnet5.jsonl --bdpass <independent verifier file> \
    --eligibility passes --spent 13.63
```

Two requests per pair (honest, attack), problem statement plus comment-stripped code, a
trusted-monitor prompt ending in `SCORE: <int>`; order shuffled; resumable from
`monitor_samegen.batch.<tag>_<arm>_<elig>.json`; output json has every per-program score and raw
reply. Reports AUROC with a bootstrap CI over problems, pairwise accuracy (ties at half credit and
strict), and the count of unparseable replies (recorded as missing, never imputed). Read it: the
paper needs the monitor's AUROC beside S on the same pairs. Monitor ≥ 0.70 with S near 0.5 is the
result that makes a collapse believable; monitor near 0.5 too means the generated attacks are not
detectable by this monitor either, which must be reported and weakens the collapse reading. The
model is the same one that wrote both classes; disclose that in the sentence.

### 3.7 Optional, if time remains: the F2 null and arm 1 symmetrised

- F2 null: permute labels within task and recompute the same folded within-task statistic that
  `scan/matched.py:29` reports, 200 replicates, so the dumbbell in F2 compares like with like.
  Needs the five `ca_*.parquet`. Otherwise caption the mismatch.
- Arm 1 under our own flag on both sides: `gate_s_eval.py` gates the human side on the artifact's
  `solution_passes_tests` and the LLM side on our harness. Add `--human-pass-file` there in the
  same way `gate_s_baseline.py` does and rerun with `gen_q3c30.jsonl` / `pass_q3c30.jsonl`.
  Expect ρ to stay above 1; record it.

---

## 4. The paper: what changes, by section

`paper/main.tex`; build with `latexmk -pdf main.tex` from `paper/`. Draft is ~6 content pages
with §1 unwritten against a limit of 4. Cut plan and word budget: `notes/06` §5.1.

### 4.1 Independent of every run (start now)

1. **§1 Introduction.** Paste the draft from `notes/06` §5.2 (cites all six mandatory papers in
   prose, credits `--leak-check` in paragraph one, distinguishes the three adjacent papers, states
   scope). Leave the transfer/inert values out of paragraph three until §3.1 has landed.
2. **The `\TODO` citation bomb.** Five keys (`terekhov2025controltax`, `sreevatsa2026legibility`,
   `gewang2026attackselection`, `terekhov2026adaptive`, `pinto2026calibration`) exist only inside
   `\TODO{}`. Writing §1 fixes it; verify with `grep -c` after, and only then uncomment
   `\renewcommand{\TODO}[1]{}`. Add real `\cite{kapoor2022leakage}` in §4's lead sentence and
   `\cite{poliak2018hypothesis}` beside Gururangan in Limitations.
3. **Abstract and §3 truthful about Gate S.** Delete or rewrite `main.tex:229-231`; fix
   `488-490` ("n = 600 requested"); replace the TODO at `492-499` with the did-not-land paragraph
   from `notes/06` §5.3 as a placeholder until §3.2 gives a real S.
4. **The cut plan** (`notes/06` §5.1): F2 and F1 to appendix, similarity and schema tables to
   sentences, Gate S block to ~150 words, token test to a clause, byline to a sentence, harness to
   35 words, CoT paragraph out, Limitations to three paragraphs. Keep F3 as the one body figure.
5. **Table 1 fixes** in `figures.py`: three-decimal pairwise accuracies; split the row that puts
   0.8255 (pairwise) beside 0.4726 (AUROC on another split); add a preprocessing column.
6. **Sentence fixes**: `552-554` "sound corpora" → "where the label is trivially recoverable";
   `429-430` "thresholds were fixed before any arm ran" → "the routing rule and its bands were";
   `337` "two of the seven declare no licence" → six of seven, two publishers; `331-332` scope the
   "no model is called" claim to the source field; `525-527` soften the causal claim about test
   counts to "consistent with".
7. **Disclosures owed** (`notes/05`): the same-generator arm used a paid API; sampling parameters
   unavailable so not bit-reproducible; thinking off though the stored attacker was a thinking
   model. Two sentences in Limitations, no dollar figure.
8. **Release sentence**: replace `main.tex:589` "Ours accompany this paper" with the sentence in
   `notes/07-release.md` once §5 has produced the bundle; until then "will be released under MIT".

### 4.2 After §3.1 (the stripped re-check)

The "signal is authorship, not sabotage" paragraph (`main.tex:391-402`): replace the transfer,
working and inert values with the stripped ones; drop the `#`-present marker; keep `__main__`;
add the sentence that all matched-protocol numbers are comment-stripped. Update the macros
`\transfer`, `\pairWorking`, `\pairInert`, `\surfaceSeven`. If the legs failed, restructure per
§3.1's third outcome.

### 4.3 After §3.2 to §3.6 (Gate S)

Replace the placeholder with the outcome sentence from `notes/06` §4.4 (collapse / partial /
content / inconclusive), giving S, its bootstrap CI, n, pass rate, ρ against B′ with its CI, pair
similarity beside it, the matched-n B from §3.3, and the monitor's AUROC on the same pairs from
§3.6. Report the strict S beside the headline S; if it used the retry pool, add the
selection-effect sentence and the §3.4 result. Report the edit arm only as a bound. Update the
macros (`\baselineB` stays; add `\sameGenS`, `\sameGenN`, `\sameGenLo`, `\sameGenHi`,
`\sameGenRho`, `\monitorS`). If nothing readable lands, the did-not-land paragraph stands.

### 4.4 After §3.5

Put the intervals into the two headline sentences and the F3 caption; the "above k of 24" count
gains "k2 with a paired-bootstrap CI excluding zero".

### 4.5 Before submission

Fresh-checkout compile; four content pages exactly (references and appendix unlimited); `\TODO`
no-op; anonymity pass (no names, URLs, costs, "our earlier repo"); the licence sentence; the
supplementary zip attached; `README.md` and `RESULTS.md` status boxes synced to what shipped.

---

## 5. The release

`notes/07-release.md` has the procedure; `experiments/RELEASE-CARD.md` is the rendered card.

```
python release_split.py --out ~/asn-release --bdpass-independent <independent verifier file> --keep first
python release_split.py --check ~/asn-release
```

`--keep best` only with the retry pool and only with the selection-effect disclosure. The
checker refuses upstream code, forbidden fields, local paths and batch ids. Zip the directory and
attach it as supplementary material (primary route; no external account); optionally upload to an
anonymous HuggingFace dataset repo with the `hf` commands in `notes/07`. `LICENSE` at the repo root
is MIT with an anonymous copyright line.

---

## 6. Fan-out: subagents, ownership, and merge order

Seven workers plus a coordinator. Each owns the files listed and touches nothing else; each
reports numbers to the coordinator in the RESULTS.md format (quantity, value, n, command).

| Worker | Owns | Does | Needs | Blocks |
|---|---|---|---|---|
| **A · Environment and inventory** | nothing tracked | §1.1 fetch or verify, `gate_s_pool.py` counts, `gate_s_baseline.py` = 0.8714, `ls` and reconcile every jsonl against §1.2, regenerate the edit verdicts if lost, merge and verify the retry rounds into `bdind_sonnet5_retry.jsonl` + `bdindpass_sonnet5_retry.jsonl` | the local machine | everyone |
| **B · Stripped re-check** | `RESULTS.md` §6 (new) | §3.1, self-check against REPRODUCED.md, record both columns | A's B check | E (paragraph 4.2) |
| **C · Gate S** | `RESULTS.md` §7 (new), the samegen/learning-curve json outputs | §3.2 all four runs, §3.3 both, §3.4 (write the 40-line script as `survivor_check.py`), similarity re-measure | A's reconciled files | E (paragraph 4.3), F |
| **D · Headline CIs** | `RESULTS.md` §8 (new), `headline_ci.json` | §3.5; verify `runs/scores/` fetch; report the three sentences | koran caches | E (4.4) |
| **E · Paper** | `paper/main.tex`, `paper/figures.py`, `paper/fig/*`, `paper/README.md` | §4.1 immediately; then §4.2, §4.3, §4.4 as B, C, F, D report; page count; §4.5 | reports from B, C, D, F | submission |
| **F · Positive control** | `monitor_samegen_*.json`, `RESULTS.md` §9 (new) | §3.6 dry-run, then the batch (needs the key and the coordinator's go, since it spends), poll, report AUROC beside S | C's headline S | E (4.3) |
| **G · Release and docs sync** | `LICENSE` (exists), `release_split.py` outputs, `notes/07`, `README.md`, `experiments/README.md`, `GATE-S-RUNBOOK.md`, `notes/02` | §5 build and check after C decides `--keep`; then sync the stale status lines listed in `notes/06` §3.4 (the Sonnet arm "not run", the runbook "never ran", notes/02 "$0 held allocation", the arm-1 model name, the refs.bib count) | C's `--keep` decision | E (release sentence) |

Merge order: A → (B, D, E-4.1 in parallel) → C → F → E-4.2/4.3/4.4 → G → E-4.5. Commit after
each worker's report. The coordinator alone edits `notes/06` and this file.

What the coordinator decides, not the workers: whether the stripped legs "hold" (§3.1 bands);
which S is the headline (default: `passes`, independent arm); `--keep first` or `best`; whether to
spend on F; whether to spend on a top-up (default no); the title (default: keep "What Survives the
Filter?"; change to "Authorship, Not Sabotage" only on a stable collapse with the positive control
in hand, and even then it can wait for camera-ready).

---

## 7. Where things are likely to break, and what to do

| Symptom | Cause | Fix |
|---|---|---|
| `gate_s_baseline.py` ≠ 0.8714 | wrong shards, wrong pool, or a changed `evaluate()` | diff `gate_s_pool.py` counts against §1.1; `git diff 205c9a2 -- experiments/apps/gate_s_eval.py` should show only the bootstrap addition |
| `strip_recheck.py` unstripped column ≠ REPRODUCED.md | reimplementation drift (vectoriser, split seed, pair construction) | compare against `matched.py`/`transfer.py` line for line; the intended difference is only `strip_comments` and the seed loop |
| samegen `REFUSING: the two classes do not share a generator` | `--bd` and `gen_` files from different models, or a `model` field missing | check the `model` field in both files; this guard is deliberate |
| samegen `only N pairs - below the 50-pair floor` on `usable` | expected before the retry merge | merge and verify the rounds (§1.2); do not lower `--min-pairs` to get a number |
| `KeyError` on a jsonl field | a file produced by an older script version | the field lists in §1.2 are from the current producers; re-run the producer if cheap (`verify_backdoor.py` is minutes) |
| `headline_ci.py` cannot find `koran_samples.pkl` | `bow.py` not run | `python fetch_inputs.py && python bow.py` |
| `headline_ci.py` fails fetching `runs/scores/` | GitHub rate limit or path change | `--scores-dir` pointing at a manual clone of `anik-jha/challenger-panels/runs/scores` |
| `monitor_samegen.py` rejects a `custom_id` | a `problem_id` with characters outside `[A-Za-z0-9_-]` | ids are numeric strings today; if not, report rather than patch |
| `release_split.py --check` flags upstream code | a released string equals a human APPS solution or stored backdoor | it should never happen for generated code; if it does, that generation is a memorised upstream solution and must be dropped and reported |
| pair similarity numbers differ from 0.924 / 0.415 / 0.469 | expected: `autojunk=False` now | record the new values; the old ones were measured with the heuristic on |
| page count still over 4 after the cut plan | the float page | check that only F3 remains as a float in the body; move its caption caveats to a footnote only as a last resort |

---

## 8. What "done" looks like on Sep 12

- `RESULTS.md` has §6 to §9 with every new number and its command.
- `main.tex` compiles from a fresh checkout at exactly four content pages, `\TODO` a no-op, all
  six first-paragraph citations present, every headline number carrying an interval, the
  authorship paragraph on stripped numbers, the Gate S paragraph stating whichever outcome landed
  in the pre-registered words, the disclosures in Limitations, the release sentence true.
- The supplementary zip built by `release_split.py` passes `--check` and is attached.
- The branch is pushed; the README status box says what shipped.
- Title: "What Survives the Filter? Trivial Baselines on Stored Honest/Attack Pairs in AI-Control
  Monitoring" unless the coordinator's rule in §6 fires.
