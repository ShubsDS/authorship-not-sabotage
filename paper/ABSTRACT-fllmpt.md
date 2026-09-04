# FLLMPT abstract registration — due 2026-09-05, 23:00 GMT

**What actually locks on Sep 5 is the author list**, not the title: NeurIPS policy, which FLLMPT
mirrors, freezes author names at the abstract deadline and says nothing about titles, and OpenReview
permits editing title and abstract until the Sep 12 paper deadline (`../notes/01`). Gate S runs Sep 8
and can still rename the paper. The title below is route-agnostic anyway, because that costs nothing.

- [ ] Every author entered in the OpenReview submission form
- [ ] Every author has an up-to-date OpenReview profile
- [ ] Title + abstract pasted
- [ ] Concurrent EvoRobust submission disclosed (their form asks)

---

## Title

> **What Survives the Filter? Trivial Baselines on Stored Honest/Attack Pairs in AI-Control Monitoring**

Route-agnostic by construction. If Gate S collapses, what survives the filter is authorship; if it
does not, what survives is content. The title is the question, and both answers fit under it, so it
holds whichever way Sep 8 goes.

Alternates, if a shorter one is wanted: *Trivial Baselines on Stored Honest/Attack Pairs* ·
*What the Preprocessing Leaves Behind*.

## Abstract — 150 words

> Trusted-monitor evaluations in AI control train, select and rank monitors on stored honest/attack
> pairs. The field already filters these pairs — working solutions only, comments stripped — and
> states why. We quantify what the filtering leaves behind. On the field's own filtered,
> comment-stripped split, a bag-of-words classifier reaches AUROC 0.806 and a classifier reading no
> code at all reaches 0.772, against 24 open-weight monitors ranked on that split at median 0.609. The signal transfers across backdoor generators at 0.9935 and is as strong on inert
> backdoors (0.954) as on working ones (0.979), so it is not detecting sabotage. We trace it to a
> mismatch between construction and deployment: the honest class is human-written and every attack is
> model-written, whereas a deployed untrusted model writes both. We report a same-generator control
> that regenerates the honest class with a local coder model, and recommend partial-input and
> bag-of-words floors beside every reported monitor number.

**Every number in it is computed and in `../experiments/RECOMPUTE.md`** except the same-generator
control, which is Gate S. The last two sentences describe the paper as it will be on Sep 12; if Gate
S does not run, the fourth route in `../PLAN.md` §3 applies and that sentence becomes the inference
statement in Limitations.

## Why this framing for this venue

FLLMPT's CFP names *"safety-critical settings"* and its motivation cites the International AI Safety
Report on *"robustness under task evolution, unintended regressions, and the limits of safe
adaptation."* Monitor training and selection **are** post-training procedures, and this result is a
distribution-shift result about them: a monitor selected on a corpus whose honest class was written
by humans was selected under a distribution that does not obtain at deployment. Lead with that, not
with the benchmark-audit framing used for EvoRobust — the dual-submission clause explicitly asks for
work *"updated or recontextualised for the workshop audience."*
