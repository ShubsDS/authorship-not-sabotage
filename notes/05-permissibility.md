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

Two local open-weight coder models write honest solutions to APPS problems that already ship with
human solutions and public tests. No scraping, no API, no new data about anyone. The generated
solutions and the rebuilt split are **released with the paper** — that release is B5 and it is the
main thing another group can reuse.

We also **execute** generated code for the first time in this project. It runs under per-case
timeouts, address-space limits and a scratch working directory — the same bar the standard APPS and
HumanEval harnesses use — on a machine we control, with no network dependence in the tests. That is
not a container, and the paper says so rather than implying an isolation it does not have.

## Compute

| Stage | Cost |
|---|---|
| Everything in `experiments/` | **$0** — laptop CPU, minutes |
| Monitor comparison, 24 × 1,375 | **$0** — `runs/scores/` is published and MIT. *This used to be a GPU gate.* |
| **Gate S** — vLLM, `Qwen2.5-Coder-7B-Instruct` **and** `-32B-Instruct`, one solution per problem for the 3,420 problems with a passing human solution, tests executed on CPU | **$0** — a held 2× H100 interactive Slurm allocation, ~1 GPU-hour total |
| Optional: one same-harness prompted monitor on the regenerated pool | **$0**, same allocation |
| **September total for this paper** | **$0** |

The binding constraints are **the test harness** (`../experiments/GATE-S-RUNBOOK.md` §4) and **writing
time**. Money is not one, and the free allocation also means Gate S can be **re-run** — there is no
one-shot GPU risk to plan around.
