"""RQ2: Analyse de la centralite des noeuds.

Identifie les noeuds les plus influents dans le reseau WETH Polygon
pendant le crash du 5 aout 2024 a travers quatre mesures de centralite
complementaires:
- Centralite de degre (entrant et sortant)
- Centralite d'intermediarite (betweenness, echantillonnee k=500)
- Centralite de proximite (closeness, sur la plus grande WCC)
- PageRank pondere

Produit 2 figures:
- figures/rq2_centrality_barplots.png : Top-10 par mesure de centralite (4 sous-graphiques)
- figures/rq2_centrality_comparison.png : Matrice de correlation de Spearman entre mesures
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

from src.graph_builder import load_and_build, get_largest_component
from src.style import (
    apply_global_style, light_style, dark_style, save_figure,
    format_address, format_number,
    PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER,
    BG_DARK, PALETTE, FIGSIZE, SEED
)
import matplotlib.colors as mcolors


def _top_k(centrality_dict, k=10):
    """Extrait les top-k noeuds tries par valeur de centralite decroissante.

    Parametres:
        centrality_dict: dict {noeud: valeur_centralite}
        k: nombre de noeuds a retourner

    Retourne:
        liste de tuples (adresse, valeur) triee par valeur decroissante
    """
    return sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)[:k]


def _print_top10(title, top10_list):
    """Affiche un classement top-10 formate dans la console.

    Parametres:
        title: titre du classement
        top10_list: liste de tuples (adresse, valeur)
    """
    print(f"\n--- {title} ---")
    for i, (addr, val) in enumerate(top10_list, 1):
        print(f"  {i:2d}. {format_address(addr)}  {val:.6f}")


def compute_degree_centrality(digraph):
    """Calcule la centralite de degre entrant et sortant.

    Utilise les fonctions normalisees de NetworkX qui divisent
    par (n-1) pour rendre les valeurs comparables entre graphes.

    Parametres:
        digraph: nx.DiGraph du reseau

    Retourne:
        dict avec les centralites completes et les top-10
    """
    in_cent = nx.in_degree_centrality(digraph)
    out_cent = nx.out_degree_centrality(digraph)

    top10_in = _top_k(in_cent)
    top10_out = _top_k(out_cent)

    _print_top10("Centralite de degre entrant (top 10)", top10_in)
    _print_top10("Centralite de degre sortant (top 10)", top10_out)

    return {
        'in_degree': in_cent,
        'out_degree': out_cent,
        'top10_in': top10_in,
        'top10_out': top10_out,
    }


def compute_betweenness_centrality(digraph):
    """Calcule la centralite d'intermediarite par echantillonnage.

    CRITIQUE: utilise k=500 noeuds pivots avec seed=42 pour eviter
    une execution trop longue (O(VE) complet sur ~13k noeuds).

    Parametres:
        digraph: nx.DiGraph du reseau

    Retourne:
        dict avec la centralite complete et le top-10
    """
    print("\n  Calcul betweenness (k=500 pivots, seed=42)...")
    bet = nx.betweenness_centrality(digraph, k=500, seed=42)

    top10_bet = _top_k(bet)
    _print_top10("Centralite d'intermediarite / betweenness (top 10)", top10_bet)

    return {
        'betweenness': bet,
        'top10_bet': top10_bet,
    }


def compute_closeness_centrality(digraph, graph):
    """Calcule la centralite de proximite sur la plus grande composante connexe.

    La closeness n'est definie que sur un graphe connexe. On extrait donc
    la plus grande WCC (composante faiblement connexe) du graphe non-oriente
    avant de calculer.

    Parametres:
        digraph: nx.DiGraph du reseau (non utilise directement)
        graph: nx.Graph version non-orientee

    Retourne:
        dict avec la centralite, le top-10 et la taille de la WCC
    """
    largest_wcc = get_largest_component(graph)
    wcc_size = largest_wcc.number_of_nodes()

    print(f"\n  Calcul closeness sur la plus grande WCC ({format_number(wcc_size)} noeuds)...")
    clo = nx.closeness_centrality(largest_wcc)

    top10_clo = _top_k(clo)
    _print_top10("Centralite de proximite / closeness (top 10, sur WCC)", top10_clo)

    return {
        'closeness': clo,
        'top10_clo': top10_clo,
        'wcc_size': wcc_size,
    }


def compute_pagerank(digraph):
    """Calcule le PageRank pondere du graphe oriente.

    Utilise les poids des aretes (montants WETH agreges) pour
    ponderer l'importance relative des liens.

    Parametres:
        digraph: nx.DiGraph du reseau

    Retourne:
        dict avec le PageRank complet et le top-10
    """
    pr = nx.pagerank(digraph, weight='weight')

    top10_pr = _top_k(pr)
    _print_top10("PageRank pondere (top 10)", top10_pr)

    return {
        'pagerank': pr,
        'top10_pr': top10_pr,
    }


def plot_centrality_barplots(degree_data, betweenness_data, closeness_data, pagerank_data):
    """Trace les barres horizontales du top-10 pour chaque mesure de centralite.

    Produit une figure 2x2 avec:
    - (0,0) Centralite de degre entrant
    - (0,1) Centralite de degre sortant
    - (1,0) Centralite d'intermediarite (betweenness)
    - (1,1) PageRank pondere

    Parametres:
        degree_data: dict retourne par compute_degree_centrality()
        betweenness_data: dict retourne par compute_betweenness_centrality()
        closeness_data: dict retourne par compute_closeness_centrality()
        pagerank_data: dict retourne par compute_pagerank()
    """
    # Donnees pour les 4 sous-graphiques
    panels = [
        ("Centralite de degre entrant (top 10)", degree_data['top10_in'], PRIMARY),
        ("Centralite de degre sortant (top 10)", degree_data['top10_out'], SECONDARY),
        ("Centralite d'intermediarite (top 10)", betweenness_data['top10_bet'], ACCENT),
        ("PageRank pondere (top 10)", pagerank_data['top10_pr'], SUCCESS),
    ]

    with light_style():
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        for ax, (title, top10, color) in zip(axes.flat, panels):
            # Extraire les adresses tronquees et les valeurs
            labels = [format_address(addr) for addr, _ in top10]
            values = [val for _, val in top10]

            # Barres horizontales (rang 1 en haut)
            ax.barh(range(len(labels)), values, color=color, alpha=0.85, edgecolor='white', linewidth=0.5)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=9, fontfamily='monospace')
            ax.invert_yaxis()
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_xlabel('Valeur de centralite')

            # Annoter les valeurs sur les barres
            for i, val in enumerate(values):
                ax.text(val, i, f' {val:.5f}', va='center', fontsize=8, color='#333')

        fig.suptitle('Classement des noeuds par mesure de centralite', fontsize=14, fontweight='bold')
        save_figure(fig, 'rq2_centrality_barplots.png')


def plot_centrality_comparison(degree_data, betweenness_data, closeness_data, pagerank_data):
    """Trace la matrice de correlation de Spearman entre les mesures de centralite.

    Calcule la correlation de rang sur les noeuds presents dans toutes
    les mesures (intersection avec les noeuds de la WCC pour closeness).

    Parametres:
        degree_data: dict retourne par compute_degree_centrality()
        betweenness_data: dict retourne par compute_betweenness_centrality()
        closeness_data: dict retourne par compute_closeness_centrality()
        pagerank_data: dict retourne par compute_pagerank()
    """
    # Noeuds presents dans toutes les mesures (closeness est le sous-ensemble limitant)
    common_nodes = set(closeness_data['closeness'].keys())
    common_nodes &= set(degree_data['in_degree'].keys())
    common_nodes &= set(betweenness_data['betweenness'].keys())
    common_nodes &= set(pagerank_data['pagerank'].keys())

    nodes = sorted(common_nodes)
    print(f"\n  Correlation de Spearman sur {format_number(len(nodes))} noeuds communs")

    # Construire les vecteurs de valeurs pour chaque mesure
    measure_names = ["Degre entrant", "Betweenness", "Closeness", "PageRank"]
    vectors = [
        [degree_data['in_degree'][n] for n in nodes],
        [betweenness_data['betweenness'][n] for n in nodes],
        [closeness_data['closeness'][n] for n in nodes],
        [pagerank_data['pagerank'][n] for n in nodes],
    ]

    # Matrice de correlation de Spearman 4x4
    n_measures = len(measure_names)
    corr_matrix = np.ones((n_measures, n_measures))
    for i in range(n_measures):
        for j in range(i + 1, n_measures):
            rho, _ = spearmanr(vectors[i], vectors[j])
            corr_matrix[i, j] = rho
            corr_matrix[j, i] = rho

    # Afficher les correlations
    print("\n--- Matrice de correlation de Spearman ---")
    for i, name_i in enumerate(measure_names):
        for j, name_j in enumerate(measure_names):
            if j > i:
                print(f"  {name_i} vs {name_j}: rho = {corr_matrix[i, j]:.4f}")

    with light_style():
        fig, ax = plt.subplots(figsize=(8, 7))

        # Heatmap
        im = ax.imshow(corr_matrix, cmap='RdYlBu_r', vmin=-1, vmax=1, aspect='equal')

        # Axes et labels
        ax.set_xticks(range(n_measures))
        ax.set_yticks(range(n_measures))
        ax.set_xticklabels(measure_names, rotation=45, ha='right', fontsize=11)
        ax.set_yticklabels(measure_names, fontsize=11)

        # Annoter chaque cellule avec la valeur de correlation
        for i in range(n_measures):
            for j in range(n_measures):
                val = corr_matrix[i, j]
                text_color = 'white' if abs(val) > 0.6 else 'black'
                ax.text(j, i, f'{val:.3f}', ha='center', va='center',
                        fontsize=12, fontweight='bold', color=text_color)

        ax.set_title('Correlation de Spearman entre mesures de centralite',
                      fontsize=13, fontweight='bold', pad=15)

        # Barre de couleurs
        cbar = fig.colorbar(im, ax=ax, shrink=0.8, label='Coefficient de Spearman')
        cbar.ax.tick_params(labelsize=10)

        save_figure(fig, 'rq2_centrality_comparison.png')


def plot_centrality_network(digraph, degree_data, betweenness_data, pagerank_data):
    """Trace le sous-graphe des noeuds les plus centraux (fond sombre).

    Extrait les top-30 noeuds par degre entrant et leurs voisins directs.
    Les noeuds sont dimensionnes par PageRank et colores par betweenness.

    Parametres:
        digraph: nx.DiGraph du reseau
        degree_data: dict retourne par compute_degree_centrality()
        betweenness_data: dict retourne par compute_betweenness_centrality()
        pagerank_data: dict retourne par compute_pagerank()
    """
    # Top-30 noeuds par degre entrant
    top30 = sorted(degree_data['in_degree'].items(), key=lambda x: x[1], reverse=True)[:30]
    central_nodes = set(n for n, _ in top30)

    # Ajouter voisins directs (max 15 par noeud central)
    ego_nodes = set(central_nodes)
    for h in central_nodes:
        neighbors = list(digraph.successors(h)) + list(digraph.predecessors(h))
        ego_nodes.update(neighbors[:15])

    # Plafonner a 500 noeuds
    if len(ego_nodes) > 500:
        total_deg = {n: digraph.in_degree(n) + digraph.out_degree(n) for n in ego_nodes}
        non_central = ego_nodes - central_nodes
        sorted_nc = sorted(non_central, key=lambda n: total_deg[n], reverse=True)
        ego_nodes = central_nodes | set(sorted_nc[:470])

    sub = digraph.subgraph(ego_nodes).copy()

    # Layout
    pos = nx.spring_layout(sub, seed=SEED, k=1.8 / np.sqrt(max(sub.number_of_nodes(), 1)))

    # Tailles par PageRank
    pr = pagerank_data['pagerank']
    pr_vals = [pr.get(n, 0) for n in sub.nodes()]
    pr_min, pr_max = min(pr_vals), max(pr_vals)
    node_sizes = [15 + 385 * (pr.get(n, 0) - pr_min) / (pr_max - pr_min + 1e-12) for n in sub.nodes()]

    # Couleurs par betweenness (gradient bleu -> orange)
    bet = betweenness_data['betweenness']
    bet_vals = np.array([bet.get(n, 0) for n in sub.nodes()])
    bet_norm = bet_vals / (bet_vals.max() + 1e-12)

    # Colormap personnalisee: bleu froid -> orange chaud
    cmap = mcolors.LinearSegmentedColormap.from_list('bet_cmap', [PRIMARY, ACCENT])
    node_colors = [cmap(v) for v in bet_norm]

    with dark_style():
        fig, ax = plt.subplots(figsize=(14, 10))

        nx.draw_networkx_edges(
            sub, pos, ax=ax,
            edge_color='#334155', alpha=0.1, width=0.3,
            arrows=True, arrowsize=3, arrowstyle='->'
        )

        nodes = nx.draw_networkx_nodes(
            sub, pos, ax=ax,
            node_color=node_colors, node_size=node_sizes,
            alpha=0.85, edgecolors='none'
        )

        # Labels pour top-10 noeuds
        top10_nodes = set(n for n, _ in top30[:10])
        labels = {n: format_address(n, 4) for n in sub.nodes() if n in top10_nodes}
        nx.draw_networkx_labels(sub, pos, labels, ax=ax,
                                font_size=7, font_color='white', font_weight='bold')

        ax.set_title(
            'Centralite du reseau WETH\n'
            '(taille = PageRank, couleur = betweenness)',
            color='white', fontsize=14, pad=15
        )

        # Barre de couleurs pour betweenness
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, bet_vals.max()))
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
        cbar.set_label('Betweenness centrality', color='white', fontsize=10)
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

        ax.set_axis_off()
        save_figure(fig, 'rq2_centrality_network.png')


def build_comparison_table(degree_data, betweenness_data, closeness_data, pagerank_data):
    """Construit un tableau comparatif des top-10 noeuds par mesure.

    Pour chaque rang 1 a 10, indique l'adresse classee a ce rang
    pour chaque mesure de centralite.

    Parametres:
        degree_data: dict retourne par compute_degree_centrality()
        betweenness_data: dict retourne par compute_betweenness_centrality()
        closeness_data: dict retourne par compute_closeness_centrality()
        pagerank_data: dict retourne par compute_pagerank()

    Retourne:
        liste de dicts, un par rang, avec les adresses et valeurs par mesure
    """
    table = []
    for rank in range(10):
        row = {'rank': rank + 1}
        # Degre entrant
        addr_in, val_in = degree_data['top10_in'][rank]
        row['in_degree_addr'] = addr_in
        row['in_degree_val'] = val_in
        # Degre sortant
        addr_out, val_out = degree_data['top10_out'][rank]
        row['out_degree_addr'] = addr_out
        row['out_degree_val'] = val_out
        # Betweenness
        addr_bet, val_bet = betweenness_data['top10_bet'][rank]
        row['betweenness_addr'] = addr_bet
        row['betweenness_val'] = val_bet
        # Closeness
        addr_clo, val_clo = closeness_data['top10_clo'][rank]
        row['closeness_addr'] = addr_clo
        row['closeness_val'] = val_clo
        # PageRank
        addr_pr, val_pr = pagerank_data['top10_pr'][rank]
        row['pagerank_addr'] = addr_pr
        row['pagerank_val'] = val_pr
        table.append(row)
    return table


def run(df=None, digraph=None, graph=None):
    """Point d'entree RQ2 - Centralite.

    Identifie les noeuds les plus influents dans le reseau WETH Polygon
    a travers quatre mesures de centralite complementaires.

    Parametres:
        df: DataFrame pandas (charge automatiquement si None)
        digraph: nx.DiGraph (charge automatiquement si None)
        graph: nx.Graph non-oriente (charge automatiquement si None)

    Retourne:
        dict avec les top-10 par mesure, la taille WCC et le tableau comparatif
    """
    if df is None:
        df, digraph, graph = load_and_build()
    apply_global_style()

    print("\n=== RQ2: Analyse de la centralite des noeuds ===")

    # Etape 1: Centralite de degre (entrant + sortant)
    degree_data = compute_degree_centrality(digraph)

    # Etape 2: Centralite d'intermediarite (echantillonnee)
    betweenness_data = compute_betweenness_centrality(digraph)

    # Etape 3: Centralite de proximite (sur WCC)
    closeness_data = compute_closeness_centrality(digraph, graph)

    # Etape 4: PageRank pondere
    pagerank_data = compute_pagerank(digraph)

    # Etape 5: Figure 1 - Barres horizontales top-10 (4 sous-graphiques)
    plot_centrality_barplots(degree_data, betweenness_data, closeness_data, pagerank_data)

    # Etape 6: Figure 2 - Matrice de correlation de Spearman
    plot_centrality_comparison(degree_data, betweenness_data, closeness_data, pagerank_data)

    # Etape 7: Figure 3 - Graphe reseau de centralite (fond sombre)
    plot_centrality_network(digraph, degree_data, betweenness_data, pagerank_data)

    # Etape 8: Tableau comparatif pour le rapport LaTeX
    comparison = build_comparison_table(degree_data, betweenness_data, closeness_data, pagerank_data)

    print("\n=== RQ2 terminee ===\n")

    return {
        'top10_in_degree': degree_data['top10_in'],
        'top10_out_degree': degree_data['top10_out'],
        'top10_betweenness': betweenness_data['top10_bet'],
        'top10_closeness': closeness_data['top10_clo'],
        'top10_pagerank': pagerank_data['top10_pr'],
        'wcc_size_closeness': closeness_data['wcc_size'],
        'comparison_table': comparison,
    }


if __name__ == "__main__":
    run()
