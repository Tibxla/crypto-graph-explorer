# Rapport — Analyse du réseau WETH/Polygon (Lundi Noir, 5 août 2024)

Sous-projet contenant l'analyse Python complète et le rapport LaTeX universitaire (L3 MIAGE, Paris Nanterre) qui accompagne le prototype web `crypto-graph-explorer`.

## Contenu

```
report/
├── polygon_weth_crash_2024-08-05.csv   # 401 709 transactions WETH (71 Mo, commité)
├── src/                                # Code Python (6 RQ + 5 analyses extras)
├── figures/                            # 21 PNG générés
├── rapport/                            # Sources LaTeX + PDF compilé
│   ├── main.tex
│   ├── main.pdf
│   ├── references.bib
│   ├── sections/                       # Une section par RQ + analyses_complementaires
│   └── annexes/                        # cahier des charges, exécution, manuel
├── run_all.py                          # Orchestrateur Python
├── requirements.txt
├── Makefile
└── CLAUDE.md                           # Conventions du projet
```

Le CSV de 71 Mo est commité dans le repo pour permettre la reproduction sans dépendance BigQuery.

## Reproduction rapide

```bash
# Depuis report/
pip install -r requirements.txt
python run_all.py            # → 21 PNG dans figures/, ~5-10 min

cd rapport
latexmk -pdf main.tex        # → main.pdf
```

Ou via `make` depuis `report/` : `make all`.

## Les 6 questions de recherche + 5 extras

| ID | Fichier | Fonction |
|----|---------|----------|
| RQ1 — Topologie | `src/rq1_topologie.py` | Distribution des degrés, composantes, densité |
| RQ2 — Centralité | `src/rq2_centralite.py` | Degree, betweenness, closeness, PageRank |
| RQ3 — Communautés | `src/rq3_communautes.py` | Louvain, modularité Q |
| RQ4 — Temporel | `src/rq4_temporel.py` | Fenêtres horaires UTC |
| RQ5 — Petit-monde | `src/rq5_petitmonde.py` | Clustering vs Erdős-Rényi, σ |
| RQ6 — Flux pondérés | `src/rq6_flux_ponderes.py` | Gini, Lorenz, whales |
| Extras | `src/extras_analyses.py` | Ponts, k-cœurs, Jaccard, SI, robustesse |

## Lien avec le prototype web

Les analyses Python produisent les résultats numériques rigoureux qui figurent dans le rapport (Gini = 0,978, σ = 115,90, Q = 0,6445). Le prototype web `crypto-graph-explorer` (dossier parent) en propose une version interactive simplifiée, sur un CSV pré-calculé (`public/data/nodes_metrics.csv`).
