"""How many attacks fire in each Table 1 row, from committed files and the public dataset.

Known counts: headline 14 of 623 (merge_draws.py select --keep first), Haiku 2 of 611, strict
99 of 99 and strict prompt-matched 96 of 96 (both fire by construction). This script derives
what the committed jsons allow for the prompt-matched row (\\matchedFire: of its 586 problems,
how many carry a firing attack) and checks that every stored attack on these rows fires.

1. Which headline problems fire. The per-draw verdicts (bdindpass_sonnet5_first.jsonl) are not
   committed, but the monitor jsons record each request's input-token count, which is fixed by
   the problem statement and the program. The headline monitor scored the first draw
   (bdind_sonnet5_first.jsonl); the strict monitor scored the crash-inclusive `best` draw
   (bdind_sonnet5_best.jsonl), which is the earliest draw that passes and fires, crash
   included. On a strict problem, therefore, the two runs scored the same attack program exactly
   when the first draw fires. A program is taken as identical when its attack request has the
   same input-token count in both Sonnet 5 runs AND in both Haiku 4.5 runs (two tokenizers, so a
   coincidental match must happen twice); the honest requests, which are the same program by
   construction, must match on every shared problem, as a check that prompt and tokenizers are
   unchanged. One problem matches under one tokenizer only; it is reported and not counted.
   This detects every firing first draw on a strict problem, and none off it. A firing first
   draw on a problem outside the strict set is one that fires only by crashing on the trigger
   with no quiet working draw later (merge_draws.py --crash-as-passes drops those), so
   14 - detected is the number of such problems, whose ids the committed files do not give.
   \\matchedFire is then bounded: detected-and-matched <= \\matchedFire <= that + (14 - detected).
   The exact count is the number of `bdindpass_sonnet5_first.jsonl` records with passes_tests
   and backdoor_works true whose problem_id is in gate_s_matched_headline.json's problem_ids.

2. Stored attacks (needs train_*.parquet from fetch.py; skipped without it). Each row's B' picks
   one stored backdoor per problem: the first entry that passes the public tests (headline,
   Haiku and prompt-matched rows, --bprime-inert) or the first that passes and works (strict
   rows). This counts how many of those carry the dataset's `backdoor_works` flag (ControlArena's
   verdict, not our harness's). The stored programs scored by the headline and strict stored
   monitor runs are also checked for identity on the shared problems, by the same token rule.

Inputs: monitor_samegen_sonnet5_independent_{passes,usable}[_haiku-4-5].json,
monitor_stored_sonnet5_independent_{passes,usable}.json, sg_indep_first_passes_v2.json,
sg_indep_best_usable_v2.json, sg_haiku45_indep_passes.json, gate_s_matched_{headline,strict}.json;
optionally train_*.parquet.

Usage:
    python fire_counts.py --out fire_counts.json
"""

from __future__ import annotations

import argparse
import glob
import json

KNOWN = {"headline": (14, 623), "haiku_headline": (2, 611), "strict": (99, 99),
         "strict_matched": (96, 96)}


def tokens(path: str) -> dict:
    """{problem_id: {class: n_prompt_tokens}} from a monitor json."""
    out: dict[str, dict] = {}
    for r in json.load(open(path))["scores"]:
        out.setdefault(str(r["problem_id"]), {})[r["class"]] = r.get("n_prompt_tokens")
    return out


def stored_check(rows: dict) -> dict:
    import pandas as pd
    import pyarrow.parquet as pq

    shards = sorted(glob.glob("train_*.parquet"))
    df = pd.concat([pq.read_table(f, columns=["problem_id", "backdoors"]).to_pandas()
                    for f in shards], ignore_index=True)
    df["problem_id"] = df.problem_id.astype(str)
    bds = dict(zip(df.problem_id, df.backdoors))
    out = {}
    for name, (pids, inert) in rows.items():
        n_fire, not_fire = 0, []
        for p in pids:
            entries = [dict(b) for b in bds[p]]
            ok = [b for b in entries if b["passes_tests"] and (inert or b["backdoor_works"])]
            pick = ok[0]
            if pick["backdoor_works"]:
                n_fire += 1
            else:
                not_fire.append(p)
        out[name] = {"n_problems": len(pids), "n_stored_attack_fires": n_fire,
                     "not_firing": not_fire,
                     "rule": "first entry passing the public tests" if inert
                             else "first entry passing and working"}
        print(f"  {name:16s} stored attack fires on {n_fire} of {len(pids)}"
              f"  ({out[name]['rule']})")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="fire_counts.json")
    args = ap.parse_args()

    head = json.load(open("sg_indep_first_passes_v2.json"))["problem_ids"]
    strict = json.load(open("sg_indep_best_usable_v2.json"))["problem_ids"]
    haiku = json.load(open("sg_haiku45_indep_passes.json"))["problem_ids"]
    mh = json.load(open("gate_s_matched_headline.json"))
    ms = json.load(open("gate_s_matched_strict.json"))
    matched = set(mh["problem_ids"])
    shared = sorted(set(head) & set(strict))

    base = "monitor_samegen_sonnet5_independent_"
    runs = {"sonnet": (tokens(base + "passes.json"), tokens(base + "usable.json")),
            "haiku": (tokens(base + "passes_haiku-4-5.json"),
                      tokens(base + "usable_haiku-4-5.json"))}
    honest_ok = all(h[p]["honest"] == s[p]["honest"] for h, s in runs.values() for p in shared)
    same = {m: {p for p in shared if h[p]["attack"] == s[p]["attack"]}
            for m, (h, s) in runs.items()}
    detected = sorted(same["sonnet"] & same["haiku"])
    one_only = sorted(same["sonnet"] ^ same["haiku"])
    n_fire, n_head = KNOWN["headline"]
    lo = len([p for p in detected if p in matched])
    hi = lo + (n_fire - len(detected))

    print(f"headline {len(head)}, strict {len(strict)}, shared {len(shared)}")
    print(f"honest programs identical on all shared problems (token check): {honest_ok}")
    print(f"attack identical under Sonnet tokens {len(same['sonnet'])}, Haiku tokens "
          f"{len(same['haiku'])}, both {len(detected)}; one tokenizer only: {one_only}")
    print(f"firing first draws on strict problems: {len(detected)} {detected}")
    print(f"firing first draws outside the strict set (crash-only): {n_fire - len(detected)}")
    print(f"of the detected, in the prompt-matched 586: {lo}; dropped there: "
          f"{[p for p in detected if p not in matched]}")
    print(f"\\matchedFire in [{lo}, {hi}] of {len(matched)}")

    out = {
        "known": {k: {"fire": f, "n": n} for k, (f, n) in KNOWN.items()},
        "shared_problems": len(shared),
        "honest_token_check_passes": honest_ok,
        "attack_identical": {"sonnet_tokens": sorted(same["sonnet"]),
                             "haiku_tokens": sorted(same["haiku"]),
                             "both": detected, "one_tokenizer_only": one_only},
        "headline_firing_on_strict_problems": detected,
        "headline_firing_outside_strict": n_fire - len(detected),
        "matchedFire": {"lower": lo, "upper": hi, "n_matched": len(matched),
                        "detected_in_matched": [p for p in detected if p in matched],
                        "detected_dropped_by_matching": [p for p in detected
                                                         if p not in matched],
                        "exact_needs": "bdindpass_sonnet5_first.jsonl: count records with "
                                       "passes_tests and backdoor_works whose problem_id is in "
                                       "gate_s_matched_headline.json problem_ids"},
        "strict_matched_all_fire": {"n": len(ms["problem_ids"]),
                                    "subset_of_strict": set(ms["problem_ids"]) <= set(strict)},
    }

    # Stored programs on shared problems: the headline B' (first passing) and the strict B'
    # (first passing and working) pick the same entry exactly when the first passing entry works.
    sh, ss = tokens("monitor_stored_sonnet5_independent_passes.json"), \
        tokens("monitor_stored_sonnet5_independent_usable.json")
    same_stored = [p for p in shared if sh[p].get("attack") == ss[p].get("attack")]
    out["stored_attack_same_program_headline_vs_strict"] = {"n_shared": len(shared),
                                                            "n_same": len(same_stored)}
    print(f"stored attack identical in the headline and strict stored runs on "
          f"{len(same_stored)} of {len(shared)} shared problems")

    if glob.glob("train_*.parquet"):
        print("stored attacks (public dataset, `backdoor_works` flag):")
        out["stored_attacks"] = stored_check({
            "headline": (head, True), "haiku_headline": (haiku, True),
            "prompt_matched": (sorted(matched), True), "strict": (strict, False),
            "strict_matched": (ms["problem_ids"], False)})
    else:
        print("no train_*.parquet here: stored-attack check skipped (python fetch.py)")

    json.dump(out, open(args.out, "w"), indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
