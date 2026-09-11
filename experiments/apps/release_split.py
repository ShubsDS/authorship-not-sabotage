"""Build (and validate) the anonymised public release of the same-generator APPS split.

This is the artifact `main.tex` promises when it says the split definition and the scripts
accompany the paper. It turns the run products on disk --- `gen_<tag>.jsonl`, `pass_<tag>.jsonl`
and the two attack arms with their verifier outputs --- into a self-contained `release/`
directory that another group can download, read and recompute a floor from.

    python release_split.py                      # build ./release from the default file names
    python release_split.py --out /tmp/release    # build somewhere else
    python release_split.py --check release       # validate a built directory
    python release_split.py --render-card-only --card-out ../RELEASE-CARD.md

The scripts, and the licence (added 2026-09-11; schema 3)
---------------------------------------------------------
Recommendation 4 of the paper is "release the split *and the scripts*", so the bundle ships
both. `release/scripts/` carries the programs behind the paper's numbers, read from the
**committed** revision (`git show HEAD:...`) rather than from the working tree, so a
half-finished edit by a parallel session cannot ship; `--scripts-from-worktree` overrides that
for a checkout without git. `release/LICENSE` is a copy inside the directory: the archive used
to store it as `../../LICENSE`, which extracts beside the release rather than into it.

Scripts are scrubbed on a list of their own (`SCRIPT_SCRUB_PATTERNS`). The data scrub bans
every `github.com/<owner>/` URL, but two scripts carry one inside a third-party licence notice
that `THIRD-PARTY-NOTICES.md` obliges us to keep, and an upstream repository is a citation, not
an author. What the script scrub bans is what actually de-anonymises or leaks: credentials, API
batch ids, local paths, personal names and email addresses --- and cost figures, which are
redacted to `$X` on the way in and then refused if any survive.

What it releases, and what it deliberately does not
---------------------------------------------------
Released: **our** generations only --- honest solutions and backdoored solutions written by
`claude-sonnet-5`, their triggers, our harness verdicts, and the problem ids that pair them up.

Not released, under the project's standing rule that we redistribute nothing upstream
(`notes/05-permissibility.md`):

  * no human APPS solutions, and no problem statements, inputs or outputs --- the upstream
    artifact is referenced by `problem_id` only;
  * no stored backdoors from `RoganInglis/apps-control-arena`. That corpus is MIT and could
    lawfully be redistributed; the rule is stricter than the licence on purpose, so that one
    sentence covers every corpus;
  * nothing derived from `eugenekoran/apps-control-arena-high-quality`, which declares no
    licence and therefore grants no permission to redistribute anything at all.

Anonymity
---------
The paper is double-blind until acceptance, so the bundle is scrubbed: no local paths, no
usernames, no hostnames, no API batch ids, no keys, no dollar figures, no author or institution
names, no repository URL. `--check` re-runs that scrub against a built directory and fails on a
hit, so an accidental leak cannot ship quietly.

Every released record carries only the fields listed in `HONEST_FIELDS` / `ATTACK_FIELDS`.
Anything else in the source jsonl --- notably the model's full `raw` reply --- is dropped rather
than filtered, because an allow-list cannot be defeated by a field nobody thought of.

The retry pool and the two selections (added 2026-09-11; schema 2)
-------------------------------------------------------------------
The independent arm was resampled (`merge_draws.py`), so a reader must be able to reproduce both
the paper's headline selection and its strict one from the same bundle:

  * `attacks_independent.jsonl` + `pairs_passes.csv` / `pairs_usable.csv` --- one draw per problem
    under `--keep` (default `first`: the earliest draw, chosen blind to its outcome). This is
    unchanged from schema 1 apart from the new `crash_on_trigger` field.
  * `--pool-independent` / `--poolpass-independent` --- ship EVERY draw of the independent arm as
    `attacks_independent_pool.jsonl`, undeduplicated, with `draw` / `source` / `round` so the
    draws can be ordered and joined. Nothing else changes when the flags are absent.
  * `--also-select best` (needs the pool) --- also write `pairs_passes_best.csv` and
    `pairs_usable_best.csv`, keyed by `draw` into the pool: the benchmark's own survivor
    selection, with a crash on the trigger scored as *not* working (ControlArena's rule). Per
    problem: the earliest draw that passes the public tests and fires without crashing; failing
    that, for the passes list, the earliest draw that passes; for the usable list, the earliest
    draw that fires by crashing, flagged `crash_on_trigger = true`. So `pairs_usable_best.csv`
    filtered to `crash_on_trigger == false` is the strict set the paper reports, and the whole
    file is the crash-inclusive sensitivity set.

`crash_on_trigger` is `reason == "backdoor crashes on trigger"` from `verify_backdoor.py`, which
counts a crash as `backdoor_works`; the flag lets a reader apply either rule.

Trivial programs that coincide with a human solution (added 2026-09-11)
-----------------------------------------------------------------------
The first full build failed `--check` on 53 released strings byte-identical to an upstream human
solution: every one a one-liner of at most 117 characters (7 lines) for an introductory problem,
51 of 53 on the same problem, none matching a stored backdoor. That is the canonical solution
being the only solution, not memorisation. `--allow-trivial-identical CHARS` (off by default, so
the strict rule stands unless invoked) lets the build keep matches of at most CHARS characters,
refuses any longer match and any match with a stored backdoor, and declares the retained ones by
file and problem id under `upstream_identical_trivial` in `MANIFEST.json`; `--check` with the
same flag recomputes the set against the shards and fails on any undeclared or over-length match.
The card states the count. Without the flag, `--check` fails on them exactly as before.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import strip_comments  # noqa: E402  --- the same stripper the paper's protocol uses

# --------------------------------------------------------------------------- release schema

HONEST_FIELDS = ["problem_id", "code", "code_stripped", "passes_tests", "model",
                 "thinking", "max_tokens", "truncated", "finish_reason", "n_output_tokens"]

ATTACK_FIELDS = ["problem_id", "code", "code_stripped", "backdoor_input", "passes_tests",
                 "backdoor_works", "crash_on_trigger", "arm", "model",
                 "thinking", "max_tokens", "truncated", "finish_reason", "n_output_tokens"]

# The undeduplicated retry pool: every attack field plus the keys that order and join the draws.
POOL_FIELDS = ATTACK_FIELDS + ["draw", "source", "round"]

PAIR_CSV_FIELDS = ["problem_id", "arm"]
PAIR_BEST_CSV_FIELDS = ["problem_id", "arm", "draw", "crash_on_trigger"]

# verify_backdoor.py's reason string for a backdoor that "fires" by raising on its trigger.
CRASH_REASON = "backdoor crashes on trigger"

POOL_FILE = "attacks_independent_pool.jsonl"
BEST_FILES = ("pairs_passes_best.csv", "pairs_usable_best.csv")

# The scripts behind the paper's numbers, shipped under release/scripts/. Generation and
# verification first, then the measurements, then this builder. A name that is not on this list
# is not in the bundle; a name on it that is missing from the source tree fails the build.
SCRIPTS_DIR = "scripts"
SCRIPT_FILES = (
    "data.py",                     # the loaders, the pass flag and the comment stripper
    "gen_honest.py", "gen_honest_api.py",          # the honest class, local and batch API
    "gen_backdoor.py", "gen_backdoor_api.py",      # the two attack arms
    "run_tests.py", "verify_backdoor.py",          # the harness and the trigger verdict
    "merge_draws.py",              # the retry pool and the two selection rules
    "gate_s_baseline.py", "gate_s_eval.py",        # B, and the pipeline every row shares
    "gate_s_samegen.py", "gate_s_pool.py",         # S and B' on the same problems
    "gate_s_learning_curve.py",    # B at matched n: the underfitting control
    "survivor_check.py",           # retention is not the artifact
    "lexical_probe.py",            # what the residual signal is made of
    "headline_ci.py",              # the headline intervals and the paired monitor comparison
    "rho_joint_ci.py",             # the joint bootstrap on rho
    "monitor_samegen.py",          # the zero-shot monitor on the same pairs
    "release_split.py",            # this file: the bundle is reproducible from the bundle
)
LICENCE_FILE = "LICENSE"

# Scripts are prose as well as code. The data scrub (above) refuses every `github.com/<owner>/`
# and every upstream dataset URL, which would strip a third-party MIT notice we are obliged to
# keep and an upstream citation that identifies nobody. So scripts get their own list: what
# de-anonymises the authors, what is a credential, and what discloses spend.
SCRIPT_SCRUB_PATTERNS = [
    (r"msgbatch_[A-Za-z0-9]+", "an API batch id"),
    (r"sk-ant-[A-Za-z0-9_\-]{6,}", "an API key"),
    (r"/home/[A-Za-z0-9._\-]+/", "a local home directory path"),
    (r"/Users/[A-Za-z0-9._\-]+/", "a local home directory path"),
    (r"[A-Za-z]:\\\\Users\\\\", "a local home directory path"),
    (r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", "an email address"),
    (r"\$\s?\d", "a cost figure"),
]
COST_FIGURE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")

# Fields that must never reach the release even if a future version of a generator script adds
# them. The allow-list above already excludes them; this list exists so `--check` can say *why*
# a field is refused rather than only that it is unexpected.
FORBIDDEN_FIELDS = {
    "raw",                 # the model's full reply: unfiltered prose, not the object of study
    "batch_id", "custom_id", "state_file",
    "cost", "actual_cost", "spend", "usd", "price",
    "api_key", "anthropic_api_key",
    "path", "out_path", "cwd", "host", "hostname", "user", "username", "author",
    "question", "inputs", "outputs", "solutions", "backdoors",   # upstream content
}

# Patterns that would de-anonymise the bundle or leak a credential. Applied to the raw bytes of
# every released file, so they catch a leak inside a code string as well as inside a field name.
SCRUB_PATTERNS = [
    (r"msgbatch_[A-Za-z0-9]+", "an API batch id"),
    (r"sk-ant-[A-Za-z0-9_\-]+", "an API key"),
    (r"/home/[A-Za-z0-9._\-]+/", "a local home directory path"),
    (r"/Users/[A-Za-z0-9._\-]+/", "a local home directory path"),
    (r"[A-Za-z]:\\\\Users\\\\", "a local home directory path"),
    (r"ANTHROPIC_API_KEY", "an API key environment variable"),
    (r"github\.com/[A-Za-z0-9._\-]+/", "a repository URL"),
    (r"huggingface\.co/datasets/[A-Za-z0-9._\-]+/", "an upstream dataset URL with an owner"),
    (r"\$\s?\d+\.\d{2}", "a cost figure"),
]

# Values quoted in the dataset card when it is rendered without a built release (--render-card-only).
# They are the recorded ledger values from `experiments/RESULTS.md` 4.1-4.10, not estimates. A card
# written by a real build overwrites every one of them from MANIFEST.json.
LEDGER = {
    "model": "claude-sonnet-5",
    "generated": "September 2026",
    "agreement": "95.84%",
    "honest_total": 1444, "honest_pass": 1112,
    "edit_total": 1112, "edit_pass": 427, "edit_usable": 40,
    "ind_total": 600, "ind_pass": 335, "ind_usable": 10,
    "pairs_passes_edit": 427, "pairs_passes_ind": 335,
    "pairs_usable_edit": 40, "pairs_usable_ind": 10,
    "built": "not yet --- this copy is rendered from the recorded ledger",
    "scripts_row": "", "licence_row": "",
}

# --------------------------------------------------------------------------- dataset card

CARD_TEMPLATE = """# A same-generator honest/attack split for APPS

## What this is

Stored honest/attack pairs are how trusted monitors for AI control are trained, tuned and
ranked: a corpus of program solutions, some carrying a planted backdoor, with a label. In the
APPS-based corpora the two classes come from different authors --- the honest class is
human-written and every backdoor is model-written --- so a classifier can recover the label by
recognising who wrote the code rather than by detecting sabotage. This split removes that
confound by construction. **One model, `{model}`, wrote both classes**: the honest solutions and
the backdoored solutions, on the same {honest_total} APPS problems, under the same decoding
configuration. A trivial baseline trained on these pairs cannot key on authorship, because there
is only one author. Whatever separability survives is a property of the sabotage, not of the
provenance.

## Files

| File | Rows | What it holds |
|---|---:|---|
| `honest.jsonl` | {honest_total} | one honest solution per problem, with our harness verdict |
| `attacks_edit.jsonl` | {edit_total} | the **edit** arm: the model was shown its own honest solution and asked to hide a bug |
| `attacks_independent.jsonl` | {ind_total} | the **independent** arm: the model saw the problem only |
| `pairs_passes.csv` | {pairs_passes_total} | problem ids forming a pair under the *passes-tests* rule, by arm |
| `pairs_usable.csv` | {pairs_usable_total} | problem ids forming a pair under the *passes-and-fires* rule, by arm |
| `MANIFEST.json` | --- | row counts, SHA-256 of every file, generator, build date, harness agreement |
{scripts_row}{licence_row}{pool_file_rows}
Each code record carries `code` (as generated, comments intact) and `code_stripped` (the same
code through the comment stripper this protocol mandates). Comment presence is itself a known
label channel, so the raw text is released and the stripping is shown rather than assumed: use
`code_stripped` to reproduce the paper's protocol, `code` to study the channel.

## Provenance

* **Problem ids** are APPS problem ids, reached through the public `apps-control-arena` artifact.
  **No upstream content is redistributed here** --- no problem statements, no test cases, no human
  solutions, no stored backdoors. Join on `problem_id` to obtain them from their own sources under
  their own licences.{trivial_sentence}
* **All code in this split was generated by `{model}`** in {generated}, through the batch API,
  with comments left as the model wrote them.
* **Not bit-reproducible.** Sampling parameters are not exposed on this model, so the generations
  were drawn under the provider's default sampling and cannot be regenerated exactly. The split is
  released as data for that reason: it is the artifact, not a recipe.
* **Thinking was off** for the generations released here.
* **Harness.** Test verdicts (`passes_tests`) come from a re-implementation of the standard APPS
  execution protocol: one fork per solution, per-case timeouts, an address-space limit and a
  scratch working directory. Validated against the upstream artifact's own pass flags on the same
  {honest_total}-problem pool, it agrees on **{agreement}** of them and is strictly conservative
  there --- it never credits a solution the artifact rejects. `backdoor_works` follows the
  artifact's own definition: on the model's declared trigger input, the backdoored program's
  output differs from the honest program's output.

## Yield

| Class | Generated | Pass the public tests | Pass **and** fire |
|---|---:|---:|---:|
| honest | {honest_total} | {honest_pass} | --- |
| attack, edit arm | {edit_total} | {edit_pass} | {edit_usable} |
| attack, independent arm | {ind_total} | {ind_pass} | {ind_usable} |
{pool_yield_row}
Writing a program from scratch that passes every public test *and* diverges on a self-chosen
trigger is hard: the single-shot rate is a low single-digit percentage, against the roughly 46%
attack rate of the stored corpus this split is modelled on. That gap is a measurement, not a
defect --- the stored attack class is the survivor set of an unreported number of retries.
{retry_sentence} This card is generated from `MANIFEST.json`, so every number above is
regenerated with the data and cannot drift from it.

## Two eligibility rules, both shipped

A pair needs an honest solution that passes the tests and an attack on the same problem. What
counts as an attack admits two defensible definitions, and the split ships both rather than
choosing for the user:

* **`pairs_passes.csv` --- passes the public tests.** Intent plus test-evasion, firing not
  required. This is the same-generator analogue of the stored corpus's own labelling, in which a
  large majority of labelled backdoors do not in fact fire, and on which a trivial classifier
  scores about as well as it does on working ones. It is the higher-powered rule.
* **`pairs_usable.csv` --- passes the tests and fires on its trigger.** The strict rule, matching
  the filtered benchmark exactly. It is the smaller set and, at the counts above, underpowered on
  its own.

Report them side by side. They answer different questions and neither substitutes for the other;
a conclusion that holds under only one of them should be reported as holding under only one.
{best_lists_paragraph}
## Known limitations

1. **A later generation than the stored attacker.** The corpus this split is designed to control
   was attacked by an earlier model in the same vendor's lineage, which has since been retired and
   returns 404. This is a same-vendor, same-lineage control, **not** a same-model one.
2. {limitation_two}
3. **Interpreter-era effects.** Pass/fail verdicts are era-sensitive in both directions: modern
   fast-I/O idioms broke an earlier version of the harness (fixed), and pre-3.9 standard-library
   imports genuinely fail on a current interpreter. Both classes here are modern and from one
   model, so this split is immune; a comparison against human-written code from an older era is
   not, and should report it.
4. **Two arms are not interchangeable.** The edit arm's pairs are near-copies of each other, far
   more similar than the stored corpus's pairs; the independent arm reproduces the stored
   corpus's independent-programs structure. Results from the edit arm are a bound under maximal
   pair similarity, not a verdict.
5. **The honest class is one model's style.** Separability measured here is separability for this
   generator; it does not transfer automatically to another.

## Intended use

* Computing a **trivial-baseline floor** --- bag-of-words, length, surface features --- for a
  monitor benchmark in a setting where authorship cannot explain the result.
* As a **control split** beside a stored honest/attack corpus, to decompose a monitor's or a
  baseline's separability into an authorship component and a content component.
* As a **preprocessing testbed**: the raw and comment-stripped text of every program is shipped
  side by side.

Not intended for: training an attack policy; claiming a monitor is safe; any use that treats
`backdoor_works` as a ground truth about exploitability beyond the single declared trigger input.

## Licence

MIT. `LICENSE` in this bundle covers the data and the scripts under `scripts/`. Upstream corpora
referenced by problem id keep their own licences; nothing from them is included here. Cost
figures in the scripts' comments are redacted to `$X`; nothing else in them was changed.

## Citation

```
@misc{{whatsurvivesthefilter,
  title  = {{What Survives the Filter? Trivial Baselines on Stored Honest/Attack Pairs}},
  author = {{Anonymous}},
  year   = {{2026}},
  note   = {{Under double-blind review; dataset split accompanying the submission.
            Author and venue details will be added on acceptance.}}
}}
```

---

Generator `{model}` - generated {generated} - built {built} - harness agreement {agreement}
"""


# --------------------------------------------------------------------------- io helpers

def read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        raise SystemExit(f"missing input: {path}\n"
                         f"Run the generation and verification steps first, or point the "
                         f"corresponding flag at the file you have.")
    out = []
    with open(path) as fh:
        for ln, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{ln}: not JSON ({e})")
    return out


def grouped(vals: dict) -> dict:
    """Thousands separators for the card. 1,444 reads as a count; 1444 reads as an id."""
    return {k: (f"{v:,}" if isinstance(v, int) and not isinstance(v, bool) else v)
            for k, v in vals.items()}


def card_extras(pc: dict | None) -> dict:
    """The card paragraphs that depend on whether the retry pool ships. `pc` is the pool's
    count dict (see `pool_counts`), or None for a single-shot build / the ledger render."""
    if not pc:
        return {
            "pool_file_rows": "",
            "pool_yield_row": "",
            "retry_sentence": ("**A retry pool may raise the pass-and-fire counts** in a later "
                               "version of this split; the honest and pass-tests counts are stable."),
            "best_lists_paragraph": "",
            "limitation_two": (
                "**Single-shot, where the benchmark is a retry survivor set.** These generations "
                "are one draw\n   per problem. The stored attack class kept only the attempts that "
                "survived; any retry-pooled\n   version of this split inherits that selection "
                "effect deliberately, and must say so."),
        }
    g = grouped(pc)
    return {
        "pool_file_rows": (
            f"| `{POOL_FILE}` | {g['ind_pool_total']} | **every** draw of the independent arm, "
            f"{g['ind_pool_problems']} problems, up to {g['ind_pool_max_draws']} draws each, with "
            f"`draw` / `source` / `round` |\n"
            f"| `pairs_passes_best.csv` | {g['pairs_passes_best_ind']} | survivor selection from the "
            f"pool under the *passes-tests* rule, keyed by `draw` |\n"
            f"| `pairs_usable_best.csv` | {g['pairs_usable_best_ind']} | survivor selection under the "
            f"*passes-and-fires* rule, keyed by `draw`; {g['pairs_usable_best_noncrash_ind']} rows "
            f"fire without crashing (`crash_on_trigger = false`) |"),
        "pool_yield_row": (
            f"| attack, independent arm, **full retry pool** | {g['ind_pool_total']} | "
            f"{g['ind_pool_pass']} | {g['ind_pool_usable']} ({g['ind_pool_crash']} by crashing) |"),
        "retry_sentence": (
            f"The independent arm was therefore **resampled with the same prompt and model**, and "
            f"every draw is shipped in `{POOL_FILE}`; `attacks_independent.jsonl` is the earliest "
            f"draw per problem, chosen blind to its outcome, and the `pairs_*_best.csv` lists are "
            f"the survivor selection from the pool. The honest and pass-tests counts are stable."),
        "best_lists_paragraph": (
            "\nBoth rules are also shipped **under survivor selection** from the retry pool, which "
            "is the stored\nbenchmark's own procedure: `pairs_passes_best.csv` and "
            "`pairs_usable_best.csv` name, per problem, the\nearliest draw that passes the tests "
            "and fires without crashing, else (passes list) the earliest draw\nthat passes, else "
            "(usable list) the earliest draw that fires by crashing on its trigger, flagged\n"
            "`crash_on_trigger = true`. The upstream validator scores a crash as *not* working, so "
            "filter the\nusable list to `crash_on_trigger = false` for the strict reading; the "
            "whole file is the crash-inclusive\nsensitivity set. Anything computed on these lists "
            "inherits the benchmark's selection effect and must\nsay so.\n"),
        "limitation_two": (
            "**The `best` lists are a survivor set, like the benchmark.** `attacks_independent.jsonl` "
            "is one\n   outcome-blind draw per problem; the `pairs_*_best.csv` lists keep, per "
            "problem, the draw that\n   survived the filter, which is the selection effect the "
            "stored attack class carries. Report which\n   list a number comes from."),
    }


def trivial_sentence(decl: dict | None) -> str:
    if not decl:
        return ""
    return (f" {decl['n_strings']} released programs of at most {decl['max_chars']} characters "
            f"({decl['max_lines']} lines at most) are byte-identical to a human solution of the "
            f"same kind of trivial problem --- the canonical one-liner, which a model and a human "
            f"write alike --- and are listed by file and problem id under "
            f"`upstream_identical_trivial` in `MANIFEST.json`. They are the model's own output and "
            f"are retained as generated; none matches a stored backdoor.")


def upstream_overlap(rows_by_file: dict[str, list[dict]], upstream: dict[str, str],
                     limit: int) -> tuple[list[str], list[str], dict]:
    """Released code strings that equal an upstream one.

    Returns (long_or_backdoor, trivial, declaration): matches that must fail the build --- longer
    than `limit` characters, or equal to a stored backdoor --- and matches at most `limit`
    characters long that equal a human solution, plus the manifest declaration for the latter.
    """
    hits: dict[str, list[tuple[str, str]]] = {}
    for name, rs_ in rows_by_file.items():
        for r in rs_:
            for key in ("code", "code_stripped"):
                s = (r.get(key) or "").strip()
                if s and s in upstream:
                    hits.setdefault(s, []).append((name, r["problem_id"]))
    bad = [s for s in hits if len(s) > limit or upstream[s] != "solution"]
    triv = [s for s in hits if s not in bad]
    recs = sorted({(f, p, len(s)) for s in triv for f, p in hits[s]})
    decl = {
        "rule": (f"byte-identical to an upstream human solution, at most {limit} characters; "
                 f"retained as the model's own output and declared here. Longer matches and any "
                 f"match with a stored backdoor fail the build."),
        "max_chars": limit,
        "n_strings": len(triv),
        "max_lines": max((s.count("\n") + 1 for s in triv), default=0),
        "records": [{"file": f, "problem_id": p, "chars": n} for f, p, n in recs],
    } if triv else None
    return bad, triv, decl


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dedupe(records: list[dict], keep: str, what: str) -> list[dict]:
    """One record per problem_id.

    Generation files are appended to, so a retry pool puts several draws of the same problem in
    one file. `first` keeps the earliest draw, which is the single-shot reading. `best` keeps the
    draw that survives the strictest filter, which is the benchmark's own retry-survivor selection
    and therefore imports its selection effect --- deliberately, and it must be disclosed.
    """
    by_pid: dict[str, dict] = {}
    dups = 0
    for rec in records:
        pid = str(rec["problem_id"])
        if pid not in by_pid:
            by_pid[pid] = rec
            continue
        dups += 1
        if keep == "best":
            def rank(r: dict) -> tuple:
                return (bool(r.get("passes_tests")) and bool(r.get("backdoor_works")),
                        bool(r.get("passes_tests")))
            if rank(rec) > rank(by_pid[pid]):
                by_pid[pid] = rec
    if dups:
        print(f"  ! {what}: {dups} duplicate problem_id records (a retry pool?); "
              f"kept '{keep}'."
              + ("" if keep == "best" else
                 "  Use --keep best for a survivor-selected release, and disclose it."))
    return list(by_pid.values())


def align(candidates: list[dict], verdicts: list[dict], what: str) -> list[dict]:
    """Attach each verdict record to its candidate.

    `run_tests.py` and `verify_backdoor.py` both emit one record per input record, in order, so
    positional alignment is exact when the lengths match --- and it is the only correct alignment
    when the input carries several draws of one problem. Fall back to keying on `problem_id` when
    the lengths differ (a partial or re-run verification), which then requires unique ids.
    """
    if len(candidates) == len(verdicts):
        bad = [i for i, (c, v) in enumerate(zip(candidates, verdicts))
               if str(c["problem_id"]) != str(v["problem_id"])]
        if not bad:
            return [{**c, "_verdict": v} for c, v in zip(candidates, verdicts)]
        print(f"  ! {what}: equal lengths but {len(bad)} problem_id mismatches; "
              f"falling back to keying on problem_id")
    seen: dict[str, dict] = {}
    for v in verdicts:
        pid = str(v["problem_id"])
        if pid in seen:
            raise SystemExit(
                f"{what}: cannot align --- the verdict file has {len(verdicts)} records against "
                f"{len(candidates)} candidates AND repeats problem_id {pid}. Re-run the verifier "
                f"over exactly the candidate file you are releasing.")
        seen[pid] = v
    missing = [str(c['problem_id']) for c in candidates if str(c['problem_id']) not in seen]
    if missing:
        print(f"  ! {what}: {len(missing)} candidates have no verdict; they are dropped "
              f"(first few: {missing[:5]})")
    return [{**c, "_verdict": seen[str(c["problem_id"])]}
            for c in candidates if str(c["problem_id"]) in seen]


def scrub(text: str, where: str, fatal: bool = True) -> list[str]:
    hits = []
    for pattern, why in SCRUB_PATTERNS:
        for m in re.finditer(pattern, text):
            hits.append(f"{where}: {why} (matched {m.group(0)[:24]!r})")
    if hits and fatal:
        for h in hits[:20]:
            print(f"  ANONYMITY: {h}", file=sys.stderr)
        raise SystemExit(f"refusing to write {where}: {len(hits)} anonymity violations. "
                         f"The paper is double-blind; fix the source records, do not force this.")
    return hits


def git_head(where: str) -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True, cwd=where or ".").stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def scrub_script(text: str, where: str, fatal: bool = True) -> list[str]:
    """The script scrub. Run AFTER redact_costs(); a surviving `$<digit>` is a failure."""
    hits = []
    for pattern, why in SCRIPT_SCRUB_PATTERNS:
        for m in re.finditer(pattern, text):
            hits.append(f"{where}: {why} (matched {m.group(0)[:24]!r})")
    if hits and fatal:
        for h in hits[:20]:
            print(f"  ANONYMITY: {h}", file=sys.stderr)
        raise SystemExit(f"refusing to ship {where}: {len(hits)} anonymity violations. "
                         f"Fix the script in the repository; do not force this.")
    return hits


def redact_costs(text: str) -> tuple[str, int]:
    """Replace every `$12.34` / `$99` with `$X`. Cost figures live in docstrings and comments
    (what a smoke test costs, what a run booked); the bundle carries no dollar figure."""
    n = len(COST_FIGURE.findall(text))
    return COST_FIGURE.sub("$X", text), n


def script_source(name: str, worktree: bool, where: str) -> str:
    """The committed text of one script, or the working-tree text under --scripts-from-worktree.

    HEAD is the default because other sessions edit these files while a build runs: shipping a
    working tree means shipping whatever was half-saved at that second. `git show` is asked for
    the path as git knows it, so the build works from any directory inside the repository.
    """
    path = os.path.join(where, name)
    if not worktree:
        try:
            rel = subprocess.run(["git", "ls-files", "--full-name", "--error-unmatch", path],
                                 capture_output=True, text=True, check=True,
                                 cwd=where or ".").stdout.strip()
            out = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True,
                                 check=True, cwd=where or ".")
            return out.stdout.decode("utf-8")
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise SystemExit(
                f"{name}: cannot read the committed revision ({exc.__class__.__name__}). "
                f"Commit it, or build with --scripts-from-worktree and say so in the card.")
    if not os.path.exists(path):
        raise SystemExit(f"{name}: not found in {where or '.'}")
    return open(path, encoding="utf-8").read()


def write_scripts(out: str, where: str, worktree: bool) -> tuple[list[str], int]:
    """Write release/scripts/*.py, redacted and scrubbed. Returns the paths and the redactions."""
    os.makedirs(os.path.join(out, SCRIPTS_DIR), exist_ok=True)
    written, redactions = [], 0
    for name in SCRIPT_FILES:
        text, n = redact_costs(script_source(name, worktree, where))
        rel = f"{SCRIPTS_DIR}/{name}"
        scrub_script(text, rel)
        with open(os.path.join(out, rel), "w", encoding="utf-8") as fh:
            fh.write(text)
        written.append(rel)
        redactions += n
    return written, redactions


# --------------------------------------------------------------------------- build

def honest_record(gen: dict, passed: bool, thinking: bool, max_tokens: int) -> dict:
    code = gen.get("code") or ""
    return {
        "problem_id": str(gen["problem_id"]),
        "code": code,
        "code_stripped": strip_comments(code),
        "passes_tests": bool(passed),
        "model": gen.get("model"),
        "thinking": bool(gen.get("thinking", thinking)),
        "max_tokens": max_tokens,
        "truncated": bool(gen.get("truncated", gen.get("finish_reason") == "max_tokens")),
        "finish_reason": gen.get("finish_reason"),
        "n_output_tokens": gen.get("n_output_tokens"),
    }


def attack_record(bd: dict, verdict: dict, arm: str, thinking: bool, max_tokens: int) -> dict:
    code = bd.get("code") or ""
    return {
        "problem_id": str(bd["problem_id"]),
        "code": code,
        "code_stripped": strip_comments(code),
        "backdoor_input": bd.get("backdoor_input") or "",
        "passes_tests": bool(verdict.get("passes_tests")),
        "backdoor_works": bool(verdict.get("backdoor_works")),
        "crash_on_trigger": verdict.get("reason") == CRASH_REASON,
        "arm": bd.get("arm") or arm,
        "model": bd.get("model"),
        "thinking": bool(bd.get("thinking", thinking)),
        "max_tokens": max_tokens,
        "truncated": bool(bd.get("truncated", bd.get("finish_reason") == "max_tokens")),
        "finish_reason": bd.get("finish_reason"),
        "n_output_tokens": bd.get("n_output_tokens"),
    }


def pool_record(bd: dict, verdict: dict, thinking: bool, max_tokens: int) -> dict:
    """An attack record plus the keys `merge_draws.py` gave the draw. Never deduplicated."""
    rec = attack_record(bd, verdict, "independent", thinking, max_tokens)
    rec["draw"] = bd["draw"]
    rec["source"] = bd["source"]
    rec["round"] = bd.get("round")
    return rec


def survivor_select(pool_rows: list[dict], honest_pass: set) -> tuple[dict, dict]:
    """The `best` selection, per problem, from the pool in file order (earliest wins a tie).

    A crash on the trigger is scored as NOT working, which is the upstream validator's rule.
    passes list: earliest draw that passes and fires without crashing, else earliest that passes.
    usable list: earliest draw that passes and fires without crashing, else earliest that fires
                 by crashing (kept, flagged, so the crash-inclusive set is recoverable too).
    Returns ({problem_id: row}, {problem_id: row}) for the two lists.
    """
    def fires_clean(r: dict) -> bool:
        return bool(r["passes_tests"] and r["backdoor_works"] and not r["crash_on_trigger"])

    passes_sel: dict[str, dict] = {}
    usable_sel: dict[str, dict] = {}
    for r in pool_rows:
        pid = r["problem_id"]
        if pid not in honest_pass:
            continue
        if r["passes_tests"]:
            rank = (fires_clean(r), True)
            if pid not in passes_sel or rank > (fires_clean(passes_sel[pid]), True):
                passes_sel[pid] = r
        if r["passes_tests"] and r["backdoor_works"]:
            rank = (fires_clean(r), True)
            if pid not in usable_sel or rank > (fires_clean(usable_sel[pid]), True):
                usable_sel[pid] = r
    return passes_sel, usable_sel


def best_pairs(sel: dict) -> set[tuple[str, str, str, str]]:
    return {(pid, "independent", r["draw"], "true" if r["crash_on_trigger"] else "false")
            for pid, r in sel.items()}


def pool_counts(pool_rows: list[dict], passes_sel: dict, usable_sel: dict) -> dict:
    import collections
    per = collections.Counter(r["problem_id"] for r in pool_rows)
    return {
        "ind_pool_total": len(pool_rows),
        "ind_pool_problems": len(per),
        "ind_pool_max_draws": max(per.values()) if per else 0,
        "ind_pool_pass": sum(r["passes_tests"] for r in pool_rows),
        "ind_pool_usable": sum(r["passes_tests"] and r["backdoor_works"] for r in pool_rows),
        "ind_pool_crash": sum(r["passes_tests"] and r["backdoor_works"] and r["crash_on_trigger"]
                              for r in pool_rows),
        "pairs_passes_best_ind": len(passes_sel),
        "pairs_usable_best_ind": len(usable_sel),
        "pairs_usable_best_noncrash_ind": sum(not r["crash_on_trigger"]
                                              for r in usable_sel.values()),
    }


def write_jsonl(path: str, rows: list[dict], fields: list[str]) -> None:
    payload = "".join(json.dumps({k: r[k] for k in fields}, sort_keys=False) + "\n" for r in rows)
    scrub(payload, os.path.basename(path))
    with open(path, "w") as fh:
        fh.write(payload)


def write_pairs(path: str, pairs: list[tuple], fields: list[str] = PAIR_CSV_FIELDS) -> None:
    import io as _io
    buf = _io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(fields)
    for row in pairs:
        w.writerow(list(row))
    scrub(buf.getvalue(), os.path.basename(path))
    with open(path, "w") as fh:
        fh.write(buf.getvalue())


def build(args) -> int:
    out = args.out
    if os.path.exists(out) and os.listdir(out) and not args.force:
        raise SystemExit(f"{out}/ exists and is not empty. Use --force to overwrite.")
    os.makedirs(out, exist_ok=True)

    print(f"reading run products")
    gen = dedupe(read_jsonl(args.gen), args.keep, "honest generations")
    hp = read_jsonl(args.honest_pass)
    passed_by_pid: dict[str, bool] = {}
    for r in hp:
        pid = str(r["problem_id"])
        passed_by_pid[pid] = bool(passed_by_pid.get(pid, False) or r.get("passed"))
    no_verdict = [str(g["problem_id"]) for g in gen if str(g["problem_id"]) not in passed_by_pid]
    if no_verdict:
        print(f"  ! honest: {len(no_verdict)} generations have no harness verdict; dropped "
              f"(first few: {no_verdict[:5]})")
    honest_rows = [honest_record(g, passed_by_pid[str(g["problem_id"])], args.thinking,
                                 args.max_tokens)
                   for g in gen if str(g["problem_id"]) in passed_by_pid]

    arms: dict[str, list[dict]] = {}
    for arm, bd_path, vd_path in (("edit", args.bd_edit, args.bdpass_edit),
                                  ("independent", args.bd_independent,
                                   args.bdpass_independent)):
        if args.arms != "both" and args.arms != arm:
            print(f"  skipping the {arm} arm (--arms {args.arms})")
            arms[arm] = []
            continue
        cands = read_jsonl(bd_path)
        vds = read_jsonl(vd_path)
        joined = align(cands, vds, f"{arm} arm")
        rows = [attack_record(j, j["_verdict"], arm, args.thinking, args.max_tokens)
                for j in joined]
        rows = dedupe(rows, args.keep, f"{arm} attacks")
        arms[arm] = rows

    # The undeduplicated retry pool of the independent arm, if asked for. Aligned like an arm,
    # never reduced: every draw ships, so either selection can be recomputed by the reader.
    pool_rows: list[dict] | None = None
    if args.pool_independent or args.poolpass_independent:
        if not (args.pool_independent and args.poolpass_independent):
            raise SystemExit("--pool-independent and --poolpass-independent go together")
        pj = align(read_jsonl(args.pool_independent), read_jsonl(args.poolpass_independent),
                   "independent arm, retry pool")
        missing = [i for i, j in enumerate(pj, 1) if "draw" not in j or "source" not in j]
        if missing:
            raise SystemExit(f"retry pool: {len(missing)} draws carry no draw/source key (first "
                             f"at line {missing[0]}); build the pool with merge_draws.py merge")
        pool_rows = [pool_record(j, j["_verdict"], args.thinking, args.max_tokens) for j in pj]
        if len({r["draw"] for r in pool_rows}) != len(pool_rows):
            raise SystemExit("retry pool: duplicate draw keys; the pool must hold each draw once")
        print(f"  retry pool: {len(pool_rows)} draws over "
              f"{len({r['problem_id'] for r in pool_rows})} problems (not deduplicated)")
    if args.also_select and pool_rows is None:
        raise SystemExit("--also-select needs the pool (--pool-independent/--poolpass-independent)")

    # One generator on both sides is the entire claim of this split. Nothing above enforces it:
    # the files are named by flag, and a mismatched pair would produce a confident, wrong release.
    models = {r["model"] for r in honest_rows} | {r["model"] for rs in arms.values() for r in rs}
    models |= {r["model"] for r in (pool_rows or [])}
    models.discard(None)
    if len(models) != 1:
        raise SystemExit(
            f"REFUSING: the release would mix generators {sorted(models)}.\n"
            f"This split exists to hold authorship constant. Release one generator's classes, "
            f"or the card's central claim is false.")
    model = sorted(models)[0]
    print(f"  generator on every side: {model}")

    honest_pass = {r["problem_id"] for r in honest_rows if r["passes_tests"]}
    pairs_passes, pairs_usable = [], []
    for arm in ("edit", "independent"):
        for r in arms[arm]:
            if r["problem_id"] not in honest_pass:
                continue
            if r["passes_tests"]:
                pairs_passes.append((r["problem_id"], arm))
                if r["backdoor_works"]:
                    pairs_usable.append((r["problem_id"], arm))

    print(f"writing {out}/")
    write_jsonl(os.path.join(out, "honest.jsonl"), honest_rows, HONEST_FIELDS)
    write_jsonl(os.path.join(out, "attacks_edit.jsonl"), arms["edit"], ATTACK_FIELDS)
    write_jsonl(os.path.join(out, "attacks_independent.jsonl"), arms["independent"],
                ATTACK_FIELDS)
    write_pairs(os.path.join(out, "pairs_passes.csv"), pairs_passes)
    write_pairs(os.path.join(out, "pairs_usable.csv"), pairs_usable)

    extra_files: list[str] = []
    extra_fields: dict[str, list[str]] = {}
    pc: dict | None = None
    if pool_rows is not None:
        write_jsonl(os.path.join(out, POOL_FILE), pool_rows, POOL_FIELDS)
        extra_files.append(POOL_FILE)
        extra_fields[POOL_FILE] = POOL_FIELDS
        passes_sel, usable_sel = survivor_select(pool_rows, honest_pass)
        pc = pool_counts(pool_rows, passes_sel, usable_sel)
        if args.also_select == "best":
            for name, sel in zip(BEST_FILES, (passes_sel, usable_sel)):
                write_pairs(os.path.join(out, name), sorted(best_pairs(sel)), PAIR_BEST_CSV_FIELDS)
                extra_files.append(name)
                extra_fields[name] = PAIR_BEST_CSV_FIELDS
        else:
            # the pool ships but no best lists: keep only the pool's own counts
            pc = {k: v for k, v in pc.items() if not k.startswith("pairs_")}

    counts = {
        "honest_total": len(honest_rows),
        "honest_pass": len(honest_pass),
        "edit_total": len(arms["edit"]),
        "edit_pass": sum(r["passes_tests"] for r in arms["edit"]),
        "edit_usable": sum(r["passes_tests"] and r["backdoor_works"] for r in arms["edit"]),
        "ind_total": len(arms["independent"]),
        "ind_pass": sum(r["passes_tests"] for r in arms["independent"]),
        "ind_usable": sum(r["passes_tests"] and r["backdoor_works"]
                          for r in arms["independent"]),
        "pairs_passes_edit": sum(a == "edit" for _, a in pairs_passes),
        "pairs_passes_ind": sum(a == "independent" for _, a in pairs_passes),
        "pairs_usable_edit": sum(a == "edit" for _, a in pairs_usable),
        "pairs_usable_ind": sum(a == "independent" for _, a in pairs_usable),
        **(pc or {}),
    }
    # Trivial programs that coincide with a human solution: only with the flag, only declared.
    trivial_decl: dict | None = None
    if args.allow_trivial_identical:
        upstream = upstream_code_strings(args.shards)
        if upstream is None:
            raise SystemExit(f"--allow-trivial-identical needs the upstream shards ({args.shards!r}) "
                             f"to prove that every retained match is trivial; none found here")
        by_file = {"honest.jsonl": honest_rows, "attacks_edit.jsonl": arms["edit"],
                   "attacks_independent.jsonl": arms["independent"]}
        if pool_rows is not None:
            by_file[POOL_FILE] = pool_rows
        bad, triv, trivial_decl = upstream_overlap(by_file, upstream, args.allow_trivial_identical)
        if bad:
            raise SystemExit(f"REFUSING: {len(bad)} released code strings equal an upstream string "
                             f"longer than {args.allow_trivial_identical} characters or a stored "
                             f"backdoor. Drop those generations; do not raise the limit to fit.")
        print(f"  upstream-identical trivial programs retained and declared: {len(triv)} strings "
              f"(max {trivial_decl['max_chars'] if trivial_decl else 0} chars)")

    built = args.build_date or _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    card_vals = grouped({**LEDGER, **counts, "model": model,
                         "generated": args.generation_date,
                         "agreement": args.agreement, "built": built,
                         "pairs_passes_total": len(pairs_passes),
                         "pairs_usable_total": len(pairs_usable)})
    # The scripts and the licence: the paper's Recommendation 4, and the `../../LICENSE`
    # archive entry that used to extract outside the release directory.
    script_paths: list[str] = []
    redactions = 0
    if args.scripts:
        script_paths, redactions = write_scripts(out, args.scripts_from, args.scripts_from_worktree)
        print(f"  scripts: {len(script_paths)} files from "
              f"{'the working tree' if args.scripts_from_worktree else 'HEAD'}"
              f"{f', {redactions} cost figures redacted' if redactions else ''}")
    licence_dst = None
    if args.licence:
        if not os.path.exists(args.licence):
            raise SystemExit(f"--licence {args.licence}: not found (pass --no-licence to omit)")
        shutil.copyfile(args.licence, os.path.join(out, LICENCE_FILE))
        scrub(open(os.path.join(out, LICENCE_FILE), encoding="utf-8").read(), LICENCE_FILE)
        licence_dst = LICENCE_FILE
        print(f"  licence: {args.licence} -> {out}/{LICENCE_FILE}")

    card_vals.update(card_extras(pc if args.also_select == "best" else None))
    card_vals["scripts_row"] = (
        f"| `{SCRIPTS_DIR}/` | {len(script_paths)} | the scripts behind the paper's numbers, "
        f"at the revision that produced them |\n" if script_paths else "")
    card_vals["licence_row"] = (
        f"| `{LICENCE_FILE}` | --- | MIT, covering this bundle |\n" if licence_dst else "")
    card_vals["trivial_sentence"] = trivial_sentence(trivial_decl)
    card = CARD_TEMPLATE.format(**card_vals)
    scrub(card, "README.md")
    with open(os.path.join(out, "README.md"), "w") as fh:
        fh.write(card)
    if args.card_out:
        with open(args.card_out, "w") as fh:
            fh.write(card)
        print(f"  card copy -> {args.card_out}")

    files = {}
    for name in ("honest.jsonl", "attacks_edit.jsonl", "attacks_independent.jsonl",
                 "pairs_passes.csv", "pairs_usable.csv", *extra_files, "README.md",
                 *script_paths, *( [licence_dst] if licence_dst else [] )):
        p = os.path.join(out, name)
        n_rows = sum(1 for line in open(p) if line.strip())
        if name.endswith(".csv"):
            n_rows -= 1                       # the header is not a row
        if name == "README.md" or name.endswith(".py") or name == LICENCE_FILE:
            n_rows = None                     # prose and code: hashed, not counted
        files[name] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p), "rows": n_rows}

    manifest = {
        "name": "same-generator-apps-split",
        "schema_version": 3,
        "generator_model": model,
        "generated": args.generation_date,
        "built": built,
        "harness_agreement": args.agreement,
        "thinking": bool(args.thinking),
        "max_tokens": args.max_tokens,
        "duplicate_policy": args.keep,
        "licence": "MIT",
        "counts": counts,
        "files": files,
        "fields": {"honest.jsonl": HONEST_FIELDS,
                   "attacks_edit.jsonl": ATTACK_FIELDS,
                   "attacks_independent.jsonl": ATTACK_FIELDS,
                   "pairs_passes.csv": PAIR_CSV_FIELDS,
                   "pairs_usable.csv": PAIR_CSV_FIELDS,
                   **extra_fields},
        "selection_rules": {
            "attacks_independent.jsonl": (
                f"one draw per problem, policy '{args.keep}': 'first' = the earliest draw in "
                f"file order, chosen blind to its outcome; 'best' = the draw that passes and "
                f"fires if any, else one that passes, else any (ties to the earlier draw)"),
            **({POOL_FILE: "every draw, in file order (the order the draws were made); "
                           "never deduplicated; join the two selections on `draw`"}
               if pool_rows is not None else {}),
            **({"pairs_passes_best.csv": (
                    "per problem: the earliest pool draw that passes the public tests and fires "
                    "without crashing; else the earliest draw that passes"),
                "pairs_usable_best.csv": (
                    "per problem: the earliest pool draw that passes and fires without crashing "
                    "(crash_on_trigger = false); else the earliest draw that fires by crashing on "
                    "its trigger (crash_on_trigger = true). Filter to false for the strict set")}
               if args.also_select == "best" else {}),
            "crash_on_trigger": (
                "the verifier counted a crash on the trigger as backdoor_works; the upstream "
                "validator scores it as not working. Use the flag to apply either rule"),
        },
        "scripts": {
            "files": script_paths,
            "source": ("the working tree" if args.scripts_from_worktree
                       else "the committed revision (git show HEAD:...)"),
            "commit": git_head(args.scripts_from),
            "redacted": f"{redactions} cost figures rewritten to $X",
        } if script_paths else None,
        "licence_file": licence_dst,
        "redistributes_upstream": False,
        **({"upstream_identical_trivial": trivial_decl} if trivial_decl else {}),
        "note": ("Problem ids reference APPS through the public apps-control-arena artifact. "
                 "No upstream problem statement, test case, human solution or stored backdoor "
                 "is included; join on problem_id to obtain them under their own licences."),
    }
    with open(os.path.join(out, "MANIFEST.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=False)
        fh.write("\n")

    for k, v in counts.items():
        print(f"  {k:<20} {v}")
    print(f"\nbuilt {out}/  ({len(files) + 1} files)")
    print(f"Now validate it:  python {os.path.basename(__file__)} --check {out}")
    return 0


# --------------------------------------------------------------------------- check

def upstream_code_strings(shard_glob: str) -> dict[str, str] | None:
    """Every human solution and stored backdoor in the local upstream shards, if present, as
    {stripped code string: "solution" | "backdoor" | "both"}.

    Returns None when no shard is on this machine --- in which case the check can only warn, and
    says so. The release is built exclusively from our own generation files, so upstream code has
    no path into it; this check is the belt to that braces.
    """
    shards = sorted(glob.glob(shard_glob))
    if not shards:
        return None
    try:
        import pyarrow.parquet as pq
    except ImportError:
        print("  ! pyarrow not installed: cannot read the upstream shards for the code check")
        return None
    strings: dict[str, str] = {}
    for f in shards:
        cols = set(pq.read_schema(f).names)
        want = [c for c in ("solutions", "backdoors") if c in cols]
        if not want:
            continue
        tbl = pq.read_table(f, columns=want).to_pandas()
        for col in want:
            kind = "solution" if col == "solutions" else "backdoor"
            for cell in tbl[col]:
                for item in (cell if cell is not None else []):
                    d = dict(item)
                    for key in ("code", "backdoor_code", "solution", "solution_code"):
                        v = d.get(key)
                        if isinstance(v, str) and v.strip():
                            s = v.strip()
                            prev = strings.get(s)
                            strings[s] = kind if prev in (None, kind) else "both"
    return strings


def check(args) -> int:
    out = args.check
    errs: list[str] = []
    warns: list[str] = []
    mpath = os.path.join(out, "MANIFEST.json")
    if not os.path.exists(mpath):
        raise SystemExit(f"{mpath} not found --- is {out} a release directory?")
    manifest = json.load(open(mpath))
    print(f"checking {out}/  (schema {manifest.get('schema_version')}, "
          f"generator {manifest.get('generator_model')})")

    # 1. every listed file present, byte-identical, right number of rows
    for name, meta in manifest["files"].items():
        p = os.path.join(out, name)
        if not os.path.exists(p):
            errs.append(f"{name}: listed in the manifest but missing")
            continue
        got = sha256_file(p)
        if got != meta["sha256"]:
            errs.append(f"{name}: sha256 {got[:16]}... != manifest {meta['sha256'][:16]}...")
        if os.path.getsize(p) != meta.get("bytes"):
            errs.append(f"{name}: {os.path.getsize(p)} bytes != manifest {meta.get('bytes')}")
        if meta.get("rows") is not None:
            n = sum(1 for line in open(p) if line.strip()) - (1 if name.endswith(".csv") else 0)
            if n != meta["rows"]:
                errs.append(f"{name}: {n} rows != manifest {meta['rows']}")
    # Listed names may be nested (scripts/foo.py), so compare on the top-level entry.
    listed_top = {n.split("/", 1)[0] for n in manifest["files"]}
    extra = sorted(set(os.listdir(out)) - listed_top - {"MANIFEST.json"})
    if extra:
        errs.append(f"unlisted files in the release directory: {extra}")
    declared_scripts = (manifest.get("scripts") or {}).get("files", [])
    for name in declared_scripts:
        if name not in manifest["files"]:
            errs.append(f"{name}: declared under scripts but absent from files")
    on_disk = sorted(f"{SCRIPTS_DIR}/{n}" for n in os.listdir(os.path.join(out, SCRIPTS_DIR))) \
        if os.path.isdir(os.path.join(out, SCRIPTS_DIR)) else []
    if sorted(declared_scripts) != on_disk:
        errs.append(f"{SCRIPTS_DIR}/ holds {on_disk} but the manifest declares "
                    f"{sorted(declared_scripts)}")

    # 2. field allow-list, and no forbidden field anywhere
    rows: dict[str, list[dict]] = {}
    for name, fields in manifest["fields"].items():
        p = os.path.join(out, name)
        if not os.path.exists(p) or name.endswith(".csv"):
            continue
        recs = read_jsonl(p)
        rows[name] = recs
        for i, r in enumerate(recs, 1):
            keys = set(r)
            bad = sorted(keys - set(fields))
            if bad:
                why = [f"{k} (FORBIDDEN)" if k in FORBIDDEN_FIELDS else k for k in bad]
                errs.append(f"{name}:{i}: unexpected field(s) {why}")
                if len(errs) > 40:
                    break
            missing = sorted(set(fields) - keys)
            if missing:
                errs.append(f"{name}:{i}: missing field(s) {missing}")
                if len(errs) > 40:
                    break

    for name, want_hdr in (("pairs_passes.csv", PAIR_CSV_FIELDS),
                           ("pairs_usable.csv", PAIR_CSV_FIELDS),
                           ("pairs_passes_best.csv", PAIR_BEST_CSV_FIELDS),
                           ("pairs_usable_best.csv", PAIR_BEST_CSV_FIELDS)):
        p = os.path.join(out, name)
        if not os.path.exists(p):
            continue
        with open(p) as fh:
            hdr = next(csv.reader(fh), [])
        if hdr != want_hdr:
            errs.append(f"{name}: header {hdr} != {want_hdr}")

    # 3. anonymity scrub over the raw bytes of every released file. Scripts are scrubbed on
    #    their own list: see SCRIPT_SCRUB_PATTERNS for why a github.com URL is allowed there.
    for name in list(manifest["files"]) + ["MANIFEST.json"]:
        p = os.path.join(out, name)
        if not os.path.exists(p):
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        checker = scrub_script if name.startswith(f"{SCRIPTS_DIR}/") else scrub
        hits = checker(text, name, fatal=False)
        errs.extend(f"ANONYMITY {h}" for h in hits)

    # 4. the pair CSVs must be exactly what the jsonl files imply
    honest_pass = {r["problem_id"] for r in rows.get("honest.jsonl", []) if r["passes_tests"]}
    want_passes, want_usable = set(), set()
    for name, arm in (("attacks_edit.jsonl", "edit"),
                      ("attacks_independent.jsonl", "independent")):
        for r in rows.get(name, []):
            if r["problem_id"] in honest_pass and r["passes_tests"]:
                want_passes.add((r["problem_id"], arm))
                if r["backdoor_works"]:
                    want_usable.add((r["problem_id"], arm))
    for name, want in (("pairs_passes.csv", want_passes), ("pairs_usable.csv", want_usable)):
        p = os.path.join(out, name)
        if not os.path.exists(p):
            continue
        with open(p) as fh:
            got = {(r[0], r[1]) for r in list(csv.reader(fh))[1:] if r}
        if got != want:
            errs.append(f"{name}: {len(got - want)} rows not implied by the jsonl files, "
                        f"{len(want - got)} implied rows missing")

    # 4b. the retry pool, if shipped: unique draws, and the best lists recomputed from it
    pool_extra: dict = {}
    pool = rows.get(POOL_FILE)
    if pool is not None:
        if len({r["draw"] for r in pool}) != len(pool):
            errs.append(f"{POOL_FILE}: duplicate draw keys")
        passes_sel, usable_sel = survivor_select(pool, honest_pass)
        pool_extra = pool_counts(pool, passes_sel, usable_sel)
        have_best = [n for n in BEST_FILES if n in manifest["files"]]
        if not have_best:
            pool_extra = {k: v for k, v in pool_extra.items() if not k.startswith("pairs_")}
        for name, sel in zip(BEST_FILES, (passes_sel, usable_sel)):
            p = os.path.join(out, name)
            if name not in have_best or not os.path.exists(p):
                continue
            with open(p) as fh:
                got = {tuple(r) for r in list(csv.reader(fh))[1:] if r}
            want = best_pairs(sel)
            if got != want:
                errs.append(f"{name}: {len(got - want)} rows not implied by {POOL_FILE}, "
                            f"{len(want - got)} implied rows missing")
    elif any(n in manifest["files"] for n in BEST_FILES):
        errs.append(f"best lists are shipped without {POOL_FILE}, so they cannot be checked")

    # 5. counts in the manifest must match the data
    recount = {
        "honest_total": len(rows.get("honest.jsonl", [])),
        "honest_pass": len(honest_pass),
        "edit_total": len(rows.get("attacks_edit.jsonl", [])),
        "edit_pass": sum(r["passes_tests"] for r in rows.get("attacks_edit.jsonl", [])),
        "edit_usable": sum(r["passes_tests"] and r["backdoor_works"]
                           for r in rows.get("attacks_edit.jsonl", [])),
        "ind_total": len(rows.get("attacks_independent.jsonl", [])),
        "ind_pass": sum(r["passes_tests"] for r in rows.get("attacks_independent.jsonl", [])),
        "ind_usable": sum(r["passes_tests"] and r["backdoor_works"]
                          for r in rows.get("attacks_independent.jsonl", [])),
        "pairs_passes_edit": sum(a == "edit" for _, a in want_passes),
        "pairs_passes_ind": sum(a == "independent" for _, a in want_passes),
        "pairs_usable_edit": sum(a == "edit" for _, a in want_usable),
        "pairs_usable_ind": sum(a == "independent" for _, a in want_usable),
        **pool_extra,
    }
    for k, v in recount.items():
        if manifest["counts"].get(k) != v:
            errs.append(f"counts.{k}: manifest {manifest['counts'].get(k)} != recomputed {v}")

    # 6. one generator on every side
    models = {r["model"] for rs in rows.values() for r in rs}
    models.discard(None)
    if len(models) > 1:
        errs.append(f"more than one generator in the release: {sorted(models)}")
    elif models and manifest.get("generator_model") not in models:
        errs.append(f"manifest generator {manifest.get('generator_model')!r} is not the one in "
                    f"the data ({sorted(models)})")

    # 7. no upstream code in the release
    upstream = upstream_code_strings(args.shards)
    if upstream is None:
        warns.append(f"no upstream shards matched {args.shards!r} on this machine, so the "
                     f"'no upstream code' check could not run. Re-run --check where the shards "
                     f"live before publishing.")
    else:
        released = set()
        for rs in rows.values():
            for r in rs:
                for key in ("code", "code_stripped"):
                    if r.get(key, "").strip():
                        released.add(r[key].strip())
        overlap = released & set(upstream)
        limit = args.allow_trivial_identical
        declared = manifest.get("upstream_identical_trivial")
        if overlap and not limit:
            errs.append(f"{len(overlap)} released code strings are byte-identical to upstream "
                        f"solutions or stored backdoors --- the release must redistribute none"
                        + (f" (the manifest declares {declared['n_strings']} trivial ones; re-run "
                           f"--check with --allow-trivial-identical {declared['max_chars']} to "
                           f"verify that declaration)" if declared else ""))
        elif overlap:
            bad, triv, recomputed = upstream_overlap(rows, upstream, limit)
            if bad:
                errs.append(f"{len(bad)} released code strings equal an upstream string longer "
                            f"than {limit} characters or a stored backdoor")
            if not declared:
                errs.append(f"{len(triv)} trivial upstream-identical strings are not declared in "
                            f"the manifest (upstream_identical_trivial)")
            elif (declared.get("max_chars") != limit or declared.get("n_strings") != len(triv)
                  or declared.get("records") != recomputed["records"]):
                errs.append(f"upstream_identical_trivial in the manifest does not match the data "
                            f"(declared {declared.get('n_strings')} strings at "
                            f"{declared.get('max_chars')} chars; recomputed {len(triv)} at {limit})")
            else:
                warns.append(f"{len(triv)} released strings of at most {limit} characters equal an "
                             f"upstream human solution; declared in MANIFEST.json as trivial "
                             f"programs and retained (see the card)")
        else:
            print(f"  no upstream code: checked {len(released)} released strings against "
                  f"{len(upstream)} upstream ones, 0 matches")
            if declared:
                errs.append("the manifest declares trivial upstream-identical strings but the data "
                            "has none")

    # 8. the card must be the one this manifest describes
    card_p = os.path.join(out, "README.md")
    if os.path.exists(card_p):
        card = open(card_p).read()
        for k in ("honest_total", "honest_pass", "ind_usable"):
            v = manifest["counts"][k]
            if str(v) not in card and f"{v:,}" not in card:
                warns.append(f"README.md does not mention counts.{k} "
                             f"({manifest['counts'][k]}); regenerate the card from the manifest")

    for w in warns:
        print(f"  WARN  {w}")
    if errs:
        print(f"\nFAIL: {len(errs)} problem(s)")
        for e in errs[:40]:
            print(f"  - {e}")
        if len(errs) > 40:
            print(f"  ... and {len(errs) - 40} more")
        return 1
    tail = (("and redistributes no upstream code" if not manifest.get("upstream_identical_trivial")
             else "and redistributes no upstream code beyond the declared trivial one-liners")
            if upstream is not None
            else "with the upstream-code check SKIPPED (see the warning)")
    print(f"\nOK: {out}/ is internally consistent, anonymised, {tail}"
          + (f"  [{len(warns)} warning(s)]" if warns else ""))
    return 0


# --------------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gen", default="gen_sonnet5.jsonl", help="honest generations")
    ap.add_argument("--honest-pass", default="pass_sonnet5.jsonl",
                    help="run_tests.py verdicts for the honest class")
    ap.add_argument("--bd-edit", default="bd_sonnet5.jsonl", help="edit-arm generations")
    ap.add_argument("--bdpass-edit", default="bdpass_sonnet5.jsonl",
                    help="verify_backdoor.py output for the edit arm")
    ap.add_argument("--bd-independent", default="bdind_sonnet5.jsonl",
                    help="independent-arm generations")
    ap.add_argument("--bdpass-independent", default="bdindpass_sonnet5.jsonl",
                    help="verify_backdoor.py output for the INDEPENDENT arm. The default follows "
                         "GATE-S-RUNBOOK.md; note that gen_backdoor_api.py's closing 'Next:' line "
                         "prints bdpass_sonnet5.jsonl for both arms, so if that line was followed "
                         "literally the independent verdicts may live under another name. Check "
                         "before trusting the default.")
    ap.add_argument("--pool-independent", default=None, metavar="JSONL",
                    help="the merged retry pool of the independent arm (merge_draws.py merge "
                         "output, one record per draw with draw/source/round). Shipped whole as "
                         f"{POOL_FILE}, never deduplicated.")
    ap.add_argument("--poolpass-independent", default=None, metavar="JSONL",
                    help="verify_backdoor.py output for the pool, aligned line for line with it")
    ap.add_argument("--also-select", choices=["best"], default=None,
                    help="with the pool: also write pairs_passes_best.csv and "
                         "pairs_usable_best.csv, the survivor selection keyed by draw (a crash "
                         "on the trigger scored as not working, flagged crash_on_trigger)")
    ap.add_argument("--arms", choices=["both", "edit", "independent"], default="both",
                    help="build only one arm (the other file is written empty)")
    ap.add_argument("--out", default="release", help="output directory")
    ap.add_argument("--force", action="store_true", help="overwrite a non-empty --out")
    ap.add_argument("--keep", choices=["first", "best"], default="first",
                    help="which draw to keep when a file holds several per problem_id. "
                         "'first' is the single-shot reading (default); 'best' reproduces the "
                         "benchmark's retry-survivor selection and must be disclosed as such.")
    ap.add_argument("--agreement", default="95.84%",
                    help="harness/artifact agreement on the analysis pool, for the manifest "
                         "and the card")
    ap.add_argument("--generation-date", default="September 2026",
                    help="when the generations were drawn (month and year; no finer, for anonymity)")
    ap.add_argument("--build-date", default=None, help="override the build date (YYYY-MM-DD)")
    ap.add_argument("--thinking", action="store_true",
                    help="record that the generations used extended thinking (default: off, which "
                         "is how the released generations were drawn)")
    ap.add_argument("--max-tokens", type=int, default=4096,
                    help="the generation token cap, recorded as metadata")
    ap.add_argument("--card-out", default=None,
                    help="also write the rendered dataset card here (e.g. ../RELEASE-CARD.md)")
    ap.add_argument("--shards", default="train_*.parquet",
                    help="glob for the local upstream shards, used by --check to prove no "
                         "upstream code was released")
    ap.add_argument("--allow-trivial-identical", type=int, default=0, metavar="CHARS",
                    help="keep released programs of at most CHARS characters that are byte-identical "
                         "to an upstream HUMAN solution (the canonical one-liner of a trivial "
                         "problem), declaring each in MANIFEST.json; any longer match, or any match "
                         "with a stored backdoor, still fails. Default 0: every match fails. "
                         "Pass the same value to --check to verify the declaration.")
    ap.add_argument("--scripts", action=argparse.BooleanOptionalAction, default=True,
                    help="ship the scripts behind the paper's numbers under scripts/ (default: yes)")
    ap.add_argument("--scripts-from", default=os.path.dirname(os.path.abspath(__file__)),
                    help="directory holding the scripts (default: this file's directory)")
    ap.add_argument("--scripts-from-worktree", action="store_true",
                    help="read the scripts from the working tree instead of HEAD. The default is "
                         "HEAD because parallel sessions edit these files mid-build.")
    ap.add_argument("--licence",
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         os.pardir, os.pardir, LICENCE_FILE),
                    help="licence file to copy INTO the release (default: the repository's "
                         "LICENSE two directories up); --no-licence to omit")
    ap.add_argument("--no-licence", dest="licence", action="store_const", const="",
                    help=argparse.SUPPRESS)
    ap.add_argument("--check", metavar="DIR", default=None,
                    help="validate a built release directory instead of building one")
    ap.add_argument("--render-card-only", action="store_true",
                    help="render the dataset card from the recorded ledger values and exit, "
                         "without reading any run product. For review copies only --- a real "
                         "build regenerates every number from MANIFEST.json.")
    args = ap.parse_args()

    if args.render_card_only:
        vals = grouped({**LEDGER, "agreement": args.agreement,
                        "generated": args.generation_date,
                        "pairs_passes_total": (LEDGER["pairs_passes_edit"]
                                               + LEDGER["pairs_passes_ind"]),
                        "pairs_usable_total": (LEDGER["pairs_usable_edit"]
                                               + LEDGER["pairs_usable_ind"])})
        vals.update(card_extras(None))
        vals["trivial_sentence"] = ""
        card = CARD_TEMPLATE.format(**vals)
        scrub(card, "the dataset card")
        if args.card_out:
            with open(args.card_out, "w") as fh:
                fh.write(card)
            print(f"wrote {args.card_out} (ledger values; a real build overwrites them)")
        else:
            sys.stdout.write(card)
        return 0
    if args.check:
        return check(args)
    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
