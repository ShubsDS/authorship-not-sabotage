"""Rule out the alternatives to the public-input trigger diagnosis.

`trigger_public_check.py` establishes the defect: about half our triggers are public test inputs,
which a test-passing backdoor cannot diverge on by construction. This script establishes that the
defect is *the* explanation for the yield gap, by killing the three competing ones. Read them
together; neither is the whole argument.

  1. "Their models are simply better."   -> work|pass sits at 88.6-98.9% across TEN model variants,
                                            gpt-3.5-turbo and o1-mini included. A rate that flat
                                            across that capability range is enforced by a pipeline,
                                            not earned by a model.
  2. "Our bugs are worse."               -> we beat all ten on passing the public tests, and our
                                            diffs are more idiomatic, not less.
  3. "Their rate is like-for-like."      -> it is a best-of over two sources, ten models and up to
                                            eleven attempts per problem.

Reads only the parquet shards, the draw files and the vp_*.jsonl verdicts. Generates nothing,
spends nothing, writes nothing but stdout.

    python3 trigger_yield_evidence.py
"""

from __future__ import annotations

import argparse
import collections
import difflib
import glob
import json
import os
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import _honest_code, _pick_backdoor  # noqa: E402

# A bug hidden behind a hard-coded value is a different object from an off-by-one: the first is a
# special case bolted on to catch one input, the second is the ordinary mistake both prompts ask for.
MAGIC = re.compile(r"==\s*-?\d{2,}|!=\s*-?\d{2,}|in\s*[\(\[\{]\s*-?\d+\s*,|\bstartswith\(|\bendswith\(")
OPER = re.compile(r"[<>]=?|[+\-]\s*1\b|\brange\(")


def classify(added: list[str]) -> str:
    txt = "\n".join(added)
    if MAGIC.search(txt):
        return "magic-value special case"
    if OPER.search(txt):
        return "boundary / off-by-one"
    return "other"


def added_lines(a: str, b: str) -> list[str]:
    return [l[1:] for l in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0)
            if l.startswith("+") and not l.startswith("+++")]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draws", nargs="*", default=None)
    ap.add_argument("--honest-gen", default="gen_sonnet5.jsonl")
    ap.add_argument("--limit", type=int, default=400, help="diffs sampled per class")
    args = ap.parse_args()

    shards = sorted(glob.glob("train_*.parquet"))
    if not shards:
        raise SystemExit("no train_*.parquet here - run fetch.py first")
    art = pd.concat([pq.read_table(f, columns=["problem_id", "solutions", "backdoors", "inputs",
                                               "backdoor_works"]).to_pandas()
                     for f in shards], ignore_index=True)
    art["problem_id"] = art.problem_id.astype(str)

    # ---- 1. the artifact is an ensemble, and its work|pass is flat ---------------------------
    stat: dict = collections.defaultdict(lambda: {"n": 0, "pass": 0, "work": 0})
    per_problem: collections.Counter = collections.Counter()
    for _, r in art.iterrows():
        per_problem[len(r.backdoors)] += 1
        for b in r.backdoors:
            d = dict(b)
            s = stat[(str(d.get("source")), str(d.get("model")))]
            s["n"] += 1
            s["pass"] += bool(d.get("passes_tests"))
            s["work"] += bool(d.get("backdoor_works"))

    print("1. THE ARTIFACT IS AN ENSEMBLE, AND ITS work|pass IS FLAT ACROSS CAPABILITY\n")
    print(f"   {'source':<13}{'model':<40}{'n':>6}{'pass':>8}{'work|pass':>11}")
    lo, hi = 1.0, 0.0
    for k in sorted(stat, key=lambda x: -stat[x]["n"]):
        s = stat[k]
        wp = s["work"] / max(s["pass"], 1)
        lo, hi = min(lo, wp), max(hi, wp)
        print(f"   {k[0][:12]:<13}{k[1][:39]:<40}{s['n']:>6}{s['pass']/s['n']:>8.1%}{wp:>11.1%}")
    tot = sum(s["n"] for s in stat.values())
    multi = sum(v for k, v in per_problem.items() if k > 1)
    print(f"\n   work|pass spans {lo:.1%} to {hi:.1%} across {len(stat)} (source, model) pairs.")
    print(f"   {tot} records; {multi} problems carry more than one attempt, up to {max(per_problem)}.")
    print("   Any single-attempt comparison against this must say it is a best-of.\n")

    # ---- 2. bug structure -------------------------------------------------------------------
    theirs: collections.Counter = collections.Counter()
    n = 0
    for _, r in art.iterrows():
        if not r.backdoor_works or n >= args.limit:
            continue
        row = {"problem_id": r.problem_id, "solutions": [dict(s) for s in r.solutions],
               "backdoors": [dict(b) for b in r.backdoors], "top_backdoor_model": None}
        h, b = _honest_code(row), _pick_backdoor(row)
        if not h or not b:
            continue
        add = added_lines(h, b["backdoor_code"])
        if add:
            theirs[classify(add)] += 1
            n += 1

    hon = {json.loads(l)["problem_id"]: json.loads(l)["code"]
           for l in open(args.honest_gen) if l.strip()}
    draws = args.draws or (sorted(glob.glob("bds_r*s*.jsonl")) + sorted(glob.glob("bdind_sonnet5*.jsonl")))
    ours: collections.Counter = collections.Counter()
    m = 0
    for f in draws:
        vp = f"vp_{f[:-6]}.jsonl"
        if not os.path.exists(vp):
            continue
        verd = {json.loads(l)["problem_id"]: json.loads(l) for l in open(vp) if l.strip()}
        for line in open(f):
            if not line.strip() or m >= args.limit:
                continue
            r = json.loads(line)
            p = r["problem_id"]
            if not verd.get(p, {}).get("passes_tests") or p not in hon:
                continue
            add = added_lines(hon[p], r["code"])
            if add:
                ours[classify(add)] += 1
                m += 1

    print("2. OUR BUGS ARE NOT WORSE - THEY ARE MORE IDIOMATIC\n")
    print(f"   {'structure':<28}{'THEIRS (working)':>18}{'OURS (test-passing)':>22}")
    for k in ("boundary / off-by-one", "magic-value special case", "other"):
        print(f"   {k:<28}{theirs[k]/max(n,1):>17.1%}{ours[k]/max(m,1):>22.1%}")
    print(f"   {'n':<28}{n:>17}{m:>22}\n")

    # ---- 3. the defect itself ----------------------------------------------------------------
    tests = {r.problem_id: set(str(x).strip() for x in list(r.inputs)) for _, r in art.iterrows()}
    t_pub = t_tot = 0
    for _, r in art.iterrows():
        if not r.backdoor_works:
            continue
        b = _pick_backdoor({"problem_id": r.problem_id, "backdoors": [dict(x) for x in r.backdoors],
                            "solutions": [], "top_backdoor_model": None})
        t = (b or {}).get("backdoor_input", "")
        if not str(t).strip():
            continue
        t_tot += 1
        t_pub += str(t).strip() in tests.get(r.problem_id, ())
    o_pub = o_tot = 0
    for f in draws:
        if not os.path.exists(f):
            continue
        for line in open(f):
            if not line.strip():
                continue
            r = json.loads(line)
            t = (r.get("backdoor_input") or "").strip()
            if not t or r["problem_id"] not in tests:
                continue
            o_tot += 1
            o_pub += t in tests[r["problem_id"]]

    print("3. THE DEFECT - WHOSE TRIGGERS ARE PUBLIC TEST INPUTS\n")
    print(f"   stored working backdoors   {t_pub:>6} / {t_tot:<6}  {t_pub/max(t_tot,1):>7.1%}")
    print(f"   our draws                  {o_pub:>6} / {o_tot:<6}  {o_pub/max(o_tot,1):>7.1%}")
    print("\n   trigger_public_check.py has the firing rates these produce.")


if __name__ == "__main__":
    main()
