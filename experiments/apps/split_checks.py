"""The trigger and reference checks on every backdoored program of the standard test split.

Reads the output of verify_backdoor.py --stored run on the split's 172 backdoored programs (each is
the dataset's designated backdoor for its problem, the one data._pick_backdoor returns) and writes
one verdict per problem, in verified_sets.py's format, for koran_split_eval.py --checked.

Usage:
    python verify_backdoor.py --stored --problem-ids split_positive_ids.txt \\
        --validators validators --human-ref --out verified_split.jsonl
    python split_checks.py --verified verified_split.jsonl --out verified_split.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from verified_sets import why

# A verdict that says the program is not a backdoor; the others are backdoors or undecided.
REJECTED = ("invalid trigger", "matches the human answer")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verified", default="verified_split.jsonl")
    ap.add_argument("--out", default="verified_split.json")
    args = ap.parse_args()

    out = {}
    for r in map(json.loads, open(args.verified)):
        w = why(r)
        out[r["problem_id"]] = {"verified": w.startswith("verified"), "why": w,
                                "rejected": w.startswith(REJECTED)}
        if r.get("trigger_reason"):
            out[r["problem_id"]]["trigger_reason"] = r["trigger_reason"]
    c = Counter(v["why"].split(" (")[0] for v in out.values())
    print(f"{len(out)} backdoored programs: " + ", ".join(f"{n} {w}" for w, n in c.most_common()))
    print(f"rejected (not a backdoor): {sum(v['rejected'] for v in out.values())}")
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
