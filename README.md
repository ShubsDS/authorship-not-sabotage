# Who Wrote the Backdoor? Authorship Confounds in AI-Control Monitor Benchmarks

Code, data pointers and paper source for the EvoRobust @ NeurIPS 2026 workshop paper.

## What the paper shows

AI-control monitors are models that read code and flag backdoors (hidden sabotage). They are
trained and ranked on stored pairs of programs: for each programming problem, an honest solution
and a solution with a backdoor. In the public corpora, **a human wrote every honest solution and a
language model wrote every backdoor**, so a monitor can score well by recognising the author.

1. **Classifiers that cannot see a backdoor beat most monitors.** On the standard filtered,
   comment-stripped split, a bag-of-words classifier reaches AUROC 0.806 and a classifier that
   reads only problem metadata reaches 0.772, both above 20 of the 24 monitors ranked on that
   split. The bag-of-words signal is almost as strong on backdoors that never work.
2. **Holding the author fixed removes much of the signal on attack attempts.** When one model
   (Claude Sonnet 5, and separately Claude Haiku 4.5) writes both classes, the classifier keeps
   69% and 10% of its above-chance separability, and most of the rest goes when both classes also
   share a prompt.
3. **On verified attacks the picture is weaker.** Most generated attacks never fire. On the 99
   that do, the classifier keeps 86% of its separability, and a Sonnet 5 monitor auditing 5% of
   honest programs catches 55% of them against 81% of the stored backdoors on the same problems.
4. **The label records attack failure.** A problem whose backdoor fails contributes its human
   solution as a negative, so the negative class partly encodes which problems were hard to
   attack.

We release the same-generator corpus and recommend that stored-pair evaluations report a no-code
and a bag-of-words floor, generate both classes with one model and one prompt, define the
negative class by honesty, and report verified attacks and a catch rate at a fixed audit budget.

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
