# Release procedure — the split and the scripts, anonymised

Written 2026-09-11. Closes the open `LICENSE` item in `notes/05-permissibility.md` and makes
`main.tex:589` ("Ours accompany this paper") true rather than aspirational. The repo now carries
`LICENSE` (MIT, `Copyright (c) 2026 The authors of "What Survives the Filter?"`), which matches
both upstream artifacts this work builds on most — `RoganInglis/apps-control-arena` and
`anik-jha/challenger-panels`.

## 1. Build and check (on the machine with the run products)

```bash
cd experiments/apps
# headline build (proposed 2026-09-11; the coordinator sends the go with the final --keep):
# the outcome-blind `first` selection of the independent-arm retry pool, one draw per problem
python3 release_split.py --out release --keep first \
    --bd-independent bdind_sonnet5_first.jsonl --bdpass-independent bdindpass_sonnet5_first.jsonl \
    --card-out ../RELEASE-CARD.md
python3 release_split.py --check release         # run this from the directory holding train_*.parquet
```

`--keep` and the retry pool (`RESULTS.md` §7), checked in memory on 2026-09-11 without writing
anything: fed the full pool (`bdind_sonnet5_retry.jsonl` + `bdindpass_sonnet5_retry.jsonl`, 11,565
draws, aligned line for line), `--keep first` and `--keep best` select exactly the draws
`merge_draws.py select` wrote to `bdind_sonnet5_{first,best}.jsonl` (1,112 each; `first` gives 623
passing / 14 usable independent pairs, `best` 1,046 / 106, ten of the 106 being crash-on-trigger
survivors). Feeding the pre-selected `_first` files, as above, is the same build and skips the
dedupe warning. `--keep best` (or the `_best` files) is the strict-S build and must ship with the
selection-effect sentence; note that the 99-problem crash-excluded reading is **not** recoverable
from the released schema, which carries `backdoor_works` but no crash flag. The script cannot ship
the pool itself as it stands: it always reduces to one draw per problem, its file set is fixed, and
`--check` rejects unlisted files. Shipping the pool needs a small addition (a `--pool-independent`
pair of flags writing `attacks_independent_pool.jsonl` with `draw`/`source`/`round` and a crash
flag, an `--also-select best` writing `pairs_*_best.csv` keyed by `draw`, and the matching manifest
and `--check` entries); it is written up in the Worker G report and is not made until the go.

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

Fill the two counts from `MANIFEST.json`; if the macros are not wanted, write the numbers. If the
retry pool ships (§1), add after "pair lists": "together with every draw of the independent arm's
retry pool and the two selections made from it".

## 5. Still open, and not a blocker

`notes/05` records that GitHub still serves the purged `.pkl` blobs to anyone supplying the exact
object hash, and only GitHub Support can force the garbage collection. **That ticket is still
open.** It does not block this release: nothing in `release/` derives from that corpus, and the
bundle carries no upstream content at all. It does block the sentence "this repo is evidence that
we redistribute nothing" — until Support confirms, the paper's claim must stay the precise one:
*we redistribute one MIT-licensed file of 5,797 bytes (`monitor-summary.json`), with its notice.*
