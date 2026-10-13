# Response to reviewer 3sdp (draft)

Draft for the OpenReview camera-ready response. It follows the six weaknesses as summarised in
`camera-ready-plan.md`; check the wording against the review itself before posting. Numbers are
the camera-ready values, each from a committed script (`experiments/README.md`, "Where each
result comes from").

We thank the reviewer. We checked each of the six points against the paper and the committed
result files. All six are valid, and two were worse than stated. The camera-ready corrects them
as follows.

**1. The abstract did not state the problem, method, why the method works, or the insight.**
We rewrote it in that order. It also had three errors, now removed:
- It called the no-code floor an authorship difference, although that classifier reads only
  problem metadata.
- It said prompt matching "removes most of the rest". It does on Sonnet 5 (ρ 0.687 → 0.390) and
  not on Haiku 4.5 (0.097 → 0.110).
- It said the monitor "moves the same way" as the classifier (see point 4).

The new abstract reports the attempt and working-attack rows side by side and says what ρ is not.

**2. The headline sets are mostly failed attacks.** Agreed, and it is worse than stated:
- Only 14 of 623 (Sonnet 5) and 2 of 611 (Haiku 4.5) headline attacks fire, while every stored
  attack on those problems fires.
- Our sentence saying B′ "includes inert attacks" was false. The headline rows compared working
  stored backdoors against mostly inert attempts.

Table 2 now has a fires column and groups the rows into attempts and working sabotage. The text
says what the headline rows compare.

**3. Authorship is not isolated.** Agreed:
- Against the same human code, the stored attacking model alone moves the bag-of-words AUROC
  from 0.75 to 0.93. So ρ is neither the backdoor's share of the separability nor a bound on it.
  We removed "bound" and the sentence saying the independent arm changes "the writer and nothing
  else".
- ρ does not depend on which stored model attacked: with Claude attackers only it is 0.715,
  against 0.687 for the full mix.
- We ran the experiment that isolates authorship for the classifier: fit it to every pairing
  of an honest and an attack class (Table 3, appendix). We fixed the reading rule before
  computing the missing cell. On Sonnet 5's headline problems:
  - human honest code against our attacks scores 0.981, above B′ = 0.865;
  - our honest code against stored attacks scores 0.956;
  - only the pairing in which one model wrote both classes falls, to S = 0.750.

  Haiku 4.5 gives 0.973 and 0.966 against S = 0.534. So for the classifier the drop is
  authorship, not our attacks: our attacks are easier, not harder, to separate from human code.
  For the monitor it is the reverse (point 4).

**4. Verified attacks qualify the result.**
- **Monitor.** Valid, and it changes our claim. Swapping one class at a time (Table 3), the
  Sonnet 5 monitor scores:
  - 0.958 for human honest against stored attacks;
  - 0.446 for human honest against our attacks;
  - 0.974 for our honest against stored attacks.

  Its mean suspicion is 6.6 for our attacks and 78.8 for stored ones. The monitor's drop is in
  the attacks, not in authorship: it measures how conspicuous the attacks are. This holds on
  working attacks too: human honest against our strict attacks scores 0.755. The submission's
  "the monitor moves the same way" is withdrawn.
- **Classifier.** Partly valid. On the 64 problems in both the headline and the strict sets, ρ
  is about the same with headline and with working attacks: 0.815 against 0.749, paired 95% CI
  on the difference −0.243 to +0.131. So the attacks working do not raise ρ. By point estimate,
  the strict row's higher ρ comes from which problems yield working attacks: on the strict set's
  35 other problems ρ is 1.09 (S 0.775, B′ 0.752). That difference from the shared problems is
  not resolved (+0.34, CI −0.13 to +0.93), and the paper says so. The new appendix section shows
  this decomposition.

**5. Statistical inconsistencies.** Agreed. Points were fold means while their intervals were
bootstraps of the pooled out-of-fold scores, and we wrongly called these "the same quantity".
The appendix now states one convention:
- Every point is the pooled out-of-fold AUROC, and every interval is the bootstrap over problems
  of that same quantity (joint for ρ).
- Every permutation null is 1,000 permutations that shuffle the labels for fitting and scoring
  alike.
- The agentic nulls (Figure F2) are within-task permutations of the plotted statistic.

No conclusion changes. The strict ρ moves from 0.921 to 0.861. The held-out no-code null moves
from 0.702 to 0.558 (p = 0.001), so that row is no longer "barely above its null".

We also ran the no-code floor under the bag-of-words protocol: trained on problems outside the
test split and scored once, it scores 0.298, below chance. Outside the split, every problem that
passes the filter has a working backdoor, so the relation between test count and label
reverses. The paper now leads with that value. It reports the within-split 0.766 as a measure of
how the split's filter selects the label, not as authorship.

**6. Repetition, and no fixed audit budget.** We cut the repeated numbers and verdict words and
replaced the band labels with P(ρ > 0.72). We now report detection at a fixed audit budget. At a
2% false-positive rate, with the threshold set on each set's own honest programs, the Sonnet 5
monitor catches:
- on the 99 strict problems: 77% of stored attacks and 48% of same-generator ones (paired
  difference 0.28, 95% CI 0.15–0.42);
- on headline pairs: 85% and 6%.

The appendix gives the full table at 1%, 2% and 5% for both monitors.
