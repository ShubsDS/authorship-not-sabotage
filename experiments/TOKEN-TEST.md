# The AICD token test — run 2026-09-04. **It came back negative.**

> Standing report. `apps/token_test.py` reproduces every number here.

`PLAN.md` scheduled this as *"the cheapest strengthening available… it converts a **borrowed**
mechanism into a **tested** one in our own setting."* It ran, and it does not. The mechanism stays
borrowed, and the paper says so.

---

## What was tested

AICD Bench (`2602.02079`) App. D.1, quoted in `../lit/01-verified-bibliography.md` §4:

> *"AI-generated code often uses verbose, prompt-echoing identifiers like `answer`, `output`,
> `result`, `tests`, and `index`. In contrast, human-written code tended to use shorter, organic
> identifiers like `li`, `nums`, `pos`, `a1`, and `cur`."*

Those ten tokens were named in **their** paper, before this test, which is what makes it
confirmatory. Our attack class is LLM-written and our honest class is human-written, so the
prediction was directional: AICD's LLM identifiers should push toward **attack**, AICD's human
identifiers toward **honest**.

Setup: Koran's paired train split (2,418 samples / 1,209 problems), comments stripped with the
field's own stripper, TF-IDF word 1–2gram + LR — the same pipeline as `koran_split_eval.py`.
Restricted to the 1,453 identifier unigrams of the 13,799-feature vocabulary.

## Result

| token | AICD says | coef | percentile | got | |
|---|---|---|---|---|---|
| `answer` | attack | −0.0702 | 0.366 | honest | ✗ |
| `output` | attack | +0.3267 | 0.846 | attack | ✓ |
| `result` | attack | +1.0150 | 0.977 | attack | ✓ |
| `tests` | attack | — | not in vocab | | |
| `index` | attack | +0.3686 | 0.866 | attack | ✓ |
| `li` | honest | +0.3406 | 0.853 | attack | ✗ |
| `nums` | honest | +1.6972 | 0.992 | attack | ✗ |
| `pos` | honest | −0.1218 | 0.300 | honest | ✓ |
| `a1` | honest | — | not in vocab | | |
| `cur` | honest | +0.7955 | 0.959 | attack | ✗ |

Mean percentile: AICD-LLM **0.764** vs AICD-human **0.776**, separation **−0.013** — the wrong sign.
Permutation null over 10,000 random token pairings of the same sizes: mean −0.001, sd 0.205,
**two-sided p = 0.956**.

**The failure is not the LLM half.** Three of four testable LLM identifiers land where AICD predicts.
It is the human half: `li`, `nums` and `cur` — AICD's canonical *human* identifiers — are among the
strongest **attack**-pushing features we have.

## Why, and it is the interesting part

AICD's human class is general-purpose GitHub code. **Ours is competitive-programming code, and so is
the LLM's.** `nums`, `cur`, `li` are competitive-programming idiom, and `claude-3-7-sonnet` writing a
solution to an APPS problem writes competitive-programming idiom too. AICD's naming-style axis
separates *general* human code from LLM code; it does not separate these two populations, because
both are writing in the same narrow register.

What does separate them here is **structural**, not lexical:

| marker | honest | attack |
|---|---|---|
| `__main__` / `__name__` | **1 / 1,209** | **152 / 1,209** |

which replicates `RECOMPUTE.md`'s style-marker result (`has_main` 0.000 vs 0.116) on the Koran train
split.

## The by-product, and it is a real finding

Chasing an odd top feature — `chaotic_iak`, a Codeforces handle — turned up something worth a
sentence in the paper. The field's comment stripper is a port of the anchor's own
`comment_stripper.py` and removes `tokenize.COMMENT` tokens only. **String literals are not comments,
and they survive**:

| surviving in comment-*stripped* code | honest | attack |
|---|---|---|
| an author byline (`Author :`) | **23 / 1,209** | 2 / 1,209 |
| a triple-quoted block | **43 / 1,209** | 9 / 1,209 |
| a competitive-programming site name | **23 / 1,209** | 2 / 1,209 |

Human competitive-programming code stashes sample input in triple-quoted strings and signs itself;
LLM code does neither, at 4.7× the rate. One of the surviving blocks is base64-encoded zlib. This is
small — 1.9% of the honest class — so it is not what drives 0.806. **But it is a literal authorship
leak surviving the field's own published preprocessing**, and it belongs in §3 next to the
`0.4726 → 0.806` contrast as one more thing the fix does not reach.

## What changes in the paper

1. **§3 goes back to "authorship, three ways"** — transfer 0.9935, inert 0.954 vs working 0.979,
   style markers. Not four.
2. **Report this negative in one sentence**, with the register explanation. A reviewer who knows AICD
   may try exactly this test; better that we ran it and said so.
3. **Add the surviving-string-literal row.** It is new, it is ours, and it is cheap.
4. ⚠️ **Power.** Only 8 of the 10 tokens are in vocabulary, so the test is underpowered and a null
   result alone would prove little. What makes it informative is that the point estimate has the
   **wrong sign** and three of four human-side tokens load hard the wrong way — that is not what an
   underpowered version of a true effect looks like. Say both parts.
