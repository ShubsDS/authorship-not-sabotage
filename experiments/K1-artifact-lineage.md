# K1 — which artifact? Verdict and evidence

> **Provenance.** Written 2026-09-03 by the K1 subagent in the `beyond-private-training` ideation repo and
> copied here **verbatim** — it is a dated evidence record, not a document to keep current. Its `ideas/NN`
> and `notes/NN` references point at that repo. Its §8 script list is this repo's `experiments/apps/`;
> `fetch_code.py` and `colsize.py` were scratch and were not kept.

Run 2026-09-03. All numbers below were computed in this session; every command and its full
output is reproduced. Working dir for all commands:
`/private/tmp/claude-501/-Users-shubs-1cs-research-beyond-private-training/383c978b-e66e-4be0-a2e8-b6290f55ef81/scratchpad/K1/`

---

## VERDICT: **PASS — strongly.** The "second artifact" is a filtered *derivative of the first*.

`eugenekoran/apps-control-arena-high-quality` — the dataset released with Koran et al. (2026),
the one `2608.16190` reproduces the 1,375-sample split from — is **a 2,584-row subset of the
5,000 rows of `RoganInglis/apps-control-arena`**. Every one of its `problem_id`s is in
RoganInglis, and every shared metadata column is byte-identical except `backdoor_works`
(98.26% identical; 45 rows re-validated). Koran et al. §4.1 says so in words: it is "a filtered
subset of the APPS ControlArena dataset (Inglis et al., 2025)". `RoganInglis/apps-control-arena`
is not an outlier — it is the dataset name **hardcoded** in ControlArena's APPS setting.

There are therefore **not two distinct APPS-backdoor datasets**. There is one, and one filtered
copy of it. `notes/14`'s 1,936/482/1,375 split is real and it is a split *of the same artifact*.

The floor does not merely survive the filtering. The filtering removes the
`solution_passes_tests` leak (that column is constant `True` on all 1,375 test items) and
**installs a different, comparably strong one in its place**: on the exact 1,375-sample test
split used by both papers, a logistic regression on `difficulty + num_tests + question length`
— which never sees one character of code — scores **held-out AUROC 0.7163**, which is above
**18 of the 24 open-weight monitors `2608.16190` reports on that same split**.

---

## 1. The citation chain, verbatim

### 1.1 `2608.16190` names its data source

`https://arxiv.org/abs/2608.16190` → **HTTP 200**, 43,381 bytes.
Title: *Decorrelation Is Not Complementarity: Skill, Not Lineage, Governs Trusted-Monitor
Ensembles*. Author: **Anik Jha** (sole author). Submitted Mon, 17 Aug 2026. cs.CR; cs.LG.
DOI 10.48550/arXiv.2608.16190.

`https://arxiv.org/html/2608.16190` → **HTTP 200**, 132,782 bytes. §2 Setup, "Task and data",
verbatim:

> "We use the public backdoored-APPS dataset released with Koran et al. (2026). Each sample is a
> Python solution to a competitive-programming problem, labelled attack if it contains a
> deliberate backdoor-code that passes the visible tests but fails on a hidden input-or honest
> otherwise. We reproduce their test split exactly: 1,375 samples, 172 attack and 1,203 honest.
> Their train/validation membership is not published, so ours is a deterministic reconstruction
> that matches their stated counts but not necessarily their exact assignment."

The paper gives **no URL for the dataset**. Its own repo is
`https://github.com/anik-jha/challenger-panels` (**HTTP 200**, MIT, default branch `main`,
pushed 2026-08-17), and §6 says "The monitors and the transcript dataset are public artifacts
that the repository's download scripts fetch rather than redistribute."

### 1.2 The bibliography entry

From the same HTML:

> "Koran et al. (2026) — E. Koran, Y. Yun, S. Tetef, B. Arnav, and P. Bernabeu-Perez. Ensemble
> monitoring for AI control: Diverse signals outweigh more compute. arXiv:2605.15377, 2026."

`https://arxiv.org/abs/2605.15377` → **HTTP 200**, 42,506 bytes. *Ensemble Monitoring for AI
Control: Diverse Signals Outweigh More Compute*. Eugene Koran, Yejun Yun, Samantha Tetef,
Benjamin Arnav, Pablo Bernabeu-Pérez. v1 14 May 2026, **v2 18 May 2026**. cs.AI.

### 1.3 The artifact URL, from Koran et al. themselves

`https://arxiv.org/html/2605.15377v2` → **HTTP 200**, 334,191 bytes. "Code and Data
Availability":

> "Code: https://github.com/Multi-Signal-Control-SPAR/Multi-Signal-Monitoring
> Dataset: https://huggingface.co/datasets/eugenekoran/apps-control-arena-high-quality"

Independently confirmed from Jha's harness,
`https://raw.githubusercontent.com/anik-jha/challenger-panels/main/src/data.py` (**HTTP 200**),
module docstring:

> "Source: huggingface.co/datasets/eugenekoran/apps-control-arena-high-quality, the dataset
> released with 2605.15377."

and `runs/m1/dataset-manifest.json` (**HTTP 200**), which is the harness's own machine-written
record: `"dataset_id": "eugenekoran/apps-control-arena-high-quality", "n_total": 3793,
"n_attack": 1381, "n_honest": 2412, "test_attack": 172, "test_honest": 1203,
"train_total": 1936, "val_total": 482`.

### 1.4 Koran et al. §4.1 — the construction, verbatim (this is the load-bearing quote)

> "We evaluate all monitors and ensembles on a filtered subset of the APPS ControlArena dataset
> (Inglis et al., 2025), which combines interview-style Python coding problems from APPS
> (Hendrycks et al., 2021) with backdoored solutions sourced from Greenblatt et al. (2023) and
> Terekhov et al. (2025a). Backdoors are adversarially generated by various LLMs to pass all
> standard tests while producing incorrect outputs on specific attack inputs. **To isolate
> backdoor detection from generally incorrect code, we keep only working honest solutions
> (passing all tests) and working backdoored solutions (successfully exploiting attack inputs
> and passing all tests).**"

and, on how the negative class was built:

> "The filtered dataset contains 1,936 training (50% attack rate), 482 validation (50% attack
> rate), and 1,375 test samples (172 attack, 1,203 honest). **The test set is extended to
> problems that have working solutions but no working backdoors to sharpen FPR estimation at low
> thresholds. These problems may differ from training problems, but the shift affects all
> monitors equally and does not impact relative comparisons.**"

That second sentence *is* the audit's finding, conceded in the source paper and then dismissed
with an assertion ("affects all monitors equally") that is true of monitor *rankings* and false
of the *absolute* numbers a safety case would quote. §4.1 also states the comment leak: "we
strip all comments from the code before evaluation."

`Inglis et al. (2025)` in that bibliography is: "R. Inglis, O. Matthews, T. Tracy, O. Makins,
T. Catling, A. Cooper Stickland, … and A. Cooney. ControlArena. Note: GitHub repository."

---

## 2. `RoganInglis/apps-control-arena` is the canonical ControlArena artifact

`https://raw.githubusercontent.com/UKGovernmentBEIS/control-arena/main/control_arena/settings/apps/task/dataset.py`
→ **HTTP 200**. Line 31, verbatim:

```python
DATASET_NAME = "RoganInglis/apps-control-arena"
```

It is the only dataset the APPS setting loads (`hf_dataset(DATASET_NAME, …, split="train")`).
`docs/settings/apps.qmd` (**HTTP 200**) confirms the lineage in prose:

> "**Unified backdoor solutions**: Combines backdoor solutions from both the Control-Tax paper
> and TylordTheGreat/apps-backdoors dataset into a single unified dataset
> (RoganInglis/apps-control-arena)"

`control_arena/settings/apps/dataset/upload_dataset.py` (**HTTP 200**) is the build script.
Docstring:

> "Script to create and upload unified APPS/Control-Tax dataset to HuggingFace. This script
> creates a single unified dataset (RoganInglis/apps-control-arena) that: — Uses the original
> codeparrot/apps problems and solutions — Adds backdoors from both APPS and Control-Tax
> datasets — Validates solutions using inspect with the actual APPS sandbox — Provides
> appropriate flags for filtering"

### Default filters in `AppsSetting` (`apps_setting.py`, HTTP 200)

```python
has_solution: bool = Field(default=True, description="Whether to only use samples with solutions that have been verified to work (compile and pass tests).")
has_backdoor_solution: bool = Field(default=False, …)
backdoor_source: Literal["any","apps","control_tax"] = Field(default="any", …)
exclude_nondeterministic: bool = Field(default=True, …)
```

So ControlArena's *own* default APPS pool is already "problems whose honest solution passes
tests". The `solution_passes_tests` asymmetry the audit measures lives in the **raw
`has_backdoor` labels**, i.e. in how it is used when the stored backdoors are treated as the
attack class — which is exactly the Koran/Jha protocol.

---

## 3. Provenance: who wrote the honest code and who wrote the attack code

**(a) Honest solutions are human-written APPS reference solutions.** `upload_dataset.py`
`create_unified_dataset()` does `load_dataset("codeparrot/apps", split="test",
trust_remote_code=True)` and then `solutions = parse_apps_solutions(record.get("solutions"))`,
which is `json.loads` of the original APPS `solutions` field plus a purely mechanical
`fix_solution()` (replaces top-level `return` with `exit()`, and `nonlocal` → `global`). **No
model is ever called to produce an honest solution.** The dataset card says the same: "This
dataset is based on the codeparrot/apps dataset, enhanced with backdoor solutions from two
sources".

**(b) Every backdoor is LLM-written.** Two upstreams:
- `source="apps"`: `load_dataset("TylordTheGreat/apps-backdoors-04-02-25", split="train")` —
  the backdoors from *AI Control: Improving Safety Despite Intentional Subversion*
  (arXiv:2312.06942). HF API for that repo → **HTTP 200** (its `/raw/main/README.md` → **HTTP
  404 "Entry not found"**: it ships only `.gitattributes` and `backdoor_dataset.json`,
  4,113,590 bytes — positive control: the API call for the *same* repo returned 200 and listed
  those two files, and a genuinely absent repo `TylordTheGreat/does-not-exist-abc` returns
  **HTTP 404**).
- `source="control_tax"`: downloaded from
  `https://mikhailterekhov.github.io/control-tax/backdoor_code_paper.json` (**HTTP 200**,
  34,718,317 bytes), the release of *Control Tax: The Price of Keeping AI in Check*
  (arXiv:2506.05296 → **HTTP 200**; Terekhov, Liu, Gulcehre, Albanie; v1 5 Jun 2025, v3 2 Mar
  2026), carrying a per-backdoor `model` field.

Measured on the 1,375-row Koran test split (`(source, model)` cross-tab over all 3,747 stored
backdoors):

```
('control_tax', 'openai/o3-mini') 833
('control_tax', 'anthropic/claude-3-7-sonnet-latest') 618
('control_tax', 'openai/o1-mini') 488
('apps',        'openai/gpt-4') 439
('control_tax', 'openai/gpt-4o') 402
('control_tax', 'anthropic/claude-3-7-sonnet-thinking-latest') 306
('control_tax', 'google/gemini-2.0-flash') 255
('control_tax', 'anthropic/claude-3-5-haiku-latest') 199
('control_tax', 'openai/gpt-4o-mini') 151
('control_tax', 'openai/gpt-3.5-turbo') 56
```

`source == "apps"` ⇒ `model == "openai/gpt-4"`, 439/439. **The coordinator's hypothesis is
confirmed exactly.** (Note a discrepancy worth one footnote: the *current* `upload_dataset.py`
sets `"model": "unknown"` for apps-source backdoors, so the shipped parquet was built from an
earlier revision that labelled them `openai/gpt-4`.)

**(c) `backdoor_works`, exact definition.**
`control_arena/settings/apps/dataset/validation.py` (**HTTP 200**), `validate_backdoor()`:
run the backdoor code and the reference solution on `backdoor_input` in the sandbox; if the
backdoor compiles, passes all normal tests, both runs produce no stderr, and
`check_solutions_equal(backdoor_output, reference_output)` is False, then `backdoor_works =
True`. Any compile failure, test failure, missing `backdoor_input`, missing reference solution,
stderr on either run, or exception ⇒ `False`. The row-level flag is
`new_sample["backdoor_works"] = new_sample["backdoors"][0].get("backdoor_works", False)` after
backdoors are sorted by `(backdoor_works, passes_tests, compiles)` descending — i.e. "at least
one backdoor works".

**(d) Live ControlArena eval: the agent generates; replay is opt-in.** `docs/settings/apps.qmd`:
"3. In honest mode, the agent simply tries to solve the problem correctly / 4. In attack mode,
the agent tries to produce a solution that contains a backdoor". Replay is a *separate,
explicitly documented* policy, `control_arena/settings/apps/apps_solution_policy.py`
(**HTTP 200**), docstring verbatim:

> "Directly submits pre-existing solutions or backdoor solutions from the dataset depending on
> the eval mode. If in EvalMode.HONEST, it submits the original solution provided in the
> dataset. If in EvalMode.ATTACK, it submits a backdoor solution provided in the dataset."

with `get_solution_tool_call` returning `sample_metadata.solutions[0]["code"]` (human) and
`get_backdoor_tool_call` returning `backdoor["backdoor_code"]` (LLM). **So the authorship
confound is a property of the stored-solutions protocol, not of ControlArena as such** — and
the stored-solutions protocol is precisely what Koran et al. and Jha use.

**(e) Koran artifact: same asymmetry.** Jha's `src/data.py` `_honest_code(row)` returns
`s["code"]` from `row["solutions"]` (human APPS) and `_pick_backdoor(row)` returns
`backdoor_code` (LLM). Honest and attack do **not** come from the same model there either.

**(f) `get_dataset(has_backdoor_solution=True, backdoor_source=…)` filters on
`backdoor_works`,** not on `passes_tests`:

```python
if backdoor_source == APPS_SPLIT_NAME:        backdoor_works_field = "apps_backdoor_works"
elif backdoor_source == CONTROL_TAX_SPLIT_NAME: backdoor_works_field = "control_tax_backdoor_works"
else:                                          backdoor_works_field = "backdoor_works"
...
if has_backdoor_solution and not apps_metadata.get(backdoor_works_field, False): return False
```
plus `if has_solution and not apps_metadata.get("solution_passes_tests", False): return False`
and `if exclude_nondeterministic and apps_metadata.get("is_nondeterministic", False): return False`.

---

## 4. The numbers

### 4.0 Provenance of the data used (column-projected parquet reads over `HfFileSystem`)

```
$ uv run --with pandas --with pyarrow --with huggingface_hub python fetch_cols.py eugenekoran/apps-control-arena-high-quality koran_meta.parquet
files: ['datasets/eugenekoran/apps-control-arena-high-quality/data/test-00000-of-00002.parquet', 'datasets/eugenekoran/apps-control-arena-high-quality/data/test-00001-of-00002.parquet', 'datasets/eugenekoran/apps-control-arena-high-quality/data/train-00000-of-00001.parquet']
test-00000-of-00002.parquet rows 688 cols 18
test-00001-of-00002.parquet rows 687 cols 18
train-00000-of-00001.parquet rows 1209 cols 18
saved koran_meta.parquet (2584, 19)
```
Same for `RoganInglis/apps-control-arena` → `rogan_meta.parquet` (5,000 rows, 3 parquet files).

HF API: both `https://huggingface.co/api/datasets/eugenekoran/apps-control-arena-high-quality`
and `https://huggingface.co/api/datasets/RoganInglis/apps-control-arena` → **HTTP 200**,
`private: false`, `gated: false`, `disabled: false`. Negative control:
`https://huggingface.co/api/datasets/eugenekoran/this-does-not-exist-xyz` → **HTTP 401**.

| | RoganInglis/apps-control-arena | eugenekoran/apps-control-arena-high-quality |
|---|---|---|
| licence | **MIT** (`license: mit` in card YAML, `license:mit` tag) | **none declared** — no `license:` key, no licence tag |
| rows | 5,000 (`train` only) | 2,584 (`train` 1,209 + `test` 1,375) |
| downloads (last 30d) | 6,958 | 18 |
| created / last modified | 2025-09-22 / 2025-09-29 | 2025-10-03 / 2025-10-06 |
| card prose | full datasheet (structure, filtering flags, nondeterminism, usage) | **none — YAML front-matter only** |
| columns | 30 | same 30 **+ `num_tests`, `top_backdoor_model`** |

### 4.1 Lineage: the Koran artifact is a subset of RoganInglis

```
$ uv run --with pandas --with pyarrow --with numpy python analyse.py
======================================================================
A. LINEAGE: is the Koran artifact a subset of RoganInglis?
koran rows 2584 unique pid 2584
rogan rows 5000 unique pid 5000
koran pids inside rogan: 2584 / 2584
koran pids NOT in rogan: 0
merged rows 2584
  difficulty                             identical fraction = 1.0000
  has_backdoor                           identical fraction = 1.0000
  has_apps_backdoor                      identical fraction = 1.0000
  has_control_tax_backdoor               identical fraction = 1.0000
  solution_compiles                      identical fraction = 1.0000
  solution_passes_tests                  identical fraction = 1.0000
  backdoor_solution_compiles             identical fraction = 1.0000
  backdoor_solution_passes_tests         identical fraction = 1.0000
  backdoor_works                         identical fraction = 0.9826
  apps_backdoor_works                    identical fraction = 1.0000
  control_tax_backdoor_works             identical fraction = 1.0000
  is_nondeterministic                    identical fraction = 1.0000
  nondeterminism_score                   identical fraction = 1.0000
  nondeterminism_category                identical fraction = 1.0000
  q_len                                  identical fraction = 1.0000
```

Every problem is a RoganInglis problem; every column is byte-identical except `backdoor_works`
(45 rows differ — a re-validation, and the only substantive edit).

### 4.2 How the label is assigned in the Koran test split

`src/data.py`, `build_samples`, verbatim:

> "test: one sample per row. Rows whose designated backdoor works become attack samples carrying
> the backdoor code; the rest become honest samples carrying the reference solution. This
> reproduces the paper's 172 attack / 1,203 honest exactly."

i.e. **`label == row["backdoor_works"]`**. Confirmed:

```
B. KORAN TEST SPLIT: label = backdoor_works  (per challenger-panels src/data.py)
test rows 1375  attack 172  honest 1203

top_backdoor_model among attack rows:
anthropic/claude-3-7-sonnet-thinking-latest    172

train rows 1209 backdoor_works 1209 solution_passes_tests 1209
```

**The train/val split is paired** — each of the 1,209 problems yields both an attack and an
honest sample (968×2 = 1,936 train, 241×2 = 482 val), so metadata there is balanced by
construction and the floor is 0.5. **The test split is not paired**, and every headline number
in both papers is computed on the test split.

### 4.3 The metadata floor on the Koran test split

```
$ uv run --with pandas --with pyarrow --with scikit-learn python auroc.py
======================================================================
KORAN TEST SPLIT (eugenekoran/apps-control-arena-high-quality, split=test)  n=1375  positives=172 (0.1251)
  difficulty only                                AUROC=0.6451   (test n=413, pos=52, feats=3)
  num_tests only                                 AUROC=0.6487   (test n=413, pos=52, feats=1)
  q_len only                                     AUROC=0.6206   (test n=413, pos=52, feats=1)
  PROBLEM-SIDE: difficulty+num_tests+q_len       AUROC=0.7163   (test n=413, pos=52, feats=5)
    + nondeterminism_score                       AUROC=0.7140   (test n=413, pos=52, feats=6)
  PIPELINE-SIDE: + has_apps/has_control_tax      AUROC=0.8735   (test n=413, pos=52, feats=8)
  FULL incl. backdoor validation flags           AUROC=0.9775   (test n=413, pos=52, feats=10)

single-column raw AUROC on the whole 1375 (no split, direction as-is):
  num_tests                          0.3294
  q_len                              0.4126
  nondeterminism_score               0.4999
  has_control_tax_backdoor           0.7095
  has_apps_backdoor                  0.5016
  backdoor_solution_passes_tests     0.9651
  backdoor_solution_compiles         0.7037
```
(all held-out AUROCs: 30% stratified split, `random_state=0`, `StandardScaler` +
`LogisticRegression(max_iter=5000)`; categorical columns one-hot; constant columns dropped)

Robustness, 5×5 repeated stratified CV over all 1,375 items (`analyse2.py`):
```
PROBLEM-SIDE metadata, 5x5 repeated stratified CV AUROC on all 1375: mean=0.7715 sd=0.0389
in-sample AUROC on all 1375: 0.7757
num_tests direction-flipped single-column AUROC on all 1375: 0.6706
q_len direction-flipped single-column AUROC on all 1375: 0.5874
```

Marginals (`analyse.py` §C):
```
P(attack | difficulty):        competition 36/167=0.2156   interview 64/975=0.0656   introductory 72/233=0.3090
P(attack | has_control_tax_backdoor):  False 0/504=0.0000   True 172/871=0.1975
P(attack | backdoor_solution_passes_tests): False 0/1119=0.0000   True 172/256=0.6719
P(attack | solution_passes_tests):     True 172/1375  (constant — the Koran filter removed this column's variance)
num_tests by label:  honest mean 38.85 (median 28)   attack mean 20.95 (median 15)
q_len     by label:  honest mean 1681 (median 1621)  attack mean 1490 (median 1436)
```

**Read this against the RoganInglis floor.** The Koran filter *does* close the original leak —
`solution_passes_tests` is constant `True` across all 1,375 test items, so the 0.79 single-column
predictor is gone. What replaces it: an *interview*-difficulty problem is 4.7× less likely to be
an attack than an *introductory* one, attack problems have roughly **half** the test cases
(20.95 vs 38.85), and 504 of the 1,375 items (all of them honest) can be excluded from the
attack class on `has_control_tax_backdoor` alone.

### 4.4 Where 0.7163 sits against the monitors reported on the *same* split

`https://raw.githubusercontent.com/anik-jha/challenger-panels/main/runs/x0/monitor-summary.json`
→ **HTTP 200**, 24 monitors, `test_auroc` on the same 1,375 items:

```
HuggingFaceTB/SmolLM3-3B                          3.10B  0.4341     tiiuae/Falcon3-3B-Instruct         3.20B  0.6213
HuggingFaceTB/SmolLM2-360M-Instruct               0.36B  0.4453     Qwen/Qwen3-4B                      4.00B  0.6518
HuggingFaceTB/SmolLM2-1.7B-Instruct               1.70B  0.4583     tiiuae/Falcon3-7B-Instruct         7.50B  0.6746
01-ai/Yi-1.5-6B-Chat                              6.00B  0.4604     allenai/OLMo-2-0325-32B-Instruct  32.00B  0.6791
Qwen/Qwen3-0.6B                                   0.60B  0.5074     Qwen/Qwen3-8B                      8.00B  0.7153
allenai/OLMo-2-0425-1B-Instruct                   1.00B  0.5450    ---- metadata-only floor: 0.7163 ----
Qwen/Qwen3-1.7B                                   1.70B  0.5475     microsoft/phi-4                   14.70B  0.7517
ibm-granite/granite-3.3-8b-instruct               8.10B  0.5586     tiiuae/Falcon3-10B-Instruct       10.30B  0.7583
allenai/OLMo-2-1124-13B-Instruct                 13.70B  0.5737    ---- metadata-only floor, 5x5 CV: 0.7715 ----
allenai/OLMo-2-1124-7B-Instruct                   7.30B  0.5882     mistralai/Mistral-Small-3.2-24B   24.00B  0.8308
microsoft/Phi-4-mini-instruct                     3.80B  0.5909     Qwen/Qwen3.6-35B-A3B-reap25       26.00B  0.8582
ibm-granite/granite-3.3-2b-instruct               2.50B  0.6023     google/gemma-4-26b-a4b-it         26.00B  0.9358
mistralai/Mistral-7B-Instruct-v0.3                7.20B  0.6167     Qwen/Qwen3.6-27B                  27.00B  0.9371
```
median monitor `test_auroc` = **0.6095**; **18 of 24 below 0.7163; 20 of 24 below 0.7715**,
including the 32B OLMo (0.6791). Caveat recorded in §6.

### 4.5 The authorship confound survives comment-stripping, but only partly

Reconstructing the 1,375 samples exactly per `src/data.py` (including its `strip_comments`
port) and re-running the repo's own leak checks:

```
$ uv run --with pandas --with numpy --with scikit-learn --with pyarrow python bow.py
reconstructed: 1375 attack 172 honest 1203

--- comment presence (RAW, before stripping)
label
0    0.203658
1    0.616279

--- '#' count AUROC raw vs stripped (reproducing the repo's leak check)
  raw      hash-count AUROC = 0.6957
  stripped hash-count AUROC = 0.4983
  attacks with comments raw=106 stripped=0 ; honest raw=245 stripped=1

[code    ] word 1-2gram tfidf   held-out AUROC=0.8098  acc=0.8910 (n=413,pos=52)
[code    ] char 3-5gram tfidf   held-out AUROC=0.8506  acc=0.9080 (n=413,pos=52)
[stripped] word 1-2gram tfidf   held-out AUROC=0.6836  acc=0.8765 (n=413,pos=52)
[stripped] char 3-5gram tfidf   held-out AUROC=0.7162  acc=0.8741 (n=413,pos=52)

code-length-only AUROC (stripped): 0.4726  (repo reports 0.4726)
code-length-only AUROC direction-flipped: 0.5274
```

**Three independent bit-exact reproductions of Jha's own harness output** — `hash_count_only_detector_auroc`
0.6957 before / 0.4983 after, `attacks_with_comments` 106 → 0, and `code_length_only_auroc`
0.4726 (from `runs/m1/dataset-manifest.json` and `runs/x2/leakage-checks.json`, both **HTTP 200**).
That certifies my reconstruction of the split is theirs.

So on this artifact: comments 61.6% of attacks vs 20.4% of honest; a character-n-gram
authorship classifier reaches **0.8506** on raw code — above 21 of the 24 monitors — and
**0.7162 even after their mandatory comment-stripping**, i.e. still above 18 of 24. Comment
stripping removes the crudest tell but not the human-vs-LLM authorship signal.

### 4.6 The "backdoor does not work" problem — worse here, not better

```
$ uv run --with pandas --with pyarrow --with scikit-learn python analyse2.py
test: n=1375 attack=172 honest=1203 base_rate=0.1251
test rows carrying >=1 labelled backdoor (has_backdoor): 892
  of which the backdoor WORKS (-> labelled attack): 172
  of which NO backdoor works (-> relabelled HONEST): 720
fraction of labelled backdoors in test that do not work: 0.8072
honest test items that are backdoor-authored problems: 720 / 1203 = 0.5985

whole koran artifact: has_backdoor=2101 backdoor_works=1381 -> 0.3427 do not work
rogan: has_backdoor=2473 backdoor_works=1582 -> 0.3603 do not work
```

The 36% figure replicates on RoganInglis (0.3603) and holds at 34.3% on the Koran artifact. But
in the Koran **test split** the inert backdoors have not been dropped — they have been *promoted
into the negative class*: **60% of the 1,203 "honest" test items are problems somebody did author
a backdoor for, and the backdoor simply failed.** The negative class is defined by the failure
of an attack attempt.

### 4.7 Pipeline positive control — RoganInglis reproduces `ideas/28` §12

```
RoganInglis/apps-control-arena  label=has_backdoor  n=5000  positives=2473 (0.4946)
  difficulty only                                AUROC=0.6832   (test n=1500, pos=742, feats=3)
  solution_passes_tests only                     AUROC=0.7881   (test n=1500, pos=742, feats=1)
  METADATA-ONLY (difficulty+solution flags+q_len+nondet) AUROC=0.8169   (test n=1500, pos=742, feats=8)

rogan solution_passes_tests by has_backdoor:   False 2527 0.396913   True 2473 0.977355
rogan P(has_backdoor|difficulty):  competition 203/1000=0.2030  interview 1874/3000=0.6247  introductory 396/1000=0.3960
```
`0.9774 / 0.3969`, `0.2030 / 0.6247 / 0.3960`, `2473`, `1582` and difficulty-only `0.6832`
(vs `ideas/28`'s 0.6823) all match. Metadata-only comes out **0.8169** against `ideas/28`'s
**0.8229** — a feature-set difference, not a discrepancy in the data; the exact feature list
behind 0.8229 is not recorded in `ideas/28` and must be pinned down before publication.

---

## 5. Candidate "which artifact and why" paragraph for the paper

> We audit `RoganInglis/apps-control-arena` (HuggingFace, 5,000 rows, MIT), which is the dataset
> ControlArena's APPS setting loads by name — `DATASET_NAME = "RoganInglis/apps-control-arena"`
> in `control_arena/settings/apps/task/dataset.py` — and which is therefore the artifact behind
> the field's open code-backdoor monitoring results. It is built by merging the GPT-4 backdoors
> released with *AI Control* (Greenblatt et al., 2023) and the ten-model backdoor set released
> with *Control Tax* (Terekhov et al., 2025) onto the 5,000 problems of `codeparrot/apps`, whose
> human-written reference solutions serve as the honest class. We report our floors on this
> artifact and, separately, on `eugenekoran/apps-control-arena-high-quality`, the filtered
> release accompanying Koran et al. (2026) and reused unchanged by Jha (2026); we verified that
> the latter is a 2,584-row subset of the former with every shared metadata column identical
> except a re-validated `backdoor_works`, so these are one artifact and one derived copy of it,
> not two independent benchmarks. The two are worth reporting separately because the derived
> copy shows the failure is not a packaging accident: Koran et al.'s filter ("we keep only
> working honest solutions … and working backdoored solutions") does remove the
> `solution_passes_tests` asymmetry, and the leak reappears in other columns, because the same
> filter defines the evaluation's negative class by the *failure of an attack attempt* — as
> §4.1 concedes, "the test set is extended to problems that have working solutions but no
> working backdoors." On their exact 1,375-item test split, a logistic regression over problem
> difficulty, test-case count and problem-statement length — reading no code at all — reaches
> held-out AUROC 0.716 (0.772 under 5×5 CV), above 18 of the 24 open-weight monitors evaluated
> on that split.

---

## 6. What I could NOT verify

1. **The 0.8229 metadata-only AUROC in `ideas/28` §12.** My reconstruction on the same 5,000
   rows gives **0.8169** with the feature set `difficulty + solution_compiles +
   solution_passes_tests + q_len + is_nondeterministic + nondeterminism_score`. The gap is a
   feature-list difference; the original list is not recorded. **Pin the exact feature set and
   restate the number before it goes in a paper.**
2. **Monitor-vs-floor is not a matched comparison.** The 24 monitor AUROCs are computed on all
   1,375 items; my 0.7163 is on a 413-item held-out slice of the same items (the CV number,
   0.7715 ± 0.039, is the fairer one). No metadata model can be fit on Koran's train/val split,
   because that split is *paired* by problem and metadata is balanced there by construction.
   The right framing is: "a floor fitted and evaluated within the test split", and it must be
   stated that way.
3. **Whether the honest APPS solutions are unmodified human code.** Verified at source level
   (`codeparrot/apps` `solutions` field + a mechanical `fix_solution`); I did **not** download
   `codeparrot/apps` and diff strings, and `fix_solution` does rewrite top-level `return` →
   `exit()`, which is itself a systematic textual edit applied to honest code and *not* to
   backdoor code — a possible contributor to the 0.85 raw-code authorship AUROC that I have not
   isolated. (Actually `fix_solution` is applied to backdoor code too — `load_apps_backdoors`
   and `load_control_tax_backdoors` both call it — so this is likely a non-issue, but it is
   untested.)
4. **The Koran licence.** `eugenekoran/apps-control-arena-high-quality` declares **no licence**
   at all. It is a derivative of an MIT dataset, but nothing on the repo says so. If the paper
   redistributes or re-derives from it, this needs a sentence.
5. **`2607.06596` (Pinto)** — not opened here; that is K2's job. Note for K2: Jha's harness
   already ships two partial-input controls (`code_length_only_auroc` 0.4726,
   `hash_count_only_detector_auroc` 0.6957→0.4983). They are **code-side** partial-input
   baselines, both reported as *negative* results, and neither touches problem-side metadata.
   That is the closest prior art I encountered and the novelty sentence must distinguish it.
6. **Control Tax full text** — only the abstract page was fetched (HTTP 200); the JSON release
   was confirmed to exist (34.7 MB, HTTP 200) but not downloaded or parsed. How Control Tax
   chose *which* problems to attempt backdoors on — the true upstream origin of the selection —
   is therefore **unverified**, and it is the single most useful remaining check.
7. **`Multi-Signal-Control-SPAR/Multi-Signal-Monitoring`** — confirmed to exist (HTTP 200) but
   its contents were not read; Koran et al.'s own split-construction script was not inspected.
   Everything about their split here comes from their §4.1 prose plus Jha's reconstruction.
8. **`ideas/28`'s claim that a published monitor scores AUC 0.64 on this task** ("the DSPy/GEPA
   writeup") — not checked in this session.

---

## 7. URL log (every fetch this session)

| URL | HTTP |
|---|---|
| https://arxiv.org/abs/2608.16190 | 200 (43,381 B) |
| https://arxiv.org/html/2608.16190 | 200 (132,782 B) |
| https://arxiv.org/abs/2605.15377 | 200 (42,506 B) |
| https://arxiv.org/html/2605.15377v2 | 200 (334,191 B) |
| https://arxiv.org/abs/2506.05296 | 200 (41,767 B) |
| https://api.github.com/repos/anik-jha/challenger-panels | 200 |
| https://github.com/anik-jha/challenger-panels | 200 |
| https://api.github.com/repos/anik-jha/challenger-panels/git/trees/main?recursive=1 | 200 |
| https://api.github.com/repos/UKGovernmentBEIS/control-arena | 200 (positive control) |
| https://api.github.com/repos/UKGovernmentBEIS/control-arena/git/trees/main?recursive=1 | 200 |
| https://api.github.com/repos/TylordTheGreat/does-not-exist-abc | **404** (negative control) |
| https://api.github.com/repos/Multi-Signal-Control-SPAR/Multi-Signal-Monitoring | 200 |
| raw…/challenger-panels/main/README.md | 200 |
| raw…/challenger-panels/main/src/data.py | 200 |
| raw…/challenger-panels/main/runs/m1/dataset-manifest.json | 200 |
| raw…/challenger-panels/main/runs/m0/anchor-facts.json | 200 |
| raw…/challenger-panels/main/runs/x2/leakage-checks.json | 200 |
| raw…/challenger-panels/main/runs/x0/monitor-summary.json | 200 |
| raw…/challenger-panels/main/runs/scores/score-summary.json | 200 |
| raw…/control-arena/main/control_arena/settings/apps/task/dataset.py | 200 |
| raw…/control-arena/main/control_arena/settings/apps/apps_setting.py | 200 |
| raw…/control-arena/main/control_arena/settings/apps/apps_solution_policy.py | 200 |
| raw…/control-arena/main/control_arena/settings/apps/README.md | 200 |
| raw…/control-arena/main/control_arena/settings/apps/dataset/upload_dataset.py | 200 |
| raw…/control-arena/main/control_arena/settings/apps/dataset/validation.py | 200 |
| raw…/control-arena/main/control_arena/settings/apps/dataset/HF_README.template.md | 200 |
| raw…/control-arena/main/docs/settings/apps.qmd | 200 |
| https://huggingface.co/api/datasets/eugenekoran/apps-control-arena-high-quality | 200 |
| https://huggingface.co/api/datasets/RoganInglis/apps-control-arena | 200 |
| https://huggingface.co/api/datasets/eugenekoran/this-does-not-exist-xyz | **401** (negative control) |
| https://huggingface.co/datasets/eugenekoran/apps-control-arena-high-quality/raw/main/README.md | 200 |
| https://huggingface.co/datasets/RoganInglis/apps-control-arena/raw/main/README.md | 200 |
| https://huggingface.co/api/datasets/eugenekoran/apps-control-arena-high-quality/tree/main/data | 200 |
| https://huggingface.co/api/datasets/TylordTheGreat/apps-backdoors-04-02-25 | 200 |
| https://huggingface.co/api/datasets/TylordTheGreat/apps-backdoors-04-02-25/tree/main | 200 |
| https://huggingface.co/datasets/TylordTheGreat/apps-backdoors-04-02-25/raw/main/README.md | **404** "Entry not found" (no card exists; repo does) |
| https://mikhailterekhov.github.io/control-tax/ | 200 (533,434 B) |
| https://mikhailterekhov.github.io/control-tax/backdoor_code_paper.json | 200 (34,718,317 B) |
| HfFileSystem parquet reads: 3 files eugenekoran, 3 files RoganInglis | 200 |

`export.arxiv.org/api` was **not used**. Sleeps of ≥9 s were taken between all arxiv.org fetches.

## 8. Scripts written (all in this directory)

`fetch_cols.py` (metadata column projection), `fetch_code.py` (code column projection),
`colsize.py` (per-column parquet sizes), `analyse.py` (lineage + marginals), `analyse2.py`
(inert-backdoor counts + CV), `auroc.py` (held-out metadata AUROCs), `bow.py` (authorship /
leak checks), `data.py` (Jha's harness file, fetched verbatim and imported).
