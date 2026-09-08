"""Generate the Gate S honest class with a local open-weight coder model (vLLM, offline batch).

The only GPU code in this repo. Run it twice, once per arm:

    CUDA_VISIBLE_DEVICES=0 python gen_honest.py \
        --model Qwen/Qwen2.5-Coder-7B-Instruct  --out gen_7b.jsonl
    CUDA_VISIBLE_DEVICES=1 python gen_honest.py \
        --model Qwen/Qwen2.5-Coder-32B-Instruct --out gen_32b.jsonl

The cards are H100 NVL at 94 GB, so the 32B fits at bf16 on ONE card (~62 GB of weights). Both arms
therefore run concurrently, one GPU each, instead of sequentially at tensor_parallel_size=2 - which
also removes the tensor-parallel failure mode entirely.

Generation covers all 5,000 problems, not the 3,420 with a shipped passing solution: which problems
are eligible depends on how the harness validation lands, and that is an analysis-time filter, not a
generation-time one (`gate_s_pool.py`).

Requires `gate_s_pool.parquet` (run `gate_s_pool.py` first). Resumable: problem_ids already in
`--out` are skipped, so an interrupted allocation costs only the unfinished tail.

The protocol is fixed in `../GATE-S-RUNBOOK.md` §3 and the reasons matter more than the values:

  one sample per problem, no best-of-n   further selection on quality would install exactly the
                                         selection artifact this paper audits
  temperature 0, fixed seed              removes sampling as a free parameter a reviewer can poke
  the question verbatim, tests withheld  the model gets what a human solver got, and cannot fit
                                         the checker
  NO style instructions                  comment and identifier style is the channel under test.
                                         Saying "no comments" or "be concise" would destroy the
                                         measurement. Comments are stripped downstream by the same
                                         strip_comments() applied to the human class.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

import pandas as pd

PROMPT = """Solve the following competitive programming problem in Python 3.
Read input from standard input and write the answer to standard output.
Respond with a single ```python code block containing the complete program and nothing else.

{question}"""

FENCED = re.compile(r"```[ \t]*(?:python|py|python3)?[ \t]*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code(completion: str) -> str:
    """First fenced block wins. No block is a failure and is recorded as one."""
    m = FENCED.search(completion)
    if m:
        return m.group(1).strip()
    # An unterminated fence: the generation hit max_tokens mid-block. Keep what there is so the
    # harness can record it as a truncation failure rather than an empty record.
    m = re.search(r"```[ \t]*(?:python|py|python3)?[ \t]*\n(.*)$", completion,
                  re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def already_done(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    done = set()
    with open(path) as fh:
        for line in fh:
            try:
                done.add(str(json.loads(line)["problem_id"]))
            except Exception:
                continue
    return done


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tp", type=int, default=1,
                    help="tensor_parallel_size; 1 is right on 94 GB cards, even for the 32B")
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--max-model-len", type=int, default=8192)
    ap.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="first N problems, for a smoke test")
    ap.add_argument("--generation-pool-only", action="store_true",
                    help="restrict to the 3,420 with a shipped passing solution. Off by default: "
                         "eligibility is an analysis-time filter, and generating the superset means "
                         "the harness validation cannot send us back to the GPU.")
    args = ap.parse_args()

    pool = pd.read_parquet("gate_s_pool.parquet")
    pool["problem_id"] = pool.problem_id.astype(str)
    if args.generation_pool_only:
        pool = pool[pool.in_generation_pool]
        print("restricted to in_generation_pool (the shipped solution_passes_tests)")
    done = already_done(args.out)
    todo = pool[~pool.problem_id.isin(done)]
    if args.limit:
        todo = todo.head(args.limit)
    print(f"pool {len(pool)} problems, {len(done)} already in {args.out}, generating {len(todo)}")
    if todo.empty:
        return

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(args.model)
    prompts = [
        tok.apply_chat_template(
            [{"role": "user", "content": PROMPT.format(question=q)}],
            tokenize=False, add_generation_prompt=True,
        )
        for q in todo.question
    ]

    # Drop prompts that cannot leave room for an answer rather than letting vLLM truncate silently.
    budget = args.max_model_len - args.max_tokens
    lens = [len(tok(p).input_ids) for p in prompts]
    keep = [i for i, n in enumerate(lens) if n <= budget]
    if len(keep) < len(prompts):
        print(f"WARNING: {len(prompts) - len(keep)} prompts exceed {budget} tokens and are "
              f"skipped; they are recorded as failures by their absence from {args.out}",
              file=sys.stderr)
    prompts = [prompts[i] for i in keep]
    rows = todo.iloc[keep]

    llm = LLM(
        model=args.model,
        tensor_parallel_size=args.tp,
        dtype="bfloat16",
        max_model_len=args.max_model_len,
        gpu_memory_utilization=args.gpu_memory_utilization,
        seed=args.seed,
    )
    sampling = SamplingParams(temperature=0.0, top_p=1.0, max_tokens=args.max_tokens,
                              seed=args.seed)

    outputs = llm.generate(prompts, sampling)

    n_trunc = n_nocode = 0
    with open(args.out, "a") as fh:
        for (_, row), out in zip(rows.iterrows(), outputs):
            comp = out.outputs[0]
            code = extract_code(comp.text)
            truncated = comp.finish_reason == "length"
            n_trunc += truncated
            n_nocode += (not code)
            fh.write(json.dumps({
                "problem_id": row.problem_id,
                "model": args.model,
                "code": code,
                "raw": comp.text,
                "finish_reason": comp.finish_reason,
                "n_prompt_tokens": len(out.prompt_token_ids),
                "n_output_tokens": len(comp.token_ids),
                "truncated": bool(truncated),
            }) + "\n")

    print(f"\nwrote {len(outputs)} generations to {args.out}")
    print(f"  truncated at max_tokens   {n_trunc}")
    print(f"  no extractable code block {n_nocode}")
    print("Both counts are failures and stay in the denominator. Next: run_tests.py")


if __name__ == "__main__":
    main()
