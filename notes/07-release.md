# Release procedure — the split and the scripts, anonymised

Written 2026-09-11. Closes the open `LICENSE` item in `notes/05-permissibility.md` and makes
`main.tex:589` ("Ours accompany this paper") true rather than aspirational. The repo now carries
`LICENSE` (MIT, `Copyright (c) 2026 The authors of "What Survives the Filter?"`), which matches
both upstream artifacts this work builds on most — `RoganInglis/apps-control-arena` and
`anik-jha/challenger-panels`.

## 1. Build and check (on the machine with the run products)

```bash
cd experiments/apps
python release_split.py --out release            # add --keep best ONLY if the retry pool is in
python release_split.py --check release          # run this from the directory holding train_*.parquet
```

The build refuses to write on any anonymity hit (local path, username, `msgbatch_…`, `sk-ant-…`,
repo URL, dollar figure) and refuses to mix generators. `--check` re-verifies counts, SHA-256s,
the field allow-list, the pair CSVs against the jsonl, and that **no released code string is
byte-identical to any upstream solution or stored backdoor**. That last check is skipped with a
loud warning if the parquet shards are not present, so run `--check` where they are. Default
independent-arm verifier file is `bdindpass_sonnet5.jsonl` per `GATE-S-RUNBOOK.md`; override with
`--bdpass-independent` if the run followed `gen_backdoor_api.py`'s closing line instead.

## 2. Primary route — supplementary material with the submission

The workshop is 4 pages **plus unlimited supplementary**, so this needs no external account and no
anonymity gamble:

```bash
cd experiments/apps && zip -r ../../same-generator-apps-split.zip release ../../LICENSE
```

Attach the zip on OpenReview. It is self-contained: data, `MANIFEST.json`, dataset card, licence.
Do this first; it is the route that cannot fail.

## 3. Secondary route — an anonymised HuggingFace dataset

Use a throwaway account created for review (no real name, no linked email that identifies us), or
keep the repo private and hand reviewers a read token. Public-under-a-throwaway is simpler and is
what we should do.

```bash
hf auth login                                    # throwaway account token
hf repo create anon-filter-2026/same-generator-apps-split --type dataset
hf upload anon-filter-2026/same-generator-apps-split ./release . --type dataset \
    --commit-message "Initial release"
```

Equivalent Python (`huggingface_hub` 1.31):

```python
from huggingface_hub import HfApi
api = HfApi(token=TOKEN)
api.create_repo("anon-filter-2026/same-generator-apps-split", repo_type="dataset",
                private=False, exist_ok=True)
api.upload_folder(repo_id="anon-filter-2026/same-generator-apps-split", repo_type="dataset",
                  folder_path="experiments/apps/release", path_in_repo=".",
                  commit_message="Initial release")
```

`release/README.md` becomes the dataset card on upload. Re-run `--check` on the *uploaded* copy
before citing it. Do not add the HF link to the PDF unless the account is genuinely anonymous.

## 4. The sentence for `main.tex:589`

Replace "Ours accompany this paper." with:

> Ours accompany this paper as supplementary material: the same-generator split
> (\nSameGenHonest{} honest and \nSameGenAttack{} attack programs written by one model, with both
> eligibility rules shipped as separate pair lists), the generation, execution and verification
> scripts, and a manifest of row counts and checksums, released under the MIT licence.

Fill the two counts from `MANIFEST.json`; if the macros are not wanted, write the numbers.

## 5. Still open, and not a blocker

`notes/05` records that GitHub still serves the purged `.pkl` blobs to anyone supplying the exact
object hash, and only GitHub Support can force the garbage collection. **That ticket is still
open.** It does not block this release: nothing in `release/` derives from that corpus, and the
bundle carries no upstream content at all. It does block the sentence "this repo is evidence that
we redistribute nothing" — until Support confirms, the paper's claim must stay the precise one:
*we redistribute one 8 KB MIT-licensed file, with its notice.*
