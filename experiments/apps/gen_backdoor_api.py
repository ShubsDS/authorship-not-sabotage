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

**A second same-generator model (2026-09-11, §15).** One model, one vendor, one sample is the
reviewer's objection to Gate S, so `--model` runs the identical pipeline on another Claude. Each
model gets its own price pair and its own default output/state names, keyed off a short slug, so no
Sonnet file can be overwritten by a Haiku run or the reverse:

    python gen_backdoor_api.py --model claude-haiku-4-5 --independent --pool analysis --dry-run
    python gen_backdoor_api.py --model claude-haiku-4-5 --independent --pool analysis   # bdind_haiku45.jsonl

**The independent arm does not need an honest pass file.** It is never shown a reference solution,
so nothing about it depends on which honest solutions passed; `--honest-pass` is therefore optional
for `--independent` and the arm runs on the whole `--pool` slice. Gating it on the honest pass file
(as the edit arm must) would only couple two independent batches and shrink the attack class for no
reason. The edit arm still requires `--honest-pass`, because it edits that solution.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_backdoor import PROMPT, PROMPT_INDEPENDENT, extract  # noqa: E402 - shared with the local arm
from gen_honest import already_done  # noqa: E402

DEFAULT_MODEL = "claude-sonnet-5"
MAX_TOKENS = 4096
# Thinking tokens are drawn from the SAME max_tokens budget as the reply. At 4,096 the 2026-09-10
# pilot spent the budget reasoning and truncated 77 of 120 replies before any code was emitted.
MAX_TOKENS_THINKING = 16384
BATCH_DISCOUNT = 0.5

# List price per million tokens, (input, output), before the 50% Batch API discount, and the slug
# that names this model's files. Adding a model here is the whole of what a new same-generator arm
# needs from this script. Slugs must be distinct: they are the only thing keeping two models'
# outputs apart on disk.
MODELS = {
    "claude-sonnet-5":  {"slug": "sonnet5",  "price_in": 2.00, "price_out": 10.00},
    "claude-haiku-4-5": {"slug": "haiku45",  "price_in": 1.00, "price_out":  5.00},
}


def model_paths(model: str, independent: bool) -> tuple[str, str, str, float, float]:
    """(out, state_file, log_name, price_in, price_out) for this model and arm."""
    if model not in MODELS:
        raise SystemExit(f"unknown model {model!r}; known: {', '.join(sorted(MODELS))}. "
                         f"Add it to MODELS with its list price before running it.")
    m = MODELS[model]
    stem = f"bdind_{m['slug']}" if independent else f"bd_{m['slug']}"
    return (f"{stem}.jsonl", f"{stem}.batch.json", f"{stem}.log",
            m["price_in"], m["price_out"])
BUDGET_CEILING = 135.0   # hard stop. Was $110; raised 2026-09-11 22:40 UTC: owner reports $83 of credit left with ~$101.6 booked; this session caps NEW spend at ~$33


def build(pool: pd.DataFrame, honest: dict, independent: bool = False,
          thinking: bool = False, model: str = DEFAULT_MODEL):
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    reqs, kept = [], []
    for _, row in pool.iterrows():
        sol = honest.get(row.problem_id, "")
        # The independent arm never shows the model a reference solution - that is the whole point -
        # but it stays on the same problems as the edit arm so the two are comparable.
        if not independent and not sol.strip():
            continue
        if independent:
            body = PROMPT_INDEPENDENT.replace("<question>", row.question)
        else:
            body = PROMPT.replace("<question>", row.question).replace("<solution>", sol)
        reqs.append(Request(custom_id=f"p{row.problem_id}",
                            params=MessageCreateParamsNonStreaming(
                                model=model,
                                max_tokens=(MAX_TOKENS_THINKING if thinking else MAX_TOKENS),
                                thinking=({"type": "adaptive"} if thinking
                                          else {"type": "disabled"}),
                                messages=[{"role": "user", "content": body}])))
        kept.append(row.problem_id)
    return reqs, kept


def estimate(pool: pd.DataFrame, honest: dict, spent_so_far: float,
             independent: bool = False, price_in: float = 2.00,
             price_out: float = 10.00, model: str = DEFAULT_MODEL) -> float:
    chars = sum(len(r.question) + (0 if independent else len(honest.get(r.problem_id, ""))) + 400
                for _, r in pool.iterrows())
    approx_in, approx_out = chars / 4, len(pool) * 700
    cost = (approx_in / 1e6 * price_in + approx_out / 1e6 * price_out) * BATCH_DISCOUNT
    print(f"model                 {model}  (${price_in:.2f}/${price_out:.2f} per M, "
          f"{int(BATCH_DISCOUNT*100)}% batch discount)")
    print(f"problems              {len(pool)}")
    what = "question + prompt" if independent else "question + honest solution + prompt"
    print(f"approx input tokens   {approx_in/1e6:.2f} M   ({what})")
    print(f"approx output tokens  {approx_out/1e6:.2f} M")
    print(f"estimated batch cost  ${cost:.2f}")
    worst = (approx_in / 1e6 * price_in
             + len(pool) * MAX_TOKENS / 1e6 * price_out) * BATCH_DISCOUNT
    print(f"WORST CASE            ${worst:.2f}  (every reply hits max_tokens={MAX_TOKENS})")
    print(f"already spent         ${spent_so_far:.2f}")
    print(f"projected total       ${spent_so_far + cost:.2f}  (ceiling ${BUDGET_CEILING:.0f})")
    return cost


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL, choices=sorted(MODELS),
                    help="which Claude writes the attack class. Each model has its own price pair "
                         "and its own default output/state names (bd[ind]_<slug>.jsonl), so two "
                         "models' arms cannot overwrite one another.")
    ap.add_argument("--honest-pass", default=None,
                    help="run_tests.py output for this model's honest class. REQUIRED for the edit "
                         "arm, which edits that solution. Optional for --independent, which is "
                         "never shown a reference solution and therefore does not depend on it; "
                         "omitted, the independent arm runs on the whole --pool slice.")
    ap.add_argument("--honest-gen", default=None)
    ap.add_argument("--pool", choices=["analysis", "generation", "all"], default="analysis",
                    help="slice of gate_s_pool.parquet to generate for, as in gen_honest_api.py. "
                         "Only used when the pool is not already restricted by --honest-pass.")
    ap.add_argument("--out", default=None,
                    help="default: bdind_<slug>.jsonl for --independent, else bd_<slug>.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--offset", type=int, default=0,
                    help="skip the first N eligible problems. With --limit this shards one round "
                         "across several small batches, which matters: measured 2026-09-11, a "
                         "200-request batch finished in 2.0 min while six concurrent 1,112-request "
                         "batches were still running at 100 min. Latency scales superlinearly with "
                         "batch size, so many small batches beat few large ones at identical cost.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--spent", type=float, default=0.0,
                    help="dollars already spent on this project, for the budget ceiling")
    ap.add_argument("--poll-seconds", type=int, default=60)
    ap.add_argument("--thinking", action="store_true",
                    help="adaptive thinking. The stored backdoors came from claude-3-7-sonnet-"
                         "THINKING, and writing a bug that passes every public test yet fires on a "
                         "self-chosen input is reasoning-heavy: without it the single-shot usable "
                         "rate was 3.6% (edit) and 1.7% (independent). Raises output tokens.")
    ap.add_argument("--state-suffix", default="",
                    help="distinguish concurrent batches of the same arm")
    ap.add_argument("--independent", action="store_true",
                    help="write the backdoored solution from the PROBLEM ALONE, never shown a "
                         "reference solution. The default arm edits the model's own honest "
                         "solution, which also makes the pair a near-copy; this one changes only "
                         "authorship, matching the benchmark's independent-programs structure.")
    args = ap.parse_args()

    if not args.independent and not args.honest_pass:
        raise SystemExit("--honest-pass is required for the edit arm: it edits that solution. "
                         "Only --independent may omit it.")
    default_out, default_state, log_name, price_in, price_out = model_paths(
        args.model, args.independent)
    out_path = args.out or default_out
    print(f"model {args.model}  ->  {out_path}   (suggested log: {log_name})")

    gen_path = args.honest_gen or (args.honest_pass.replace("pass_", "gen_")
                                   if args.honest_pass else None)
    honest = ({json.loads(l)["problem_id"]: json.loads(l)["code"]
               for l in open(gen_path) if l.strip()} if gen_path else {})
    pool = pd.read_parquet("gate_s_pool.parquet")
    pool["problem_id"] = pool.problem_id.astype(str)
    n_all = len(pool)
    done = already_done(out_path)
    if args.honest_pass:
        passers = {json.loads(l)["problem_id"] for l in open(args.honest_pass)
                   if l.strip() and json.loads(l)["passed"]}
        todo = pool[pool.problem_id.isin(passers) & ~pool.problem_id.isin(done)]
    else:
        # The independent arm on its own pool slice: no honest solution is ever shown, so nothing
        # here may depend on which honest solutions passed.
        passers = set()
        if args.pool == "analysis":
            pool = pool[pool.in_analysis_pool]
        elif args.pool == "generation":
            pool = pool[pool.in_generation_pool]
        print(f"pool slice '{args.pool}': {len(pool)} of {n_all} problems")
        todo = pool[~pool.problem_id.isin(done)]
    if args.offset:
        todo = todo.iloc[args.offset:]
    if args.limit:
        todo = todo.head(args.limit)
    print(f"honest passers {len(passers)}, already done {len(done)}, to generate {len(todo)}\n")
    if todo.empty:
        print("nothing to do")
        return

    cost = estimate(todo, honest, args.spent, args.independent, price_in, price_out, args.model)
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

    state_file = default_state
    if args.state_suffix:
        state_file = state_file.replace(".json", f".{args.state_suffix}.json")
    batch_id = None
    if os.path.exists(state_file):
        batch_id = json.load(open(state_file))["batch_id"]
        print(f"resuming batch {batch_id}")
    if batch_id is None:
        reqs, kept = build(todo, honest, args.independent, args.thinking, args.model)
        print(f"\nsubmitting {len(reqs)} backdoor requests to {args.model} ...")
        batch = client.messages.batches.create(requests=reqs)
        batch_id = batch.id
        json.dump({"batch_id": batch_id, "n": len(reqs)}, open(state_file, "w"))
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
    with open(out_path, "a") as fh:
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
                "problem_id": res.custom_id[1:], "model": args.model, "code": code,
                "arm": "independent" if args.independent else "edit",
                "thinking": bool(args.thinking),
                "backdoor_input": trig, "raw": text, "finish_reason": msg.stop_reason,
                "n_output_tokens": msg.usage.output_tokens,
                "truncated": msg.stop_reason == "max_tokens",
            }) + "\n")

    spend = (tin / 1e6 * price_in + tout / 1e6 * price_out) * BATCH_DISCOUNT
    print(f"\nsucceeded {n_ok} | no code {n_nocode} | no trigger {n_notrig} | truncated {n_trunc}")
    print(f"ACTUAL COST ${spend:.2f}   (running total ${args.spent + spend:.2f})")
    os.remove(state_file)
    slug = MODELS[args.model]["slug"]
    bdpass = ("bdindpass_" if args.independent else "bdpass_") + slug + ".jsonl"
    print(f"\nNext: verify_backdoor.py --backdoors {out_path} "
          f"--honest-gen {gen_path or f'gen_{slug}.jsonl'} --out {bdpass}")


if __name__ == "__main__":
    main()
