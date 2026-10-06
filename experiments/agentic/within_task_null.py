"""Like-for-like permutation null for the within-task character-count AUROC (appendix figure).

matched.py reports, per setting, a within-task Mann-Whitney AUROC on transcript character count,
pooled over tasks weighted by pair count and reported direction-free, max(a, 1 - a). This script
computes the null distribution of exactly that statistic: labels are shuffled within each task
(so every task keeps its own class balance) and the statistic is recomputed, including the
direction-free fold, which puts the null mean above 0.5 when tasks are small.

Usage:
    python within_task_null.py --perms 1000 --out within_task_null.json
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

SETTINGS = ["bash", "shade", "iac", "rogue_eval", "agentdojo"]


def within_task(x: np.ndarray, y: np.ndarray, groups: list[np.ndarray]) -> float:
    num = den = 0.0
    for idx in groups:
        a, b = x[idx][y[idx] == 1], x[idx][y[idx] == 0]
        if len(a) == 0 or len(b) == 0:
            continue
        num += (a[:, None] > b[None, :]).sum() + 0.5 * (a[:, None] == b[None, :]).sum()
        den += len(a) * len(b)
    wt = num / den
    return max(wt, 1 - wt)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=1000)
    ap.add_argument("--out", default="within_task_null.json")
    args = ap.parse_args()
    rng = np.random.default_rng(0)
    out = {}
    for s in SETTINGS:
        df = pd.read_parquet(f"ca_{s}.parquet", columns=["transcript", "ground_truth", "extra_info"])
        task = pd.json_normalize(df["extra_info"])["main_task_description"].fillna("").values
        y = df["ground_truth"].astype(int).values
        x = df["transcript"].fillna("").astype(str).str.len().values
        groups = [np.flatnonzero(task == t) for t in pd.unique(task)]
        observed = within_task(x, y, groups)
        null = []
        for _ in range(args.perms):
            yp = y.copy()
            for idx in groups:
                yp[idx] = rng.permutation(yp[idx])
            null.append(within_task(x, yp, groups))
        null = np.array(null)
        n_tasks = sum(1 for g in groups if 0 < y[g].sum() < len(g))
        out[s] = {"observed": observed, "null_mean": float(null.mean()),
                  "null_p95": float(np.percentile(null, 95)),
                  "p": float((1 + (null >= observed).sum()) / (1 + len(null))),
                  "n_tasks": n_tasks, "n_perms": args.perms}
        print(f"{s:11s} observed {observed:.4f}  null mean {null.mean():.4f}  "
              f"p95 {np.percentile(null, 95):.4f}  p {out[s]['p']:.4f}  tasks {n_tasks}")
    json.dump(out, open(args.out, "w"), indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
