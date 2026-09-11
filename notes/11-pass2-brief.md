# Pass 2 brief: what §13–15 do to the paper (coordinator, 2026-09-12 00:40 UTC)

Numbers are quoted from RESULTS.md §13–15 as reported by their workers; `notes/10-ledger-recheck.md`
(pending) is the verified macro block and wins on any disagreement. The Haiku strict row (§15.8)
is in flight; the sentences below are written so it can be added as one clause or omitted.

## The decomposition the paper now carries

| generator | S (same-gen, `first`/passes) | B′ same problems | ρ (joint CI) | S with the prompt matched too | prompt-only floor (honest vs matched honest) |
|---|---|---|---|---|---|
| Sonnet 5 | 0.751 (n 623) | 0.866 | 0.687 (0.625–0.755) | 0.642 (n 586), ρ 0.394 (0.326–0.454) | 0.601 (0.577–0.624) |
| Haiku 4.5 | 0.534 (n 611) | 0.858 | 0.095 (0.044–0.150) | 0.540 (n 562), ρ 0.113 | 0.492 (0.472–0.513) |

Strict (pass AND fire, Sonnet only, n 99 / matched 96): S 0.765, ρ 0.921 fold-mean / 0.86 pooled
(0.662–1.089); matched 0.711, ρ 0.697 (0.494–0.856). Haiku strict refused at 35 < 50 usable.

Monitors (zero-shot trusted-monitor prompt, same problems):

| row | monitor | same-gen pairs | stored pairs | monitor-ρ |
|---|---|---|---|---|
| headline 623 | Sonnet 5 (wrote both) | 0.566 | 0.958 | 0.145 (0.111–0.182) |
| headline 623 | Haiku 4.5 (wrote neither; a bound, truncation) | 0.558 | 0.882 | 0.151 (0.063–0.242) |
| strict 99 | Sonnet 5 | 0.818 | 0.944 | 0.717 (0.601–0.832) |
| strict 99 | Haiku 4.5 | 0.787 | 0.883 | 0.749 (0.514–0.993) |

## The reading (state it in this order; do not go beyond it)

1. With one model writing both classes the bag-of-words floor falls from ~0.86 to 0.75 (Sonnet 5)
   or 0.53 (Haiku 4.5): authorship is the whole story for one generator and about a third of it for
   the other. Two generators, two bands; say both, never average them.
2. The Sonnet residue is mostly the attack prompt's framing, not the backdoor: matching the prompt
   takes S to 0.64 (ρ 0.39, content band excluded), and two *correct* honest classes from one model
   under the two prompts already separate at 0.60. For Haiku the prompt floor is at chance and
   nothing survives.
3. On attacks that pass and fire (the row that obeys our Recommendation 3; n = 99, low power) the
   residue survives prompt matching (0.71, ρ 0.70) and a monitor reads it (0.82 vs 0.57 on the
   headline set): real backdoors from the same author carry surface signal, and it is the signal a
   monitor also reads. So content in the classifier's sense exists only where sabotage exists.
4. Monitors are inflated by authorship at least as much as the classifier: the same prompt scores
   0.96 / 0.88 on the stored pairs over the same problems and keeps 15% (headline) to 72–75%
   (firing backdoors) of that separability when authorship is held constant; a weaker monitor that
   wrote neither class agrees. This is the sentence the workshop's audience needs.
5. Caveat carried in Limitations: the stored attacker and the same-generator attacker differ in
   backdoor style as well as authorship, so every ρ (classifier or monitor) is an upper bound on
   the authorship share only in the direction "at most this much is content"; and the Haiku
   comparison exists on the `passes` eligibility only.

## Text changes (each within the 13.5-line slack; measure after each)

- **Abstract**, replace from "Holding authorship constant by construction" to the end of that
  sentence with: "Holding authorship constant by construction, with one model writing both
  classes, removes between a third (Claude Sonnet 5, $\rho = \sameGenRho$) and nine-tenths (Claude
  Haiku 4.5, $\rho = \haikuRho$) of the separability; matching the attack prompt's framing removes
  most of what remains, and what survives on attacks that actually fire is surface content a
  monitor also reads. A zero-shot trusted monitor is inflated the same way, scoring
  \monStoredHead{} on the stored pairs and \monitorStrict{} on firing backdoors from the same
  author." Keep the recommendations sentence; add "and the same prompt" to "use same-generator
  honest samples".
- **§1 contribution (ii)**: "a same-generator control on two generators, attributing between a
  third and nine-tenths of the separability to authorship and most of the remainder to the attack
  prompt's framing, with a negative result on the way: regenerating one half of a stored pair
  swaps the confound rather than removing it".
- **§3 Gate S paragraph**: replace the sentence "The arm holds the model constant, not the prompt,
  so $\rho$ is an upper bound on content." with the §13 sentence (branch 1 of notes/09 §4) and add
  the Haiku clause after the first ρ; replace the monitor sentence with one carrying the stored
  0.958 / 0.882 and monitor-ρ 0.717 (0.601–0.832) beside the classifier's. Keep "at low power" on
  the strict row.
- **Recommendation 1**: "Generate both classes with the same model \textbf{and the same prompt
  framing}".
- **Limitations**, second paragraph: one clause for caveat 5.
- **Appendix `app:robust`**: the §13 masking/char rows, the Haiku similarity-stratified check
  (S 0.47–0.51 in every similarity stratum while B′ holds 0.79–0.85), the Haiku headline monitor
  truncation note, and the Sonnet-vs-Haiku pass/fire funnel (0.770 / 0.728 honest pass; 2.5% /
  2.4% fire-given-pass; 52% of triggers are public test inputs, TRIGGER-YIELD.md).
- **Title stays** "What Survives the Filter?". The answer the paper now gives: authorship, the
  attack prompt's framing, and on firing backdoors a residue that is sabotage a monitor reads.
