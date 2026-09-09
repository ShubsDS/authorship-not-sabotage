# Permissibility, licences and compute

**Public datasets only · no experiments involving real people · nothing person-specific reported ·
local open-weight models, no paid API.** Everything below is checked against those.

## Is this research allowed? Yes, and nothing here is close to a line

- **No human-subjects research.** No recruitment, no intervention, no interaction with anyone, no new
  collection of data about anyone. This is secondary analysis of already-public corpora of *code and
  agent transcripts*. Not human-subjects research under the Common Rule; no IRB.
- **No third-party system is touched.** No probing of live APIs, no auditing of anyone's production
  service. Public HuggingFace datasets and local models on local hardware.
- **No person appears in any result.** The unit of analysis is a problem or a rollout.
- **We redistribute nothing.** The scripts fetch public artifacts at run time; `.gitignore` keeps
  every parquet out of the repo. What we release is *our split definition and our scripts*, not
  anyone's data.

  > ⚠️ **This was not true until 2026-09-09, and the paper must not repeat it carelessly.**
  > `experiments/apps/koran_test_code.pkl` was **tracked**: 24 MB holding the `solutions` and
  > `backdoors` code structs of `eugenekoran/apps-control-arena-high-quality` — the corpus that
  > **declares no licence** — together with `koran_samples.pkl` derived from it. Both are now
  > untracked and gitignored, and `fetch_inputs.py` + `bow.py` rebuild them, so the claim holds
  > **going forward**. **Untracking does not rewrite history: both blobs remain in earlier commits.**
  > If the repo is made public as-is, that history is public too. Decide deliberately whether to
  > rewrite it before release — do not discover this after the fact.
  >
  > `monitor-summary.json` (8 KB, Jha, **MIT**) is still tracked. MIT permits redistribution but
  > requires the licence notice travel with it; there is currently no `LICENSE` file and no
  > attribution notice in the repo. See the open item at the foot of this file.

## The one honest flag: two of the seven corpora declare no licence

| Artifact | Licence | Handling |
|---|---|---|
| `RoganInglis/apps-control-arena` | **MIT** | Fine. The APPS leg — the paper's main claim — runs entirely on this. |
| `anik-jha/challenger-panels` (`runs/scores/`, `runs/x0`, `runs/x2`) | **MIT** | Fine. The monitor comparison. |
| `eugenekoran/apps-control-arena-high-quality` | ⚠️ **none declared** | Aggregate statistics only; nothing redistributed; **state it in the paper.** |
| `adityaasinha28/control_arena_{bash,shade,iac,rogue_eval,agentdojo}` | ⚠️ **none declared** | Same handling. Also scope the title to *"public releases of"* rather than *"ControlArena"*, since these are one user's repackaging. |

This is a real defect and the mitigation is real too: we report only aggregates over data that is
already public and ungated, and we say the licences are absent rather than implying they are
permissive. **Do not skip that sentence to save a line.**

## What we generate ourselves (Gate S)

Local open-weight models write honest solutions to APPS problems that already ship with human
solutions and public tests. No scraping, no new data about anyone. The generated solutions and the
rebuilt split are **released with the paper** — that release is B5 and it is the main thing another
group can reuse.

> ### ⛔ OPEN DECISION — `gen_honest_api.py` breaks the "no paid API / $0" constraint
> **Raised 2026-09-09. Not resolved. Do not let this reach the paper unresolved either way.**
>
> Commit `e27ed50` added `experiments/apps/gen_honest_api.py`, a **Claude Sonnet 5 batch arm at
> roughly $17**. It is not mentioned in any markdown file in this repo — it exists only as a script
> — and it contradicts the standing constraint at the top of this file, the `$0` table below,
> `PLAN.md` §7, and the front-page README.
>
> **The case for it is the strongest on record.** The backdoors are `claude-3-7-sonnet-thinking`, so
> a Claude honest class is a **same-vendor** control, which answers the sharpest recorded objection —
> *"a collapse might just be Qwen-vs-Claude"* — and **no Qwen arm can**. It also does not depend on
> the cluster queue, which is currently the binding constraint on Gate S.
>
> **The case against** is that "$0, public data, local open-weight models only" is a constraint this
> project has stated publicly and repeatedly, and quietly breaking it is exactly the kind of
> provenance slippage this paper criticises in others.
>
> **Three caveats if it is used**, from the script's own header: the exact attack model
> (`claude-3-7-sonnet-20250219`) is retired, so this is same-vendor and same-lineage but a *later
> generation*; sampling parameters are unavailable on Sonnet 5, so the arm is not bit-reproducible
> the way the vLLM arms are; and thinking is off by default though the attacks came from a thinking
> model. **All three belong in Limitations, not buried.**
>
> **Resolve it one of three ways, and write the choice down here:**
> 1. Amend the constraint — *"local open-weight models, plus one paid same-vendor control arm at
>    $17, disclosed in the paper"* — and update this file, `PLAN.md` §7 and the README together.
> 2. Drop the arm and delete the script.
> 3. Keep the script unrun, clearly marked as not-used. (This is the current de facto state, and it
>    is the worst of the three, because nothing records the decision.)

We also **execute** generated code for the first time in this project. It runs under per-case
timeouts, address-space limits and a scratch working directory — the same bar the standard APPS and
HumanEval harnesses use — on a machine we control, with no network dependence in the tests. That is
not a container, and the paper says so rather than implying an isolation it does not have.

## Compute

| Stage | Cost |
|---|---|
| Everything in `experiments/` | **$0** — laptop CPU, minutes |
| Monitor comparison, 24 × 1,375 | **$0** — `runs/scores/` is published and MIT. *This used to be a GPU gate.* |
| **Gate S** — vLLM, `Qwen3.8-27B` **and** `Qwen3-Coder-30B-A3B-Instruct`, plus an 8B→14B→32B ladder; one solution per problem, tests executed on CPU | **$0** — cluster A100 batch jobs. *Revised 2026-09-08: the H100 allocation expired unused and the H100 queue does not clear before the deadline.* |
| **B**, the baseline Gate S routes against | **$0** — laptop CPU, ~10 min. Run 2026-09-09. |
| Optional: one same-harness prompted monitor on the regenerated pool | **$0**, same allocation |
| ⛔ `gen_honest_api.py`, Claude Sonnet 5 batch arm | **~$17 — NOT $0, and the decision is open.** See the box above. |
| **September total for this paper** | **$0 as run to date.** $17 if the Sonnet 5 arm is approved. |

The binding constraint is **writing time**. The test harness is built and validated. Money is not a
constraint, and batch jobs can be re-run — there is no one-shot GPU risk to plan around, only a
queue-time risk.

## ⛔ Open item — this repo has no `LICENSE` file

`PLAN.md` §4 marks *"the release of the split and the scripts"* as never-cut, and B5 makes the
regenerated pool the main reusable output. **A release with no licence is not a release** — it
leaves every reuser without permission, which is precisely the defect this paper flags in two of the
seven corpora it audits. Auditing unlicensed corpora from an unlicensed repo is an avoidable
own-goal a reviewer may notice.

MIT is the obvious default (it matches `RoganInglis/apps-control-arena` and
`anik-jha/challenger-panels`, the two artifacts this work builds on most directly), but **the choice
is the authors' and has not been made.** Whatever is chosen, add the file and include the MIT notice
for the `monitor-summary.json` that ships in the repo.
