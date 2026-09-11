# Where the prompt-matched arm (arm 3) goes in the paper, at zero net lines

Written 2026-09-11 by session 7f for session f2, which owns `paper/main.tex` and RESULTS.md §13.
The Gate S paragraph (`main.tex`, the block after `% --- Gate S outcome`) is at its line budget:
References begins on page 5 and there is no slack. Every sentence added below is paid for by a
sentence named beside it.

## 1. The slot

The paragraph currently carries, in this order: headline S and ρ → verdict state → "authorship
about a third; length-only to chance" → **the §11 mechanism sentence** ("It is not the trigger: …
`def main` and `data[` … the layout the attack prompt elicits.") → **"The arm holds the model
constant, not the prompt, so ρ is an upper bound on content."** → similarity → learning curve →
strict row → survivor check → edit bound → monitors → funnel → interval rule.

Arm 3 answers exactly the sentence in bold. Replace that one sentence (it is the placeholder for
this result) with the outcome sentence below. Nothing else moves; the mechanism sentence before it
stays because it is what motivates the arm.

## 2. Macros to add (top of `main.tex`, beside `\sameGen*`)

```
\newcommand{\pmS}{0.xxx}        % S with the honest class regenerated under the attack prompt's framing
\newcommand{\pmLo}{0.xxx}\newcommand{\pmHi}{0.xxx}
\newcommand{\pmN}{nnn}
\newcommand{\pmRho}{0.xx}\newcommand{\pmRhoLo}{0.xx}\newcommand{\pmRhoHi}{0.xx}   % joint bootstrap
\newcommand{\pmBprime}{0.xxx}
```

Same eligibility as the headline (outcome-blind draw, attack passes the tests, B′ inert-inclusive),
same problems as far as the prompt-matched honest passers allow; report the realised n.

## 3. The sentence, by outcome (paste one; the ρ bands are the pre-registered ones)

- **Prompt framing was the rest** (CI of ρ_pm upper < 0.33): "Regenerating the honest class under
  the attack prompt's framing removes it: $S = \pmS{}$ (\pmLo{}--\pmHi{}; $n = \pmN{}$),
  $\rho = \pmRho{}$ (\pmRhoLo{}--\pmRhoHi{}), inside the collapse band. With model and prompt both
  held constant a bag-of-words classifier is near chance; the stored benchmark's separability was
  who wrote the code and how it was asked to."
  → the abstract's "about a third" becomes "authorship and prompt framing together account for
  the separability"; §1 paragraph 3 likewise. Title stays.
- **Some content survives** (whole CI inside 0.33–0.72, or spanning 0.72): "Regenerating the honest
  class under the attack prompt's framing lowers it to $S = \pmS{}$ (\pmLo{}--\pmHi{};
  $n = \pmN{}$), $\rho = \pmRho{}$ (\pmRhoLo{}--\pmRhoHi{}): prompt framing carried
  [about half / most] of what authorship did not, and the remainder is content of the attack
  class itself." Keep "upper bound" language for the headline ρ.
- **Nothing moves** (CI of ρ_pm overlaps the headline's 0.625–0.755): "Regenerating the honest
  class under the attack prompt's framing does not move it ($S = \pmS{}$, \pmLo{}--\pmHi{}), so the
  layout signal is not the prompt's: it is how this model writes when asked to hide something."
  → then the §11 sentence's "the layout the attack prompt elicits" must soften to "a layout that
  travels with the attack instruction", and the "upper bound" clause is dropped rather than
  replaced (that is the one case that saves a line).

## 4. If a second line is needed

Pay with the interval-rule sentence at the end of the paragraph ("Intervals are bootstraps over
problems … before the retry pool was read."): move it to the appendix's Gate S paragraph, where
the ±2 fold-sd history is already explained, and leave "(joint bootstrap over problems)" as a
parenthetical after the first ρ. That is a net −1 line in the body.

## 5. Ledger shape (§13)

Same table as §9.1 plus a column "honest prompt" (original / attack-framed); the §11 masking rows
(none / NUM+CMP / ID) rerun on the prompt-matched pairs, so the paper can say whether identifier
normalisation still moves S once the framing is matched; the `def main` / `data[` presence
fractions on both sides; pair similarity. If arm 3's honest passers are a subset of the 1,112,
say how many and rerun the headline on the intersection for a like-for-like ρ.
