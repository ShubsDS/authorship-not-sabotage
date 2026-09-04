# The scores and the five gates, run against *this* headline

The rubric was written on 2026-09-02, **before** the sweep results it would be used on, so it cannot
be reverse-fitted to whichever idea survived. Acceptance and safety-relevance are scored
**separately and reported separately** — averaging them lets a high-acceptance/no-relevance paper
hide, which is how the previous lead drifted for three rounds.

Reported as `A: x/30, B: y/25`, plus gate pass/fail, plus the sharpest reviewer objection and whether
there is an answer.

---

## A — acceptance probability: **26 / 30 @ EvoRobust**

| # | Dimension | Score | Why |
|---|---|---|---|
| A1 | Novelty, verified | **4** | The application is unmade out-of-field and the authorship reading is unclaimed — confirmed by **reading** the two nearest papers, not by grepping them (`lit/01` §4). **Not 5**, because one carrier (the comment leak) is published in the anchor's own repo, and because AICD Bench App. D.1 already publishes the token-level mechanism. **Held at 4 after the sweep — it neither rose nor fell**, which is the outcome R11 exists to make visible. |
| A2 | Scoop resistance | **3** | Tracy, Redwood/UK AISI and Jha are all active here, and Jha already owns the instrument. This is the weakest acceptance dimension and it does not improve by waiting. |
| A3 | Outcome robustness | **5** | Realised *inside one table*, not argued: bash 0.504 clean vs agentdojo 0.802 leaky; `solution_passes_tests` 0.500 on the filtered split (the field's fix works) vs metadata 0.772 (it does not reach the problem side). **The paper cannot come out "no result."** |
| A4 | Venue fit | **5** | *"Benchmarks and Governance: continuously evolving safety benchmarks… coverage metrics"* names the object. |
| A5 | Executability | **5** | Every CPU number exists today. One GPU control remains, ≤$10. |
| A6 | Claim discipline | **4** | Every abstract sentence has a number behind it, once Gate S returns. |

## B — relevance to general AI safety: **20 / 25**

| # | Dimension | Score | Why |
|---|---|---|---|
| B1 | Does a safety decision change? | **4** | Three concrete protocol changes: same-generator honest samples, report partial-input and bag-of-words floors, drop inert backdoors from both classes. |
| B2 | Generality | **4** | Six corpora, **two distinct mechanisms** — authorship on the APPS family, structure on the agentic settings. It was a 3 until the five agentic settings came in free. |
| B3 | Survives capability scaling? | **4** | Structural to the dataset, not to any model. **Better attack models make it worse, not better** — a stronger backdoor writer widens the authorship gap. |
| B4 | Threat-model honesty | **4** | No adversary is required; this is a validity audit. |
| B5 | Citability | **4–5** | A released split, and a floor every stored-pair monitoring paper has to report. |

## The gates — all five run, none inherited

A gate reads **pass**, **fail**, or **unrunnable**. A blank, a silence, or a tick inherited from a
previous round is none of these and must not be reported as a pass. **A gate does not survive a
reframe** — this headline is not the round-16 headline, so all five were re-run against the new one.

| Gate | Status | Evidence |
|---|---|---|
| **G1** — verified novelty, including *outside* the home field | ✅ **PASS — fully discharged 2026-09-03** | Out-of-field sweep run on hypothesis-only baselines, Clever Hans, the leakage taxonomy and AI-code detection, zeros with in-batch positive controls. **The count-level caveat is closed:** `2602.02079` and `2506.11059` were read end to end — setup, evaluation, appendices, limitations — and both come back **NEIGHBOUR**. Neither connects AI-code detection to the validity of any downstream safety or monitoring benchmark, in any wording (`lit/01` §4). |
| **G2** — organizer / speaker collision | **PASS**, conditional on excluding AgentHarm | `notes/01`. Andriushchenko is adjacent, not colliding; his benchmark is excluded in writing. |
| **G3** — data and harness resolve before commitment | **PASS** | Seven corpora loaded and analysed on 2026-09-03 — the first time in seventeen rounds that hour one actually happened. |
| **G4** — the obvious competing axis | **PASS** | `2608.16190` shows free choice of open-weight monitor spans **29×** in pAUC@10%FPR. A floor is a property of the *evaluation*, so the 29× monitor span does not touch it — every one of those 24 monitors is ranked on the same leaking split. |
| **G5** — relevance floor (B1 and B3 both ≥3) | **PASS** | 4 and 4. |

## The sharpest reviewer objection, and the answer that must be in the abstract

> *"Length and authorship style are part of the input the monitor legitimately reads. A high floor
> means the task is easy, not that the benchmark is invalid — and Jha already checked and fixed the
> code-side carriers."*

**Answer.** In deployment the untrusted model chooses its own trajectory length and **writes both
classes**. A monitor scoring well on a corpus where the honest class was written by humans and the
attack class by an LLM has been validated on a discrimination it will never face. **The
same-generator arm is the constructive half of the paper, not a robustness check** — which is why
Gate S is on the critical path and the figures are not.

**Second objection, weaker but real:** *"Rows 3–7 are one user's unlicensed repackaging with 27–54
downloads and no README."* Provenance is legible inside the files (`eval_file`,
`extra_info.setting`, `extra_info.model`); the APPS leg runs on MIT artifacts with 6,958 downloads;
the comparison monitors come from an MIT repo. **Scope the title to "public releases of" rather than
"ControlArena."**

**Third, and new on 2026-09-04:** *"TF-IDF separating human-written from LLM-written code is a known
result — AICD Bench publishes it. What is new here?"* **Answer: nothing about the mechanism, and that is
the point.** We cite it as established and claim only the application: that a corpus whose classes
differ by author is used to train, select and rank sabotage monitors, and that nobody has quantified
what survives the field's preprocessing. A well-established separability result makes the benchmark's
construction *less* defensible, not our contribution smaller. **This objection is why the paper leads
with the validity claim rather than the number** (`../paper/OUTLINE.md` §1).

**Fourth:** *"A trained classifier beats zero-shot monitors — so what?"* The claim is Gururangan's,
not "our monitor is better": the label is recoverable from features that cannot see a backdoor, at
200 training pairs, and from no code at all.

## What the budget surplus buys, in order

A second **task setting** (done — five agentic settings, $0), an **adversarial arm** (not applicable
— there is no adversary in a validity audit), and **confidence intervals** (permutation nulls beside
every floor, 5×5 CV — done). **Breadth buys nothing here.** More points on an existing curve is
padding; the binding constraint is writing time.
