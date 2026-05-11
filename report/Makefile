# =============================================================================
# Makefile - Rapport LaTeX Analyse Reseau WETH Polygon
# Usage: make          (genere figures + compile le rapport)
#        make figures   (genere les figures PNG uniquement)
#        make rapport   (compile le rapport LaTeX uniquement)
#        make clean     (supprime tous les artefacts generes)
# =============================================================================

.PHONY: all figures rapport clean clean-rapport

all: figures rapport

figures: $(wildcard src/*.py) polygon_weth_crash_2024-08-05.csv
	python run_all.py

rapport: rapport/main.pdf

rapport/main.pdf: $(wildcard rapport/sections/*.tex) $(wildcard rapport/annexes/*.tex) rapport/main.tex rapport/references.bib
	cd rapport && latexmk -pdf -interaction=nonstopmode main.tex

clean-rapport:
	cd rapport && latexmk -C

clean: clean-rapport
	rm -f figures/*.png
