# 12 — Final cold review and submission check (2026-09-11)

Written by a fresh reviewer who read `paper/main.pdf` **before** any source, then `paper/main.tex`,
`notes/09-review-audit.md`, `notes/01-venue-evorobust.md`, `notes/10-ledger-recheck.md` and
`experiments/RESULTS.md` §13–§15. Stance: EvoRobust @ NeurIPS 2026, robustness / benchmark-validity,
4 content pages, non-archival, double-blind, four-day review window. Nothing was run; `main.tex` was
**not edited** (§5 says why).

---

## 1. The review, as it would be posted

### Summary

Trusted monitoring in AI control is trained, tuned and ranked on stored honest/attack pairs. The
field already knows those pairs leak and preprocesses them (keep working solutions, strip comments).
This paper asks what survives that preprocessing and finds two floors on the field's own split: a
trained bag-of-words classifier at AUROC 0.806, above 20 of the 24 open-weight monitors ranked on the
same 1,375 items (median 0.609), and a classifier that reads no code at all — difficulty, test count,
question length — at 0.772, above 20 by point estimate and 17 with a paired interval. It then traces
the residue to *authorship*: the honest class is human APPS code and every backdoor is model-written;
the classifier transfers across backdoor generators (0.969 pairwise), is nearly as strong on inert
backdoors (0.879) as on working ones (0.935), and the residual carrier is `__main__`, untouched by
the stripper. Three controls follow. Regenerating only the honest half makes separation *worse*
(ρ = 1.234) — a published null about the obvious fix. One model writing both classes removes between
a third (Sonnet 5, ρ = 0.687) and nine-tenths (Haiku 4.5, ρ = 0.095) of the separability. Matching
the attack prompt's framing on the honest side takes Sonnet's ρ to 0.394 with a prompt-only floor of
0.6006, so most of what is left is the layout the attack prompt elicits rather than the backdoor. A
zero-shot monitor deflates far harder than the classifier (monitor-ρ 0.145 against 0.687), and a
second artifact is documented: labelling by `backdoor_works` defines the negative class by attack
failure at the problem level, which is where the content-blind 0.772 comes from. Four
recommendations and a released same-generator split close it.

### Strengths

1. **Measurement discipline well above the workshop median.** Every headline number carries a
   bootstrap over problems, a permutation null, and — against the 24 monitors — a *paired* bootstrap,
   with both the point-estimate count (20) and the paired-interval count (18) reported. Intervals now
   say which point estimate they are intervals of (`on the pooled out-of-fold 0.766`, `on the
   pooled-score 0.86`), which is rarer than it should be.
2. **The decisive control was run, twice, and the pre-registered rule was honoured.** Bands were
   fixed before any arm ran; the Sonnet arm returns *inconclusive between partial and content* and
   the paper prints those words instead of rounding to a verdict. The learning curve (B = 0.8521 ±
   0.0055 at n = 623) forecloses the "it is just sample size" reply.
3. **Negative results are reported as results.** Arm 1 (ρ = 1.234) is published as a null about the
   method; the AICD token replication fails with the wrong sign and is reported with its power
   caveat; the comments-kept values are printed beside the stripped ones and labelled *inflated by
   the comment channel* — the paper's thesis applied to itself.
4. **The free negative control is elegant.** Five agentic corpora where the same three models write
   both classes give a structural floor (`bash` 0.504, on its null; `agentdojo` 0.802 from character
   count) with no authorship confound possible. It converts "your floor is an artifact of your
   pipeline" into a per-benchmark instrument.
5. **The recommendations are precedented, not invented** (CodeMirage's line/character gating,
   MultiAIGCD's shared problem definitions), and the tension with Recommendation 3 — the headline
   attack class is 97.75% inert and the strict row is the compliant one — is named in the body rather
   than hidden.

### Weaknesses

1. **The central paragraph is not readable in a four-day window.** §3's Gate S paragraph is one
   ~30-line block carrying six protocols (Sonnet headline, Sonnet strict, prompt-matched headline,
   prompt-matched strict, Haiku headline, Haiku prompt-matched), two detectors, roughly forty
   numbers, two pre-registered bands and three interval conventions. A specialist can follow it on a
   second pass; the robustness/evolutionary-computation reviewer this venue actually fields will not.
   Everything needed to accept the paper is inside that block, which makes readability the binding
   constraint on the score rather than the evidence.
2. **The abstract crosses two protocols in its most quotable sentence.** "scoring 0.9579 on the
   stored pairs and 0.818 on firing backdoors from the same author" puts the *headline* stored score
   (n = 623) beside the *strict* same-generator score (n = 99). The same-row pair is 0.9437 → 0.818.
   A reviewer who checks this in the appendix finds the paper doing, in its abstract, the
   cross-protocol splice its own §3 spends a sentence warning against.
3. **"Trusted monitor" is the wrong name for the monitor that produces the headline ratio.** The
   monitor scoring 0.9579/0.566 is `claude-sonnet-5` — the model that wrote both classes. It is a
   self-evaluation by a frontier model, not a trusted (weaker) monitor in the ControlArena sense. The
   paper's own ledger tells it not to use that word. The body's "a monitor that wrote neither class
   returns the same two ratios" is the defence, but it arrives as an aside and the reader is never
   told the first monitor *is* the generator.
4. **The two generators disagree by 7× and the paper reports the range rather than the reason.** ρ =
   0.687 and ρ = 0.095 are not two samples of one quantity: the appendix shows Haiku never adopts the
   attack prompt's layout at all (`def main`, `sys.stdin`, `data[` at 0.000 in all three of its
   classes). So the headline range measures *whether a generator complies with the prompt's layout*,
   not how much of the stored benchmark is authorship. That is a more interesting finding than the
   range, and it is buried in appendix prose.
5. **"Most of what remains" is 44.7% on the paper's own arithmetic.** Prompt matching takes ρ from
   0.712 to 0.394 on the same 586 problems — a 44.7% reduction, which the ledger itself calls "most".
   The claim is rescuable only via the prompt-only floor (S_matched 0.6423 against a 0.6006 floor
   built with no attack class at all), and that is the argument the paper should be making in the
   sentence rather than behind it.
6. **The strict row carries more weight than n = 99 can bear.** It is the row that complies with
   Recommendation 3, the row the abstract's last clause rests on, and the row whose ρ interval
   (0.662–1.089) spans partial, content and ρ > 1. The paper says "at low power" — correctly — and
   then lets the abstract state the conclusion flatly.
7. **One APPS-derived family.** The headline is one HuggingFace artifact plus one filtered view of
   it; five of the seven corpora are one user's repackaging. Scoped honestly in §1 and §5, but the
   title asks a general question the evidence answers for one benchmark and five agentic settings.

### Questions to the authors

1. Which model is the monitor in "The same zero-shot trusted-monitor prompt scores 0.9579…"? If it
   is the model that wrote both same-generator classes, say so in that sentence.
2. Why is the abstract's monitor pair 0.9579/0.818 rather than the same-row 0.9437/0.818?
3. Haiku's residual collapses because it never writes `def main`/`sys.stdin` at all. Does that make ρ
   a measure of prompt compliance rather than of authorship share? What would you expect from a
   generator that adopts the layout but is not Claude?
4. Prompt matching removes 44.7% of the above-chance signal. On what reading is that "most of what
   remains"? (I assume the prompt-only floor; please put it in the sentence.)
5. The neither-class monitor lost ~50% of its headline replies to a 512-token ceiling, with
   class-differential missingness on the stored side. §3 quotes its ratio 0.151 as a point. Is it a
   point or a bound?
6. Where in the supplementary bundle is the MIT-licensed file of published monitor scores the
   appendix says "our release carries"? I could not find it in the zip.
7. The bundle ships one generator's split. The paper's two-generator claim and the prompt-matched arm
   are not reproducible from it. Is that deliberate for the submission version?

### Score

**6 / 10 — weak accept, confidence 4.**

For a non-archival workshop whose audience is robustness-literate but not AI-control-native, this is
above threshold: the core claim (your evaluation corpus's label is recoverable without reading a
backdoor, and much of that is who wrote the code) is demonstrated, controlled and hedged, and the
recommendations are usable tomorrow. It is not a 7 because the one paragraph that carries the
contribution cannot be read at review speed, and because the abstract states two things — the
monitor ratio and "surface content" on firing attacks — more flatly than the body supports. Both are
edits, not experiments, which is why my confidence that a revision clears 7 is high.

**Is the Gate S paragraph readable by a non-specialist in a four-day window?** No. It is ~30 lines,
six protocols and ~40 numbers in one block with no visual break. The numbers are right and the
hedges are present, which is exactly why it is frustrating: the paper has already done the work and
then makes the reviewer reconstruct the design from a wall of parentheses. Two paragraph breaks and
a five-row table would fix it.

**Do the abstract's numbers read well as rendered?** Partly. "ρ = 0.687" and "ρ = 0.095" read well
and the "a third / nine-tenths" gloss beside them is the right move. **"0.9579" does not**: four
decimals in an abstract is false precision, it is the only 4-dp number among 3-dp neighbours
(0.687, 0.095, 0.818), and the digit that matters is "0.96". Round it, or drop the number and keep
the ratio.

### The single change that would most raise the score

Make the Gate S paragraph legible without losing a number: **break it into three paragraphs and
replace ~12 lines of its prose with a five-row table** — one row per arm (Sonnet headline, Sonnet
prompt-matched, Sonnet strict, Haiku headline, Haiku prompt-matched), columns *S*, *B′*, *ρ (95% CI)*,
*n*, *band* — leaving the prose to carry only the ablations and the reading. The body has zero free
lines (§4), so this has to be paid for, and this table is what it should be paid for: it is the only
change that moves the paper from "the evidence is in there" to "the evidence is on the page".

---

## 2. Must-fix

Ordered by risk. "Ledger" = `experiments/RESULTS.md` / `notes/10-ledger-recheck.md`.

**M1 — the abstract splices two protocols.** "scoring \monStoredHead{} on the stored pairs and
\monitorStrict{} on firing backdoors from the same author": 0.9579 is the stored *headline* row
(n = 623, RESULTS §14.2) and 0.818 is the same-generator *strict* row (n = 99, §14.3). The same-row
number is \monStoredStrict{} = 0.9437. Fix: swap `\monStoredHead` → `\monStoredStrict` in the
abstract (identical rendered width, six digits either way), or name both rows.

**M2 — "trusted monitor" names a self-evaluation.** Abstract "A zero-shot trusted monitor" and §3
"The same zero-shot trusted-monitor prompt" both denote `claude-sonnet-5`, the model that wrote both
same-generator classes. RESULTS §14.7 states the paper "should say 'a smaller model of the same
family', not 'a trusted model' in the ControlArena sense". Also, §3's "The **same** …prompt" has no
antecedent in the body — the monitor prompt is never introduced before it is reused.

**M3 — an appendix sentence is false against the shipped supplementary.** `app:harness`: "Our
release carries one MIT-licensed file of published monitor scores, with its notice; the monitor
scores in Figure 1 are `runs/x0/monitor-summary.json` of that release." `unzip -l
same-generator-apps-split.zip` = 37 entries; there is no `monitor-summary.json` in it. The file is
redistributed in the *repository* (`THIRD-PARTY-NOTICES.md`, `experiments/apps/`), which reviewers
never see. Rewrite to attribute it to \cite{jha2026decorrelation}'s release (shorter; see NF3).

**M4 — "Half the gap" is wrong arithmetic.** `app:secondpass`: "Half the gap between our single-shot
firing rate and the stored attacker's is our own attack prompt". Ours is 2.5%, the stored attacker's
67.2%; removing the public-input-trigger defect moves ours to ≈5.1% (52.0% of draws at 0.15%, 48% at
5.13%), i.e. it closes ~4% of a 64.7-point gap. The prompt halves *our rate*, not the gap. One-clause
fix in NF4.

**M5 — the abstract's last content clause outruns the pre-registered band.** "what survives on
attacks that actually fire is surface content a monitor also reads": the prompt-matched strict row is
ρ = 0.697 (0.494–0.856) — *below* the paper's own content line of 0.72, P(ρ > 0.72) = 0.281 — and
RESULTS §13.6 says "consistent with content, at the n = 96 this arm has". "is surface content" should
be "is consistent with content" or "is content a monitor also reads, at n = 96".

**M6 — a bounded number is quoted as a point in the body.** §3: "a monitor that wrote neither class
returns the same two ratios (0.151, 0.749)". 0.151 derives from a row where 628 of 1,246 replies were
lost to a 512-token ceiling, with class-differential missingness on the stored side (50.1% honest vs
23.4% attack). `notes/10` §"Is the block safe to paste?" condition 2: that number "must never appear
without §14.5's missingness caveat". The appendix has the caveat; the body has no pointer to it.

**M7 — "(appendices A, A)" renders on page 3.** Every appendix cross-reference resolves to the single
appendix section "A" because all appendix units are `\paragraph`. Nine body references read
"(appendix A)" — uninformative but not wrong — and the two-reference case renders as a visible
defect. Fix: promote the appendix `\paragraph`s to `\subsection` (refs become A.1…A.9). This adds ~2
characters per body reference and therefore **must be paired with a cut** (see M8).

**M8 — the page budget is exhausted, and `paper/README.md` §3 says otherwise.** The README claims
"three free lines by the probe" (N = 3). Re-run today: **N = 0** — one `\noindent PROBELINE\\` before
`\bibliographystyle` already lands on page 5. Confirmed independently with `pdftotext -bbox-layout`:
page 4's last body baseline is yMax = 722.15, identical to the last baselines of pages 3 and 5, i.e.
the block is full to the same bottom edge. **Any addition to §1–§5 must be paid for by a cut of equal
length.** Update the README before someone edits on the strength of it.

**M9 — the deadline arithmetic in `notes/01` is 30 minutes optimistic.** `notes/01` records
"EvoRobust Sep 13 12:29 UTC = Sep 12 AoE" while quoting the CFP's own "All deadlines are 11:59 PM
AoE". Sep 12 23:59 AoE = **Sep 13 11:59 UTC**. Use 11:59 UTC as the wall.

**M10 — the one venue item not closable from the repo: is a checklist required?** `notes/01`'s
EvoRobust row records format (4 content pages, 5 camera-ready, unlimited references and
supplementary, NeurIPS 2026 style, 50 MB), archival status, dual submission and abstract
registration — and says nothing about a paper checklist. `paper/checklist-reference.tex` is
deliberately not `\input`. Confirm on the OpenReview submission form before uploading; it is a
two-minute check and the only rule I cannot verify from here.

### Checked and clean (do not re-check these)

| Check | Result |
|---|---|
| Body page count | **4 content pages.** References begin on page 5; the appendix follows the references, which the venue does not count. |
| Overfull boxes | **0** (`main.log`). One underfull hbox at lines 719–729, invisible in the PDF. |
| Double-blind, `main.tex` | No author names, affiliations, emails, repo URLs, acknowledgements, "our earlier version" or dollar figures. `grep -niE "cost\|spend\|USD\|\\$[0-9]"` on both source and PDF text: empty. |
| PDF metadata | `Author:` and `Title:` empty; Creator/Producer are pdfTeX defaults. |
| Anonymity block | Emitted by `neurips_2026.sty` under `dblblindworkshop`; `\author{}` carries no real name. |
| Only external URL | `github.com/anik-jha/challenger-panels` inside bibliography entry [9] — a third-party citation, not a leak. |
| AgentHarm exclusion sentence | "whose author is an invited speaker at this venue" — venue-identifying, not author-identifying. Correct per `notes/01` G2. Must change if the paper is submitted elsewhere. |
| Supplementary anonymity | `release/README.md`, `release/MANIFEST.json`, `release/LICENSE` and the data files grepped for names, emails, `@…`, `/home/`, `/u/`, `/Users/`, `github.com`, ORCID, acknowledgements: **no hits**. LICENSE reads "Copyright (c) 2026 The authors of 'What Survives the Filter?'". |
| Supplementary contents vs the paper | 37 entries, **24 scripts** (matches `\relScripts`), `LICENSE` inside `release/` (the `../../LICENSE` defect from `notes/09` #22 is fixed). MANIFEST counts 1,444 / 1,112 / 1,112 / 11,565 / 623 / 14 / 1,046 / 106 / 99 — every one matches the appendix release sentence. |
| Size limits | `main.pdf` 205 KB; zip 26 MB against a 50 MB cap. |
| Body prose numbers not carried by macros | Only 0.116 / 0.000 (RESULTS §6.x `has_main`), "152 versus 1 of 1,209" (`TOKEN-TEST.md`), "50-pair floor", "82 test pairs", "8 of their 10 canonical tokens", "512"/"1,024"/"2 of 198", "247 tasks". All verified. |
| F1's hardcoded values vs the macros | All 16 agree (0.8063, 0.8914, 0.7715 ± 0.0389, 0.7163, 0.4726, 0.4983, 0.6957, 0.8917, 0.6823, 0.7881, 0.5000, 0.897, 0.935, 0.879, 0.969, 0.962, 0.979, 0.955, 0.994, 0.826). |
| "one of ten named models" | **Correct**, and it looks wrong. `scan/FINDINGS.md` says "9 named LLMs + 2,516 unknown"; `K1-artifact-lineage.md` §(b) shows the shipped parquet labels the `source=apps` rows `openai/gpt-4`, giving ten distinct models on the Koran split. Leave it. |

---

## 3. Nice-to-fix, ranked by value per line of body space

Body lines are the scarce resource (M8: zero free). Items NF1–NF4 are free or negative in length;
NF5 costs only appendix space, which the venue does not count.

**NF1 — two paragraph breaks in the Gate S paragraph. Cost: ≤1 line. Value: the whole review.**
Insert `\par`-level breaks at two places in §3's Gate S block, before:
> `What survives is lexical: length-only falls to \sameGenLen{} while TF-IDF holds.`

and before:
> `A monitor is inflated the same way.`

Result: one paragraph of design and the two generators' ρ, one of ablations and prompt matching, one
of the monitor. No word changes, no number moves.

**NF2 — the abstract's monitor sentence (fixes M1 and M2 at once, −10 characters).**
Replaces:
> `A zero-shot trusted monitor is inflated the same way, scoring \monStoredHead{} on the stored pairs and \monitorStrict{} on firing backdoors from the same author.`

With:
> `A zero-shot monitor is inflated the same way, scoring \monStoredStrict{} on stored pairs and \monitorStrict{} on firing backdoors from the same author.`

**NF3 — the release/monitor-scores sentence (fixes M3, −36 characters).**
Replaces:
> `Our release carries one MIT-licensed file of published monitor scores, with its notice; the monitor scores in Figure~\ref{fig:monitors} are \texttt{runs/x0/monitor-summary.json} of that release.`

With:
> `The monitor scores in Figure~\ref{fig:monitors} are \texttt{runs/x0/monitor-summary.json} of \cite{jha2026decorrelation}'s MIT release, used under its notice.`

**NF4 — the funnel's "half the gap" (fixes M4, −43 characters).**
Replaces:
> `Half the gap between our single-shot firing rate and the stored attacker's is our own attack prompt: \trigPublicShare{} of our test-passing draws offer a public test input as the trigger,`

With:
> `Our own attack prompt halves our single-shot firing rate: \trigPublicShare{} of our test-passing draws offer a public test input as the trigger,`

**NF5 — one clause in the appendix monitor paragraph. Cost: 2 appendix lines, 0 body lines.**
Append to `The monitor rows, and what bounds the second monitor.`:
> `On the stored pairs both monitors beat the bag-of-words baseline over the same problems (\(+0.09\) and \(+0.15\) for the first, \(+0.02\) and \(+0.09\) for the second): Figure~\ref{fig:monitors}'s ranking is a statement about those monitors on that split, not a claim that a bag of words beats a monitor here.`

This is RESULTS §14.2's own instruction ("that distinction should survive into the paper") and it
pre-empts the single most likely hostile reading of Figure 1. Highest-value item on this list after
NF1, and it costs nothing that counts.

**NF6 — attach the presence rates to the feature they measure (−2 characters).**
Replaces:
> `the top attack-side features are \texttt{def main} and \texttt{data[} (\defMainAttack{} vs \defMainHonest{} of pair sides)`

With:
> `the top attack-side features are \texttt{def main} (\defMainAttack{} vs \defMainHonest{} of sides) and \texttt{data[}`

As written the parenthetical reads as covering both features; the ledger's `data[` rates are 37.7%
vs 13.6%.

**NF7 — flag the bounded ratio in the body (fixes M6, +19 characters).**
Replaces:
> `returns the same two ratios (\monHaikuRhoHead{}, \monHaikuRhoStrict{}).`

With:
> `returns the same two ratios (\monHaikuRhoHead{}, a bound at half missingness, and \monHaikuRhoStrict{}).`

**NF8 — the dangling count in §1 (+8 characters).**
Replaces:
> `question length, reaches \nocodeCV{}, above \nocodeCVCount{}.`

With:
> `question length, reaches \nocodeCV{}, above \nocodeCVCount{} of them.`

**NF9 — §1's bare citation as a subject (+4 characters).**
Replaces:
> `\cite{sreevatsa2026legibility} is an entire paper on the comment channel.`

With:
> `an entire paper \cite{sreevatsa2026legibility} is devoted to the comment channel.`

Numeric citation styles read badly when the number is the sentence's subject; this is the only such
occurrence.

**NF10 — Haiku's mechanism deserves a body clause, if NF1's table frees the room.** The appendix's
"`def main`, `sys.stdin`, `data[` … present in 0.000 of the second generator's programs in all three
of its classes" is the *explanation* of the 7× ρ gap and it is the paper's most interesting single
fact. One clause after "on an attack class 99.67% inert": `--- a generator that never adopts the
prompt's layout ---`. Costs ~1 line; buys weakness 4 of the review above.

---

## 4. Number verification

Every value in the abstract and in §3's Gate S paragraph, against `RESULTS.md` §9–§15 (and the jsons
those sections name). "Ledger" quotes the source at full precision.

### 4.1 Abstract

| # | Paper as rendered | Ledger | Source | Match |
|---|---|---|---|---|
| 1 | "above roughly four-fifths of the open-weight monitors" | 20 of 24 = 0.833 by point, 18 by paired CI | §8 (`0.8063`, per-monitor table) | ✅ |
| 2 | "a classifier that reads no code at all … scores above most of them" | 0.7715, above 20 of 24; 17 by paired CI | §8 | ✅ |
| 3 | ρ = 0.687 (Claude Sonnet 5) | 0.687 fold-mean, joint CI 0.625–0.755 | §9.1 row 1 / §13.2 | ✅ |
| 4 | "removes between a third" | 1 − 0.687 = 0.313 | arithmetic | ✅ |
| 5 | ρ = 0.095 (Claude Haiku 4.5) | 0.0950, joint CI 0.0445–0.1500 | §15.3 | ✅ |
| 6 | "and nine-tenths" | 1 − 0.095 = 0.905 | arithmetic | ✅ |
| 7 | "matching the attack prompt's framing removes most of what remains" | ρ 0.712 → 0.394 on the same 586 = **44.7%** of the above-chance signal; "most" holds only via the prompt-only floor (0.6423 against 0.6006) | §13.2, §13.6 | ⚠️ defensible, not as stated |
| 8 | "what survives on attacks that actually fire is surface content" | prompt-matched strict ρ = 0.697 (0.494–0.856), P(ρ > 0.72) = 0.281 — **partial** band by point; ledger says "consistent with content, at the n = 96" | §13.2, §13.6 | ❌ overstated (**M5**) |
| 9 | 0.9579 "on the stored pairs" | 0.9579 = Sonnet monitor, stored pairs, **headline** row, n = 623 | §14.2 row 1 | ✅ value |
| 10 | …paired with 0.818 "on firing backdoors" | 0.8182 = Sonnet monitor, same-generator **strict** row, n = 99; the same-row stored value is 0.9437 | §14.3 rows 1 and 3 | ❌ cross-protocol (**M1**) |
| 11 | "a zero-shot **trusted** monitor" | the monitor is `claude-sonnet-5`, the generator of both classes; §14.7 says not to call it trusted | §14, §14.7 | ❌ (**M2**) |
| 12 | "with an open-weight model writing the honest class … separability rises" | arm 1, Qwen3-Coder-30B, G = 0.962 vs B′ = 0.874, ρ = 1.234 | §3 | ✅ |

### 4.2 The Gate S paragraph, §3

| # | Paper as rendered | Ledger | Source | Match |
|---|---|---|---|---|
| 1 | 2.2% of draws fire | 14 / 623 = 2.25% | §13.6, `notes/10` §7 | ✅ |
| 2 | the split's own 80.7% inert class | 80.7% of 892 labelled backdoors | §7 (982) | ✅ |
| 3 | S = 0.751 (0.7295–0.7713; n = 623) | 0.7512, 0.7295–0.7713, n = 623 | §9.1 row 1 | ✅ |
| 4 | B′ = 0.8658 | 0.8658 (0.8480–0.8812) | §9.1 row 1 | ✅ |
| 5 | ρ = 0.687 (0.625–0.755, joint bootstrap) | 0.687 fold-mean; joint 0.625–0.755 (S-only 0.627–0.742) | §12.2, §13.2 | ✅ |
| 6 | second generator n = 611 | 611 = 1,051 honest passers ∩ 689 attack passers | §15.3 | ✅ |
| 7 | S = 0.5340, B′ = 0.8584 | 0.5340 (0.5159–0.5531), 0.8584 (0.8397–0.8737) | §15.3 | ✅ |
| 8 | ρ = 0.095 (0.044–0.150) | 0.0950, joint 0.0445–0.1500, P(≤0.33) = 1.0000 | §15.3 | ✅ |
| 9 | 99.67% inert vs 97.75% | 2 of 611; 14 of 623 | `notes/10` §7 | ✅ |
| 10 | "the first interval … spans the content line", "the second lies inside the collapse band" | 0.625–0.755 crosses 0.72; 0.044–0.150 ⊂ (0, 0.33] | bands per PLAN §3 | ✅ |
| 11 | length-only falls to 0.5851 | 0.5851 | §9.1 row 1 | ✅ |
| 12 | masking numerals and comparison operators leaves S unchanged | NUM 0.7525, CMP 0.7503 vs control 0.7512, intervals overlapping | §11.2 | ✅ |
| 13 | identifiers normalised → 0.700 (ρ = 0.54) | 0.6997 (0.6785–0.7205), ρ = 0.537 (0.480–0.592) | §11.2 | ✅ |
| 14 | `def main`/`data[` at 67% vs 38.5% | `def main` 0.669 attack / 0.385 honest (`data[` 0.377 / 0.136) | §11.3, §11.5 | ✅ for `def main` (NF6) |
| 15 | S = 0.6423 (0.6179–0.6621; n = 586) | 0.6423, 0.6179–0.6621, n = 586 | §13.2 row 3 | ✅ |
| 16 | ρ = 0.394 (0.326–0.454) | 0.394 fold-mean, joint 0.326–0.454 (pooled 0.390) | §13.2 | ✅ |
| 17 | the two honest classes separate at 0.6006 | 0.6006 (0.5768–0.6243) | §13.2 row 4 | ✅ |
| 18 | Haiku prompt-matched S = 0.5399 (ρ = 0.113) | 0.5399, ρ 0.113 (0.055–0.165), n = 562 | §15.5 | ✅ |
| 19 | Haiku prompt-only floor 0.4918, "an interval containing chance" | 0.4918 (0.4724–0.5126) ∋ 0.5 | §15.5 | ✅ |
| 20 | B at n = 623 is 0.8521 ± 0.0055 | 0.8521 ± 0.0055 (range 0.8392–0.8634) | §9.2 | ✅ |
| 21 | strict ρ = 0.921 (0.662–1.089 on the pooled-score 0.86) | fold-mean 0.921; joint interval on pooled 0.861 | §12.2 | ✅ (convention stated) |
| 22 | strict S = 0.7652 (0.7016–0.8000; n = 99), B′ = 0.7877 | identical | §9.1 row 2 | ✅ |
| 23 | B at n = 99 is 0.7807 ± 0.0248 | identical | §9.2 | ✅ |
| 24 | monitor 0.9579 on stored pairs over the same problems | 0.9579 (0.9466–0.9683), n = 623 | §14.2 | ✅ |
| 25 | monitor 0.566 (0.5507–0.5833) on the headline pairs | 0.5662 (0.5507–0.5833) | §14.3 | ✅ |
| 26 | monitor-ρ 0.145 (0.111–0.182) | identical | §14.3 | ✅ |
| 27 | strict 0.9437 and 0.818 (0.7630–0.8686) | 0.9437 (0.9086–0.9724); 0.8182 (0.7630–0.8686) | §14.2, §14.3 | ✅ |
| 28 | monitor-ρ 0.717 (0.601–0.832) | identical | §14.3 | ✅ |
| 29 | neither-class monitor "returns the same two ratios (0.151, 0.749)" | 0.151 (0.063–0.242) and 0.749 (0.514–0.993); the first rests on a row with 628/1,246 replies missing | §14.3, §14.5 | ⚠️ value ✅, caveat missing (**M6**) |
| 30 | φ = 0.04 | 0.04 (§12.3 table); 0.035 quoted in §12's coordinator note | §12.3 | ✅ |
| 31 | fire given a pass 2.5% vs stored 67.2% | 167/6,570 = 2.5%; 172/256 = 67.2% | §7.7 (994–995) | ✅ |

**Summary: 41 of 43 values are exact against the ledger.** The two failures are not wrong numbers —
they are a wrong *pairing* (M1) and a wrong *modality* (M5); one caveat is missing (M6) and one gloss
is generous (abstract #7).

---

## 5. What was changed in `paper/main.tex`

**Nothing.** The remit was unambiguous, line-count-neutral corrections only, and after checking every
number in the abstract, §3 and the appendix against the ledger and the jsons it names, there is no
wrong number, no typo and no duplicated word to correct (a duplicated-word scan over the whole PDF
text returns empty; "one of ten named models" looks wrong against `scan/FINDINGS.md` and is right
against `K1-artifact-lineage.md`). Every remaining defect found is either a wording change whose
correct form is a judgement call (M1, M2, M4, M5), an addition (M6, NF5), or a structural change that
costs body lines the paper does not have (M7). All of them are written out above with their exact
replacement text so they can be applied in one pass with the probe re-run afterwards.

`main.pdf` as committed is current with `main.tex` (pdf 19:35, tex 19:34), zero overfull boxes, body
on four pages, References on page 5.

### The probe, re-run

```
N = 0  →  body ends page 4, References page 5
N = 1  →  the probe line is on page 5      ← the body has no slack at all
```
plus `pdftotext -bbox-layout`: page 4's last body line is yMax = 722.15, the same bottom edge as the
last lines of pages 3 and 5. `paper/README.md` §3's "N = 3" is stale and should be corrected to
N = 0 (M8).

### Operational note

`experiments/apps/merge_draws.py` and `verify_backdoor.py` carry uncommitted edits from the
concurrent session `RESULTS.md` §15.8 and `notes/10` §9 describe. The supplementary zip was built
2026-09-11 19:27 from the working tree, so `release/scripts/verify_backdoor.py` may carry that
session's unused `--trigger-pool` diff. It is behaviourally identical on the default path, but if the
bundle is rebuilt before submission, rebuild it from a clean tree.
