# The venue — EvoRobust, Sep 12 AoE, with FLLMPT as a free dual

Every row below was confirmed by fetching the workshop's own CFP page, not an aggregator, and
re-verified on 2026-09-03.

## The timezone rule, first, because it moved ~25 deadlines once already

**`aiworkshoptracker.com` publishes deadlines in UTC. AoE = UTC − 12h**, so AoE is *later* than the
UTC timestamp — a correction that **opens** rows, and once got used to close them. Verified against
four venues independently: AIWILD Sep 6 13:00 UTC = Sep 5 AoE; InfPriv Sep 8 12:00 UTC = Sep 7 AoE;
**EvoRobust Sep 13 12:29 UTC = Sep 12 AoE**; VERICODEGEN Sep 14 11:59 UTC = Sep 13 AoE.

**FLLMPT is the exception and it will catch you: its deadlines are GMT, not AoE — 13 hours earlier
than EvoRobust.**

## EvoRobust — the target

**Self-Evolving Diversity-Driven Search for Robust AI Systems**, NeurIPS 2026, Sydney.

| | |
|---|---|
| **Deadline** | **Sep 12 AoE.** Re-checked 2026-09-03: no extension. |
| Format | **4 pp** (5 pp camera-ready), NeurIPS template, 50 MB |
| Archival | **No.** OpenReview, double-blind. |
| Dual submission | **Allowed** — *"under review… or recently accepted without published proceedings"* |

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

## FLLMPT — the free dual, and the only thing on Sep 5

Non-archival, dual submission welcome *"including work previously published, provided it has been
updated or recontextualised."* CFP names *"ML theory, reinforcement learning, and **AI safety**"* and
*"**safety-critical settings**, where unintended regressions or feedback loops may arise."*

| | |
|---|---|
| **Abstract** | **2026-09-05, 23:00 GMT — mandatory, and this is the only irreversible date before Sep 12** |
| Paper | 2026-09-12, 23:00 GMT, marked *"Firm deadline"* |

Fit is post-training, so weaker than EvoRobust for a monitoring paper. **It costs a title and 150
words on Sep 5 and it buys a second shot; register it.** It is an option, not a target — if the
abstract is not registered by then, FLLMPT is simply gone and nothing else changes.

## If Sep 12 is missed

Missing it costs **7–11 weeks**, not silence. Every date off the venue's own page:

| Venue | Deadline | Format | Fit for this paper |
|---|---|---|---|
| **SaTML 2027** main | abstract Sep 22 / paper Sep 29 AoE | ≤12 pp, **archival**, no dual | Security bar; a 4-page measurement is not a SaTML paper without more corpora |
| **ARR October** → NAACL/COLING 2027 | Oct 12 | ACL format | The Poliak/Gururangan framing is native here |
| **FAccT 2027** | abstract Oct 27 / paper Nov 3 AoE | ≤14 pp, archival **or** non-archival | *"AI red teaming and adversarial testing"*, *"Science of responsible… AI evaluation"*, *"audits of systems"* — **the best-fitting venue in the window** |
| **AAAI-27 workshops** | Nov 20 AoE | per workshop | List not public until ~Oct 2; historically the densest safety/alignment concentration |

**Closed side-doors, checked so nobody re-checks them:** IAB's NeurIPS-reviews route (Oct 1) and
InfPriv's fast track (Sep 25) both require an existing NeurIPS 2026 main-conference submission with
reviews attached. Neither is reachable. AAAI-27's AI Alignment special track closed Aug 21 — note it
for 2028, its topic list is a near-exact match.
