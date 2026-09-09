# paper/ — the submission

Built and verified 2026-09-09. `main.tex` compiles clean from a fresh checkout:
**exit 0, no BibTeX errors, no undefined citations.**

```bash
cd paper && latexmk -pdf main.tex
```

`latexmk -C` cleans. MiKTeX 25.12 and TeX Live both work; nothing exotic is used.

## What is here

| File | What |
|---|---|
| `main.tex` | The paper. Section-by-section skeleton following `OUTLINE.md`, every gap marked `\TODO{}` carrying that section's instruction. |
| `refs.bib` | 25 entries, built **only** from `lit/01-verified-bibliography.md`. |
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

**3. It is currently ~4.3 content pages against a 4-page limit — and that is with
`\TODO` markers, not prose.** References start partway down page 5 and do not count.
The fixed cost is the float load: two tables (schema, F1) and two figures (F2, F3).
F1 alone is 14 rows. `PLAN.md` §5 already fixes the cut order — CoT paragraph, then the
character-n-gram row, then the fifth agentic setting. Expect to need it.

### Both tables are width-constrained; do not "tidy" the column specs

The first build overflowed the 5.5in text block badly — F1 by ~104pt, with the rules
running off the page edge. `figures.py:fig1_table` now emits a 4-column table (the Metric
column is gone; rows are grouped under *AUROC* / *Pairwise accuracy* subheadings instead)
with `p{}` columns tuned against two hard constraints:

| Column | Width | Constraint |
|---|---|---|
| Protocol | `0.345` | must hold "Koran's exact split, comments stripped" on one line |
| Baseline | `0.225` | must hold `solution_passes_tests`, which is unbreakable |
| Against | `0.170` | absorbs the remaining slack; wraps freely |

Narrowing either of the first two reintroduces an overfull box. The schema table in
`main.tex` has the same problem and the same fix. **Current state: zero overfull boxes.**

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

- [ ] Uncomment the `\renewcommand{\TODO}[1]{}` line so markers stop rendering.
- [ ] `grep -n INCOMPLETE refs.bib` — **18 of 28 entries** need their author list
      completed from the arXiv abs page. Two (`legibility2026`, `lengthpenalties2026`)
      have **no authors at all** recorded in `lit/01`, and one of those is the paper we
      credit for owning the scratchpad-regex instrument. Budget an hour.
- [ ] Confirm the content body is within 4 pages.
- [ ] Gate S: either fill the Results paragraph and update `\baselineB`, or delete that
      paragraph and take route 4 (`PLAN.md` §3) — the Limitations `\TODO` for it is
      already written.
- [ ] Author block stays anonymous. The style file suppresses it, but do not paste real
      names in and rely on that.
