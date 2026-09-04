# Verified bibliography — *Authorship, Not Sabotage*

**✅ means the page was actually fetched and read. ⚠️ means do not cite until it is.** A fabricated
reference is a desk-reject, and a citation described from a search snippet has been wrong here twice
(`../notes/03-method-rules.md` R1).

Everything below was fetched on **2026-09-02 or 2026-09-03** unless the row says otherwise. Carried
across from the ideation repo's `lit/02`, filtered to this paper and reorganised by the job each
citation does. Entries about the InfPriv paper, the compression tax, sandbagging probes and C9 are
not here; they were never about this paper.

---

## 1. Paragraph one, and the order it goes in

These six are **mandatory** and they are the condition on which the paper's novelty claim survives.
The field already does most of the preprocessing this paper measures. Credit it first, then state
what is left.

| id | Verified | Why it must be cited first |
|---|---|---|
| `2605.15377` ✅ | Koran, Yun, Tetef, Arnav, Bernabeu-Pérez, *Ensemble Monitoring for AI Control: Diverse Signals Outweigh More Compute*, v2 18 May 2026. `arxiv.org/html/2605.15377v2`, 334,191 B. | **This is "Koran et al. (2026)."** §4.1 verbatim: *"To isolate backdoor detection from generally incorrect code, we keep only working honest solutions (passing all tests) and working backdoored solutions… we strip all comments from the code before evaluation."* And: *"The test set is extended to problems that have working solutions but no working backdoors to sharpen FPR estimation at low thresholds… the shift affects all monitors equally and does not impact relative comparisons."* Every protocol arm the audit proposed, with its rationale, in one paragraph. Its release is the split every number in this paper is measured on. |
| `2608.16190` ✅ | Jha, *Decorrelation Is Not Complementarity*. Repo `github.com/anik-jha/challenger-panels`, **MIT**, pushed 2026-08-17. | Names the comment leak outright: *"Backdoor code in this dataset frequently carries comments that name the backdoor outright and would otherwise leak the label."* Ships `--leak-check` with two published trivial baselines (`hash_count_only_detector_auroc` 0.6957 → **0.4983** after stripping; `code_length_only_auroc` **0.4726**) and the verdict *"Stripping is mandatory, not cosmetic."* **Supplies the comparison set**: `runs/x0/monitor-summary.json`, 24 monitors' `test_auroc` on the 1,375-item split — min 0.434, **median 0.609**, max 0.937 — and `runs/scores/`, per-item scores for all 24. All three of its published numbers were bit-reproduced by our split reconstruction. |
| `2506.05296` ✅ | Terekhov, Liu, Gulcehre, Albanie, *Control Tax*. | §2.3: *"public unit tests serve as a pre-filtering mechanism… a quality threshold that attacker's proposed backdoors need to pass."* Appendix C.3 is titled *"Monitoring failed backdoors."* The selection effect is reported. |
| `2602.10153` ✅ | *Basic Legibility Protocols Improve Trusted Monitoring*. `comment` ×272. | An entire paper on the comment channel. It is why "the comment leak is unreported" is a dead sentence. |
| `2606.06529` ✅ | Ge-Wang, Crosse, Hadad, Schaeffer, Potham, **Tracy**, *Attack Selection in Agentic AI Control Evaluations Meaningfully Decreases Safety*, 2026-06-03. BashArena + LinuxArena, **−20/−28 pp at 1% audit budget**. | Makes the "control evaluations are optimistic" case from the **attacker** side — when to attack. Ours is the dataset-construction side. Cite as the neighbour that agrees. It also tells us Redwood / UK AISI people are in this neighbourhood, which is why A2 is 3 and not 5. |
| `2510.09462` ✅ | Terekhov, Panfilov, Dzenhaliou, Gulcehre, **Andriushchenko**, Prabhu, Geiping, *Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols*, ICLR 2026. | Adjacent, **not** colliding: they subvert monitors with injected text; we show the benchmark's label leaks through authorship. Different failure axis. Andriushchenko is an EvoRobust invited speaker — cite and distinguish in paragraph one, and see `../notes/01-venue-evorobust.md` for the G2 finding. |

**And cite one paper against ourselves**, in Limitations, unprompted:

| id | Verified | Why |
|---|---|---|
| `1905.05778` ✅ | Feng, Wallace & Boyd-Graber, *Misleading Failures of Partial-input Baselines*, ACL 2019. | Verbatim: *"the failure of a partial-input baseline does not mean a dataset is free of artifacts."* The symmetric warning applies to us — a high floor is evidence about the corpus, not proof that every monitor number on it is meaningless. Say it ourselves before a reviewer says it. |

## 2. K2 — is the floor unreported? **FAIL as written; a narrower claim survives**

The K2 check was supposed to confirm that no control paper reports a construct-validity check. It
did the opposite, and the way it failed is the most useful thing in this repo.

Seventeen full texts fetched, keyword tables in [`k2-greps/`](k2-greps/README.md): the fourteen
AI-control papers `2312.06942`, `2506.05296`, `2608.16190`, `2605.15377`, `2607.06596`, `2602.10153`,
`2510.09462`, `2602.04930`, `2606.06529`, `2607.14570`, `2605.26047`, `2605.29178`, `2605.27157`,
`2512.13526` (Async Control — the ControlArena team; **ControlArena itself has no paper**, it is
cited as a GitHub repo), plus three out-of-field positive controls.

| Clause | Verdict | Evidence |
|---|---|---|
| No partial-input / problem-only / metadata-only baseline reported | **holds** | 0/14 on every phrasing |
| No TF-IDF / bag-of-words / n-gram code-text baseline | **holds** | 0/14 |
| No human-vs-LLM **authorship** confound named | **holds** | `authorship` 0/14 |
| "No construct-validity check on these benchmarks" | ⛔ **FAIL** | §1's four rows |
| `backdoor_works` / inert backdoors unreported | ⛔ **FAIL** | `2605.15377` §4.1; `2506.05296` App. C.3 |
| `solution_passes_tests` selection unreported | ⛔ **FAIL** | `2506.05296` §2.3; `2312.06942` §M.1: *"You can think of this difficulty filter as a crude guess at whether or not the original submission from GPT-4 is correct."* |
| Comment leak unreported | ⛔ **FAIL** | `2608.16190`; `2602.10153` |
| "The floor is above the published monitor" | ⛔ **INVALID** | The 0.64 figure **does not exist**. The DSPy tutorial reports **69% pairwise accuracy** untrained and 78–81% after GEPA, on a *matched* protocol where the metadata floor is **exactly 0.5000**. Every published pAUC is on Koran's filtered, comment-stripped split — never on the raw artifact. |

**What survives, and it is what the paper claims:** nobody reports a partial-input, bag-of-words or
authorship baseline; nobody quantifies what the preprocessing leaves behind; and the field's own
filter *installs a second selection artifact* by defining the negative class through attack failure.

## 3. The nearest in-field neighbour, and the sentence that separates us

| id | Verified | Distinction |
|---|---|---|
| `2607.06596` ✅ | Pinto, *Calibration-Family Overfit: Why Trusted Sabotage Monitors Don't Transfer Across Lineages*, 2026-07-06. Full text read, not grepped: `blatancy` ×13, `transcript length` ×2; difficulty- and blatancy-matched controls, code-only vs full-transcript cuts, MLP/SVM/RF/GB head swaps, hash-disjoint splits. | **He removes transcript length as a nuisance covariate** so a cross-family interaction estimates cleanly — *"regressing placement on policy-family and monitor-family main effects, a diagonal indicator, the continuous obviousness grade, transcript length…"*. **We publish the content-blind classifier's own AUROC as a floor published monitor numbers must clear, per benchmark.** His heads are `text-embedding-3-small` + PCA, not raw n-grams; his numbers are far from ceiling (mean diagonal 0.71); **both his arms are LLM-authored** because he regenerates them with ControlArena, so his confound is family style among four LLM lineages, not human-vs-LLM. He also declines the success filter (*"a strict success filter is degenerate at this scale"*) and never touches the agentic settings. |
| `2607.09786` ✅ | *Length Penalties Make CoT Less Monitorable.* Already runs a lexical hint-echo detector validated against an LLM judge, a **content-blind length-matched null**, and a scrubbed-vs-unscrubbed classifier ablation (0.879 → 0.877, Table 14). | **This is why the scratchpad-regex result is one paragraph and not a section.** Different setting (MCQ hint disclosure under compression vs agentic sabotage), same instrument. It owns the instrument; say so. |
| `2312.06942` ✅ | Greenblatt, Shlegeris, Sachan, Roger, *AI Control*. | The origin of the `source="apps"` GPT-4 backdoors (439/439 on Koran's test split carry `model == "openai/gpt-4"`). Cite for the protocol and for §M.1's difficulty filter. |
| `2506.15740` ✅ · `2504.10374` ✅ | SHADE-Arena (Kutasov … Shlegeris, Benton); Ctrl-Z (Bhatt … Shlegeris). | Context. Neither reports a floor. |

## 4. Out-of-field neighbours — the two the G1 gate requires, and the rest

A monitor is a classifier; a benchmark artifact is a benchmark artifact. **The method is 2018 NLP.**

| id | Verified | Role |
|---|---|---|
| `1805.01042` ✅ | Poliak, Naradowsky, Haldar, Rudinger, Van Durme, *Hypothesis Only Baselines in Natural Language Inference*, 2018. Ten NLI datasets. *"assessing entailment relations while ignoring the provided context is a degenerate solution."* | **Nearest out-of-field neighbour #1 — the method.** |
| `1803.02324` ✅ | Gururangan et al., *Annotation Artifacts in Natural Language Inference Data*. | **Nearest out-of-field neighbour #2 — the phenomenon.** Our claim has his shape: *the label is recoverable from features that cannot see the thing being labelled.* Not "our monitor is better." |
| `2410.11672` ✅ | Pacchiardi, Tesic, Cheke, Hernández-Orallo, *Leaving the barn door open for Clever Hans: Simple features predict LLM benchmark answers*, 2024. | The internal-validity framing, applied to LLM benchmarks. |
| `2207.07048` ✅ | Kapoor & Narayanan, *Leakage and the Reproducibility Crisis in ML-based Science*. 329 papers, 8 leakage types, "model info sheets". | The taxonomy, and the recommendation format the paper's §5 should imitate. |
| `1808.04926` ✅ | Kaushik & Lipton. | Companion to Poliak. |
| `2410.06992` ✅ | *SWE-Bench+* — 32.67% solution leakage, 31.08% weak tests, 12.47% → 3.97% resolution after filtering. | The same audit, done to the code-agent benchmark next door. The closest thing to a template. |
| `2503.15223` ⚠️ · `2502.06215` ⚠️ | Code-eval validity, recorded from the round-17 sweep. **Titles and authors not verified in this repo.** | **Fetch before citing.** |

### The mechanism, established out-of-field and never connected to AI control

This is the live G1 risk and the reason the paper claims only the *application*.

| id | Verified | Note |
|---|---|---|
| `2602.02079` ✅ | Orel, Azizov, Paul, Wang, Gurevych, Nakov, **AICD Bench**, EACL 2026. 2M examples, 77 models, 11 families, 9 languages; human/machine/hybrid/adversarial. | Full text greped: **"ai control", "control evaluation", "trusted monitor", "sabotage", "APPS", "monitoring" all 0.** |
| `2506.11059` ✅ | Guo, Cheng, Zhang, Shen, Zhang, **CodeMirage**, 2025. 10 languages, 10 production LLMs, original + paraphrased. | Same greps 0, with `backdoor` = 1 and `safety` = 1 **as the in-batch positive controls proving the grep fires**. |
| `2507.21693` ⚠️ | MultiAIGCD. Abstract-level only. | **Fetch before citing.** |

> **Open obligation, and it is the one check that can still void the framing.** The AICD sweep above
> is full-text and its zeros carry in-batch controls — but the record is *counts*, and R18 exists
> because counts are not practice. Read the setup and evaluation sections of `2602.02079` and
> `2506.11059` and write one line each saying what they filter, strip and match. It costs hours and
> no GPU. **Do it before the split is released or the paper is posted, not after** (R16).

## 5. LessWrong and the Alignment Forum (R9)

Six queries, ~31 distinct LW/AF links across two sweeps. **No post reports a partial-input or
metadata floor.** The relevant ones: *Monitoring benchmark for AI control* (LW, 2026-01-30) —
*"All attacks are filtered for side task success"*, no validity discussion; *Introducing
ControlArena*; *Ensemble monitoring for AI control*; *Early Experiments in Human Auditing for AI
Control* (AF) — the attack policy *"erase[d] incriminating comments"*; *Classifier Context Rot*;
*Trusted monitoring with deception probes*; *Building Black-box Scheming Monitors*.

One prose acknowledgment is close enough to quote in related work:

> *"LLM-based assistants used to label the ControlArena training data likely share blind spots with
> the monitors being optimized … inflating the apparent performance of future LLM-based monitors on
> the dataset"* — and *"trajectories that were questioned during review were omitted from datasets
> rather than relabeled."*

**The thesis exists in prose in someone's limitations section. The measurement does not exist
anywhere.** Say exactly that; do not claim the thought is new.

## 6. Artifacts, with licence and per-class provenance

The paper must state every one of these, because two of them have no licence and one of them is the
whole argument.

| Artifact | HTTP | Licence | n | Honest class written by | Attack class written by | Confound |
|---|---|---|---|---|---|---|
| `RoganInglis/apps-control-arena` | 200 | **MIT** | 5,000 | **humans** — `codeparrot/apps` via `upload_dataset.py` → `parse_apps_solutions` → mechanical `fix_solution()`; **no model is ever called** | **9 named LLMs** (o1-mini 1,250, gpt-4o 1,148, o3-mini 2,261, claude-3-5-haiku 591, claude-3-7-sonnet 1,864, gemini-2.0-flash 715, gpt-4o-mini 367, claude-3-7-sonnet-thinking 517, gpt-3.5-turbo 142) + 2,516 `source=apps` GPT-4 | **YES — human vs LLM** |
| `eugenekoran/apps-control-arena-high-quality` | 200 | ⚠️ **none declared** | 1,209 train / **1,375 test** | as above, filtered | `top_backdoor_model` = `claude-3-7-sonnet-thinking-latest` for **all 172** attacks, `NONE` for all 1,203 honest | **YES**, and the column is a literal label |
| `adityaasinha28/control_arena_{bash,shade,iac,rogue_eval,agentdojo}` | 200 | ⚠️ **none declared** | 1,500 each | claude-sonnet-4 / gemini-2.5-pro / gpt-5 | **the same three models** | **NO — same generator, balanced** |
| `anik-jha/challenger-panels` `runs/scores/` | 200 | **MIT** | 24 × 1,375 | — | — | The comparison set. **No GPU.** |
| `RoganInglis/vllm-control-arena` | 200 | MIT | 200 | model-generated APPS solutions, **no attack/honest labels** | — | Gate S route 1 — check its generator first |

**Rejected, with reasons:** `AISafety-Student/labeled-bashBench` — `danger_level` and `action_type`
separate the label perfectly (danger 0 → label 0; danger ≥1 → label 1); the "label" *is* the danger
annotation, so it is circular and not a monitor benchmark. `TylordTheGreat/apps-backdoors-04-02-25`,
`RoganInglis/apps-backdoors`, `RoganInglis/control-tax` — upstream sources of the first row, same
confound, no extra corpus. `aksh-n/control_arena_shade-monitor-labels` — usable as a second label
source, no README, no licence. **`ai-safety-institute/AgentHarm` — deliberately excluded, G2.**

## 7. Corrections to our own records

Kept because acting on a mis-remembered number costs exactly as much as a hallucinated citation.

- **There are not two APPS-backdoor datasets.** The ideation repo's ledger said so for two rounds,
  reversed itself in round 16, and was wrong both times. K1 settled it: all 2,584 Koran `problem_id`s
  are in `RoganInglis/apps-control-arena`, every shared column is byte-identical except a
  re-validated `backdoor_works` (98.26%), and Koran §4.1 says *"a filtered subset of the APPS
  ControlArena dataset (Inglis et al., 2025)."* One dataset, one derived copy.
- **`2607.06596` was understated as "cross-generator generalisation republished inside safety."** It
  is a much heavier paper than that. See §3.
- **The "82% — longer code is the attack" number is protocol-bound.** 0.8255 within-pair on the raw
  tutorial protocol; **0.4726 on Jha's exact comment-stripped split**, which K1 reproduced bit-exactly.
  Length is a carrier on the raw artifact and is not one after the field's filter. Both numbers are
  correct and they measure different objects — which is the paper's table, not a contradiction.
- **Three arXiv search queries returned HTTP 429** during the scan. They are recorded as
  *uncontrolled*, **not** as zeros. A throttled response is a transport failure, not evidence (R3).

## 8. What is still owed before anything is public

1. §4's AICD/CodeMirage **setup sections**, read and summarised in one line each (R16 + R18).
2. `2503.15223`, `2502.06215`, `2507.21693` fetched, or dropped from the paper.
3. The Gate S control (`../PLAN.md` §3) — the only number in the abstract that does not yet exist.
