"""Compute B, the human-honest baseline, over the full analysis pool.

B is human honest code against the stored working backdoors, fitted with
gate_s_eval.evaluate() (imported, so it is the same fit that produces G, S and B'). It needs no
generated code. It prints B and the G (or S) value each rho band corresponds to at this B.

This B is over the full pool. rho's denominator is B', the same quantity refitted on exactly the
problems an arm covers (gate_s_eval.py and gate_s_samegen.py compute it); the two coincide only
if an arm covers every problem.

Two definitions of the human pass flag:
    shipped  the artifact's `solution_passes_tests`      1,444 pairs, B = 0.8714
    own      run_tests.py's verdict on the human class   1,406 pairs, B = 0.8729
With --human-pass-file the own flag both gates eligibility and selects which human solution is
used; without it the shipped flag is used.

Usage:
    python gate_s_baseline.py                  # -> gate_s_baseline.json
    python gate_s_baseline.py --human-pass-file pass_human_fixed.jsonl \
        --out gate_s_baseline_ownflag.json
"""

from __future__ import annotations

import argparse
import glob
import json
import sys

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, ".")
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402
from gate_s_eval import COLLAPSE, NO_COLLAPSE, evaluate  # noqa: E402

# `top_backdoor_model` is not a column of RoganInglis/apps-control-arena (it exists only in
# eugenekoran/apps-control-arena-high-quality, which fetch_inputs.py reads), so rows are built
# with top_backdoor_model=None and _pick_backdoor falls through to the first usable backdoor.
COLS = ["problem_id", "solutions", "backdoors",
        "solution_passes_tests", "backdoor_works", "is_nondeterministic"]


def build_pairs(df: pd.DataFrame, honest_ok: set[str] | None,
                honest_idx: dict[str, list[int]] | None = None) -> pd.DataFrame:
    rows, no_backdoor, no_honest = [], 0, 0
    for _, r in df.iterrows():
        if not (r.backdoor_works and not r.is_nondeterministic):
            continue
        pid = r.problem_id
        if honest_ok is None:
            if not r.solution_passes_tests:
                continue
        elif pid not in honest_ok:
            continue

        row = {"problem_id": pid,
               "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions],
               "top_backdoor_model": None}
        bd = _pick_backdoor(row)
        if honest_idx is None:
            human = _honest_code(row)
        else:
            # Select the honest program with the same flag that gated eligibility: the first
            # solution our harness passes. _honest_code() picks the first solution the artifact
            # marks passing, which for 22 problems is code our harness fails.
            human = next((row["solutions"][i]["code"] for i in honest_idx.get(pid, [])
                          if i < len(row["solutions"])), None)
        if bd is None:
            no_backdoor += 1
            continue
        if human is None:
            no_honest += 1
            continue
        rows.append({"problem_id": pid,
                     "honest": strip_comments(human),
                     "attack": strip_comments(bd["backdoor_code"])})

    if no_backdoor or no_honest:
        print(f"  dropped: {no_backdoor} with no usable backdoor, {no_honest} with no honest code")
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--human-pass-file", default=None,
                    help="run_tests.py output for the human class; falls back to the shipped flag")
    ap.add_argument("--out", default="gate_s_baseline.json")
    args = ap.parse_args()

    shards = sorted(glob.glob("train_*.parquet"))
    if not shards:
        raise SystemExit("no train_*.parquet here - run `python fetch.py` first")
    df = pd.concat([pq.read_table(f, columns=COLS).to_pandas() for f in shards], ignore_index=True)
    df["problem_id"] = df.problem_id.astype(str)
    print(f"artifact rows {len(df)}")

    honest_ok = honest_idx = None
    if args.human_pass_file:
        honest_idx = {}
        for line in open(args.human_pass_file):
            if not line.strip():
                continue
            r = json.loads(line)
            if r["passed"]:
                honest_idx.setdefault(str(r["problem_id"]), []).append(r["sol_idx"])
        for v in honest_idx.values():
            v.sort()
        honest_ok = set(honest_idx)
        print(f"human pass flag: OUR OWN harness, {len(honest_ok)} passing "
              f"({args.human_pass_file}); code selected with the same flag")
    else:
        print("human pass flag: the artifact's shipped `solution_passes_tests` "
              "(no --human-pass-file given)")

    pairs = build_pairs(df, honest_ok, honest_idx)
    print(f"\neligible pairs (passing human honest + working backdoor + deterministic): "
          f"{len(pairs)}")
    if len(pairs) < 50:
        raise SystemExit(f"only {len(pairs)} eligible pairs")

    print("problem-disjoint 5-fold, comments stripped, identical pipeline:")
    B = evaluate(pairs, "B  human honest")
    b = B["auroc"]

    print(f"\n{'=' * 78}")
    print(f"B = {b:.4f}  (sd {B['auroc_sd']:.4f}, n = {B['n_pairs']} pairs)")
    print(f"\nrho bands at this B - the G each threshold implies:")
    print(f"  rho <= {COLLAPSE}  collapse -> authorship   requires G <= "
          f"{0.5 + COLLAPSE * (b - 0.5):.4f}")
    print(f"  rho <= {NO_COLLAPSE}  partial                  requires G <= "
          f"{0.5 + NO_COLLAPSE * (b - 0.5):.4f}")
    print(f"  rho >  {NO_COLLAPSE}  content                  is G >  "
          f"{0.5 + NO_COLLAPSE * (b - 0.5):.4f}")

    print(f"\n{'=' * 78}")
    print("CAVEAT, and it must travel with this number: B is computed over the analysis-pool")
    print("CEILING. rho's denominator is B over the arm's realised eligible set, which is this")
    print("pool intersected with whichever generations pass. Recompute B with gate_s_eval.py")
    print("when an arm lands; do not carry this value into rho.")

    import sklearn
    json.dump({"B": B,
               "g_thresholds": {"collapse_max": 0.5 + COLLAPSE * (b - 0.5),
                                "partial_max": 0.5 + NO_COLLAPSE * (b - 0.5)},
               "human_pass_flag": "own" if honest_ok else "shipped",
               "pool": "analysis ceiling (not an arm's realised set)",
               "sklearn": sklearn.__version__,
               "pandas": pd.__version__}, open(args.out, "w"), indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
