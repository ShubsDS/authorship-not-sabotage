"""Is a low S just near-copies? S re-fitted inside pair-similarity strata.

§9.1 demotes the edit arm to "a bound, not a verdict" because its honest/attack pairs are
near-copies (mean 0.928): when the two programs are almost the same text, a trivial classifier has
nothing to separate and a low S says nothing about authorship. The independent arm exists to avoid
that, and its Sonnet pairs sit in the stored benchmark's regime (0.659 against 0.606).

The Haiku 4.5 arm (§15) returns a much lower S, so the same question has to be asked of it before
the collapse can be read: its pairs are more self-similar than Sonnet's (0.724 vs 0.659, with 12.6%
above 0.95 against Sonnet's 3.3%), because a smaller model has less output diversity and, asked
twice for a program for the same problem, more often writes the same one.

This script re-fits S with `gate_s_eval.evaluate()` unchanged inside similarity strata, and on the
pairs BELOW a cut, so the collapse can be read off the subset where the two programs are genuinely
different texts. B' is re-fitted on the same subset each time, so rho stays like-for-like.

    python3 sim_stratified_s.py sg_haiku45_indep_passes.json --gen gen_haiku45.jsonl \
        --bd bdind_haiku45.jsonl --out sim_strata_haiku45.json
"""

from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402
from gate_s_eval import evaluate  # noqa: E402 - unchanged, as everywhere in the ledger

CUTS = [(0.0, 0.60), (0.60, 0.80), (0.80, 0.95), (0.95, 1.01)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sg_json")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--bd", required=True)
    ap.add_argument("--bprime-inert", action="store_true", default=True)
    ap.add_argument("--no-bprime-inert", dest="bprime_inert", action="store_false")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    ref = json.load(open(args.sg_json))
    pids = [str(p) for p in ref["problem_ids"]]
    code = lambda p: {json.loads(l)["problem_id"]: json.loads(l)["code"]
                      for l in open(p) if l.strip()}
    honest, attack = code(args.gen), code(args.bd)

    art = pd.concat([pq.read_table(f, columns=["problem_id", "solutions", "backdoors"]).to_pandas()
                     for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
    art["problem_id"] = art.problem_id.astype(str)
    stored = {}
    for _, r in art[art.problem_id.isin(set(pids))].iterrows():
        row = {"problem_id": r.problem_id, "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions], "top_backdoor_model": None}
        b = (([x for x in row["backdoors"] if x["passes_tests"]] or [None])[0]
             if args.bprime_inert else _pick_backdoor(row))
        h = _honest_code(row)
        if b and h:
            stored[r.problem_id] = {"problem_id": r.problem_id, "honest": strip_comments(h),
                                    "attack": strip_comments(b["backdoor_code"])}

    pair = {p: (strip_comments(honest[p]), strip_comments(attack[p])) for p in pids}
    sim = {p: difflib.SequenceMatcher(None, *pair[p], autojunk=False).ratio() for p in pids}

    def fit(keep: list, label: str) -> dict:
        same = pd.DataFrame([{"problem_id": p, "honest": pair[p][0], "attack": pair[p][1]}
                             for p in keep])
        S = evaluate(same, f"S  {label}")
        st = pd.DataFrame([stored[p] for p in keep if p in stored])
        B = evaluate(st, f"B' {label}") if len(st) >= 10 else None
        rec = {"n": len(keep), "S": S["auroc"], "S_ci95": S["auroc_ci95_boot"],
               "pairwise": S["pairwise_acc"],
               "mean_sim": float(np.mean([sim[p] for p in keep]))}
        if B:
            rec.update({"B_prime": B["auroc"], "B_prime_ci95": B["auroc_ci95_boot"],
                        "rho": (S["auroc"] - 0.5) / (B["auroc"] - 0.5)})
        return rec

    out = {"sg_json": args.sg_json, "n_all": len(pids),
           "ledger_S": ref["S"]["auroc"], "ledger_B_prime": ref["B_prime"]["auroc"],
           "strata": {}, "below_cut": {}}
    for lo, hi in CUTS:
        keep = [p for p in pids if lo <= sim[p] < hi]
        name = f"{lo:.2f}-{min(hi,1.0):.2f}"
        if len(keep) < 50:
            out["strata"][name] = {"n": len(keep), "refused": "below the 50-pair floor"}
            print(f"stratum {name}: n={len(keep)} - below the 50-pair floor, not fitted")
            continue
        out["strata"][name] = fit(keep, f"sim {name}")
    for cut in (0.95, 0.90, 0.80):
        keep = [p for p in pids if sim[p] < cut]
        if len(keep) >= 50:
            out["below_cut"][f"<{cut}"] = fit(keep, f"sim < {cut}")

    print(f"\n{'subset':14} {'n':>5} {'mean sim':>9} {'S':>8} {'95% CI':>17} {'B_prime':>8} {'rho':>7}")
    def show(name, r):
        if "refused" in r:
            print(f"{name:14} {r['n']:5d}   {r['refused']}")
            return
        ci = f"{r['S_ci95'][0]:.4f}-{r['S_ci95'][1]:.4f}"
        bp = f"{r['B_prime']:.4f}" if "B_prime" in r else "-"
        rho = f"{r['rho']:.3f}" if "rho" in r else "-"
        print(f"{name:14} {r['n']:5d} {r['mean_sim']:9.3f} {r['S']:8.4f} {ci:>17} {bp:>8} {rho:>7}")
    for k, v in out["strata"].items():
        show("sim " + k, v)
    for k, v in out["below_cut"].items():
        show("sim " + k, v)

    path = args.out or args.sg_json.replace(".json", "_simstrata.json")
    json.dump(out, open(path, "w"), indent=2, default=float)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
