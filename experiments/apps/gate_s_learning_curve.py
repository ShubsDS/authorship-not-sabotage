"""The matched-n learning curve of B: is a low S a collapse, or is it underfitting?

    python gate_s_learning_curve.py                                    # the curve alone
    python gate_s_learning_curve.py --human-pass-file human_verify.jsonl
    python gate_s_learning_curve.py --match-problems gate_s_samegen_sonnet5_independent_passes.json

S is fitted on a few hundred pairs; B = 0.8714 was fitted on 1,444. At n = 125 each training
fold sees ~200 documents against 2,310, and `min_df=3` keeps a fraction of the vocabulary, so a
low S is confounded with underfitting until B is measured at the same n through the same code.
That is all this script does: subsample the B pairs, refit, and report the curve.

Nothing here is a new pipeline. `build_pairs()` and the pool loading come from
`gate_s_baseline.py` and `evaluate()` from `gate_s_eval.py`, both imported, so every point on
this curve is the same function that produced B and S. Only the number of pairs changes.

What it needs (in the working directory, i.e. `experiments/apps/`):
    train_*.parquet             the artifact shards (`python fetch.py`)
    human_verify.jsonl          optional; run_tests.py's verdict on the human class. Pass it so
                                the curve uses the same pool definition as B under our own flag
                                (1,406 pairs), not the shipped flag (1,444).
    a gate_s_samegen_*.json     optional; with --match-problems B is ALSO recomputed over exactly
                                the problem ids S used. That json must carry `problem_ids`
                                (gate_s_samegen.py writes it); if it does not, this script says so
                                and falls back to matching n only.

Outputs `gate_s_learning_curve.json` and a table, and ends with the one sentence the paper needs:

    At n = <S's n>, B under the identical pipeline is X +/- Y, so a collapse to S
    is / is not attributable to sample size.

Cost: CPU only, but not instant. The default grid at 30 draws is ~180 refits, each carrying
evaluate()'s 2,000-resample bootstrap: 12 min on a 625-pair synthetic pool, so budget 20-45 min on
the real 1,444-pair one. `--boot 500` cuts most of that and moves only the reported CI width.
Every draw is seeded (`--seed`), so the table is reproducible.

⚠️ Read the curve, not just its endpoint. If B at S's n is still near 0.85, a low S is a real
collapse. If B itself falls toward 0.75 at that n, the pre-registered rho bands were computed at
a sample size the arm never had, and the honest denominator is the problem-matched B' that
gate_s_samegen.py fits - which is what --match-problems reports.
"""

from __future__ import annotations

import argparse
import contextlib
import glob
import io
import json
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, ".")
from gate_s_baseline import COLS, build_pairs  # noqa: E402 - identical pool by construction
from gate_s_eval import evaluate  # noqa: E402 - identical fit by construction

DEFAULT_GRID = [50, 100, 125, 200, 335, 400, 800]
FIELDS = ["auroc", "pairwise_acc", "length_only_auroc", "surface7_auroc"]


def _quiet_evaluate(pairs: pd.DataFrame, label: str, n_boot: int) -> dict:
    """evaluate() with its per-fit print swallowed; 250 of them is not a table."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return evaluate(pairs, label, n_boot=n_boot)


def load_pool(human_pass_file: str | None) -> pd.DataFrame:
    """The B pool, exactly as gate_s_baseline.main() builds it.

    The pair construction itself is `build_pairs()`, imported. Only the shard read and the
    --human-pass-file parse are restated here, because gate_s_baseline keeps them inline in
    main() and nothing in this branch may refactor that file. If they are ever factored out,
    delete this function and call it instead - the two must not drift.
    """
    shards = sorted(glob.glob("train_*.parquet"))
    if not shards:
        raise SystemExit("no train_*.parquet here - run `python fetch.py` first")
    df = pd.concat([pq.read_table(f, columns=COLS).to_pandas() for f in shards],
                   ignore_index=True)
    df["problem_id"] = df.problem_id.astype(str)
    print(f"artifact rows {len(df)}")

    honest_ok = honest_idx = None
    if human_pass_file:
        honest_idx = {}
        for line in open(human_pass_file):
            if not line.strip():
                continue
            r = json.loads(line)
            if r["passed"]:
                honest_idx.setdefault(str(r["problem_id"]), []).append(r["sol_idx"])
        for v in honest_idx.values():
            v.sort()
        honest_ok = set(honest_idx)
        print(f"human pass flag: OUR OWN harness, {len(honest_ok)} passing ({human_pass_file})")
    else:
        print("human pass flag: the artifact's shipped `solution_passes_tests` "
              "(no --human-pass-file given)")
    return build_pairs(df, honest_ok, honest_idx)


def curve_point(pairs: pd.DataFrame, n: int, draws: int, seed: int, n_boot: int) -> dict:
    """`draws` random n-pair subsamples of the B pool, refit from scratch each time."""
    N = len(pairs)
    if n >= N:                      # the full pool is one deterministic draw, not `draws` copies
        n, draws = N, 1
    rng = np.random.RandomState(seed + n)
    runs = []
    for d in range(draws):
        idx = rng.choice(N, size=n, replace=False) if n < N else np.arange(N)
        sub = pairs.iloc[np.sort(idx)].reset_index(drop=True)
        runs.append(_quiet_evaluate(sub, f"B n={n} draw={d}", n_boot))
    pt = {"n": n, "draws": draws, "n_pairs_used": int(runs[0]["n_pairs"])}
    for f in FIELDS:
        v = np.array([r[f] for r in runs], dtype=float)
        pt[f"{f}_mean"], pt[f"{f}_sd"] = float(v.mean()), float(v.std())
    widths = np.array([r["auroc_ci95_boot"][1] - r["auroc_ci95_boot"][0] for r in runs])
    pt["ci_width_mean"] = float(widths.mean())
    pt["auroc_pooled_oof_mean"] = float(np.mean([r["auroc_pooled_oof"] for r in runs]))
    pt["auroc_min"], pt["auroc_max"] = (float(min(r["auroc"] for r in runs)),
                                        float(max(r["auroc"] for r in runs)))
    print(f"  n={pt['n']:5d} draws={draws:3d}  TF-IDF {pt['auroc_mean']:.4f} +/- "
          f"{pt['auroc_sd']:.4f}  pairwise {pt['pairwise_acc_mean']:.4f}  "
          f"length {pt['length_only_auroc_mean']:.4f}  surface7 "
          f"{pt['surface7_auroc_mean']:.4f}  mean CI width {pt['ci_width_mean']:.4f}")
    return pt


def print_table(points: list[dict]) -> None:
    print(f"\n{'=' * 100}")
    print("MATCHED-n LEARNING CURVE OF B  (mean +/- sd over draws; identical pipeline throughout)")
    print(f"{'n':>6} {'draws':>6} {'TF-IDF':>16} {'pairwise':>15} {'length':>15} "
          f"{'surface7':>15} {'CI width':>9}")
    for p in points:
        print(f"{p['n']:>6} {p['draws']:>6} "
              f"{p['auroc_mean']:>8.4f} +/-{p['auroc_sd']:.4f} "
              f"{p['pairwise_acc_mean']:>7.4f} +/-{p['pairwise_acc_sd']:.4f} "
              f"{p['length_only_auroc_mean']:>7.4f} +/-{p['length_only_auroc_sd']:.4f} "
              f"{p['surface7_auroc_mean']:>7.4f} +/-{p['surface7_auroc_sd']:.4f} "
              f"{p['ci_width_mean']:>9.4f}")
    print(f"{'=' * 100}")


def nearest_point(points: list[dict], n: int) -> dict:
    return min(points, key=lambda p: abs(p["n"] - n))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--human-pass-file", default=None,
                    help="run_tests.py output for the human class; falls back to the shipped flag")
    ap.add_argument("--grid", default=",".join(str(x) for x in DEFAULT_GRID),
                    help=f"comma-separated n values (default {DEFAULT_GRID}); the full pool is "
                         f"always appended")
    ap.add_argument("--draws", type=int, default=30, help="random subsamples per n (default 30)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--boot", type=int, default=2000,
                    help="bootstrap resamples inside evaluate() (default 2000, as in B). Lower it "
                         "to ~500 for a quick curve; it moves the reported CI width slightly and "
                         "nothing else.")
    ap.add_argument("--match-problems", default=None,
                    help="a gate_s_samegen_*.json; also compute B over exactly S's problem ids")
    ap.add_argument("--out", default="gate_s_learning_curve.json")
    args = ap.parse_args()

    # Read the arm first, so S's own n becomes a grid point rather than a nearest-neighbour.
    sg = json.load(open(args.match_problems)) if args.match_problems else None
    s_n = (sg.get("n_same_generator_pairs", sg["S"]["n_pairs"]) if sg else None)

    pairs = load_pool(args.human_pass_file)
    N = len(pairs)
    print(f"\nB pool: {N} pairs")
    if N < 50:
        raise SystemExit(f"only {N} eligible pairs")

    grid = sorted({int(x) for x in args.grid.split(",") if x.strip()} | {N}
                  | ({s_n} if s_n else set()))
    grid = [n for n in grid if n <= N]
    print(f"grid {grid}, {args.draws} draws per n (seed {args.seed}), "
          f"{args.boot} bootstrap resamples per fit\n")
    points = [curve_point(pairs, n, args.draws, args.seed, args.boot) for n in grid]
    print_table(points)

    full = points[-1]
    out = {"pool_n": N, "draws": args.draws, "seed": args.seed, "n_boot": args.boot,
           "human_pass_flag": "own" if args.human_pass_file else "shipped",
           "points": points, "full_pool_auroc": full["auroc_mean"]}

    # ---- matched to a same-generator arm -------------------------------------------------
    s_auroc = s_ci = None
    matched = None
    if sg is not None:
        s_auroc = sg["S"]["auroc"]
        s_ci = sg["S"].get("auroc_ci95_boot")
        out["samegen"] = {"file": args.match_problems, "tag": sg.get("tag"),
                          "arm": sg.get("arm"), "eligibility": sg.get("eligibility"),
                          "S_auroc": s_auroc, "S_ci95": s_ci, "S_n": s_n,
                          "B_prime_auroc": (sg.get("B_prime") or {}).get("auroc")}
        pids = sg.get("problem_ids")
        print(f"\n--match-problems: {args.match_problems}  "
              f"(S = {s_auroc:.4f} on n = {s_n})")
        if pids:
            sub = pairs[pairs.problem_id.isin(set(str(p) for p in pids))]
            print(f"  S's problem ids: {len(pids)} stored, {len(sub)} of them are in the B pool")
            if len(sub) >= 50:
                print("  B restricted to EXACTLY those problems (1 fit, no subsampling):")
                matched = evaluate(sub.reset_index(drop=True), "B  same problems as S")
                out["b_on_s_problems"] = matched
                if sg.get("eligibility") == "passes" and \
                        sg.get("b_prime_attack_rule", "").startswith("passes ("):
                    print("  NOTE: this B is the B POOL restricted to S's problems, so its attack "
                          "side is\n        all-firing. S's own arm was scored against an "
                          "inert-inclusive B' (--bprime-inert).\n        Quote that B' for the "
                          "`passes` headline; this row is the all-firing comparator.")
            else:
                print(f"  only {len(sub)} of S's problems survive the B pool filter "
                      f"(working stored backdoor + passing human honest + deterministic); "
                      f"below the 50-pair floor, falling back to matched n")
        else:
            print("  THIS JSON STORES NO `problem_ids`, so B cannot be restricted to S's exact\n"
                  "  problems; falling back to MATCHED n. Rerun gate_s_samegen.py (current\n"
                  "  version writes the field) if the problem-matched number is wanted.")
            out["match_problems_note"] = "json had no problem_ids; matched n only"

    # ---- the sentence ---------------------------------------------------------------------
    print(f"\n{'=' * 100}")
    if s_n is None:
        print("FOR THE PAPER (no --match-problems given, so S's n is not known here):")
        # the two candidate S sizes: ~125 strict pairs, 335 test-passing independent-arm pairs
        shown: list[int] = []
        for n in (125, 335):
            p = nearest_point(points, n)
            if p["n"] in shown:
                continue
            shown.append(p["n"])
            print(f"  At n = {p['n']}, B under the identical pipeline is "
                  f"{p['auroc_mean']:.4f} +/- {p['auroc_sd']:.4f} "
                  f"(full pool n = {N}: {full['auroc_mean']:.4f}).")
        print("  Rerun with --match-problems <gate_s_samegen json> to get the routed sentence.")
    else:
        p = nearest_point(points, s_n)
        # Does B ITSELF fall to S's level at this n? If S's bootstrap interval reaches down into
        # the spread of B-at-n, sample size alone can produce S and the comparison is not
        # informative. If S sits clearly below every B draw at that n, the drop is real.
        b_lo = p["auroc_mean"] - 2 * p["auroc_sd"]
        s_hi = s_ci[1] if s_ci else s_auroc
        attributable = s_hi >= min(b_lo, p["auroc_min"])
        verb = "is" if attributable else "is not"
        print("FOR THE PAPER, verbatim:")
        print(f"  At n = {s_n}, B under the identical pipeline is {p['auroc_mean']:.4f} "
              f"+/- {p['auroc_sd']:.4f}, so a collapse to S {verb} attributable to sample size.")
        if p["n"] != s_n:
            print(f"  (nearest grid point is n = {p['n']}; add {s_n} to --grid for an exact match)")
        print(f"  supporting: S = {s_auroc:.4f}"
              + (f" (95% CI {s_ci[0]:.4f}-{s_ci[1]:.4f})" if s_ci else "")
              + f"; B at n={p['n']} ranged {p['auroc_min']:.4f}-{p['auroc_max']:.4f} over "
                f"{p['draws']} draws; B at the full pool n={N} is {full['auroc_mean']:.4f}.")
        if matched:
            print(f"  problem-matched: B over S's own {matched['n_pairs']} problems is "
                  f"{matched['auroc']:.4f} (95% CI {matched['auroc_ci95_boot'][0]:.4f}-"
                  f"{matched['auroc_ci95_boot'][1]:.4f}). Prefer this to the matched-n row: it "
                  f"holds the problems fixed as well as the sample size.")
        out["paper_sentence"] = (
            f"At n = {s_n}, B under the identical pipeline is {p['auroc_mean']:.4f} "
            f"+/- {p['auroc_sd']:.4f}, so a collapse to S {verb} attributable to sample size.")
        out["collapse_attributable_to_n"] = bool(attributable)
    print(f"{'=' * 100}")

    import sklearn
    out["sklearn"], out["pandas"] = sklearn.__version__, pd.__version__
    json.dump(out, open(args.out, "w"), indent=2, default=float)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
