# The standing rules that bind this paper

Carried from the ideation repo's eighteen rules, filtered to the ones with live obligations against
*this* paper. **Every one was bought with a failure**, and the failure is kept because the rule
without it is a slogan.

---

## R1 — Verify every citation by fetching the source

Never cite from a search snippet. `arxiv.org/abs/<id>` for title, full author list and date.
**Live debt:** three ids in `lit/01` §4 are ⚠️ — fetch them or drop them from the paper.

## R3 — A zero-result is citable only with a positive control in the same batch

Three separate ways this repo has fabricated a zero:

1. `http://export.arxiv.org` returns a **301**; a client that does not follow it gets an empty body
   that parses as `totalResults=0`. One sweep reported "zero hits"; the answer was 25.
2. Double-escaped quotes (`%2522`) — arXiv **silently ignores** malformed tokens and returns a
   date-sorted dump of recent submissions. A 40-result response that looked like a successful query
   was pure noise; the giveaway was neutrino detectors in a deception-probe search.
3. A throttled response is a **~14-byte body that also parses as zero.**

**In force here:** every zero in `lit/01` §2 and §4 has an in-batch positive control, and the three
HTTP 429 queries are recorded as *uncontrolled*, not as negatives.

## R5 — Prefer outcome-robust ideas, and re-check that the robustness is still real

Outcome-robustness can be destroyed by later literature without the idea changing. **In force here:**
Gate S's four routes are fixed in `PLAN.md` §3 *before* it runs, and both directions are a paper —
one of them with a different title.

## R8 — An `abs:` query cannot certify a claim about what papers *report*

Round 13 killed a candidate on this: Granite Guardian publishes ROC curves and a nine-guard
fixed-FPR leaderboard, and says none of those words in its abstract. Open the top ~10 papers and
grep their **results** sections.

## R9 — Search LessWrong and the Alignment Forum before claiming novelty in AI safety

A control that was one candidate's whole differentiator had been published on LessWrong in June.
**In force here:** `lit/01` §5, ~31 links across two sweeps, and the thesis turns out to exist in
prose in someone's limitations section. Say so.

## R15 — Read the *artifact*, not only the papers

Round 15 read three incumbents' papers, limitations sections included, and concluded a reframe was
the one formulation they did not contain. Round 16 read the **released repo** and found four
load-bearing numbers already published one directory below the paper — including one that
contradicted a gate threshold the plan was about to spend a day measuring.

**This rule paid twice on this paper.** `anik-jha/challenger-panels` ships `--leak-check` and two
published trivial baselines (killing a headline sentence), *and* ships `runs/scores/` — 24 monitors'
per-item scores on the exact split, which **deleted the GPU from the monitor comparison entirely**.

> **Corollary: check whether your gate is already answered before you schedule it.** A gate whose
> value is published is not a gate, it is a lookup. This is how Gate M died. **Grep for it first —
> and do that for Gate S route 1 (`RoganInglis/vllm-control-arena`) before renting anything.**

## R19 — The dataset card is not the dataset. Verify the data, not its description.

**New, 2026-09-04, and bought twice in one afternoon.**

R15 says read the artifact rather than only the papers. This is the level below: **read the *data*
rather than only the artifact's own description of itself.**

1. **This repo's `lit/01` recorded `RoganInglis/vllm-control-arena` as holding "model-generated APPS
   solutions with no attack/honest labels."** It holds no APPS data and no code whatsoever — 6,801
   coding *task descriptions* mined from vLLM git commits, with twelve `overlap_*` side-task scores and
   not one code column. An entire free route in the plan rested on that description.
2. **`RoganInglis/control-tax`'s card is actively false.** It advertises *"`solutions`: List of
   model-generated solutions (one per model)"* alongside a `models` column. In fact all 8,855 entries
   are byte-identical within every one of the 2,368 rows — the human APPS reference duplicated once per
   *attacker* model, to align positionally with `backdoors`. A reader who trusted the card would have
   concluded that LLM-written honest solutions were shipping, and built a control on them.

**The rule.** Before a dataset's description supports any plan step, **load the columns and compute one
statistic that the description implies.** Row count, distinct values, a byte-equality check against the
upstream source. It costs minutes. A card is written by hand, is not tested by CI, and can be wrong
about the file sitting next to it.

**Corollary, and it is the good half:** the same read that killed the route produced the paper's
cleanest evidence. `backdoors` carries `model` and `source`; `solutions` carries neither. **The
confound is in the schema.** Looking at the data rather than the description gives you both the
correction and the finding.

---

## R16 — Never schedule the check that could void a claim *after* the step that publishes it

A previous plan put the sweep that could void its framing into "dead time," **behind** a public
pre-registration. Run early, the sweep returned *partially occupied, severely*. Under the written
plan, a public pre-registration would have been timestamped on a four-fifths-occupied claim and we
would have learned it two days later.

**Order by irreversibility, not by cost. Cheapness is a reason to run something sooner.**

**Live obligation:** the AICD/CodeMirage setup sections (`lit/01` §8) run **before** the split is
released or the paper is posted.

## R17 — Verify a delegated number yourself before it becomes load-bearing

A subagent reported floor statistics from an n=1,000 sample it stated *"matches the full split
exactly."* On all 5,000 rows the headline replicated and got stronger — and two supporting figures
did not: `P(has_backdoor | difficulty=competition)` reported as **0/200 = 0.000**, actually
**203/1000 = 0.203**; difficulty-only AUROC reported **0.751**, actually **0.6823**. Either would
have gone into a paper as a headline sentence.

**A sampled statistic never enters a paper.** `experiments/RECOMPUTE.md` is the coordinator's own
recompute on the full artifact, and where it and a subagent report disagree, it wins.

**Companion:** serialize access to rate-limited endpoints across parallel agents. Three of our own
processes hit `export.arxiv.org` concurrently and sabotaged each other's negatives. Sleep ≥8 s,
treat any sub-1 KB response as transport failure, never run two sweeps at one host.

## R18 — A keyword grep of full text is still a grep; read the *setup* sections

**The rule this paper exists because of.** Twelve full-text greps for partial-input / hypothesis-only
/ TF-IDF / construct-validity returned 0/12. Re-run over seventeen papers with the positive controls
firing, the same zeros held. **They were true and useless.** `2605.15377` §4.1 states every protocol
arm the audit proposed, with its rationale, in a paragraph containing none of the grepped words;
`2506.05296` has an appendix titled *"Monitoring failed backdoors"*; `2608.16190` says backdoor
comments *"would otherwise leak the label."* **Three setup paragraphs, three kills, zero keyword hits.**

For the five nearest papers, read the data/setup/preprocessing section and the appendix titles, and
write **one line per paper** saying what they filtered, stripped, matched or excluded — *before*
claiming a preprocessing artifact is unreported.

> **Companion — compare on the same protocol or not at all.** Before writing any "X beats Y"
> sentence, write down **Y's split, Y's metric and Y's preprocessing**, and compute X under all
> three. The round-16 headline compared a problem-level metadata floor of 0.82 against "a published
> monitor at 0.64" that was a *pairwise accuracy* on a *matched* protocol where that floor is exactly
> 0.500. The apples-to-apples number — 0.806, above 20 of 24 monitors on Koran's own split — is
> **smaller** than the headline it replaced, and it is the only one that can go in a paper.
