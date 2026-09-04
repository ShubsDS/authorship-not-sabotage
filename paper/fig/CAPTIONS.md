# Figure captions — drafted 2026-09-04

The outline says some caveats belong **in the caption, not in Limitations**. Those are marked below.
Regenerate the figures with `experiments/apps/figures.py`; do not hand-edit the PDFs or the `.tex`.

## F1 · `f1-protocol-baseline.tex`

Carries its own `\caption{}`. The load-bearing clause is the second one — **rows are not comparable
across protocols** — and it is what stops a reader repeating the round-16 mistake of reading one
protocol's number against another's.

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
