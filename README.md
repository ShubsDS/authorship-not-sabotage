# A Same-Generator Corpus and Classifier Floors for AI-Control Monitor Evaluation

Code and paper source for the EvoRobust @ NeurIPS 2026 workshop paper.

## What the paper shows

AI-control monitors are models that read code and flag backdoors (hidden sabotage). They are
trained and ranked on stored pairs of programs. For each programming problem there is an honest
solution and a solution with a backdoor. In the corpora in use, **the honest solution was written
by a human and the backdoor by a language model.** A monitor can therefore tell the two apart by
recognising who wrote the code, without finding any backdoor.

1. **A bag-of-words classifier scores above most monitors without reading a backdoor.** On the
   standard filtered, comment-stripped split it reaches AUROC 0.806, above 20 of the 24 monitors
   ranked on the same split. It transfers across attacking models and is almost as strong on
   backdoors that never work, so it does not read the sabotage. The classifier is trained and the
   monitors are zero-shot, so this says what the corpus makes recoverable, not which is the
   better monitor.
2. **A classifier that reads no code reads how the label was selected.** It sees only problem
   metadata: difficulty, test count and question length. Cross-validated within the test split it
   reaches 0.766 (pooled out-of-fold), above 20 of the 24 monitors. Trained on problems outside
   the test split and scored once, it reaches 0.298, below chance (0.629 on problems with at
   least four tests). The split's filter, not the code, ties the metadata to the label. This is
   not an authorship difference.
3. **Holding the author constant.** We rebuild the corpus so that one model (Claude Sonnet 5,
   and separately Claude Haiku 4.5) writes both the honest and the backdoored solution to each
   problem. ρ is the share of the classifier's above-chance AUROC on the stored pairs that
   survives on these pairs. The headline rows are attempts: ρ is 0.687 for Sonnet 5 and 0.097
   for Haiku 4.5, but only 14 of 623 and 2 of 611 of their attacks fire, while every stored
   attack on the same problems fires. On working sabotage (99 strict pairs, every attack fires),
   ρ is 0.861 (95% CI 0.662-1.089). Using the same prompt for both classes takes Sonnet 5's ρ to
   0.390 and leaves Haiku 4.5's unchanged (0.110). ρ is not the backdoor's share: rebuilding with
   one model changes the attacks as well as the author.
4. **Swapping one class at a time separates the two detectors.** The bag-of-words classifier
   stays high whenever the two classes have different writers: human honest code against our
   attacks scores 0.981, and our honest code against stored attacks 0.956. It falls, to 0.750,
   only when one model wrote both, so its drop is authorship. The LLM monitor's drop is in the
   attacks instead. A Sonnet 5 monitor scores 0.958 on stored pairs and 0.566 on same-generator
   pairs; human honest code against our attacks scores 0.446, and our honest code against stored
   attacks 0.974. At a 2% false-positive rate it catches 77% of stored and 48% of same-generator
   working attacks (strict pairs), and 85% against 6% on the headline pairs.
5. **The label adds a second artifact.** When a problem's backdoor fails, its human solution is
   kept as a negative. So the negative class partly records which attacks failed.

We release the same-generator corpus. We recommend that stored-pair evaluations report a no-code
floor and a bag-of-words floor, each against a permutation null; generate both classes with one
model and one prompt; define the negative class by honesty rather than by attack failure; and
report detection at a fixed audit budget together with the share of attacks that fire.

## Repository layout

```
experiments/
  apps/      APPS backdoor corpora: the stored-pair floors, the same-generator corpus
             (generation, test harness, backdoor verification) and every measurement on it
  agentic/   five same-generator agentic settings (appendix)
  README.md  how to reproduce each result, with commands
paper/       LaTeX source, bibliography and figures
```

## Reproducing

See [`experiments/README.md`](experiments/README.md). The stored-pair results run on a laptop
CPU in minutes. Building the same-generator corpus needs an Anthropic API key, and its open-weight
arm needs a GPU.

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

## Data and licence

The code and our generated data are MIT-licensed ([`LICENSE`](LICENSE)). Upstream corpora are
fetched at run time and not redistributed. Their licences are listed in
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
