"""Gate S honest-class generation through the Anthropic Batch API (Claude Sonnet 5).

The same experiment as `gen_honest.py`, with the generator swapped from a local open-weight model
to a Claude model. Why it is worth doing at all: the backdoors in this dataset were written by
`claude-3-7-sonnet-thinking`, so a Claude honest class is a *same-vendor* control and answers the
sharpest objection on record — *"a collapse might just be Qwen-vs-Claude."* No Qwen arm can.

    export ANTHROPIC_API_KEY=sk-ant-...
    python gen_honest_api.py --dry-run          # cost estimate, spends nothing
    python gen_honest_api.py --limit 20         # smoke test, ~$0.10
    python gen_honest_api.py                    # the real run, ~$17

Prompt and code extraction are **imported from gen_honest.py**, not copied, so the two arms cannot
drift apart. Output is byte-compatible with `run_tests.py` and `gate_s_eval.py`.

⚠️ **The exact attack model is retired.** `claude-3-7-sonnet-20250219` was withdrawn 2026-02-19, so
this is same-vendor and same-lineage but a *later generation*. Say that in Limitations; do not claim
a same-model control.

⚠️ **Two protocol differences from the vLLM arms, which the paper must state rather than bury:**
  1. **No temperature.** Sampling parameters were removed on Sonnet 5 and return a 400. The Qwen arms
     are greedy at temperature 0; this arm uses the model's own default sampling. It is therefore not
     reproducible in the bit-exact way the local arms are.
  2. **Thinking is off by default here.** The attacks came from a *thinking* model, so `--thinking`
     exists; but thinking tokens are not part of the emitted code, they roughly double cost, and the
     object of study is the code. Whichever is used, report it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_honest import PROMPT, already_done, extract_code  # noqa: E402  - identical by construction
from gen_backdoor import PROMPT_INDEPENDENT_HONEST  # noqa: E402  - arm 3, the prompt-matched honest class
from gen_backdoor import extract as extract_two_blocks  # noqa: E402  - (code, input), same parser as the attack arm

MODEL = "claude-sonnet-5"
MAX_TOKENS = 4096          # same ceiling as the vLLM arms; 2048 truncated 34% of them
BATCH_LIMIT = 100_000      # API maximum requests per batch
# Sonnet 5 list price per million tokens; the Batch API bills at 50%.
PRICE_IN, PRICE_OUT, BATCH_DISCOUNT = 2.00, 10.00, 0.5
STATE_FILE = "gen_sonnet5.batch.json"
# Arm 3 (--matched) keeps its own output, state and log so nothing of the original honest
# arm can be overwritten by a resume or a re-run.
STATE_FILE_MATCHED = "genm_sonnet5.batch.json"
OUT_MATCHED = "genm_sonnet5.jsonl"


def build_requests(pool: pd.DataFrame, thinking: bool, matched: bool = False):
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    reqs = []
    for _, row in pool.iterrows():
        # --matched: gen_backdoor.PROMPT_INDEPENDENT_HONEST, which is PROMPT_INDEPENDENT with only
        # the flaw sentence replaced. `<question>` is substituted exactly as gen_backdoor_api.build
        # does (.replace, not .format - the prompt body contains braces).
        body = (PROMPT_INDEPENDENT_HONEST.replace("<question>", row.question) if matched
                else PROMPT.format(question=row.question))
        params = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "messages": [{"role": "user", "content": body}],
        }
        # Sonnet 5 rejects temperature/top_p/top_k with a 400, so sampling is left at the default.
        params["thinking"] = {"type": "adaptive"} if thinking else {"type": "disabled"}
        reqs.append(Request(custom_id=f"p{row.problem_id}",
                            params=MessageCreateParamsNonStreaming(**params)))
    return reqs


def estimate(pool: pd.DataFrame) -> None:
    approx_in = (pool.question.str.len() / 4 + 60).sum()
    approx_out = len(pool) * 600
    cost = (approx_in / 1e6 * PRICE_IN + approx_out / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
    print(f"problems              {len(pool)}")
    print(f"approx input tokens   {approx_in/1e6:.2f} M")
    print(f"approx output tokens  {approx_out/1e6:.2f} M   (600/problem, no thinking)")
    print(f"estimated batch cost  ${cost:.2f}   ({MODEL}, 50% batch discount)")
    worst = (approx_in / 1e6 * PRICE_IN + len(pool) * MAX_TOKENS / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
    print(f"WORST CASE            ${worst:.2f}   (every reply hits max_tokens={MAX_TOKENS})")
    print("Output length is the uncertain half; treat the estimate as +/- 50%. The worst case is")
    print("what the $100 project ceiling has to survive, so it is the number that gates the run.")


def collect(client, batch_id: str, out_path: str, matched: bool = False) -> None:
    """Write one JSONL record per result. Results arrive in arbitrary order - key by custom_id."""
    n_ok = n_err = n_trunc = n_nocode = n_noinput = 0
    tok_in = tok_out = 0
    with open(out_path, "a") as fh:
        for result in client.messages.batches.results(batch_id):
            pid = result.custom_id[1:]          # strip the "p" prefix
            kind = result.result.type
            if kind != "succeeded":
                n_err += 1
                err = getattr(result.result, "error", None)
                print(f"  [{pid}] {kind}: {getattr(err, 'type', '')}", file=sys.stderr)
                continue
            msg = result.result.message
            text = "".join(b.text for b in msg.content if b.type == "text")
            # The matched prompt asks for two fenced blocks, so it is parsed with the attack arm's
            # own parser; the `input` block is recorded as `check_input` and is not used anywhere
            # downstream (no trigger semantics - it is an input the model says it checked).
            check_input = ""
            if matched:
                code, check_input = extract_two_blocks(text)
            else:
                code = extract_code(text)
            truncated = msg.stop_reason == "max_tokens"
            n_ok += 1
            n_trunc += truncated
            n_nocode += (not code)
            n_noinput += (matched and not check_input)
            tok_in += msg.usage.input_tokens
            tok_out += msg.usage.output_tokens
            rec = {
                "problem_id": pid,
                "model": MODEL,
                "code": code,
                "raw": text,
                "finish_reason": msg.stop_reason,
                "n_prompt_tokens": msg.usage.input_tokens,
                "n_output_tokens": msg.usage.output_tokens,
                "truncated": bool(truncated),
            }
            if matched:
                rec["check_input"] = check_input
                rec["prompt"] = "PROMPT_INDEPENDENT_HONEST"
            fh.write(json.dumps(rec) + "\n")

    cost = (tok_in / 1e6 * PRICE_IN + tok_out / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
    print(f"\nsucceeded                 {n_ok}")
    print(f"errored                   {n_err}")
    print(f"truncated at max_tokens   {n_trunc}")
    print(f"no extractable code block {n_nocode}")
    if matched:
        print(f"no ```input block          {n_noinput}")
    print(f"tokens                    {tok_in/1e6:.2f} M in / {tok_out/1e6:.2f} M out")
    print(f"ACTUAL COST               ${cost:.2f}")
    pass_out = "passm_sonnet5.jsonl" if matched else "pass_sonnet5.jsonl"
    print(f"\nwrote {out_path}. Next: run_tests.py --solutions {out_path} --out {pass_out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None,
                    help="default gen_sonnet5.jsonl, or genm_sonnet5.jsonl with --matched")
    ap.add_argument("--limit", type=int, default=0, help="first N problems, for a smoke test")
    ap.add_argument("--pool", choices=["analysis", "generation", "all"], default="analysis",
                    help="which slice of gate_s_pool.parquet to generate for. The vLLM arms use "
                         "'all' because local generation is free; this arm is metered, and only "
                         "the analysis pool can ever reach a result, so it defaults to 'analysis' "
                         "(1,444: passing solution AND backdoor_works AND deterministic). "
                         "Generating the other 3,556 would cost ~3.5x and change no number.")
    ap.add_argument("--matched", action="store_true",
                    help="ARM 3: the PROMPT-MATCHED honest class. Uses "
                         "gen_backdoor.PROMPT_INDEPENDENT_HONEST - the independent attack prompt "
                         "with only its flaw sentence replaced - instead of gen_honest.PROMPT, "
                         "parses the reply with gen_backdoor.extract and records the ```input "
                         "block as `check_input`. RESULTS.md 11 showed the residual S is program "
                         "LAYOUT the attack prompt elicits, so the same-generator arm held the "
                         "model constant but not the prompt; this class holds both. Restricted to "
                         "the problems whose ORIGINAL honest program passes (--honest-pass), "
                         "which is the attack arm's own pool. Own output, state file and log: "
                         "nothing of the original honest arm is touched.")
    ap.add_argument("--honest-pass", default="pass_sonnet5.jsonl",
                    help="with --matched, generate only for problems whose original honest "
                         "program passed our harness (the attack arm's eligibility rule)")
    ap.add_argument("--max-cost", type=float, default=0.0,
                    help="refuse to submit if the estimated cost exceeds this many dollars")
    ap.add_argument("--thinking", action="store_true", help="adaptive thinking on (roughly 2x cost)")
    ap.add_argument("--dry-run", action="store_true", help="estimate cost and exit, spending nothing")
    ap.add_argument("--poll-seconds", type=int, default=60)
    args = ap.parse_args()
    out_path = args.out or (OUT_MATCHED if args.matched else "gen_sonnet5.jsonl")
    state_file = STATE_FILE_MATCHED if args.matched else STATE_FILE
    if args.matched:
        print(f"ARM 3: prompt-matched honest class (gen_backdoor.PROMPT_INDEPENDENT_HONEST)")
        print(f"out {out_path}   state {state_file}")

    pool = pd.read_parquet("gate_s_pool.parquet")
    pool["problem_id"] = pool.problem_id.astype(str)
    n_all = len(pool)
    if args.pool == "analysis":
        pool = pool[pool.in_analysis_pool]
    elif args.pool == "generation":
        pool = pool[pool.in_generation_pool]
    print(f"pool slice '{args.pool}': {len(pool)} of {n_all} problems")
    if args.matched:
        # Exactly the problems the attack arm was generated on: those whose ORIGINAL honest
        # program passes our harness (gen_backdoor_api.py's filter, same file).
        passers = {json.loads(l)["problem_id"] for l in open(args.honest_pass)
                   if l.strip() and json.loads(l)["passed"]}
        pool = pool[pool.problem_id.isin(passers)]
        print(f"--matched: restricted to the {len(passers)} passers of {args.honest_pass} "
              f"-> {len(pool)} problems in the analysis pool")
    done = already_done(out_path)
    todo = pool[~pool.problem_id.isin(done)]
    if args.limit:
        todo = todo.head(args.limit)
    print(f"pool {len(pool)}, already done {len(done)}, to generate {len(todo)}\n")
    if todo.empty:
        print("nothing to do")
        return

    estimate(todo)
    if args.max_cost:
        approx_in = (todo.question.str.len() / 4 + 60).sum()
        est = (approx_in / 1e6 * PRICE_IN + len(todo) * 600 / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
        if est > args.max_cost:
            raise SystemExit(f"\nREFUSING: estimated ${est:.2f} exceeds --max-cost "
                             f"${args.max_cost:.2f}. Narrow the pool with --limit.")
        print(f"\nunder the ${args.max_cost:.2f} cap (estimate ${est:.2f})")
    if args.dry_run:
        print("\n--dry-run: nothing submitted, nothing spent.")
        return
    if len(todo) > BATCH_LIMIT:
        raise SystemExit(f"{len(todo)} requests exceeds the {BATCH_LIMIT} per-batch limit")

    import anthropic
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        raise SystemExit("set ANTHROPIC_API_KEY (a Console API key - a Max subscription is not this)")
    client = anthropic.Anthropic()

    # Resume an in-flight batch rather than paying for it twice.
    batch_id = None
    if os.path.exists(state_file):
        batch_id = json.load(open(state_file)).get("batch_id")
        print(f"resuming batch {batch_id} from {state_file}")

    if batch_id is None:
        print(f"\nsubmitting {len(todo)} requests to {MODEL} "
              f"(thinking {'adaptive' if args.thinking else 'off'}) ...")
        batch = client.messages.batches.create(
            requests=build_requests(todo, args.thinking, args.matched))
        batch_id = batch.id
        json.dump({"batch_id": batch_id, "model": MODEL, "n": len(todo),
                   "thinking": args.thinking, "matched": args.matched,
                   "prompt": "PROMPT_INDEPENDENT_HONEST" if args.matched else "PROMPT"},
                  open(state_file, "w"))
        print(f"batch {batch_id} submitted; state saved to {state_file}")

    started = time.time()
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        c = batch.request_counts
        print(f"  [{(time.time()-started)/60:5.1f} min] {batch.processing_status}  "
              f"processing={c.processing} succeeded={c.succeeded} errored={c.errored}", flush=True)
        if batch.processing_status == "ended":
            break
        time.sleep(args.poll_seconds)

    collect(client, batch_id, out_path, args.matched)
    os.remove(state_file)


if __name__ == "__main__":
    main()
