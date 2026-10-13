"""The classifier's class-swap table: is its drop from B' to S on the honest side or the attack side?

monitor_swap.py shows that the LLM monitor's fall from stored to same-generator pairs comes
from the attack class (our attacks are far less conspicuous), not from replacing the human
honest code. This is the same 2x2 for the bag-of-words classifier, on the headline problems:

                      stored attack            our attack
    human honest      B' (the row's B')        the missing cell
    our honest        our honest vs stored     S (the row's S)

Each cell is a separate fit of gate_s_eval.evaluate() (imported: the same TF-IDF + logistic
regression, problem-disjoint 5-fold GroupKFold, comments stripped). The point is the pooled
out-of-fold AUROC; the interval is a joint bootstrap over problems of the four cells' out-of-fold
scores (2,000 draws, numpy RandomState(0), one randint(0, n, n) per draw, problems in sorted
id order), so the differences between cells carry paired intervals.

Pairs are built exactly as gate_s_samegen.py builds the headline row: our honest program from
gen_<tag>.jsonl where pass_<tag>.jsonl says it passes; our attack from --bd where --bdpass says it
passes the public tests (firing not required, --eligibility passes); the human honest program is
data._honest_code() (the artifact's shipped pass flag) and the stored attack is the first entry
that passes the public tests (--bprime-inert). The problem set must equal the --sg-json row's
`problem_ids` and the script exits if it does not; the S and B' cells are checked against that
json's `auroc_pooled_oof`.

Reading rule, fixed in camera-ready-plan.md before the cell was computed (printed with the
result): if human honest vs our attacks is near B' (~0.87), the classifier's drop is on the
honest side and the authorship reading holds for the classifier; if it is near S (~0.75), the
classifier behaves like the monitor and the corpus effect is mostly the attack distribution.

Needs the generated files, which are not committed (run on the cluster where they live), and
train_*.parquet (fetch.py). No API calls.

Usage:
    python classifier_swap.py --tag sonnet5 --bd bdind_sonnet5_first.jsonl \
        --bdpass bdindpass_sonnet5_first.jsonl --sg-json sg_indep_first_passes_v2.json \
        --out classifier_swap_sonnet5.json
    python classifier_swap.py --tag haiku45 --bd bdind_haiku45.jsonl \
        --bdpass bdpass_haiku45.jsonl --sg-json sg_haiku45_indep_passes.json \
        --out classifier_swap_haiku45.json
"""

from __future__ import annotations

import argparse
import contextlib
import glob
import io
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import _honest_code, strip_comments  # noqa: E402
from gate_s_eval import evaluate  # noqa: E402 - the identical fit used for S and B'

N_BOOT, SEED = 2000, 0
CELLS = [("human_honest", "stored_attack"), ("human_honest", "our_attack"),
         ("our_honest", "stored_attack"), ("our_honest", "our_attack")]
RULE = ("Reading rule (camera-ready-plan.md, fixed in advance): human honest vs our attacks\n"
        "  near B' (~0.87): the classifier's drop is on the honest side; the authorship reading\n"
        "                   holds for the classifier;\n"
        "  near S  (~0.75): the classifier behaves like the monitor; the corpus effect is mostly\n"
        "                   the attack distribution.")


def _read(path: str) -> list[dict]:
    return [json.loads(l) for l in open(path) if l.strip()]


def _auroc(h: np.ndarray, a: np.ndarray) -> float:
    return float(roc_auc_score(np.r_[np.zeros(len(h)), np.ones(len(a))], np.r_[h, a]))


def _pct(x) -> list:
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def build(args) -> tuple[pd.DataFrame, list]:
    gen, passed = _read(args.gen or f"gen_{args.tag}.jsonl"), _read(args.passf or f"pass_{args.tag}.jsonl")
    bd, bdpass = _read(args.bd), _read(args.bdpass)
    honest = {r["problem_id"]: r["code"] for r in gen}
    hon_pass = {r["problem_id"] for r in passed if r["passed"]}
    attack = {r["problem_id"]: r["code"] for r in bd}
    bd_ok = {r["problem_id"] for r in bdpass if r["passes_tests"]}
    hon_models, bd_models = {r.get("model") for r in gen}, {r.get("model") for r in bd}
    if hon_models != bd_models:
        raise SystemExit(f"REFUSING: the two generated classes do not share a generator "
                         f"({sorted(map(str, hon_models))} vs {sorted(map(str, bd_models))})")
    eligible = sorted(hon_pass & bd_ok & set(honest) & set(attack))

    want = sorted(str(p) for p in json.load(open(args.sg_json))["problem_ids"])
    if eligible != want:
        raise SystemExit(f"REFUSING: rebuilt problem set ({len(eligible)}) differs from "
                         f"{args.sg_json} ({len(want)}): only here {sorted(set(eligible) - set(want))[:5]}, "
                         f"only there {sorted(set(want) - set(eligible))[:5]}")

    shards = sorted(glob.glob("train_*.parquet"))
    if not shards:
        raise SystemExit("no train_*.parquet here - run `python fetch.py` first")
    art = pd.concat([pq.read_table(f, columns=["problem_id", "solutions", "backdoors"]).to_pandas()
                     for f in shards], ignore_index=True)
    art["problem_id"] = art.problem_id.astype(str)
    art = art[art.problem_id.isin(set(eligible))]
    stored = {}
    for _, r in art.iterrows():
        row = {"problem_id": r.problem_id, "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions], "top_backdoor_model": None}
        passing = [b for b in row["backdoors"] if b["passes_tests"]]   # --bprime-inert
        h = _honest_code(row)
        if passing and h:
            stored[r.problem_id] = (h, passing[0]["backdoor_code"])
    missing = [p for p in eligible if p not in stored]
    if missing:
        raise SystemExit(f"REFUSING: {len(missing)} problems have no stored pair: {missing[:5]}")

    rows = [{"problem_id": p,
             "human_honest": strip_comments(stored[p][0]),
             "stored_attack": strip_comments(stored[p][1]),
             "our_honest": strip_comments(honest[p]),
             "our_attack": strip_comments(attack[p])} for p in eligible]
    return pd.DataFrame(rows), sorted(hon_models, key=str)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", required=True, help="sonnet5 or haiku45")
    ap.add_argument("--bd", required=True, help="our attack programs (jsonl)")
    ap.add_argument("--bdpass", required=True, help="verify_backdoor.py verdicts for --bd")
    ap.add_argument("--sg-json", required=True, help="the gate_s_samegen.py row to match")
    ap.add_argument("--gen", default=None, help="our honest programs; default gen_<tag>.jsonl")
    ap.add_argument("--passf", default=None, help="their test verdicts; default pass_<tag>.jsonl")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    pairs, models = build(args)
    n = len(pairs)
    print(f"{args.tag}: {n} problems (matches {args.sg_json}); generator {models}")

    fits, oof = {}, {}
    for h, a in CELLS:
        key = f"{h}__{a}"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ev = evaluate(pairs.rename(columns={h: "honest", a: "attack"})[
                ["problem_id", "honest", "attack"]], key)
        o = pd.DataFrame(ev["oof"]).set_index("problem_id").loc[pairs.problem_id]
        oof[key] = (o.score_honest.values, o.score_attack.values)
        fits[key] = {"fold_mean": ev["auroc"], "fold_sd": ev["auroc_sd"],
                     "pooled": ev["auroc_pooled_oof"], "pooled_ci95_evaluate": ev["auroc_ci95_boot"],
                     "pairwise_acc": ev["pairwise_acc"], "length_only_auroc": ev["length_only_auroc"]}

    rng = np.random.RandomState(SEED)
    boot = {k: [] for k in oof}
    for _ in range(N_BOOT):
        idx = rng.randint(0, n, n)
        for k, (sh, sa) in oof.items():
            boot[k].append(_auroc(sh[idx], sa[idx]))
    boot = {k: np.array(v) for k, v in boot.items()}
    for k in fits:
        fits[k]["pooled_ci95_joint"] = _pct(boot[k])

    B, S = "human_honest__stored_attack", "our_honest__our_attack"
    X, G = "human_honest__our_attack", "our_honest__stored_attack"
    diffs = {"Bprime_minus_human_ours": (B, X), "human_ours_minus_S": (X, S),
             "Bprime_minus_ours_stored": (B, G), "ours_stored_minus_S": (G, S)}
    diff_out = {k: {"point": fits[x]["pooled"] - fits[y]["pooled"], "ci95": _pct(boot[x] - boot[y])}
                for k, (x, y) in diffs.items()}

    sg = json.load(open(args.sg_json))
    check = {"S_pooled_in_json": sg["S"]["auroc_pooled_oof"],
             "B_prime_pooled_in_json": sg["B_prime"]["auroc_pooled_oof"],
             "S_reproduced": abs(fits[S]["pooled"] - sg["S"]["auroc_pooled_oof"]) < 1e-9,
             "B_prime_reproduced": abs(fits[B]["pooled"] - sg["B_prime"]["auroc_pooled_oof"]) < 1e-9}

    print(f"\n  {'':14s} {'stored attack':>26s} {'our attack':>26s}   (pooled OOF AUROC, joint 95% CI)")
    for h in ("human_honest", "our_honest"):
        c = [f"{fits[f'{h}__{a}']['pooled']:.4f} ({fits[f'{h}__{a}']['pooled_ci95_joint'][0]:.4f}-"
             f"{fits[f'{h}__{a}']['pooled_ci95_joint'][1]:.4f})" for a in ("stored_attack", "our_attack")]
        print(f"  {h:14s} {c[0]:>26s} {c[1]:>26s}")
    for k, d in diff_out.items():
        print(f"  {k:26s} {d['point']:+.4f} ({d['ci95'][0]:+.4f} to {d['ci95'][1]:+.4f})")
    print(f"  check: S reproduces {args.sg_json}: {check['S_reproduced']}, "
          f"B' reproduces: {check['B_prime_reproduced']}")

    x, b, s = fits[X]["pooled"], fits[B]["pooled"], fits[S]["pooled"]
    nearer = "B'" if abs(x - b) < abs(x - s) else "S"
    print(f"\n{RULE}")
    print(f"  result: human honest vs our attacks = {x:.4f}; B' = {b:.4f}, S = {s:.4f}; "
          f"nearer {nearer} (B' minus this cell {b - x:+.4f}, this cell minus S {x - s:+.4f}; "
          f"paired intervals above)")

    out = {"tag": args.tag, "generator": models, "sg_json": args.sg_json, "bd": args.bd,
           "bdpass": args.bdpass, "n_problems": n, "n_boot": N_BOOT, "seed": SEED,
           "cells": fits, "differences": diff_out, "check_against_sg_json": check,
           "reading_rule": RULE, "nearer": nearer}
    path = args.out or f"classifier_swap_{args.tag}.json"
    json.dump(out, open(path, "w"), indent=2, default=float)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
