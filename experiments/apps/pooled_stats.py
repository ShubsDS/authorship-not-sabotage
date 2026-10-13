"""Pooled out-of-fold S, B' and rho for every same-generator point the paper quotes.

The ledger values behind the paper's macros are fold means: `evaluate()` (gate_s_eval.py) fits 5
problem-disjoint folds and reports the mean of the five per-fold AUROCs as `auroc`. Their
intervals are a different quantity, the bootstrap over problems of the pooled out-of-fold AUROC
(one AUROC over all out-of-fold scores, `auroc_pooled_oof`). The camera-ready convention is that
every point is the pooled out-of-fold AUROC and every interval is the bootstrap over problems of
that same quantity. This script reads the committed jsons and gives each point both ways.

Methods, all fixed:

  * Table 1 rows (and every other S/B' pair whose json carries per-pair `oof` scores): S, B' and
    rho = (S - 0.5)/(B' - 0.5) from the pooled out-of-fold scores, with the joint bootstrap of
    rho_joint_ci.joint_bootstrap() (imported): one problem set resampled per draw, both AUROCs
    recomputed on it, 2,000 draws, numpy RandomState(0), one randint(0, n, n) per draw, problems
    in the order of S's `oof` intersected with B''s. P(rho > 0.72) and P(rho <= 0.33) are the
    shares of draws above the content line and at or below the collapse line.
  * Points whose json holds `auroc_pooled_oof` but no per-pair scores (edit arm, survivor check,
    prompt-only floors, learning curves): the stored pooled value; rho from the two pooled
    values; no joint interval (it needs per-pair scores).
  * --refit (needs train_*.parquet from fetch.py; public data, CPU): refits B over the 1,444-pair
    pool (gate_s_baseline.build_pairs + gate_s_eval.evaluate) and the learning-curve points at
    n = 623 and n = 99 (gate_s_learning_curve's draws: RandomState(0 + n), 30 subsamples, the
    shipped human pass flag), because gate_s_baseline.json and lc_*.json predate the pooled
    field or keep only its mean. The refit's fold means are checked against the committed ones.

`old` in the macro map is the macro's value in paper/main.tex at commit 1e05846 (the plan's
reference); `new` is the pooled counterpart. Points with no pooled counterpart in any committed
file are listed under `not_available` with the file that would give one. Four groups of points
whose inputs are generated files carry their pooled values in their own jsons, regenerated on
the cluster data, and are copied into the macro map from there (`pooled_elsewhere`): the
headline length-only AUROC (sg_indep_first_passes.json, gate_s_samegen.py), the Haiku 4.5
similarity strata (sim_strata_haiku45.json, sim_stratified_s.py), the one-sided arm
(gate_s_q3c30.json, gate_s_eval.py) and B under our pass flag (gate_s_baseline_ownflag.json,
gate_s_baseline.py --human-pass-file).

Inputs: sg_indep_first_passes_v2.json, sg_haiku45_indep_passes.json, sg_indep_best_usable_v2.json,
sg_indep_best_usable_seed{0..4}.json, sg_edit_passes.json, gate_s_matched_{headline,strict,
haiku45}.json, lexical_probe.json, survivor_check.json, lc_{first_passes,best_usable}.json,
headline_ci.json, sg_indep_first_passes.json, sim_strata_haiku45.json, gate_s_q3c30.json,
gate_s_baseline_ownflag.json; with --refit also train_*.parquet.

Usage:
    python pooled_stats.py --refit --out pooled_stats.json      # ~5 min with --refit
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rho_joint_ci import COLLAPSE, NO_COLLAPSE, _oof_frame, joint_bootstrap  # noqa: E402

N_BOOT, SEED = 2000, 0

# Table 1, in the paper's row order: (key, label, json, path to the block holding S and B_prime).
TABLE1 = [
    ("sonnet_headline", "Sonnet 5, headline", "sg_indep_first_passes_v2.json", []),
    ("haiku_headline", "Haiku 4.5, headline", "sg_haiku45_indep_passes.json", []),
    ("prompt_matched", "Sonnet 5, prompt-matched", "gate_s_matched_headline.json", ["S_matched"]),
    ("strict", "Sonnet 5, strict", "sg_indep_best_usable_v2.json", []),
    ("strict_matched", "Sonnet 5, strict, matched", "gate_s_matched_strict.json", ["S_matched"]),
]
# Other S/B' pairs that carry per-pair oof scores.
OTHER_JOINT = [
    ("haiku_prompt_matched", "Haiku 4.5, prompt-matched", "gate_s_matched_haiku45.json",
     ["S_matched"]),
    ("identifier_mask_headline", "Sonnet 5 headline, identifier mask", "lexical_probe.json",
     ["headline", "masking", "ID (structure only)"]),
    ("matched_identifier_mask", "Sonnet 5 prompt-matched, identifier mask",
     "gate_s_matched_headline.json", ["masked_ID", "S_matched"]),
    ("matched_identifier_mask_original_honest",
     "Sonnet 5 original honest on the matched problems, identifier mask",
     "gate_s_matched_headline.json", ["masked_ID", "S_original_same_problems"]),
    ("matched_char_ngram", "Sonnet 5 prompt-matched, char 3-5-grams",
     "gate_s_matched_headline.json", ["char_ngram_3_5", "S_matched"]),
]


def _dig(blob: dict, path: list) -> dict:
    for k in path:
        blob = blob[k]
    return blob


def _quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return fn(*a, **kw)


def joint_row(key: str, label: str, path: str, block: list) -> dict:
    blk = _dig(json.load(open(path)), block)
    S, B = blk["S"], blk["B_prime"]
    jb = joint_bootstrap(_oof_frame(S), _oof_frame(B), N_BOOT, SEED)
    fm_rho = (S["auroc"] - 0.5) / (B["auroc"] - 0.5)
    return {
        "label": label, "source": path + "".join(f"[{b}]" for b in block),
        "n": jb["n_common_problems"],
        "fold_mean": {"S": S["auroc"], "B_prime": B["auroc"], "rho": fm_rho},
        "pooled": {"S": jb["S_pooled_oof"], "B_prime": jb["B_prime_pooled_oof"],
                   "rho": jb["rho_point_pooled_oof"]},
        "S_ci95": jb["S_ci95"], "B_prime_ci95": jb["B_prime_ci95"],
        "rho_ci95_joint": jb["rho_ci95_joint"],
        "P_rho_gt_0.72": jb["P_rho_gt_content"], "P_rho_le_0.33": jb["P_rho_le_collapse"],
        "P_rho_ge_1": jb["P_rho_ge_1"],
        # The json's own S interval (gate_s_eval.evaluate's bootstrap); identical to S_ci95 when
        # the problem order coincides, as a check that nothing drifted.
        "S_ci95_in_json": S["auroc_ci95_boot"],
    }


def pooled_only(S: dict, B: dict | None, label: str, source: str) -> dict:
    out = {"label": label, "source": source, "n": S["n_pairs"],
           "fold_mean": {"S": S["auroc"]}, "pooled": {"S": S["auroc_pooled_oof"]},
           "S_ci95": S["auroc_ci95_boot"]}
    if B is not None:
        out["fold_mean"]["B_prime"] = B["auroc"]
        out["fold_mean"]["rho"] = (S["auroc"] - 0.5) / (B["auroc"] - 0.5)
        out["pooled"]["B_prime"] = B["auroc_pooled_oof"]
        out["pooled"]["rho"] = (S["auroc_pooled_oof"] - 0.5) / (B["auroc_pooled_oof"] - 0.5)
        out["B_prime_ci95"] = B["auroc_ci95_boot"]
        out["rho_ci95_joint"] = None
        out["note"] = "no per-pair oof scores in the json, so no joint interval on rho"
    return out


def refit(lc_head: dict, lc_strict: dict) -> dict:
    """B over the 1,444-pair pool and the learning-curve points at n = 623 and 99, pooled."""
    from gate_s_eval import evaluate
    from gate_s_learning_curve import load_pool

    if not glob.glob("train_*.parquet"):
        raise SystemExit("--refit needs train_*.parquet here - run `python fetch.py` first")
    pairs = _quiet(load_pool, None)
    B = _quiet(evaluate, pairs, "B  human honest")
    out = {"B": {"n": B["n_pairs"], "fold_mean": B["auroc"], "fold_sd": B["auroc_sd"],
                 "pooled": B["auroc_pooled_oof"], "pooled_ci95": B["auroc_ci95_boot"],
                 "collapse_line_pooled": 0.5 + COLLAPSE * (B["auroc_pooled_oof"] - 0.5),
                 "content_line_pooled": 0.5 + NO_COLLAPSE * (B["auroc_pooled_oof"] - 0.5)}}
    print(f"  B over {B['n_pairs']}: fold mean {B['auroc']:.4f}  pooled {B['auroc_pooled_oof']:.4f}"
          f" ({B['auroc_ci95_boot'][0]:.4f}-{B['auroc_ci95_boot'][1]:.4f})")

    # gate_s_learning_curve.curve_point's draws, restated so the per-draw pooled values are kept.
    for name, lc, n in (("curve_headline", lc_head, 623), ("curve_strict", lc_strict, 99)):
        rng = np.random.RandomState(lc["seed"] + n)
        runs = []
        for _ in range(lc["draws"]):
            idx = rng.choice(len(pairs), size=n, replace=False)
            sub = pairs.iloc[np.sort(idx)].reset_index(drop=True)
            runs.append(_quiet(evaluate, sub, f"B n={n}", n_boot=lc["n_boot"]))
        fm = np.array([r["auroc"] for r in runs])
        po = np.array([r["auroc_pooled_oof"] for r in runs])
        ref = next(p for p in lc["points"] if p["n"] == n)
        out[name] = {"n": n, "draws": lc["draws"],
                     "fold_mean_mean": float(fm.mean()), "fold_mean_sd": float(fm.std()),
                     "pooled_mean": float(po.mean()), "pooled_sd": float(po.std()),
                     "committed_fold_mean_mean": ref["auroc_mean"],
                     "committed_pooled_mean": ref["auroc_pooled_oof_mean"],
                     "reproduces_committed": bool(abs(fm.mean() - ref["auroc_mean"]) < 1e-9
                                                  and abs(po.mean() - ref["auroc_pooled_oof_mean"])
                                                  < 1e-9)}
        print(f"  B at n={n}: fold mean {fm.mean():.4f} +/- {fm.std():.4f}   "
              f"pooled {po.mean():.4f} +/- {po.std():.4f}   "
              f"(committed {ref['auroc_mean']:.4f}; reproduces: {out[name]['reproduces_committed']})")
    import pandas as pd
    import sklearn
    out["sklearn"], out["pandas"] = sklearn.__version__, pd.__version__
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refit", action="store_true",
                    help="also refit B and the n = 623 / 99 learning-curve points (needs parquet)")
    ap.add_argument("--out", default="pooled_stats.json")
    args = ap.parse_args()

    out = {"convention": "point = pooled out-of-fold AUROC; interval = bootstrap over problems "
                         "of that same quantity; rho interval = joint bootstrap of S and B'",
           "n_boot": N_BOOT, "seed": SEED, "bands": {"collapse_le": COLLAPSE,
                                                     "content_gt": NO_COLLAPSE}}

    print("Table 1 (pooled out-of-fold; joint bootstrap 2,000 draws, seed 0)")
    print(f"  {'row':28s} {'n':>4s} {'S':>7s} {'B_prime':>8s} {'rho':>7s} {'rho 95% CI':>16s}"
          f" {'P>0.72':>7s} {'P<=0.33':>8s}   fold-mean S / B' / rho")
    rows = {}
    for key, label, path, block in TABLE1 + OTHER_JOINT:
        r = joint_row(key, label, path, block)
        rows[key] = r
        p, f = r["pooled"], r["fold_mean"]
        print(f"  {label[:28]:28s} {r['n']:4d} {p['S']:7.4f} {p['B_prime']:8.4f} {p['rho']:7.3f}"
              f"  {r['rho_ci95_joint'][0]:6.3f}-{r['rho_ci95_joint'][1]:6.3f}"
              f" {r['P_rho_gt_0.72']:7.3f} {r['P_rho_le_0.33']:8.3f}"
              f"   {f['S']:.4f} / {f['B_prime']:.4f} / {f['rho']:.3f}")
        if key == "haiku_prompt_matched":
            print("  -- other points with per-pair oof scores --")
    out["table1"] = {k: rows[k] for k, *_ in TABLE1}
    out["other_joint"] = {k: rows[k] for k, *_ in OTHER_JOINT}

    # ---- points with a stored pooled value but no per-pair scores ---------------------------
    edit = json.load(open("sg_edit_passes.json"))
    mh = json.load(open("gate_s_matched_headline.json"))
    mk = json.load(open("gate_s_matched_haiku45.json"))
    sv = json.load(open("survivor_check.json"))
    po = {
        "edit_arm": pooled_only(edit["S"], edit["B_prime"], "edit arm",
                                "sg_edit_passes.json"),
        "prompt_only_sonnet": pooled_only(mh["prompt_only"]["S"], None,
                                          "prompt-only floor, Sonnet 5",
                                          "gate_s_matched_headline.json[prompt_only]"),
        "prompt_only_haiku": pooled_only(mk["prompt_only"]["S"], None,
                                         "prompt-only floor, Haiku 4.5",
                                         "gate_s_matched_haiku45.json[prompt_only]"),
        "survivor_swap_S": pooled_only(sv["d_S_inert_same_problems"], None,
                                       "S with non-firing attempts on the strict problems",
                                       "survivor_check.json[d_S_inert_same_problems]"),
        "survivor_swap_Sref": pooled_only(sv["d_strict_S_same_subset"], None,
                                          "strict S on the same 98 problems",
                                          "survivor_check.json[d_strict_S_same_subset]"),
        "survivor_auroc": {"label": "survivors vs non-survivors (attack side)",
                           "source": "survivor_check.json[a_attack_surv_vs_nonsurv]",
                           "fold_mean": {"S": sv["a_attack_surv_vs_nonsurv"]["auroc"]},
                           "pooled": {"S": sv["a_attack_surv_vs_nonsurv"]["auroc_pooled_oof"]},
                           "S_ci95": sv["a_attack_surv_vs_nonsurv"]["auroc_ci95_boot"]},
    }
    hc = json.load(open("headline_ci.json"))
    nocode = next(f for f in hc["floors"] if f.get("protocol") == "5x5 CV within test")
    po["nocode_cv"] = {"label": "no-code floor, 5x5 CV within the test split",
                       "source": "headline_ci.json[floors, protocol '5x5 CV within test']",
                       # key renamed to fold_mean when headline_ci.py moved to 1,000 permutations
                       "fold_mean": {"S": nocode.get("fold_mean",
                                                     nocode.get("headline_fold_mean"))},
                       "pooled": {"S": nocode["auroc"]}, "S_ci95": nocode["ci95"],
                       "above_n_of_24_pooled": nocode["above_n_of_24_point_estimates"]}
    lc_h, lc_s = json.load(open("lc_first_passes.json")), json.load(open("lc_best_usable.json"))
    for name, lc, n in (("curve_headline", lc_h, 623), ("curve_strict", lc_s, 99)):
        pt = next(p for p in lc["points"] if p["n"] == n)
        po[name] = {"label": f"B at matched n = {n}, mean of {pt['draws']} subsamples",
                    "source": f"{'lc_first_passes.json' if n == 623 else 'lc_best_usable.json'}"
                              f"[points n={n}]",
                    "fold_mean": {"mean": pt["auroc_mean"], "sd": pt["auroc_sd"]},
                    "pooled": {"mean": pt["auroc_pooled_oof_mean"], "sd": None},
                    "note": "the json keeps the pooled mean but not its sd; --refit gives it"}
    out["pooled_only"] = po

    # ---- strict row under five fold seeds -------------------------------------------------
    seeds = {}
    for k in range(5):
        path = f"sg_indep_best_usable_seed{k}.json"
        r = joint_row(f"seed{k}", f"strict, fold seed {k}", path, [])
        seeds[k] = {"fold_mean_rho": r["fold_mean"]["rho"], "pooled_rho": r["pooled"]["rho"],
                    "pooled_S": r["pooled"]["S"], "pooled_B_prime": r["pooled"]["B_prime"],
                    "rho_ci95_joint": r["rho_ci95_joint"]}
    fm = [v["fold_mean_rho"] for v in seeds.values()]
    pr = [v["pooled_rho"] for v in seeds.values()]
    out["strict_fold_seeds"] = {"per_seed": seeds,
                                "fold_mean_rho_range": [min(fm), max(fm)],
                                "pooled_rho_range": [min(pr), max(pr)],
                                "note": "seeds 0-4 shuffle the problem-to-fold assignment; the "
                                        "default unshuffled split is the Table 1 strict row"}
    print(f"\nstrict row, fold seeds 0-4: fold-mean rho {min(fm):.3f}-{max(fm):.3f}; "
          f"pooled rho {min(pr):.3f}-{max(pr):.3f}")

    if args.refit:
        print("\nrefits (public data):")
        out["refit"] = refit(lc_h, lc_s)

    # ---- macro map --------------------------------------------------------------------------
    t, o = out["table1"], out["other_joint"]
    M = {}

    def put(macro, old, new, source, note=None):
        M[macro] = {"old": old, "new": new, "source": source}
        if note:
            M[macro]["note"] = note

    for pre, key in (("sameGen", "sonnet_headline"), ("haiku", "haiku_headline"),
                     ("matched", "prompt_matched"), ("strict", "strict"),
                     ("matchedStrict", "strict_matched")):
        r = t[key]
        src = r["source"]
        S_macro = {"sameGen": "sameGenS", "haiku": "haikuS", "matched": "matchedS",
                   "strict": "strictS", "matchedStrict": "matchedStrictS"}[pre]
        old = {"sameGenS": "0.7512", "haikuS": "0.5340", "matchedS": "0.6423",
               "strictS": "0.7652", "matchedStrictS": "0.7113"}[S_macro]
        put(f"\\{S_macro}", old, f"{r['pooled']['S']:.4f}", src)
        oldb = {"sameGen": "0.8658", "haiku": "0.8584", "matched": "0.8613", "strict": "0.7877",
                "matchedStrict": "0.8030"}[pre]
        put(f"\\{pre}Bprime", oldb, f"{r['pooled']['B_prime']:.4f}", src)
        rho_macro = {"sameGen": "sameGenRho", "haiku": "haikuRho", "matched": "matchedRho",
                     "strict": "strictRho", "matchedStrict": "matchedStrictRho"}[pre]
        oldr = {"sameGenRho": "0.687", "haikuRho": "0.095", "matchedRho": "0.394",
                "strictRho": "0.921", "matchedStrictRho": "0.697"}[rho_macro]
        put(f"\\{rho_macro}", oldr, f"{r['pooled']['rho']:.3f}", src)
        lo_hi = {"sameGen": ("sameGenRhoLo", "sameGenRhoHi", "0.625", "0.755"),
                 "haiku": ("haikuRhoLo", "haikuRhoHi", "0.044", "0.150"),
                 "matched": ("matchedRhoLo", "matchedRhoHi", "0.326", "0.454"),
                 "strict": ("strictRhoLo", "strictRhoHi", "0.662", "1.089"),
                 "matchedStrict": ("matchedStrictRhoLo", "matchedStrictRhoHi", "0.494", "0.856")}
        a, b, ol, oh = lo_hi[pre]
        put(f"\\{a}", ol, f"{r['rho_ci95_joint'][0]:.3f}", src, "unchanged: already the joint "
            "bootstrap of the pooled rho")
        put(f"\\{b}", oh, f"{r['rho_ci95_joint'][1]:.3f}", src)
        s_ci = {"sameGen": ("sameGenLo", "sameGenHi", "0.7295", "0.7713"),
                "haiku": ("haikuSLo", "haikuSHi", "0.5159", "0.5531"),
                "matched": ("matchedLo", "matchedHi", "0.6179", "0.6621"),
                "strict": ("strictLo", "strictHi", "0.7016", "0.8000"),
                "matchedStrict": ("matchedStrictLo", "matchedStrictHi", "0.6464", "0.7453")}
        a, b, ol, oh = s_ci[pre]
        put(f"\\{a}", ol, f"{r['S_ci95'][0]:.4f}", src, "unchanged: already the bootstrap of the "
            "pooled S")
        put(f"\\{b}", oh, f"{r['S_ci95'][1]:.4f}", src)
    put("\\strictRhoPooled", "0.86", f"{t['strict']['pooled']['rho']:.3f}",
        t["strict"]["source"], "becomes \\strictRho under the new convention")
    put("\\matchedRhoPooled", "0.390", f"{t['prompt_matched']['pooled']['rho']:.3f}",
        t["prompt_matched"]["source"], "becomes \\matchedRho under the new convention")
    put("\\matchedStrictRhoPooled", "0.662", f"{t['strict_matched']['pooled']['rho']:.3f}",
        t["strict_matched"]["source"], "becomes \\matchedStrictRho under the new convention")
    put("\\haikuRhoPooled", "0.097", f"{t['haiku_headline']['pooled']['rho']:.3f}",
        t["haiku_headline"]["source"], "becomes \\haikuRho under the new convention")
    r = o["haiku_prompt_matched"]
    put("\\haikuSMatched", "0.5399", f"{r['pooled']['S']:.4f}", r["source"])
    put("\\haikuMatchedRho", "0.113", f"{r['pooled']['rho']:.3f}", r["source"],
        f"joint CI {r['rho_ci95_joint'][0]:.3f}-{r['rho_ci95_joint'][1]:.3f}")
    r = o["identifier_mask_headline"]
    put("\\sameGenSid", "0.700", f"{r['pooled']['S']:.3f}", r["source"])
    put("\\sameGenRhoId", "0.54", f"{r['pooled']['rho']:.2f}", r["source"],
        f"pooled {r['pooled']['rho']:.4f}, joint CI {r['rho_ci95_joint'][0]:.3f}-"
        f"{r['rho_ci95_joint'][1]:.3f}")
    r = o["matched_identifier_mask"]
    put("\\matchedSid", "0.6264", f"{r['pooled']['S']:.4f}", r["source"])
    put("\\matchedRhoId", "0.342", f"{r['pooled']['rho']:.3f}", r["source"])
    put("\\matchedRhoIdLo", "0.280", f"{r['rho_ci95_joint'][0]:.3f}", r["source"],
        "unchanged: already pooled")
    put("\\matchedRhoIdHi", "0.394", f"{r['rho_ci95_joint'][1]:.3f}", r["source"])
    put("\\matchedRhoIdCollapse", "40\\%", f"{100 * r['P_rho_le_0.33']:.0f}\\%", r["source"],
        "P(rho <= 0.33) under the joint bootstrap; unchanged")
    r = o["matched_identifier_mask_original_honest"]
    put("\\matchedSidOrig", "0.7046", f"{r['pooled']['S']:.4f}", r["source"])
    r = o["matched_char_ngram"]
    put("\\matchedChar", "0.6817", f"{r['pooled']['S']:.4f}", r["source"])
    put("\\matchedRhoChar", "0.493", f"{r['pooled']['rho']:.3f}", r["source"])
    r = po["edit_arm"]
    put("\\editS", "0.6266", f"{r['pooled']['S']:.4f}", r["source"])
    put("\\editRho", "0.371", f"{r['pooled']['rho']:.3f}", r["source"], r["note"])
    r = po["prompt_only_sonnet"]
    put("\\promptOnly", "0.6006", f"{r['pooled']['S']:.4f}", r["source"],
        "\\promptOnlyLo/Hi (0.5768-0.6243) are already the pooled bootstrap; unchanged")
    r = po["prompt_only_haiku"]
    put("\\haikuPromptFloor", "0.4918", f"{r['pooled']['S']:.4f}", r["source"],
        f"pooled CI {r['S_ci95'][0]:.4f}-{r['S_ci95'][1]:.4f}")
    put("\\survivorSwapS", "0.7595", f"{po['survivor_swap_S']['pooled']['S']:.4f}",
        po["survivor_swap_S"]["source"])
    put("\\survivorSwapSref", "0.7687", f"{po['survivor_swap_Sref']['pooled']['S']:.4f}",
        po["survivor_swap_Sref"]["source"])
    put("\\survivorAuroc", "0.62", f"{po['survivor_auroc']['pooled']['S']:.2f}",
        po["survivor_auroc"]["source"])
    put("\\nocodeCV", "0.772", f"{po['nocode_cv']['pooled']['S']:.3f}",
        po["nocode_cv"]["source"], "already in the paper as \\nocodeCVPooled")
    put("\\curveHeadline", "0.8521", f"{po['curve_headline']['pooled']['mean']:.4f}",
        po["curve_headline"]["source"])
    put("\\curveStrict", "0.7807", f"{po['curve_strict']['pooled']['mean']:.4f}",
        po["curve_strict"]["source"])
    s = out["strict_fold_seeds"]
    put("\\strictRhoSeeds", "0.85--0.92",
        f"{s['pooled_rho_range'][0]:.2f}--{s['pooled_rho_range'][1]:.2f}",
        "sg_indep_best_usable_seed{0..4}.json",
        f"pooled rho per seed {[round(v['pooled_rho'], 3) for v in s['per_seed'].values()]}")
    if args.refit:
        rf = out["refit"]
        put("\\curveHeadlineSd", "0.0055", f"{rf['curve_headline']['pooled_sd']:.4f}",
            "pooled_stats.py --refit (lc_first_passes.json draws)")
        put("\\curveStrictSd", "0.0248", f"{rf['curve_strict']['pooled_sd']:.4f}",
            "pooled_stats.py --refit (lc_best_usable.json draws)")
        put("\\baselineB", "0.871", f"{rf['B']['pooled']:.3f}",
            "pooled_stats.py --refit (gate_s_baseline.build_pairs + evaluate)",
            f"pooled {rf['B']['pooled']:.4f} ({rf['B']['pooled_ci95'][0]:.4f}-"
            f"{rf['B']['pooled_ci95'][1]:.4f}); fold mean {rf['B']['fold_mean']:.4f}")
        put("\\gCollapseMax", "0.6226", f"{rf['B']['collapse_line_pooled']:.4f}",
            "derived from the pooled B")
        put("\\gPartialMax", "0.7674", f"{rf['B']['content_line_pooled']:.4f}",
            "derived from the pooled B")
    # ---- points pooled in their own jsons (regenerated from the generated files) -----------
    hl = json.load(open("sg_indep_first_passes.json"))["S"]
    st = json.load(open("sim_strata_haiku45.json"))["range_over_strata"]
    q3 = json.load(open("gate_s_q3c30.json"))["pooled"]
    of = json.load(open("gate_s_baseline_ownflag.json"))["B_pooled"]
    rng2 = lambda v, d: f"{v[0]:.{d}f}--{v[1]:.{d}f}"
    put("\\sameGenLen", "0.5851", f"{hl['length_only_auroc_pooled']:.4f}",
        "sg_indep_first_passes.json[S][length_only_auroc_pooled]",
        f"pooled over all pairs (length is not fitted); CI "
        f"{hl['length_only_ci95_boot'][0]:.4f}-{hl['length_only_ci95_boot'][1]:.4f}")
    put("\\haikuStrataS", "0.4737--0.5142", rng2(st["pooled"]["S"], 4),
        "sim_strata_haiku45.json[range_over_strata][pooled][S]", "min-max over the four strata")
    put("\\haikuStrataBprime", "0.7884--0.8334", rng2(st["pooled"]["B_prime"], 4),
        "sim_strata_haiku45.json[range_over_strata][pooled][B_prime]",
        "min-max over the four strata")
    put("\\haikuStrataLowSim", "0.451", f"{st['mean_sim_lowest_stratum']:.3f}",
        "sim_strata_haiku45.json[range_over_strata][mean_sim_lowest_stratum]",
        "mean pair similarity, not an AUROC; unchanged")
    put("\\armOneBprime", "0.874", f"{q3['B']:.3f}", "gate_s_q3c30.json[pooled][B]",
        f"CI {q3['B_ci95'][0]:.4f}-{q3['B_ci95'][1]:.4f}")
    put("\\armOneG", "0.962", f"{q3['G']:.3f}", "gate_s_q3c30.json[pooled][G]",
        f"CI {q3['G_ci95'][0]:.4f}-{q3['G_ci95'][1]:.4f}")
    put("\\armOneRho", "1.234", f"{q3['rho']:.3f}", "gate_s_q3c30.json[pooled][rho]",
        f"joint CI {q3['rho_ci95_joint'][0]:.3f}-{q3['rho_ci95_joint'][1]:.3f}")
    put("\\armOneTfidfDelta", "+0.088", f"{q3['G_minus_B']:+.3f}",
        "gate_s_q3c30.json[pooled][G_minus_B]",
        f"paired CI {q3['G_minus_B_ci95'][0]:+.3f} to {q3['G_minus_B_ci95'][1]:+.3f}")
    put("\\armOneLenG", "0.489", f"{q3['length_only_G']:.3f}",
        "gate_s_q3c30.json[pooled][length_only_G]",
        f"CI {q3['length_only_G_ci95'][0]:.4f}-{q3['length_only_G_ci95'][1]:.4f}")
    put("\\baselineBownflag", "0.873", f"{of['auroc_pooled_oof']:.3f}",
        "gate_s_baseline_ownflag.json[B_pooled]",
        f"pooled {of['auroc_pooled_oof']:.4f} ({of['ci95_boot'][0]:.4f}-{of['ci95_boot'][1]:.4f}); "
        f"fold mean {of['fold_mean']:.4f}; n = {of['n_pairs']}")
    out["pooled_elsewhere"] = {
        "\\sameGenLen": "sg_indep_first_passes.json (gate_s_samegen.py)",
        "\\haikuStrataS, \\haikuStrataBprime": "sim_strata_haiku45.json (sim_stratified_s.py)",
        "\\armOneG, \\armOneBprime, \\armOneRho, \\armOneTfidfDelta, \\armOneLenG":
            "gate_s_q3c30.json (gate_s_eval.py)",
        "\\baselineBownflag": "gate_s_baseline_ownflag.json (gate_s_baseline.py "
                              "--human-pass-file pass_human_fixed.jsonl)",
    }

    out["macro_map"] = M
    out["not_available"] = {
        "edit-arm joint rho interval": "sg_edit_passes.json has pooled points but no per-pair "
                                       "oof; re-run gate_s_samegen.py for the edit arm",
        "\\curveHeadlineSd, \\curveStrictSd, \\baselineB": (
            "given by --refit (public data)" if args.refit else
            "not in the committed jsons; run with --refit"),
    }

    print("\nmacro map (old -> new):")
    for k, v in M.items():
        flag = "" if v["old"] == v["new"] else "   *"
        print(f"  {k:24s} {v['old']:>11s} -> {v['new']:>11s}{flag}")
    json.dump(out, open(args.out, "w"), indent=2, default=float)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
