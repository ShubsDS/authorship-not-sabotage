"""Build the Gate S problem pool and print the numbers that go in the paper.

Two pools, and conflating them is the mistake this script exists to prevent:

  generation pool  problems with a passing human solution (3,420). We generate for all of these,
                   because we cannot know in advance which generations will pass.
  analysis pool    the subset that can actually form a Gate S pair: a working backdoor to serve as
                   the attack class, and deterministic tests so exact-match scoring is meaningful.

The analysis pool is much smaller than 3,420, and the paper has to say so rather than let a reader
infer the larger number. See `../GATE-S-RUNBOOK.md` §2.
"""

from __future__ import annotations

import glob

import pandas as pd
import pyarrow.parquet as pq

COLS = ["problem_id", "question", "inputs", "outputs", "difficulty",
        "solutions", "backdoors", "solution_passes_tests", "backdoor_works",
        "is_nondeterministic", "nondeterminism_category"]


def main() -> None:
    shards = sorted(glob.glob("train_*.parquet"))
    if not shards:
        raise SystemExit("no train_*.parquet here — run `python fetch.py` first")
    df = pd.concat([pq.read_table(f, columns=COLS).to_pandas() for f in shards],
                   ignore_index=True)
    df["problem_id"] = df.problem_id.astype(str)
    df["n_tests"] = df.inputs.map(len)
    df["n_solutions"] = df.solutions.map(len)

    n = len(df)
    gen_pool = df[df.solution_passes_tests]
    det = df[~df.is_nondeterministic]
    workable = df[df.backdoor_works]

    print(f"artifact rows                                  {n}")
    print(f"  solution_passes_tests                        {len(gen_pool)}   <- GENERATION POOL")
    print(f"  backdoor_works                               {len(workable)}")
    print(f"  is_nondeterministic                          {int(df.is_nondeterministic.sum())}")
    print(df.nondeterminism_category.value_counts().to_string())

    analysis = df[df.solution_passes_tests & df.backdoor_works & ~df.is_nondeterministic]
    print(f"\npassing solution AND working backdoor          "
          f"{int((df.solution_passes_tests & df.backdoor_works).sum())}")
    print(f"  ... AND deterministic                        {len(analysis)}   <- ANALYSIS CEILING")
    print("\nThis is the ceiling before the generator's own pass rate. The realised n per arm is"
          "\nthis number times that arm's pass rate — report it, do not imply 3,420.")

    print("\nanalysis pool by difficulty:")
    print(analysis.difficulty.value_counts().to_string())
    print(f"\ntest cases in the analysis pool: median {int(analysis.n_tests.median())}, "
          f"mean {analysis.n_tests.mean():.1f}, max {int(analysis.n_tests.max())}")

    out = gen_pool[["problem_id", "question", "difficulty", "n_tests", "n_solutions",
                    "backdoor_works", "is_nondeterministic"]].copy()
    out["in_analysis_pool"] = out.problem_id.isin(set(analysis.problem_id))
    out.to_parquet("gate_s_pool.parquet", index=False)
    print(f"\nwrote gate_s_pool.parquet  {out.shape}  "
          f"({int(out.in_analysis_pool.sum())} flagged in_analysis_pool)")


if __name__ == "__main__":
    main()
