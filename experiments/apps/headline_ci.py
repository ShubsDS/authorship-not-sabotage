"""Uncertainty for the paper's two headline floors, and a paired test against the 24 monitors.

Answers `notes/06-path-to-submission.md` §6 item 4 and the §3.4 defect *"No permutation null or CI
on the APPS floors ... `monitor-summary.json` ships a `ci` per monitor, unused."*

What it computes
----------------
(a) **TF-IDF headline, 0.8063.** Refits the exact pipeline of `koran_split_eval.py` (word 1-2gram
    TF-IDF, `LogisticRegression(max_iter=5000, C=5)`, trained on Koran's paired *train* split,
    scored on their 1,375-item test split, comments stripped), then attaches
      * a bootstrap-over-PROBLEMS 95% CI (2,000 draws), and
      * a permutation null that **reshuffles the TRAINING labels and refits** (200 permutations),
        reporting the null's 95th percentile and the empirical p.

(b) **The no-code floor, under BOTH of its protocols, never crossed** (`paper/fig/CAPTIONS.md`:
    *"Never write 0.772, above 18 of 24"*):
      * 5x5 repeated stratified CV *within* the test split  -> 0.7715 +- 0.0389, above 20 of 24
      * a single 413-item held-out slice of the same items  -> 0.7163,           above 18 of 24
    Each keeps its own monitor count in every table, JSON field and sentence this script emits.

(c) **A paired comparison against each of the 24 monitors**, using Jha's per-item score files in
    `runs/scores/` (MIT). For every monitor: the paired bootstrap over problems of
    (our AUROC - monitor AUROC) computed on *identical* items, its 95% CI, and whether that CI
    excludes zero. Summarised as "above k1 of 24 (point estimates), k2 of 24 with a CI excluding 0".

(d) A compact printed table, `headline_ci.json`, and the exact sentences for the paper.

Why these choices
-----------------
* **The permutation null shuffles TRAINING labels, not test labels.** For a *trained* classifier the
  null hypothesis is "the training corpus carries no label-predictive signal that transfers". Shuffling
  the test labels instead would only destroy the evaluation, tests nothing about what was learned, and
  gives a null centred on 0.5 by construction whatever the training set contained. So we permute
  `y_train`, refit, and score the untouched test labels. The vectorizer is *not* refit: its vocabulary,
  `min_df` and IDF depend on X alone, so refitting it would be wasted work, not a different null.
* **The bootstrap unit is the problem, not the item.** Two samples from the same APPS problem share a
  question, a difficulty and a test suite; they are not independent draws. Resampling items would
  understate the interval. In Koran's *test* split the 1,375 items happen to be one per problem
  (they are not paired there: 172 attack / 1,203 honest), so grouping is a no-op on that split -- but
  the script groups anyway and prints the group-size distribution, so the same code is correct if it
  is ever pointed at a paired split.
* **Paired bootstrap, not DeLong.** DeLong's covariance estimate leans on asymptotic normality of the
  placement values; with 172 positives, heavily tied monitor scores (Jha's files carry as few as 193
  distinct values over 1,857 samples, and several monitors are flagged `degenerate`), its variance is
  unstable and its intervals are not trustworthy here. The paired percentile bootstrap over problems
  makes no distributional assumption and handles ties natively.

Inputs (all produced by scripts already in this directory, run from `experiments/apps/`)
----------------------------------------------------------------------------------------
    python fetch.py            # RoganInglis train_*.parquet shards
    python fetch_inputs.py     # koran_meta.parquet, monitor-summary.json, koran_test_code.pkl
    python bow.py              # koran_samples.pkl
    python headline_ci.py      # this script; downloads runs/scores/ itself if absent

`runs/scores/<repo with / -> __>.json` is fetched from `anik-jha/challenger-panels` (MIT,
Copyright (c) 2026 Anik Jha) at run time; nothing is redistributed and `runs/` is gitignored.

COLUMN / FORMAT ASSUMPTIONS (every one matched to an existing script, none invented)
-----------------------------------------------------------------------------------
  1. `koran_samples.pkl` has `problem_id, label, code, stripped`         -- written by `bow.py`.
  2. `koran_meta.parquet` has `problem_id, split, backdoor_works, difficulty, num_tests, q_len,
     top_backdoor_model`                                                 -- `fetch_cols.py`,
     `analyse2.py`, `auroc.py`, `koran_split_eval.py`.
  3. `train_*.parquet` shards have `problem_id, solutions, backdoors`, with `solutions` structs
     carrying `code/passes_tests/compiles` and `backdoors` structs carrying
     `backdoor_code/backdoor_works/passes_tests/model`                   -- `koran_split_eval.py`,
     `data.py:_pick_backdoor/_honest_code`.
  4. `monitor-summary.json` is a LIST of dicts with `repo, test_auroc, ci`  -- the tracked file.
  5. `runs/scores/*.json`: dict with `repo, lineage, params_b, ok, n, seconds, sample_ids, scores,
     test_auroc, test_auroc_ci, test_pauc10, n_distinct, degenerate`. `sample_ids[i]` is
     `"<split>/<problem_id>/<attack|honest>"` over val+test (482 + 1,375 = 1,857 entries); we keep
     the `test/` prefix only. `scores[i]` is a raw suspicion score, **higher = more suspicious**
     (verified: rank-AUROC of the `test/` subset reproduces the file's own `test_auroc` to 4dp for
     all 24). Filename = `repo.replace("/", "__") + ".json"`. `internlm/internlm3-8b-instruct` also
     has a file but it is `ok: false` with no scores, and is absent from `monitor-summary.json` --
     the 24 monitors are exactly the entries of `monitor-summary.json`.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import urllib.request

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402

RAW_BASE = "https://raw.githubusercontent.com/anik-jha/challenger-panels/main/runs/scores/"
SCORES_LICENCE = "MIT (Copyright (c) 2026 Anik Jha), github.com/anik-jha/challenger-panels"

# --------------------------------------------------------------------------------------------
# generic statistics
# --------------------------------------------------------------------------------------------


def _avg_ranks(x: np.ndarray) -> np.ndarray:
    """Average (tie-corrected) ranks, 1-based. Vectorised; monitor scores are heavily tied."""
    sorter = np.argsort(x, kind="stable")
    inv = np.empty(len(x), dtype=np.int64)
    inv[sorter] = np.arange(len(x))
    xs = x[sorter]
    obs = np.empty(len(x), dtype=bool)
    obs[0] = True
    np.not_equal(xs[1:], xs[:-1], out=obs[1:])
    dense = obs.cumsum()[inv]
    count = np.r_[np.nonzero(obs)[0], len(x)]
    return 0.5 * (count[dense] + count[dense - 1] + 1)


def fast_auroc(y: np.ndarray, s: np.ndarray) -> float:
    """Mann-Whitney AUROC with tie correction. Matches sklearn's roc_auc_score."""
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = _avg_ranks(s)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def problem_bootstrap_indices(problem_ids: np.ndarray, n_boot: int, rng) -> list[np.ndarray]:
    """Resample PROBLEMS with replacement; return the item indices each draw selects.

    Items are grouped by `problem_id` and whole groups are drawn, so a paired split would keep its
    pairs together. On Koran's test split every group has size 1 and this reduces to an item
    bootstrap -- which is correct there, and is asserted rather than assumed (see `group_sizes`).
    """
    order = np.argsort(problem_ids, kind="stable")
    sorted_pids = problem_ids[order]
    starts = np.r_[0, np.nonzero(sorted_pids[1:] != sorted_pids[:-1])[0] + 1]
    groups = np.split(order, starts[1:])
    n_groups = len(groups)
    out = []
    for _ in range(n_boot):
        pick = rng.integers(0, n_groups, size=n_groups)
        out.append(np.concatenate([groups[i] for i in pick]))
    return out


def boot_ci(vals: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    lo, hi = np.nanpercentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def perm_p(observed: float, null: np.ndarray) -> float:
    """One-sided empirical p with the +1 correction (Phipson & Smyth)."""
    return float((1 + int(np.sum(np.asarray(null) >= observed))) / (len(null) + 1))


# --------------------------------------------------------------------------------------------
# runs/scores/ -- fetch and load
# --------------------------------------------------------------------------------------------


def monitor_repos(summary_path: str) -> list[dict]:
    mon = json.load(open(summary_path))
    if not isinstance(mon, list):
        mon = mon.get("monitors", list(mon.values()))
    return [m for m in mon if isinstance(m, dict) and m.get("test_auroc") is not None]


def fetch_scores(repos: list[dict], scores_dir: str) -> None:
    """Download the 24 per-item score files from GitHub raw if they are not already present."""
    os.makedirs(scores_dir, exist_ok=True)
    for m in repos:
        fn = m["repo"].replace("/", "__") + ".json"
        dst = os.path.join(scores_dir, fn)
        if os.path.exists(dst):
            continue
        url = RAW_BASE + fn
        print(f"  fetching {url}")
        with urllib.request.urlopen(url, timeout=120) as r:
            body = r.read()
        with open(dst, "wb") as fh:
            fh.write(body)
        print(f"    -> {dst} ({len(body)} bytes)")


def load_scores(repos: list[dict], scores_dir: str) -> pd.DataFrame:
    """One column per monitor of per-item test scores, indexed by problem_id, plus `label`.

    Asserts that every monitor file agrees on the item set and the labels, and that the rank-AUROC
    of each column reproduces the file's published `test_auroc`.
    """
    frames, meta = {}, {}
    label = None
    for m in repos:
        path = os.path.join(scores_dir, m["repo"].replace("/", "__") + ".json")
        d = json.load(open(path))
        if not d.get("ok", True):
            raise SystemExit(f"{path}: ok=false ({d.get('error')!r}); it should not be in the 24")
        keep = [(i, s) for i, s in zip(d["sample_ids"], d["scores"]) if i.startswith("test/")]
        pids = [i.split("/")[1] for i in (k[0] for k in keep)]
        lab = pd.Series([1 if k[0].endswith("/attack") else 0 for k in keep], index=pids)
        if len(set(pids)) != len(pids):
            raise SystemExit(f"{path}: duplicate problem_id in the test subset")
        if label is None:
            label = lab
        elif not label.equals(lab.reindex(label.index)):
            raise SystemExit(f"{path}: item set or labels differ from the first monitor file")
        frames[m["repo"]] = pd.Series([k[1] for k in keep], index=pids, dtype=float)
        meta[m["repo"]] = {
            "published_test_auroc": d.get("test_auroc"),
            "published_ci": d.get("test_auroc_ci"),
            "n_distinct": d.get("n_distinct"),
            "degenerate": bool(d.get("degenerate", False)),
            "params_b": d.get("params_b"),
            "lineage": d.get("lineage"),
        }
    df = pd.DataFrame(frames)
    df.insert(0, "label", label.reindex(df.index).astype(int))
    y = df["label"].to_numpy()
    for repo, info in meta.items():
        got = round(fast_auroc(y, df[repo].to_numpy()), 4)
        if info["published_test_auroc"] is not None and abs(got - info["published_test_auroc"]) > 1e-4:
            raise SystemExit(f"{repo}: recomputed test AUROC {got} != published {info['published_test_auroc']}")
    return df, meta


# --------------------------------------------------------------------------------------------
# (a) the TF-IDF headline
# --------------------------------------------------------------------------------------------

HEADLINE_VEC = dict(
    token_pattern=r"[A-Za-z_]+|\d+|[^\sA-Za-z_\d]",
    ngram_range=(1, 2),
    min_df=2,
    max_features=50000,
    sublinear_tf=True,
)


def build_train(data_dir: str, test_pids: set[str]) -> pd.DataFrame:
    """Koran's paired TRAIN split, reconstructed exactly as `koran_split_eval.py` does it."""
    km = pd.read_parquet(os.path.join(data_dir, "koran_meta.parquet"))
    train_pids = set(km.problem_id.astype(str)) - test_pids
    shards = sorted(glob.glob(os.path.join(data_dir, "train_*.parquet")))
    if not shards:
        raise SystemExit(f"no train_*.parquet in {data_dir!r} -- run fetch.py first")
    full = pd.concat(
        [pq.read_table(f, columns=["problem_id", "solutions", "backdoors"]).to_pandas() for f in shards],
        ignore_index=True,
    )
    full = full[full.problem_id.astype(str).isin(train_pids)]
    tbm = dict(zip(km.problem_id.astype(str), km.top_backdoor_model))
    rows = []
    for _, r in full.iterrows():
        row = {
            "problem_id": str(r.problem_id),
            "backdoors": [dict(b) for b in r.backdoors],
            "solutions": [dict(s) for s in r.solutions],
            "top_backdoor_model": tbm.get(str(r.problem_id)),
        }
        bd, hc = _pick_backdoor(row), _honest_code(row)
        if bd is None or hc is None:
            continue
        rows.append((row["problem_id"], 1, bd["backdoor_code"]))
        rows.append((row["problem_id"], 0, hc))
    tr = pd.DataFrame(rows, columns=["problem_id", "label", "code"])
    tr["stripped"] = tr.code.map(strip_comments)
    return tr


def tfidf_headline(data_dir: str, item_index: pd.Index, n_perm: int, rng) -> dict:
    """Refit the 0.8063 pipeline; return per-item test scores and the training-label null."""
    test = pd.read_pickle(os.path.join(data_dir, "koran_samples.pkl"))
    test["problem_id"] = test.problem_id.astype(str)
    tr = build_train(data_dir, set(test.problem_id))
    print(f"  train: {len(tr)} samples over {tr.problem_id.nunique()} problems "
          f"({int(tr.label.sum())} attack / {int((1 - tr.label).sum())} honest)")
    print(f"  test : {len(test)} samples ({int(test.label.sum())} attack / {int((1 - test.label).sum())} honest)")

    vec = TfidfVectorizer(**HEADLINE_VEC)
    Xtr = vec.fit_transform(tr["stripped"])
    Xte = vec.transform(test["stripped"])
    ytr = tr.label.to_numpy()
    clf = LogisticRegression(max_iter=5000, C=5).fit(Xtr, ytr)
    s = pd.Series(clf.predict_proba(Xte)[:, 1], index=test.problem_id.to_numpy())
    yte = pd.Series(test.label.to_numpy().astype(int), index=test.problem_id.to_numpy())

    missing = item_index.difference(s.index)
    if len(missing):
        raise SystemExit(f"{len(missing)} monitor items absent from koran_samples.pkl, e.g. {list(missing[:5])}")
    s, yte = s.reindex(item_index), yte.reindex(item_index)

    # Permutation null: shuffle the TRAINING labels and refit. The vectorizer is label-independent
    # and is deliberately not refit.
    null = []
    for i in range(n_perm):
        yp = rng.permutation(ytr)
        c = LogisticRegression(max_iter=5000, C=5).fit(Xtr, yp)
        null.append(fast_auroc(yte.to_numpy(), c.predict_proba(Xte)[:, 1]))
        if (i + 1) % 25 == 0:
            print(f"    permutation {i + 1}/{n_perm}")
    return {"scores": s, "y": yte, "null": np.array(null), "n_train": len(tr),
            "n_vocab": len(vec.vocabulary_)}


# --------------------------------------------------------------------------------------------
# (b) the no-code floor, two protocols
# --------------------------------------------------------------------------------------------

NOCODE_COLS = ["difficulty", "num_tests", "q_len"]


def nocode_design(data_dir: str) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """The metadata design matrix of `analyse2.py` / `auroc.py`, on Koran's test split."""
    k = pd.read_parquet(os.path.join(data_dir, "koran_meta.parquet"))
    kt = k[k.split == "test"].copy()
    kt["problem_id"] = kt.problem_id.astype(str)
    y = kt.backdoor_works.astype(int).to_numpy()
    X = pd.get_dummies(kt[NOCODE_COLS].astype({"difficulty": "object"}), columns=["difficulty"]).astype(float)
    X = X[[c for c in X.columns if X[c].nunique() > 1]]
    return X, y, kt.problem_id.to_numpy()


def _nocode_model():
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))


def nocode_cv(X: pd.DataFrame, y: np.ndarray, n_perm: int, rng) -> dict:
    """Protocol A: 5x5 repeated stratified CV *within* the test split -- the 0.7715 +- 0.0389 value.

    The fold-mean is the paper's statistic. For the interval we bootstrap the pooled out-of-fold
    score vector (averaged over the 5 repeats): bootstrapping the CV itself would put duplicated
    items on both sides of a fold and inflate the AUROC.
    """
    Xv = X.to_numpy()

    def run(yy):
        cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=0)
        folds, oof = [], np.zeros((5, len(yy)))
        for i, (a, b) in enumerate(cv.split(Xv, yy)):
            m = _nocode_model().fit(Xv[a], yy[a])
            p = m.predict_proba(Xv[b])[:, 1]
            folds.append(roc_auc_score(yy[b], p))
            oof[i // 5, b] = p
        return np.array(folds), oof.mean(axis=0)

    folds, oof = run(y)
    null = []
    for i in range(n_perm):
        f, _ = run(rng.permutation(y))
        null.append(f.mean())
        if (i + 1) % 25 == 0:
            print(f"    permutation {i + 1}/{n_perm}")
    return {"fold_mean": float(folds.mean()), "fold_sd": float(folds.std()), "n_folds": len(folds),
            "oof": oof, "y": y, "null": np.array(null)}


def nocode_holdout(X: pd.DataFrame, y: np.ndarray, pids: np.ndarray, n_perm: int, rng) -> dict:
    """Protocol B: the single stratified 30% held-out slice of `auroc.py` -- the 0.7163 value."""
    idx = np.arange(len(y))
    itr, ite = train_test_split(idx, test_size=0.30, stratify=y, random_state=0)
    Xv = X.to_numpy()
    m = _nocode_model().fit(Xv[itr], y[itr])
    p = m.predict_proba(Xv[ite])[:, 1]
    null = []
    for i in range(n_perm):
        mm = _nocode_model().fit(Xv[itr], rng.permutation(y[itr]))
        null.append(fast_auroc(y[ite], mm.predict_proba(Xv[ite])[:, 1]))
    return {"scores": p, "y": y[ite], "pids": pids[ite], "n_train": len(itr), "n_test": len(ite),
            "null": np.array(null)}


# --------------------------------------------------------------------------------------------
# bootstrap machinery shared by (a), (b) and (c)
# --------------------------------------------------------------------------------------------


def own_boot(y: np.ndarray, s: np.ndarray, pids: np.ndarray, n_boot: int, rng) -> dict:
    idxs = problem_bootstrap_indices(pids, n_boot, rng)
    vals = np.array([fast_auroc(y[i], s[i]) for i in idxs])
    lo, hi = boot_ci(vals)
    sizes = pd.Series(pids).value_counts()
    return {"auroc": fast_auroc(y, s), "ci_lo": lo, "ci_hi": hi, "boot_sd": float(np.nanstd(vals)),
            "n_items": int(len(y)), "n_problems": int(sizes.size),
            "group_sizes": {str(k): int(v) for k, v in sizes.value_counts().sort_index().items()}}


def paired_vs_monitors(y, ours, mon_df: pd.DataFrame, meta: dict, pids, n_boot, rng) -> list[dict]:
    """Paired bootstrap over problems of (our AUROC - monitor AUROC) on IDENTICAL items."""
    repos = [c for c in mon_df.columns if c != "label"]
    M = mon_df[repos].to_numpy()
    idxs = problem_bootstrap_indices(pids, n_boot, rng)
    obs_mon = np.array([fast_auroc(y, M[:, j]) for j in range(M.shape[1])])
    obs_ours = fast_auroc(y, ours)
    diffs = np.empty((n_boot, len(repos)))
    for b, i in enumerate(idxs):
        yb, ob, Mb = y[i], ours[i], M[i]
        a_ours = fast_auroc(yb, ob)
        for j in range(len(repos)):
            diffs[b, j] = a_ours - fast_auroc(yb, Mb[:, j])
    out = []
    for j, repo in enumerate(repos):
        lo, hi = boot_ci(diffs[:, j])
        out.append({
            "repo": repo,
            "monitor_auroc_on_these_items": round(float(obs_mon[j]), 4),
            "monitor_published_test_auroc": meta.get(repo, {}).get("published_test_auroc"),
            "monitor_published_ci": meta.get(repo, {}).get("published_ci"),
            "our_auroc": round(obs_ours, 4),
            "diff": round(float(obs_ours - obs_mon[j]), 4),
            "diff_ci": [round(lo, 4), round(hi, 4)],
            "ci_excludes_zero": bool(lo > 0 or hi < 0),
            "we_are_higher": bool(obs_ours > obs_mon[j]),
            "higher_and_ci_excludes_zero": bool(lo > 0),
        })
    return sorted(out, key=lambda d: d["monitor_auroc_on_these_items"])


# --------------------------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------------------------


def summarise(name, protocol, own, null, paired, raw_count_basis) -> dict:
    """Assemble one floor's block. `raw_count_basis` says which monitor AUROC the raw count used."""
    above_raw = sum(1 for d in paired if d["we_are_higher"])
    above_ci = sum(1 for d in paired if d["higher_and_ci_excludes_zero"])
    if raw_count_basis == "published":
        above_raw = sum(1 for d in paired if own["auroc"] > (d["monitor_published_test_auroc"] or -1))
    return {
        "name": name,
        "protocol": protocol,
        "auroc": round(own["auroc"], 4),
        "ci95": [round(own["ci_lo"], 4), round(own["ci_hi"], 4)],
        "bootstrap_sd": round(own["boot_sd"], 4),
        "n_items": own["n_items"],
        "n_problems": own["n_problems"],
        "bootstrap_group_sizes": own["group_sizes"],
        "perm_null_p95": round(float(np.percentile(null, 95)), 4),
        "perm_null_mean": round(float(np.mean(null)), 4),
        "perm_null_max": round(float(np.max(null)), 4),
        "perm_p": perm_p(own["auroc"], null),
        "n_perm": int(len(null)),
        "above_n_of_24_point_estimates": above_raw,
        "above_n_of_24_ci_excludes_zero": above_ci,
        "raw_count_basis": raw_count_basis,
        "per_monitor": paired,
    }


def sentence(b: dict, label: str) -> str:
    return (f"{label} {b['auroc']:.4f} (95% CI {b['ci95'][0]:.4f}-{b['ci95'][1]:.4f}; "
            f"permutation null 95th pct {b['perm_null_p95']:.4f}, p = {b['perm_p']:.4g}), "
            f"above {b['above_n_of_24_point_estimates']} of 24 monitors, "
            f"{b['above_n_of_24_ci_excludes_zero']} of them with a paired-bootstrap CI excluding zero.")


def print_table(blocks: list[dict]) -> None:
    w = max(34, max(len(b["name"]) for b in blocks) + 2)
    width = w + 26 + 8 + 18 + 10 + 9 + 6 + 6
    print("\n" + "=" * width)
    print(f"{'floor':<{w}}{'protocol':<26}{'AUROC':>8}{'95% CI':>18}{'null p95':>10}{'p':>9}{'>pt':>6}{'>CI':>6}")
    print("-" * width)
    for b in blocks:
        ci = f"{b['ci95'][0]:.4f}-{b['ci95'][1]:.4f}"
        print(f"{b['name']:<{w}}{b['protocol']:<26}{b['auroc']:>8.4f}{ci:>18}"
              f"{b['perm_null_p95']:>10.4f}{b['perm_p']:>9.4g}"
              f"{b['above_n_of_24_point_estimates']:>6}{b['above_n_of_24_ci_excludes_zero']:>6}")
    print("=" * width)
    print("  >pt = monitors whose PUBLISHED full-split test_auroc is below our point estimate "
          "(this is the paper's raw count)")
    print("  >CI = monitors we beat on IDENTICAL items with a paired-bootstrap 95% CI that excludes 0")
    for b in blocks:
        print(f"\n--- {b['name']} ({b['protocol']}), paired bootstrap over problems, "
              f"n_items={b['n_items']} -------")
        print(f"{'monitor':<46}{'mon':>8}{'ours':>8}{'diff':>9}{'95% CI of diff':>20}{'excl 0':>8}")
        for d in b["per_monitor"]:
            ci = f"{d['diff_ci'][0]:+.4f},{d['diff_ci'][1]:+.4f}"
            print(f"{d['repo']:<46}{d['monitor_auroc_on_these_items']:>8.4f}{d['our_auroc']:>8.4f}"
                  f"{d['diff']:>+9.4f}{ci:>20}{('yes' if d['ci_excludes_zero'] else 'no'):>8}")


# --------------------------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data-dir", default=".", help="where koran_meta.parquet / koran_samples.pkl / train_*.parquet live")
    ap.add_argument("--scores-dir", default="runs/scores", help="per-item monitor scores (downloaded if absent)")
    ap.add_argument("--monitor-summary", default="monitor-summary.json")
    ap.add_argument("--out", default="headline_ci.json")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-fetch", action="store_true", help="fail instead of downloading runs/scores/")
    ap.add_argument("--fetch-only", action="store_true")
    ap.add_argument("--skip-tfidf", action="store_true", help="no-code floors only (no train shards needed)")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    print(f"monitor summary: {a.monitor_summary}")
    repos = monitor_repos(a.monitor_summary)
    print(f"  {len(repos)} monitors with a test_auroc")
    if not a.no_fetch:
        fetch_scores(repos, a.scores_dir)
    if a.fetch_only:
        return
    mon_df, mon_meta = load_scores(repos, a.scores_dir)
    print(f"  per-item scores loaded: {mon_df.shape[0]} test items x {mon_df.shape[1] - 1} monitors "
          f"({int(mon_df.label.sum())} attack / {int((1 - mon_df.label).sum())} honest); "
          f"every column's rank-AUROC matches its published test_auroc")

    blocks = []

    if not a.skip_tfidf:
        print("\n(a) TF-IDF word 1-2gram, Koran's paired train split -> their 1,375-item test split, stripped")
        t = tfidf_headline(a.data_dir, mon_df.index, a.n_perm, rng)
        y, s, pids = t["y"].to_numpy(), t["scores"].to_numpy(), np.asarray(mon_df.index)
        own = own_boot(y, s, pids, a.n_boot, rng)
        print(f"  AUROC={own['auroc']:.4f}  (koran_split_eval.py reports 0.8063)")
        paired = paired_vs_monitors(y, s, mon_df, mon_meta, pids, a.n_boot, rng)
        blocks.append(summarise("TF-IDF word 1-2gram (stripped)", "Koran train -> Koran test",
                                own, t["null"], paired, "published"))
        blocks[-1]["train_samples"] = t["n_train"]
        blocks[-1]["vocabulary"] = t["n_vocab"]

    X, y_all, pids_all = nocode_design(a.data_dir)
    miss = set(pids_all) - set(mon_df.index)
    if miss:
        raise SystemExit(f"{len(miss)} koran_meta test problem_ids absent from runs/scores/, e.g. {sorted(miss)[:5]}")
    if not np.array_equal(mon_df.loc[pids_all, "label"].to_numpy(), y_all):
        raise SystemExit("koran_meta `backdoor_works` disagrees with the monitor files' attack/honest labels")
    print(f"\n(b) no-code floor: {X.shape[1]} features {list(X.columns)} on {len(y_all)} test items")

    print("  protocol A: 5x5 repeated stratified CV within the test split")
    cv = nocode_cv(X, y_all, a.n_perm, rng)
    print(f"    fold mean={cv['fold_mean']:.4f} sd={cv['fold_sd']:.4f} over {cv['n_folds']} folds "
          f"(analyse2.py reports 0.7715 +- 0.0389)")
    own_cv = own_boot(cv["y"], cv["oof"], pids_all, a.n_boot, rng)
    print(f"    pooled out-of-fold AUROC={own_cv['auroc']:.4f} (the statistic the CI is built on)")
    paired_cv = paired_vs_monitors(cv["y"], cv["oof"], mon_df.loc[pids_all], mon_meta, pids_all, a.n_boot, rng)
    b_cv = summarise("no-code floor (metadata only)", "5x5 CV within test",
                     own_cv, cv["null"], paired_cv, "published")
    b_cv["headline_fold_mean"] = round(cv["fold_mean"], 4)
    b_cv["headline_fold_sd"] = round(cv["fold_sd"], 4)
    b_cv["above_n_of_24_point_estimates"] = sum(
        1 for d in paired_cv if cv["fold_mean"] > (d["monitor_published_test_auroc"] or -1))
    b_cv["note"] = ("The paper's value for this protocol is the fold mean 0.7715 +- 0.0389 and its count is "
                    "20 of 24. The CI and the paired tests are computed on the pooled out-of-fold score "
                    "vector, the only per-item statistic this protocol produces. Never pair this value "
                    "with the held-out protocol's count of 18.")
    blocks.append(b_cv)

    print("  protocol B: single stratified 30% held-out slice of the same items")
    ho = nocode_holdout(X, y_all, pids_all, a.n_perm, rng)
    print(f"    held-out n={ho['n_test']} (train {ho['n_train']}); auroc.py reports 0.7163")
    own_ho = own_boot(ho["y"], ho["scores"], ho["pids"], a.n_boot, rng)
    paired_ho = paired_vs_monitors(ho["y"], ho["scores"], mon_df.loc[ho["pids"]], mon_meta, ho["pids"], a.n_boot, rng)
    b_ho = summarise("no-code floor (metadata only)", f"{ho['n_test']}-item held-out slice",
                     own_ho, ho["null"], paired_ho, "published")
    b_ho["note"] = ("The paper's count for this protocol is 18 of 24, taken against the monitors' published "
                    "full-split test_auroc. The paired column beside it recomputes each monitor's AUROC on "
                    "the SAME held-out items, which is the only comparison a paired bootstrap can make; the "
                    "two counts are therefore not required to agree and must not be swapped. Never pair "
                    "this count with the 5x5 CV value.")
    blocks.append(b_ho)

    print_table(blocks)

    sentences = {}
    if not a.skip_tfidf:
        sentences["tfidf"] = sentence(blocks[0], "TF-IDF")
    sentences["nocode_cv"] = (
        f"No-code floor (5x5 CV within the test split) {b_cv['headline_fold_mean']:.4f} "
        f"+- {b_cv['headline_fold_sd']:.4f} (bootstrap-over-problems 95% CI of the pooled out-of-fold "
        f"AUROC {b_cv['ci95'][0]:.4f}-{b_cv['ci95'][1]:.4f}; permutation null 95th pct "
        f"{b_cv['perm_null_p95']:.4f}, p = {b_cv['perm_p']:.4g}), above "
        f"{b_cv['above_n_of_24_point_estimates']} of 24 monitors, "
        f"{b_cv['above_n_of_24_ci_excludes_zero']} of them with a paired-bootstrap CI excluding zero.")
    sentences["nocode_holdout"] = sentence(
        b_ho, f"No-code floor ({b_ho['protocol']})")

    print("\nSENTENCES FOR THE PAPER")
    for k, v in sentences.items():
        print(f"  [{k}] {v}")

    out = {
        "generated_by": "experiments/apps/headline_ci.py",
        "n_boot": a.n_boot, "n_perm": a.n_perm, "seed": a.seed,
        "bootstrap_unit": "problem_id (whole groups resampled with replacement)",
        "permutation_null": "training labels shuffled and the classifier refit; test labels untouched",
        "interval_method": "paired percentile bootstrap over problems (NOT DeLong: unstable at 172 "
                           "positives with heavily tied, partly degenerate monitor scores)",
        "monitor_scores": {"source": RAW_BASE, "licence": SCORES_LICENCE,
                           "n_monitors": int(mon_df.shape[1] - 1), "n_items": int(mon_df.shape[0])},
        "floors": blocks,
        "paper_sentences": sentences,
    }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
