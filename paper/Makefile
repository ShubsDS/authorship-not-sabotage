# Build the paper:  make            (needs a TeX distribution with pdflatex and bibtex)
# Rebuild figures:  make figures    (needs matplotlib; writes fig/ from experiments/apps/figures.py)

LATEX = pdflatex -interaction=nonstopmode -halt-on-error

main.pdf: main.tex refs.bib neurips_2026.sty $(wildcard fig/*)
	$(LATEX) main
	bibtex main
	$(LATEX) main
	$(LATEX) main

figures:
	cd ../experiments/apps && python figures.py

clean:
	rm -f main.aux main.bbl main.blg main.log main.out main.pdf missfont.log

.PHONY: figures clean
