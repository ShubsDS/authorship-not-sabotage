# Four pages, section by section, with the number that goes in each

NeurIPS template, 4 pp body. Written Sep 10–11. **Every sentence in the abstract has a number behind
it in a table** (A6), and any sentence that does not is cut rather than softened.

Figures are three: **F1** protocol × baseline table, **F2** per-corpus floor bars with permutation
nulls, **F3** monitor-vs-floor dot plot on Koran's 1,375-item split.

---

## §1 Introduction — ¾ page

**Paragraph one credits the field before it says anything else.** This is the condition on which the
novelty claim survives, and it is the paragraph a reviewer from this neighbourhood reads first.

> ### ★ Lead with the validity claim, not with the number
>
> To a reviewer who knows the AI-code-detection literature, *"TF-IDF separates human-written from
> LLM-written code"* is 2025 news — AICD Bench publishes exactly that, at token level, with their SVM
> beating every neural detector. If the paper
> opens on **0.806 beats 20 of 24**, that reader's first thought is *of course it does*.
>
> The contribution is **not** that bag-of-words separates the classes. It is that **a corpus whose two
> classes differ by author is being used to train, select and rank sabotage monitors**, and that nobody
> has quantified what survives the field's own preprocessing. **The known-ness of the mechanism is the
> argument, not a dent in it** — a well-established separability result is exactly what makes the
> benchmark's construction indefensible.

1. Trusted monitoring is evaluated on **stored** honest/attack pairs — `2312.06942`, `2506.05296`,
   `2605.15377`, `2608.16190`, and the reference DSPy tutorial.
2. **The field already knows these pairs leak.** Koran §4.1 filters to working honest + working
   backdoors and strips comments, with the rationale stated. Control Tax §2.3 reports the
   pass-tests pre-filter and appendices *"Monitoring failed backdoors."* Jha names the comment leak,
   ships `--leak-check`, and publishes both numbers: `#`-count detector **0.6957 → 0.4983** after
   stripping, `code_length_only_auroc` **0.4726**. `2602.10153` is a whole paper on the comment channel.
3. **What nobody has measured is what the preprocessing leaves behind.** On the field's own filtered,
   comment-stripped split, TF-IDF reaches **0.806** and a classifier reading **no code** reaches
   **0.772**, against 24 monitors at median 0.609.
4. **The mechanism is authorship.** Honest solutions are human-written (`codeparrot/apps`, no model
   ever called); every backdoor is LLM-written. The signal transfers across generators at **0.9935**
   and is as strong on **inert** backdoors (0.954) as on working ones (0.979) — it is not sabotage.
5. **Adjacent work, distinguished in one sentence each.** `2510.09462` subverts monitors with
   injected text (different axis). `2606.06529` shows attacker-side selection inflates safety
   estimates (same conclusion, other side). `2607.06596` removes transcript length as a nuisance
   covariate; we publish the content-blind classifier's own AUROC as a per-benchmark floor.
6. **The neighbouring field already applies the control that is missing here.** CodeMirage forces its
   LLM-written class to agree with the human class on line count and character length and gates on it (`2506.11059` §3.1); MultiAIGCD pairs to the same CodeNet problem
   definitions (`2507.21693`); AICD Bench filters explicitly *"to prevent detectors from exploiting
   distributional artifacts rather than learning meaningful code patterns"* (`2602.02079` §4.1). **The
   unmatched honest/attack pairs are a defect by the neighbouring field's own published standard**, not
   by one we invented. ⚠️ Cite the mechanism as *established* — AICD App. D.1 already names the tokens
   (`answer`, `output`, `result` vs `li`, `nums`, `pos`) — and claim only the application.
7. Contributions, four bullets. **Scope claim: this concerns monitor training, selection and
   benchmarking on stored pairs — ControlArena's live evals generate both classes.** Say it here,
   not in Limitations, or the first reviewer says it for us.

## §2 Setup — ½ page

- The artifacts, with **licence and per-class provenance** (`lit/01` §6), including the sentence that
  two of the seven declare none and that we redistribute nothing.
- One dataset and one derived copy — not two (K1).
- ★ **Lead §2 with the schema, not with prose.** `backdoors` carries `model` and `source`; `solutions`
  carries only `code`, `compiles`, `passes_tests`. **The attack class records who generated it; the
  honest class has no generator field because it has no generator.** One small table, no measurement,
  and it survives every objection about protocol, metric and split. Everything after it in §3 is
  quantification of a fact already established here.
- Koran's split as the evaluation surface: 1,209 train / **1,375 test (172 attack / 1,203 honest)**,
  label = `backdoor_works`, comments stripped, reconstructed with Jha's own `src/data.py`.
- **Protocols must be named and kept distinct.** Raw artifact vs Koran's filtered split; pooled vs
  matched vs within-task; pairwise accuracy vs AUROC. Every "X above Y" sentence states Y's split,
  Y's metric and Y's preprocessing (R18's companion). This is where the round-16 headline died.
- **AgentHarm excluded, and why** (an invited speaker authored it).

## §3 Results — 1½ pages, the paper's weight

**F1 — protocol × baseline.** Rows: metadata-only under P0–P4 (**P3 matched = 0.5000 exactly**);
length-only (0.8255 raw → **0.4726 filtered**); seven surface features (0.8302); TF-IDF (0.9621
pairwise; **0.806 on Koran's split**, 0.8914 with comments kept); no-code (**0.7163 held-out /
0.7715 ± 0.039**). The **0.4726 → 0.806** contrast *is* the paper: the field's fix works on the
carrier it was aimed at and does not reach the two beside it.

**Authorship, three ways.** Cross-generator transfer 0.9935 (Control Tax → the 2023 GPT-4 set);
working 0.9787 vs inert 0.9543 — *the signal is not sabotage*; style markers (`#` present: attack
0.685 vs honest 0.176; `__main__`: 0.116 vs **0.000**, replicated on Koran's train split at
152/1,209 vs 1/1,209).

> ### ⛔ There was a fourth way. It was tested on 2026-09-04 and it failed.
> The plan was to confirm AICD App. D.1's token-level mechanism in our own setting. It does not
> replicate: separation **−0.013**, the wrong sign, permutation **p = 0.956**. `li`, `nums` and `cur`
> — AICD's canonical *human* identifiers — are among our strongest **attack**-pushing features.
> The reason is register: AICD's human class is general-purpose GitHub code, while **both** of our
> classes are competitive-programming code, so a naming-style axis that separates general human code
> from LLM code does not separate these two populations.
>
> **Report it in one sentence.** A reviewer who knows AICD may run exactly this test; far better that
> we ran it and said so. Note the power caveat honestly — only 8 of 10 tokens are in vocabulary — but
> also note that the point estimate has the wrong sign, which is not what an underpowered true effect
> looks like. Full record: `../experiments/TOKEN-TEST.md`.

**★ New, and it belongs beside the 0.4726 → 0.806 contrast.** The field's comment stripper removes
`tokenize.COMMENT` tokens only — **string literals are not comments and survive it.** In the
comment-stripped train split, an author byline (`Author :`) survives in **23/1,209 honest** vs
**2/1,209 attack** samples, a triple-quoted block in **43 vs 9**, a competitive-programming site name
in **23 vs 2**. Human competitive-programming code stashes sample input in triple-quoted strings and
signs itself; LLM code does neither. It is 1.9% of the honest class, so it is not what drives 0.806 —
but it is a **literal authorship leak surviving the field's own published preprocessing**, and it is
one more thing the fix does not reach.

**Gate S — the constructive half** (`../PLAN.md` §3, run per `../experiments/GATE-S-RUNBOOK.md`).
Regenerate the honest class with an LLM, rebuild the pairs, rerun. The number here routes the title,
and the route was fixed before the run. Report **both generator arms** (Qwen2.5-Coder 7B and 32B) with
their separate n's, the pass rates, and the human-honest baseline **B** computed under the identical
protocol — a reader cannot interpret the collapse without B.

**F3 — the comparison, done honestly.** Against `runs/x0/monitor-summary.json`: TF-IDF **0.806 above
20 of 24**; no-code **0.772 above 18 of 24**; median 0.609, max 0.937. Caveats **in the caption, not
in Limitations**: those 24 are zero-shot prompted while ours is trained on the benchmark's own paired
train split, and the metadata floor is fitted within the test split because their train/val is
paired. **This is a Gururangan-style artifact statement, not a claim that bag-of-words is a better
monitor.**

**The second artifact the filter installs.** The negative class is defined by *attack failure*:
**80.7%** of Koran's test-split labelled backdoors do not work and are relabelled honest, so ~60% of
the "honest" items are failed attacks — and attack problems carry **half** the test cases (20.95 vs
38.85), which is where the no-code floor comes from.

**F2 — the negative control, five same-generator settings.** Within-task, character count only:
bash **0.504** (clean) · shade 0.602 · iac 0.704 · rogue_eval 0.616 · agentdojo **0.802** (leaky),
every bar beside its permutation null (0.48–0.51). Report the **within-task** column and say plainly
that the pooled column was largely task composition and that we broke it ourselves. **Two mechanisms,
one table:** authorship on APPS, structure on the agentic settings.

**One paragraph, not a section:** the 15-word scratchpad regex, 0.76–0.82 across five settings,
crediting `2607.09786` for the instrument.

## §4 Recommendations — ⅓ page

Written as a checklist someone can apply, in Kapoor & Narayanan's register (`2207.07048`):

1. **Use same-generator honest samples.** If the attack class is model-written, the honest class must
   be too. **Precedent, not invention:** `2506.11059` §3.1 matches on line count and character length
   with a rule-based gate and forced regeneration; `2507.21693` pairs to shared problem definitions.
2. **Report a partial-input floor and a bag-of-words floor** beside every monitor number, with a
   permutation null.
3. **Drop inert backdoors from both classes** — do not relabel a failed attack as honest.
4. **State the split, the metric and the preprocessing** whenever monitors are compared.
5. Released: the split definition, the regenerated honest pool, and the scripts.

## §5 Limitations — ⅓ page

- **`1905.05778`, cited against ourselves.** *"The failure of a partial-input baseline does not mean a
  dataset is free of artifacts"* — and its converse binds us: a high floor is evidence about the
  corpus, not proof that every monitor number on it is meaningless.
- Trained-vs-zero-shot asymmetry in F3, restated.
- Two corpora carry no licence; five are one user's repackaging. Provenance is legible inside the
  files, and the title says *"public releases of."*
- If Gate S route 2 did not run: the authorship reading is **inference from transfer, inert-backdoor
  and style evidence plus the five same-generator settings**, and it says so in these words.
- One benchmark family for the authorship mechanism. The generalisation claim is the November paper,
  not this one.
- ⚠️ **Pre-empt the AICD counter-punch, do not wait for rebuttal.** AICD's SVM+TF-IDF scores *below
  random* on their hardest task (43.05 Macro-F1 vs 45.73). A reviewer can wave that as *"bag-of-words is
  weak at this."* It is not comparable — 77 generators, 9 languages, out-of-distribution generalisation,
  and **Macro-F1, not AUROC**. Say so in one sentence. Comparing across protocols is the exact error
  that killed this paper's previous headline (R18's companion); do not commit it in the other direction
  either by quoting their number next to ours.
- **The substitute generator, defended in one line.** The backdoors are `claude-3-7-sonnet-thinking`;
  our honest class is written by a local open-weight model. AICD's cues are language- and
  generator-independent and our own transfer is 0.9935, so what collapses is LLM-ness, not one vendor's
  style. (`PLAN.md` §3.)
- **Why we do not length-match**, deliberately: in deployment the untrusted model chooses its own
  trajectory length, so matching would remove a difference that belongs to the distribution. Stated as a
  design choice, not left as an omission.

---

## Before anything is public

Every pre-publication check is discharged: the AICD/CodeMirage setup reads and all three ⚠️ citations
on 2026-09-03 (`lit/01` §4, §8), G2 for both venues by 2026-09-04 (`notes/01`). **What remains is
Gate S alone** — `../experiments/GATE-S-RUNBOOK.md`.

⚠️ Two things the sweep put on the do-not-write list. **Never compare our AUROC to AICD's Macro-F1** —
their numbers sit below random on their hardest task, they are a different metric on a different
construction, and "X beats Y" across protocols is the error that killed the round-16 headline (R18's
companion). And **cite CodeMirage §3.2 honestly**: its claim that *"naive statistical classifiers would
struggle to detect AI-generated code using basic code features"* is asserted from overlapping
histograms and never tested — it is true of their *matched* construction, which is the point.
