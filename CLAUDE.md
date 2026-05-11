# Crypto Graph Explorer — projet L3 MIAGE

## Vue d'ensemble

Devoir universitaire en deux livrables couplés sur l'analyse du réseau WETH/Polygon pendant le crash du 5 août 2024 ("Lundi Noir") :

1. **Prototype web interactif** (racine du repo) — visualisation D3.js des 12 880 nœuds, panneau d'analyse avec 6 RQ + 8 analyses avancées.
2. **Sous-projet `report/`** — analyse Python rigoureuse sur 401 709 transactions + rapport LaTeX universitaire (59 pages, Paris Nanterre).

Les deux artefacts couvrent les mêmes 6 questions de recherche (RQ1-RQ6) sous deux angles : le web pour l'exploration interactive, le rapport pour la rigueur scientifique et les chiffres exacts.

## Commandes principales

### Prototype web (racine)
```bash
npm install
npm run dev          # http://localhost:8080
npm run build        # → dist/
npm test             # Vitest
```

### Sous-projet rapport (`report/`)
```bash
cd report
pip install -r requirements.txt
python run_all.py                       # ~11 min, génère 21 PNG dans figures/
cd rapport && latexmk -pdf main.tex     # → main.pdf (59 pages)

# Ou via make depuis report/
make            # figures + rapport
make figures    # PNG uniquement
make rapport    # PDF uniquement
make clean      # supprime artefacts
```

## Structure

```
crypto-graph-explorer/
├── src/                # Frontend React/TS
│   ├── components/     # GraphCanvas, AnalysisPanel, etc.
│   │   └── ui/         # shadcn (12 composants utilisés sur 48)
│   ├── lib/            # graphUtils.ts, graphTypes.ts
│   ├── pages/          # Index, NotFound
│   └── hooks/
├── public/data/        # nodes_metrics.csv (12 880 nœuds pré-calculés)
├── report/             # Sous-projet rapport
│   ├── polygon_weth_crash_2024-08-05.csv   # 71 Mo, commité
│   ├── src/            # 7 modules Python (rq1-rq6 + extras)
│   ├── figures/        # 21 PNG (16 RQ + 5 extras)
│   ├── rapport/        # LaTeX (sections/, annexes/, main.tex, main.pdf)
│   ├── run_all.py
│   ├── requirements.txt
│   └── Makefile
└── README.md           # Doc utilisateur du prototype web
```

## Stack technique

### Frontend
- **Vite 5.4** + **React 18** + **TypeScript 5.8**
- **D3.js 7.9** pour la visualisation force-directed
- **shadcn/ui** + **TailwindCSS 3.4** (composants Radix)
- **Vitest** pour les tests (`src/test/`)
- Port dev : **8080**

### Analyse Python (report/)
- **Python ≥ 3.10** (sur 3.14 chez l'utilisateur, certains pins matplotlib échouent mais l'install fonctionne)
- **NetworkX 3.4.2**, **Pandas 2.2.3**, **NumPy 2.1**, **Matplotlib 3.9.4**, **SciPy 1.14**, **powerlaw 2.0.0**
- Algorithmes : Louvain natif NetworkX (RQ3), Watts-Strogatz σ (RQ5), Gini (RQ6), Tarjan bridges + Seidman k-core + SI + cascade (extras)

### Rapport LaTeX (report/rapport/)
- **pdfLaTeX** + **biber** (template Paris Nanterre)
- Packages clés : `biblatex`, `babel[french]`, `booktabs`, `hyperref`, `cleveref`, `listings`
- 14 sections + 3 annexes, 21 figures intégrées, 59 pages

## Conventions

### Frontend
- Composants en `PascalCase.tsx` pour le métier, `kebab-case.tsx` pour shadcn
- Tests Vitest dans `src/test/` (setup central) ou co-localisés
- Pas d'emojis dans le code UI ni dans le README
- Aucune trace de Lovable (le projet a été initialisé via Lovable puis nettoyé)

### Python
- Snake_case pour fonctions/variables, UPPERCASE pour constantes
- Style fonctionnel pur, pas d'OOP
- Commentaires et docstrings en français
- Seed fixée à **42** partout pour reproductibilité
- Sampling explicite pour les algos `O(n³)` (betweenness, closeness)

### LaTeX
- Sources `.tex` en UTF-8 avec escape sequences (`\'e`, `\`a`, `\oe{}`)
- Une section LaTeX par RQ (`sections/rqN.tex`), annexes séparées
- Figures référencées par `\ref{fig:rqN_xxx}`, tables par `\ref{tab:xxx}`

## Résultats numériques de référence (depuis report/)

| RQ | Métrique clé | Valeur |
|---|---|---|
| RQ1 | Densité, WCC géante, diamètre | 2,41×10⁻⁴, 97,3 %, 15 |
| RQ2 | Spearman degré/PageRank | 0,6061 |
| RQ3 | Modularité Louvain Q | **0,6445** (174 communautés) |
| RQ4 | Pic transactions / pic volume | 13h / 01h UTC |
| RQ5 | σ small-world | **115,90** |
| RQ6 | Coefficient de Gini | **0,9780** |
| Extras | Ponts, k_max, cascade top-degré | 5 890 (17,5 %), 37, -56,7 % |

Le prototype web reproduit ces analyses de façon approximative (sampling réduit, CSV pré-calculé sans timestamps ni poids WETH). Pour les chiffres exacts du rapport, c'est `report/` qui fait foi.

## Fichiers sensibles

Le projet d'origine utilisait `google_key.json` (compte de service GCP pour BigQuery). Ce fichier **n'est pas dans le repo** et ne doit jamais y être commité. Le CSV pré-extrait suffit à reproduire toutes les analyses, BigQuery n'est plus nécessaire.

## Pièges connus

- **Python 3.13+** : `matplotlib~=3.9.4` peut échouer à builder. Sur 3.14, installer `scipy` et `powerlaw` séparément après pip install, matplotlib étant déjà disponible via une version plus récente.
- **Self-loops dans le graphe non orienté** : `nx.core_number()` refuse les self-loops. Les retirer avec `G.remove_edges_from(nx.selfloop_edges(G))` avant la décomposition k-core (déjà fait dans `extras_analyses.py`).
- **`run_all.py` ~11 min** : la moitié du temps part dans la détection des ponts et la simulation de robustesse. Pour itérer rapidement sur un seul module, lancer `python -m src.rqN_xxx`.
- **Vite port 8080** : fixé dans `vite.config.ts` (pas le 5173 par défaut).
