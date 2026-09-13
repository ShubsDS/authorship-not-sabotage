# Figure captions — drafted 2026-09-04, inventory checked 2026-09-10

The outline says some caveats belong **in the caption, not in Limitations**. Those are marked below.
Regenerate the figures with `experiments/apps/figures.py`; do not hand-edit the PDFs or the `.tex`.

> ### Regenerating: two things to know before you run it
> **`figures.py` needs `matplotlib`, which the documented install line omitted until 2026-09-10.** A
> fresh clone following `experiments/README.md` could not rebuild the figures. Fixed there.
>
> **Every figure is laptop-reproducible with no data fetch.** F1, F2, F4 and F5 are computed from
> constants in `figures.py` (`F1_ROWS`, `SCAN`, `CONSTRUCTIONS`, `RHO_ROWS`); F3 reads the tracked
> `monitor-summary.json`. None of them needs the parquet shards. As of the 2026-09-13 rebuild the
> script also reads `../../paper/main.tex` — for `check()`, not for any drawn value — so run it
> from `experiments/apps/` with the paper checked out beside it.
>
> ✅ **The figures are now bit-reproducible on a fixed matplotlib (2026-09-10).** They previously
> differed on every rebuild by exactly 8 bytes, the `/CreationDate` matplotlib stamps into each PDF.
> `figures.py` now passes `metadata={"CreationDate": None}`, so two consecutive runs give identical
> hashes and git no longer reports unchanged plots as modified. Verified when the change was made:
> every decompressed content stream matched the previous build — 45/45 for F2, 42/42 for F3, equal
> SHA-256 — so only the timestamp and the xref offsets it shifted actually changed. F1's `.tex`
> already reproduced exactly.
>
> ⚠️ **A different matplotlib version will still change the bytes** — font subsetting differs across
> versions (17,318 → 17,597 for F2 on matplotlib 3.11.1). Reproducibility here means *same version,
> same bytes*, not across versions. Built on matplotlib 3.10.5.
>
> ⚠️ **The FONT has to be present too, and on 2026-09-13 it was not.** `figures.py` asks for Nimbus
> Roman first and Times New Roman second. Nimbus Roman is not installed on this machine in any form
> matplotlib can read — TeX Live ships it as Type 1 `.pfb` (`utmr8a.pfb`), which the Agg backend
> cannot use, and there is no `.otf`/`.ttf` copy anywhere on disk — so every figure rebuilt on
> 2026-09-13 fell back to **Times New Roman**. The two are metrically compatible Times designs and
> nothing reflowed, but the glyphs are Monotype's rather than URW's, and the body text is still
> ptm (= Nimbus). All four figures were regenerated together so the paper is at least internally
> consistent. **To restore Nimbus: install the URW base-35 fonts (ghostscript, or a
> `font-urw-base35` cask) and re-run `figures.py`** — it changes font bytes only, no layout.
>
> ℹ️ **The paper was already mixed before this, which is how the fallback went unnoticed.** F5 as
> committed was *already* Times New Roman — regenerating it on 2026-09-13 produced byte-identical
> output, so it had been built on a machine without Nimbus at some earlier point, while F2 and F3
> still carried Nimbus. Whoever restores the font should re-run `figures.py` once and commit all
> four together, rather than fixing the figure they happen to be editing.

> ### Rebuilt on the dashboard draft, 2026-09-13
> All four PDFs were regenerated from a rewritten `figures.py` that takes its visual language —
> panel/card/badge layout, shaded retention bands, the null-to-value connector — from a
> dashboard-style draft written outside the repo. Three properties of that draft did **not**
> survive the port and must not come back:
>
> * **Its numbers.** Five of the five `SCAN` permutation nulls, two ρ intervals, one invented ρ
>   interval and F4's leading AUROC were not the measured values. Every figure value is now a
>   named constant carrying its ledger location, and `figures.py check()` asserts the lot against
>   `main.tex`'s `\newcommand` block at every run — 189 macros read, and the run **fails** rather
>   than drawing a number the prose contradicts. That check is the reason to keep the macros and
>   the script in sync in both directions.
> * **Its type.** It set in DejaVu Sans. The paper sets in ptm; see the font box above.
> * **Its point sizes.** It was drawn 11 in wide for figures included at 3.5–5.5 in, which would
>   have printed 4 pt badges. `figsize` is now the printed width in every figure (`W_F2`, `W_F3`,
>   `W_F4` derive from the 5.5 in block and the `\includegraphics` fractions in `main.tex`), so
>   every `fontsize=` is the size it lands on the page. Nothing renders below 6 pt.
>
> Its two extra figures — a chart of the F1 table, and a pair-similarity/feature panel — were not
> taken: Table A2 already is the first, and the second's numbers were Table A3's rows under
> shuffled arm labels (it captioned the **edit** arm's 64.2 % near-copy share as the
> prompt-matched arm's, which inverts why the edit arm was excluded).

> ### ✅ RESOLVED — the constructive half has two figures now
> This box read *"MISSING: there is no Gate S figure"* while the paper's constructive half was
> prose-only. F4 (the constructions) and F5 (the ρ forest) both exist; F1 did move to the
> appendix as the swap at the foot of this file proposed. **The planning section at the bottom is
> superseded and kept only for the argument it records.**

## F1 · `f1-protocol-baseline.tex`

Carries its own `\caption{}`. The load-bearing clause is the second one — **rows are not comparable
across protocols** — and it is what stops a reader repeating the round-16 mistake of reading one
protocol's number against another's.

## F4 · `f4-constructions.pdf`

**Fourth version, 2026-09-13.** V1 was a flow diagram (trees, arrows, a chip row per panel). V2
was the same content as a grid of twelve filled rounded boxes, and it still read as cluttered.
V3 removed every box. **V4 puts the cards back** — the dashboard draft's panel, problem deck,
honest/attack cards, factor rows and status badges — but keeps V3's encoding intact, which is the
only reason the port is defensible. The merged / split grammar and the alignment survive intact,
and the badge only *names* what position already says. The enclosure finding is the one V4 spends
down — see the second bullet below. Height is **3.15 in**, up from V3's 2.16, which the cards cost.

Three things V4 changes beyond the styling:

* The pair count (`1,444 pairs`, `623 pairs`, `586 pairs`) is now **in** each panel. The caption
  used to carry all three, and the ladder claim — these are different problem sets, not a paired
  comparison — is the one thing a reader must not miss.
* The AUROC row is a **number in a tinted pill**, not a dot on a chance-to-1.0 scale. The caption's
  clause "on one scale from chance to 1.0" was cut with it; do not restore one without the other.
* The draft labelled panel one **`BoW: 0.806`**. That is the Koran-split floor, and this figure's
  own caption says in as many words that none of the three numbers is it. The value is
  `\baselineB` = 0.871. `check()` now fails the build if panel one is ever within 0.005 of the
  floor again.

The three findings that decided V3. Two are spent exactly as they were; the middle one is not:

* **Cleveland & McGill's ranking of elementary perceptual tasks** (Wong, *Nat. Methods* **7**:665)
  puts *position on a common scale* first and *colour hue* last. V2 encoded its one claim — are
  the two classes the same in this property or not — in **fill colour**, rank 6–7. V3 puts it in
  **position**: a shared property is written **once**, centred across the pair and tied; a
  differing one is written **twice**, once under each class. One word versus two.
* **Gestalt grouping** (Wong, *Nat. Methods* **7**:863): enclosure is the strongest grouping cue,
  strong enough to override similarity, proximity and connection — so it must be spent once, on
  the grouping that matters most. V2 spent it on all twelve cells plus the panel, so nothing was
  grouped. V3 spent it once, on the tint behind the two columns we build. **V4 re-enclosed the
  panels and the cards, so enclosure is no longer what marks that grouping** — the tint still is,
  and it is now the only thing distinguishing the two columns we build from the one we inherited.
  This is the finding V4 spends down; it is the price of the card layout, and it is why the tint
  must not be dropped.
* **Visual completion** (Wong, *Nat. Methods* **7**:941): *"enables us to forgo the extraneous
  lines, boxes, bullets and other graphical elements that tend to clutter our presentations."*
  The rows and columns hold together on alignment alone, with two hairlines for structure.

The tie under a merged value is grouping by **connection**, the next cue down, which is the right
weight for a secondary signal. Count the ties and you have the paper: none, one, two.

Column titles are the ladder. V3's were *as stored* / *+ same writer* / *+ same prompt*, each
naming the row it merges. V4's are the paper's own names for the three corpora — *stored
benchmark*, *same-generator*, *prompt-matched* — because the body and Table 2 name the arms that
way and the reader has to get from one to the other. The merged rows still say which property
each construction fixed, so the rename costs nothing.

**Cut on request, 2026-09-13:** the *as stored* / *what we build* band labels (the tint carries
it, and the caption names it); $\rho$ (nothing near this figure explains it — it is defined in
§3 and tabulated in Table 2); and the $B$ / $S$ symbols. $B$ and $S$ are the same classifier's
AUROC on different corpora, and printing them under two letters made one measurement look like
two — the three numbers are now bare under a row labelled AUROC.

**Text budget — this applies to every figure, not only F4.** Every string on the canvas is a
label, never a phrase. The row label and the cell form the phrase between them ("prompt" +
"solve", not a cell reading "solve the problem"), and anything needing a clause goes in the
caption. V2 still carried "Claude Sonnet 5 writes both", "one prompt for both classes", "written
for APPS" and "$\rho$ = 0.687 of the baseline"; all of it is gone. Both generators are Sonnet
models, so they are named "Sonnet 3.7" and "Sonnet 5" rather than "Claude 3.7" against "Claude
Sonnet 5", which hid that and cost a word.

Not in it, deliberately: Haiku 4.5 and the strict rows (Table 2 carries every row), the fire
shares, and the flow arrows V1 spent most of its ink on. Height is **2.16 in**, down from V1's
2.62: dropping the boxes, the band row and the $\rho$ row took it there, and the space went to a
caption that now has to teach the encoding.

> ⚠️ **One imprecision this figure turned up, not yet fixed in the ledger.** `RESULTS.md` §13 says
> `PROMPT_INDEPENDENT_HONEST` is `PROMPT_INDEPENDENT` "with only the flaw sentence replaced", and
> §13's bullet says the classes "differ in the one sentence that asks for a flaw". Printing the
> two constants side by side, they differ in **four** places — the opening clause, the
> correctness requirement, the "looks like ordinary code/mistake" sentence, and the description
> of the ```` ```input ```` block. All four are about the flaw, so the substantive claim stands,
> but "one sentence" is wrong. The caption says "the sentences that ask for a flaw".

## F2 · `f2-corpus-floors.pdf`

**V4 note, 2026-09-13.** The draft's connector from the permutation null to the measured value is
kept, drawn thin. It is *not* drawn at bar weight: at 4 pt it reads as a bar grown from the null,
and zero is not the reference for an AUROC — 0.5 is. **Three of the five nulls sit below chance**
(0.4801–0.5118, `scan/FINDINGS.md` §2b), so three connectors cross the chance rule. The draft had
every null above chance and no row crossing, on five numbers that are in no ledger.

> **The structural floor in five same-generator agentic settings.** Each setting's content-blind
> classifier — six count features, no content read — scored *within task* against its own permutation
> null. No authorship confound is possible here: claude-sonnet-4, gemini-2.5-pro and gpt-5 write both
> classes in all five. `bash` sits on its null; `agentdojo` reaches 0.802 from character count alone.
> **The task-group count beside each setting matters:** `shade` and `iac` average over five task
> groups each while `bash` averages over 247, so these floors are not equally well determined. We
> report the within-task column because our own pooled numbers partly broke on task composition, and
> we broke them ourselves. Two of these corpora declare no licence; we redistribute nothing and
> report aggregates only.

## F3 · `f3-monitors-vs-floors.pdf`

**V4 note, 2026-09-13.** Two of the draft's choices are kept and one is dropped.

*Kept:* the shaded spans behind the two floors. They are the bootstrap CIs of `RESULTS.md` §8.3
(0.7319–0.8005 and 0.7704–0.8409), they genuinely overlap, and that overlap is the honest picture
of "both floors clear 20 of 24". The earlier version omitted a band on the ±0.039, which was the
right call for a *fold spread*; a CI is a different object and can be drawn.

*Dropped:* colouring each monitor dot by whether it cleared the no-code floor. There are **two**
floors 0.035 apart, so a dot at 0.79 is below one and above the other, and a two-tone split on one
of them asserts a count the figure cannot support. One hue.

Every vertical rule, and now every span, **stops at the top of the data**. Drawn full height with
`axvline`/`axvspan` they run through the key — the span more heavily than the line ever did.

> **Two floors against the 24 open-weight monitors ranked on the same split.** All values are AUROC on
> Koran et al.'s 1,375-item test split (172 attack / 1,203 honest), comments stripped. Monitor scores
> are `runs/x0/monitor-summary.json` from Jha (MIT); median 0.609, max 0.937.
> **Two caveats belong here rather than in Limitations.** (i) The 24 monitors are zero-shot prompted
> while the bag-of-words classifier is *trained* on the benchmark's own paired train split — this is a
> statement about what the corpus makes recoverable, in the sense of Gururangan et al., not a claim
> that bag-of-words is a better monitor. (ii) The no-code floor is fitted **within** the test split by
> 5×5 cross-validation, because the released train/val split is paired and therefore
> metadata-balanced; on a single held-out slice of the same items it is **0.7163, above 18 of 24**.

## F5 · `f5-rho-forest.pdf`

**Built and tracked, but `main.tex` does not `\includegraphics` it** — Table 2 carries these rows
instead. Keep it correct anyway; it is one edit away from being a float, and a stale tracked PDF is
worse than none.

A forest plot: one ratio measured eleven ways, and the reader's question is which pre-registered
band each lands in. The draft's shaded bands and their headers are kept. Its colour-by-band is not:
band membership is already position, so hue goes to *which measurement* — bag-of-words classifier,
LLM monitor, bound. The null at ρ = 1.234 sits to the **right** of ρ = 1, which is the whole reason
to publish it.

**Rows with no published joint interval get a point and no whisker.** The draft drew
1.150–1.318 around the 1.234; `RESULTS.md` §2 quotes no interval there. It also had 0.055–0.175 for
the Haiku prompt-matched row (§15.6 says 0.055–**0.165**) and 0.301–0.441 for the edit bound (§9.1
row 7 says 0.306–**0.430**).

## ⚠️ Two numbers that must not be written carelessly

### Never write "0.772, above 18 of 24"

That takes the 5×5 CV *value* and the held-out *count*. The two self-consistent readings are:

| Protocol | Value | Monitors below |
|---|---|---|
| 5×5 CV within the test split | **0.7715 ± 0.0389** | **20 of 24** |
| single 413-item held-out slice | **0.7163** | **18 of 24** |

`experiments/K1-artifact-lineage.md` §4.4 had this right. The summary documents compressed it wrongly
and it reached the README and this outline. It is R18's companion error — *compare on the same
protocol or not at all* — committed against ourselves, and building F3 is what caught it, because a
figure has to pick one number and then count.

### Pairwise accuracies get three decimals, not four

**0.962, 0.979, 0.955.** The resolution of a pairwise accuracy over 2,641 pairs is 1/2,641 = 0.00038,
so a fourth decimal is a single pair. Re-running on a second machine moved exactly one pair in two of
these numbers (`experiments/REPRODUCED.md`). AUROCs are not threshold-sensitive in that way and match
to four decimals.

---

## The figure that does not exist yet — Gate S

Three figures cover the *diagnostic* half of the paper (what the preprocessing leaves behind, how
the floors compare to monitors, the same-generator negative control). **Nothing covers the
constructive half**, which is the newest and most contested part of the argument.

### What already exists to plot, with no further runs

| Quantity | Value | Source |
|---|---|---|
| **B** (benchmark as shipped) | 0.8714 ± 0.0085, n = 1,444 | `apps/gate_s_baseline.json` |
| routing thresholds | collapse ≤ 0.6226 · content > 0.7674 | same |
| **arm 1** B′ → G | 0.8739 ± 0.0160 → 0.9616 ± 0.0090, n = 668 | `apps/gate_s_q3c30.json` |
| **ρ** | 1.2344, +4.78 sd — CONFOUNDED | same |
| carrier decomposition, B′ → G | TF-IDF 0.874 → 0.962 · length 0.653 → **0.489** · surface-7 0.803 → 0.809 | same |
| **S** | pending | `apps/gate_s_samegen.py` |

### The strongest candidate: the carrier decomposition

Three carriers, B′ → G, as paired points on one AUROC axis. It renders the paper's sharpest new
sentence — *the new gap is lexical, not structural* — as a picture: **TF-IDF rises while length
collapses to chance and surface-7 does not move.** At present those three numbers sit inside a
sentence, where a reader has to do the comparison in their head. It is also what turns arm 1 from
"an arm that failed" into "a diagnosis of why one-sided regeneration cannot work", which is a
contribution rather than a gap.

A second option is a ρ number line — B, the two thresholds, arm 1 landing off-scale above 1, and a
slot for S — which shows the routing rule was fixed in advance and where each arm fell.

### ⚠️ This is a SWAP, not an addition

The paper is already ~5.5 content pages against a hard 4 (`../README.md`). A new float costs
~0.5 pp. The recommended trade is **F1 out to supplementary, Gate S figure in**: F1 is a 14-row
lookup table whose two load-bearing rows (0.4726 → 0.806) are already stated in prose, whereas the
Gate S figure carries an argument that currently has no visual at all. Do not add it on top.
