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

MODEL = "claude-sonnet-5"
MAX_TOKENS = 2048          # same ceiling as the vLLM arms
BATCH_LIMIT = 100_000      # API maximum requests per batch
# Sonnet 5 list price per million tokens; the Batch API bills at 50%.
PRICE_IN, PRICE_OUT, BATCH_DISCOUNT = 2.00, 10.00, 0.5
STATE_FILE = "gen_sonnet5.batch.json"


def build_requests(pool: pd.DataFrame, thinking: bool):
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    reqs = []
    for _, row in pool.iterrows():
        params = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "messages": [{"role": "user", "content": PROMPT.format(question=row.question)}],
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
    print("Output length is the uncertain half; treat this as +/- 50%.")


def collect(client, batch_id: str, out_path: str) -> None:
    """Write one JSONL record per result. Results arrive in arbitrary order - key by custom_id."""
    n_ok = n_err = n_trunc = n_nocode = 0
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
            code = extract_code(text)
            truncated = msg.stop_reason == "max_tokens"
            n_ok += 1
            n_trunc += truncated
            n_nocode += (not code)
            tok_in += msg.usage.input_tokens
            tok_out += msg.usage.output_tokens
            fh.write(json.dumps({
                "problem_id": pid,
                "model": MODEL,
                "code": code,
                "raw": text,
                "finish_reason": msg.stop_reason,
                "n_prompt_tokens": msg.usage.input_tokens,
                "n_output_tokens": msg.usage.output_tokens,
                "truncated": bool(truncated),
            }) + "\n")

    cost = (tok_in / 1e6 * PRICE_IN + tok_out / 1e6 * PRICE_OUT) * BATCH_DISCOUNT
    print(f"\nsucceeded                 {n_ok}")
    print(f"errored                   {n_err}")
    print(f"truncated at max_tokens   {n_trunc}")
    print(f"no extractable code block {n_nocode}")
    print(f"tokens                    {tok_in/1e6:.2f} M in / {tok_out/1e6:.2f} M out")
    print(f"ACTUAL COST               ${cost:.2f}")
    print(f"\nwrote {out_path}. Next: run_tests.py --solutions {out_path} --out pass_sonnet5.jsonl")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="gen_sonnet5.jsonl")
    ap.add_argument("--limit", type=int, default=0, help="first N problems, for a smoke test")
    ap.add_argument("--thinking", action="store_true", help="adaptive thinking on (roughly 2x cost)")
    ap.add_argument("--dry-run", action="store_true", help="estimate cost and exit, spending nothing")
    ap.add_argument("--poll-seconds", type=int, default=60)
    args = ap.parse_args()

    pool = pd.read_parquet("gate_s_pool.parquet")
    pool["problem_id"] = pool.problem_id.astype(str)
    done = already_done(args.out)
    todo = pool[~pool.problem_id.isin(done)]
    if args.limit:
        todo = todo.head(args.limit)
    print(f"pool {len(pool)}, already done {len(done)}, to generate {len(todo)}\n")
    if todo.empty:
        print("nothing to do")
        return

    estimate(todo)
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
    if os.path.exists(STATE_FILE):
        batch_id = json.load(open(STATE_FILE)).get("batch_id")
        print(f"resuming batch {batch_id} from {STATE_FILE}")

    if batch_id is None:
        print(f"\nsubmitting {len(todo)} requests to {MODEL} "
              f"(thinking {'adaptive' if args.thinking else 'off'}) ...")
        batch = client.messages.batches.create(requests=build_requests(todo, args.thinking))
        batch_id = batch.id
        json.dump({"batch_id": batch_id, "model": MODEL, "n": len(todo),
                   "thinking": args.thinking}, open(STATE_FILE, "w"))
        print(f"batch {batch_id} submitted; state saved to {STATE_FILE}")

    started = time.time()
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        c = batch.request_counts
        print(f"  [{(time.time()-started)/60:5.1f} min] {batch.processing_status}  "
              f"processing={c.processing} succeeded={c.succeeded} errored={c.errored}", flush=True)
        if batch.processing_status == "ended":
            break
        time.sleep(args.poll_seconds)

    collect(client, batch_id, args.out)
    os.remove(STATE_FILE)


if __name__ == "__main__":
    main()
