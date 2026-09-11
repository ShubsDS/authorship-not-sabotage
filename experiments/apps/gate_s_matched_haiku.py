"""The prompt-matched rows for the Haiku 4.5 same-generator arm (RESULTS.md §15).

`gate_s_matched.py` (Worker A) defines the arm and computes it for Sonnet 5. Its `SETS`, and the
`load()` that backs them, name `gen_sonnet5.jsonl` / `pass_sonnet5.jsonl` / `bdind_sonnet5_*.jsonl`
directly, so it cannot be pointed at another model with a flag. Rather than edit another worker's
file mid-flight, this script **imports A's helpers** — `frame`, `rho_block`, `similarity`,
`presence`, `stored_frame` — so the two models' rows are produced by the same code, and supplies
its own Haiku loader. `gate_s_eval.evaluate()` is untouched, as everywhere else in the ledger.

Two numbers, defined exactly as A defines them:

    (a) S_matched    matched honest (PROMPT_INDEPENDENT_HONEST) vs the SAME attack draws. Model
                     AND prompt held constant; only the sentence asking for a flaw differs.
    (b) prompt-only  original honest vs matched honest. Two correct classes by one model that
                     differ in nothing but the prompt — how much of the residual framing alone
                     can manufacture.

`S_original_same_problems` is the §15 headline row re-fitted on the reduced problem set, because
(a) is only comparable against the original honest class on the SAME problems, not against the
full-set headline.

    python3 gate_s_matched_haiku.py --sg-json sg_haiku45_indep_passes.json
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402
from gate_s_eval import evaluate  # noqa: E402 - the identical fit used for B, S and B'
from gate_s_matched import frame, jsonl_code, passers, presence  # noqa: E402 - A's loaders
from gate_s_matched import rho_block, similarity, stored_frame  # noqa: E402


def load_haiku(sg_json: str, bdpass_path: str, elig: str, inert: bool,
               gen: str, hon_pass_file: str, bd_path: str,
               matched_gen: str, matched_pass: str):
    """The §15 pairs, rebuilt and checked against the problem_ids gate_s_samegen.py recorded."""
    pids = json.load(open(sg_json))["problem_ids"]
    honest = jsonl_code(gen)
    hon_pass = passers(hon_pass_file)
    bd = jsonl_code(bd_path)
    ok = {r["problem_id"] for r in map(json.loads, filter(str.strip, open(bdpass_path)))
          if r["passes_tests"] and (elig == "passes" or r["backdoor_works"])}
    eligible = sorted(hon_pass & ok & set(honest) & set(bd))
    assert eligible == sorted(pids), (
        f"{sg_json}: rebuilt {len(eligible)} pairs, json has {len(pids)}")

    matched = jsonl_code(matched_gen)
    mat_pass = passers(matched_pass)
    matched = {p: c for p, c in matched.items() if p in mat_pass and c.strip()}

    art = pd.concat([pq.read_table(f, columns=["problem_id", "solutions", "backdoors"]).to_pandas()
                     for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
    art["problem_id"] = art.problem_id.astype(str)
    stored = {}
    for _, r in art[art.problem_id.isin(set(eligible))].iterrows():
        row = {"problem_id": r.problem_id, "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions], "top_backdoor_model": None}
        b = (([x for x in row["backdoors"] if x["passes_tests"]] or [None])[0] if inert
             else _pick_backdoor(row))
        h = _honest_code(row)
        if b and h:
            stored[r.problem_id] = {"problem_id": r.problem_id, "honest": strip_comments(h),
                                    "attack": strip_comments(b["backdoor_code"])}
    return eligible, honest, matched, bd, stored


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sg-json", default="sg_haiku45_indep_passes.json",
                    help="the gate_s_samegen.py output whose problem_ids define the arm")
    ap.add_argument("--gen", default="gen_haiku45.jsonl")
    ap.add_argument("--honest-pass", default="pass_haiku45.jsonl")
    ap.add_argument("--bd", default="bdind_haiku45.jsonl")
    ap.add_argument("--bdpass", default="bdpass_haiku45.jsonl")
    ap.add_argument("--matched-gen", default="genm_haiku45.jsonl")
    ap.add_argument("--matched-pass", default="passm_haiku45.jsonl")
    ap.add_argument("--eligibility", choices=["passes", "usable"], default="passes")
    ap.add_argument("--bprime-inert", action="store_true", default=True)
    ap.add_argument("--no-bprime-inert", dest="bprime_inert", action="store_false")
    ap.add_argument("--out", default="gate_s_matched_haiku45.json")
    args = ap.parse_args()

    pids, honest, matched, attack, stored = load_haiku(
        args.sg_json, args.bdpass, args.eligibility, args.bprime_inert,
        args.gen, args.honest_pass, args.bd, args.matched_gen, args.matched_pass)
    ref = json.load(open(args.sg_json))
    keep = [p for p in pids if p in matched]
    dropped = [p for p in pids if p not in matched]
    print(f"\n=== haiku45: {len(pids)} §15 problems, matched honest passes on {len(keep)} "
          f"({len(dropped)} dropped)   B' rule = {ref['b_prime_attack_rule']}")

    out = {"tag": "haiku45", "sg_json": args.sg_json, "eligibility": args.eligibility,
           "b_prime_attack_rule": ref["b_prime_attack_rule"],
           "n_problems_gate_s": len(pids), "n_problems_matched": len(keep),
           "n_dropped_matched_fails": len(dropped), "problem_ids": keep,
           "dropped_problem_ids": dropped,
           "ledger": {"S": ref["S"]["auroc"], "B_prime": ref["B_prime"]["auroc"]}}

    # Control: the ORIGINAL honest class on the FULL §15 set must reproduce the committed json.
    print("control (original honest, all §15 problems):")
    ctl_S = evaluate(frame(pids, honest, attack), "S  haiku45 original (control)")
    ctl_B = evaluate(stored_frame(pids, stored), "B' haiku45 (control)")
    for key, got, want in [("S", ctl_S["auroc"], ref["S"]["auroc"]),
                           ("B'", ctl_B["auroc"], ref["B_prime"]["auroc"])]:
        if f"{got:.4f}" != f"{want:.4f}":
            raise SystemExit(f"CONTROL FAILED: {key} = {got:.4f}, ledger {want:.4f}")
    print(f"  control reproduces {args.sg_json}: S {ctl_S['auroc']:.4f}, B' {ctl_B['auroc']:.4f}")
    out["control_original_full"] = {"S": ctl_S, "B_prime": ctl_B, **rho_block(ctl_S, ctl_B)}

    if len(keep) < 50:
        out["refused"] = f"only {len(keep)} problems with a passing matched honest program"
        print(f"  REFUSING: {out['refused']}")
        json.dump(out, open(args.out, "w"), indent=2, default=float)
        return

    print("(a) matched honest vs the same attack draws:")
    S_m = evaluate(frame(keep, matched, attack), "S  haiku45 MATCHED honest vs attack")
    B_k = evaluate(stored_frame(keep, stored), "B' haiku45 (matched problems)")
    S_o = evaluate(frame(keep, honest, attack), "S  haiku45 original honest, same problems")
    out["S_matched"] = {"S": S_m, "B_prime": B_k, **rho_block(S_m, B_k)}
    out["S_original_same_problems"] = {"S": S_o, "B_prime": B_k, **rho_block(S_o, B_k)}

    print("(b) prompt-only floor (original honest vs matched honest):")
    out["prompt_only"] = {"S": evaluate(frame(keep, honest, matched),
                                        "P  haiku45 original vs matched honest")}

    out["presence"] = {"matched_honest": presence([matched[p] for p in keep]),
                       "original_honest": presence([honest[p] for p in keep]),
                       "attack": presence([attack[p] for p in keep])}
    out["pair_similarity"] = {
        "matched_honest_vs_attack": similarity(keep, matched, attack),
        "original_honest_vs_attack": similarity(keep, honest, attack),
        "original_vs_matched_honest": similarity(keep, honest, matched)}

    json.dump(out, open(args.out, "w"), indent=2, default=float)
    print(f"wrote {args.out}")

    def line(tag, blk, bp=True):
        s = blk["S"]
        txt = (f"haiku45  {tag:28s} n={s['n_pairs']:4d} AUROC={s['auroc']:.4f} "
               f"({s['auroc_ci95_boot'][0]:.4f}-{s['auroc_ci95_boot'][1]:.4f}) "
               f"pairwise={s['pairwise_acc']:.3f} len={s['length_only_auroc']:.4f} "
               f"surf7={s['surface7_auroc']:.4f}")
        if bp and "rho" in blk:
            txt += (f"  B'={blk['B_prime']['auroc']:.4f} rho={blk['rho']:.3f} "
                    f"(joint {blk['rho_ci95_joint'][0]:.3f}-{blk['rho_ci95_joint'][1]:.3f})")
        print(txt)
    print()
    line("control original (all §15)", out["control_original_full"])
    line("(a) S_matched", out["S_matched"])
    line("    S_original same problems", out["S_original_same_problems"])
    line("(b) prompt-only floor", out["prompt_only"], bp=False)


if __name__ == "__main__":
    main()
