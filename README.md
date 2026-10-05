# A Same-Generator Corpus and Classifier Floors for AI-Control Monitor Evaluation

Code and paper source for the EvoRobust @ NeurIPS 2026 workshop paper.

## What the paper shows

AI-control monitors are models that read code and flag backdoors (hidden sabotage). They are
trained and ranked on stored pairs of programs. For each programming problem there is an honest
solution and a solution with a backdoor. In the corpora in use, **the honest solution was written
by a human and the backdoor by a language model.** A monitor can therefore tell the two apart by
recognising who wrote the code, without finding any backdoor.

1. **Simple classifiers that cannot see backdoors beat most monitors.** On the standard filtered,
   comment-stripped split, a bag-of-words classifier reaches AUROC 0.806. That is above 20 of the
   24 monitors ranked on the same split. A classifier that reads no code at all, only problem
   metadata, reaches 0.772. The signal is almost as strong on backdoors that never work, so it
   does not come from the sabotage.
2. **Holding the author constant removes most of the signal.** We rebuild the corpus so that one
   model (Claude Sonnet 5, and separately Claude Haiku 4.5) writes both the honest and the
   backdoored solution to each problem. This removes between a third and nine-tenths of the
   classifier's separability. Using the same prompt for both classes removes most of the rest. An
   LLM monitor drops the same way: from 0.958 on stored pairs to 0.566 on same-generator pairs.
3. **The label adds a second artifact.** When a problem's backdoor fails, its human solution is
   kept as a negative. So the negative class partly records which attacks failed.

We release the same-generator corpus. We recommend that stored-pair evaluations report a no-code
floor and a bag-of-words floor, generate both classes with one model and one prompt, and define
the negative class by honesty rather than by attack failure.

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
