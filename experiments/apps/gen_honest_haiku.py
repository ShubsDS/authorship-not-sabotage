"""Gate S honest classes from Claude Haiku 4.5 — the second same-generator model (§15).

Gate S as it stands rests on one model, one vendor, one sample; `gen_honest_api.py` +
`gen_backdoor_api.py` gave Claude Sonnet 5 both sides of the pair and returned S = 0.7512 against
B' = 0.8658 (ρ = 0.687). The sharpest remaining objection is that a single generator's idiolect
could carry the whole residual. This script runs the identical honest-side pipeline on
`claude-haiku-4-5`, so the two models are comparable row for row.

Two honest classes, matching the Sonnet arm exactly:

    python gen_honest_haiku.py --dry-run              # gen_haiku45.jsonl,  gen_honest.PROMPT
    python gen_honest_haiku.py
    python gen_honest_haiku.py --matched --dry-run    # genm_haiku45.jsonl, PROMPT_INDEPENDENT_HONEST
    python gen_honest_haiku.py --matched

**Why a wrapper and not `gen_honest_api.py --model`.** That file belongs to the Sonnet arm and is
owned by another worker. Its `build_requests`/`collect` are importable without side effects (the
module body only does a `sys.path.insert` and three imports) but they close over module-level
`MODEL`, `PRICE_IN`/`PRICE_OUT` and `STATE_FILE`, none of which is a parameter — calling them here
would stamp `"model": "claude-sonnet-5"` into Haiku records and price them at Sonnet rates. That is
not a cosmetic problem: `gate_s_samegen.py` refuses outright when the honest and attack files
disagree on `model`, so the run would die at analysis time with a confusing message. So the batch
loop is copied and the *prompts and parsers* are imported, which is where drift would actually
matter: `gen_honest.PROMPT`, `gen_honest.extract_code`, `gen_backdoor.PROMPT_INDEPENDENT_HONEST`
and `gen_backdoor.extract` are the same objects both arms use.

Protocol, identical to the Sonnet arm and stated rather than buried:
  * `max_tokens = 4096`, the same ceiling as every other arm.
  * **Thinking disabled.** The object of study is the emitted code.
  * **Default sampling.** These models reject `temperature`/`top_p`/`top_k` with a 400, so there is
    no temperature-0 setting to match the vLLM arms with; neither Claude arm is bit-reproducible.
  * One draw per problem, no best-of-n — further selection would install the selection artifact
    this paper audits.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_honest import PROMPT, already_done, extract_code  # noqa: E402 - shared with every honest arm
from gen_backdoor import PROMPT_INDEPENDENT_HONEST  # noqa: E402 - arm 3, the prompt-matched honest class
from gen_backdoor import extract as extract_two_blocks  # noqa: E402 - (code, input), the attack arm's parser

MODEL = "claude-haiku-4-5"
MAX_TOKENS = 4096
BATCH_LIMIT = 100_000
# Haiku 4.5 list price per million tokens; the Batch API bills at 50%.
PRICE_IN, PRICE_OUT, BATCH_DISCOUNT = 1.00, 5.00, 0.5

OUT = "gen_haiku45.jsonl"
OUT_MATCHED = "genm_haiku45.jsonl"
STATE_FILE = "gen_haiku45.batch.json"
STATE_FILE_MATCHED = "genm_haiku45.batch.json"
BUDGET_CEILING = 135.0   # the project ceiling, mirrored from gen_backdoor_api.py


def build_requests(pool: pd.DataFrame, thinking: bool, matched: bool = False):
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    reqs = []
    for _, row in pool.iterrows():
        # `.replace` for the matched prompt (its body contains braces, so `.format` would raise);
        # `.format` for the plain one. Both exactly as the Sonnet arm substitutes them.
        body = (PROMPT_INDEPENDENT_HONEST.replace("<question>", row.question) if matched
                else PROMPT.format(question=row.question))
        reqs.append(Request(custom_id=f"p{row.problem_id}",
                            params=MessageCreateParamsNonStreaming(
                                model=MODEL,
                                max_tokens=MAX_TOKENS,
                                thinking=({"type": "adaptive"} if thinking
                                          else {"type": "disabled"}),
                                messages=[{"role": "user", "content": body}])))
    return reqs


def estimate(pool: pd.DataFrame, spent_so_far: float, matched: bool) -> float:
    extra = len(PROMPT_INDEPENDENT_HONEST) if matched else len(PROMPT)
    approx_in = (pool.question.str.len() / 4 + extra / 4).sum()
    approx_out = len(pool) * 700
    cost = (approx_in / 1e6 * PRICE_IN + approx_out / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
    worst = (approx_in / 1e6 * PRICE_IN
             + len(pool) * MAX_TOKENS / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
    print(f"model                 {MODEL}  (${PRICE_IN:.2f}/${PRICE_OUT:.2f} per M, "
          f"{int(BATCH_DISCOUNT*100)}% batch discount)")
    print(f"prompt                {'PROMPT_INDEPENDENT_HONEST' if matched else 'gen_honest.PROMPT'}")
    print(f"problems              {len(pool)}")
    print(f"approx input tokens   {approx_in/1e6:.2f} M")
    print(f"approx output tokens  {approx_out/1e6:.2f} M   (700/problem, no thinking)")
    print(f"estimated batch cost  ${cost:.2f}")
    print(f"WORST CASE            ${worst:.2f}   (every reply hits max_tokens={MAX_TOKENS})")
    print(f"already spent         ${spent_so_far:.2f}")
    print(f"projected total       ${spent_so_far + cost:.2f}  (ceiling ${BUDGET_CEILING:.0f})")
    print("The Sonnet honest arm came in 72% over a 600-token/problem estimate (§4.2); the estimate")
    print("here assumes 700 and is still the uncertain half. The worst case is what gates the run.")
    return cost


def collect(client, batch_id: str, out_path: str, matched: bool) -> float:
    """One JSONL record per result. Results arrive in arbitrary order — key by custom_id."""
    n_ok = n_err = n_trunc = n_nocode = n_noinput = 0
    tok_in = tok_out = 0
    with open(out_path, "a") as fh:
        for result in client.messages.batches.results(batch_id):
            pid = result.custom_id[1:]          # strip the "p" prefix
            if result.result.type != "succeeded":
                n_err += 1
                err = getattr(result.result, "error", None)
                print(f"  [{pid}] {result.result.type}: {getattr(err, 'type', '')}",
                      file=sys.stderr)
                continue
            msg = result.result.message
            text = "".join(b.text for b in msg.content if b.type == "text")
            # The matched prompt asks for two fenced blocks, so it is parsed with the attack arm's
            # own parser; the `input` block is stored as `check_input` and is NOT a trigger and is
            # not used downstream — it is an input the model claims to have checked.
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
        print(f"no ```input block         {n_noinput}")
    print(f"tokens                    {tok_in/1e6:.2f} M in / {tok_out/1e6:.2f} M out")
    print(f"ACTUAL COST               ${cost:.2f}")
    pass_out = "passm_haiku45.jsonl" if matched else "pass_haiku45.jsonl"
    print(f"\nwrote {out_path}. Next: run_tests.py --solutions {out_path} --out {pass_out}")
    return cost


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--matched", action="store_true",
                    help="generate the PROMPT-MATCHED honest class: gen_backdoor."
                         "PROMPT_INDEPENDENT_HONEST, which is PROMPT_INDEPENDENT with only the "
                         "flaw sentence replaced. Its reply is two fenced blocks; the second is "
                         "stored as `check_input`. Separate output and state files, so a matched "
                         "run can never overwrite the plain honest class.")
    ap.add_argument("--out", default=None,
                    help=f"default {OUT_MATCHED} with --matched, else {OUT}")
    ap.add_argument("--limit", type=int, default=0, help="first N problems, for a smoke test")
    ap.add_argument("--problem-ids", default=None,
                    help="JSON file holding a list of problem_ids, or an object with a "
                         "`problem_ids` key (a gate_s_samegen.py output json is exactly that). "
                         "Restricts generation to those problems. Used for the MATCHED class: "
                         "gate_s_matched.py drops every problem where the matched honest program "
                         "is missing or fails, and keeps only problems already in the Gate S set, "
                         "so generating the matched class outside that set buys nothing and costs "
                         "the same per problem as inside it.")
    ap.add_argument("--pool", choices=["analysis", "generation", "all"], default="analysis",
                    help="slice of gate_s_pool.parquet. 'analysis' (1,444) is the only slice that "
                         "can reach a result and is what the Sonnet honest arm used.")
    ap.add_argument("--thinking", action="store_true",
                    help="adaptive thinking on (roughly 2x cost). OFF for every published row.")
    ap.add_argument("--dry-run", action="store_true",
                    help="estimate cost and exit, spending nothing")
    ap.add_argument("--spent", type=float, default=0.0,
                    help="dollars already spent on this project, for the budget ceiling")
    ap.add_argument("--poll-seconds", type=int, default=60)
    args = ap.parse_args()

    out_path = args.out or (OUT_MATCHED if args.matched else OUT)
    state_file = STATE_FILE_MATCHED if args.matched else STATE_FILE

    pool = pd.read_parquet("gate_s_pool.parquet")
    pool["problem_id"] = pool.problem_id.astype(str)
    n_all = len(pool)
    if args.pool == "analysis":
        pool = pool[pool.in_analysis_pool]
    elif args.pool == "generation":
        pool = pool[pool.in_generation_pool]
    print(f"pool slice '{args.pool}': {len(pool)} of {n_all} problems  ->  {out_path}")
    if args.problem_ids:
        blob = json.load(open(args.problem_ids))
        wanted = {str(x) for x in (blob["problem_ids"] if isinstance(blob, dict) else blob)}
        before = len(pool)
        pool = pool[pool.problem_id.isin(wanted)]
        print(f"--problem-ids {args.problem_ids}: {len(wanted)} requested, "
              f"{len(pool)} of {before} pool problems matched")
        if not len(pool):
            raise SystemExit("no pool problem matched --problem-ids; wrong file?")
    done = already_done(out_path)
    todo = pool[~pool.problem_id.isin(done)]
    if args.limit:
        todo = todo.head(args.limit)
    print(f"pool {len(pool)}, already done {len(done)}, to generate {len(todo)}\n")
    if todo.empty:
        print("nothing to do")
        return

    cost = estimate(todo, args.spent, args.matched)
    if args.spent + cost > BUDGET_CEILING:
        raise SystemExit(f"\nREFUSING: projected ${args.spent + cost:.2f} exceeds the "
                         f"${BUDGET_CEILING:.0f} ceiling.")
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
              f"(thinking {'adaptive' if args.thinking else 'off'}, "
              f"{'matched' if args.matched else 'plain'} prompt) ...")
        batch = client.messages.batches.create(
            requests=build_requests(todo, args.thinking, args.matched))
        batch_id = batch.id
        json.dump({"batch_id": batch_id, "model": MODEL, "n": len(todo),
                   "thinking": args.thinking, "matched": args.matched},
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
