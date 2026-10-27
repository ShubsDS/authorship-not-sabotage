"""Check that each problem's input validator accepts every stored test input of that problem.

A validator that rejects a real test input is too strict and would wrongly discard backdoors, so
every validator must pass this check before verify_backdoor.py uses it. Test inputs are read from
the artifact (`train_*.parquet`), or from `<problems_dir>/<id>/test_inputs.json` if given.

Usage:
    python check_validators.py --validators validators/ [--problems-dir problems/] [ids ...]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from input_validation import check_input, load_validator  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--validators", required=True)
    ap.add_argument("--problems-dir")
    ap.add_argument("ids", nargs="*", help="problem ids (default: every validator present)")
    args = ap.parse_args()

    ids = args.ids or sorted(os.path.basename(p)[:-3]
                             for p in glob.glob(os.path.join(args.validators, "*.py")))
    if args.problems_dir:
        tests = {p: json.load(open(os.path.join(args.problems_dir, p, "test_inputs.json")))
                 for p in ids}
    else:
        import pandas as pd
        import pyarrow.parquet as pq
        df = pd.concat([pq.read_table(f, columns=["problem_id", "inputs"]).to_pandas()
                        for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
        df["problem_id"] = df.problem_id.astype(str)
        tests = {r.problem_id: list(r.inputs) for _, r in df[df.problem_id.isin(ids)].iterrows()}

    bad = 0
    for p in ids:
        try:
            mod = load_validator(args.validators, p)
        except Exception as e:                  # noqa: BLE001 - report a broken module, go on
            print(f"{p}: FAILS TO LOAD: {type(e).__name__}: {e}")
            bad += 1
            continue
        if mod is None:
            print(f"{p}: no validator")
            bad += 1
            continue
        rejected = []
        for i, s in enumerate(tests.get(p, [])):
            r = check_input(args.validators, p, s)
            if r["valid"] is not True:
                rejected.append((i, r["reason"]))
        unchecked = getattr(mod, "UNCHECKED", [])
        status = "ok" if not rejected else f"REJECTS {len(rejected)} TEST INPUT(S)"
        print(f"{p}: {status}  ({len(tests.get(p, []))} tests"
              f"{'; unchecked: ' + '; '.join(unchecked) if unchecked else ''})")
        for i, reason in rejected[:3]:
            print(f"    test {i}: {reason}")
        bad += bool(rejected)
    print(f"\n{len(ids) - bad}/{len(ids)} validators accept all their test inputs")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
