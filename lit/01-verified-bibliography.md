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
| `2503.15223` ✅ | Wang, Pradel, Liu, *Are "Solved Issues" in SWE-bench Really Solved Correctly? An Empirical Study*. v1 19 Mar 2025, **v2 9 Sep 2025 — cite v2**; DOI `10.1145/3744916.3764576` (ACM, so no longer preprint-only). PatchDiff differential patch testing: **7.8%** of patches pass while failing the developer test suite, **29.6%** behave differently from ground truth, reported resolution rates inflated by **6.2 pp**. | A genuine sibling to SWE-Bench+ — same weak-test validity failure, different mechanism. |
| `2502.06215` ✅ | Zhou, Weyssow, Widyasari, Zhang, He, Lyu, Chang, Zhang, Huang, Lo, *LessLeak-Bench: A First Investigation of Data Leakage in LLMs Across 83 Software Engineering Benchmarks*, 10 Feb 2025, v1, 25 pp. No venue stated. | ⚠️ **Do not pair this with SWE-Bench+ as though both report heavy leakage.** Its headline is that leakage is **minimal on average** — 4.8% Python, 2.8% Java, 0.7% C/C++ — with specific benchmarks failing badly (QuixBugs 100%, BigCloneBench 55.7%). It supports *"measure leakage per benchmark, because some fail badly"*, not *"leakage is pervasive."* |

### The mechanism, established out-of-field and never connected to AI control

This was the live G1 risk and the reason the paper claims only the *application*. **Both papers were
read end to end on 2026-09-03 — setup, evaluation, appendices, limitations — not greped** (R18). Raw
full texts were saved and every quote below was checked against the source by the coordinator (R17).

**Verdict: both NEIGHBOUR. The framing survives.** Neither paper connects AI-code detection to the
validity of any downstream safety, security, monitoring or backdoor benchmark, in any wording.

| id | Verified | Note |
|---|---|---|
| `2602.02079` ✅ | Orel, Azizov, Paul, Wang, Gurevych, Nakov, *AICD Bench: A Challenging Benchmark for AI-Generated Code Detection*. Submitted **2 Feb 2026, v1 only**; cs.LG primary, cs.SE. 2M examples, 77 generators (82 with quantizations), 11 families, 9 languages. | ⚠️ **Correction: the abs page states NO venue** — there is no `Comments:` field at all. This repo previously recorded "EACL 2026"; that attribution was unsourced and is **withdrawn** (R1). |
| `2506.11059` ✅ | Guo, Cheng, Zhang, Shen, Zhang, *CodeMirage: A Multi-Lingual Benchmark for Detecting AI-Generated and Paraphrased Source Code from Production-Level LLMs*. Submitted **27 May 2025, v1 only**; cs.SE primary. 10 languages, 10 production LLMs, original + paraphrased. | No venue stated. The `2506` id on a May-2025 date is real, not a transcription error. |

#### What they filter, strip and match — the R18 deliverable

**`2602.02079` (AICD Bench).** §4.1, and the rationale is the interesting part:

> *"We replicate Droid's filtering pipeline to maintain consistency in data distribution and **to
> prevent detectors from exploiting distributional artifacts rather than learning meaningful code
> patterns**."*

- Removes *"unparsable code, overly simple or excessively complex samples, non-code and auto-generated
  files, and non-English content."*
- Table 3 band-pass, applied to **both classes alike**: AST depth 2–31 · max line length 12–400 · avg
  line length 5–140 · **LOC 6–300** · alphanumeric fraction 0.20–0.75 · docstring English confidence
  99–100%. A shared band-pass, **not** a per-pair length match.
- MinHash de-duplication at threshold 0.8, *"applied jointly to the original and newly generated
  samples"* — which actively deletes near-identical cross-class pairs.
- **Classes are not matched** on length, difficulty or problem identity. Worse, class and source are
  partly confounded **by design**: the 50K human samples from The Heap and 100K hybrids from Swallow
  Code are loaded into the out-of-domain evaluation half.
- They name their own filter as a distortion of the human class (Limitations): it *"excludes highly
  verbose, overly complex, extremely short, or poorly structured code commonly found in practice."*

**`2506.11059` (CodeMirage).** §3.1, and it is the mirror image — **matched by construction**:

> *"To align the structural characteristics of the generated code with the original human-written
> version, we additionally supply the LLMs with **metadata such as the line count and total character
> length**."*

Enforced, not merely requested: *"a rule-based inspector that verifies: (1) consistency with the
original human-written code's line count and character length, and (2) adequate token-level
divergence from the original, enforced by requiring a BLEU score below 0.5 to avoid recitation.
Regeneration is forced if any check fails."* 1:10 human→machine mapping.

- Human class: CodeParrot `github-code-clean`, 1,000 files × 10 languages, *"collected and sanitized in
  May 2022, prior to the widespread deployment of code LLMs"* — the human label is guaranteed by date.
- Machine class: **text-to-code, never code-to-code** — an LLM summarizes each human file, and the
  summary alone is handed to 10 production LLMs, *"ensuring that the LLM does not access the original
  human-written implementation."*
- ✅ **They never strip comments and never discuss them.** `comment` and `docstring` occur **zero**
  times in the entire paper — verified against the raw HTML, not only the text conversion.

#### The three things this read found that a grep could not

1. **AICD runs our baseline, and it wins.** §5.1 trains LR / SVM / CatBoost over TF-IDF (uni-, bi- and
   tri-grams, no lowercasing, no normalisation, SVD to 500 dims). §5.2.1: *"classical models achieve
   unexpectedly strong performance: SVM and Logistic Regression with TF-IDF features **outperform all
   deep learning models**."* ⚠️ Their metric is **Macro-F1, not AUROC**, and on their hardest task the
   numbers are *below* random (SVM TF-IDF 43.05, best neural DeBERTa 34.13, Random 45.73). **Do not
   compare their number to ours** — that is R18's companion, and it is the exact error that killed the
   round-16 headline.
2. **AICD publishes our mechanism at token level, so we cannot claim it.** §5.2.1: *"language-independent
   cues, such as variable naming patterns, play a central role in distinguishing human-written from
   AI-generated code."* Appendix D.1: *"AI-generated code often uses verbose, prompt-echoing identifiers
   like answer, output, result, tests, and index. In contrast, human-written code tended to use shorter,
   organic identifiers like li, nums, pos, a1, and cur."* **Any interpretability claim about *which*
   tokens carry the authorship signal is pre-empted.** Cite it as established; keep to the application.
3. **The neighbouring field treats cross-class matching as a basic requirement — and that is an argument
   we did not have.** CodeMirage forces line-count and character-length agreement and gates on it;
   MultiAIGCD pairs to the same CodeNet problem definitions; AICD filters explicitly to stop detectors
   exploiting distributional artifacts. **Three independent AI-code-detection papers spend engineering
   effort on the control the AI-control monitoring benchmarks never applied.** The absence is therefore
   a defect *by the neighbouring field's own published standard*, not by a standard we invented for the
   occasion. This belongs in §1 and in the recommendations.

#### The nearest sentence each paper has to our claim, verbatim

- `2602.02079` §4.1 — the anti-artifact rationale quoted above. It is our confound logic applied
  **inward**, to protect their own benchmark, never outward to anyone else's.
- `2506.11059` §1 — *"Robust AI-code detection is therefore critical for secure software supply
  chains, responsible academic practice, and licence compliance."* Detection as useful, not authorship
  as a contaminant of someone else's labels.
- ⚠️ **One CodeMirage claim points the other way and is worth citing honestly.** §3.2, from
  distribution overlap in lines of code, character length and AST depth: *"This similarity implies that
  naive statistical classifiers would struggle to detect AI-generated code using basic code features."*
  **It is asserted from overlapping histograms and never tested with an actual naive classifier** — and
  it is true *of their matched construction*, which is precisely our point about the unmatched one.

#### Loose ends closed

- **CodeMirage's single `backdoor` hit is benign.** It is reference [91] in the bibliography (Yan et al.,
  USENIX Security 2024, an LLM-assisted backdoor attack on **code completion models** — training-data
  poisoning), cited once in §1's motivation sweep. Not a code-backdoor benchmark, not APPS, not
  monitoring. **Chased and closed.**
- Control-term counts on both full texts, with in-batch positive controls: `ai control`, `control
  evaluation`, `trusted monitor`, `sabotage`, `APPS`, `monitoring` = **0** in both; `backdoor` and
  `safety` = 0 in AICD, 1 each in CodeMirage. Positive controls fire (`detection` 50 / `detect` 174,
  ` the ` 303 / 326, `TF-IDF` 26, `paraphras` 60).

| id | Verified | Note |
|---|---|---|
| `2507.21693` ✅ | Demirok, Kutlu, Mergen, *MultiAIGCD: A Comprehensive dataset for AI Generated Code Detection Covering Multiple Languages, Models,Prompts, and Scenarios*, 29 Jul 2025, v1. Python/Java/Go from CodeNet problem definitions; 6 LLMs × 3 prompts × 3 scenarios; **121,271 AI-generated / 32,148 human-written**. | The missing space in *"Models,Prompts"* is in the official arXiv title. **A third instance of point 3 above** — paired to the same problem definitions as the human code. |

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
| ~~`RoganInglis/vllm-control-arena`~~ | 200 | MIT | **6,801** | ⛔ **This row was wrong.** It holds **no APPS data and no code at all** — 6,801 coding *task descriptions* mined from vLLM git commits (`commit_hash`, `task_instructions`, twelve `overlap_*` side-task scores; **zero** code, solution, `problem_id` or label columns). Its card names `claude-3-7-sonnet-latest` as having written the **task text**, not solutions. Verified against the full parquet 2026-09-04. | — | **Gate S route 1 is DEAD.** No overlap with Koran's filter is even computable. |

> ### ⛔ Two more free-control candidates checked and killed, 2026-09-04
> The rule is to look before generating, so every plausible source of **LLM-written honest APPS code**
> was checked, not just the one the plan named.
>
> **`RoganInglis/control-tax` (MIT, 2,368 rows) — its dataset card is FALSE.** The card claims
> verbatim: *"`solutions`: List of model-generated solutions (**one per model**), sorted by whether they
> pass tests and compile"* with a matching *"`models`: List of model names."* Recomputed on the full
> parquet: **8,855 solution entries, byte-identical within all 2,368 rows, 2,366 distinct strings in
> total.** The list is *one* solution duplicated once per attacker model to align positionally with
> `backdoors`. 2,074/2,368 are verbatim upstream `codeparrot/apps` human solutions; of the remaining
> 294, median similarity to a human solution is 0.984 and 271 contain `exit()` — the card's own note
> that top-level returns were rewritten. **Zero LLM-written honest solutions.**
> *(Recorded coverage in case it is ever useful: 2,368 pids, all inside `apps-control-arena`; 2,055 of
> Koran's 2,584; 871 of the 1,375 test rows.)*
>
> **`jprivera44/arena-control-apps-v5-dataset`** (1,793 rows; 765 honest / 1,028 backdoored) — all 765
> honest rows checked: 426 verbatim upstream human APPS, the rest at median similarity 0.980. **Also
> human.**
>
> ⚠️ The 294 + 339 non-verbatim rows are established as human by high similarity plus the documented
> `exit()` rewrite, **not** by byte equality — inference from a computed distribution, not proof per
> file. It does not move the verdict: neither repo carries any per-model variation to offer.

> ### ★ The confound is legible in the schema itself — the cleanest evidence we have
> In `RoganInglis/apps-control-arena`, verified from the dataset info endpoint on 2026-09-04:
>
> | struct | sub-fields |
> |---|---|
> | `solutions` | `code`, `compiles`, `passes_tests` |
> | `backdoors` | `backdoor_code`, `backdoor_input`, `backdoor_works`, `compiles`, **`model`**, `passes_tests`, **`source`** |
>
> **The attack class records which model wrote it. The honest class has no generator field, because
> there is no generator.** The card says so too: *"This dataset is based on the codeparrot/apps dataset,
> enhanced with backdoor solutions from two sources."* This is a one-line statement of the paper's whole
> thesis, and it belongs in §2 of the paper — it needs no AUROC to be convincing.

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

1. ~~The AICD/CodeMirage setup sections, read and summarised.~~ ✅ **Discharged 2026-09-03** — §4. Both
   NEIGHBOUR; the framing survives; three findings a grep could not have produced.
2. ~~`2503.15223`, `2502.06215`, `2507.21693` fetched or dropped.~~ ✅ **All three verified** — §4. One
   *characterisation* correction, not a bibliographic one: LessLeak-Bench reports leakage as minimal on
   average, and must not be cited as though it reports the opposite.
3. **The Gate S control** (`../PLAN.md` §3) — the only number in the abstract that does not yet exist.
