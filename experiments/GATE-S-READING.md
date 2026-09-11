# Gate S — how to run it and how to read it

For whoever runs Gate S on the real data. `GATE-S-RUNBOOK.md` is how the data was made; this is what to run
once it exists and what the numbers mean. CPU only. Run from
`experiments/apps/` with `train_*.parquet`, `gen_<tag>.jsonl`, `pass_<tag>.jsonl`,
`bdind_<tag>.jsonl`, `bdpass_<tag>.jsonl` and `human_verify.jsonl` present.

## 1. The command sequence, in order

```bash
# (a) HEADLINE — independent arm, attack class = passes the public tests (n ≈ 335)
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5.jsonl \
    --eligibility passes --bprime-inert --out sg_indep_passes.json

# (c) STRICT — same arm, attack class = passes AND fires (n ≈ 10 now, ~125 with the retry batch)
python gate_s_samegen.py --tag sonnet5 --bd bdind_sonnet5.jsonl \
    --eligibility usable --out sg_indep_usable.json

# the underfitting control, once per arm you intend to quote
python gate_s_learning_curve.py --human-pass-file human_verify.jsonl \
    --match-problems sg_indep_passes.json --out lc_passes.json
python gate_s_learning_curve.py --human-pass-file human_verify.jsonl \
    --match-problems sg_indep_usable.json --out lc_usable.json
```

Always pass `--out`: the default filename keys on tag/arm/eligibility only, so the `passes` run
with and without `--bprime-inert` would overwrite each other. `--eligibility all` is a sanity row,
not a result. The edit arm (`--bd bd_<tag>.jsonl`) is a **bound**, never a verdict: its pairs are
near-copies (mean similarity 0.924, 68.7% above 0.95, against 0.469 in the benchmark).

`gate_s_samegen.py` refuses to run if the two jsonl files disagree on `model` — with different
generators on the two sides it measures authorship and its verdict lines would be confidently
wrong — and below `--min-pairs` (default 50).

## 2. The fields

`gate_s_samegen_*.json`

| Field | Meaning |
|---|---|
| `n_same_generator_pairs`, `problem_ids` | S's n and the exact problems; the ids feed `--match-problems` |
| `S.auroc`, `S.auroc_sd` | mean and across-fold sd of the 5-fold TF-IDF AUROC. **The sd is not a standard error** — it is ~1.9× a true 95% half-width; never print ±2 sd |
| `S.auroc_ci95_boot` | bootstrap over problems on the pooled out-of-fold scores. **This is the interval to quote** |
| `S.pairwise_acc`, `S.length_only_auroc`, `S.surface7_auroc` | the three carriers; length falling to chance while TF-IDF stays high is the signature of a lexical, not a size, effect |
| `B_prime` | the same fit on the stored benchmark over the *same problems* — ρ's denominator |
| `b_prime_attack_rule` | which stored backdoors B′ used: `passes AND fires`, or `passes (inert-inclusive)` under `--bprime-inert` |
| `retained_vs_stored`, `rho_ci95` | ρ = (S−0.5)/(B′−0.5) and its interval, from S's bootstrap CI |
| `pair_similarity` | with `stored_same_problems`: an arm far above the stored mean can manufacture a low S by construction |
| `verdict_lines`, `verdict` | the two AUROC lines the ρ bands imply at this B′, and the state |

`gate_s_learning_curve.json`: `points[]` carries, per n, `auroc_mean/_sd` (over `--draws`
subsamples of the B pool), the same for pairwise/length/surface7, and `ci_width_mean`;
`b_on_s_problems` is B refit on S's own problem ids; `paper_sentence` and
`collapse_attributable_to_n` are the routed conclusion.

## 3. Reading ρ against B′

Bands were fixed before any arm ran: collapse ρ ≤ 0.33, partial 0.33–0.72, content ρ > 0.72. Read
the **bootstrap CI**, not the point estimate, against the two AUROC lines the script prints:

1. **AUTHORSHIP** — CI upper below the collapse line. Use the collapse sentence, `notes/06` §4.4.
2. **CONTENT** — CI lower above the content line. Content sentence; the title changes.
3. **PARTIAL, stable** — the whole CI inside the partial band. Partial sentence, ρ with interval.
4. **INCONCLUSIVE** — the CI spans a line. State the interval, do not round it to a verdict;
   the inconclusive sentence already carries the 2%-yield measurement.

The six paste-ready sentences (collapse, partial, partial-stable, content, inconclusive,
did-not-land) are verbatim in `notes/06` §4.4 and §5.3; fill in the measured value, its bootstrap
CI, n and ρ, and change nothing else. If neither (a) nor (c) is readable, the did-not-land
paragraph goes in unchanged.
**Route only where (a) and (c) agree**; if they disagree, report both and take the inconclusive
sentence.

## 4. Two limits to state, not discover

**Underfitting.** At n = 125 each training fold sees ~200 documents against 2,310 at n = 1,444, and
`min_df=3` keeps a fraction of the vocabulary, so a low S is confounded with sample size until B is
measured at the same n through the same code — the learning curve. If B at S's n is still near
0.85, a low S is a real collapse; if B itself falls toward 0.75, the bands were set at a size the
arm never had and the honest denominator is the problem-matched B′. Quote the curve's
`paper_sentence` beside S.

**S ≈ 0.55 is not distinguishable from chance at any affordable n.** Under a correct CI,
P(declare collapse | true S = 0.55) is 0.27 at n = 125, 0.41 at 200, 0.71 at 400. An interval that
excludes the content line but includes the collapse line is consistent both with a full collapse
and with a small real content effect; the inconclusive sentence must say so. This is also why a
top-up to n = 400 is not worth buying.

## 5. The inert-inclusive B′

`--eligibility passes` admits same-generator attacks that never fire, while B′ from
`data._pick_backdoor` is all-firing. Comparing them is inert-inclusive against
all-firing, in a direction not known in advance. **For the `passes` headline the like-for-like
comparison is B′ computed with the stored inert backdoors included over the same problems** —
`--bprime-inert`, which selects `backdoors` entries on `passes_tests` alone. Keep it OFF for
`--eligibility usable`, whose analogue is the all-firing B′. Say in the paper which rule each row
used; `b_prime_attack_rule` records it. `gate_s_learning_curve.py --match-problems` restricts the *B
pool*, which is all-firing by construction, so its `b_on_s_problems` row is the all-firing
comparator; the script prints that caveat.

Framing for the paper, which is what makes (a) land: 80.7% of the benchmark's labelled backdoors do
not fire and the classifier scores 0.955 on them, so our attack class is defined the same way the
benchmark's is — by intent plus test-passing, not by success.
