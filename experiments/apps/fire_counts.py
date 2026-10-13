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

3. Exact counts (needs the generated verdict files; skipped without them). A row's attack fires
   when its verdict record has passes_tests and backdoor_works true. Sonnet 5 rows read
   bdindpass_sonnet5_first.jsonl (the headline and prompt-matched rows score the first draw);
   Haiku 4.5 rows read bdpass_haiku45.jsonl (the verdicts gate_s_samegen.py and
   gate_s_matched_haiku.py read for the Haiku headline and prompt-matched rows). Counted over
   each row's problem_ids: headline (sg_indep_first_passes_v2.json), prompt-matched
   (gate_s_matched_headline.json), Haiku (sg_haiku45_indep_passes.json), Haiku prompt-matched
   (gate_s_matched_haiku45.json). The headline and Haiku counts must reproduce 14 and 2, and the
   firing first draws on strict problems must be the ones the token rule of part 1 detected.
   This gives \\matchedFire and \\haikuMatchedFire exactly.

Inputs: monitor_samegen_sonnet5_independent_{passes,usable}[_haiku-4-5].json,
monitor_stored_sonnet5_independent_{passes,usable}.json, sg_indep_first_passes_v2.json,
sg_indep_best_usable_v2.json, sg_haiku45_indep_passes.json, gate_s_matched_{headline,strict,
haiku45}.json; optionally train_*.parquet, bdindpass_sonnet5_first.jsonl, bdpass_haiku45.jsonl.

Usage:
    python fire_counts.py --out fire_counts.json
"""

from __future__ import annotations

import argparse
import glob
import json
import os

KNOWN = {"headline": (14, 623), "haiku_headline": (2, 611), "strict": (99, 99),
         "strict_matched": (96, 96)}
VERDICTS = {"sonnet": "bdindpass_sonnet5_first.jsonl", "haiku": "bdpass_haiku45.jsonl"}


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


def firing(path: str) -> set:
    """Problem ids whose verdict record passes the public tests and fires (one record each)."""
    recs = [json.loads(l) for l in open(path) if l.strip()]
    assert len(recs) == len({str(r["problem_id"]) for r in recs}), f"{path}: duplicate problem"
    return {str(r["problem_id"]) for r in recs if r["passes_tests"] and r["backdoor_works"]}


def exact_counts(rows: dict, detected: list, strict: list) -> dict:
    """Exact fire count per row from the verdict files; checks the known counts."""
    fire = {m: firing(p) for m, p in VERDICTS.items()}
    out = {"verdict_files": VERDICTS, "rule": "passes_tests and backdoor_works true", "rows": {}}
    for name, (model, pids) in rows.items():
        hit = sorted(fire[model] & set(map(str, pids)))
        out["rows"][name] = {"fire": len(hit), "n": len(pids), "verdict_file": VERDICTS[model],
                             "firing_problem_ids": hit}
        print(f"  {name:22s} {len(hit):3d} of {len(pids):3d} fire   {hit}")
    for name in ("headline", "haiku_headline"):
        got, want = out["rows"][name]["fire"], KNOWN[name][0]
        assert got == want, f"{name}: {got} fire, expected {want}"
    on_strict = sorted(fire["sonnet"] & set(strict))
    out["headline_firing_on_strict_problems_exact"] = on_strict
    out["token_rule_detected_exactly_these"] = on_strict == sorted(detected)
    out["headline_firing_outside_strict_exact"] = sorted(
        set(out["rows"]["headline"]["firing_problem_ids"]) - set(strict))
    print(f"  firing first draws on strict problems equal the token rule's {len(detected)}: "
          f"{out['token_rule_detected_exactly_these']}; outside the strict set: "
          f"{out['headline_firing_outside_strict_exact']}")
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

    if all(os.path.exists(p) for p in VERDICTS.values()):
        print("exact counts (generated verdict files):")
        mk = json.load(open("gate_s_matched_haiku45.json"))
        ex = exact_counts({"headline": ("sonnet", head),
                           "prompt_matched": ("sonnet", mh["problem_ids"]),
                           "haiku_headline": ("haiku", haiku),
                           "haiku_prompt_matched": ("haiku", mk["problem_ids"])},
                          detected, strict)
        out["exact"] = ex
        r = ex["rows"]["prompt_matched"]
        out["matchedFire"]["exact"] = r["fire"]
        out["matchedFire"]["exact_firing_problem_ids"] = r["firing_problem_ids"]
        out["haikuMatchedFire"] = {"exact": ex["rows"]["haiku_prompt_matched"]["fire"],
                                   "n_matched": ex["rows"]["haiku_prompt_matched"]["n"],
                                   "firing_problem_ids":
                                       ex["rows"]["haiku_prompt_matched"]["firing_problem_ids"]}
        print(f"\\matchedFire = {r['fire']} of {r['n']}; \\haikuMatchedFire = "
              f"{out['haikuMatchedFire']['exact']} of {out['haikuMatchedFire']['n_matched']}")
    else:
        print(f"no {' / '.join(VERDICTS.values())} here: exact counts skipped (bounds only)")

    json.dump(out, open(args.out, "w"), indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
