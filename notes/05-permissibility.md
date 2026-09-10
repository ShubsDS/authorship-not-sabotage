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
  > **declares no licence** — together with `koran_samples.pkl` derived from it. Both were untracked
  > and gitignored on 2026-09-09, and `fetch_inputs.py` + `bow.py` rebuild them.
  >
  > ✅ **History rewritten 2026-09-10.** Untracking alone left both blobs in earlier commits of a
  > repo that is public, so the claim above was false for anyone checking out an older commit.
  > `git filter-repo --invert-paths` removed both from every commit, and `main` and
  > `paper-scaffold-and-baseline` were both force-pushed — the side branch mattered, because it
  > still carried both blobs after `main` was clean and would have kept them reachable. Verified
  > from a fresh mirror clone of the remote: no `.pkl` in any ref, no blob over 200 KB, whole repo
  > 548 KB. Working tree unchanged — the rewritten HEAD has a byte-identical tree hash and all 64
  > commits survive.
  >
  > ⚠️ **One residue, and it is not fixed by anything we can run.** GitHub keeps unreachable objects
  > and still serves them through its API to anyone who supplies the exact 40-character object hash;
  > this was confirmed by request after the force-push. Cloning, browsing and the network graph are
  > all clean, so the corpus is no longer *distributed* — but it is not *destroyed*. Only GitHub
  > Support can force the garbage collection. **Open that ticket before citing this repo as
  > evidence that we redistribute nothing.** The hashes are deliberately not recorded here or
  > anywhere else in the repo, because writing them down would publish the one key that retrieves
  > the data.
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

> ### ✅ RESOLVED BY EVENTS — option 1, recorded 2026-09-10
> **The arm ran on 2026-09-09 and cost $8.62** (1,444/1,444 requests succeeded;
> `experiments/RESULTS.md` §4.1). The backdoor half is in flight. The decision was therefore taken
> in practice before it was written down, which is the failure mode the box above warned about —
> recording it now rather than leaving the repo asserting "$0" while money is spent.
>
> **The standing constraint is amended to:** *public datasets only · no experiments involving real
> people · nothing person-specific reported · local open-weight models, **plus a metered
> same-vendor API arm, disclosed in the paper**.*
>
> **Why this is the right call and not a rationalisation.** Arm 1 settled it empirically:
> regenerating only the honest half with an open-weight model produced **ρ = 1.234** — separation
> *worse*, not better, because a Qwen-vs-Claude gap is larger than the human-vs-Claude one it
> replaced. Isolating content requires one model writing **both** classes, and the only such model
> in the stored backdoors' own lineage is behind a paid API. The constraint as originally written
> would have made the paper's central control unbuildable.
>
> **Three things now owed to Limitations**, unchanged from the box above: the exact attacker
> (`claude-3-7-sonnet-20250219`) is retired — verified by calling it, **404 on 2026-09-09** — so this
> is same-vendor and same-lineage but a *later generation*; sampling parameters are unavailable, so
> the arm is not bit-reproducible the way the vLLM arms are; and thinking is off by default though
> the attacks came from a thinking model. **Whichever is used, report it.**
>
> ⚠️ **The $100 ceiling is cited in `RESULTS.md` §4.2 but was defined nowhere.** It is recorded in
> the compute table below so that it governs something. Spend to date: **$8.62.**

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
| ✅ `gen_honest_api.py` — Sonnet 5 honest class, 1,444 problems, run 2026-09-09 | **$8.62 actual** (estimate was $5.00; output ran 1,057 tokens/solution against an assumed 600) |
| ⏳ `gen_backdoor_api.py` — Sonnet 5 attack class, 1,112 requests | in flight |
| **Spend to date** | **$8.62** |
| **Ceiling** | **$100.** Cited in `../experiments/RESULTS.md` §4.2 and, until 2026-09-10, defined nowhere. It lives here now. `estimate()` prints a worst case beside the point estimate because the worst case is the number a ceiling has to survive: the honest arm over all 5,000 rows would have been ~$30 actual with a **$102 worst case** — over the ceiling before a single backdoor. Restricting generation to the 1,444-problem analysis pool is what contained it. |

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
is the authors' and has not been made.** It is a one-line decision and nothing else blocks on it.

> ✅ **The third-party half is done (2026-09-10).** `THIRD-PARTY-NOTICES.md` now carries Jha's MIT
> licence in full for the `monitor-summary.json` this repo redistributes, which is what that licence
> requires of a redistributor. The tracked file was checked against upstream before the notice was
> written rather than after: **byte-identical**, 5,797 bytes, matching SHA-256 prefix `ca60d68c`,
> 24 rows. That notice stands whatever licence the authors pick for their own code.
>
> ⛔ **Still open: the repo's own `LICENSE`.** Redistributing someone else's MIT file correctly does
> not grant anyone permission to reuse *our* split definition or scripts. Until that file exists the
> release is still a release without a licence.
