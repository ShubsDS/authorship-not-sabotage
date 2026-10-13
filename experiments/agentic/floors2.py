"""Within-task permutation nulls for the five ControlArena agentic settings (Figure F2).

The statistic is the one matched.py reports in its within-task column and Figure F2 plots: group
the transcripts of a setting by main task (extra_info.main_task_description); within every task
that has both classes, count the (attack, honest) pairs in which the attack transcript has more
characters, ties counting one half; sum those counts and the pair totals over tasks; AUROC = sum /
total, reported direction-free as max(a, 1 - a). This is a Mann-Whitney AUROC pooled over tasks,
weighted by each task's pair count.

Null: permute the labels within each task group, so every task keeps its class counts and so its
pair total, and recompute the same folded statistic; R = 1,000 permutations (--perms). Reported per
setting: the null's mean and 95th percentile, and p = (1 + #{null >= observed}) / (1 + R). Because
the statistic is folded, its null sits above 0.5.

The earlier nulls in this script were the mean of three label permutations of a different
statistic (a gradient-boosted model on six transcript counts under pooled stratified 5-fold CV).
They are replaced here; nothing in the paper uses that pooled model.

Usage:
    python floors2.py            # needs ca_<setting>.parquet from fetch_scan.py -> within_task_null.json
    python floors2.py --perms 1000 --seed 0 --out within_task_null.json
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from scipy.stats import rankdata

SETTINGS = ["bash", "shade", "iac", "rogue_eval", "agentdojo"]

# matched.py's within-task column, which the observed statistic must reproduce.
EXPECTED = {"bash": 0.5044, "shade": 0.6022, "iac": 0.7041, "rogue_eval": 0.6158, "agentdojo": 0.8020}


def load(setting: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Character count, label and main task per transcript, built exactly as matched.py builds them."""
    df = pd.read_parquet(f"ca_{setting}.parquet", columns=["transcript", "ground_truth", "extra_info"])
    ei = pd.json_normalize(df["extra_info"])
    y = df["ground_truth"].astype(int).to_numpy()
    x = df["transcript"].fillna("").astype(str).str.len().to_numpy()
    task = ei["main_task_description"].fillna("").to_numpy()
    return x, y, task


class WithinTask:
    """Pre-ranked task groups, so each permutation only re-sums ranks."""

    def __init__(self, x: np.ndarray, y: np.ndarray, task: np.ndarray):
        self.groups = []                       # (average ranks within the task, labels)
        pairs = 0
        for t in pd.unique(task):
            idx = np.flatnonzero(task == t)
            yy = y[idx]
            n1 = int(yy.sum())
            n0 = len(yy) - n1
            if n1 == 0 or n0 == 0:
                continue
            self.groups.append((rankdata(x[idx]), yy, n1))
            pairs += n1 * n0
        self.pairs = pairs
        self.n_tasks = len(self.groups)

    def auroc(self, labels: list[np.ndarray] | None = None) -> float:
        """Unfolded pooled AUROC; `labels` replaces each group's labels (same order as self.groups)."""
        wins = 0.0
        for k, (r, yy, n1) in enumerate(self.groups):
            lab = yy if labels is None else labels[k]
            wins += r[lab == 1].sum() - n1 * (n1 + 1) / 2.0
        return wins / self.pairs

    def null(self, n_perm: int, rng) -> np.ndarray:
        out = np.empty(n_perm)
        for i in range(n_perm):
            a = self.auroc([rng.permutation(yy) for _, yy, _ in self.groups])
            out[i] = max(a, 1 - a)
        return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--perms", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="within_task_null.json")
    a = ap.parse_args()

    rows = []
    print(f"{'setting':11s} {'n':>5} {'tasks':>6} {'within-task':>12} {'null mean':>10} {'null p95':>9} {'p':>8}")
    for k, s in enumerate(SETTINGS):
        x, y, task = load(s)
        w = WithinTask(x, y, task)
        raw = w.auroc()
        obs = max(raw, 1 - raw)
        if abs(round(obs, 4) - EXPECTED[s]) > 1e-4:
            raise SystemExit(f"{s}: within-task AUROC {obs:.4f} does not reproduce matched.py's {EXPECTED[s]}")
        null = w.null(a.perms, np.random.default_rng([a.seed, k]))
        p = float((1 + int(np.sum(null >= obs))) / (1 + len(null)))
        row = {"setting": s, "n": int(len(y)), "n_attack": int(y.sum()), "tasks_used": w.n_tasks,
               "pairs": int(w.pairs), "within_task_auroc": round(obs, 4),
               "direction": "attack longer" if raw >= 0.5 else "attack shorter",
               "null_mean": round(float(null.mean()), 4), "null_p95": round(float(np.percentile(null, 95)), 4),
               "null_max": round(float(null.max()), 4), "perm_p": round(p, 4), "n_perm": int(len(null))}
        rows.append(row)
        print(f"{s:11s} {row['n']:5d} {w.n_tasks:6d} {obs:12.4f} {row['null_mean']:10.4f} "
              f"{row['null_p95']:9.4f} {p:8.4f}")

    out = {
        "generated_by": "experiments/agentic/floors2.py",
        "statistic": "within-task Mann-Whitney AUROC on character count, pooled over tasks by pair count, "
                     "direction-free max(a, 1 - a) (matched.py's within-task column)",
        "null": "labels permuted within each main-task group; same folded statistic recomputed",
        "p_value": "(1 + #{null >= observed}) / (1 + R)",
        "n_perm": a.perms, "seed": a.seed,
        "settings": rows,
    }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
