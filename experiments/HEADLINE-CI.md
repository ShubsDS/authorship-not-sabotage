# Uncertainty on the two headline floors — `apps/headline_ci.py`

Closes §6 item 4 of `notes/06-path-to-submission.md` and the §3.4 defect *"No permutation null or CI
on the APPS floors … `monitor-summary.json` ships a `ci` per monitor, unused."*

## What it computes

1. **The 0.8063 TF-IDF headline.** Refits `koran_split_eval.py`'s pipeline exactly (its word 1–2gram
   `TfidfVectorizer`; `LogisticRegression(max_iter=5000, C=5)`; Koran's paired *train* split → their
   1,375-item test split, stripped), plus a bootstrap-over-problems 95% CI (2,000 draws) and a
   permutation null (200 refits).
2. **The no-code floor under both protocols, never crossed:** 5×5 CV *within* the test split
   (0.7715 ± 0.0389, **20 of 24**) and the single 413-item held-out slice (0.7163, **18 of 24**).
   Each value keeps its own monitor count in every row, JSON field and sentence, per
   `paper/fig/CAPTIONS.md`.
3. **A paired comparison against each of the 24 monitors** from Jha's per-item score files: the
   paired bootstrap over problems of (our AUROC − monitor AUROC) on *identical* items, the
   difference, its 95% CI, and whether that CI excludes 0 — turning "above 20 of 24 point estimates"
   into "above k₁ of 24, k₂ with a CI excluding zero". Each monitor's published `ci` prints beside
   its row, consuming the shipped-but-unused field.
4. A table, `headline_ci.json`, and the sentences below.

## Three method choices

**The permutation null shuffles TRAINING labels and refits.** For a *trained* classifier the null is
"the training corpus carries no label-predictive signal that transfers". Shuffling the *test* labels
destroys the evaluation, not the hypothesis: it sits at 0.5 by construction whatever the training
corpus held. So `y_train` is permuted, the classifier refit, the untouched test labels scored. The
vectorizer is deliberately not refit — vocabulary, `min_df` and IDF depend on X alone.

**The bootstrap unit is the problem.** Two samples from one APPS problem share a question, a
difficulty and a test suite, so resampling items would understate the interval. Koran's *test* split
is one item per problem (172 attack / 1,203 honest, unpaired), so grouping is a no-op here — but the
script groups anyway, asserts it, and prints the group-size histogram, staying correct if ever
pointed at a paired split.

**Paired bootstrap, not DeLong.** DeLong leans on asymptotic normality of the placement values; with
172 positives and heavily tied scores (as few as 193 distinct values over 1,857 samples, several
monitors flagged `degenerate`) that variance is unstable. The paired percentile bootstrap assumes no
distribution and handles ties natively.

## The `runs/scores/` format

`github.com/anik-jha/challenger-panels`, **MIT** (Copyright (c) 2026 Anik Jha). One JSON per monitor,
named `repo.replace("/", "__") + ".json"`, fetched at run time from

```
https://raw.githubusercontent.com/anik-jha/challenger-panels/main/runs/scores/Qwen__Qwen3-8B.json
```

Keys: `repo, lineage, params_b, ok, n, seconds, sample_ids, scores, test_auroc, test_auroc_ci,
test_pauc10, n_distinct, degenerate`. `sample_ids[i]` is `"<split>/<problem_id>/<attack|honest>"`
over **val + test = 482 + 1,375 = 1,857** entries; only the `test/` prefix is kept. `scores[i]` is a
raw suspicion score, **higher = more suspicious**; the rank-AUROC of the `test/` subset reproduces
each file's own `test_auroc` to four decimals, asserted on every load.
`internlm/internlm3-8b-instruct` has a file too, but it is `ok: false` with no scores and absent
from `monitor-summary.json` — **the 24 monitors are exactly `monitor-summary.json`'s entries**.
Nothing is redistributed; `runs/` is gitignored.

## Running it

```bash
cd experiments/apps
python fetch.py && python fetch_inputs.py && python bow.py   # inputs, if not already present
python headline_ci.py                                         # downloads runs/scores/ itself
# --n-boot 2000 --n-perm 200 --seed 0 --skip-tfidf --no-fetch --out headline_ci.json
```

15–30 minutes, CPU only, no GPU, no API; the permutation refits dominate.

## Assumptions, and two protocol facts

Every column name comes from the script that writes it, and is checked at load: `koran_samples.pkl`
→ `problem_id, label, code, stripped` (`bow.py`); `koran_meta.parquet` → `problem_id, split,
backdoor_works, difficulty, num_tests, q_len, top_backdoor_model` (`fetch_cols.py`, `auroc.py`);
`train_*.parquet` → `problem_id, solutions, backdoors` with the structs `data.py` reads;
`monitor-summary.json` → a list of `repo, test_auroc, ci`.

The CV block's **CI and paired tests use the pooled out-of-fold score vector** (bootstrapping the CV
itself would put duplicated items on both sides of a fold and inflate it); its headline value stays
the fold mean. The held-out block's **raw** count uses the monitors' published full-split
`test_auroc` — the paper's 18 of 24 — while its **paired** column recomputes each monitor on the same
413 items, so the two counts need not agree and must never be swapped.

## The sentences

One shape, three fills — take each whole:

> **⟨FLOOR⟩ ⟨X⟩ (95% CI ⟨a⟩–⟨b⟩; permutation null 95th pct ⟨c⟩, p = ⟨p⟩), above ⟨k₁⟩ of 24 monitors,
> ⟨k₂⟩ of them with a paired-bootstrap CI excluding zero.**

⟨FLOOR⟩ is `TF-IDF`, `No-code floor (5×5 CV within the test split)` or
`No-code floor (413-item held-out slice)`. The CV fill alone carries `⟨X⟩ ± ⟨sd⟩` and names its
interval *"bootstrap-over-problems 95% CI of the pooled out-of-fold AUROC"*. The last two are
different protocols on the same items; their numbers do not interchange — the "never write 0.772
above 18" rule, enforced here in code. `headline_ci.py` prints all three filled in.
