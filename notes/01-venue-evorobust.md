# The venues — EvoRobust Sep 12 (FLLMPT and AIWILD both out)

> ⛔ **FLLMPT was DROPPED on 2026-09-10, and AIWILD is out for this cycle. EvoRobust is the sole
> target.** FLLMPT was only reachable by registering an abstract before Sep 5 23:00 GMT; that gate
> passed unregistered, so the option expired. Everything about FLLMPT below is kept as the record of
> a check that was really performed — its G2 pass, its format, its 23:00 GMT wall — but **none of it
> constrains this paper any more.** Read the FLLMPT rows as history, not as a live deadline.

Every row below was confirmed by fetching the workshop's own CFP page, not an aggregator. EvoRobust
and FLLMPT were both re-fetched on **2026-09-04** and every date, page limit and policy below is off
those two pages.

⚠️ **The two workshops are on different continents on adjacent days** — EvoRobust is Sydney, Dec 11;
FLLMPT is Paris, Dec 12–13. Both are non-archival poster workshops, so this is a travel question and
not a submission question, but do not discover it in December.

## The timezone rule, first, because it moved ~25 deadlines once already

**`aiworkshoptracker.com` publishes deadlines in UTC. AoE = UTC − 12h**, so AoE is *later* than the
UTC timestamp — a correction that **opens** rows, and once got used to close them. Verified against
three venues independently: AIWILD Sep 6 13:00 UTC = Sep 5 AoE; **EvoRobust Sep 13 12:29 UTC = Sep 12
AoE**; VERICODEGEN Sep 14 11:59 UTC = Sep 13 AoE.

**FLLMPT is the exception and it will catch you: its deadlines are GMT, not AoE — 13 hours earlier
than EvoRobust.**

## EvoRobust — the target

**Self-Evolving Diversity-Driven Search for Robust AI Systems**, NeurIPS 2026, Sydney.

| | |
|---|---|
| **Deadline** | **Sep 12 AoE** (*"All deadlines are 11:59 PM AoE"*). Re-checked 2026-09-04: no extension. |
| Format | **4 content pages** (5 camera-ready), unlimited references and supplementary, NeurIPS 2026 style, 50 MB |
| Archival | **No.** OpenReview, double-blind. |
| Dual submission | **Allowed**, explicitly — *"Workshop submissions can be subsequently or concurrently submitted to other venues."* |
| Abstract registration | **None.** Only the Sep 12 paper deadline exists. |
| Workshop date | Sydney, **Dec 11, 2026** |

**Why this venue and not a control-native one:** two of its five topic areas name our objects
verbatim — *"**Agentic Safety & Interactive Robustness**: safety of tool-using agents, long-horizon
failures, multi-agent risks, human oversight and controllability"* and *"**Benchmarks and
Governance**: continuously evolving safety benchmarks, automated test case generation, **coverage
metrics**."* The others are Safety Scenario Search & Failure Discovery, Novelty Search &
Quality-Diversity for Robustness, and Multi-Objective Trustworthy AI.

The PC is **not** AI-control natives — organizers include Moosavi-Dezfooli alongside
evolutionary-computation people (Yew-Soon Ong, Escalera); speakers include Andriushchenko, David
Wagner, Hamed Hassani, Bo Han. **They are robustness-literate and adaptive-attack-literate**, which
is enough. This was mis-graded ⚠️ off its title for two rounds before anyone fetched the CFP; that
mistake is rule R13.

> **Write for that reader.** A benchmark-validity result is legible to an adversarial-robustness
> reviewer as *your evaluation measures the wrong thing*. It is not legible as psychometrics, which
> is why the IRT variant of this paper was killed on venue fit.

### G2 — organizer and speaker collision, run 2026-09-03

| Check | Result |
|---|---|
| Andriushchenko (invited speaker), `2510.09462` adaptive attacks on trusted monitors | **Adjacent, not colliding.** Different failure axis — he subverts monitors with injected text; we show the label leaks through authorship. **Cite in paragraph one and distinguish.** |
| **AgentHarm as a sixth corpus** | ⛔ **EXCLUDED.** Andriushchenko authored it. Auditing an invited speaker's own benchmark at his own workshop is an avoidable own-goal. Say the exclusion in the paper, and say why. |
| Any organizer or other speaker with a trivial-baseline or benchmark-validity paper | **None.** |

## AIWILD — the best reviewer fit on the calendar, and it closes Sep 5 AoE

**3rd Workshop on Agents in the Wild**, NeurIPS 2026, Sydney. Re-verified on its own page 2026-09-02.

| | |
|---|---|
| **Deadline** | **Sep 5 AoE** (extended from Aug 29) = **Sep 6, 12:00 UTC** |
| Format | 9 pp regular / **4 pp short**, non-archival, **work-in-progress explicitly welcome** |
| Dual submission | **Allowed** — *"papers under review or recently accepted at other venues"* |
| Reviewer fit | ★★★ **Clean — the only one on the calendar.** CFP names *"Agent safety, alignment, **control**, and oversight"* verbatim, and the workshop published `2606.30449`, a probes-fail-on-pre-action-monitoring paper. **They read this literature; EvoRobust's PC does not.** |

⚠️ Its page **discourages** submissions from the NeurIPS/ICLR/ICML main tracks. Not applicable to us.

**Because it is non-archival and permits concurrent submission, an AIWILD short paper does not consume
the EvoRobust slot.** The Sep 12 EvoRobust version can be the same work with Gate S added.

> ### ⛔ AIWILD is out for this cycle — recorded as a decision, not left dangling
> **Its deadline is a whole 4-page paper on Sep 5, and the prose is not written until Sep 10–11.**
> There is no version of the schedule where a submittable paper exists tomorrow, so the best reviewer
> fit on the calendar is unreachable this round. `PLAN.md` never mentioned AIWILD, which read as an
> oversight; it is a decision, and this is where it is written down.
>
> **Two live consequences.** (1) If Sep 12 slips, AIWILD is *not* the fallback — see the table below.
> (2) **G2 has never been run for AIWILD**, and if it ever comes back onto the calendar that gate runs
> first: `2606.30449`'s group is the plausible occupant of any agent-monitoring workshop and is the same
> repo (`maxf-zn/misalignment_monitoring`) that C9 was going to build on. Probably adjacent rather than
> colliding — **probably is not a gate result.**

## FLLMPT — Foundations of LLM Post-Training in Changing Environments

*The free dual.* Everything below is off `https://www.fllmpt-work.shop/call/`, fetched 2026-09-04.
Paris, 12–13 Dec 2026. Organised by the ELLIS Units Paris and Oxford with Warwick, Oxford and EIT.

| Milestone | Date (all GMT, stated as such on the page) |
|---|---|
| Submission portal opens | 2026/07/29 00:00 |
| **Abstract registration** | **2026/09/05 23:00** — *"One week before paper deadline"* |
| **Paper submission** | **2026/09/12 23:00** — *"Firm deadline"* |
| Notification | October 2026 (TBA) |
| Camera-ready | November 2026 (TBA), **non-archival** |

⚠️ **A third-party listing is wrong and will mislead you.** The ELLIS events page advertises a paper
deadline of **30 August 2026**. The workshop's own CFP says **12 Sep**. The venue's own page wins (R1).

Non-archival. CFP names *"machine learning theory, reinforcement learning, and AI safety"* and
*"safety-critical settings"*, and its motivation cites the International AI Safety Report on the lack
of theoretical understanding of *"robustness under task evolution, unintended regressions, and the
limits of safe adaptation."*

Fit was graded post-training and therefore weaker than EvoRobust. **That grading is probably too
harsh.** This paper is a *distribution-shift* result: the corpus's honest class is human-written, and
in deployment the untrusted model writes both classes, so a monitor selected on it was selected under a
distribution that does not obtain at deployment. Monitor training and selection **are** post-training
procedures, and *"unintended regressions in safety-critical settings"* is close to a verbatim
description. Framed as shift-between-construction-and-deployment rather than as a benchmark audit, the
fit is decent — and that reframing is exactly the *"recontextualised"* the dual-submission clause asks
for.

### The three gaps, all closed 2026-09-04

**1. G2 for FLLMPT — ✅ PASS, run properly, not inherited.** The full roster off the organisers and
speakers pages:

| Role | Who | Collision? |
|---|---|---|
| Lead organiser | **Francesco Quinzan** (Oxford) — AI safety, statistical learning, robustness, alignment of foundation models | Nearest topical match on the committee. No monitoring benchmark, no AI-control artifact. **Clear.** |
| Organisers | Gabriel Peyré (ENS/CNRS), Patrick Rebeschini (Oxford), Chengchun Shi (LSE), Fanghui Liu (SJTU) | Optimal transport, statistical foundations of RL, causal inference, learning efficiency. **Clear.** |
| Additional organiser | **James Dixon** (Oxford DPhil, LASR studentship) — *"AI Security and mechanistic interpretability"* | The closest thing to our neighbourhood on the committee. Searched for an AI-control / trusted-monitoring paper under his name: **none found**, in a batch where the topical positive controls fired hard (the search returned `2602.20628`, `2607.07368`, `2602.04930`, `2510.09462`, `2512.22154`). **Adjacent field, no colliding artifact.** |
| Additional organiser | Valentina Zangirolami (Milano-Bicocca) — RL, partial observability | **Clear.** |
| Keynote | Mihaela van der Schaar (Cambridge) — principled evaluation, adaptation under distribution shift | Sympathetic register, different domain. **Clear.** |
| Speakers | Yee Whye Teh (Oxford/DeepMind), **Yali Du** (KCL), Giorgia Ramponi (UZH), Gido van de Ven (Groningen) | **Du is a benchmark author** — `2512.03318`, NeurIPS 2025 D&B, generalisation of LLM agents in cooperative and mixed-motive settings. Different family entirely: cooperation and coordination, not sabotage monitoring. **Adjacent, not colliding**, and a likely sympathetic reader. |

**No organiser or speaker authored any of our seven corpora**, so unlike AgentHarm at EvoRobust,
nothing has to be excluded. Write the recommendations as addressed to the field, not as an indictment
of benchmark authors — one of the speakers is one.

**2. The page limit — ✅ recorded, and it is not 4 pages.** The CFP: *"Submissions must follow the
exact same paper type and format as NeurIPS 2026 main track submissions, as our workshop mirrors the
main track's policies."* The NeurIPS 2026 Main Track Handbook: *"The main text of a submitted paper is
limited to nine content pages, including all figures and tables."*

> **Consequence.** A 4-page EvoRobust paper is *format-legal* at FLLMPT — it is under the limit — but it
> sits against 9-page submissions. Submitting the EvoRobust PDF unchanged is allowed and is the cheap
> path; if there is slack after Sep 11, the obvious use of it is expanding to 6–7 pages with the
> shift-between-construction-and-deployment framing in front.

**3. Dual submission with EvoRobust — ✅ verified from both sides, as a pair.** FLLMPT: *"We welcome
submissions of work currently under review at other venues and work that has previously been
published, provided it has been updated or recontextualised for the workshop audience. Please disclose
prior publication in the submission form."* EvoRobust: *"The workshop is a non-archival venue…
Workshop submissions can be subsequently or concurrently submitted to other venues."* Both
non-archival, both explicit. **Disclose the concurrent submission on the FLLMPT form** — the CFP asks.

### The title lock — ✅ resolved, and it is not a lock

The NeurIPS 2026 handbook locks **author names** at the abstract deadline (*"All author names must be
entered into the submission form by the abstract submission deadline. After this, no changes can be
made, except to the author order."*) and says **nothing about the title**. FLLMPT mirrors main-track
policy and adds no rule of its own; OpenReview permits editing title and abstract until the paper
deadline.

**So Gate S on Sep 8 can still change the title before the Sep 12 paper.** Recorded honestly: this is
the *absence of a prohibition* rather than an explicit permission. It is strong enough to act on. If
the route-2 result would make the change dramatic, one email to `contact@fllmpt-work.shop` settles it.

**What still binds on Sep 5:** the **author list**. Get every author's OpenReview profile entered by
23:00 GMT — that is the one thing genuinely irreversible on that date. The title is not.

> **Net effect: the Sep 5 date is much cheaper than the plan assumed.** It costs a title, 150 words and
> a correct author list, and none of it constrains Gate S. Register it.

## If Sep 12 is missed

Missing it costs **7–11 weeks**, not silence. Every date off the venue's own page:

| Venue | Deadline | Format | Fit for this paper |
|---|---|---|---|
| **SaTML 2027** main | abstract Sep 22 / paper Sep 29 AoE | ≤12 pp, **archival**, no dual | Security bar; a 4-page measurement is not a SaTML paper without more corpora |
| **ARR October** → NAACL/COLING 2027 | Oct 12 | ACL format | The Poliak/Gururangan framing is native here |
| **FAccT 2027** | abstract Oct 27 / paper Nov 3 AoE | ≤14 pp, archival **or** non-archival | *"AI red teaming and adversarial testing"*, *"Science of responsible… AI evaluation"*, *"audits of systems"* — **the best-fitting venue in the window** |
| **AAAI-27 workshops** | Nov 20 AoE | per workshop | List not public until ~Oct 2; historically the densest safety/alignment concentration |

**Closed side-doors, checked so nobody re-checks them:** IAB's NeurIPS-reviews route (Oct 1) requires
an existing NeurIPS 2026 main-conference submission with reviews attached and is not reachable.
AAAI-27's AI Alignment special track closed Aug 21 — note it for 2028, its topic list is a near-exact
match.
