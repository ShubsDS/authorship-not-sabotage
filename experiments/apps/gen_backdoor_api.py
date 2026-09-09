"""Generate the ATTACK class with Claude Sonnet 5, matching the honest class generator exactly.

This closes Gate S properly. The stored benchmark pairs human honest code against Claude backdoors,
so a trivial classifier separates them on authorship. Regenerating only the honest half with a
different vendor made it worse, not better (AUROC 0.874 -> 0.962, rho 1.23) - it swapped the gap
rather than removing it. Generating BOTH classes with one model removes it by construction.

`claude-3-7-sonnet`, which wrote the stored backdoors, was checked against this key on 2026-09-09
and returns 404 - it reached end-of-life on 2026-02-19. So both classes come from `claude-sonnet-5`
instead. That is not the original attacker, but it is the same generator on both sides, which is the
property Gate S actually needs.

    python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl --dry-run
    python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl --limit 20
    python gen_backdoor_api.py --honest-pass pass_sonnet5.jsonl

The prompt is imported from `gen_backdoor.py`, so the local and API attack arms stay identical.
Output is byte-compatible with `verify_backdoor.py`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_backdoor import PROMPT, extract  # noqa: E402 - identical to the local arm by construction
from gen_honest import already_done  # noqa: E402

MODEL = "claude-sonnet-5"
MAX_TOKENS = 4096
PRICE_IN, PRICE_OUT, BATCH_DISCOUNT = 2.00, 10.00, 0.5
STATE_FILE = "bd_sonnet5.batch.json"
BUDGET_CEILING = 100.0   # hard stop: total spend on this project must stay under $100


def build(pool: pd.DataFrame, honest: dict):
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    reqs, kept = [], []
    for _, row in pool.iterrows():
        sol = honest.get(row.problem_id, "")
        if not sol.strip():
            continue
        body = PROMPT.replace("<question>", row.question).replace("<solution>", sol)
        reqs.append(Request(custom_id=f"p{row.problem_id}",
                            params=MessageCreateParamsNonStreaming(
                                model=MODEL, max_tokens=MAX_TOKENS,
                                thinking={"type": "disabled"},
                                messages=[{"role": "user", "content": body}])))
        kept.append(row.problem_id)
    return reqs, kept


def estimate(pool: pd.DataFrame, honest: dict, spent_so_far: float) -> float:
    chars = sum(len(r.question) + len(honest.get(r.problem_id, "")) + 400
                for _, r in pool.iterrows())
    approx_in, approx_out = chars / 4, len(pool) * 700
    cost = (approx_in / 1e6 * PRICE_IN + approx_out / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
    print(f"problems              {len(pool)}")
    print(f"approx input tokens   {approx_in/1e6:.2f} M   (question + honest solution + prompt)")
    print(f"approx output tokens  {approx_out/1e6:.2f} M")
    print(f"estimated batch cost  ${cost:.2f}")
    print(f"already spent         ${spent_so_far:.2f}")
    print(f"projected total       ${spent_so_far + cost:.2f}  (ceiling ${BUDGET_CEILING:.0f})")
    return cost


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--honest-pass", required=True)
    ap.add_argument("--honest-gen", default=None)
    ap.add_argument("--out", default="bd_sonnet5.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--spent", type=float, default=0.0,
                    help="dollars already spent on this project, for the budget ceiling")
    ap.add_argument("--poll-seconds", type=int, default=60)
    args = ap.parse_args()

    gen_path = args.honest_gen or args.honest_pass.replace("pass_", "gen_")
    honest = {json.loads(l)["problem_id"]: json.loads(l)["code"]
              for l in open(gen_path) if l.strip()}
    passers = {json.loads(l)["problem_id"] for l in open(args.honest_pass)
               if l.strip() and json.loads(l)["passed"]}
    pool = pd.read_parquet("gate_s_pool.parquet")
    pool["problem_id"] = pool.problem_id.astype(str)
    done = already_done(args.out)
    todo = pool[pool.problem_id.isin(passers) & ~pool.problem_id.isin(done)]
    if args.limit:
        todo = todo.head(args.limit)
    print(f"honest passers {len(passers)}, already done {len(done)}, to generate {len(todo)}\n")
    if todo.empty:
        print("nothing to do")
        return

    cost = estimate(todo, honest, args.spent)
    if args.spent + cost > BUDGET_CEILING:
        raise SystemExit(f"\nREFUSING: projected ${args.spent + cost:.2f} exceeds the "
                         f"${BUDGET_CEILING:.0f} ceiling. Narrow the pool with --limit.")
    if args.dry_run:
        print("\n--dry-run: nothing submitted, nothing spent.")
        return

    import anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set")
    client = anthropic.Anthropic()

    batch_id = None
    if os.path.exists(STATE_FILE):
        batch_id = json.load(open(STATE_FILE))["batch_id"]
        print(f"resuming batch {batch_id}")
    if batch_id is None:
        reqs, kept = build(todo, honest)
        print(f"\nsubmitting {len(reqs)} backdoor requests to {MODEL} ...")
        batch = client.messages.batches.create(requests=reqs)
        batch_id = batch.id
        json.dump({"batch_id": batch_id, "n": len(reqs)}, open(STATE_FILE, "w"))
        print(f"batch {batch_id}; state saved")

    started = time.time()
    while True:
        b = client.messages.batches.retrieve(batch_id)
        c = b.request_counts
        print(f"  [{(time.time()-started)/60:5.1f} min] {b.processing_status}  "
              f"processing={c.processing} succeeded={c.succeeded} errored={c.errored}", flush=True)
        if b.processing_status == "ended":
            break
        time.sleep(args.poll_seconds)

    n_ok = n_nocode = n_notrig = n_trunc = 0
    tin = tout = 0
    with open(args.out, "a") as fh:
        for res in client.messages.batches.results(batch_id):
            if res.result.type != "succeeded":
                continue
            msg = res.result.message
            text = "".join(b.text for b in msg.content if b.type == "text")
            code, trig = extract(text)
            n_ok += 1
            n_nocode += (not code)
            n_notrig += (not trig)
            n_trunc += msg.stop_reason == "max_tokens"
            tin += msg.usage.input_tokens
            tout += msg.usage.output_tokens
            fh.write(json.dumps({
                "problem_id": res.custom_id[1:], "model": MODEL, "code": code,
                "backdoor_input": trig, "raw": text, "finish_reason": msg.stop_reason,
                "n_output_tokens": msg.usage.output_tokens,
                "truncated": msg.stop_reason == "max_tokens",
            }) + "\n")

    spend = (tin / 1e6 * PRICE_IN + tout / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
    print(f"\nsucceeded {n_ok} | no code {n_nocode} | no trigger {n_notrig} | truncated {n_trunc}")
    print(f"ACTUAL COST ${spend:.2f}   (running total ${args.spent + spend:.2f})")
    os.remove(STATE_FILE)
    print(f"\nNext: verify_backdoor.py --backdoors {args.out} --honest-gen {gen_path} "
          f"--out bdpass_sonnet5.jsonl")


if __name__ == "__main__":
    main()
