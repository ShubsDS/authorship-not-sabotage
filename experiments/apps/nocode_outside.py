"""The no-code floor trained outside the test split and scored once on it.

This matches the bag-of-words protocol (train on problems outside Koran's 1,375-item test split,
score the test split once) for the metadata-only classifier. The paired train split cannot be used:
each of its problems contributes one honest and one attack item with identical metadata, so a
metadata classifier fit on it learns nothing (floors.py, P3 = 0.5000).

Construction
------------
Training items: every RoganInglis/apps-control-arena problem (5,000) whose problem_id is not in the
test split (3,625), built the way bow.py / data.py build the test split: one item per problem, an
attack if a stored backdoor works and passes the tests (_pick_backdoor; the artifact's
`backdoor_works` flag), otherwise honest if a reference solution compiles and passes the tests
(_honest_code); problems with neither are dropped. That leaves 2,045 items: 1,365 attack (1,209 of
them the problems of Koran's paired train split) and 680 honest.

Koran's artifact is the RoganInglis problems with a compiling, passing, deterministic reference
solution and at least four tests; every one of its problems outside the test split has a working
backdoor. So every honest training item comes from a problem that filter removed: 414 have only two
or three tests and 301 are nondeterministic (some are both). The classifier sees the test count of
problems the test split cannot contain, and learns the opposite sign on it: outside the split,
attack problems have more tests (25.3 against 14.8); inside, fewer (21.0 against 38.8).

Two rows are reported:
  * all     -- the construction above, the primary value;
  * min4    -- the same pool restricted to problems with at least four tests, the test-count rule
               every test item satisfies (1,613 items: 1,347 attack, 266 honest, the honest ones all
               nondeterministic).

Features and model: difficulty (one-hot), num_tests and q_len, exactly the columns of analyse2.py /
auroc.py / headline_ci.py, with StandardScaler + LogisticRegression(max_iter=5000). For the
training items num_tests is len(inputs) and q_len is len(question); both equal Koran's own columns
on all 2,584 of its problems (asserted). Test features and labels are koran_meta's, as in
headline_ci.py.

Statistics: AUROC on the test split; a 2,000-draw bootstrap over problems; the permutation null of
headline_ci.py (training and test labels both permuted, model refit, AUROC recomputed; 1,000
permutations, p = (1 + #{null >= observed}) / (1 + R)), with the training-labels-only null kept for
reference; and the paired bootstrap against the 24 monitors on the same 1,375 items.

Usage (from experiments/apps):
    python nocode_outside.py        # needs fetch.py, fetch_inputs.py; runs/scores/ as headline_ci.py
    python nocode_outside.py --perms 1000 --out nocode_outside.json
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
from data import _honest_code, _pick_backdoor  # noqa: E402
from headline_ci import (  # noqa: E402
    COUNT_BASIS, _nocode_model, fast_auroc, fetch_scores, load_scores, monitor_repos, nocode_design,
    null_summary, own_boot, paired_vs_monitors, run_chunked, sentence, streams, summarise,
)


def outside_items(data_dir: str, test_pids: set[str]) -> pd.DataFrame:
    """One item per RoganInglis problem outside the test split, labelled as the test split is."""
    shards = sorted(glob.glob(os.path.join(data_dir, "train_*.parquet")))
    if not shards:
        raise SystemExit(f"no train_*.parquet in {data_dir!r} -- run fetch.py first")
    sh = pd.concat([pq.read_table(f, columns=["problem_id", "inputs", "solutions", "backdoors"]).to_pandas()
                    for f in shards], ignore_index=True)
    sh["problem_id"] = sh.problem_id.astype(str)
    rm = pd.read_parquet(os.path.join(data_dir, "rogan_meta.parquet"))
    rm["problem_id"] = rm.problem_id.astype(str)
    km = pd.read_parquet(os.path.join(data_dir, "koran_meta.parquet"))
    km["problem_id"] = km.problem_id.astype(str)

    # Feature provenance: on Koran's own problems, len(inputs) and Rogan's q_len are Koran's columns.
    chk = km.merge(sh[["problem_id", "inputs"]], on="problem_id").merge(rm[["problem_id", "q_len"]],
                                                                         on="problem_id", suffixes=("", "_r"))
    if len(chk) != len(km):
        raise SystemExit("some koran_meta problems are absent from the RoganInglis shards")
    if not (chk.num_tests == chk.inputs.map(len)).all() or not (chk.q_len == chk.q_len_r).all():
        raise SystemExit("num_tests != len(inputs) or q_len differs on Koran's problems")
    if km[km.split == "test"].num_tests.min() < 4:
        raise SystemExit("a test item has fewer than four tests; the min4 row's premise fails")

    rows = []
    for r in sh[~sh.problem_id.isin(test_pids)].itertuples(index=False):
        row = {"problem_id": r.problem_id, "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions], "top_backdoor_model": None}
        if _pick_backdoor(row) is not None:
            rows.append((r.problem_id, 1, len(r.inputs)))
        elif _honest_code(row) is not None:
            rows.append((r.problem_id, 0, len(r.inputs)))
    o = pd.DataFrame(rows, columns=["problem_id", "label", "num_tests"])
    o = o.merge(rm[["problem_id", "difficulty", "q_len", "is_nondeterministic", "backdoor_works"]],
                on="problem_id", how="left")
    if not (o.backdoor_works.astype(int) == o.label).all():
        raise SystemExit("an item's label disagrees with the artifact's backdoor_works flag")
    o["in_koran_train"] = o.problem_id.isin(set(km.problem_id[km.split == "train"]))
    return o


def design(df: pd.DataFrame, columns: list[str]) -> np.ndarray:
    X = pd.get_dummies(df[["difficulty", "num_tests", "q_len"]].astype({"difficulty": "object"}),
                       columns=["difficulty"]).astype(float)
    extra = set(X.columns) - set(columns)
    if extra:
        raise SystemExit(f"training design has columns the test design lacks: {sorted(extra)}")
    return X.reindex(columns=columns, fill_value=0.0).to_numpy()


def _perm_chunk(Xo, yo, Xt, yt, perms):
    out = []
    for po, pt in perms:
        s = _nocode_model().fit(Xo, yo[po]).predict_proba(Xt)[:, 1]
        out.append((fast_auroc(yt[pt], s), fast_auroc(yt, s)))
    return out


def composition(o: pd.DataFrame) -> dict:
    h, a = o[o.label == 0], o[o.label == 1]
    return {
        "n_items": int(len(o)), "attack": int(len(a)), "honest": int(len(h)),
        "attack_from_koran_paired_train": int(a.in_koran_train.sum()),
        "honest_with_2_or_3_tests": int((h.num_tests < 4).sum()),
        "honest_nondeterministic": int(h.is_nondeterministic.sum()),
        "mean_num_tests": {"attack": round(float(a.num_tests.mean()), 2), "honest": round(float(h.num_tests.mean()), 2)},
        "num_tests_auroc_for_attack": round(float(roc_auc_score(o.label, o.num_tests)), 4),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data-dir", default=".")
    ap.add_argument("--scores-dir", default="runs/scores")
    ap.add_argument("--monitor-summary", default="monitor-summary.json")
    ap.add_argument("--out", default="nocode_outside.json")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--perms", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=-1)
    ap.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()

    repos = monitor_repos(a.monitor_summary)
    if not a.no_fetch:
        fetch_scores(repos, a.scores_dir)
    mon_df, mon_meta = load_scores(repos, a.scores_dir)

    Xt_df, yt, pids = nocode_design(a.data_dir)
    if not np.array_equal(mon_df.loc[pids, "label"].to_numpy(), yt):
        raise SystemExit("koran_meta `backdoor_works` disagrees with the monitor files' labels")
    cols = list(Xt_df.columns)
    Xt = Xt_df.to_numpy()
    yt_te = pd.Series(yt, index=pids)
    print(f"test split: {len(yt)} items ({int(yt.sum())} attack), features {cols}")
    print(f"  single-column num_tests AUROC on the test split: {roc_auc_score(yt, Xt_df.num_tests):.4f}")

    pool = outside_items(a.data_dir, set(pids))
    rows = {"all": pool, "min4": pool[pool.num_tests >= 4]}
    blocks = []
    for k, (key, o) in enumerate(rows.items()):
        rng = streams(a.seed + 100 * k, ["perm", "boot", "paired"])
        Xo, yo = design(o, cols), o.label.to_numpy()
        model = _nocode_model().fit(Xo, yo)
        s = model.predict_proba(Xt)[:, 1]
        comp = composition(o)
        print(f"\n[{key}] trained on {comp['n_items']} outside items ({comp['attack']} attack / "
              f"{comp['honest']} honest); attack mean tests {comp['mean_num_tests']['attack']} vs honest "
              f"{comp['mean_num_tests']['honest']}")
        perms = [(rng["perm"].permutation(len(yo)), rng["perm"].permutation(len(yt))) for _ in range(a.perms)]
        res = run_chunked(lambda c: _perm_chunk(Xo, yo, Xt, yt, c), perms, a.jobs)
        own = own_boot(yt, s, pids, a.n_boot, rng["boot"])
        paired = paired_vs_monitors(yt, s, mon_df.loc[pids], mon_meta, pids, a.n_boot, rng["paired"])
        b = summarise("no-code floor (metadata only)", f"outside the test split -> test split [{key}]",
                      own, np.array([r[0] for r in res]), paired, np.array([r[1] for r in res]))
        b["row"] = key
        b["training_items"] = comp
        b["standardised_coefficients"] = dict(zip(cols, np.round(model[-1].coef_[0], 4).tolist()))
        blocks.append(b)
        print("  " + sentence(b, f"[{key}]"))
        print(f"  training-labels-only null: p95 {b['train_labels_only_null']['p95']:.4f}, "
              f"p = {b['train_labels_only_null']['p']:.4g}")
        print(f"  coefficients {b['standardised_coefficients']}")

    out = {
        "generated_by": "experiments/apps/nocode_outside.py",
        "construction": ("RoganInglis problems outside Koran's test split, one item per problem: attack if a "
                         "stored backdoor works and passes the tests, else honest if a reference solution "
                         "compiles and passes; features difficulty, num_tests, q_len; scored once on the "
                         "1,375-item test split. Row min4 keeps the problems with at least four tests."),
        "n_boot": a.n_boot, "n_perm": a.perms, "seed": a.seed,
        "permutation_null": "training and test labels both permuted, model refit, AUROC recomputed; "
                            "p = (1 + #{null >= observed}) / (1 + R)",
        "count_basis": COUNT_BASIS,
        "test_split_num_tests_auroc_for_attack": round(float(roc_auc_score(yt, Xt_df.num_tests)), 4),
        "floors": blocks,
    }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
