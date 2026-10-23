# Who Wrote the Backdoor? Authorship Confounds in AI-Control Monitor Benchmarks

Code and paper source for the EvoRobust @ NeurIPS 2026 workshop paper.

## What the paper shows

AI-control monitors are models that read code and flag backdoors (hidden sabotage). They are
developed and ranked on fixed datasets of program pairs. For each programming problem there is an
honest solution and a solution with a backdoor. In the datasets in use, **the honest solution was
written by a human and the backdoor by a language model.** A monitor can therefore tell the two
apart by recognising who wrote the code, without finding any backdoor. We study the public
APPS-backdoor dataset (RoganInglis/apps-control-arena) and call its pairs the original pairs.

1. **A bag-of-words classifier scores above most monitors without reading a backdoor.** On the
   filtered test split (comment-stripped, 1,375 items) it reaches AUROC 0.806, above 20 of the 24
   monitors ranked on the same split. It transfers across attacking models and is almost as strong
   on non-working backdoors, so it does not read the sabotage. The classifier is trained and the
   monitors are zero-shot, so this says what the dataset makes recoverable, not which is the
   better monitor.
2. **A classifier that reads no code reads how the label was selected.** It sees only problem
   metadata: difficulty, test count and question length. Cross-validated within the test split it
   reaches 0.766 (pooled out-of-fold), above 20 of the 24 monitors. Trained on problems outside
   the test split and scored once, it reaches 0.298, below chance (0.629 on problems with at
   least four tests). The split's filter, not the code, ties the metadata to the label. This is
   not an authorship difference.
3. **Holding the author constant.** We rebuild the pairs so that one model (Claude Sonnet 5,
   and separately Claude Haiku 4.5) writes both the honest and the backdoored solution to each
   problem; these are the rebuilt pairs. ρ = (rebuilt − 0.5) / (original − 0.5) is the share of
   the classifier's above-chance AUROC on the original pairs that remains on the rebuilt pairs of
   the same problems. Over all attempts (one attack per problem, chosen before its outcome is
   known and kept if it passes the public tests), ρ is 0.687 for Sonnet 5 and 0.097 for Haiku
   4.5, but only 14 of 623 and 2 of 611 of their backdoors work, while every original backdoor on
   the same problems works. On working backdoors only (99 pairs, drawn from a pool of retries),
   ρ is 0.861 (95% CI 0.662-1.089). Using the same prompt for both classes takes Sonnet 5's ρ to
   0.390 and leaves Haiku 4.5's unchanged (0.110). ρ is not the backdoor's share: rebuilding with
   one model changes the attacks as well as the author.
4. **Swapping one class at a time separates the two detectors.** We name each kind of pair by
   who wrote its honest and its backdoored side. The original pairs are person / weaker models,
   where the weaker models are the nine models, all released by early 2025, that wrote the
   dataset's backdoors. Bag-of-words stays high whenever the two sides have different writers
   (person / Sonnet 5 0.981, Sonnet 5 / weaker models 0.956, original pairs 0.865) and falls, to
   0.750, only for Sonnet 5 / Sonnet 5, so its drop is authorship. The Sonnet 5 monitor's drop is
   in the attacks instead: 0.958 on the original pairs and 0.974 on Sonnet 5 / weaker models, but
   0.446 on person / Sonnet 5 and 0.564 on Sonnet 5 / Sonnet 5. At a 2% false-positive rate it
   catches 77% of the weaker models' working backdoors and 48% of Sonnet 5's, and 85% against 6%
   over all attempts. Figure 1 of the paper shows the floors, the swap and this catch rate.
5. **The label adds a second confound.** When a problem's backdoor fails, its human solution is
   kept as a negative. So the negative class partly records which attacks failed.

We release our corpus of rebuilt pairs. We recommend that evaluations on original pairs report a
no-code floor and a bag-of-words floor, each against a permutation null; generate both classes
with one model and one prompt; define the negative class by honesty rather than by attack failure;
and report detection at a fixed audit budget together with the share of backdoors that work.

## Repository layout

```
experiments/
  apps/      APPS backdoor dataset: the floors on the original pairs, the rebuilt pairs
             (generation, test harness, backdoor verification) and every measurement on them
  agentic/   five agentic settings in which one model wrote both classes (appendix)
  README.md  how to reproduce each result, with commands
paper/       LaTeX source, bibliography and figures
```

## Reproducing

See [`experiments/README.md`](experiments/README.md). The results on the original pairs run on a
laptop CPU in minutes. Building the rebuilt pairs needs an Anthropic API key, and the open-weight
variant (which regenerates only the honest class) needs a GPU.

```bash
pip install -r requirements.txt
cd experiments/apps
python fetch.py && python fetch_inputs.py && python bow.py
python koran_split_eval.py      # the bag-of-words floor: AUROC 0.806, above 20 of 24 monitors
```

## Building the paper

```bash
cd paper
make             # main.pdf (pdflatex + bibtex)
make figures     # regenerate fig/ from experiments/apps/figures.py
```

A full TeX Live has everything. A basic install (BasicTeX, TeX Live `scheme-basic`) also needs
`siunitx`, `tcolorbox` (with `tikzfill`, `pdfcol` and `listingsutf8`) and `inconsolata` for the
paper, and `cm-super` for `make figures`, which typesets the plots' text with LaTeX. Without
admin rights they install into your user tree:

```bash
tlmgr init-usertree
tlmgr --usermode install siunitx tcolorbox tikzfill pdfcol listings listingsutf8 inconsolata cm-super
updmap-user --enable Map=zi4.map
```

## Data and licence

Our corpus of rebuilt pairs is `same-generator-apps-split.zip`, attached to the
[v1.0 release](https://github.com/ShubsDS/authorship-not-sabotage/releases/tag/v1.0): the honest
and attack programs, the independent variant's full retry pool, the pair lists for all attempts
and for working backdoors under both draw selections (first draw, best draw), the scripts behind
the paper's numbers, a dataset card and a manifest of row counts and checksums.
`experiments/apps/release_split.py` builds it and `--check` validates it
(`experiments/README.md`, stage 7).

The code and our generated data are MIT-licensed ([`LICENSE`](LICENSE)). Upstream datasets are
fetched at run time and not redistributed. Their licences are listed in
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
