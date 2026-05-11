# Analyse Polygon WETH Crash Network

## Overview
Python network analysis of WETH transfers on Polygon during the Aug 5, 2024 crash.
6 research questions (RQ1-RQ6) analyzing topology, centrality, communities, temporal dynamics, small-world properties, and weighted flows.

## Commands
- `python main.py` - Fetch data from BigQuery (requires google_key.json)
- `python run_all.py` - Run all 6 analyses, generates 12 PNGs in figures/

## Project Structure
- `src/rq{1-6}_*.py` - One module per research question, each independent
- `src/graph_builder.py` - Shared CSV loading and NetworkX graph construction
- `src/style.py` - Global matplotlib styling, color palettes, helper functions
- `figures/` - Generated PNG visualizations (200 DPI)
- `rapport/` - LaTeX report (empty, intended for future)
- `polygon_weth_crash_2024-08-05.csv` - 401k transactions dataset (74MB)

## Code Conventions
- French comments and docstrings, English module-level docs
- snake_case functions/variables, UPPERCASE constants, no type hints
- No OOP - purely functional style with module-level functions
- Matplotlib: dark backgrounds (#0F172A) for network graphs, light for analytical charts
- Colors defined in src/style.py (primary=#2563EB, secondary=#7C3AED, accent=#F59E0B)
- Random seeds fixed to 42 for reproducibility
- Large networks use sampling optimizations (betweenness, path length >5000 nodes)

## Data
- CSV columns: transaction_hash, chrono (unix timestamp), source, target, weight (WETH)
- Graph: directed weighted DiGraph (default), undirected for RQ3/RQ5
- Multiple edges between same nodes aggregated by summing weights

## Sensitive Files
- `google_key.json` - GCP service account credentials, NEVER commit or share

<!-- GSD:project-start source:PROJECT.md -->
## Project

**Rapport LaTeX — Analyse du Reseau WETH Polygon (Lundi Noir)**

Rapport universitaire complet en LaTeX analysant le reseau de transferts WETH sur la blockchain Polygon pendant le crash du 5 aout 2024 ("Lundi Noir"). Le rapport repond a 6 questions de recherche (RQ1-RQ6) couvrant topologie, centralite, communautes, dynamique temporelle, proprietes petit-monde et flux ponderes. Le livrable est un PDF academique avec figures integrees, suivant le template de l'Universite Paris Nanterre (Licence MIAGE).

**Core Value:** Produire un rapport LaTeX professionnel et complet, sans limite de pages, avec des visualisations coherentes et esthetiques qui repondent rigoureusement aux 6 questions de recherche sur le reseau WETH Polygon.

### Constraints

- **Template**: Doit suivre exactement le template LaTeX Paris Nanterre (taille, police, interlignes, marges fixes)
- **Donnees**: CSV existant uniquement (pas de re-fetching BigQuery)
- **Langue**: Rapport en francais, code Python avec commentaires francais
- **Reproductibilite**: Seeds fixes a 42, resultats deterministes
- **Qualite visuelle**: Toutes les figures doivent suivre la meme trame graphique coherente
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Python Runtime
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | >=3.10, <3.13 | Runtime | 3.10+ required for NetworkX 3.4 compatibility. Cap at 3.12 for maximum library compatibility across the scientific stack. Python 3.13 works but some C-extension packages (powerlaw, older scipy) may lack prebuilt wheels. |
### Core Analysis Libraries
| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| NetworkX | ~=3.4.2 | Graph construction, algorithms, centrality, community detection | De facto standard for Python graph analysis. Pure Python = trivial install on Windows. 3.4.2 (Oct 2024) is the latest stable patch in the 3.4 line, supports Python 3.10-3.13. Includes built-in Louvain, PageRank, betweenness, closeness, clustering, connected components, shortest paths -- covers every RQ. Prefer 3.4.x over 3.6.x because 3.6 drops Python 3.10 support (requires >=3.11). | HIGH |
| NumPy | ~=2.1 | Numerical operations, array manipulation | Foundation for all scientific computing. 2.1.x is stable (mid-2024 line) with broad ecosystem compatibility. Avoid 2.4 which is too recent for some dependencies. | HIGH |
| Pandas | ~=2.2.3 | CSV loading, data manipulation, time-windowing (RQ4) | Mature, stable. 2.2.3 is the final 2.2 patch, works with both NumPy 1.x and 2.x. Avoid Pandas 3.0 (Jan 2026) which enforces Copy-on-Write by default and removes deprecated APIs -- migration risk for no benefit here. | HIGH |
| SciPy | ~=1.14 | Statistical tests, sparse matrices, curve fitting | Needed for Kolmogorov-Smirnov tests in distribution analysis, sparse graph representations, and as a dependency for powerlaw. 1.14 is the stable 2024 line. | HIGH |
### Community Detection
| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| NetworkX built-in `louvain_communities` | (included in NetworkX >=3.2) | Louvain community detection for RQ3 | **Use this instead of python-louvain.** The external `python-louvain` package (pip: `python-louvain`, import: `community`) has not been updated since January 2022 (v0.16). NetworkX 3.x includes a native `networkx.algorithms.community.louvain.louvain_communities()` with identical algorithm plus `resolution` and `seed` parameters for reproducibility. Zero additional dependency. Modularity computed via `networkx.algorithms.community.quality.modularity()`. | HIGH |
- `python-louvain` (v0.16) -- abandoned since January 2022, confusing naming (pip name != import name), unnecessary given NetworkX built-in
- `cdlib` -- library of 39 community detection algorithms. Massive overkill for a project that needs exactly Louvain. Pulls in igraph, leidenalg, and dozens of transitive dependencies
- `louvain` (louvain-igraph) -- igraph-based, adds C compilation dependency for no benefit
### Visualization
| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Matplotlib | ~=3.9.4 | All figure generation (network graphs + analytical charts) | Core visualization engine. 3.9.4 (Dec 2024) is the final 3.9 patch, well-tested. Supports PGF backend for LaTeX integration if ever needed. 3.9.x preferred over 3.10.x: 3.10 is newer (Dec 2024 initial) but 3.9 is battle-tested with no known Windows regressions. | HIGH |
| Technology | Version | Purpose | When | Confidence |
|------------|---------|---------|------|------------|
| Seaborn | ~=0.13.2 | Statistical distribution plots | Only if matplotlib's `hist()` + custom styling proves insufficient for RQ1/RQ6 distributions. Currently not needed -- the project's custom `src/style.py` handles all aesthetics. | MEDIUM |
- `SciencePlots` -- requires a working LaTeX installation just for matplotlib styles. Adds unnecessary build complexity. The project already has a comprehensive custom style module (`src/style.py`).
- `Plotly` / `Bokeh` -- interactive, web-based. Not suitable for static PNG figures destined for LaTeX inclusion.
- `matplot2tikz` (successor to deprecated `tikzplotlib`) -- converts matplotlib to TikZ code. Breaks on complex plots (network layouts with thousands of nodes, custom colormaps, dark backgrounds). `tikzplotlib` itself is abandoned; `matplot2tikz` (Nov 2025 fork) is still fragile for non-standard visualizations.
### Distribution Analysis
| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| powerlaw | ~=2.0.0 | Power-law distribution fitting for RQ1 (degree distribution) and RQ6 (weight distribution) | Purpose-built for heavy-tailed distribution analysis. Provides `Fit` objects with alpha exponent, xmin estimation, and comparison tests (power-law vs lognormal vs exponential). Peer-reviewed (Alstott et al., PLOS ONE 2014). v2.0.0 is the latest on PyPI. Dependencies: numpy, scipy, matplotlib, mpmath. | MEDIUM |
## LaTeX Toolchain
### Compiler and Build
| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| TeX Live | 2024 or 2025 (full) | Complete LaTeX distribution | Standard distribution for academic LaTeX. Full install includes all packages below. On Windows, MiKTeX with auto-install is also viable if disk space is a concern. | HIGH |
| pdfLaTeX | (included in TeX Live) | PDF compilation engine | Simpler and faster than LuaLaTeX/XeLaTeX. Sufficient for French documents with T1 encoding. No exotic font requirements in this project. | HIGH |
| Biber | (included in TeX Live) | Bibliography backend | Required for biblatex. Handles Unicode (French accents in author names), flexible sorting, modern features. Superior to BibTeX for French academic documents. | HIGH |
| latexmk | (included in TeX Live) | Build automation | Automatically runs pdflatex + biber as many times as needed to resolve cross-references. Single command: `latexmk -pdf rapport.tex`. | HIGH |
### Document Class and Core Packages
| Package | Purpose | Why This One | Confidence |
|---------|---------|-------------|------------|
| `report` class (or `article` per template) | Base document class | `report` provides `\chapter` which is natural for 6 RQ sections. However, if the Paris Nanterre template specifies `article`, use `article` with `\section` as top-level. Check the provided template PDF. | HIGH |
| `babel` with `[french]` | French typographic conventions | Handles non-breaking spaces before `:`, `;`, `!`, `?`. Translates "Chapter" -> "Chapitre", "Table of Contents" -> "Table des matieres". babel-french v4.0e (Aug 2025) is current. | HIGH |
| `fontenc` with `[T1]` | Font encoding | Required for correct rendering of French accented characters with pdfLaTeX. Without T1, accented characters break hyphenation. | HIGH |
| `inputenc` with `[utf8]` | Input encoding | Allows UTF-8 in .tex source files. Default in modern LaTeX but explicit declaration is safer and portable. | HIGH |
| `geometry` | Page margins | Precise margin control to match Paris Nanterre template. Example: `\usepackage[a4paper, margin=2.5cm]{geometry}`. | HIGH |
### Figure and Table Packages
| Package | Purpose | Why This One | Confidence |
|---------|---------|-------------|------------|
| `graphicx` | Figure inclusion | Standard `\includegraphics` command for PNG/PDF figures from matplotlib. | HIGH |
| `float` | Float placement | Provides `[H]` specifier for "place exactly here". Essential when figures must appear at a specific position. | HIGH |
| `caption` | Caption customization | Customize caption fonts, spacing, separator to match template. | HIGH |
| `subcaption` | Subfigures | Multi-panel figures (e.g., in-degree + out-degree side by side). `subfigure` environment. | HIGH |
| `booktabs` | Professional tables | `\toprule`, `\midrule`, `\bottomrule` for clean tables. Used for centrality rankings, per-hour metrics, comparison tables. | HIGH |
### Cross-referencing and Navigation
| Package | Purpose | Notes | Confidence |
|---------|---------|-------|------------|
| `hyperref` | Clickable PDF links | Makes TOC, figures, tables, citations clickable. **Load late in preamble.** | HIGH |
| `cleveref` | Smart cross-references | `\cref{fig:rq1}` auto-produces "Figure 1" / "figure 1" in French. **Load after hyperref.** | HIGH |
### Bibliography
| Package | Purpose | Notes | Confidence |
|---------|---------|-------|------------|
| `biblatex` with `backend=biber` | Bibliography management | Full Unicode, flexible styles. Use `style=numeric` or `style=authoryear` per template. Separate bibliography/webography via `\printbibliography[keyword=web]`. | HIGH |
### Mathematics and Code
| Package | Purpose | Notes | Confidence |
|---------|---------|-------|------------|
| `amsmath` + `amssymb` | Mathematical notation | Modularity Q, Gini coefficient G, clustering coefficient C, power-law exponent alpha. | HIGH |
| `listings` | Code listings | Python code in appendices. No external dependency (unlike `minted` which needs Pygments + `-shell-escape`). Sufficient for this project. | HIGH |
### Styling and Layout
| Package | Purpose | Notes | Confidence |
|---------|---------|-------|------------|
| `xcolor` | Color definitions | `\definecolor{primary}{HTML}{2563EB}`. Used in headings, code listings, table accents. | HIGH |
| `fancyhdr` | Headers/footers | Custom page headers with chapter/section names, page numbers per template. | HIGH |
| `titlesec` | Section title formatting | Customize heading appearance (font, size, spacing, color). | HIGH |
| `tocloft` | TOC formatting | Customize TOC entry appearance. | MEDIUM |
| `setspace` | Line spacing | `\onehalfspacing` if template requires it. | MEDIUM |
### Package Loading Order
## Integration: Python Figures to LaTeX
### Recommended Approach: PNG at 200 DPI
### Workflow
# Save with proper background preservation
### Approaches NOT Recommended for This Project
| Approach | Why Not Here |
|----------|-------------|
| PGF backend | Network graphs with 5000+ nodes produce enormous PGF files. Dark backgrounds are not standard PGF territory. |
| PDF vector export | Network graph PDFs with thousands of nodes are 10+ MB. Fine for simple line charts but not for this project's primary figures. |
| matplot2tikz | Breaks on custom colormaps, network layouts, scatter with alpha. Too fragile for production use. |
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Graph library | NetworkX 3.4 | graph-tool | 40-250x faster per benchmarks, but requires C++ compilation, extremely complex install on Windows (no pip wheel), overkill for ~13k nodes which NetworkX handles in seconds |
| Graph library | NetworkX 3.4 | igraph (python-igraph) | 5-20x faster, C-based. Adds compilation dependency, less Pythonic API, less matplotlib integration. Not worth the complexity for this dataset size |
| Community detection | NX built-in Louvain | python-louvain 0.16 | Abandoned since Jan 2022. NetworkX 3.x has identical algorithm built in |
| Community detection | NX built-in Louvain | CDlib | 39 algorithms when we need exactly 1. Pulls igraph + leidenalg + 20 other deps |
| Visualization | Matplotlib 3.9 + custom style.py | SciencePlots | Requires LaTeX for style rendering. Project already has comprehensive custom styling |
| Visualization | Matplotlib 3.9 | Plotly | Interactive only, produces HTML not PNG/PDF |
| Data processing | Pandas 2.2 | Polars | Faster but less mature ecosystem, overkill for a single 74MB CSV |
| LaTeX engine | pdfLaTeX | LuaLaTeX/XeLaTeX | No OpenType font requirements. pdfLaTeX is simpler, faster, T1 handles all French characters |
| Bibliography | biblatex + biber | natbib + bibtex | biblatex is more modern, better Unicode for French names, more flexible |
| Figure format | PNG 200 DPI | PGF/TikZ | Network graphs with thousands of nodes produce enormous PGF files |
## Installation
### Python Dependencies (requirements.txt)
### LaTeX (Windows)
### Build Pipeline
# 1. Generate all figures
# 2. Compile report
## Version Pinning Strategy
- `networkx~=3.4.2` allows 3.4.3+ but not 3.5
- `pandas~=2.2.3` allows 2.2.4+ but not 2.3
- This balances stability with security patches
## Sources
- NetworkX 3.4.2 release: https://networkx.org/documentation/stable/release/release_3.4.2.html
- NetworkX community algorithms: https://networkx.org/documentation/stable/reference/algorithms/community.html
- NetworkX louvain_communities: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html
- python-louvain PyPI (last update Jan 2022): https://pypi.org/project/python-louvain/
- Matplotlib PyPI 3.9.4: https://pypi.org/project/matplotlib/3.9.4/
- Matplotlib PGF backend: https://jwalton.info/Matplotlib-latex-PGF/
- Pandas release notes: https://pandas.pydata.org/docs/whatsnew/index.html
- NumPy PyPI: https://pypi.org/project/numpy/
- SciPy sparse.csgraph: https://docs.scipy.org/doc/scipy/reference/sparse.csgraph.html
- powerlaw paper (PLOS ONE): https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0085777
- graph-tool benchmarks: https://graph-tool.skewed.de/performance.html
- 2025 graph tools comparison: https://link.springer.com/article/10.1007/s13278-025-01409-y
- tikzplotlib deprecation / matplot2tikz: https://pypi.org/project/matplot2tikz/
- babel-french v4.0e: https://ctan.org/pkg/babel-french
- Essential LaTeX packages: https://inscrive.io/articles/essential-latex-packages
- Publication-quality matplotlib: https://www.steven-braun.com/blog/2021/matplotlib-viz/
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
