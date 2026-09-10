# Gate S — results ledger

Every number here was produced by a script in `apps/` and is reproducible from the command shown.
Nothing in this file is an estimate, a projection, or a number carried over from a plan document.
When a run supersedes an earlier one, the earlier row stays and is marked, because a superseded
result is evidence about the protocol even when it is not evidence about the question.

**Reading the ledger.** Gate S asks whether the stored benchmark's separability is *authorship*
(who wrote the code) or *content* (the sabotage itself). Each arm removes a different part of the
authorship gap and reports what survives.

---

## 1. The pool

`apps/gate_s_pool.py` → `gate_s_pool.parquet`. Measured on the full artifact, re-verified on a
second machine 2026-09-09; every count exact.

| Cut | n | What it removes |
|---|---:|---|
| APPS problems in the artifact | 5,000 | — |
| ∧ `solution_passes_tests` | 3,420 | no working honest reference exists |
| ∧ `backdoor_works` | 1,582 | no working stored backdoor to pair against |
| ∧ deterministic | **1,444** | exact-match scoring is meaningless on these |

**1,444 is the analysis ceiling.** The realised n of any arm is 1,444 × that arm's pass rate. The
paper must state this; a reader must not be left to infer 3,420.

Composition of the 1,444: 1,061 interview, 277 introductory, 106 competition. Median 18 test
cases per problem, max 223.

---

## 2. B — the baseline Gate S routes against

What a deliberately trivial classifier (TF-IDF bag-of-words, logistic regression, problem-disjoint
5-fold CV, comments stripped from both classes) achieves on the benchmark **as shipped**: human
honest code vs `claude-3-7-sonnet-thinking` backdoors.

```
python gate_s_baseline.py          # CPU only, no GPU required
```

| Carrier | AUROC |
|---|---:|
| **TF-IDF (the headline)** | **0.8714 ± 0.0085** |
| pairwise accuracy | 0.9605 |
| length alone | 0.6081 |
| surface-7 features | 0.7673 |

n = 1,444. sklearn 1.9.0, pandas 3.0.5.

A bag-of-words model separates the two classes at 0.87 without being told anything about program
semantics. That is the number the paper is about: it is far too high for a benchmark whose classes
are supposed to differ only by a subtle logic bug.

### Routing thresholds, fixed before any arm ran

Derived from B, so no arm can move the goalposts after the fact:

| Band | ρ = (G − 0.5)/(B − 0.5) | AUROC of G | Reading |
|---|---|---|---|
| collapse | ≤ 0.33 | ≤ 0.6226 | separability was authorship |
| partial | 0.33 – 0.72 | 0.6226 – 0.7674 | mixed |
| content | > 0.72 | > 0.7674 | separability is the sabotage |
| **confounded** | **> 1.0** | — | G exceeds B; the substitute generator added more gap than it removed |

The `confounded` band was added after arm 1 produced ρ > 1, a case the original three bands could
not express. It is a guard, not a result.

---

## 3. Arm 1 — regenerate the honest half only (Qwen3-Coder-30B)

```
python gen_honest.py --model Qwen/Qwen3-Coder-30B-A3B-Instruct ...
python gate_s_eval.py --arm q3c30
```

Replaces human honest code with an open-weight model's, keeping the stored Claude backdoors.

| Quantity | Value |
|---|---:|
| n pairs | 668 |
| B′ (same problems) | 0.8739 ± 0.0160 |
| **G** | **0.9616 ± 0.0090** |
| **ρ** | **1.2344** |
| excess over B′ | **+4.78 sd** |

Per-carrier movement, B′ → G:

| Carrier | B′ | G | Δ |
|---|---:|---:|---:|
| TF-IDF | 0.8739 | 0.9616 | **+0.0877** |
| length alone | 0.6528 | 0.4885 | **−0.1642** |
| surface-7 | 0.8026 | 0.8091 | +0.0065 |

**Verdict: CONFOUNDED — do not route a title on this arm.** Separation got *worse*, not better.
Swapping the honest author replaced a human-vs-Claude gap with a larger Qwen-vs-Claude one. The
length carrier collapsing to chance (0.4885) while TF-IDF *rose* is the signature: the new gap is
lexical, not structural — vocabulary and idiom, not program length.

This is a null result about the *method*, and it is why the same-generator arm exists. Regenerating
one half of a pair cannot isolate content, because it swaps the confound instead of removing it.

---

## 4. Arm 2 — one generator writes both classes (Claude Sonnet 5)

The only configuration in which authorship is held constant **by construction**. Whatever a
bag-of-words classifier can still separate must then be sabotage content, because nothing else
differs.

> ⚠️ **Not the original attacker.** `claude-3-7-sonnet-20250219` wrote the stored backdoors and
> reached end-of-life 2026-02-19; called against a live key on 2026-09-09 it returns **404**. This
> arm is same-vendor and same-lineage but a *later generation*. It must be described that way in
> Limitations — it is not a same-model control.

### 4.1 Honest class — generated, landed 2026-09-09

```
python gen_honest_api.py --out gen_sonnet5.jsonl        # --pool analysis (default)
```

| Quantity | Value |
|---|---:|
| requests submitted | 1,444 |
| **succeeded** | **1,444 (100%)** |
| errored | 0 |
| batch wall-clock | 304.6 min |
| input tokens | 0.99 M |
| output tokens | 1.53 M |
| **actual cost** | **$8.62** |

Output-length distribution — the reason cost is hard to predict here:

| Statistic | Output tokens |
|---|---:|
| mean | 1,057 |
| median | 289 |
| p90 | 3,335 |
| max (= cap) | 4,096 |

Heavily right-skewed: a typical solution is short, but a long tail runs into the cap.

| Outcome | n | Share |
|---|---:|---:|
| truncated at `max_tokens=4096` | 113 | 7.8% |
| no extractable code block | 82 | 5.7% |
| — of which truncated | 82 | **100%** |
| — lost code for any other reason | **0** | 0% |
| **usable (code extracted)** | **1,362** | **94.3%** |

**Extraction is not a failure mode.** Every non-truncated reply yielded a parseable code block; all
82 losses are the token cap. The 31 replies that truncated *but still* produced a partial block are
left in and allowed to fail the tests, per the protocol rule that truncations are counted and
dropped as failures rather than silently discarded.

### 4.2 Cost estimation — a correction worth recording

The pre-run estimate assumed 600 output tokens per solution and predicted $5.00. Actual was 1,057,
so the arm came in **72% over estimate**. This is the second time this assumption has been wrong in
this project: the same class of guess set `max_tokens=2048` on the first Qwen arm and truncated 34%
of it.

The consequence was contained only because generation was restricted to the analysis pool. On the
full 5,000 rows the honest arm alone would have been ~$30 actual, with a worst case of **$102** —
over the project's $100 ceiling before a single backdoor. `estimate()` now prints the worst case
next to the point estimate, because the worst case is the number a budget ceiling has to survive.

| Scope | Estimated | Worst case | Actual |
|---|---:|---:|---:|
| all 5,000 (as originally coded) | $17.00 | $102.00 | not run |
| **1,444 analysis pool (as run)** | **$5.00** | **$30.24** | **$8.62** |

### 4.3 Honest class — test execution

```
python run_tests.py --solutions gen_sonnet5.jsonl --out pass_sonnet5.jsonl --workers 8
```

**1,112 of 1,444 pass — 77.01%.** 1,444 solutions in 152.7 s.

| Failure reason | n |
|---|---:|
| mismatch | 293 |
| timeout | 17 |
| compile: SyntaxError | 13 |
| raised: ValueError | 3 |
| raised: IndexError | 2 |
| raised: NameError | 2 |
| raised: TypeError | 1 |
| budget exceeded or died | 1 |
| **passed** | **1,112** |

Pass rate splits sharply on whether generation was truncated, which is why truncation is counted
rather than ignored:

| Generation outcome | n | passed | rate |
|---|---:|---:|---:|
| clean (not truncated) | 1,331 | — | — |
| truncated, partial code kept | 31 | — | — |
| truncated, no code | 82 | 0 | 0.0000 |

(Split measured on the pre-fix run; the group sizes are unchanged by the fix in §4.4.)

---

## 4.4 A harness artifact found mid-run, and why it mattered

The first execution of the honest class returned **1,062 / 1,444 (73.55%)** with a conspicuous
cluster of **61 `AttributeError`s**, every one failing at case 0 in ~0.1 s — before the program
could compute anything.

**Cause.** `run_tests.py` patched stdin with `io.StringIO`, which has no `.buffer` attribute. Any
solution using `sys.stdin.buffer.read()` — a standard competitive-programming fast-I/O idiom —
raised `AttributeError` immediately, whatever it would have computed. `sys.stdout.buffer.write()`
had the same defect.

**Fix.** Wrap real byte buffers: `io.TextIOWrapper(io.BytesIO(...))` exposes `.buffer` natively, so
the text and binary paths both work.

| | before | after |
|---|---:|---:|
| passed | 1,062 (73.55%) | **1,112 (77.01%)** |
| `raised: AttributeError` | 61 | **0** |
| fail → pass | — | **50** |
| **pass → fail (regressions)** | — | **0** |

The 11 ex-`AttributeError` solutions that still fail now report a real diagnosis (9 mismatch,
1 IndexError, 1 TypeError) instead of having it masked.

### Why this was not a routine bug

The idiom is **class-correlated**, so the artifact was invisible on the benchmark as shipped and
became load-bearing only once a generator that writes this way was introduced:

| Class | uses `std{in,out}.buffer` | rate |
|---|---:|---:|
| human honest (the B class) | 2 / 3,420 | 0.06% |
| stored `claude-3-7` backdoors | 0 / 1,582 | 0.00% |
| **Claude Sonnet 5 honest** | **61 / 1,362** | **4.48%** |

Two consequences:

1. **B = 0.8714 is unaffected and is not recomputed.** The bug touches 2 human solutions and zero
   backdoors — far below its ±0.0085 standard deviation.
2. **It would have biased arm 2 in the worst possible direction.** The 61 are not a random 4.5% of
   the honest class; they are exactly its fast-I/O stylistic subgroup. Silently dropping them would
   have reshaped the honest class's style distribution along the same lexical axis the TF-IDF
   classifier reads — a methodology artifact manufacturing a result, which is the failure mode this
   paper exists to document. The paper would have been produced by the bug it is about.

The idiom gap is also a finding in its own right: Sonnet 5 uses this construction **~75× more often
than human APPS authors do**. That is a concrete instance of the lexical authorship channel arm 1
detected as a +0.0877 TF-IDF rise against a length carrier collapsing to chance.

> **Rule this earns.** A pass/fail harness must be validated against *each* class it will score, not
> only against the one it was written for. Agreement with the shipped flag on human code (0.9575)
> said nothing about a generator whose style differs.

---

## 4.6 Harness fidelity re-validated after the fix (2026-09-10)

The §4.4 change touched the I/O plumbing every solution runs through, so the human class it had
previously been validated against had to be re-scored rather than assumed unaffected.

```
python run_tests.py --solutions human --out pass_human_fixed.jsonl --workers 8
```

115,212 solutions in 11,241.9 s (3.1 h). **The run was mis-scoped**: only `solutions[0]` per problem
is ever used downstream, so the population that matters is 3,765, not 115,212. The superset is still
usable — the 3,765 are a subset of it — but the same mis-scoping has now cost time twice.

### Compared on the same protocol, not on the headline

The run's own headline is 0.9193 over 115,212 rows. That is **not** comparable to the 0.9575 on
record, which was measured over 3,765. Nor is a two-sided disagreement count comparable to the
recorded column, which is one-sided (*we fail / they pass*). Both crossings are corrected here:

| population | n | agree (pre-fix) | agree (post-fix) | we fail / they pass |
|---|---:|---:|---:|---:|
| every row with a solution | 3,765 | 0.9575 | **0.9586** | 141 → **137** |
| deterministic rows only | 3,126 | 0.9533 | **0.9543** | 130 → **127** |
| **the analysis pool — what Gate S uses** | **1,444** | **0.9584** | **0.9584** | 60 → **60** |

**The analysis pool is unchanged to four decimal places, with an identical disagreement count.**
The paper's 95.84% harness-fidelity figure survives the fix and is not recomputed. This is what
§4.4's idiom table predicted: 2 human uses in 3,420, so there was almost nothing there to recover.

The harness is also **strictly conservative on the analysis pool** — 60 we-fail/they-pass and
**0 we-pass/they-fail**. It never credits a solution the artifact rejects.

### The residual disagreements are a Python-version artifact, not a harness defect

**This was already known, not newly found.** `GATE-S-RUNBOOK.md` §4.2 recorded "19 `ImportError`
from the pre-3.9 Python gap" on 2026-09-04. What follows confirms that diagnosis at the full scale
and names the exact call; it does not discover it.

Across the full run, `ImportError` accounts for 250 of the we-fail/they-pass rows over 122 problems.
The dominant cause:

```
>>> from fractions import gcd
ImportError: cannot import name 'gcd' from 'fractions'      # Python 3.12.11
```

`fractions.gcd` was removed in Python 3.9. 19 of those 122 problems use it. The artifact's
`solution_passes_tests` was computed on an older interpreter; the code genuinely does not run here,
so this is **correctly** scored as a failure and is not fixed.

It is worth reporting because it is **era-correlated in the opposite direction from §4.4**:

| Artifact | Penalises | Direction |
|---|---|---|
| `StringIO` has no `.buffer` (§4.4, **fixed**) | modern LLM fast-I/O idiom | against the model class |
| `fractions.gcd` removed in 3.9 (**not fixable**) | pre-3.9 human code | against the human class |

Both are interpreter-era effects that fall unevenly on classes written in different eras. Gate S's
same-generator arm is immune — both its classes are modern and from one model — but B is not, and
the paper should say so rather than let a reviewer find it.

## 4.7 B is robust to the pass-flag choice

B was published from the artifact's **shipped** flag because no harness output for the human class
existed yet. It does now, and the runbook specifies our own flag for both classes, so B was
recomputed. A protocol crossing surfaced in the process:

> `build_pairs()` gated eligibility on **our** flag but selected the code with `_honest_code()`,
> which returns the first solution the **artifact** marks passing. A problem could therefore qualify
> because solution #7 passes our harness while the code actually used was solution #0, which our
> harness fails. Measured: **22 of 1,406 pairs, 1.56%**. Selection now uses the same flag that
> gated, which is also how the runbook's recorded 1,384 arises (the stricter `solutions[0]` reading).

| Protocol | n | B | sd |
|---|---:|---:|---:|
| shipped flag — **as published** | 1,444 | **0.8714** | 0.0085 |
| our flag, crossed selection (the bug) | 1,406 | 0.8731 | 0.0102 |
| our flag, consistent selection (**fixed**) | 1,406 | **0.8729** | 0.0107 |

**All three sit inside one standard deviation of each other.** The headline does not depend on which
pass flag is used, nor on the crossing — a reviewer will ask, and the answer is now measured rather
than asserted. `B = 0.8714` is kept as the published value; the alternatives are reported as a
robustness check, not as a replacement.

### The flag comparison was itself nearly a crossed protocol

The two rows above were first computed in **different library environments** — the published value
under sklearn 1.9.0 / pandas 3.0.5 on a second machine, the recomputation under sklearn 1.7.1 /
pandas 2.3.1 here. Comparing them as though they differed only by the pass flag would have repeated
the very error corrected two paragraphs above.

Rerunning the shipped-flag baseline in *this* environment settles it, and the result is stronger
than the check required:

| | sklearn 1.9.0 / pandas 3.0.5 | sklearn 1.7.1 / pandas 2.3.1 |
|---|---:|---:|
| B (TF-IDF) | 0.8714 | **0.8714** |
| sd | 0.0085 | **0.0085** |
| pairwise accuracy | 0.9605 | **0.9605** |
| length-only | 0.6081 | **0.6081** |
| surface-7 | 0.7673 | **0.7673** |
| n | 1,444 | **1,444** |

**Bit-identical across both environments.** So the flag comparison is valid as stated, and B carries
an independent cross-environment reproduction on top — two machines, two library generations, every
carrier the same to four decimals. That is a stronger reproducibility claim than the paper currently
makes, and it costs nothing to state.

---

### 4.8 Remaining stages

| Stage | Status |
|---|---|
| honest generation | ✅ done — §4.1 |
| honest test execution | ✅ done — §4.3, §4.4 |
| backdoor generation | ⏳ in flight — `msgbatch_01LCpHv4vQaEs85xTBkJ9qUE`, 1,112 requests |
| harness re-validation vs shipped flag | ⏳ running |
| backdoor verification | pending |
| same-generator evaluation (S) | pending |

---

## 5. What is not yet answered

Gate S has **not** been settled. Arm 1 is confounded and arm 2 is incomplete. No title claim is
routed on anything in this file yet. `gate_s_samegen.py` reads S through a ±2sd interval and refuses
to collapse an inconclusive interval into a verdict:

- authorship if the interval's **upper** bound < 0.60
- content if its **lower** bound > 0.75
- otherwise state the interval, do not round it
