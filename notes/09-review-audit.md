# Hostile review audit of `paper/main.tex`

Written 2026-09-11 by an adversarial-reviewer pass over `paper/main.tex` (compiled
`paper/main.pdf`, 8 pages), `README.md`, `notes/01`, `notes/04`, `notes/06` §0–§5,
`experiments/RESULTS.md` §6–§12, and the scripts behind the two load-bearing claims
(`experiments/apps/bow.py`, `data.py`, `trigger_public_check.py`) plus the release zip's
`MANIFEST.json`. No experiment was run; nothing outside this file was edited.

Stance: EvoRobust 2026, robustness / benchmark-validity track, 4 content pages, non-archival,
double-blind. A reviewer with a four-day window who reads the PDF, opens the supplementary
bundle, and checks three numbers.

Written on the assumption that three arms land within hours and go into the paper:
**A** prompt-matched honest class (S_matched, plus a prompt-only floor = original honest vs
matched honest), **B** a weaker trusted monitor (Haiku 4.5) on the same-generator pairs and
Sonnet 5 + Haiku monitors on the STORED pairs over the same problems (a monitor-ρ beside the
classifier's ρ = 0.687), **C** a second same-generator model (Haiku 4.5 writes both classes).

---

## 1. The OpenReview review

### Summary

The paper asks what an AI-control stored-pair benchmark still leaks after the field's own
preprocessing (filter to working solutions, strip comments). On Koran et al.'s filtered,
comment-stripped split — the split on which 24 open-weight monitors have published per-item
scores — a word bag-of-words classifier reaches AUROC 0.806, above 20 of those 24 monitors
(median 0.609), and a classifier that reads no code at all, only problem difficulty, test count
and question length, reaches 0.772, above 20 of 24. The paper traces the residue to *authorship*:
the honest class is human APPS code and every backdoor is model-written, the classifier transfers
across backdoor generators (0.969 pairwise, stripped) and is nearly as strong on inert backdoors
(0.879) as on working ones (0.935). Two controls follow. Regenerating only the honest half with an
open-weight model makes separation *worse* (ρ = 1.234) — a clean negative result about the method.
Generating both classes from one model (Sonnet 5, 623 problem-disjoint pairs) gives S = 0.751
against B′ = 0.8658, ρ = 0.687 (0.625–0.755): the pre-registered collapse band is excluded and the
content line is spanned. A zero-shot monitor from the same model scores 0.566 on those pairs and
0.818 on the 99 that actually fire; masking ablations say the residue is program layout, not the
trigger. The paper closes with a four-item preprocessing checklist and a released same-generator
split.

### Strengths

1. **The measurement discipline is better than the median workshop paper by a wide margin.**
   Every headline number carries a bootstrap CI over problems, a permutation null, and a *paired*
   bootstrap against each of the 24 monitors on identical items (20 above by point, 18 by paired
   CI — the paper reports both, which most papers would not). Three of Jha's published values are
   bit-matched by an independent reconstruction.
2. **The decisive control was actually run, and the pre-registered reading rule was honoured.**
   ρ bands were fixed before any arm ran; the arm returns *inconclusive between partial and
   content* and the paper says so in those words instead of rounding to a verdict. The learning
   curve (B at n = 623 is 0.8521 ± 0.0055) forecloses the obvious "it's just sample size" reply
   before the reviewer can make it.
3. **The negative results are reported as results.** Arm 1 (ρ = 1.234) is published as a null
   about the method; the AICD token test fails to replicate and is reported with the wrong sign
   and its power caveat; the unstripped numbers are labelled as inflated by the comment channel —
   the paper's thesis applied to itself.
4. **The built-in negative control is elegant and cheap.** Five agentic settings where the same
   three models write both classes give a structural floor (bash 0.504 = on its null, agentdojo
   0.802 from character count) with no authorship confound possible.
5. **The recommendations are actionable and precedented** (CodeMirage's line/character gating,
   MultiAIGCD's shared problem definitions), not invented for the paper.

### Weaknesses

1. **One load-bearing sentence is false under the authors' own pipeline.** §3 claims "most of the
   ``honest'' class consists of failed attacks". `experiments/apps/bow.py` builds the negative
   class as `_honest_code(row)` — the first human APPS solution that compiles and passes — when
   `backdoor_works` is false. The failed attack's *code* is never in the split. The real artifact
   (the negative class is selected at the *problem* level by attack failure, which is why problem
   metadata predicts the label at 0.772) is defensible and more interesting; the sentence as
   written is checkable and wrong, and it is the one contribution a reviewer can falsify in five
   minutes with the cited released code.
2. **The abstract claims more than the body supports, and the body says so.** The abstract:
   "attributes the remainder to surface content of the attack class". §3, four sentences later:
   "the top attack-side features are `def main` and `data[` … the layout the attack prompt
   elicits. The arm holds the model constant, not the prompt, so ρ is an upper bound on content."
   Those are not the same claim. The paragraph heading "The signal is authorship, not sabotage."
   sits above a measurement that assigns authorship ~31% of the separability.
3. **The headline same-generator attack class is ~98% non-functional backdoors.** Under the
   outcome-blind `first` rule, 14 of 623 selected attacks fire (RESULTS §7.4). So the row the
   abstract's "about a third" comes from is a class of *attempts*, and the paper's own
   Recommendation 3 says to drop exactly this population. The row that complies with the
   recommendation is the strict row, n = 99, ρ = 0.921 (0.662–1.089) — i.e. holding authorship
   constant removes essentially nothing. The paper reports both honestly but never states the
   share, and the abstract routes on the non-compliant row.
4. **Two intervals are attached to point estimates they are not intervals of.** The no-code floor
   is quoted as "0.772 (CI 0.7319–0.8005)" — RESULTS §8.3 states that CI is on the pooled
   out-of-fold AUROC 0.7658, never printed in the paper. The strict ρ is quoted as "0.921
   (0.662–1.089)" where the interval is built on a pooled ρ of 0.861 (RESULTS §12.2, which itself
   says "the ledger should say which convention it quotes").
5. **The paper exceeds the page limit.** Four lines of §5 sit on page 5 above References.
6. **The generator is not the stored attacker** (Sonnet 5, thinking off, vs
   `claude-3-7-sonnet-thinking`), and the single-shot/stored funnel comparison carries an
   unearned causal clause ("which executes and iterates") that the authors' own repo now
   contradicts (52% of their triggers are public test inputs and cannot fire by construction).
7. **"Release the split and the scripts. Ours accompany this paper"** — the bundle contains twelve
   files and no scripts.

### Questions to the authors

1. In `bow.py`, the label-0 item is `_honest_code(row)`, a human solution, not the inert backdoor.
   In what sense is an inert backdoor "relabelled honest"? Please state the negative class's
   actual construction and re-derive the claim.
2. What fraction of the 623 headline attack draws fire on their trigger? Please put the number in
   the paper beside "the attack class defined, as in the benchmark, by intent plus passing the
   public tests".
3. Recommendation 3 says to drop inert backdoors from both classes. Your headline row does not.
   Under the row that follows your own recommendation (n = 99) ρ = 0.921. Why is the headline the
   other one, and what does the abstract's "about a third" become under the strict row?
4. Is the "CI 0.7319–0.8005" the interval of 0.772 or of the pooled out-of-fold 0.7658? Same
   question for ρ = 0.921 against an interval centred near 0.86.
5. Your ablations say the residue is layout the attack prompt elicits. What does S become when the
   honest class is generated under the same prompt framing, minus the flaw sentence?
6. Would a *different* monitor — one that wrote neither class, and a weaker one — reproduce 0.566
   on the headline pairs and 0.818 on the firing ones?
7. What are the scripts referred to in Recommendation 4, and where are they in the bundle?

### Score

**5 / 10 (marginally below threshold), confidence 4.**
The measurement is stronger than the writing. Weaknesses 1, 2 and 5 are all fixable in an hour and
are the difference between 5 and 7 for me; weakness 3 is the one that needs a sentence of honest
accounting rather than new data. I would not fight an accept, and I would argue hard against
accepting it with the abstract as written.

### The single sentence that would most raise the score

> "Regenerating the honest class under the attack prompt's framing — identical prompt, minus the
> flaw sentence — takes S from 0.751 to S_matched (CI; n), ρ_matched (joint CI), so the residue
> that survives with authorship held constant is [mostly / only partly] the prompt's framing and
> not content of the attack code."

That is arm A. It converts the paper's weakest construct ("ρ is an upper bound on content") into a
measurement, and it is the only sentence that can make the abstract's third clause true or retire
it.

---

## 2. The twelve most damaging objections, ranked

"Existing?" = does the evidence already in the repo answer it. "A/B/C?" = does an incoming arm
answer it. Quotes are exact from `paper/main.tex`.

| # | Objection | Where it bites (quoted) | Existing? | A/B/C? | Cheapest fix in text |
|---|---|---|---|---|---|
| 1 | **The negative class is not failed attacks.** `bow.py` takes `_honest_code(row)` — a human APPS solution — whenever `backdoor_works` is false. The inert backdoor's code never enters the split. The stated artifact is therefore mis-described, and it is checkable from the released code the paper cites. | "\inertShare{} of the test split's labelled backdoors do not work (\inertSharePassing{} of those that pass the public tests) and are relabelled honest, so most of the ``honest'' class consists of failed attacks." | **No** — the repo contradicts it | No | Replace the clause after the semicolon with: "so the negative class is defined by *attack failure at the problem level*: a problem whose backdoor fails contributes its honest solution instead, and the label is fixed before any code is read." Everything downstream (test-count gap, no-code floor) survives unchanged and reads better. |
| 2 | **Abstract and §1 claim content; §3 says prompt framing and calls ρ an upper bound.** A reviewer who reads the abstract and then the paragraph finds the paper arguing against itself within a page. | Abstract: "the same-generator control excludes authorship as the whole story and attributes the remainder to surface content of the attack class." §3: "the layout the attack prompt elicits. The arm holds the model constant, not the prompt, so $\rho$ is an upper bound on content." | Partly — §11 is in the paper but only as the mechanism sentence | **A decides it** (both branches) | Until A lands: change the abstract to "…and leaves a residue that is surface *form* of the attack class — partly the program layout its prompt elicits." Same for §1 contribution (ii). One word per site. |
| 3 | **The headline "attack class" is ~98% non-backdoors, and the paper's own Recommendation 3 forbids it.** 14 of 623 `first`-selected attacks fire (RESULTS §7.4). The compliant row (n = 99) returns ρ = 0.921 — authorship removes almost nothing. The abstract routes on the non-compliant row. | "the attack class defined, as in the benchmark, by intent plus passing the public tests" ‖ Rec. 3: "Drop inert backdoors from both classes rather than relabelling a failed attack as honest." | Partly — strict row is reported; the share is not, and the tension is never named | Partly: **C** replicates both rows on a second model; **B** shows what a monitor sees on each | Add ten words to the headline sentence: "(2.2\% of these draws fire, the same-generator analogue of the split's own \inertShare{} inert class)", and one clause to the strict sentence: "the row that follows our own Recommendation 3". Naming the tension costs a line and removes the objection's sting. |
| 4 | **Intervals attached to the wrong point estimate**, twice, in the two most-read numbers. | "a no-code floor of \nocodeCV{} (CI \nocodeCVLo{}--\nocodeCVHi{}; null \nocodeCVNull{}, $\permP$)" ‖ "$\rho = \strictRho{}$ (\strictRhoLo{}--\strictRhoHi{})" | **No** — RESULTS §8.3 and §12.2 both flag it; the paper does not | No | Six words each: "(interval on the pooled out-of-fold AUROC, 0.766)" and "(interval on the pooled-score $\rho$, 0.86)". Alternatively quote the pooled point in both places. |
| 5 | **Page-limit violation.** Content runs to page 5: §5's third paragraph ("Scope, provenance and the harness.", 4 lines) sits above References. The venue is 4 content pages (`notes/01`: "4 content pages (5 camera-ready), unlimited references and supplementary"). Appendix-after-references is fine at this venue; the four lines are not. | `pdfinfo`: 8 pp; page 5 begins with "Scope, provenance and the harness." | No | No | Cut five body lines. Cheapest five are listed in §4 below. This is a mechanical desk-reject risk and the cheapest point on the list. |
| 6 | **"The signal is authorship, not sabotage." over a measurement giving authorship ~31%.** The section heading was written for the pre-Gate-S paper. | \paragraph{The signal is authorship, not sabotage.} | Partly — the Gate S paragraph corrects it two paragraphs later | **A** (if S_matched collapses, the heading becomes defensible again as "authorship and framing") | Retitle to "**The signal is not sabotage.**" — true under every branch (inert ≈ working, transfer, monitor 0.566), costs zero lines, and stops the paper contradicting its own §3. |
| 7 | **Zero-shot monitors vs a trained classifier**, and the caveat lives only in a figure caption while the abstract and §1 state the comparison bare. | Abstract: "a bag-of-words classifier scores above roughly four-fifths of the open-weight monitors ranked on it". Caption: "(i)~The \monN{} monitors are zero-shot prompted while the bag-of-words classifier is \emph{trained}…" | Yes, but in the wrong place | **B** partly: a monitor that wrote neither class, plus a weak one, on the same pairs, is the like-for-like a reviewer wants | Insert one word in the abstract: "a *trained* bag-of-words classifier". The caption already carries the Gururangan framing; the abstract must not be quotable without it. |
| 8 | **The funnel sentence's causal clause is contradicted by the authors' own repo.** `trigger_public_check.py` (committed 2026-09-11): 52.0% of their triggers are public test inputs and fire 0.15%; stored working backdoors with a public-input trigger, 0 of 3,188. Half the 2.5%-vs-67.2% gap is a prompt defect, not the stored attacker's iteration. | "Our single-shot attacks fire given a pass at \fireGivenPassOurs{} against the stored attacker's \fireGivenPassStored{}, which executes and iterates: the stored attack class is a survivor set." | **No** — the check exists but post-dates the paragraph | No | Drop "which executes and iterates" and end at "the stored attack class is a survivor set." If a line is available, the honest version is stronger: "half of that gap is our own attack prompt reusing public inputs as triggers; the rest is retry-and-keep." |
| 9 | **The same-generator model is not the stored attacker** (Sonnet 5, thinking off, vs `claude-3-7-sonnet-thinking`), so B′ compares generations as well as prompts, and ρ mixes them. | "The stored attacker, \texttt{claude-3-7-sonnet-thinking}, is retired (404 against a live key), so both same-generator classes come from a later model of the same lineage… and thinking was off although the stored attacker was a thinking model." | Disclosed, not measured | **C decides it**: if Haiku 4.5's ρ lands inside 0.625–0.755, model identity is not carrying the result | Add six words to the Gate S paragraph once C lands: "a second generator (Haiku 4.5) gives $\rho = \haikuRho{}$". Until then the disclosure is adequate but a reviewer will still dock for it. |
| 10 | **One stored-pair family.** The headline is one HuggingFace artifact and one derived view of it; five of the seven corpora are one user's repackaging. The title asks a general question the evidence answers for one benchmark. | "We use seven public corpora" ‖ "Whether stored-pair corpora leak this way in general is not established here. Five of our seven corpora are one user's repackaging" | Yes, but only in Limitations on page 5 | No | Move the scope sentence up into §1's **Scope** clause, where the claim is made: "…on *stored* pairs; our measurement is of one APPS-derived family plus five agentic settings." Costs nothing, buys the reviewer's trust before the claims land. |
| 11 | **The strict row is underpowered and the paper leans on it for agreement.** n = 99, ρ CI 0.662–1.089 spans partial, content and ρ > 1; fold seeds move strict ρ from 0.92 to 0.85 (RESULTS §12.4) and the published deterministic split sits at the top of that range. | "The strict row … agrees: $\rho = \strictRho{}$ (\strictRhoLo{}--\strictRhoHi{})" | Partly — the learning-curve caveat is there, the seed spread is not | **C** (a second model's strict set roughly doubles the firing pairs if pooled) | One word: "agrees, at low power:". And if room: "(five fold seeds move it 0.85–0.92)". |
| 12 | **"Release the split and the scripts. Ours accompany this paper" — the bundle has no scripts.** Twelve files: four JSONL, four CSV, README, MANIFEST, LICENSE. Also, the zip stores the licence as `../../LICENSE`, which extracts outside `release/`. | "\textbf{State the split, the metric and the preprocessing} … and \textbf{release the split and the scripts}. Ours accompany this paper as supplementary material under MIT" | **No** | No | Either add the scripts to the bundle (preferred, and it is the paper's own recommendation) or change "Ours" to "The split accompanies this paper as supplementary material; the scripts are released with the camera-ready." Fix the `../../LICENSE` entry either way. |

### Assessed and ranked below the cut

- **"About a third" in the abstract.** Defensible: ρ = 0.687 → 31.3% removed; the joint CI gives
  24.5–37.5%. Keep the phrase; it is the *attribution* clause after it that overclaims (#2).
- **Do the recommendations follow from the results?** 1, 2 and 4 follow directly. **3 does not
  follow from the paper's own headline** — the headline attack class violates it (#3), and after
  fix #1 the recommendation's wording ("rather than relabelling a failed attack as honest")
  describes something the pipeline does not do. Reword to "Do not define the negative class by
  attack outcome: drop the problems whose attacks failed, or sample the negative class
  independently of attack success."
- **Double-blind leaks: clean.** No URL, repo name, dollar figure, self-citation, acknowledgements,
  or "our earlier work" in `main.tex`; the author block is the style file's anonymous block; the
  only GitHub URL is in a third-party bib entry (`anik-jha/challenger-panels`), which is a
  citation, not a leak. PDF metadata carries no author. `\workshoptitle` only renders under
  `[final]`. One soft spot, not a leak: "Among the agentic corpora we exclude AgentHarm, whose
  author is an invited speaker at this venue." — it is venue-specific rather than
  author-identifying, it is the right call per `notes/01` G2, and I would keep it; if the paper is
  also submitted elsewhere the phrase must change.
- **Invited-speaker citation conflict: clean and correct.** Andriushchenko's `2510.09462` is cited
  and distinguished in §1 ("subverts monitors with injected text"), AgentHarm is excluded and the
  exclusion is stated. No other organiser or speaker from `notes/01`'s roster appears in
  `refs.bib`; the 24-monitor scores are Jha's (MIT), unaffiliated with the committee.
- **Page limit / appendix.** `notes/01` off the CFP: "4 content pages (5 camera-ready), unlimited
  references and supplementary". So the appendix after References is allowed at any length; the
  violation is only the four body lines on page 5 (#5). Content pages before References as
  compiled: **4 pages plus 4 lines**.
- **The no-code floor fitted within the test split.** Disclosed in the caption with the held-out
  fallback and its p = 0.030. A reviewer will note the held-out CI (0.6476–0.7796) contains its
  own null's 95th percentile (0.7023) — the paper says the claim rests on the CV protocol, which
  is the right call. Adequate as written; add "(0.716 on a single held-out slice)" to the
  abstract's "most of them" if a reviewer presses.
- **"Relabelling inert backdoors as honest is Koran's rule, not ours."** Correct as a defence of
  the *criticism* — the label column is shipped and the field selects on it — and the paper frames
  it that way. It does not survive objection #1, which is about what the negative class contains,
  not whose rule it is.
- **The unreconciled 0.6836** (stripped TF-IDF fitted *within* the test split, 0.12 below the
  0.8063 headline on the same corpus) is still absent from the paper although `notes/06` §3.4 asks
  for one appendix sentence. A reviewer who runs `bow.py` finds it. One sentence in
  appendix~\ref{app:stripped}.
- **Macro discipline is broken in the generated float.** `fig/f1-protocol-baseline.tex` hardcodes
  0.8063 / 0.8914 / 0.7715 ± 0.0389 / 0.7163 / 0.969 / 0.962 / 0.979 / 0.955 / 0.994 rather than
  using the macros the header calls mandatory. It happens to agree today.

---

## 3. Internal inconsistencies

Checked `main.tex`'s macro blocks line by line against `RESULTS.md` §9–§12 (and §6–§8 where a
macro's comment names them), then `README.md` and `notes/04` against both. Twenty-two found.
"Paper-facing" means a reviewer could see it in the PDF.

**Paper-facing**

1. **`\splitTrain{}` is a problem count used as an item count.** §2: "\splitTrain{} train and
   \splitTest{} test items (\splitAttack{} attack, \splitHonest{} honest)". RESULTS §8.1: the
   training set is "2,418 samples over 1,209 problems (1,209 attack / 1,209 honest)", and the F3
   caption calls it "the benchmark's own *paired* train split". The appendix then uses 1,209
   per class — "in \bylineHonest{} of \splitTrain{} honest samples" and "152 versus 1 of
   \splitTrain{}" — which is only coherent if 1,209 is per class. §2 says 1,375 *test* items,
   which is right, and 1,209 *train* items, which is half the truth. Fix: "1,209 train problems
   (2,418 paired items)".
2. **The no-code CI is the CI of a number the paper never prints.** `\nocodeCVLo/Hi`
   (0.7319–0.8005) belong to the pooled out-of-fold AUROC 0.7658 (RESULTS §8.3); the prose puts
   them on 0.772. The macro comment knows ("% CI on the pooled out-of-fold AUROC"); the prose does
   not. Macro comment vs prose.
3. **The strict ρ point and its interval use different conventions.** `\strictRho` 0.921 is the
   fold-mean; `\strictRhoLo/Hi` 0.662–1.089 is the joint bootstrap on the pooled ρ = 0.861
   (RESULTS §12.2, which explicitly asks the ledger to say which convention it quotes). The paper
   says neither.
4. **"most of the ``honest'' class consists of failed attacks"** contradicts `bow.py`'s
   reconstruction (label 0 = `_honest_code(row)`), and also contradicts §1's own description of
   the filter: "Koran et al.\ keep only working honest solutions and working backdoors".
5. **`\monitorS`'s macro comment quotes a cross-protocol share.** "% Headline set: 97.5% of its
   attacks never fire." 97.5% is the *pooled per-draw* rate (2.5% of 6,570, RESULTS §7.3). The
   headline set's realised rate is 14 of 623 = 2.2% firing, 97.8% not (RESULTS §7.4). RESULTS §10's
   own table header repeats the 97.5%. This is exactly the R18 failure the macro block warns
   against, committed inside the macro block's comments.
6. **`\defMainHonest` 39% vs RESULTS §11.3/§11.5's 0.385 / "38.5%".** Rounds up; harmless but the
   paper's own convention elsewhere is to quote the measured value.
7. **Similarity table's "stored benchmark" row is not the edit row's comparison set.** The table's
   stored row (0.606 / 3.4% / 45.4%, labelled "--- (the regime to match)") is measured on the 623
   headline problems (`sg_indep_first_passes.json`); the edit row's own stored comparison over its
   427 problems is 0.603 / 4.2% / 45.4% (`sg_edit_passes.json`). Same table, two populations, one
   label.
8. **The funnel's causal clause vs `trigger_public_check.py`** (commit 40089f2, same day): "which
   executes and iterates" is at most half the mechanism; 52.0% of our triggers are public test
   inputs and cannot fire, and 0 of 3,188 stored working backdoors have such a trigger.
9. **Recommendation 4's "and the scripts"** vs the release bundle's twelve data/metadata files
   (`MANIFEST.json` inspected: no `.py`). The counts in the release sentence are all correct
   (1,444 / 1,112 / 1,112 / 11,565 / 623 / 14 / 1,046 / 99 / 106 all match `MANIFEST.json`); only
   "the scripts" is unbacked.
10. **Page count vs the venue rule and vs the README's status box** ("Paper: four content pages
    exactly", and the table row "Prose | 4 pages"): the compiled PDF puts four lines of §5 on
    page 5.
11. **Abstract/§1 "surface content of the attack class" vs §3 "the layout the attack prompt
    elicits" / "$\rho$ is an upper bound on content"** — RESULTS §11's coordinator correction is in
    the body but not in the abstract or the contributions list.
12. **`\paragraph{The signal is authorship, not sabotage.}` vs ρ = 0.687**, which assigns
    authorship about a third and the rest to something else.

**Repo-facing (README / notes vs the ledger and the paper)**

13. **README quotes the superseded S-only ρ intervals in two places** — "ρ = 0.687 (0.627–0.742)"
    and "ρ = 0.921 (0.700–1.043)" (status box and the Gate S table row) — where `main.tex` and
    RESULTS §12.2 now carry the joint bootstrap, 0.625–0.755 and 0.662–1.089.
14. **README's one-paragraph claim uses the *unstripped* pairwise numbers**: "as strong on
    **inert** backdoors (0.954 pairwise) as on working ones (0.979)". The paper reports the
    stripped 0.879 / 0.935 and moves the unstripped values to an appendix labelled "inflated by
    the comment channel". The README is the version of the claim the ledger retired.
15. **…and 0.954 is not the unstripped value either.** RESULTS §6.1/§6.2 and `\pairInertKept` both
    give 0.955.
16. **`notes/04` §"framings that are alive" item 3 is stale in three numbers**: transfer 0.9935,
    inert 0.954, working 0.979 (all unstripped), plus "`#` present: attack 0.685 vs honest 0.176",
    a marker the paper now explicitly drops after stripping (0.007 vs 0.008). `notes/04` is the
    file whose job is to stop dead sentences being revived.
17. **`notes/06` §0 item 2** — "\"Authorship, Not Sabotage\" is not supported by what has landed,
    and should not be the title" — is now contradicted by the §3 paragraph heading that says
    exactly that (#12), and by the outcome banner added at the top of §4.
18. **Three different API ceilings across the repo**: `notes/06` §6 "$86 remains of the $100
    ceiling", RESULTS §10 "about $101.6 against the $110 ceiling", commit 0c2005e "ceiling to 135".
    README says only "Spend stayed inside the project ceiling", which is true under exactly one of
    them at a time. Not paper-facing (no dollar figure is in `main.tex`, correctly), but the
    disclosure owed by `notes/05` is graded against a moving number.
19. **`\nIndep{}` = 600 sits beside `\simIndep`'s comment "independent arm, n=623".** 600 is the
    pre-retry request count; the arm the paper reports is 623 problems out of a 1,112-problem,
    11,565-draw pool. `\nIndep`, `\usableIndep` (10), `\usableEdit` (40), `\nEdit` (1,112),
    `\pairFloor` (50) and `\yieldSingleShot` (2\%) are all from the did-not-land draft and are now
    unused; leaving them defined invites a future paste of a superseded number.
20. **Macros defined and never used** (25 of them), including `\nocodeCVsd` — whose value 0.039 is
    nevertheless printed in the F3 figure, hardcoded in `figures.py` rather than read from the
    macro. Also `\gCollapseMax` / `\gPartialMax` (the corrected routing thresholds the README calls
    out as important), `\charNgram`, `\monMin`, `\sameGenPairwise`, `\monitorSPairwise`,
    `\monitorStrictPairwise`, `\editN`, `\survivorLine`, `\retryProblems`, `\retryMaxDraws`,
    `\armOneSd`, `\artifactRows`, `\genPool`, `\analysisCeiling`, `\lenRaw`, `\TBD`.
21. **`notes/06` §3.4's open items still open in the paper**: the unreconciled 0.6836 appendix
    sentence was never added.
22. **The release zip's licence entry is `../../LICENSE`**, outside `release/`, while the appendix
    describes the bundle as carrying "a manifest of row counts and checksums, under the MIT
    licence". `release_split.py --check` passed, so the check does not cover archive layout.

Not inconsistencies, verified clean: every `\sameGen*`, `\strict*`, `\edit*`, `\monitor*`,
`\survivor*`, `\curve*`, `\sim*`, `\rel*`, `\armOne*`, `\baselineB*`, `\inertShare*`,
`\fireGivenPass*`, `\tfidf*`, `\nocode*`, `\mon*`, `\pair*`, `\transfer*`, `\surfaceSeven*`,
`\hashPres*`, `\byline*`, `\triple*`, `\token*` value against RESULTS §6–§12 and against
`sg_indep_first_passes.json` / `sg_edit_passes.json` / `MANIFEST.json` (the similarity shares
3.4% / 45.4% / 34.8% / 64.2% / 4.0%, absent from RESULTS.md prose, are exact in the jsons).

---

## 4. Absorbing A, B and C in four pages

Budget reality: the body is already **4 pages + 4 lines**. So the plan must free **at least 5
lines before adding anything**, then pay for each new sentence. Three new body sentences ≈ 8–9
lines. Total to free: **13–14 lines**. All of it comes out of §3, which is over budget, and none
of it loses a number — every cut sentence has an appendix home that already exists.

### Cuts (quoted exactly; all from §3 unless marked)

| # | Cut this sentence | Lines | Where it goes |
|---|---|---|---|
| C1 | "Intervals are bootstraps over problems, resampling $S$ and $B'$ jointly for $\rho$; this replaced a $\pm2$ fold-sd rule before the retry pool was read." | 3 | Appendix; leave "(joint bootstrap over problems)" as a parenthetical after the first $\rho$. This is `notes/09-arm3-paper-slot.md` §4's own recommendation. |
| C2 | "Retention is not the artifact: survivors and non-survivors separate at only \survivorAuroc{}, and $S$ with non-firing attempts on the same problems is \survivorSwapS{} against \survivorSwapSref{}." | 3 | Appendix. It defends the **strict** row only, which after C3's edit is explicitly the low-power row; a pointer costs four words. |
| C3 | "The edit arm bounds $S$ under near-copies (similarity \editSim{}): \editS{}, $\rho = \editRho{}$." | 2 | Appendix, beside Table~\ref{tab:similarity}, which already carries the similarity story. |
| C4 | "A fourth, token-level test \cite{orel2026aicd} does not replicate here (separation \tokenSep{}, permutation $p = \tokenP{}$; appendix~\ref{app:token}), a register effect; and one authorship leak, author bylines inside string literals, survives the field's own comment stripper (appendix~\ref{app:stripped})." → "A token-level test \cite{orel2026aicd} does not replicate, and one authorship leak survives the stripper (appendices~\ref{app:token},~\ref{app:stripped})." | 3 | Both appendices already hold the numbers verbatim. |
| C5 | (§2) "Five populations (the raw artifact, this split, pooled, matched pairs, within-task) and two metrics appear below; every comparison names its split, metric and preprocessing." → "Every comparison below names its split, metric and preprocessing." | 2 | The enumeration is in Table~\ref{tab:protocol-baseline}'s protocol column. |
| C6 | (§3, if still short) "\texttt{bash} sits on its permutation null at \bashFloor{} while \texttt{agentdojo} reaches \agentdojoFloor{} from character count alone." → "…floors run from \bashFloor{} (on its null) to \agentdojoFloor{} from character count alone." | 1 | — |

C1–C5 free **13 lines**; C6 is the reserve. That pays the 4-line overflow *and* three new
sentences, with ~1 line of slack.

### Macros to add

```latex
% --- Arm A: prompt-matched honest class (RESULTS §13) --------------------------------
\newcommand{\pmS}{0.xxx}\newcommand{\pmLo}{0.xxx}\newcommand{\pmHi}{0.xxx}
\newcommand{\pmN}{nnn}\newcommand{\pmBprime}{0.xxx}
\newcommand{\pmRho}{0.xx}\newcommand{\pmRhoLo}{0.xx}\newcommand{\pmRhoHi}{0.xx}  % joint
\newcommand{\promptFloor}{0.xxx}      % original honest vs prompt-matched honest: the prompt-only floor
\newcommand{\promptFloorLo}{0.xxx}\newcommand{\promptFloorHi}{0.xxx}
% --- Arm B: monitors that wrote neither class, and the stored pairs -------------------
\newcommand{\monHaiku}{0.xxx}         % Haiku 4.5 monitor, same-generator headline pairs
\newcommand{\monStoredSonnet}{0.xxx}  % Sonnet 5 monitor on the STORED pairs, same problems
\newcommand{\monStoredHaiku}{0.xxx}   % Haiku 4.5 monitor on the STORED pairs, same problems
\newcommand{\monRho}{0.xx}            % (monitor S - .5)/(monitor B' - .5): rho read by a monitor
\newcommand{\monRhoLo}{0.xx}\newcommand{\monRhoHi}{0.xx}
% --- Arm C: a second same-generator model --------------------------------------------
\newcommand{\haikuS}{0.xxx}\newcommand{\haikuLo}{0.xxx}\newcommand{\haikuHi}{0.xxx}
\newcommand{\haikuN}{nnn}\newcommand{\haikuBprime}{0.xxx}
\newcommand{\haikuRho}{0.xx}\newcommand{\haikuRhoLo}{0.xx}\newcommand{\haikuRhoHi}{0.xx}
```

Keep the existing rule: one macro, one protocol, its count in its comment. Delete
`\nIndep`, `\usableIndep`, `\usableEdit`, `\nEdit`, `\pairFloor`, `\yieldSingleShot`, `\TBD` in the
same pass (inconsistency 19) so no superseded yield number can be pasted beside the new ones.

### The three new sentences

**B — replaces nothing; appended to the existing monitor sentence.** The monitor sentence already
ends "…read different things --- the layout, and the backdoor." Extend with:

> "The split is not an artefact of the monitor sharing the generator's identity: a monitor that
> wrote neither class scores \monHaiku{} on the same pairs, and both monitors read the *stored*
> pairs over the same problems at \monStoredSonnet{} and \monStoredHaiku{}, so a monitor's own
> $\rho$ is \monRho{} (\monRhoLo{}--\monRhoHi{}) against the classifier's \sameGenRho{}."

This is the single highest-value addition after A: it answers objection #7 (zero-shot vs trained)
*and* gives the paper a ρ in the monitors' own metric, which is the quantity the workshop's
audience actually cares about.

**C — one clause inside the existing headline sentence**, not a new sentence, if lines are tight:

> "…so $\rho = \sameGenRho{}$ (\sameGenRhoLo{}--\sameGenRhoHi{}); a second generator writing both
> classes (\haikuN{} pairs) gives $\rho = \haikuRho{}$ (\haikuRhoLo{}--\haikuRhoHi{})."

If C *disagrees* with the Sonnet arm, it must become its own sentence and the abstract must say
"one to two thirds" or name the range; do not average two generators into one ρ.

**A — replaces one sentence.** Per `notes/09-arm3-paper-slot.md` §1, arm A is the answer to
exactly this sentence, so it is paid for in place:

> **Cut:** "The arm holds the model constant, not the prompt, so $\rho$ is an upper bound on
> content."

#### Branch 1 — S_matched collapses (the residue was framing)

Paste in its place:

> "Holding the prompt constant as well removes most of the rest: with the honest class regenerated
> under the attack prompt's framing minus the flaw sentence, $S = \pmS{}$ (\pmLo{}--\pmHi{};
> $n = \pmN{}$), $\rho = \pmRho{}$ (\pmRhoLo{}--\pmRhoHi{}), and the two honest classes separate
> from each other at \promptFloor{}."

Then, **at zero net lines**, three edits elsewhere:

- Abstract: "…and leaves the rest: the same-generator control excludes authorship as the whole
  story and attributes the remainder to surface content of the attack class." → "…and leaves a
  residue that is the attack *prompt's* framing, not content of the backdoor: matching the honest
  prompt removes most of it."
- §1 contribution (ii): "attributing roughly a third of the separability to authorship and the
  rest to surface content of the attack class" → "attributing the separability to authorship and
  to the attack prompt's framing, and not to the backdoor".
- §3 heading (#6 above) → "**The signal is not sabotage.**" The paper now has a positive
  mechanism: authorship + framing, with the monitor at 0.566 as the independent witness. This is
  the stronger paper, and the title "What Survives the Filter?" still fits.
- Recommendation 1 gains four words at no line cost: "Generate both classes with the same model
  **and the same prompt**" — which makes the checklist follow from the result, answering the
  "do the recommendations follow?" objection in the same stroke.

#### Branch 2 — S_matched holds (the residue is content)

Paste in its place:

> "It is not the prompt either: with the honest class regenerated under the attack prompt's
> framing, $S = \pmS{}$ (\pmLo{}--\pmHi{}; $n = \pmN{}$), $\rho = \pmRho{}$
> (\pmRhoLo{}--\pmRhoHi{}), and the two honest classes are separable from each other at only
> \promptFloor{}."

Then:

- Keep the abstract's "surface content of the attack class" — it becomes *earned*, and this is the
  only branch in which the current abstract is true. Add three words: "…to surface content of the
  attack class, which survives matching the prompt."
- The §11 mechanism sentence must soften, per `notes/09-arm3-paper-slot.md` §3: "the layout the
  attack prompt elicits" → "a layout that travels with the attack instruction".
- The "upper bound" clause is *dropped rather than replaced* — that is the branch that saves a
  line, so C's clause fits without touching C6.
- §3 heading → "**The signal is not sabotage.**" still, because ρ ≤ 1 and the monitor reads 0.566:
  content in the classifier's sense is not sabotage in the monitor's, which is the distinction the
  title asks about and the one the workshop's audience will take away.

#### In both branches

- Apply fixes #1, #4 and #8 from the table (one clause each, ~2 lines total) out of the C6 reserve
  or out of C2's saved lines. #1 is not optional: it is the only *false* sentence in the paper.
- The strict row keeps its "at low power" and, after fix #3, a ten-word acknowledgement that it is
  the row that obeys Recommendation 3. If arm C's firing pairs are pooled with the Sonnet arm's
  99, say the pooled n; do not report two underpowered strict rows separately.
