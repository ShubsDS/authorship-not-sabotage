"""Arm 3: the PROMPT-MATCHED honest class, against the same attack draws.

RESULTS.md §9 held the *model* constant (Sonnet 5 wrote both classes) and found a residual
S = 0.7512 against B' = 0.8658 (ρ = 0.687, n = 623). §11 then measured what that residual is made
of: not the trigger idiom (masking numerals and comparison operators moves S by < 0.003) but
program LAYOUT — `def main` in 66.9% of attacks against 38.5% of honest, `data[` 37.7% vs 13.6% —
which is layout the *attack prompt* elicits. So the arm held the model constant but not the prompt,
and the obvious reviewer objection is that the residual is prompt framing rather than content.

This script measures that objection directly. `gen_honest_api.py --matched` regenerated the honest
class from `gen_backdoor.PROMPT_INDEPENDENT_HONEST` — PROMPT_INDEPENDENT with only the flaw
sentence replaced, same framing, same two-block output format — on exactly the problems the attack
arm was generated on. Two numbers follow:

    (a) S_matched      matched honest vs the SAME attack draws. Model and prompt both held
                       constant; only the one sentence asking for a flaw differs.
    (b) prompt-only    original honest vs matched honest. Two correct classes by one model that
                       differ in nothing but the prompt. This is the cleanest number here: it is
                       how much of the §11 residual the framing alone can manufacture.

Reading, against the pre-registered ρ bands (collapse ≤ 0.33, partial, content > 0.72):

    S_matched in the collapse band AND a high prompt-only floor
        the §11 residual was framing. Holding the prompt constant removes it.
    S_matched near 0.75
        the residual is content of the attack class, independent of framing.

Everything is computed as §9 and §11 compute it: `gate_s_eval.evaluate()` unchanged (problem-
disjoint 5-fold, comments stripped, bootstrap over problems, 2,000 draws, seed 0), the pair
loaders copied from `gate_s_samegen.py` / `lexical_probe.py` rather than edited, the ID mask and
the attribution fit imported from `lexical_probe.py`, the joint ρ bootstrap from `rho_joint_ci.py`.
The unmasked ORIGINAL honest row is re-fitted on the full problem set as a control and the script
stops if it does not reproduce the committed json to four decimals.

    python3 gate_s_matched.py     # CPU, a few minutes
"""

from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import re
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate_s_eval  # noqa: E402
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402
from gate_s_eval import evaluate  # noqa: E402 - the identical fit used for B, S and B'
from lexical_probe import attribution, mask  # noqa: E402 - the same ID mask and the same fit
from rho_joint_ci import joint_bootstrap  # noqa: E402 - §12.2's joint interval for ρ

SETS = {  # name -> (sg json, bd file, bdpass file, eligibility, bprime_inert)
    "headline": ("sg_indep_first_passes.json", "bdind_sonnet5_first.jsonl",
                 "bdindpass_sonnet5_first.jsonl", "passes", True),
    "strict": ("sg_indep_best_usable.json", "bdind_sonnet5_best_nocrash.jsonl",
               "bdindpass_sonnet5_best_nocrash.jsonl", "usable", False)}

# §11.3's presence probes, on the comment-stripped code.
PRESENCE = {"def main": r"def\s+main", "data[": r"\bdata\s*\[", "any def": r"\bdef\s",
            "sys.stdin": r"sys\.stdin", "input(": r"\binput\s*\("}


def jsonl_code(path: str) -> dict:
    return {json.loads(l)["problem_id"]: json.loads(l)["code"] for l in open(path) if l.strip()}


def passers(path: str) -> set:
    return {json.loads(l)["problem_id"] for l in open(path)
            if l.strip() and json.loads(l)["passed"]}


def load(sg_json: str, bd_path: str, bdpass_path: str, elig: str, inert: bool,
         matched_gen: str, matched_pass: str):
    """Pairs exactly as gate_s_samegen.py builds them, plus the matched honest class.

    Returns (pids, honest, matched, attack, stored) where `stored` maps problem_id to the stored
    benchmark's pair over the same problems, so B' can be re-fitted on any subset of them.
    """
    pids = json.load(open(sg_json))["problem_ids"]
    honest = jsonl_code("gen_sonnet5.jsonl")
    hon_pass = passers("pass_sonnet5.jsonl")
    bd = jsonl_code(bd_path)
    ok = {r["problem_id"] for r in map(json.loads, filter(str.strip, open(bdpass_path)))
          if r["passes_tests"] and (elig == "passes" or r["backdoor_works"])}
    eligible = sorted(hon_pass & ok & set(honest) & set(bd))
    assert eligible == sorted(pids), f"{sg_json}: rebuilt {len(eligible)} pairs, json has {len(pids)}"

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
        b = ([x for x in row["backdoors"] if x["passes_tests"]] or [None])[0] if inert \
            else _pick_backdoor(row)
        h = _honest_code(row)
        if b and h:
            stored[r.problem_id] = {"problem_id": r.problem_id, "honest": strip_comments(h),
                                    "attack": strip_comments(b["backdoor_code"])}
    return eligible, honest, matched, bd, stored


def frame(pids, left: dict, right: dict, what: tuple = ()) -> pd.DataFrame:
    """One row per problem: `honest` is the negative class, `attack` the positive one."""
    return pd.DataFrame([{"problem_id": p,
                          "honest": mask(strip_comments(left[p]), what),
                          "attack": mask(strip_comments(right[p]), what)} for p in pids])


def stored_frame(pids, stored: dict, what: tuple = ()) -> pd.DataFrame:
    return pd.DataFrame([{"problem_id": p, "honest": mask(stored[p]["honest"], what),
                          "attack": mask(stored[p]["attack"], what)}
                         for p in pids if p in stored])


def rho_block(S: dict, Bp: dict) -> dict:
    """ρ = (S - 0.5)/(B' - 0.5): the S-only interval of §9 and the joint interval of §12.2."""
    bp = Bp["auroc"]
    out = {"rho": (S["auroc"] - 0.5) / (bp - 0.5),
           "rho_ci95_S_only": [(c - 0.5) / (bp - 0.5) for c in S["auroc_ci95_boot"]]}
    s_df = pd.DataFrame(S["oof"]).set_index("problem_id")
    b_df = pd.DataFrame(Bp["oof"]).set_index("problem_id")
    jb = joint_bootstrap(s_df, b_df, 2000, 0)
    out["joint"] = jb
    out["rho_ci95_joint"] = jb["rho_ci95_joint"]
    return out


def similarity(pids, left: dict, right: dict) -> dict:
    sims = [difflib.SequenceMatcher(None, strip_comments(left[p]), strip_comments(right[p]),
                                    autojunk=False).ratio() for p in pids]
    s = sorted(sims)
    return {"n": len(sims), "mean": float(np.mean(sims)), "median": float(np.median(sims)),
            "p10": s[int(0.10 * len(s))], "p90": s[int(0.90 * len(s))],
            "frac_above_0.95": float(np.mean([x > 0.95 for x in sims])),
            "frac_below_0.60": float(np.mean([x < 0.60 for x in sims]))}


def presence(codes: list) -> dict:
    stripped = [strip_comments(c) for c in codes]
    return {k: float(np.mean([bool(re.search(rx, c)) for c in stripped]))
            for k, rx in PRESENCE.items()}


def run_set(name: str, spec, matched_gen: str, matched_pass: str, out_path: str) -> dict:
    sg_json, bd_path, bdpass_path, elig, inert = spec
    pids, honest, matched, attack, stored = load(sg_json, bd_path, bdpass_path, elig, inert,
                                                 matched_gen, matched_pass)
    ref = json.load(open(sg_json))
    keep = [p for p in pids if p in matched]          # matched honest exists AND passes
    dropped = [p for p in pids if p not in matched]
    print(f"\n=== {name}: {len(pids)} §9 problems, matched honest passes on {len(keep)} "
          f"({len(dropped)} dropped)   B' rule = {ref['b_prime_attack_rule']}")

    out = {"set": name, "sg_json": sg_json, "bd": bd_path, "bdpass": bdpass_path,
           "eligibility": elig, "b_prime_attack_rule": ref["b_prime_attack_rule"],
           "n_problems_gate_s": len(pids), "n_problems_matched": len(keep),
           "n_dropped_matched_fails": len(dropped), "problem_ids": keep,
           "dropped_problem_ids": dropped,
           "ledger": {"S": ref["S"]["auroc"], "B_prime": ref["B_prime"]["auroc"],
                      "rho": ref["retained_vs_stored"]}}

    # --- control: the ORIGINAL honest class on the FULL §9 problem set must reproduce the ledger
    print("control (original honest, all §9 problems):")
    ctl_S = evaluate(frame(pids, honest, attack), f"S  {name} original (control)")
    ctl_B = evaluate(stored_frame(pids, stored), f"B' {name} (control)")
    for key, got, want in [("S", ctl_S["auroc"], ref["S"]["auroc"]),
                           ("B'", ctl_B["auroc"], ref["B_prime"]["auroc"])]:
        if f"{got:.4f}" != f"{want:.4f}":
            raise SystemExit(f"CONTROL FAILED on {name}: {key} = {got:.4f}, ledger {want:.4f}")
    print(f"  control reproduces {sg_json}: S {ctl_S['auroc']:.4f}, B' {ctl_B['auroc']:.4f}")
    out["control_original_full"] = {"S": ctl_S, "B_prime": ctl_B, **rho_block(ctl_S, ctl_B)}

    if len(keep) < 50:
        out["refused"] = f"only {len(keep)} problems with a passing matched honest program"
        print(f"  REFUSING the rest of {name}: {out['refused']}")
        json.dump(out, open(out_path, "w"), indent=2, default=float)
        return out

    # --- (a) S_matched, and the original S on the same reduced problem set for comparability
    print("(a) matched honest vs the same attack draws:")
    S_m = evaluate(frame(keep, matched, attack), f"S  {name} MATCHED honest vs attack")
    B_k = evaluate(stored_frame(keep, stored), f"B' {name} (matched problems)")
    S_o = evaluate(frame(keep, honest, attack), f"S  {name} original honest, same problems")
    out["S_matched"] = {"S": S_m, "B_prime": B_k, **rho_block(S_m, B_k)}
    out["S_original_same_problems"] = {"S": S_o, "B_prime": B_k, **rho_block(S_o, B_k)}

    # --- (b) the prompt-only floor: two correct classes, one model, only the prompt differs
    print("(b) prompt-only floor (original honest vs matched honest):")
    P = evaluate(frame(keep, honest, matched), f"P  {name} original vs matched honest")
    out["prompt_only"] = {"S": P}

    # --- (c) identifier normalisation (§11's only mask that moved S) and the char_wb row
    print("(c) ID mask (structure only) and char_wb 3-5:")
    S_mi = evaluate(frame(keep, matched, attack, ("ident",)), f"S  {name} MATCHED [ID]")
    B_ki = evaluate(stored_frame(keep, stored, ("ident",)), f"B' {name} [ID]")
    S_oi = evaluate(frame(keep, honest, attack, ("ident",)), f"S  {name} original [ID]")
    P_i = evaluate(frame(keep, honest, matched, ("ident",)), f"P  {name} prompt-only [ID]")
    out["masked_ID"] = {"S_matched": {"S": S_mi, "B_prime": B_ki, **rho_block(S_mi, B_ki)},
                        "S_original_same_problems": {"S": S_oi, "B_prime": B_ki,
                                                     **rho_block(S_oi, B_ki)},
                        "prompt_only": {"S": P_i}}

    orig_vec = gate_s_eval.TfidfVectorizer
    gate_s_eval.TfidfVectorizer = lambda **kw: orig_vec(
        **{**{k: v for k, v in kw.items() if k != "token_pattern"},
           "analyzer": "char_wb", "ngram_range": (3, 5)})
    try:
        S_mc = evaluate(frame(keep, matched, attack), f"S  {name} MATCHED [char_wb]")
        B_kc = evaluate(stored_frame(keep, stored), f"B' {name} [char_wb]")
        P_c = evaluate(frame(keep, honest, matched), f"P  {name} prompt-only [char_wb]")
    finally:
        gate_s_eval.TfidfVectorizer = orig_vec
    out["char_ngram_3_5"] = {"S_matched": {"S": S_mc, "B_prime": B_kc, **rho_block(S_mc, B_kc)},
                             "prompt_only": {"S": P_c}}

    # --- (d) presence rates (§11.3 style) and the top features of the S_matched fit
    out["presence"] = {
        "matched_honest": presence([matched[p] for p in keep]),
        "original_honest": presence([honest[p] for p in keep]),
        "attack": presence([attack[p] for p in keep]),
        "stored_honest": presence([stored[p]["honest"] for p in keep if p in stored]),
        "stored_attack": presence([stored[p]["attack"] for p in keep if p in stored])}
    out["attribution"] = {"S_matched": attribution(frame(keep, matched, attack)),
                          "prompt_only": attribution(frame(keep, honest, matched))}

    # --- (f) pair similarity, difflib autojunk=False, as gate_s_samegen measures it
    out["pair_similarity"] = {
        "matched_honest_vs_attack": similarity(keep, matched, attack),
        "original_honest_vs_attack": similarity(keep, honest, attack),
        "original_vs_matched_honest": similarity(keep, honest, matched),
        "stored_same_problems": similarity([p for p in keep if p in stored],
                                           {p: v["honest"] for p, v in stored.items()},
                                           {p: v["attack"] for p, v in stored.items()})}

    json.dump(out, open(out_path, "w"), indent=2, default=float)
    print(f"wrote {out_path}")
    return out


def summarise(res: dict) -> None:
    name = res["set"]
    if "refused" in res:
        print(f"{name:9s} REFUSED: {res['refused']}")
        return
    def line(tag, blk, bp=True):
        s = blk["S"]
        txt = (f"{name:9s} {tag:28s} n={s['n_pairs']:4d} AUROC={s['auroc']:.4f} "
               f"({s['auroc_ci95_boot'][0]:.4f}-{s['auroc_ci95_boot'][1]:.4f}) "
               f"pairwise={s['pairwise_acc']:.3f} len={s['length_only_auroc']:.4f} "
               f"surf7={s['surface7_auroc']:.4f}")
        if bp and "rho" in blk:
            txt += (f"  B'={blk['B_prime']['auroc']:.4f} rho={blk['rho']:.3f} "
                    f"(S-only {blk['rho_ci95_S_only'][0]:.3f}-{blk['rho_ci95_S_only'][1]:.3f}; "
                    f"joint {blk['rho_ci95_joint'][0]:.3f}-{blk['rho_ci95_joint'][1]:.3f})")
        print(txt)
    line("control original (all §9)", res["control_original_full"])
    line("(a) S_matched", res["S_matched"])
    line("    S_original same problems", res["S_original_same_problems"])
    line("(b) prompt-only floor", res["prompt_only"], bp=False)
    line("(c) S_matched [ID]", res["masked_ID"]["S_matched"])
    line("    S_original [ID]", res["masked_ID"]["S_original_same_problems"])
    line("    prompt-only [ID]", res["masked_ID"]["prompt_only"], bp=False)
    line("    S_matched [char_wb]", res["char_ngram_3_5"]["S_matched"])
    line("    prompt-only [char_wb]", res["char_ngram_3_5"]["prompt_only"], bp=False)
    print(f"  {name} presence (matched / original honest / attack):")
    for k in PRESENCE:
        p = res["presence"]
        print(f"    {k:10s} {p['matched_honest'][k]:.3f} / {p['original_honest'][k]:.3f} / "
              f"{p['attack'][k]:.3f}   (stored {p['stored_honest'][k]:.3f} / "
              f"{p['stored_attack'][k]:.3f})")
    for tag in ("S_matched", "prompt_only"):
        a = res["attribution"][tag]
        print(f"  {name} {tag} top-10 -> attack/matched: "
              + ", ".join(f"{f} ({w:+.2f})" for f, w in a["attack"][:10]))
        print(f"  {name} {tag} top-10 -> honest/original: "
              + ", ".join(f"{f} ({w:+.2f})" for f, w in a["honest"][:10]))
    s = res["pair_similarity"]
    for k, v in s.items():
        print(f"  {name} similarity {k:30s} mean {v['mean']:.3f} median {v['median']:.3f} "
              f">0.95 {v['frac_above_0.95']:.1%} <0.60 {v['frac_below_0.60']:.1%} (n={v['n']})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--matched-gen", default="genm_sonnet5.jsonl")
    ap.add_argument("--matched-pass", default="passm_sonnet5.jsonl")
    ap.add_argument("--out-headline", default="gate_s_matched_headline.json")
    ap.add_argument("--out-strict", default="gate_s_matched_strict.json")
    ap.add_argument("--only", choices=sorted(SETS), default=None)
    args = ap.parse_args()
    outs = {"headline": args.out_headline, "strict": args.out_strict}

    results = {}
    for name, spec in SETS.items():
        if args.only and name != args.only:
            continue
        results[name] = run_set(name, spec, args.matched_gen, args.matched_pass, outs[name])
    print()
    for name in results:
        summarise(results[name])


if __name__ == "__main__":
    main()
