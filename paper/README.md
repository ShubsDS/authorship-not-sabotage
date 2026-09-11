# paper/ — the submission

Built and verified 2026-09-11. `main.tex` compiles clean:
**exit 0, no undefined citations, zero overfull boxes, exactly four content pages**
(the References heading is the first line of page 5; the appendix follows the references).

```bash
cd paper && pdflatex -interaction=nonstopmode main && bibtex main \
  && pdflatex -interaction=nonstopmode main && pdflatex -interaction=nonstopmode main
```

`latexmk` is **not** installed on the local machine; the four-pass line above is the build.
MiKTeX 25.12 and TeX Live both work; nothing exotic is used. Count content pages from the
PDF (`pdftotext -layout main.pdf - | grep -n References`), not from the source.

## What is here

| File | What |
|---|---|
| `main.tex` | The paper. §1–§5 plus F3 as the only body float; schema table, F1, similarity table, F2, the token test, the harness note, the comment-stripping companion values and the scratchpad channel are in the appendix after the references. `\TODO` is the no-op form (2026-09-11) — see "Before submitting". |
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

**3. ⚠️ THE BINDING CONSTRAINT: the body is at exactly four pages with no slack.**
The cut plan in `notes/06` §5.1 was applied 2026-09-11 (F1, F2, the schema and similarity
tables, the token test and the scratchpad channel moved to the appendix; §1 written; Gate S
block, byline, harness and Limitations compressed; F3 at `0.70\linewidth` is the one body
float). Measured after that: 8 pages total, References heading on the first line of page 5.
**Any sentence added to §1–§5 pushes Limitations onto page 5.** When the Gate S outcome
sentence replaces the did-not-land paragraph (handoff §4.3) or the headline intervals go in
(§4.4), cut an equal amount elsewhere and re-measure. If a float page appears, check that
only F3 remains as a float in the body.

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
the appendix) has the same problem and the same fix. **Current state: zero overfull boxes.**
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
- [ ] Gate S placeholders: `\sameGenS`, `\sameGenN`, `\sameGenLo`, `\sameGenHi`, `\sameGenRho`,
      `\monitorS` are defined as a visible red **TBD** and are not used anywhere in the body while
      the did-not-land paragraph (notes/06 §5.3) is the active §3 text. Either fill them and swap
      in the outcome sentence, or leave the paragraph; never ship a TBD (grep the PDF text).
- [x] ~~Complete the bibliography.~~ **Done 2026-09-10.** All 28 entries verified against the arXiv
      API in one query (HTTP 200, every arXiv-hosted entry returned — not a throttled stub, per R3). **Six of `lit/01`'s
      partial records were wrong, not merely incomplete**; see the CORRECTIONS block atop `refs.bib`.
      Control Tax is a *2025* paper with a longer title; `2607.09786`'s author is Bryce Little, where
      `lit/01` recorded none — for the paper we credit with owning the scratchpad-regex instrument;
      and AICD's "Paul" and "Wang" are first names, so "Paul et al." would have been wrong.
- [ ] Confirm the content body is within 4 pages (it is exactly 4 as of 2026-09-11; re-check
      after every edit to §1–§5).
- [ ] Gate S: the did-not-land paragraph stands in §3 and Limitations says the authorship
      reading is inference. If a readable S lands, replace per handoff §4.3 and cut elsewhere.
- [ ] Release sentence in §4 reads "Ours will be released under MIT"; replace with the
      sentence from `notes/07-release.md` once the bundle exists.
- [ ] Author block stays anonymous. The style file suppresses it, but do not paste real
      names in and rely on that.
