"""Execute Python solutions against the shipped APPS `inputs`/`outputs` test cases.

The first thing in this repo that runs code. See `../GATE-S-RUNBOOK.md` §4 for the design
rationale; the two decisions that shape it are:

  * Problem 0 ships 565 test cases and problem 1 ships 278, so one subprocess per test case is
    millions of launches. We fork **once per solution**, loop the cases in-process against a
    patched `sys.stdin`, and **stop at the first failure**.
  * A hung solution has to be killable. Each solution runs in its own `multiprocessing.Process`
    which the parent hard-kills after a wall-clock budget; inside it, each case additionally gets
    an interval timer.

Usage
-----
    python run_tests.py --solutions human --out human_verify.jsonl
    python run_tests.py --solutions gen_32b.jsonl --out pass_32b.jsonl

`--solutions human` reads the shipped human solutions out of the parquet shards and compares our
verdict against the artifact's own `passes_tests` flag. That comparison is the harness's
validation and it runs *before* anything is generated: if our checker is stricter than the one
upstream used, the LLM honest class gets filtered harder than the human class and Gate S measures
our checker instead of authorship.

Sandboxing is timeouts + address-space limits + a scratch cwd, which is the bar the standard APPS
and HumanEval harnesses use. It is not a container, and the paper says so.
"""

from __future__ import annotations

import argparse
import glob
import io
import json
import multiprocessing as mp
import os
import resource
import signal
import sys
import tempfile
import time
from contextlib import redirect_stdout

import pandas as pd
import pyarrow.parquet as pq

# Resource limits. Module-level because the forked children read them, CLI-overridable because they
# are a *measurement choice*, not a constant.
#
# The first pass used 4 s / 60 s / 4 GiB and that was too tight in a way that biased the answer: 346
# timeouts and 207 MemoryErrors were 41% of all disagreements with the artifact's own flags. APPS
# solutions legitimately do things like `[0] * (10**7 + 1)` twice, and a problem with 43 test cases
# legitimately takes more than 4 s per case. A limit that fails a correct solution makes our harness
# look stricter than it is - and in Gate S it would shrink the human arm specifically, since the
# generated class is modern code that does not do this.
PER_CASE_TIMEOUT = 10.0
PER_SOLUTION_BUDGET = 150.0
ADDRESS_SPACE_LIMIT = 8 << 30  # 8 GiB; the box has 345 GB and at most 14 children run at once


# --------------------------------------------------------------------------- comparison


def normalise(text: str) -> list[str]:
    """Trailing whitespace per line, trailing blank lines. Nothing else.

    Deliberately no float tolerance and no token reordering: the nondeterminism exclusion in
    `gate_s_pool.py` is what handles ambiguous problems. Adding tolerance here would make our
    filter differ from the upstream one in a way we could not characterise.
    """
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


class _CaseTimeout(Exception):
    pass


def _on_alarm(signum, frame):
    raise _CaseTimeout()


# --------------------------------------------------------------------------- the child


def _run_solution(code: str, inputs: list[str], outputs: list[str], conn) -> None:
    """Runs inside a forked child. Sends one result dict back down `conn`."""
    result = {
        "passed": False,
        "n_cases": len(inputs),
        "n_cases_run": 0,
        "failed_at": None,
        "reason": None,
    }
    try:
        resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE_LIMIT, ADDRESS_SPACE_LIMIT))
    except (ValueError, OSError):
        pass  # some systems refuse; the parent's hard kill is the real guarantee

    workdir = tempfile.mkdtemp(prefix="apps-run-")
    try:
        os.chdir(workdir)
    except OSError:
        pass

    signal.signal(signal.SIGALRM, _on_alarm)

    try:
        compiled = compile(code, "<solution>", "exec")
    except (SyntaxError, ValueError, MemoryError) as exc:
        result["reason"] = f"compile: {type(exc).__name__}"
        conn.send(result)
        conn.close()
        return

    real_stdin = sys.stdin
    for i, (case_in, case_out) in enumerate(zip(inputs, outputs)):
        result["n_cases_run"] = i + 1
        buf = io.StringIO()
        try:
            signal.setitimer(signal.ITIMER_REAL, PER_CASE_TIMEOUT)
            sys.stdin = io.StringIO(case_in)
            # A fresh globals dict per case, so module-level state cannot leak between cases.
            with redirect_stdout(buf):
                try:
                    exec(compiled, {"__name__": "__main__", "__file__": "solution.py"})
                except SystemExit:
                    pass  # sys.exit() is a normal ending for these programs
        except _CaseTimeout:
            result["failed_at"] = i
            result["reason"] = "timeout"
            break
        except BaseException as exc:  # noqa: BLE001 - any failure is a failed test case
            result["failed_at"] = i
            result["reason"] = f"raised: {type(exc).__name__}"
            break
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            sys.stdin = real_stdin

        if normalise(buf.getvalue()) != normalise(case_out):
            result["failed_at"] = i
            result["reason"] = "mismatch"
            break
    else:
        result["passed"] = True

    conn.send(result)
    conn.close()


# --------------------------------------------------------------------------- the parent


def run_one(code: str, inputs: list[str], outputs: list[str], ctx) -> dict:
    """Run one solution in a killable child. Never raises."""
    started = time.monotonic()
    if not inputs:
        return {"passed": False, "n_cases": 0, "n_cases_run": 0,
                "failed_at": None, "reason": "no test cases", "elapsed_s": 0.0}

    parent_conn, child_conn = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_run_solution, args=(code, inputs, outputs, child_conn))
    proc.start()
    child_conn.close()

    result = None
    try:
        if parent_conn.poll(PER_SOLUTION_BUDGET):
            try:
                result = parent_conn.recv()
            except EOFError:
                result = None
    finally:
        parent_conn.close()
        if proc.is_alive():
            proc.kill()
        proc.join(5)

    if result is None:
        result = {
            "passed": False,
            "n_cases": len(inputs),
            "n_cases_run": None,
            "failed_at": None,
            # exitcode -N means killed by signal N: a segfault from deep recursion, an OOM, or
            # our own kill after the budget. Distinguishing them is not worth the complexity.
            "reason": "budget exceeded or died" if proc.exitcode is None or proc.exitcode < 0
                      else f"no result (exit {proc.exitcode})",
        }
    result["elapsed_s"] = round(time.monotonic() - started, 3)
    return result


# The artifact, loaded once in the parent *before* the workers fork, so they inherit it
# copy-on-write. Nothing about a problem travels through the queue except its row index: sending
# the test arrays instead makes the parent the bottleneck and starves every worker. Measured, not
# guessed - the version that pickled test data per problem kept 13 workers busy 12% of the time.
_DF = None


def _row_payload(row_idx, gen_code):
    """Everything a worker needs for one problem, read out of the inherited frame."""
    row = _DF.iloc[row_idx]
    inputs, outputs = list(row.inputs), list(row.outputs)
    pmeta = {"problem_id": row.problem_id,
             "is_nondeterministic": bool(row.is_nondeterministic)}
    if gen_code is None:
        sols = [{"sol_idx": i, "code": s["code"],
                 "expected_passes": bool(s["passes_tests"]),
                 "expected_compiles": bool(s["compiles"])}
                for i, s in enumerate(row.solutions)]
        return pmeta, inputs, outputs, sols
    if not gen_code.strip():
        return (pmeta, inputs[:1], ["\x00"],
                [{"sol_idx": 0, "code": "raise SystemExit('no code extracted')"}])
    return pmeta, inputs, outputs, [{"sol_idx": 0, "code": gen_code}]


def worker_loop(task_queue, done_queue, max_per_problem=0):
    """One long-lived worker; forks a fresh child per solution so a hang is contained."""
    ctx = mp.get_context("fork")
    while True:
        task = task_queue.get()
        if task is None:
            break
        row_idx, extra = task
        pmeta, inputs, outputs, sols = _row_payload(row_idx, extra.get("code"))
        pmeta.update({k: v for k, v in extra.items() if k != "code"})
        if max_per_problem:
            sols = sols[:max_per_problem]
        results = []
        for sol in sols:
            code = sol.pop("code")
            results.append({**pmeta, **sol, **run_one(code, inputs, outputs, ctx)})
        done_queue.put(results)


# --------------------------------------------------------------------------- inputs


def load_artifact() -> pd.DataFrame:
    shards = sorted(glob.glob("train_*.parquet"))
    if not shards:
        raise SystemExit("no train_*.parquet here — run `python fetch.py` first")
    cols = ["problem_id", "inputs", "outputs", "solutions",
            "solution_passes_tests", "is_nondeterministic"]
    df = pd.concat(
        [pq.read_table(f, columns=cols).to_pandas() for f in shards], ignore_index=True
    )
    df["problem_id"] = df.problem_id.astype(str)
    return df


def tasks_human(df):
    """One task per problem. Just the row index: the worker reads the frame it inherited."""
    for i in range(len(df)):
        yield i, {}


def tasks_generated(df, path):
    """One task per generated solution, carrying only its (small) code and metadata."""
    idx_by_pid = {pid: i for i, pid in enumerate(df.problem_id)}
    with open(path) as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            pid = str(rec["problem_id"])
            if pid not in idx_by_pid:
                continue
            yield idx_by_pid[pid], {"code": rec.get("code") or "",
                                    "model": rec.get("model"),
                                    "finish_reason": rec.get("finish_reason")}


# --------------------------------------------------------------------------- report


def report_human(records: list[dict]) -> None:
    df = pd.DataFrame(records)
    agree = (df.passed == df.expected_passes).mean()
    per_problem = df.groupby("problem_id").passed.any()
    print("\n--- harness validation against the artifact's own flags ---")
    print(f"solutions run                      {len(df)}")
    print(f"our verdict == solutions[].passes_tests  {agree:.4f}")
    print(f"  we fail, artifact passes         {int(((~df.passed) & df.expected_passes).sum())}")
    print(f"  we pass, artifact fails          {int((df.passed & (~df.expected_passes)).sum())}")
    print(f"problems with >=1 passing solution {int(per_problem.sum())}   (artifact: 3420)")
    det = df[~df.is_nondeterministic]
    print(f"agreement on deterministic only    {(det.passed == det.expected_passes).mean():.4f}"
          f"  (n={len(det)})")
    print("\nreasons we failed a solution the artifact passed:")
    miss = df[(~df.passed) & df.expected_passes]
    if len(miss):
        print(miss.reason.value_counts().to_string())
    else:
        print("  none")
    print("""
Reading: >=98% means the harness is faithful, report the rate in the paper.
90-98% means use OUR pass flag for both classes rather than the shipped column.
<90% means debug before generating anything (GATE-S-RUNBOOK.md §4.2).""")


def report_generated(records: list[dict], label: str) -> None:
    df = pd.DataFrame(records)
    print(f"\n--- {label} ---")
    print(f"solutions            {len(df)}")
    print(f"passed               {int(df.passed.sum())}  ({df.passed.mean():.4f})")
    det = df[~df.is_nondeterministic]
    print(f"passed, deterministic only  {int(det.passed.sum())} / {len(det)}"
          f"  ({det.passed.mean():.4f})" if len(det) else "")
    print("failure reasons:")
    print(df[~df.passed].reason.value_counts().to_string() if (~df.passed).any() else "  none")


# --------------------------------------------------------------------------- main


def main() -> None:
    global _DF, PER_CASE_TIMEOUT, PER_SOLUTION_BUDGET, ADDRESS_SPACE_LIMIT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--solutions", required=True,
                    help="'human' for the shipped solutions, else a generation .jsonl")
    ap.add_argument("--out", required=True, help="JSONL of per-solution results")
    ap.add_argument("--workers", type=int, default=max(1, min(14, (os.cpu_count() or 4) - 2)))
    ap.add_argument("--limit", type=int, default=0, help="first N problems, for a smoke test")
    ap.add_argument("--max-per-problem", type=int, default=0,
                    help="cap solutions per problem (0 = all); applies to --solutions human")
    ap.add_argument("--case-timeout", type=float, default=PER_CASE_TIMEOUT)
    ap.add_argument("--solution-budget", type=float, default=PER_SOLUTION_BUDGET)
    ap.add_argument("--mem-gib", type=float, default=ADDRESS_SPACE_LIMIT / (1 << 30))
    args = ap.parse_args()

    PER_CASE_TIMEOUT = args.case_timeout
    PER_SOLUTION_BUDGET = args.solution_budget
    ADDRESS_SPACE_LIMIT = int(args.mem_gib * (1 << 30))
    print(f"limits: {PER_CASE_TIMEOUT}s/case, {PER_SOLUTION_BUDGET}s/solution, "
          f"{args.mem_gib:g} GiB address space", flush=True)
    _DF = df = load_artifact()
    print(f"artifact: {len(df)} problems, {int(df.solution_passes_tests.sum())} with "
          f"solution_passes_tests, {int(df.is_nondeterministic.sum())} nondeterministic",
          flush=True)

    gen = (tasks_human(df) if args.solutions == "human"
           else tasks_generated(df, args.solutions))

    ctx = mp.get_context("fork")
    task_queue, done_queue = ctx.Queue(maxsize=args.workers * 4), ctx.Queue()
    # Workers fork here, after _DF is populated, so the frame is inherited rather than pickled.
    workers = [ctx.Process(target=worker_loop,
                           args=(task_queue, done_queue, args.max_per_problem))
               for _ in range(args.workers)]
    for w in workers:
        w.start()

    records, submitted, done_problems, started = [], 0, 0, time.monotonic()

    def drain(out, block=False):
        nonlocal done_problems
        while True:
            if not block and done_queue.empty():
                return
            batch = done_queue.get()
            done_problems += 1
            for rec in batch:
                records.append(rec)
                out.write(json.dumps(rec) + "\n")
            out.flush()
            if done_problems % 200 == 0:
                el = time.monotonic() - started
                print(f"  problems {done_problems}/{submitted}, solutions {len(records)}, "
                      f"{len(records) / max(1e-9, el):.1f} sol/s, {el / 60:.1f} min",
                      flush=True)
            return

    with open(args.out, "w") as out:
        try:
            for task in gen:
                if args.limit and submitted >= args.limit:
                    break
                task_queue.put(task)
                submitted += 1
                drain(out)
            for _ in workers:
                task_queue.put(None)
            while done_problems < submitted:
                drain(out, block=True)
        finally:
            for w in workers:
                w.join(10)
                if w.is_alive():
                    w.kill()

    print(f"\n{len(records)} solutions in {time.monotonic() - started:.1f}s -> {args.out}")
    if args.solutions == "human":
        report_human(records)
    else:
        report_generated(records, args.solutions)


if __name__ == "__main__":
    main()
