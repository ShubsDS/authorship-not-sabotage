# Who Wrote the Backdoor? Authorship Confounds in AI-Control Monitor Benchmarks

Code and paper source for the EvoRobust @ NeurIPS 2026 workshop paper.

## What the paper shows

AI-control monitors are models that read code and flag backdoors (hidden sabotage). They are
developed and ranked on fixed datasets in which each programming problem has an honest solution and
a backdoored one. A monitor should score well on such a dataset only by finding the backdoor. We
study the public APPS backdoor dataset (RoganInglis/apps-control-arena), whose honest solutions
were written by people and whose backdoors were written by **older models** (Claude 3.7 Sonnet,
o3-mini, o1-mini, GPT-4o and four smaller models, all released by early 2025, plus an unattributed
source). We call its pairs the original pairs. Figure 1 of the paper summarises the results.

1. **A classifier that never runs the code beats most monitors.** On the standard test split
   (1,375 problems, one program each, comments removed) a bag-of-words classifier trained on the
   split's training problems reaches AUROC 0.806, above 20 of 24 open-weight models (0.4B-35B)
   prompted as monitors in prior work. What it reads is shared across attacking models and present
   whether or not a backdoor works; its strongest backdoor-side tokens (`and`, `==`, `if`) are a
   shallow trace of any added special case. The classifier is trained and the monitors are not, so
   this measures what the dataset gives away, not which detector is better.
2. **The labels leak.** The test split keeps a problem's backdoored program only if the backdoor
   works; 720 of the 892 problems with a backdoor fail and contribute their honest solution
   instead. Backdoor-class problems therefore have about half as many tests, and a classifier that
   reads only problem metadata (difficulty, test count, statement length) reaches 0.766
   cross-validated within the split, above 20 monitors. Fitted outside the split it scores 0.298,
   the same relation reversed, because there the honest items come from problems the split
   excluded. The leak comes from how labels were chosen, not from the code.
3. **The classifier reads the author.** We rebuild the pairs with one model, Claude Sonnet 5 (and
   separately Claude Haiku 4.5), writing both solutions, and pair each class with the other
   author's. Naming each kind of pair by who wrote its honest and its backdoored side, on the 99
   problems where every backdoor works bag-of-words scores 0.789 on person / older models and
   0.749 on Sonnet 5 / Sonnet 5, but 0.953 on person / Sonnet 5 and 0.905 on Sonnet 5 / older
   models. If Sonnet 5's backdoors were harder to spot, pairing them with human code would lower the
   score; it raises it. The same holds over all attempts (0.981 against 0.865). With one author the
   classifier keeps rho = 0.687 of its advantage over chance on Sonnet 5's single attempts and
   0.097 on Haiku 4.5's; part of what Sonnet 5 keeps is a layout our attack prompt induces
   (`def main`), and requesting the honest solution with that prompt lowers rho to 0.390.
4. **Which backdoors work.** A Sonnet 5 monitor is not fooled by authorship (0.944 on the original
   pairs, 0.966 when Sonnet 5 wrote the honest side). It seems to fall on person / Sonnet 5
   (0.755), but 41 of the 99 Sonnet 5 backdoors it scored are wrong only on inputs the problem
   forbids (35) or only on stray whitespace (6), and it scores them low. We check every trigger in
   both classes against an input validator written from the statement, and require the backdoor's
   output there to differ from the human solutions' majority answer. Of the older models' 99
   backdoors on the same problems, 15 also fire only on forbidden inputs, as do 20 of the 172 in the
   standard test split (bag-of-words still scores 0.810 without them). Both backdoors pass on
   52 problems. On these the monitor's AUROC falls only from 0.955 to 0.900, and flagging 2% of the
   human solutions it catches 77% of the older models' backdoors and 61% of Sonnet 5's (difference
   0.15, 95% CI -0.01 to 0.31). On real backdoors the catch rate does not clearly depend on who
   wrote them.

So a score on a dataset built this way does not show that a monitor finds sabotage, and a catch
rate means little until every trigger is checked. We release the rebuilt pairs, the input
validators and the checks, and recommend running them on other monitor benchmarks: report
baselines that never run the code (bag-of-words, problem metadata, length) with their
shuffled-label scores; pair each class with another author's code; check that every trigger is a
legal input on which the backdoor's answer is wrong; report catch rates at a fixed audit budget on
the backdoors that pass, from several generators including current models; and where the checks
find shortcuts, have one model write both classes from the same prompt and choose honest examples
independently of whether an attack succeeded.

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
