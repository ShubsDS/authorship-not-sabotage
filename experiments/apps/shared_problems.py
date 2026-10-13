"""Same problems, inert or working attacks: is the strict row's higher rho the attacks or the problems?

The headline set (623 problems, first draw, 14 fire) and the strict set (99 problems, a draw that
passes and fires) share 64 problems. On those the honest program is the same (gen_sonnet5.jsonl)
and so is the stored pair (fire_counts.py's token check: 64 of 64 stored attacks identical), so
the only thing that differs between the two rows is our attack program: the first draw against a
working one.

S and B' on a subset are the existing pooled out-of-fold scores restricted to that subset (no
refit): S from the row's `S.oof`, B' from its `B_prime.oof`, each AUROC computed over the
subset's honest and attack scores, rho = (S - 0.5)/(B' - 0.5). The headline numbers come from
sg_indep_first_passes_v2.json (fits on 623 problems) and the strict ones from
sg_indep_best_usable_v2.json (fits on 99), so the two rows' scores on a shared problem come from
different fits; that is the comparison the paper's two rows make.

Intervals: bootstrap over problems, 2,000 draws, numpy RandomState(0). On the shared problems
one randint(0, n, n) per draw resamples the problems and all four AUROCs (S and B' of each row)
are recomputed on the draw, so the difference in rho is paired. For the strict row split into
shared and non-shared problems the draw is stratified (each subset resampled within itself,
shared first), so the subsets keep their sizes. Draws whose B' is at or below 0.5 are dropped
and counted.

Subsets reported: the 64 shared problems; the 53 of them whose two attack programs differ and
the 11 where they are the same program; the strict row's 35 non-shared problems; the headline
row's 559 non-shared problems.

Which attack programs are the same is read from the files the two classifier rows used,
bdind_sonnet5_first.jsonl (headline) and bdind_sonnet5_best_nocrash.jsonl (strict), by their
`draw` key. Those files are on the cluster; without them the script falls back to
fire_counts.json's token rule, which compares the monitor runs' files instead and so counts
problem 1701 as the same program (the monitor's strict file kept the crash-on-trigger first
draw there, the classifier's a later quiet draw): 52 / 12 instead of 53 / 11.

Inputs: sg_indep_first_passes_v2.json, sg_indep_best_usable_v2.json, and either the two jsonl
files above or fire_counts.json.

Usage:
    python shared_problems.py --out shared_problems.json
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np
from sklearn.metrics import roc_auc_score

N_BOOT, SEED = 2000, 0


def _auroc(h: np.ndarray, a: np.ndarray) -> float:
    return float(roc_auc_score(np.r_[np.zeros(len(h)), np.ones(len(a))], np.r_[h, a]))


def _rho(s: float, b: float) -> float:
    return (s - 0.5) / (b - 0.5) if b > 0.5 else float("nan")


def _pct(x) -> list:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def oof(block: dict) -> dict:
    return {str(o["problem_id"]): (o["score_honest"], o["score_attack"]) for o in block["oof"]}


class Row:
    """S and B' out-of-fold scores of one gate_s_samegen json."""

    def __init__(self, path: str):
        blob = json.load(open(path))
        self.path = path
        self.S, self.B = oof(blob["S"]), oof(blob["B_prime"])

    def arrays(self, pids: list) -> tuple:
        S = np.array([self.S[p] for p in pids])
        B = np.array([self.B[p] for p in pids])
        return S[:, 0], S[:, 1], B[:, 0], B[:, 1]

    def stats(self, pids: list, idx=None) -> dict:
        sh, sa, bh, ba = self.arrays(pids)
        if idx is not None:
            sh, sa, bh, ba = sh[idx], sa[idx], bh[idx], ba[idx]
        s, b = _auroc(sh, sa), _auroc(bh, ba)
        return {"S": s, "B_prime": b, "rho": _rho(s, b)}


def subset(row: Row, pids: list, name: str) -> dict:
    pt = row.stats(pids)
    rng = np.random.RandomState(SEED)
    n = len(pids)
    bs = [row.stats(pids, rng.randint(0, n, n)) for _ in range(N_BOOT)]
    rho = np.array([b["rho"] for b in bs])
    return {"subset": name, "source": row.path, "n": n, **pt,
            "S_ci95": _pct([b["S"] for b in bs]), "B_prime_ci95": _pct([b["B_prime"] for b in bs]),
            "rho_ci95": _pct(rho), "n_draws_bprime_le_half": int(np.isnan(rho).sum())}


def paired(head: Row, strict: Row, pids: list, name: str) -> dict:
    h, s = head.stats(pids), strict.stats(pids)
    rng = np.random.RandomState(SEED)
    n = len(pids)
    dh, ds = [], []
    for _ in range(N_BOOT):
        idx = rng.randint(0, n, n)
        dh.append(head.stats(pids, idx))
        ds.append(strict.stats(pids, idx))
    rh, rs = np.array([d["rho"] for d in dh]), np.array([d["rho"] for d in ds])
    out = {"subset": name, "n": n,
           "headline_attacks": {**h, "S_ci95": _pct([d["S"] for d in dh]),
                                "B_prime_ci95": _pct([d["B_prime"] for d in dh]),
                                "rho_ci95": _pct(rh)},
           "strict_attacks": {**s, "S_ci95": _pct([d["S"] for d in ds]),
                              "B_prime_ci95": _pct([d["B_prime"] for d in ds]),
                              "rho_ci95": _pct(rs)},
           "rho_strict_minus_headline": {"point": s["rho"] - h["rho"], "ci95": _pct(rs - rh)},
           "S_strict_minus_headline": {"point": s["S"] - h["S"],
                                       "ci95": _pct(np.array([d["S"] for d in ds])
                                                    - np.array([d["S"] for d in dh]))},
           "n_draws_bprime_le_half": int(np.isnan(rh).sum() + np.isnan(rs).sum())}
    print(f"\n{name} (n = {n}), paired:")
    for lab, r in (("headline attacks", out["headline_attacks"]),
                   ("strict attacks", out["strict_attacks"])):
        print(f"  {lab:17s} S {r['S']:.4f} ({r['S_ci95'][0]:.4f}-{r['S_ci95'][1]:.4f})"
              f"  B' {r['B_prime']:.4f}  rho {r['rho']:.3f} ({r['rho_ci95'][0]:.3f}-"
              f"{r['rho_ci95'][1]:.3f})")
    d = out["rho_strict_minus_headline"]
    print(f"  rho strict - headline {d['point']:+.3f} ({d['ci95'][0]:+.3f} to {d['ci95'][1]:+.3f})")
    return out


def stratified(strict: Row, shared: list, rest: list) -> dict:
    """Strict row on shared vs non-shared problems; stratified bootstrap of the difference."""
    a, b = strict.stats(shared), strict.stats(rest)
    rng = np.random.RandomState(SEED)
    da, db = [], []
    for _ in range(N_BOOT):
        da.append(strict.stats(shared, rng.randint(0, len(shared), len(shared)))["rho"])
        db.append(strict.stats(rest, rng.randint(0, len(rest), len(rest)))["rho"])
    da, db = np.array(da), np.array(db)
    return {"shared": {**a, "n": len(shared), "rho_ci95": _pct(da)},
            "non_shared": {**b, "n": len(rest), "rho_ci95": _pct(db)},
            "rho_non_shared_minus_shared": {"point": b["rho"] - a["rho"], "ci95": _pct(db - da)}}


CLASSIFIER_FILES = ("bdind_sonnet5_first.jsonl", "bdind_sonnet5_best_nocrash.jsonl")


def _same_program(shared: list[str]) -> tuple[set[str], str]:
    """Shared problems whose headline and strict attack are the same program, and the rule used."""
    if all(os.path.exists(f) for f in CLASSIFIER_FILES):
        head, strict = ({r["problem_id"]: r["draw"]
                         for r in (json.loads(l) for l in open(f) if l.strip())}
                        for f in CLASSIFIER_FILES)
        return ({p for p in shared if head.get(p) is not None and head.get(p) == strict.get(p)},
                "draw keys of " + " and ".join(CLASSIFIER_FILES))
    return (set(json.load(open("fire_counts.json"))["attack_identical"]["both"]),
            "fire_counts.json token rule (monitor files; fallback)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="shared_problems.json")
    args = ap.parse_args()

    head, strict = Row("sg_indep_first_passes_v2.json"), Row("sg_indep_best_usable_v2.json")
    shared = sorted(set(head.S) & set(strict.S))
    same_prog, same_rule = _same_program(shared)
    differ = [p for p in shared if p not in same_prog]
    identical = [p for p in shared if p in same_prog]
    strict_only = sorted(set(strict.S) - set(shared))
    head_only = sorted(set(head.S) - set(shared))
    print(f"headline {len(head.S)}, strict {len(strict.S)}, shared {len(shared)} "
          f"(attack programs differ on {len(differ)}, identical on {len(identical)})")

    out = {"method": "existing pooled out-of-fold scores restricted to each subset; no refit",
           "same_program_rule": same_rule,
           "n_boot": N_BOOT, "seed": SEED,
           "full_rows": {"headline": subset(head, sorted(head.S), "headline, all 623"),
                         "strict": subset(strict, sorted(strict.S), "strict, all 99")},
           "shared": paired(head, strict, shared, "shared problems"),
           "shared_attacks_differ": paired(head, strict, differ,
                                           "shared problems, attack programs differ"),
           "shared_attacks_identical": {"n": len(identical), "problem_ids": identical,
                                        "headline": head.stats(identical),
                                        "strict": strict.stats(identical),
                                        "note": "too few for an interval"},
           "strict_shared_vs_non_shared": stratified(strict, shared, strict_only),
           "headline_non_shared": subset(head, head_only, "headline, non-shared"),
           "problem_ids": {"shared": shared, "strict_only": strict_only}}
    st = out["strict_shared_vs_non_shared"]
    print(f"\nstrict row: shared {st['shared']['n']} rho {st['shared']['rho']:.3f} "
          f"({st['shared']['rho_ci95'][0]:.3f}-{st['shared']['rho_ci95'][1]:.3f}); non-shared "
          f"{st['non_shared']['n']} S {st['non_shared']['S']:.4f} B' {st['non_shared']['B_prime']:.4f}"
          f" rho {st['non_shared']['rho']:.3f} ({st['non_shared']['rho_ci95'][0]:.3f}-"
          f"{st['non_shared']['rho_ci95'][1]:.3f}); difference "
          f"{st['rho_non_shared_minus_shared']['point']:+.3f} "
          f"({st['rho_non_shared_minus_shared']['ci95'][0]:+.3f} to "
          f"{st['rho_non_shared_minus_shared']['ci95'][1]:+.3f})")
    hn = out["headline_non_shared"]
    print(f"headline row, non-shared {hn['n']}: S {hn['S']:.4f} B' {hn['B_prime']:.4f} "
          f"rho {hn['rho']:.3f} ({hn['rho_ci95'][0]:.3f}-{hn['rho_ci95'][1]:.3f})")
    for k in ("headline", "strict"):
        r = out["full_rows"][k]
        print(f"{k} row, all: S {r['S']:.4f} B' {r['B_prime']:.4f} rho {r['rho']:.3f}")
    si = out["shared_attacks_identical"]
    print(f"identical-program problems ({si['n']}): headline rho {si['headline']['rho']:.3f}, "
          f"strict rho {si['strict']['rho']:.3f}")

    json.dump(out, open(args.out, "w"), indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
