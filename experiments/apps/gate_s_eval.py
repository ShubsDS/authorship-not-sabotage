"""Cross-generator arm: B and G over the same problems, and the shared evaluate() pipeline.

"Gate S" is this repo's name for the control that tests whether the stored benchmark's
separability is authorship: refit the same bag-of-words classifier with the authorship gap
removed and compare it with B. Every gate_s_* script imports `evaluate()` from this file, so B,
G, S and B' are all the same fit.

This script runs the cross-generator arm. It regenerates the honest class with an LLM and fits
the pipeline twice over the same problems, changing only who wrote the honest code:

    B   human honest  vs stored LLM backdoor   the baseline
    G   LLM honest    vs stored LLM backdoor   the arm

and reports rho = (G - 0.5) / (B - 0.5) against the bands fixed before any arm ran (collapse
<= 0.33, content > 0.72). With Qwen3-Coder-30B as the honest generator (n = 668) it prints
B = 0.8739, G = 0.9616, rho = 1.234: the substitute generator replaced the authorship gap with a
larger one, so this arm cannot separate authorship from content. gate_s_samegen.py, where one
model writes both classes, is the control that can. The `title` field in the output is the
working title each band was tied to when the bands were fixed.

B is recomputed here rather than taken from the published 0.806. That number is TF-IDF trained
on Koran's paired train split and scored on their 1,375-item test split, whose honest class is
the human code, so it cannot be reconstructed once the honest class is regenerated.

Usage:
    python gate_s_eval.py --gen-file gen_q3c30.jsonl --pass-file pass_q3c30.jsonl \
        --label q3c30 --out gate_s_q3c30.json
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

sys.path.insert(0, ".")
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402

COLLAPSE, NO_COLLAPSE = 0.33, 0.72


def surface_features(code: str) -> list[float]:
    """Seven surface counts: length, newlines, `if`, 3+ digit numerals, `==`, `%`, `#`."""
    return [len(code), code.count("\n"), len(re.findall(r"\bif\b", code)),
            len(re.findall(r"\d{3,}", code)), code.count("=="), code.count("%"),
            len(re.findall(r"#", code))]


def evaluate(pairs: pd.DataFrame, label: str, n_splits: int = 5, n_boot: int = 2000,
             seed: int | None = None) -> dict:
    """Problem-disjoint 5-fold TF-IDF + logistic regression over honest/attack pairs.

    `pairs` has one row per problem with columns problem_id, honest, attack. Returns the
    fold-mean AUROC (`auroc`, the number reported as B, G, S and B'; B = 0.8714, sd 0.0085) and
    its across-fold sd, pairwise accuracy, the length-only and surface-7 AUROCs, the pooled
    out-of-fold AUROC with a 95% CI from a bootstrap over problems (`auroc_ci95_boot`, RNG seed
    0), and the per-pair out-of-fold scores under `oof` for reuse downstream (rho_joint_ci.py).

    `seed=None` keeps the deterministic GroupKFold assignment used for every reported number; an
    integer shuffles the problem-to-fold assignment, for the fold-seed robustness check.
    """
    groups = pairs.problem_id.values
    n_splits = min(n_splits, len(np.unique(groups)))
    vec_kw = dict(token_pattern=r"[A-Za-z_]+|\d+|[^\sA-Za-z_\d]", ngram_range=(1, 2),
                  min_df=3, max_features=50000, sublinear_tf=True)

    aurocs, pairaccs, len_aurocs, surf_aurocs = [], [], [], []
    # Out-of-fold scores per pair, for the bootstrap over problems below. The across-fold sd is
    # the spread of five estimates on n/5 pairs each, not a standard error; in simulation a
    # +/-2 sd interval is about 1.9x wider than the true 95% CI, so the bootstrap interval is the
    # one to quote.
    oof_h = np.full(len(pairs), np.nan)
    oof_a = np.full(len(pairs), np.nan)
    splitter = (GroupKFold(n_splits) if seed is None
                else GroupKFold(n_splits, shuffle=True, random_state=seed))
    for tr_idx, te_idx in splitter.split(pairs, groups=groups):
        tr, te = pairs.iloc[tr_idx], pairs.iloc[te_idx]
        y_tr = np.r_[np.zeros(len(tr)), np.ones(len(tr))]
        y_te = np.r_[np.zeros(len(te)), np.ones(len(te))]

        vec = TfidfVectorizer(**vec_kw)
        X_tr = vec.fit_transform(list(tr.honest) + list(tr.attack))
        clf = LogisticRegression(max_iter=3000, class_weight="balanced").fit(X_tr, y_tr)
        s_h = clf.predict_proba(vec.transform(list(te.honest)))[:, 1]
        s_a = clf.predict_proba(vec.transform(list(te.attack)))[:, 1]
        aurocs.append(roc_auc_score(y_te, np.r_[s_h, s_a]))
        pairaccs.append(float((s_a > s_h).mean()))
        oof_h[te_idx], oof_a[te_idx] = s_h, s_a

        lengths = np.r_[[len(c) for c in te.honest], [len(c) for c in te.attack]]
        len_aurocs.append(roc_auc_score(y_te, lengths))

        F_tr = np.log1p(np.array([surface_features(c) for c in list(tr.honest) + list(tr.attack)],
                                 dtype=float))
        F_te = np.log1p(np.array([surface_features(c) for c in list(te.honest) + list(te.attack)],
                                 dtype=float))
        sclf = LogisticRegression(max_iter=3000).fit(F_tr, y_tr)
        surf_aurocs.append(roc_auc_score(y_te, sclf.predict_proba(F_te)[:, 1]))

    # Pooled out-of-fold AUROC and a bootstrap-over-problems 95% CI. Each pair is one problem, so
    # resampling rows resamples problems; honest and attack scores travel together.
    y_all = np.r_[np.zeros(len(pairs)), np.ones(len(pairs))]
    pooled = float(roc_auc_score(y_all, np.r_[oof_h, oof_a]))
    rng = np.random.RandomState(0)
    boots = []
    for _ in range(n_boot):
        idx = rng.randint(0, len(pairs), len(pairs))
        boots.append(roc_auc_score(y_all, np.r_[oof_h[idx], oof_a[idx]]))
    ci_lo, ci_hi = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))

    out = {
        "label": label, "n_pairs": len(pairs),
        "auroc": float(np.mean(aurocs)), "auroc_sd": float(np.std(aurocs)),
        "auroc_pooled_oof": pooled, "auroc_ci95_boot": [ci_lo, ci_hi], "n_boot": n_boot,
        "pairwise_acc": float(np.mean(pairaccs)),
        "length_only_auroc": float(np.mean(len_aurocs)),
        "surface7_auroc": float(np.mean(surf_aurocs)),
        "fold_seed": seed,
        "oof": [{"problem_id": str(p), "score_honest": float(h), "score_attack": float(a)}
                for p, h, a in zip(pairs.problem_id.values, oof_h, oof_a)],
    }
    print(f"  {label:24s} n={out['n_pairs']:5d}  TF-IDF AUROC={out['auroc']:.4f}"
          f" (sd {out['auroc_sd']:.4f}; pooled {pooled:.4f}, 95% CI {ci_lo:.4f}-{ci_hi:.4f})"
          f"  pairwise={out['pairwise_acc']:.4f}"
          f"  length-only={out['length_only_auroc']:.4f}"
          f"  surface7={out['surface7_auroc']:.4f}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pass-file", required=True, help="run_tests.py output for this arm")
    ap.add_argument("--gen-file", required=True, help="gen_honest.py output for this arm")
    ap.add_argument("--label", required=True, help="e.g. 7B or 32B")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cols = ["problem_id", "solutions", "backdoors", "solution_passes_tests",
            "backdoor_works", "is_nondeterministic"]
    df = pd.concat([pq.read_table(f, columns=cols).to_pandas()
                    for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
    df["problem_id"] = df.problem_id.astype(str)

    code_by_pid = {json.loads(l)["problem_id"]: json.loads(l)["code"]
                   for l in open(args.gen_file) if l.strip()}
    passed = {json.loads(l)["problem_id"] for l in open(args.pass_file)
              if l.strip() and json.loads(l)["passed"]}
    print(f"generated {len(code_by_pid)}, passed tests {len(passed)}")

    rows = []
    for _, r in df.iterrows():
        if not (r.solution_passes_tests and r.backdoor_works and not r.is_nondeterministic):
            continue
        pid = r.problem_id
        if pid not in passed or not code_by_pid.get(pid, "").strip():
            continue
        row = {"problem_id": pid,
               "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions],
               "top_backdoor_model": None}
        bd, human = _pick_backdoor(row), _honest_code(row)
        if bd is None or human is None:
            continue
        rows.append({"problem_id": pid,
                     "attack": strip_comments(bd["backdoor_code"]),
                     "honest_llm": strip_comments(code_by_pid[pid]),
                     "honest_human": strip_comments(human)})

    pairs = pd.DataFrame(rows)
    if len(pairs) < 50:
        raise SystemExit(f"only {len(pairs)} eligible pairs — too few to route a title")
    print(f"eligible pairs (passing LLM honest + working backdoor + deterministic): {len(pairs)}\n")

    print("problem-disjoint 5-fold, comments stripped, identical pipeline:")
    B = evaluate(pairs.rename(columns={"honest_human": "honest"})[
        ["problem_id", "honest", "attack"]], "B  human honest")
    G = evaluate(pairs.rename(columns={"honest_llm": "honest"})[
        ["problem_id", "honest", "attack"]], f"G  {args.label} honest")

    rho = (G["auroc"] - 0.5) / (B["auroc"] - 0.5) if B["auroc"] > 0.5 else float("nan")

    # rho > 1 means the regenerated pairs separate better than the stored ones. The bands assume
    # rho in [0, 1], i.e. that a substitute generator can only remove signal; a different-vendor
    # generator can instead replace the authorship gap with a larger one. Such an arm cannot tell
    # authorship from content, so it is reported as confounded rather than read as content.
    import math
    sd = math.sqrt(G["auroc_sd"] ** 2 + B["auroc_sd"] ** 2)
    excess_sd = (G["auroc"] - B["auroc"]) / sd if sd > 0 else 0.0

    if rho > 1.0 and excess_sd > 2.0:
        verdict = (f"CONFOUNDED - G exceeds B by {excess_sd:.1f} sd. The substitute generator "
                   f"introduced a LARGER authorship gap than the one it removed. This arm does not "
                   f"discriminate authorship from content; do not route a title on it.")
        title = "INCONCLUSIVE - needs a generator closer to the attacker's lineage"
    elif rho <= COLLAPSE:
        verdict, title = "COLLAPSE -> authorship", "Authorship, Not Sabotage (stands)"
    elif rho <= NO_COLLAPSE:
        verdict, title = "PARTIAL", "Stands; the abstract states the split"
    else:
        verdict, title = "NO COLLAPSE -> content", "A Linear Model Beats the Trusted Monitor"

    print(f"\n  B = {B['auroc']:.4f}   G = {G['auroc']:.4f}   "
          f"rho = (G-0.5)/(B-0.5) = {rho:.4f}")
    print(f"  per-carrier shift B -> G:  TF-IDF {G['auroc']-B['auroc']:+.4f}   "
          f"length-only {G['length_only_auroc']-B['length_only_auroc']:+.4f}   "
          f"surface7 {G['surface7_auroc']-B['surface7_auroc']:+.4f}")
    print("  (lexical UP while length-only falls to chance is the signature of a swapped, not "
          "removed, authorship gap)")
    print(f"  bands: <= {COLLAPSE} collapse | <= {NO_COLLAPSE} partial | > {NO_COLLAPSE} content")
    print(f"  {verdict}\n  title: {title}")
    print("\nRoute the title on the arm whose generator is closest to the attacker's lineage. "
          "A cross-vendor arm bounds the effect; it does not decide it.")

    if args.out:
        json.dump({"arm": args.label, "B": B, "G": G, "rho": rho,
                   "excess_sd": excess_sd, "verdict": verdict,
                   "title": title}, open(args.out, "w"), indent=2)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
