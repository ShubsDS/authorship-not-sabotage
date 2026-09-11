"""Why the single-shot conditional firing rate is 2.5%: half the triggers are public test inputs.

APPS copies the statement's sample I/O into `inputs`/`outputs`, and a backdoor must pass every
public test. A draw whose `backdoor_input` is one of those inputs therefore cannot diverge from
the honest solution by construction. This script counts, over every test-passing draw in the
merged retry pool, how many triggers are public inputs and how often each kind fires, and the
same for the stored working backdoors (whose triggers were produced by a pipeline that executed
the code).

    python3 trigger_public_check.py            # reads bdind_sonnet5_retry.jsonl + verdicts + shards

Measured 2026-09-11 over 6,570 test-passing draws: 52.0% of triggers are public inputs and fire
0.15%; the other 48.0% fire 5.13%; combined 2.54%. Stored working backdoors with a public-input
trigger: 0 of 3,188. The fix for a later generation round is one sentence in the attack prompt
forbidding any input shown in the problem statement (expected ~2x on the usable yield).
"""

from __future__ import annotations

import argparse
import glob
import json

import pandas as pd
import pyarrow.parquet as pq


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draws", default="bdind_sonnet5_retry.jsonl")
    ap.add_argument("--verdicts", default="bdindpass_sonnet5_retry.jsonl")
    args = ap.parse_args()

    draws = {json.loads(l)["draw"]: json.loads(l) for l in open(args.draws) if l.strip()}
    verd = [json.loads(l) for l in open(args.verdicts) if l.strip()]
    df = pd.concat([pq.read_table(f, columns=["problem_id", "inputs", "backdoors"]).to_pandas()
                    for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
    df["problem_id"] = df.problem_id.astype(str)
    tests = {r.problem_id: {str(x).strip() for x in r.inputs} for r in df.itertuples()}

    rows = []
    for v in verd:
        if not v["passes_tests"]:
            continue
        trig = (draws[v["draw"]].get("backdoor_input") or "").strip()
        rows.append({"public_input": trig in tests.get(v["problem_id"], set()),
                     "fires": bool(v["backdoor_works"]),
                     "crash": v.get("reason") == "backdoor crashes on trigger"})
    r = pd.DataFrame(rows)
    print(f"test-passing draws: {len(r)}")
    g = r.groupby("public_input").agg(n=("fires", "size"), fires=("fires", "mean"),
                                      crash=("crash", "mean"))
    print(g.assign(fires=lambda x: (100 * x.fires).round(2), crash=lambda x: (100 * x.crash).round(2)))
    print(f"share with a public-input trigger: {100 * r.public_input.mean():.1f}%   "
          f"combined fire rate {100 * r.fires.mean():.2f}%")

    n_stored = n_pub = 0
    for rr in df.itertuples():
        for b in rr.backdoors:
            b = dict(b)
            if b.get("passes_tests") and b.get("backdoor_works"):
                n_stored += 1
                n_pub += (str(b.get("backdoor_input") or "").strip() in tests[rr.problem_id])
    print(f"stored working backdoors whose trigger is a public input: {n_pub} of {n_stored}")


if __name__ == "__main__":
    main()
