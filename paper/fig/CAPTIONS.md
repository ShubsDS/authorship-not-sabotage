# Figure captions — drafted 2026-09-04, inventory checked 2026-09-10

The outline says some caveats belong **in the caption, not in Limitations**. Those are marked below.
Regenerate the figures with `experiments/apps/figures.py`; do not hand-edit the PDFs or the `.tex`.

> ### Regenerating: two things to know before you run it
> **`figures.py` needs `matplotlib`, which the documented install line omitted until 2026-09-10.** A
> fresh clone following `experiments/README.md` could not rebuild the figures. Fixed there.
>
> **All three figures are laptop-reproducible with no data fetch.** F1 and F2 are computed from
> constants in `figures.py` (`F1_ROWS`, `SCAN`); F3 reads the tracked `monitor-summary.json`. None of
> them needs the parquet shards.
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

**Third version, 2026-09-13.** V1 was a flow diagram (trees, arrows, a chip row per panel). V2
was the same content as a grid of twelve filled rounded boxes, and it still read as cluttered.
V3 removes every box. Three findings decided it, and each is spent deliberately:

* **Cleveland & McGill's ranking of elementary perceptual tasks** (Wong, *Nat. Methods* **7**:665)
  puts *position on a common scale* first and *colour hue* last. V2 encoded its one claim — are
  the two classes the same in this property or not — in **fill colour**, rank 6–7. V3 puts it in
  **position**: a shared property is written **once**, centred across the pair and tied; a
  differing one is written **twice**, once under each class. One word versus two.
* **Gestalt grouping** (Wong, *Nat. Methods* **7**:863): enclosure is the strongest grouping cue,
  strong enough to override similarity, proximity and connection — so it must be spent once, on
  the grouping that matters most. V2 spent it on all twelve cells plus the panel, so nothing was
  grouped. The **only** enclosure now is the tint behind the two columns we build.
* **Visual completion** (Wong, *Nat. Methods* **7**:941): *"enables us to forgo the extraneous
  lines, boxes, bullets and other graphical elements that tend to clutter our presentations."*
  The rows and columns hold together on alignment alone, with two hairlines for structure.

The tie under a merged value is grouping by **connection**, the next cue down, which is the right
weight for a secondary signal. Count the ties and you have the paper: none, one, two.

Column titles are the ladder — *as stored*, *+ same writer*, *+ same prompt* — and each names the
row it merges, so a title can be traced to its row. The AUROC row is a **dot on a scale from
chance to 1.0**, not a filled bar: position again, and a hairline plus a dot where V2 had three
more rounded rectangles.

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

> **Two floors against the 24 open-weight monitors ranked on the same split.** All values are AUROC on
> Koran et al.'s 1,375-item test split (172 attack / 1,203 honest), comments stripped. Monitor scores
> are `runs/x0/monitor-summary.json` from Jha (MIT); median 0.609, max 0.937.
> **Two caveats belong here rather than in Limitations.** (i) The 24 monitors are zero-shot prompted
> while the bag-of-words classifier is *trained* on the benchmark's own paired train split — this is a
> statement about what the corpus makes recoverable, in the sense of Gururangan et al., not a claim
> that bag-of-words is a better monitor. (ii) The no-code floor is fitted **within** the test split by
> 5×5 cross-validation, because the released train/val split is paired and therefore
> metadata-balanced; on a single held-out slice of the same items it is **0.7163, above 18 of 24**.

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
