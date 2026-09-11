"""The same-generator comparison: one model wrote BOTH classes, so authorship is held constant.

Every earlier arm compared two different generators and therefore could not separate the two
hypotheses:

    stored benchmark   human honest      vs  claude-3-7 backdoor   -> B, AUROC 0.871
    honest-only arm    Qwen honest       vs  claude-3-7 backdoor   -> G, AUROC 0.962, rho 1.23
    THIS               <model> honest    vs  <model> backdoor      -> S

B and G both carry an authorship gap; the honest-only arm merely swapped one for a larger one,
which is why its rho came out above 1. S has no authorship gap at all. Whatever a bag-of-words
classifier can still separate here is sabotage content, because that is the only thing left.

Reading S:

    S near 0.5      the stored 0.87 was authorship. Same-generator pairs are not separable by a
                    trivial baseline, and the benchmark measured who wrote the code.
    S clearly high  these backdoors carry real surface signal even from one author. The content
                    reading stands and the recommendation shifts to reporting the floor, not to
                    same-generator sampling alone.

    python gate_s_samegen.py --tag sonnet5
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402
from gate_s_eval import evaluate  # noqa: E402 - the identical fit used for B and G


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", required=True, help="e.g. sonnet5 or q3c30")
    ap.add_argument("--out", default=None)
    ap.add_argument("--bd", default=None,
                    help="backdoor jsonl; defaults to bd_<tag>.jsonl. Point at bdind_<tag>.jsonl "
                         "to evaluate the independent arm against the same honest class.")
    ap.add_argument("--bdpass", default=None,
                    help="verifier output; defaults to bdpass_<tag>.jsonl")
    ap.add_argument("--label", default=None, help="name for this arm in the output")
    ap.add_argument("--eligibility", choices=["usable", "passes", "all"], default="usable",
                    help="which generated backdoors count as the attack class. "
                         "`usable` (default): passes the public tests AND fires on its trigger - the "
                         "strict set, and the one whose yield is ~2%%. `passes`: passes the public "
                         "tests, firing not required - the same-generator analogue of the stored "
                         "benchmark's inert backdoors, which the paper already shows are separable "
                         "at 0.955 pairwise, i.e. the classifier does not read firing. `all`: every "
                         "generated candidate. Report `usable` and `passes` side by side; the two "
                         "answer different questions and neither is a substitute for the other.")
    ap.add_argument("--min-pairs", type=int, default=50,
                    help="refuse to print a verdict below this many pairs (default 50)")
    args = ap.parse_args()
    tag = args.tag

    honest = {json.loads(l)["problem_id"]: json.loads(l)["code"]
              for l in open(f"gen_{tag}.jsonl") if l.strip()}
    hon_pass = {json.loads(l)["problem_id"] for l in open(f"pass_{tag}.jsonl")
                if l.strip() and json.loads(l)["passed"]}
    bd_path = args.bd or f"bd_{tag}.jsonl"
    bdpass_path = args.bdpass or f"bdpass_{tag}.jsonl"
    bd = {json.loads(l)["problem_id"]: json.loads(l)["code"]
          for l in open(bd_path) if l.strip()}
    def _eligible(rec: dict) -> bool:
        if args.eligibility == "all":
            return True
        if args.eligibility == "passes":
            return bool(rec["passes_tests"])
        return bool(rec["passes_tests"] and rec["backdoor_works"])
    bd_ok = {json.loads(l)["problem_id"] for l in open(bdpass_path)
             if l.strip() and _eligible(json.loads(l))}
    print(f"attack-class eligibility: {args.eligibility}")
    arm = args.label or ("independent" if "bdind" in bd_path else "edit")
    print(f"arm: {arm}   backdoors from {bd_path}")

    # The whole claim of this arm is that ONE model wrote both classes. Nothing above enforces it -
    # the files are located by tag, so a mismatched pair produces a confident and wrong verdict.
    # (Observed: Sonnet 5 honest against the stored claude-3-7 backdoors scores S=0.92 and prints
    # "CONTENT", when it is really a cross-generator comparison - the G arm under another name.)
    hon_models = {json.loads(l).get("model") for l in open(f"gen_{tag}.jsonl") if l.strip()}
    bd_models = {json.loads(l).get("model") for l in open(bd_path) if l.strip()}
    if hon_models != bd_models:
        raise SystemExit(
            f"REFUSING: the two classes do not share a generator.\n"
            f"  honest   {sorted(m or '?' for m in hon_models)}\n"
            f"  backdoor {sorted(m or '?' for m in bd_models)}\n"
            f"This script measures what survives when authorship is held constant. With different\n"
            f"generators on the two sides it measures authorship instead, and its verdict lines\n"
            f"would be wrong rather than merely weak. Use gate_s_eval.py for cross-generator arms.")
    print(f"generator on both sides: {sorted(hon_models)[0]}")

    eligible = sorted(hon_pass & bd_ok & set(honest) & set(bd))
    print(f"honest generated {len(honest)}, of which pass tests {len(hon_pass)}")
    print(f"backdoors generated {len(bd)}, of which usable {len(bd_ok)}")
    print(f"SAME-GENERATOR PAIRS (both sides valid): {len(eligible)}\n")
    if len(eligible) < args.min_pairs:
        raise SystemExit(f"only {len(eligible)} pairs - below the {args.min_pairs}-pair floor")

    rows = [{"problem_id": p,
             "honest": strip_comments(honest[p]),
             "attack": strip_comments(bd[p])} for p in eligible]
    same = pd.DataFrame(rows)

    # The stored benchmark restricted to these same problems, so the two are like-for-like.
    cols = ["problem_id", "solutions", "backdoors"]
    art = pd.concat([pq.read_table(f, columns=cols).to_pandas()
                     for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
    art["problem_id"] = art.problem_id.astype(str)
    stored = []
    for _, r in art[art.problem_id.isin(set(eligible))].iterrows():
        row = {"problem_id": r.problem_id, "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions], "top_backdoor_model": None}
        b, h = _pick_backdoor(row), _honest_code(row)
        if b and h:
            stored.append({"problem_id": r.problem_id,
                           "honest": strip_comments(h),
                           "attack": strip_comments(b["backdoor_code"])})
    stored = pd.DataFrame(stored)

    # How similar is each pair? This is what distinguishes the two arms, and without it a low S is
    # ambiguous. The edit arm is handed its own honest solution, so its pairs are near-copies; the
    # stored benchmark's pairs are largely independent programs (measured 2026-09-10 over 400
    # analysis-pool pairs: mean 0.469, 2.5% above 0.95, 60.8% below 0.60). An arm whose similarity
    # sits near the stored value has changed only authorship; one near 1.0 has changed more.
    import difflib
    sim = [difflib.SequenceMatcher(None, r["honest"], r["attack"]).ratio() for r in rows]
    sim_s = sorted(sim)
    pair_sim = {"mean": float(np.mean(sim)), "median": float(np.median(sim)),
                "p10": sim_s[int(0.10 * len(sim_s))], "p90": sim_s[int(0.90 * len(sim_s))],
                "frac_above_0.95": float(np.mean([x > 0.95 for x in sim])),
                "frac_below_0.60": float(np.mean([x < 0.60 for x in sim]))}
    print(f"pair similarity (honest vs attack, chars): mean {pair_sim['mean']:.3f}  "
          f"median {pair_sim['median']:.3f}  >0.95 {pair_sim['frac_above_0.95']:.1%}  "
          f"<0.60 {pair_sim['frac_below_0.60']:.1%}")
    if len(stored):
        sim_st = [difflib.SequenceMatcher(None, r["honest"], r["attack"]).ratio()
                  for _, r in stored.iterrows()]
        pair_sim["stored_same_problems"] = {
            "mean": float(np.mean(sim_st)), "median": float(np.median(sim_st)),
            "frac_above_0.95": float(np.mean([x > 0.95 for x in sim_st])),
            "frac_below_0.60": float(np.mean([x < 0.60 for x in sim_st])), "n": len(sim_st)}
        st = pair_sim["stored_same_problems"]
        print(f"  stored benchmark, SAME problems, same measure: mean {st['mean']:.3f}  "
              f"median {st['median']:.3f}  >0.95 {st['frac_above_0.95']:.1%}  "
              f"<0.60 {st['frac_below_0.60']:.1%}  (n={st['n']})")
    print("  stored benchmark, 400-pair sample (RESULTS.md 4.8): mean 0.469  median 0.475  "
          ">0.95 2.5%  <0.60 60.8%")
    if pair_sim["mean"] > 0.80:
        print("  ^ NEAR-COPIES. A low S here does not separate 'the benchmark measured authorship'\n"
              "    from 'these two classes are nearly the same text'. Report it as a bound.")

    print("problem-disjoint 5-fold, comments stripped, identical pipeline:")
    S = evaluate(same, f"S  {tag} honest vs {tag} backdoor")
    out = {"tag": tag, "arm": arm, "eligibility": args.eligibility,
           "n_same_generator_pairs": len(same), "pair_similarity": pair_sim, "S": S}
    if len(stored) >= 50:
        Bp = evaluate(stored, "B' human honest vs stored backdoor (same problems)")
        out["B_prime"] = Bp
        drop = (S["auroc"] - 0.5) / (Bp["auroc"] - 0.5) if Bp["auroc"] > 0.5 else float("nan")
        out["retained_vs_stored"] = drop
        print(f"\n  B' = {Bp['auroc']:.4f}   S = {S['auroc']:.4f}   "
              f"retained = (S-0.5)/(B'-0.5) = {drop:.4f}")
        print(f"  per-carrier B' -> S:  TF-IDF {S['auroc']-Bp['auroc']:+.4f}   "
              f"length-only {S['length_only_auroc']-Bp['length_only_auroc']:+.4f}   "
              f"surface7 {S['surface7_auroc']-Bp['surface7_auroc']:+.4f}")

    lo, hi = S["auroc"] - 2 * S["auroc_sd"], S["auroc"] + 2 * S["auroc_sd"]
    print(f"\n  S = {S['auroc']:.4f}  (+/-2sd: {lo:.4f} - {hi:.4f})")
    if hi < 0.60:
        verdict = ("AUTHORSHIP. With one generator on both sides a trivial baseline is near chance. "
                   "The stored benchmark's separability was who wrote the code.")
    elif lo > 0.75:
        verdict = ("CONTENT. These backdoors carry real surface signal even with authorship held "
                   "constant. Report the floor; same-generator sampling alone does not fix it.")
    else:
        verdict = ("PARTIAL / INCONCLUSIVE at this n. State the interval, do not round it to a "
                   "verdict.")
    out["verdict"] = verdict
    print(f"  {verdict}")

    path = args.out or f"gate_s_samegen_{tag}_{arm}_{args.eligibility}.json"
    json.dump(out, open(path, "w"), indent=2, default=float)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
