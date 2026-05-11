"""RQ1: Analyse de la topologie globale du reseau.

Analyse la structure du reseau WETH Polygon pendant le crash du 5 aout 2024:
- Distribution des degres entrants/sortants (CCDF log-log)
- Densite du reseau
- Composantes connexes (fortement et faiblement)
- Diametre et longueur moyenne des chemins (echantillonnage)

Produit 2 figures:
- figures/rq1_degree_distribution.png : CCDF des degres en echelle log-log
- figures/rq1_components.png : Distribution de la taille des composantes connexes
"""

import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

from src.graph_builder import load_and_build, get_largest_component
from src.style import (
    apply_global_style, light_style, dark_style, save_figure,
    PRIMARY, SECONDARY, ACCENT, PALETTE, BG_DARK,
    FIGSIZE, SEED, format_number
)


def compute_ccdf(degrees):
    """Calcule la CCDF (fonction de repartition complementaire) d'une distribution de degres.

    Pour chaque valeur k, calcule P(X >= k) = 1 - CDF(k-1).
    Utilisee pour les graphiques log-log des distributions a queue lourde.

    Parametres:
        degrees: liste des valeurs de degres

    Retourne:
        (sorted_k, ccdf_at_k): listes triees des degres et de leur CCDF
    """
    counter = Counter(degrees)
    total = sum(counter.values())
    sorted_k = sorted(counter.keys())

    # P(X >= k) : probabilite que le degre soit >= k
    ccdf_at_k = []
    cumul = 0
    for k in sorted_k:
        ccdf_at_k.append(1.0 - cumul / total)
        cumul += counter[k]

    return sorted_k, ccdf_at_k


def compute_basic_metrics(digraph):
    """Calcule les metriques de base du reseau: noeuds, aretes, densite, degre moyen.

    Parametres:
        digraph: nx.DiGraph du reseau

    Retourne:
        dict avec les metriques de base
    """
    n = digraph.number_of_nodes()
    m = digraph.number_of_edges()
    density = nx.density(digraph)
    avg_degree = m / n if n > 0 else 0

    print("\n--- Metriques de base ---")
    print(f"  Noeuds:        {format_number(n)}")
    print(f"  Aretes:        {format_number(m)}")
    print(f"  Densite:       {density:.6f}")
    print(f"  Degre moyen:   {avg_degree:.2f}")

    return {'n': n, 'm': m, 'density': density, 'avg_degree': avg_degree}


def compute_degree_distributions(digraph):
    """Calcule les distributions de degres entrants et sortants.

    Parametres:
        digraph: nx.DiGraph du reseau

    Retourne:
        dict avec les degres, CCDF, et statistiques descriptives
    """
    in_degrees = [d for _, d in digraph.in_degree()]
    out_degrees = [d for _, d in digraph.out_degree()]

    in_k, in_ccdf = compute_ccdf(in_degrees)
    out_k, out_ccdf = compute_ccdf(out_degrees)

    # Statistiques descriptives
    in_arr = np.array(in_degrees)
    out_arr = np.array(out_degrees)

    print("\n--- Distribution des degres ---")
    print(f"  Degre entrant  : min={in_arr.min()}, max={in_arr.max()}, "
          f"moy={in_arr.mean():.2f}, med={np.median(in_arr):.1f}")
    print(f"  Degre sortant  : min={out_arr.min()}, max={out_arr.max()}, "
          f"moy={out_arr.mean():.2f}, med={np.median(out_arr):.1f}")

    return {
        'in_degrees': in_degrees, 'out_degrees': out_degrees,
        'in_k': in_k, 'in_ccdf': in_ccdf,
        'out_k': out_k, 'out_ccdf': out_ccdf,
        'in_max': int(in_arr.max()), 'out_max': int(out_arr.max()),
        'in_mean': float(in_arr.mean()), 'out_mean': float(out_arr.mean()),
    }


def compute_connected_components(digraph):
    """Calcule les composantes faiblement et fortement connexes.

    Parametres:
        digraph: nx.DiGraph du reseau

    Retourne:
        dict avec les listes de composantes et leurs statistiques
    """
    wcc = list(nx.weakly_connected_components(digraph))
    scc = list(nx.strongly_connected_components(digraph))

    # Trier par taille decroissante
    wcc.sort(key=len, reverse=True)
    scc.sort(key=len, reverse=True)

    n = digraph.number_of_nodes()
    wcc_sizes = [len(c) for c in wcc]
    scc_sizes = [len(c) for c in scc]

    print("\n--- Composantes connexes ---")
    print(f"  Composantes faiblement connexes (WCC): {format_number(len(wcc))}")
    print(f"    Geante: {format_number(wcc_sizes[0])} noeuds ({wcc_sizes[0]/n*100:.1f}%)")
    print(f"  Composantes fortement connexes (SCC):  {format_number(len(scc))}")
    print(f"    Geante: {format_number(scc_sizes[0])} noeuds ({scc_sizes[0]/n*100:.1f}%)")

    return {
        'wcc': wcc, 'scc': scc,
        'wcc_sizes': wcc_sizes, 'scc_sizes': scc_sizes,
        'n_wcc': len(wcc), 'n_scc': len(scc),
        'giant_wcc_size': wcc_sizes[0], 'giant_wcc_pct': wcc_sizes[0] / n * 100,
        'giant_scc_size': scc_sizes[0], 'giant_scc_pct': scc_sizes[0] / n * 100,
    }


def compute_diameter_and_paths(digraph, graph, scc_list):
    """Estime le diametre (sur la plus grande SCC) et la longueur moyenne des chemins.

    Le diametre est estime par echantillonnage si la SCC depasse 5000 noeuds.
    La longueur moyenne des chemins est calculee sur la plus grande WCC
    (version non-orientee) par echantillonnage de 1000 paires aleatoires.

    Parametres:
        digraph: nx.DiGraph du reseau
        graph: nx.Graph version non-orientee
        scc_list: liste des SCC triees par taille decroissante

    Retourne:
        dict avec le diametre estime et la longueur moyenne des chemins
    """
    # Fixer les graines pour reproductibilite
    random.seed(SEED)
    np.random.seed(SEED)

    # Diametre sur la plus grande SCC
    largest_scc = digraph.subgraph(scc_list[0]).copy()
    scc_size = largest_scc.number_of_nodes()

    if scc_size > 5000:
        # Echantillonnage: excentricite de 500 noeuds aleatoires
        sample_nodes = random.sample(list(largest_scc.nodes()),
                                     min(500, scc_size))
        sampled_paths = []
        for node in sample_nodes:
            lengths = nx.single_source_shortest_path_length(largest_scc, node)
            sampled_paths.append(max(lengths.values()))
        approx_diameter = max(sampled_paths)
        diameter_method = f"echantillonne (500 noeuds sur {format_number(scc_size)})"
    else:
        approx_diameter = nx.diameter(largest_scc)
        diameter_method = f"exact (SCC de {format_number(scc_size)} noeuds)"

    # Longueur moyenne des chemins sur la plus grande WCC (non-orientee)
    largest_wcc = get_largest_component(graph)
    nodes_list = list(largest_wcc.nodes())
    wcc_size = len(nodes_list)
    n_samples = min(1000, wcc_size * (wcc_size - 1) // 2)

    random.seed(SEED)
    path_lengths = []
    for _ in range(n_samples):
        u, v = random.sample(nodes_list, 2)
        try:
            length = nx.shortest_path_length(largest_wcc, u, v)
            path_lengths.append(length)
        except nx.NetworkXNoPath:
            pass

    avg_path_length = float(np.mean(path_lengths)) if path_lengths else float('inf')

    print("\n--- Diametre et chemins ---")
    print(f"  Diametre (SCC geante):            {approx_diameter} ({diameter_method})")
    print(f"  Longueur moyenne des chemins:      {avg_path_length:.3f}")
    print(f"    (echantillon de {format_number(len(path_lengths))} paires sur WCC "
          f"de {format_number(wcc_size)} noeuds)")

    return {
        'diameter_approx': approx_diameter,
        'diameter_method': diameter_method,
        'avg_path_length': avg_path_length,
        'path_samples': len(path_lengths),
    }


def plot_degree_distribution(degree_data):
    """Trace la distribution des degres en echelle log-log (CCDF).

    Produit un graphique avec les degres entrants et sortants sur le meme plot,
    en utilisant le style analytique clair du projet.

    Parametres:
        degree_data: dict retourne par compute_degree_distributions()
    """
    with light_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)

        # CCDF des degres entrants
        ax.loglog(
            degree_data['in_k'], degree_data['in_ccdf'],
            'o', color=PRIMARY, markersize=4, alpha=0.7,
            label='Degre entrant'
        )

        # CCDF des degres sortants
        ax.loglog(
            degree_data['out_k'], degree_data['out_ccdf'],
            's', color=SECONDARY, markersize=4, alpha=0.7,
            label='Degre sortant'
        )

        ax.set_xlabel('Degre k')
        ax.set_ylabel('CCDF  P(X >= k)')
        ax.set_title('Distribution des degres du reseau WETH (echelle log-log)')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, which='both')

        save_figure(fig, 'rq1_degree_distribution.png')


def plot_components(comp_data):
    """Trace la distribution de la taille des composantes connexes.

    Affiche les 20 plus grandes composantes pour WCC et SCC
    sous forme de barres, avec echelle logarithmique si necessaire.

    Parametres:
        comp_data: dict retourne par compute_connected_components()
    """
    with light_style():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Top 20 WCC
        wcc_top = comp_data['wcc_sizes'][:20]
        ax1.bar(range(len(wcc_top)), wcc_top, color=PRIMARY, alpha=0.8)
        ax1.set_xlabel('Composante (rang)')
        ax1.set_ylabel('Nombre de noeuds')
        ax1.set_title('Composantes faiblement connexes')
        # Echelle log si la geante est > 10x la deuxieme
        if len(wcc_top) > 1 and wcc_top[0] > 10 * wcc_top[1]:
            ax1.set_yscale('log')

        # Top 20 SCC
        scc_top = comp_data['scc_sizes'][:20]
        ax2.bar(range(len(scc_top)), scc_top, color=SECONDARY, alpha=0.8)
        ax2.set_xlabel('Composante (rang)')
        ax2.set_ylabel('Nombre de noeuds')
        ax2.set_title('Composantes fortement connexes')
        if len(scc_top) > 1 and scc_top[0] > 10 * scc_top[1]:
            ax2.set_yscale('log')

        fig.suptitle('Distribution de la taille des composantes connexes', fontsize=14)

        save_figure(fig, 'rq1_components.png')


def plot_hub_network(digraph):
    """Trace le sous-graphe des hubs principaux (fond sombre).

    Extrait les top-20 noeuds par degre total (entrant + sortant)
    et leurs voisins directs, plafonne a ~500 noeuds pour la lisibilite.
    Les noeuds sont colores par ratio in/out et dimensionnes par degre.

    Parametres:
        digraph: nx.DiGraph du reseau
    """
    # Top-20 hubs par degre total
    total_degree = {n: digraph.in_degree(n) + digraph.out_degree(n) for n in digraph.nodes()}
    top_hubs = sorted(total_degree.items(), key=lambda x: x[1], reverse=True)[:20]
    hub_nodes = set(n for n, _ in top_hubs)

    # Ego-network: hubs + voisins directs
    ego_nodes = set(hub_nodes)
    for h in hub_nodes:
        neighbors = list(digraph.successors(h)) + list(digraph.predecessors(h))
        ego_nodes.update(neighbors[:25])  # max 25 voisins par hub

    # Plafonner a 500 noeuds
    if len(ego_nodes) > 500:
        # Garder les hubs + les voisins les plus connectes
        non_hubs = ego_nodes - hub_nodes
        non_hub_degrees = [(n, total_degree[n]) for n in non_hubs]
        non_hub_degrees.sort(key=lambda x: x[1], reverse=True)
        ego_nodes = hub_nodes | set(n for n, _ in non_hub_degrees[:480])

    sub = digraph.subgraph(ego_nodes).copy()
    print(f"\n  Sous-graphe hubs: {sub.number_of_nodes()} noeuds, {sub.number_of_edges()} aretes")

    # Layout
    pos = nx.spring_layout(sub, seed=SEED, k=1.5 / np.sqrt(max(sub.number_of_nodes(), 1)))

    # Tailles par degre total dans le sous-graphe
    degrees = {n: sub.in_degree(n) + sub.out_degree(n) for n in sub.nodes()}
    deg_vals = list(degrees.values())
    min_d, max_d = min(deg_vals), max(deg_vals)
    node_sizes = [15 + 285 * (degrees[n] - min_d) / (max_d - min_d + 1) for n in sub.nodes()]

    # Couleurs: hubs en accent (orange), voisins en primary (bleu)
    node_colors = [ACCENT if n in hub_nodes else PRIMARY for n in sub.nodes()]
    node_alphas = [0.95 if n in hub_nodes else 0.5 for n in sub.nodes()]

    with dark_style():
        fig, ax = plt.subplots(figsize=(14, 10))

        nx.draw_networkx_edges(
            sub, pos, ax=ax,
            edge_color='#334155', alpha=0.1, width=0.3,
            arrows=True, arrowsize=3, arrowstyle='->'
        )

        nx.draw_networkx_nodes(
            sub, pos, ax=ax,
            node_color=node_colors, node_size=node_sizes,
            alpha=0.8, edgecolors='none'
        )

        ax.set_title(
            'Topologie du reseau WETH\n'
            '(sous-graphe des 20 hubs principaux et leurs voisins)',
            color='white', fontsize=14, pad=15
        )

        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w',
                       markerfacecolor=ACCENT, markersize=10,
                       label=f'Hubs (top 20, degre max={max(d for n, d in top_hubs)})'),
            plt.Line2D([0], [0], marker='o', color='w',
                       markerfacecolor=PRIMARY, markersize=7,
                       label=f'Voisins ({sub.number_of_nodes() - len(hub_nodes)} noeuds)'),
        ]
        ax.legend(
            handles=legend_elements, loc='upper left',
            fontsize=9, facecolor=BG_DARK, edgecolor='#334155',
            labelcolor='white'
        )

        ax.set_axis_off()
        save_figure(fig, 'rq1_hub_network.png')


def run(df=None, digraph=None, graph=None):
    """Point d'entree RQ1 - Topologie.

    Analyse la structure globale du reseau: distribution des degres,
    densite, composantes connexes, diametre et longueur moyenne des chemins.

    Parametres:
        df: DataFrame pandas (charge automatiquement si None)
        digraph: nx.DiGraph (charge automatiquement si None)
        graph: nx.Graph non-oriente (charge automatiquement si None)

    Retourne:
        dict avec toutes les metriques calculees
    """
    if df is None:
        df, digraph, graph = load_and_build()
    apply_global_style()

    print("\n=== RQ1: Analyse de la topologie globale du reseau ===")

    # Etape 1: Metriques de base
    basic = compute_basic_metrics(digraph)

    # Etape 2: Distributions des degres
    degree_data = compute_degree_distributions(digraph)

    # Etape 3: Composantes connexes
    comp_data = compute_connected_components(digraph)

    # Etape 4: Diametre et longueur moyenne des chemins
    path_data = compute_diameter_and_paths(digraph, graph, comp_data['scc'])

    # Etape 5: Figure 1 - Distribution des degres (log-log CCDF)
    plot_degree_distribution(degree_data)

    # Etape 6: Figure 2 - Distribution des composantes connexes
    plot_components(comp_data)

    # Etape 7: Figure 3 - Graphe reseau des hubs (fond sombre)
    plot_hub_network(digraph)

    print("\n=== RQ1 terminee ===\n")

    # Retourner un dictionnaire avec toutes les metriques
    return {
        'n_nodes': basic['n'],
        'n_edges': basic['m'],
        'density': basic['density'],
        'avg_degree': basic['avg_degree'],
        'n_wcc': comp_data['n_wcc'],
        'n_scc': comp_data['n_scc'],
        'giant_wcc_size': comp_data['giant_wcc_size'],
        'giant_wcc_pct': comp_data['giant_wcc_pct'],
        'giant_scc_size': comp_data['giant_scc_size'],
        'giant_scc_pct': comp_data['giant_scc_pct'],
        'diameter_approx': path_data['diameter_approx'],
        'avg_path_length': path_data['avg_path_length'],
        'in_degree_max': degree_data['in_max'],
        'out_degree_max': degree_data['out_max'],
    }


if __name__ == "__main__":
    run()
