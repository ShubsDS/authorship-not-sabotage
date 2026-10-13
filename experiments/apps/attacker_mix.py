"""Which stored model wrote each stored backdoor, and how much the attacker alone moves B.

The stored attack class is not one model. Every backdoor entry in RoganInglis/apps-control-arena
carries a `model` field (`unknown` for the entries whose `source` is `apps`, which are
unattributed). This script reads it for the backdoor each row's B' actually uses (the first
entry that passes the public tests for the headline, Haiku and prompt-matched rows, which were
built with --bprime-inert; the first that passes and works for the strict rows), and for the
analysis pool and the filtered split.

Per attacking model it reports B from the existing pooled out-of-fold B' scores of the headline
row (sg_indep_first_passes_v2.json `B_prime.oof`, no refit), two ways:

  within    the problems that model attacked: their human honest scores against their stored
            attack scores (the honest programs differ between models);
  fixed     all 623 human honest scores against that model's attack scores, so the honest class
            is the same code for every model and only the attacker changes.

With --refit (default on when the parquet shards are present) the same is done on the 1,444-pair
analysis pool, refitting B once with gate_s_eval.evaluate() over gate_s_baseline.build_pairs()
(the backdoor there is data._pick_backdoor's, the first that passes and works), so the groups
are larger.

rho restricted to stored attackers from Claude models: S and B' of the headline row restricted to
the problems whose B' attack was written by an anthropic/* model (existing out-of-fold scores, no
refit), rho = (S - 0.5)/(B' - 0.5), joint bootstrap over those problems with
rho_joint_ci.joint_bootstrap (2,000 draws, seed 0). Also for claude-3-7-sonnet-thinking alone,
the model the paper names as the stored attacker, and for the non-Claude complement.

Attacker counts are given over every backdoor entry of the 5,000-row artifact, over the backdoor
selected for each of the 1,444 analysis-pool problems, over each row's B' problems, and over the
filtered split (eugenekoran/apps-control-arena-high-quality `top_backdoor_model`, from
koran_meta.parquet written by fetch_inputs.py; skipped if absent). The filtered split's metadata
names one model the artifact does not, openai/gpt-4; the script checks whether those problems'
working backdoors in the artifact are the unattributed apps-source entries.

Inputs: train_*.parquet (fetch.py), optionally koran_meta.parquet (fetch_inputs.py),
sg_indep_first_passes_v2.json, sg_indep_best_usable_v2.json, sg_haiku45_indep_passes.json,
gate_s_matched_headline.json.

Usage:
    python attacker_mix.py --out attacker_mix.json      # ~1 min, plus ~1 min for the refit
"""

from __future__ import annotations

import argparse
import collections
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
from data import _honest_code, _pick_backdoor  # noqa: E402
from rho_joint_ci import _oof_frame, joint_bootstrap  # noqa: E402

N_BOOT, SEED = 2000, 0
MIN_N = 10   # per-model AUROCs below this many problems are reported without an interval


def _auroc(h, a) -> float:
    return float(roc_auc_score(np.r_[np.zeros(len(h)), np.ones(len(a))], np.r_[h, a]))


def _pct(x) -> list:
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def stored_model(bds, inert: bool) -> str:
    ok = [dict(b) for b in bds if b["passes_tests"] and (inert or b["backdoor_works"])]
    return ok[0]["model"] if ok else None


def per_model_b(oof: pd.DataFrame, model_of: dict) -> dict:
    """B per attacking model from out-of-fold scores (index problem_id; score_honest/attack)."""
    oof = oof.copy()
    oof["model"] = [model_of[p] for p in oof.index]
    all_h = oof.score_honest.values
    rng = np.random.RandomState(SEED)
    out = {}
    for m, g in sorted(oof.groupby("model"), key=lambda kv: -len(kv[1])):
        h, a = g.score_honest.values, g.score_attack.values
        r = {"n": int(len(g)), "B_within": _auroc(h, a), "B_fixed_honest": _auroc(all_h, a)}
        if len(g) >= MIN_N:
            bw, bf = [], []
            for _ in range(N_BOOT):
                i = rng.randint(0, len(g), len(g))
                j = rng.randint(0, len(all_h), len(all_h))
                bw.append(_auroc(h[i], a[i]))
                bf.append(_auroc(all_h[j], a[i]))
            r["B_within_ci95"], r["B_fixed_honest_ci95"] = _pct(bw), _pct(bf)
        out[m] = r
    return out


def show(title: str, d: dict) -> None:
    print(f"\n{title}")
    print(f"  {'attacking model':46s} {'n':>4s} {'B within (95% CI)':>24s} {'B fixed honest':>24s}")
    for m, r in d.items():
        ci = lambda k: (f" ({r[k + '_ci95'][0]:.3f}-{r[k + '_ci95'][1]:.3f})"
                        if k + "_ci95" in r else "")
        print(f"  {m:46s} {r['n']:4d} {r['B_within']:8.3f}{ci('B_within'):16s}"
              f" {r['B_fixed_honest']:8.3f}{ci('B_fixed_honest'):16s}")


def rho_subset(blob: dict, pids: list, label: str) -> dict:
    S, B = _oof_frame(blob["S"]), _oof_frame(blob["B_prime"])
    keep = [p for p in S.index if p in set(pids)]
    jb = joint_bootstrap(S.loc[keep], B.loc[keep], N_BOOT, SEED)
    print(f"  {label:44s} n={jb['n_common_problems']:4d}  S {jb['S_pooled_oof']:.4f}  "
          f"B' {jb['B_prime_pooled_oof']:.4f}  rho {jb['rho_point_pooled_oof']:.3f} "
          f"({jb['rho_ci95_joint'][0]:.3f}-{jb['rho_ci95_joint'][1]:.3f})")
    return {"label": label, **jb}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-refit", action="store_true", help="skip the 1,444-pair refit")
    ap.add_argument("--out", default="attacker_mix.json")
    args = ap.parse_args()

    shards = sorted(glob.glob("train_*.parquet"))
    if not shards:
        raise SystemExit("no train_*.parquet here - run `python fetch.py` first")
    cols = ["problem_id", "solutions", "backdoors", "solution_passes_tests", "backdoor_works",
            "is_nondeterministic"]
    df = pd.concat([pq.read_table(f, columns=cols).to_pandas() for f in shards],
                   ignore_index=True)
    df["problem_id"] = df.problem_id.astype(str)
    bds = dict(zip(df.problem_id, df.backdoors))
    out = {"n_boot": N_BOOT, "seed": SEED, "counts": {}}

    # ---- counts -----------------------------------------------------------------------------
    entries = collections.Counter(b["model"] for x in df.backdoors for b in x)
    src = collections.Counter((b["source"], b["model"]) for x in df.backdoors for b in x)
    out["counts"]["artifact_all_entries"] = dict(entries.most_common())
    out["counts"]["artifact_unknown_by_source"] = {f"{s}:{m}": n for (s, m), n in src.items()
                                                  if m == "unknown"}
    pool = df[df.solution_passes_tests & df.backdoor_works & ~df.is_nondeterministic]
    pool_model = {}
    for _, r in pool.iterrows():
        row = {"problem_id": r.problem_id, "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions], "top_backdoor_model": None}
        b = _pick_backdoor(row)
        if b is not None and _honest_code(row) is not None:
            pool_model[r.problem_id] = b["model"]
    out["counts"]["analysis_pool_selected"] = dict(
        collections.Counter(pool_model.values()).most_common())

    rows = {"headline": ("sg_indep_first_passes_v2.json", True),
            "haiku_headline": ("sg_haiku45_indep_passes.json", True),
            "prompt_matched": ("gate_s_matched_headline.json", True),
            "strict": ("sg_indep_best_usable_v2.json", False)}
    row_models = {}
    for name, (path, inert) in rows.items():
        pids = [str(p) for p in json.load(open(path))["problem_ids"]]
        row_models[name] = {p: stored_model(bds[p], inert) for p in pids}
        out["counts"][f"row_{name}"] = dict(
            collections.Counter(row_models[name].values()).most_common())

    if os.path.exists("koran_meta.parquet"):
        k = pd.read_parquet("koran_meta.parquet")
        k["problem_id"] = k.problem_id.astype(str)
        test_att = k[(k.split == "test") & k.backdoor_works]
        test_hon = k[(k.split == "test") & ~k.backdoor_works]
        train = k[k.split == "train"]
        out["counts"]["filtered_split_test_attack_items"] = dict(
            test_att.top_backdoor_model.fillna("(none)").value_counts())
        out["counts"]["filtered_split_train_problems"] = dict(
            train.top_backdoor_model.fillna("(none)").value_counts())
        out["counts"]["filtered_split_test_honest_items"] = dict(
            test_hon.top_backdoor_model.fillna("(none)").value_counts())
        out["counts"]["filtered_split_attack_items_all"] = dict(
            pd.concat([test_att, train]).top_backdoor_model.fillna("(none)").value_counts())
        out["counts"]["filtered_split_n"] = {"test_attack": int(len(test_att)),
                                            "test_honest": int(len(test_hon)),
                                            "train": int(len(train))}
        # The filtered split names a model the artifact does not: openai/gpt-4. Check whether
        # those problems' working backdoors in the artifact include the unattributed apps source.
        g4 = k[k.top_backdoor_model == "openai/gpt-4"].problem_id
        has_apps = [any(b["source"] == "apps" and b["passes_tests"] and b["backdoor_works"]
                        for b in bds[p]) for p in g4 if p in bds]
        out["gpt4_is_apps_source"] = {
            "n_filtered_split_problems_named_gpt4": int(len(g4)),
            "n_with_a_working_apps_source_backdoor_in_artifact": int(sum(has_apps)),
            "n_with_a_working_named_gpt4_backdoor_in_artifact": int(sum(
                any(b["model"] == "openai/gpt-4" for b in bds[p]) for p in g4 if p in bds))}
        all_named = sorted(set(k.top_backdoor_model.dropna()))
        out["counts"]["filtered_split_all_rows_named_models"] = all_named
    out["counts"] = {k: ({m: int(n) for m, n in v.items()} if isinstance(v, dict) else v)
                     for k, v in out["counts"].items()}

    print("attacking models (`unknown` = source apps, unattributed):")
    for k, v in out["counts"].items():
        if k in ("filtered_split_n", "filtered_split_all_rows_named_models",
                 "artifact_unknown_by_source"):
            print(f"  {k:36s} {v}")
            continue
        named = [m for m in v if m not in ("unknown", "(none)")]
        print(f"  {k:36s} {len(named)} named + {'unknown' if 'unknown' in v else '-'}: {v}")
    if "gpt4_is_apps_source" in out:
        g = out["gpt4_is_apps_source"]
        print(f"  filtered split's openai/gpt-4: {g['n_filtered_split_problems_named_gpt4']} "
              f"problems, {g['n_with_a_working_apps_source_backdoor_in_artifact']} with a working "
              f"apps-source (unattributed) backdoor in the artifact, "
              f"{g['n_with_a_working_named_gpt4_backdoor_in_artifact']} with any entry named "
              f"openai/gpt-4 there")

    # ---- B per attacking model, headline row's B' oof -----------------------------------------
    blob = json.load(open("sg_indep_first_passes_v2.json"))
    B = _oof_frame(blob["B_prime"])
    out["B_by_model_headline_oof"] = per_model_b(B, row_models["headline"])
    show("B per attacking model, headline row (623 problems), existing B' out-of-fold scores",
         out["B_by_model_headline_oof"])

    if not args.no_refit:
        from gate_s_baseline import build_pairs
        from gate_s_eval import evaluate
        pairs = build_pairs(df, None)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ev = evaluate(pairs, "B  human honest")
        oof = pd.DataFrame(ev["oof"]).set_index("problem_id")
        out["B_pool_refit"] = {"n": ev["n_pairs"], "fold_mean": ev["auroc"],
                               "pooled": ev["auroc_pooled_oof"]}
        out["B_by_model_pool_refit"] = per_model_b(oof, pool_model)
        show(f"B per attacking model, analysis pool ({ev['n_pairs']} problems), one refit "
             f"(fold mean {ev['auroc']:.4f}, pooled {ev['auroc_pooled_oof']:.4f})",
             out["B_by_model_pool_refit"])

    # ---- rho with Claude-written stored attacks ----------------------------------------------
    hm = row_models["headline"]
    claude = [p for p, m in hm.items() if m.startswith("anthropic/")]
    thinking = [p for p, m in hm.items() if m == "anthropic/claude-3-7-sonnet-thinking-latest"]
    other = [p for p, m in hm.items() if not m.startswith("anthropic/")]
    named_other = [p for p in other if hm[p] != "unknown"]
    print("\nheadline row restricted by stored attacker (existing oof scores, joint bootstrap):")
    out["rho_by_attacker_headline"] = {
        "all": rho_subset(blob, list(hm), "all stored attackers"),
        "claude": rho_subset(blob, claude, "anthropic/* attackers"),
        "claude_3_7_sonnet_thinking": rho_subset(blob, thinking,
                                                 "claude-3-7-sonnet-thinking only"),
        "non_claude": rho_subset(blob, other, "non-Claude (incl. unknown)"),
        "non_claude_named": rho_subset(blob, named_other, "non-Claude named models"),
    }

    json.dump(out, open(args.out, "w"), indent=2, default=float)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
