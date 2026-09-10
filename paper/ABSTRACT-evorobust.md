# EvoRobust abstract — for the 4-page paper, due 2026-09-12 AoE

**EvoRobust has no abstract registration.** The abstract exists only inside the submitted PDF, so it
is editable by definition until the paper deadline — you replace the whole submission. Written
deliberately soft: **Gate S has not run**, and nothing below commits us to either routing.

Write for the reader `notes/01` describes: robustness- and adversarial-robustness-literate, *not*
AI-control natives. A benchmark-validity result reads to them as **your evaluation measures the
wrong thing**.

---

## Version A — soft, route-agnostic. Use this until Gate S returns.

> Trusted monitoring in AI control is evaluated on stored honest/attack pairs. The field already
> knows these pairs leak: it filters to working solutions, strips comments, and states why. We ask
> what that preprocessing leaves behind. On the field's own filtered, comment-stripped split, a
> bag-of-words classifier scores above roughly four-fifths of the open-weight monitors ranked on that
> same split, and a classifier that reads no code at all — only problem metadata — scores above most
> of them as well. We trace the residue to authorship rather than sabotage: the honest class is
> human-written while every attack is model-written. The signal transfers almost unchanged across
> backdoor generators, is as strong on inert backdoors as on working ones, and survives the field's
> own comment stripper in the form of author bylines left inside string literals. Five same-generator
> agentic settings, where no authorship confound is possible, carry a second and structural floor
> ranging from chance to strongly leaky. We regenerate the honest class with a local open-weight
> coder model as a same-generator control, and recommend that stored-pair monitor evaluations report
> partial-input and bag-of-words floors against permutation nulls, use same-generator honest samples,
> and drop inert backdoors from both classes.

**~210 words. No hard number appears, and every claim is true under either Gate S outcome.**

## Version B — the numbers, to swap in once Gate S returns

Replace sentences 3–4 of Version A with:

> On the field's own filtered, comment-stripped split, a bag-of-words classifier reaches AUROC 0.806
> and a classifier that reads no code at all reaches 0.772, against 24 open-weight monitors ranked on
> that same split at a median of 0.609.

and sentence 6 with:

> The signal transfers across backdoor generators at 0.994 pairwise, is as strong on inert backdoors
> (0.955) as on working ones (0.979), and author bylines survive the field's own comment stripper in
> 23 of 1,209 honest samples against 2 of 1,209 attack samples.

### ⚠️ Two number rules that must survive editing

1. **Never pair 0.772 with "above 18 of 24."** 0.7715 (5×5 CV within the test split) clears **20** of
   24; 0.7163 (single held-out slice) clears **18**. Crossing them is R18's companion error and it
   already reached this repo once (`fig/CAPTIONS.md`).
2. **Pairwise accuracies get three decimals.** 0.962, 0.979, 0.955, 0.994 — the resolution over
   ~2,600 pairs is 1/2,600, so a fourth decimal is one pair (`experiments/REPRODUCED.md`).

## The Gate S sentence, three ways

| Situation | Sentence |
|---|---|
| Collapse (ρ ≤ 0.33) | "Regenerating the honest class with a local coder model removes the signal." |
| Partial / no collapse | "Regenerating the honest class with a local coder model leaves *X* of it intact." |
| **Gate S does not run** | Drop the control sentence entirely. The authorship reading then rests on transfer, inert backdoors, style markers and the five same-generator settings — **stated as inference in Limitations**, in those words (`PLAN.md` §3, route 4). |

Version A's control sentence — *"We regenerate the honest class … as a same-generator control"* —
describes the method, not the result, so it survives the first two rows unchanged. **It does not
survive row three**; if Gate S does not run, that sentence has to go.

## Title

The EvoRobust title is not locked by anything and can be decided on Sep 12. Route-agnostic option,
**What Survives the Filter? Trivial Baselines on Stored Honest/Attack Pairs
in AI-Control Monitoring**. If Gate S collapses, *Authorship, Not Sabotage* is stronger.
