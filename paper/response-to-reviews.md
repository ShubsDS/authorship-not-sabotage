# Response to reviewer 3sdp (draft)

Draft for the OpenReview camera-ready response. It follows the six weaknesses as summarised in
`camera-ready-plan.md`; check the wording against the review itself before posting. Numbers are
the camera-ready values, each from a committed script (`experiments/README.md`, "Where each
result comes from").

We thank the reviewer. We checked each of the six points against the paper and the committed
result files. All six are valid, and two were worse than stated. The camera-ready corrects them
as follows. It also renames terms the reviewer knows from the submission: the stored pairs are now
the original pairs, the same-generator pairs the rebuilt pairs, the headline rows all attempts,
the strict rows working backdoors, and an attack that fires is one that works. B′ and S are
written out as the AUROC on the original and on the rebuilt pairs of the same problems. The models
that wrote the original backdoors, all released by early 2025, are called the older models, and
each kind of pair is named by who wrote its honest and its backdoored side (person / older models
for the original pairs, Sonnet 5 / Sonnet 5 for the rebuilt ones).

**1. The abstract did not state the problem, method, why the method works, or the insight.**
We rewrote it in that order. It also had three errors, now removed:
- It called the no-code floor an authorship difference, although that classifier reads only
  problem metadata.
- It said prompt matching "removes most of the rest". It does on Sonnet 5 (ρ 0.687 → 0.390) and
  not on Haiku 4.5 (0.097 → 0.110).
- It said the monitor "moves the same way" as the classifier (see point 4).

The new abstract states the problem, the two baselines that never run the code, the class swap
and the catch rate at a fixed audit budget on backdoors whose triggers we checked (point 4). ρ, the all-attempts and working-backdoor rows, and what
ρ is not are in Section 4 and Table 1.

**2. The all-attempts sets are mostly failed attacks.** Agreed, and it is worse than stated:
- Only 14 of 623 (Sonnet 5) and 2 of 611 (Haiku 4.5) of these attacks work, while every original
  backdoor on those problems works.
- Our sentence saying that the original pairs in this comparison include non-working backdoors
  was false. The all-attempts rows compared working original backdoors against mostly
  non-working attempts.

Table 1 now has a column counting the backdoors that work and groups the rows into all attempts
and working backdoors. The text says what the all-attempts rows compare.

**3. Authorship is not isolated.** Agreed:
- Against the same human code, the model that wrote the original backdoor alone moves the
  bag-of-words AUROC from 0.75 to 0.93. So ρ is neither the backdoor's share of the separability
  nor a bound on it. We removed "bound" and the sentence saying the independent variant changes
  "the writer and nothing else".
- ρ does not depend on which model wrote the original backdoors: with Claude attackers only it is
  0.715, against 0.687 for the full mix.
- We ran the experiment that isolates authorship for the classifier: fit it to every pairing
  of an honest and an attack class (Table A8; Figure 1b shows the working-backdoor problems). We
  fixed the reading rule before computing the missing cell. On Sonnet 5's all-attempts problems:
  - human honest code against our attacks scores 0.981, above the 0.865 of the original pairs;
  - our honest code against original backdoors scores 0.956;
  - only the pairing in which one model wrote both classes (the rebuilt pairs) falls, to 0.750.

  Haiku 4.5 gives 0.973 and 0.966 against 0.534 on its rebuilt pairs, and on Sonnet 5's 99
  working-backdoor problems the two mixed pairings score 0.953 and 0.905 against 0.789 (original)
  and 0.749 (rebuilt). So for the classifier the
  drop is authorship, not our attacks: our attacks are easier, not harder, to separate from human
  code. For the monitor it is the reverse (point 4).

**4. Verified attacks qualify the result.**
- **Monitor.** Valid, and it changes our claim. Swapping one class at a time (Table A10; Figure 1c
  shows the working-backdoor problems), the Sonnet 5 monitor scores, over all attempts:
  - 0.958 for human honest against original backdoors;
  - 0.446 for human honest against our attacks;
  - 0.974 for our honest against original backdoors.

  Its mean suspicion is 6.6 for our attacks and 78.8 for the original backdoors. Over all
  attempts the monitor's drop is in the attacks, not in authorship, and most of our attempts do
  not work. On working backdoors human honest code against ours scores 0.755, against 0.944 on
  the original pairs, but part of that fall is the labels. A draw counted as working if, on the
  trigger Sonnet 5 proposed, its output differed from Sonnet 5's own honest solution; nothing
  asked whether the trigger was a legal input. We now check every trigger in both classes against
  an input validator written from the statement, require the backdoor's output there to differ
  from the human solutions' majority answer, and when a check fails search 40 nearby legal inputs
  for one where the backdoor is wrong anyway (appendix D.3). Of the 99 working backdoors the
  monitor scored, 34 have only an illegal trigger and 6 give the human answer on theirs; the
  monitor scores them low, though it scores several of the older models' illegal-trigger
  backdoors high, so it is not detecting legality. The dataset's labels have the same problem: in
  the standard test split, on which every published monitor is scored, 17 of the 172 backdoored
  programs have only an illegal trigger and 7 print a wrong integer on a public test. Without those
  24, bag-of-words scores 0.817 (against 0.806), and rescoring the 24 published monitors from their
  released scores moves them by a median of +0.010. Both backdoors pass on 54 problems. On these
  Sonnet 5's backdoors are still harder to catch, but by less: AUROC 0.958 against 0.904
  (difference −0.053, 95% CI −0.108 to −0.004), and flagging 2% of the human solutions the monitor
  catches 78% of the older models' backdoors and 61% of ours (difference 0.17, 0.0002 to 0.32,
  against 0.40 before the checks; Figure 1d). It also finds Sonnet 5's honest code slightly less
  suspicious than human code (+0.042, 0.013 to 0.075), a confound we name in the limitations. The submission's "the monitor moves the same way" is withdrawn.
- **Classifier.** Partly valid. On the 64 problems in both the all-attempts and the
  working-backdoor sets, ρ is about the same with all attempts and with working backdoors: 0.815
  against 0.749, paired 95% CI on the difference −0.243 to +0.131. So working attacks do not raise
  ρ. By point estimate, the working-backdoor row's higher ρ comes from which problems yield
  working backdoors: on that set's 35 other problems ρ is 1.09 (rebuilt 0.775, original 0.752).
  That difference from the shared problems is not resolved (+0.34, CI −0.13 to +0.93), and the
  paper says so. The new appendix section shows this decomposition.

**5. Statistical inconsistencies.** Agreed. Points were fold means while their intervals were
bootstraps of the pooled out-of-fold scores, and we wrongly called these "the same quantity".
The appendix now states one convention:
- Every point is the pooled out-of-fold AUROC, and every interval is the bootstrap over problems
  of that same quantity (joint for ρ).
- Every permutation null is 1,000 permutations that shuffle the labels for fitting and scoring
  alike.
- The agentic nulls (Figure A5) are within-task permutations of the plotted statistic.

No conclusion changes. The working-backdoor ρ moves from 0.921 to 0.861. The held-out no-code null
moves from 0.702 to 0.558 (p = 0.001), so that row is no longer "barely above its null".

We also ran the no-code floor under the bag-of-words protocol: trained on problems outside the
test split and scored once, it scores 0.298, below chance. Outside the split, every problem that
passes the filter has a working backdoor, so the relation between test count and label
reverses. Section 3.1 reports it beside the within-split 0.766, as the same relation reversed, and
presents both as a measure of how the split chose its labels, not as authorship.

**6. Repetition, and no fixed audit budget.** We cut the repeated numbers and verdict words. The band
labels are gone: the body reports ρ with its interval, and the two values we fixed in advance (0.33
and 0.72) are disclosed in the appendix with why we no longer use them. We now report detection at a fixed audit budget. At a
2% false-positive rate, with the threshold set on each set's own honest programs, the Sonnet 5
monitor catches:
- on the 54 working-backdoor problems where both backdoors pass the trigger checks (point 4): 78%
  of the older models' backdoors and 74% of ours (paired difference 0.04, 95% CI −0.12 to 0.19);
- on the same problems with the threshold set on the human solutions for both, so that only the
  backdoors change: 78% and 61% (difference 0.17, 0.0002 to 0.32), the comparison Figure 1d leads
  with; at 1% the difference is 0.19 (0.03 to 0.32);
- over all attempts, whose triggers we did not check: 85% and 6%.

Honest programs are not filtered, so each threshold is still set on all 99 working-backdoor
problems' honest programs.

The appendix gives the full table at 1%, 2% and 5% for both monitors.
