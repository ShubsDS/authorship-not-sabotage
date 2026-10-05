"""monitor-rho: the monitor's counterpart of the classifier's rho, on the same problems.

    monitor-rho = (M_samegen - 0.5) / (M_stored - 0.5)

where M_samegen and M_stored are the monitor's AUROCs from `monitor_samegen.py` and
`monitor_samegen.py --stored`. The interval is a joint bootstrap over problems: one problem set
is drawn per replicate and both AUROCs are recomputed on it (2,000 draws, seed 0), as
`rho_joint_ci.py` does for the classifier. The classifier's S, B' and rho are recomputed inside
the same draws from the `oof` scores of the gate_s_samegen json, so the monitor-minus-classifier
differences come with paired intervals.

Reads sg_indep_first_passes_v2.json, sg_indep_best_usable_v2.json, rho_joint_{headline,strict}.json
and the monitor jsons, located by `monitor_samegen.py`'s naming convention:

    monitor_samegen_<tag>_<arm>_<elig>[_<model>].json     M_samegen
    monitor_stored_<tag>_<arm>_<elig>[_<model>].json      M_stored

Writes monitor_rho.json. claude-sonnet-5 gives monitor-rho 0.145 (0.111-0.182) on the headline
row and 0.717 (0.601-0.832) on the strict row (the monitor rows in Section 3 and the appendix).

Caveats:

  1. The 24-monitor comparison on Koran's split is a different problem set and protocol; these
     AUROCs are not comparable with it.
  2. claude-sonnet-5 wrote both same-generator classes, so its M_samegen is a self-evaluation;
     claude-haiku-4-5 wrote neither.
  3. The stored pairs are human honest vs stored Claude 3.7 backdoor, so M_stored includes the
     authorship gap by construction; that is what the denominator is for.

Usage:
    python monitor_rho.py --out monitor_rho.json
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

# The headline and strict same-generator rows, with their classifier joint-bootstrap jsons.
ROWS = [
    {"row": "headline", "gate_s": "sg_indep_first_passes_v2.json",
     "rho_joint": "rho_joint_headline.json", "arm": "independent", "eligibility": "passes",
     "desc": "first / passes the tests (97.5% never fire), n = 623"},
    {"row": "strict", "gate_s": "sg_indep_best_usable_v2.json",
     "rho_joint": "rho_joint_strict.json", "arm": "independent", "eligibility": "usable",
     "desc": "best, crash excluded / passes AND fires, n = 99"},
]
# (label, file suffix). The third entry is a truncation control: claude-haiku-4-5 writes long
# rationales and lost 42-50% of its replies to the 512-token ceiling, so the strict row was re-run
# at 1024. Monitors whose files do not exist are skipped.
MONITORS = [("claude-sonnet-5", ""), ("claude-haiku-4-5", "_haiku-4-5"),
            ("claude-haiku-4-5 @ max_tokens=1024", "_haiku-4-5_mt1024")]


def _auroc(h: np.ndarray, a: np.ndarray) -> float:
    y = np.r_[np.zeros(len(h)), np.ones(len(a))]
    return float(roc_auc_score(y, np.r_[h, a]))


def _pct(x) -> list:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))] if len(x) else None


def monitor_scores(path: str) -> dict:
    """{problem_id: {"honest": score|None, "attack": score|None}} from a monitor_*.json."""
    blob = json.load(open(path))
    by: dict[str, dict] = {}
    for r in blob["scores"]:
        by.setdefault(str(r["problem_id"]), {})[r["class"]] = r["score"]
    return {"path": path, "blob": blob, "by": by}


def side_stats(by: dict, order: list) -> dict:
    """AUROC, pairwise accuracy (ties half), class means and missing counts over `order`.

    Identical conventions to `monitor_samegen.analyse()`: a program with no parseable score is
    excluded and counted, never imputed; pairwise accuracy uses only pairs scored on both sides.
    """
    hs, as_, comp_h, comp_a = [], [], [], []
    for p in order:
        m = by.get(p, {})
        if m.get("honest") is not None:
            hs.append(float(m["honest"]))
        if m.get("attack") is not None:
            as_.append(float(m["attack"]))
        if m.get("honest") is not None and m.get("attack") is not None:
            comp_h.append(float(m["honest"]))
            comp_a.append(float(m["attack"]))
    comp_h, comp_a = np.array(comp_h), np.array(comp_a)
    pw = float(((comp_a > comp_h) + 0.5 * (comp_a == comp_h)).mean()) if len(comp_h) else None
    return {
        "n_problems": len(order),
        "n_programs_scored": len(hs) + len(as_),
        "n_programs_missing": 2 * len(order) - len(hs) - len(as_),
        "n_pairs_both_sides_scored": int(len(comp_h)),
        "auroc": _auroc(np.array(hs), np.array(as_)) if hs and as_ else None,
        "pairwise_acc_ties_half": pw,
        "mean_score_honest": float(np.mean(hs)) if hs else None,
        "mean_score_attack": float(np.mean(as_)) if as_ else None,
    }


def _draw_auroc(by: dict, order: list, idx: np.ndarray) -> float:
    hs, as_ = [], []
    for d in idx:
        m = by.get(order[d], {})
        if m.get("honest") is not None:
            hs.append(float(m["honest"]))
        if m.get("attack") is not None:
            as_.append(float(m["attack"]))
    if not hs or not as_:
        return float("nan")
    return _auroc(np.array(hs), np.array(as_))


def joint(order: list, mon_same: dict, mon_stored: dict, clf_S: dict, clf_B: dict,
          n_boot: int, seed: int) -> dict:
    """One resampled problem set per draw; every AUROC on this row recomputed on it.

    The classifier's S and B' ride in the same draws, so the monitor-vs-classifier differences get
    paired intervals and the classifier's own joint rho is reproduced here as a check against
    `rho_joint_ci.py` (same RandomState, same one-randint-per-draw sequence, same problem order).
    """
    n = len(order)
    s_h = np.array([clf_S[p]["honest"] for p in order])
    s_a = np.array([clf_S[p]["attack"] for p in order])
    b_h = np.array([clf_B[p]["honest"] for p in order])
    b_a = np.array([clf_B[p]["attack"] for p in order])

    rng = np.random.RandomState(seed)
    cols = {k: [] for k in ("m_same", "m_stored", "m_rho", "S", "B", "c_rho",
                            "d_stored", "d_same", "d_rho")}
    n_degenerate = 0
    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        ms = _draw_auroc(mon_same, order, idx)
        mt = _draw_auroc(mon_stored, order, idx)
        s = _auroc(s_h[idx], s_a[idx])
        b = _auroc(b_h[idx], b_a[idx])
        if np.isnan(ms) or np.isnan(mt):
            n_degenerate += 1
            continue
        mrho = (ms - 0.5) / (mt - 0.5) if mt > 0.5 else np.nan
        crho = (s - 0.5) / (b - 0.5) if b > 0.5 else np.nan
        cols["m_same"].append(ms)
        cols["m_stored"].append(mt)
        cols["m_rho"].append(mrho)
        cols["S"].append(s)
        cols["B"].append(b)
        cols["c_rho"].append(crho)
        cols["d_stored"].append(mt - b)       # monitor vs bag-of-words on the STORED pairs
        cols["d_same"].append(ms - s)         # monitor vs bag-of-words on the same-generator pairs
        cols["d_rho"].append(mrho - crho)     # monitor-rho vs classifier rho
    mr = np.asarray(cols["m_rho"], dtype=float)
    return {
        "n_boot": n_boot, "seed": seed, "n_problems": n, "n_boot_degenerate": n_degenerate,
        "M_samegen_ci95": _pct(cols["m_same"]), "M_stored_ci95": _pct(cols["m_stored"]),
        "monitor_rho_ci95": _pct(mr), "monitor_rho_median": float(np.nanmedian(mr)),
        "P_monitor_rho_lt_1": float(np.nanmean(mr < 1.0)),
        "P_monitor_rho_le_0.33": float(np.nanmean(mr <= 0.33)),
        "P_monitor_rho_gt_0.72": float(np.nanmean(mr > 0.72)),
        "S_ci95": _pct(cols["S"]), "B_prime_ci95": _pct(cols["B"]),
        "classifier_rho_ci95_recomputed": _pct(cols["c_rho"]),
        "delta_stored_monitor_minus_Bprime": {
            "point": None, "ci95": _pct(cols["d_stored"]),
            "P_gt_0": float(np.mean(np.asarray(cols["d_stored"]) > 0))},
        "delta_samegen_monitor_minus_S": {
            "point": None, "ci95": _pct(cols["d_same"]),
            "P_gt_0": float(np.mean(np.asarray(cols["d_same"]) > 0))},
        "delta_monitor_rho_minus_classifier_rho": {
            "ci95": _pct(cols["d_rho"]),
            "P_lt_0": float(np.nanmean(np.asarray(cols["d_rho"], dtype=float) < 0))},
    }


def cross_monitor(order: list, a_by: dict, b_by: dict) -> dict:
    """Do the two monitors agree pair by pair? Spearman on margins and on each class."""
    ah, aa, bh, ba = [], [], [], []
    for p in order:
        x, y = a_by.get(p, {}), b_by.get(p, {})
        if None in (x.get("honest"), x.get("attack"), y.get("honest"), y.get("attack")):
            continue
        ah.append(x["honest"]); aa.append(x["attack"])
        bh.append(y["honest"]); ba.append(y["attack"])
    if len(ah) < 3:
        return {"n": len(ah)}
    ah, aa, bh, ba = map(np.array, (ah, aa, bh, ba))
    agree = ((aa > ah) == (ba > bh)).mean()
    return {"n": int(len(ah)),
            "spearman_margins": float(spearmanr(aa - ah, ba - bh).statistic),
            "spearman_attack_scores": float(spearmanr(aa, ba).statistic),
            "spearman_honest_scores": float(spearmanr(ah, bh).statistic),
            "frac_same_pairwise_call": float(agree)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", default="sonnet5")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="monitor_rho.json")
    args = ap.parse_args()

    out_rows = []
    for spec in ROWS:
        blob = json.load(open(spec["gate_s"]))
        clf_S = {str(o["problem_id"]): {"honest": o["score_honest"], "attack": o["score_attack"]}
                 for o in blob["S"]["oof"]}
        clf_B = {str(o["problem_id"]): {"honest": o["score_honest"], "attack": o["score_attack"]}
                 for o in blob["B_prime"]["oof"]}
        # Problem order as the json persists it, so the classifier's joint rho recomputed inside
        # these draws is bit-comparable with rho_joint_ci.py's.
        order = [str(o["problem_id"]) for o in blob["S"]["oof"] if str(o["problem_id"]) in clf_B]
        published = json.load(open(spec["rho_joint"])) if os.path.exists(spec["rho_joint"]) else {}

        print(f"\n=== {spec['row']}: {spec['desc']}")
        print(f"    {spec['gate_s']}: S = {blob['S']['auroc']:.4f}  "
              f"B' = {blob['B_prime']['auroc']:.4f}  rho = {blob['retained_vs_stored']:.4f} "
              f"(fold-mean); {len(order)} problems")

        row = {**{k: spec[k] for k in ("row", "desc", "gate_s", "rho_joint")},
               "n_problems": len(order),
               "classifier": {
                   "S_fold_mean": blob["S"]["auroc"], "B_prime_fold_mean": blob["B_prime"]["auroc"],
                   "S_pooled_oof": _auroc(np.array([clf_S[p]["honest"] for p in order]),
                                          np.array([clf_S[p]["attack"] for p in order])),
                   "B_prime_pooled_oof": _auroc(np.array([clf_B[p]["honest"] for p in order]),
                                                np.array([clf_B[p]["attack"] for p in order])),
                   "rho_fold_mean": blob["retained_vs_stored"],
                   "rho_joint_ci95_published": (published.get("joint") or {}).get("rho_ci95_joint"),
                   "rho_pooled_published": (published.get("joint") or {}).get(
                       "rho_point_pooled_oof")},
               "monitors": {}}

        for model, msfx in MONITORS:
            f_same = f"monitor_samegen_{args.tag}_{spec['arm']}_{spec['eligibility']}{msfx}.json"
            f_stor = f"monitor_stored_{args.tag}_{spec['arm']}_{spec['eligibility']}{msfx}.json"
            if not (os.path.exists(f_same) and os.path.exists(f_stor)):
                print(f"    {model}: SKIPPED, missing "
                      f"{[f for f in (f_same, f_stor) if not os.path.exists(f)]}")
                continue
            same, stor = monitor_scores(f_same), monitor_scores(f_stor)
            st_same = side_stats(same["by"], order)
            st_stor = side_stats(stor["by"], order)
            m_s, m_t = st_same["auroc"], st_stor["auroc"]
            rho = (m_s - 0.5) / (m_t - 0.5) if m_t and m_t > 0.5 else float("nan")
            jb = joint(order, same["by"], stor["by"], clf_S, clf_B, args.n_boot, args.seed)
            jb["delta_stored_monitor_minus_Bprime"]["point"] = m_t - row["classifier"][
                "B_prime_pooled_oof"]
            jb["delta_samegen_monitor_minus_S"]["point"] = m_s - row["classifier"]["S_pooled_oof"]
            row["monitors"][model] = {
                "self_evaluation_on_samegen": bool(same["blob"].get("self_evaluation")),
                "samegen_json": f_same, "stored_json": f_stor,
                "samegen_auroc_published": (same["blob"]["metrics"] or {}).get("auroc"),
                "samegen": st_same, "stored": st_stor,
                "monitor_rho_point": rho, "joint": jb,
            }
            print(f"    {model:18s} M_samegen {m_s:.4f} "
                  f"({jb['M_samegen_ci95'][0]:.4f}-{jb['M_samegen_ci95'][1]:.4f})   "
                  f"M_stored {m_t:.4f} ({jb['M_stored_ci95'][0]:.4f}-{jb['M_stored_ci95'][1]:.4f})"
                  f"   monitor-rho {rho:.4f} "
                  f"({jb['monitor_rho_ci95'][0]:.4f}-{jb['monitor_rho_ci95'][1]:.4f})")
            print(f"    {'':18s} vs B' on the SAME stored pairs: "
                  f"{jb['delta_stored_monitor_minus_Bprime']['point']:+.4f} "
                  f"({jb['delta_stored_monitor_minus_Bprime']['ci95'][0]:+.4f},"
                  f"{jb['delta_stored_monitor_minus_Bprime']['ci95'][1]:+.4f})   "
                  f"P(monitor > B') = {jb['delta_stored_monitor_minus_Bprime']['P_gt_0']:.3f}   "
                  f"P(monitor-rho < 1) = {jb['P_monitor_rho_lt_1']:.3f}")
            print(f"    {'':18s} pairwise (ties half) samegen {st_same['pairwise_acc_ties_half']:.4f}"
                  f" / stored {st_stor['pairwise_acc_ties_half']:.4f};  mean honest/attack samegen "
                  f"{st_same['mean_score_honest']:.1f}/{st_same['mean_score_attack']:.1f}, stored "
                  f"{st_stor['mean_score_honest']:.1f}/{st_stor['mean_score_attack']:.1f};  missing"
                  f" {st_same['n_programs_missing']} / {st_stor['n_programs_missing']}")
            if model == MONITORS[0][0]:
                print(f"    {'':18s} classifier rho recomputed in these draws: "
                      f"{jb['classifier_rho_ci95_recomputed'][0]:.4f}-"
                      f"{jb['classifier_rho_ci95_recomputed'][1]:.4f}"
                      f"   (published joint {row['classifier']['rho_joint_ci95_published']})")

        names = [m for m, _ in MONITORS[:2] if m in row["monitors"]]
        if len(names) == 2:
            a, b = (monitor_scores(row["monitors"][n]["samegen_json"])["by"] for n in names)
            c, d = (monitor_scores(row["monitors"][n]["stored_json"])["by"] for n in names)
            row["monitor_agreement"] = {"models": names,
                                        "samegen": cross_monitor(order, a, b),
                                        "stored": cross_monitor(order, c, d)}
            ag = row["monitor_agreement"]
            print(f"    agreement {names[0]} vs {names[1]}: same-gen Spearman(margins) "
                  f"{ag['samegen']['spearman_margins']:+.3f}, same call "
                  f"{ag['samegen']['frac_same_pairwise_call']:.3f};  stored "
                  f"{ag['stored']['spearman_margins']:+.3f} / "
                  f"{ag['stored']['frac_same_pairwise_call']:.3f}")
        out_rows.append(row)

    out = {"n_boot": args.n_boot, "seed": args.seed, "rows": out_rows,
           "note": ("monitor-rho = (M_samegen - 0.5)/(M_stored - 0.5), one problem set resampled "
                    "per draw and both AUROCs recomputed on it. The 24-monitor comparison on "
                    "Koran's split is a different problem set and these numbers are not "
                    "comparable with it. claude-sonnet-5 wrote both same-generator classes (self-evaluation); "
                    "claude-haiku-4-5 wrote neither.")}
    json.dump(out, open(args.out, "w"), indent=2, default=float)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
