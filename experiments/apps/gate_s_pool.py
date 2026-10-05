"""Build the problem pool and print the pool sizes reported in the paper.

There are two pools:

  generation pool  problems with a passing human solution (3,420). Honest solutions are generated
                   for these, since which generations will pass is not known in advance.
  analysis pool    the subset that can form an honest/attack pair: a working backdoor to serve as
                   the attack class, and deterministic tests so exact-match scoring is meaningful.

Prints 5,000 artifact rows, 3,420 in the generation pool, 1,582 with a passing solution and a
working backdoor, and 1,444 of those deterministic (the analysis pool). The realised n per arm is
the analysis pool times that arm's pass rate. Writes gate_s_pool.parquet with all 5,000 rows and
the pool flags.

Usage:
    python gate_s_pool.py
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

    # Write all 5,000 problems, not just the 3,420, and flag pool membership. The generation pool
    # uses the artifact's shipped `solution_passes_tests`, but our own harness's pass flag admits
    # problems the shipped flag rejects; keeping the superset lets either definition be applied at
    # analysis time without regenerating.
    out = df[["problem_id", "question", "difficulty", "n_tests", "n_solutions",
              "solution_passes_tests", "backdoor_works", "is_nondeterministic"]].copy()
    out["in_generation_pool"] = out.solution_passes_tests
    out["in_analysis_pool"] = out.problem_id.isin(set(analysis.problem_id))
    out.to_parquet("gate_s_pool.parquet", index=False)
    print(f"\nwrote gate_s_pool.parquet  {out.shape}  "
          f"({int(out.in_generation_pool.sum())} in_generation_pool, "
          f"{int(out.in_analysis_pool.sum())} in_analysis_pool)")
    print("Generation runs over ALL rows; the flags are applied at analysis time.")


if __name__ == "__main__":
    main()
