"""What the residual same-generator signal is made of: attribution and masking, S beside B'.

RESULTS.md 9-10 leave the headline S = 0.7512 (n = 623, attack = passes the public tests, 97.5%
never fire) with a reading but not a measurement: a monitor scores 0.566 on those pairs, so what the
bag-of-words classifier still separates with authorship held constant is claimed to be a lexical
trace of the attack INSTRUCTION - the trigger idiom (`==` against a magic constant, >= 3-digit
numerals; survivor check p = 0.0024 / 0.0025) - rather than sabotage. This script makes that a
measurement, three ways, always fitting S and the stored B' over the SAME problems so that every
row carries both numbers:

    1. attribution   the identical pipeline fitted once on all pairs; top-25 weights each way
    2. masking       token-exact (tokenize module) ablations, each re-run through evaluate():
                       NUM   every NUMBER token -> NUM
                       CMP   ==  !=  <=  >=  <  >  -> CMP
                       ID    every NAME that is not a keyword/builtin -> ID  ("structure only")
                     the unmasked row must reproduce 0.7512 / 0.8658 (headline) and
                     0.7652 / 0.7877 (strict) to the printed decimals, else the script stops
    3. char n-gram   analyzer="char_wb", (3, 5), same classifier and folds - one robustness row

Reading: S falls under NUM/CMP while B' holds -> the residual is the trigger idiom. S holds ->
the residual is broader; read the feature lists. B' falls as much as S -> the idiom is in the
stored benchmark too. Pairs are built exactly as gate_s_samegen.py builds them (its code is
copied, not imported, because that script has no loader function). Nothing tracked is modified.

    python3 lexical_probe.py --out lexical_probe.json
"""

from __future__ import annotations

import argparse
import builtins
import glob
import io
import json
import keyword
import os
import sys
import tokenize

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate_s_eval  # noqa: E402
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402
from gate_s_eval import evaluate  # noqa: E402 - the identical fit used for S and B'

VEC_KW = dict(token_pattern=r"[A-Za-z_]+|\d+|[^\sA-Za-z_\d]", ngram_range=(1, 2),
              min_df=3, max_features=50000, sublinear_tf=True)  # verbatim from evaluate()
CMP_OPS = {"==", "!=", "<=", ">=", "<", ">"}
KEEP_NAMES = set(keyword.kwlist) | set(keyword.softkwlist) | set(dir(builtins))
MASKS = {"none": (), "NUM": ("num",), "CMP": ("cmp",), "NUM+CMP": ("num", "cmp"),
         # collapsing keeps the `CMP NUM` bigram (the idiom's presence); deleting removes it
         "NUM+CMP deleted": ("num", "cmp", "delete"), "ID (structure only)": ("ident",)}
SETS = {  # name -> (sg json, bd file, bdpass file, eligibility, bprime_inert)
    "headline": ("sg_indep_first_passes.json", "bdind_sonnet5_first.jsonl",
                 "bdindpass_sonnet5_first.jsonl", "passes", True),
    "strict": ("sg_indep_best_usable.json", "bdind_sonnet5_best_nocrash.jsonl",
               "bdindpass_sonnet5_best_nocrash.jsonl", "usable", False)}
MASK_FAILS = {"n": 0}


def mask(code: str, what: tuple[str, ...]) -> str:
    """Replace whole tokens in place by (row, col) so nothing else in the source moves."""
    if not what:
        return code
    lines, edits = code.split("\n"), []
    try:
        for t in tokenize.tokenize(io.BytesIO(code.encode("utf-8")).readline):
            if t.start[0] != t.end[0]:
                continue
            rep = ("NUM" if "num" in what and t.type == tokenize.NUMBER else
                   "CMP" if "cmp" in what and t.type == tokenize.OP and t.string in CMP_OPS else
                   "ID" if "ident" in what and t.type == tokenize.NAME
                   and t.string not in KEEP_NAMES else None)
            if rep:
                edits.append((t.start[0] - 1, t.start[1], t.end[1], "" if "delete" in what else rep))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        MASK_FAILS["n"] += 1  # strip_comments also falls through; left unmasked and counted
        return code
    for row, c0, c1, rep in sorted(edits, reverse=True):
        lines[row] = lines[row][:c0] + rep + lines[row][c1:]
    return "\n".join(lines)


def load_pairs(sg_json: str, bd_path: str, bdpass_path: str, elig: str, inert: bool):
    """The same-generator pairs and the stored pairs over the same problems, as gate_s_samegen.py."""
    pids = json.load(open(sg_json))["problem_ids"]
    honest = {json.loads(l)["problem_id"]: json.loads(l)["code"]
              for l in open("gen_sonnet5.jsonl") if l.strip()}
    hon_pass = {json.loads(l)["problem_id"] for l in open("pass_sonnet5.jsonl")
                if l.strip() and json.loads(l)["passed"]}
    bd = {json.loads(l)["problem_id"]: json.loads(l)["code"] for l in open(bd_path) if l.strip()}
    ok = {r["problem_id"] for r in map(json.loads, filter(str.strip, open(bdpass_path)))
          if r["passes_tests"] and (elig == "passes" or r["backdoor_works"])}
    eligible = sorted(hon_pass & ok & set(honest) & set(bd))
    assert eligible == sorted(pids), f"{sg_json}: rebuilt {len(eligible)} pairs, json has {len(pids)}"
    same = pd.DataFrame([{"problem_id": p, "honest": strip_comments(honest[p]),
                          "attack": strip_comments(bd[p])} for p in eligible])
    art = pd.concat([pq.read_table(f, columns=["problem_id", "solutions", "backdoors"]).to_pandas()
                     for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
    art["problem_id"] = art.problem_id.astype(str)
    stored = []
    for _, r in art[art.problem_id.isin(set(eligible))].iterrows():
        row = {"problem_id": r.problem_id, "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions], "top_backdoor_model": None}
        b = ([b for b in row["backdoors"] if b["passes_tests"]] or [None])[0] if inert \
            else _pick_backdoor(row)
        h = _honest_code(row)
        if b and h:
            stored.append({"problem_id": r.problem_id, "honest": strip_comments(h),
                           "attack": strip_comments(b["backdoor_code"])})
    return same, pd.DataFrame(stored)


def masked(pairs: pd.DataFrame, what: tuple[str, ...]) -> pd.DataFrame:
    out = pairs.copy()
    out["honest"], out["attack"] = [mask(c, what) for c in out.honest], [mask(c, what) for c in out.attack]
    return out


def attribution(pairs: pd.DataFrame, k: int = 25) -> dict:
    """One fit of the identical pipeline on all pairs; the k largest weights each way."""
    vec = TfidfVectorizer(**VEC_KW)
    X = vec.fit_transform(list(pairs.honest) + list(pairs.attack))
    y = np.r_[np.zeros(len(pairs)), np.ones(len(pairs))]
    w = LogisticRegression(max_iter=3000, class_weight="balanced").fit(X, y).coef_[0]
    names, order = vec.get_feature_names_out(), np.argsort(w)
    return {"n_features": int(len(w)),
            "attack": [[str(names[i]), round(float(w[i]), 4)] for i in order[::-1][:k]],
            "honest": [[str(names[i]), round(float(w[i]), 4)] for i in order[:k]]}


def row(name: str, same: pd.DataFrame, stored: pd.DataFrame) -> dict:
    S, Bp = evaluate(same, f"S  {name}"), evaluate(stored, f"B' {name}")
    rho = (S["auroc"] - 0.5) / (Bp["auroc"] - 0.5)
    return {"S": S, "B_prime": Bp, "rho": rho,
            "rho_ci95": [(c - 0.5) / (Bp["auroc"] - 0.5) for c in S["auroc_ci95_boot"]]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="lexical_probe.json")
    args = ap.parse_args()
    out = {}
    for name, (sg, bdf, bdp, elig, inert) in SETS.items():
        same, stored = load_pairs(sg, bdf, bdp, elig, inert)
        ref = json.load(open(sg))
        print(f"\n== {name}: {len(same)} same-generator pairs, {len(stored)} stored pairs, "
              f"B' rule = {ref['b_prime_attack_rule']}")
        res = {"n_pairs": len(same), "n_stored": len(stored), "b_prime_attack_rule": ref["b_prime_attack_rule"],
               "attribution": {"S": attribution(same), "B_prime": attribution(stored)}, "masking": {}}
        for mname, what in MASKS.items():
            if name == "strict" and mname in ("ID (structure only)", "NUM+CMP deleted"):
                continue
            r = res["masking"][mname] = row(f"{name} [{mname}]", masked(same, what), masked(stored, what))
            if mname == "none":  # the control: must reproduce the ledger to the printed decimals
                for key, got, want in [("S", r["S"]["auroc"], ref["S"]["auroc"]),
                                       ("B'", r["B_prime"]["auroc"], ref["B_prime"]["auroc"])]:
                    if f"{got:.4f}" != f"{want:.4f}":
                        raise SystemExit(f"CONTROL FAILED on {name}: {key} = {got:.4f}, ledger {want:.4f}")
                print(f"  control reproduces {sg}: S {r['S']['auroc']:.4f}, B' {r['B_prime']['auroc']:.4f}")
        if name == "headline":  # the char n-gram row: same classifier and folds, other vectoriser
            orig = gate_s_eval.TfidfVectorizer
            gate_s_eval.TfidfVectorizer = lambda **kw: orig(**{**{k: v for k, v in kw.items() if k != "token_pattern"},
                                                               "analyzer": "char_wb", "ngram_range": (3, 5)})
            try:
                res["char_ngram_3_5"] = row("headline [char_wb 3-5]", same, stored)
            finally:
                gate_s_eval.TfidfVectorizer = orig
        out[name] = res
    out["mask_tokenize_failures"] = MASK_FAILS["n"]

    print(f"\n{'set':9s} {'mask':20s} {'S':>7s} {'95% CI':>15s} {'B_prime':>7s} {'95% CI':>15s} {'rho':>6s} {'rho CI':>13s}")
    for name, res in ((n, out[n]) for n in SETS):
        rows = list(res["masking"].items()) + ([("char_wb 3-5", res["char_ngram_3_5"])] if "char_ngram_3_5" in res else [])
        for mname, r in rows:
            s, b = r["S"], r["B_prime"]
            print(f"{name:9s} {mname:20s} {s['auroc']:7.4f} {s['auroc_ci95_boot'][0]:7.4f}-{s['auroc_ci95_boot'][1]:6.4f}"
                  f" {b['auroc']:7.4f} {b['auroc_ci95_boot'][0]:7.4f}-{b['auroc_ci95_boot'][1]:6.4f}"
                  f" {r['rho']:6.3f} {r['rho_ci95'][0]:6.3f}-{r['rho_ci95'][1]:5.3f}")
        for side in ("S", "B_prime"):
            a = res["attribution"][side]
            print(f"  {name} {side} top-10 -> attack: " + ", ".join(f"{f} ({w:+.2f})" for f, w in a["attack"][:10]))
            print(f"  {name} {side} top-10 -> honest: " + ", ".join(f"{f} ({w:+.2f})" for f, w in a["honest"][:10]))
    print(f"tokenize failures during masking (left unmasked): {MASK_FAILS['n']}")
    json.dump(out, open(args.out, "w"), indent=2, default=float)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
