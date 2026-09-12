# paper/ — the submission

Built and verified 2026-09-11 after **pass 3** — the cold review
([`notes/12-final-review.md`](../notes/12-final-review.md)), whose M1–M10 are applied — on top of
the second pass (`notes/11-pass2-brief.md`) and the reviewer audit
([`notes/09-review-audit.md`](../notes/09-review-audit.md)).
`main.tex` compiles clean: **exit 0, no undefined citations, zero overfull boxes, four content
pages** — the body fills page 4 with **2 free body lines by the probe below**,
References begins on page 5, and the appendix follows the references. Nothing of the body reaches
page 5.

```bash
cd paper && pdflatex -interaction=nonstopmode main && bibtex main \
  && pdflatex -interaction=nonstopmode main && pdflatex -interaction=nonstopmode main
```

`latexmk` is **not** installed on the local machine; the four-pass line above is the build.
MiKTeX 25.12 and TeX Live both work; nothing exotic is used. Count content pages from the
PDF, not from the source: `pdftotext -layout main.pdf - | awk '/\f/{p++} {print p": "$0}' |
grep -n References` must report a page index of 3 or more, with no body text after it.

## What is here

| File | What |
|---|---|
| `main.tex` | The paper. §1–§5 plus **two body floats, F3 and Table~1 (the Gate S rows)**; schema table, F1, similarity table, F2, the token test, the harness note, the comment-stripping companion values and the scratchpad channel are in the appendix after the references. `\TODO` is the no-op form (2026-09-11) — see "Before submitting". |
| `refs.bib` | 28 entries, built **only** from `lit/01-verified-bibliography.md`. |
| `neurips_2026.sty` | Official style file, from `media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip` (fetched 2026-09-09, HTTP 200). Unmodified. |
| `checklist-reference.tex` | The template's checklist, kept for reference. **Not** `\input` by `main.tex` — workshops do not require it. |
| `fig/` | F1 (`\input` as a table), F2 and F3 (PDFs). Regenerate with `experiments/apps/figures.py`; do not hand-edit. |
| `OUTLINE.md`, `ABSTRACT-*.md` | The planning documents `main.tex` was built from. |

## Four things that will bite if nobody says them

**1. The track option is `dblblindworkshop`, not the default.**
`\usepackage[dblblindworkshop]{neurips_2026}`. The template's default is the *main track*.
The workshop options additionally require `\workshoptitle{}`, which is set to EvoRobust's
full name. On acceptance, change to `[dblblindworkshop, final]`.

Two things about this option are **not** bugs, checked against `neurips_2026.sty`, because
both look wrong at first glance:

- The page-1 footer reads *"Submitted to 40th Conference on Neural Information Processing
  Systems (NeurIPS 2026). Do not distribute."* — with no workshop name. That is correct.
  The style file only uses `\@trackname` (which carries "Workshop: …") under `[final]`;
  at submission the notice is a fixed string. The workshop name appears on acceptance.
- The author block prints "Anonymous Author(s) / Affiliation / Address / email". That is
  emitted by the style file itself (sty line 336) under `\if@anonymous`, not by our
  `\author{}`. `dblblindworkshop` deliberately does *not* set `\@anonymousfalse` — unlike
  `sglblindworkshop`, which does. Double-blind is working.

**2. Citations are numeric, by choice.** `\PassOptionsToPackage{numbers,compress}{natbib}`
before the style file. Numeric is NeurIPS house style, it is far tighter than author-year
at 4 pages, and it stops the two entries whose authors `lit/01` never recorded from
rendering inline as "leg [2026]" and "len [2026]".

**3. THE PAGE BUDGET: four pages, and two free lines left after pass 3.**
The `notes/06` §5.1 cut plan was applied 2026-09-11 (F1, F2, the schema and similarity tables,
the token test and the scratchpad channel to the appendix; §1 written; F3, then the only body
float, at `0.70\linewidth`). That still left four lines of §5 above References, so the audit's cuts
C1–C6 were taken as well, plus nine compressions of material the paper says twice — every one
with an appendix home, and **no number left the paper**. The new appendix paragraph
`app:robust` holds the interval rule, the survivor check, the edit-arm bound, arm 1's carrier
deltas and the public-input trigger share.

Measure the slack, do not estimate it: the last body baseline against the bottom of the text
block, in 10.9pt lines. `pdftotext -bbox-layout` is the only reliable way — the submission
style prints a line number beside every line and a folio under the block, and both come back
as `<line>` elements that will flatter your count if you leave them in.

**Since the second pass the body fills page 4, so that measurement reads 0.0 and is no longer
the one to use.** The style file sets `\flushbottom`, so once no References line shares page 4
the last body baseline is stretched onto the block's bottom edge whatever the true slack is.
Probe instead: append N one-word body lines (`\noindent PROBELINE\\`) just before
`\bibliographystyle`, rebuild, and find the largest N that keeps every probe line on page 4.
**On 2026-09-11, after pass 3, that is N = 2**; the third spills. (`notes/12` M8 re-ran the probe
against the pass-2 body and got **N = 0**, not the 3 this file used to claim — the second pass had
spent the slack and the figure was stale. Re-run the probe after every edit to §1–§5; do not trust
a number written here without a date.)

**There are now two body floats.** Pass 3 moved the Gate S rows into Table~1 (`tab:gates`,
`[h]`, `\footnotesize` + booktabs, five rows: Sonnet headline, Haiku headline, Sonnet
prompt-matched, Sonnet strict, Sonnet strict prompt-matched). It is placed `[h]` deliberately, so
it stays inside §3 beside the paragraphs that read it; it currently sets at the foot of page 3.
Its caption is short **because caption lines are body lines**: the ρ definition and the bands are
in the arm-1 paragraph, the interval convention is in `app:robust`, and the caption carries only
what neither does. If you lengthen it, re-run the probe.

**F3's float anchor is load-bearing.** A `[t]` float lands at the top of the page *after* the
page its definition falls on, so with the definition sitting in §3 a four-word edit anywhere
earlier flipped it between pages 3 and 4 and swung the end of the body by a page. It is now
defined inside §2, a page from either boundary. Leave it there. Pass 3 narrowed it to
`0.64\linewidth` (from `0.70`) to pay for part of Table~1; if a float-only page ever appears,
check where F3 and Table~1 have gone.

**Pass 3 (2026-09-11) spent, and then re-earned, the last of the slack.** The Gate S paragraph
became three paragraphs plus Table~1, which costs more lines than the prose it replaced, so the
cuts `notes/12` §3 ranks were taken in its order: arm 1's row-level numbers to `app:robust`, the
agentic-settings paragraph to one sentence, the token-test clause to its pointer, the
retention/edit-arm clause (already in `app:robust`), the pair-similarity paragraph folded into a
clause, Recommendation 4's bundle enumeration (it is in `app:release`), and F3 to `0.64`.
**No number left the paper** — checked by comparing every `\newcommand` against its uses before
and after. Four numbers came *in*: `\matchedStrictLo/Hi/Bprime` and `\matchedBprime`.

**The three arms landed on 2026-09-12 and spent that slack.** The reserved block is gone:
`\matched*`, `\promptOnly*`, `\mon*` and `\haiku*` carry measured values from `RESULTS.md`
§13–§15, each with its protocol, its n and its ledger section in the comment; `\TBDRED` is
deleted and `grep -n TBD main.tex` is empty. The sentences of `notes/09` §4 (branch 1) and the
Haiku clause cost the 13.5 lines almost exactly, so cut C1's "five fold seeds" parenthetical was
taken as well and its number moved to `app:robust`. (That pass left **no** free lines, not the
three this file claimed until pass 3 measured it — see the probe above.)

### Both tables are width-constrained; do not "tidy" the column specs

The first build overflowed the 5.5in text block badly — F1 by ~104pt, with the rules
running off the page edge. `figures.py:fig1_table` now emits a 5-column table (the Metric
column is gone; rows are grouped under *AUROC* / *Pairwise accuracy* subheadings instead;
a *Prep.* column, added 2026-09-11, says per row whether comments were stripped, kept, or
never read) with `p{}` columns tuned against these constraints:

| Column | Width | Constraint |
|---|---|---|
| Protocol | `0.255` | ", comments stripped" moved to the Prep. column, so "Koran's exact split" fits; longer protocol names wrap |
| Baseline | `0.225` | must hold `solution_passes_tests`, which is unbreakable |
| Prep. | `0.090` | holds "stripped" / "kept" / "no code" on one line |
| Against | `0.170` | absorbs the remaining slack; wraps freely |

Narrowing Baseline reintroduces an overfull box. The schema table in `main.tex` (now in
the appendix) has the same problem and the same fix. Table~1 (Gate S, body) is the third:
`@{}l r l r l l@{}` at `\tabcolsep` 4pt and `\footnotesize` fits the 5.5in block with the
arm labels as written; lengthening a row label or a band word will overflow it. **Current state: zero overfull boxes.**
F1's pairwise rows carry the comment-stripped values from `RESULTS.md` §6 with the earlier
comments-kept values beside them labelled "inflated by the comment channel"; pairwise
accuracies are three decimals, AUROCs four.

**3. Every load-bearing number is a macro, defined once at the top of `main.tex`.**
Do not hardcode a number inline. This is not tidiness: this project's recurring failure is
a value from one protocol written beside a count from another, and it has reached the
README, the outline and `figures.py`. The macros make the two no-code protocols
impossible to cross by accident:

| Macro | Value | Count macro | Protocol |
|---|---|---|---|
| `\nocodeCV` | 0.772 | `\nocodeCVCount` = **20** | 5×5 CV within the test split |
| `\nocodeHeldout` | 0.716 | `\nocodeHeldoutCount` = **18** | single 413-item held-out slice |

## Before submitting

- [x] ~~Uncomment the `\renewcommand{\TODO}[1]{}` line so markers stop rendering.~~ **Done
      2026-09-11**, after verifying by grep that the five citation keys that used to live only
      inside `\TODO{}` blocks are cited in §1's prose. No `\TODO{}` remains in the source.
- [x] Gate S: filled 2026-09-11 from `RESULTS.md` §9 (S, B′, ρ with CIs, learning curve,
      survivor check, edit-arm bound) and §10 (the positive control, `\monitorS` / `\monitorStrict`).
      The §3 outcome paragraph states the pre-registered ruling: inconclusive between partial and
      content, collapse excluded. The old `\TBD` is deleted; `\TBDRED` and the arm A/B/C
      placeholders are the only `TBD` in the source, and `grep -c TBD` on the **PDF text** stays 0.
- [x] ~~**Second pass, pending `RESULTS.md` §13–§15.**~~ **Done 2026-09-12.** The reserved
      placeholders carry measured values; `notes/09-review-audit.md` §4's **branch 1** was taken
      (S_matched collapses, so the residue is the attack prompt's framing), and the abstract's
      third clause now states two generators and two bands — a third (Sonnet 5) to nine-tenths
      (Haiku 4.5) — which are never averaged. Cut C1's "five fold seeds" parenthetical was taken
      to hold a three-line margin; its number moved to `app:robust`, so no number left the paper.
- [x] ~~Complete the bibliography.~~ **Done 2026-09-10.** All 28 entries verified against the arXiv
      API in one query (HTTP 200, every arXiv-hosted entry returned — not a throttled stub, per R3). **Six of `lit/01`'s
      partial records were wrong, not merely incomplete**; see the CORRECTIONS block atop `refs.bib`.
      Control Tax is a *2025* paper with a longer title; `2607.09786`'s author is Bryce Little, where
      `lit/01` recorded none — for the paper we credit with owning the scratchpad-regex instrument;
      and AICD's "Paul" and "Wang" are first names, so "Paul et al." would have been wrong.
- [ ] Confirm the content body is within 4 pages (it is exactly 4 as of 2026-09-11 after pass 3,
      with **two** free lines by the probe above; re-check after every edit to §1–§5).
- [x] **Is a paper checklist required? No.** Settled 2026-09-12: the workshop CFP page
      (`index.html` of the workshop site) does not contain the word, and the OpenReview form
      carries only title, authors, keywords, TL;DR, abstract, PDF, licence, readers and
      signatures. `checklist-reference.tex` stays un-`\input`.
- [x] Release sentence in §4 item 4 names what the bundle holds without the counts, which now
      live once, in appendix paragraph `app:release`, with the crash-as-firing count and the
      `\relScripts{}` scripts. The bundle really does carry them as of schema 3 — `release/scripts/`
      and `release/LICENSE`, `notes/07` has the build and zip commands.
- [ ] Author block stays anonymous. The style file suppresses it, but do not paste real
      names in and rely on that.
