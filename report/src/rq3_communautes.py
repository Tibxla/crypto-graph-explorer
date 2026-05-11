"""RQ3: Detection et analyse des communautes.

Detecte les communautes dans le reseau WETH Polygon pendant le crash
du 5 aout 2024 en utilisant l'algorithme de Louvain (NetworkX built-in):
- Detection de communautes par Louvain (graphe non-oriente)
- Score de modularite Q
- Distribution de la taille des communautes
- Visualisation du sous-graphe des principales communautes

Produit 2 figures:
- figures/rq3_communities.png : Visualisation reseau des principales communautes (fond sombre)
- figures/rq3_community_sizes.png : Distribution de la taille des communautes (fond clair)
"""

import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

from src.graph_builder import load_and_build
from src.style import (
    apply_global_style, dark_style, light_style, save_figure,
    format_address, format_number,
    PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER, INFO, PINK,
    PALETTE, BG_DARK, FIGSIZE, SEED
)


def detect_communities(graph):
    """Detecte les communautes par l'algorithme de Louvain (NetworkX built-in).

    Utilise le graphe non-oriente avec poids pour la detection.
    Les communautes sont triees par taille decroissante.

    Parametres:
        graph: nx.Graph non-oriente avec attribut 'weight' sur les aretes

    Retourne:
        liste de frozensets, triee par taille decroissante
    """
    print("\n--- Detection des communautes (Louvain) ---")
    communities = nx.community.louvain_communities(
        graph, weight='weight', seed=42, resolution=1.0
    )

    # Trier par taille decroissante
    communities = sorted(communities, key=len, reverse=True)

    print(f"  Nombre de communautes detectees: {len(communities)}")
    print(f"  Taille des 5 plus grandes communautes:")
    for i, c in enumerate(communities[:5]):
        print(f"    C{i+1}: {format_number(len(c))} noeuds")

    return communities


def compute_modularity(graph, communities):
    """Calcule le score de modularite Q du partitionnement.

    La modularite mesure la qualite de la partition: Q > 0.3 est
    generalement considere comme une structure communautaire significative.

    Parametres:
        graph: nx.Graph non-oriente
        communities: liste de frozensets (partitionnement)

    Retourne:
        float: score de modularite Q
    """
    Q = nx.community.modularity(graph, communities, weight='weight')

    print(f"\n--- Score de modularite ---")
    print(f"  Q = {Q:.4f}")
    if Q > 0.3:
        print(f"  -> Structure communautaire significative (Q > 0.3)")
    elif Q > 0.1:
        print(f"  -> Structure communautaire moderee (0.1 < Q <= 0.3)")
    else:
        print(f"  -> Structure communautaire faible (Q <= 0.1)")

    return Q


def analyze_community_sizes(communities):
    """Analyse la distribution des tailles de communautes.

    Calcule les statistiques descriptives: total, plus grande,
    singletons, mediane, moyenne, etc.

    Parametres:
        communities: liste de frozensets triee par taille decroissante

    Retourne:
        dict avec les statistiques de distribution
    """
    sizes = [len(c) for c in communities]
    total_nodes = sum(sizes)
    n_communities = len(communities)
    largest_size = sizes[0]
    largest_pct = largest_size / total_nodes * 100 if total_nodes > 0 else 0
    singletons = sum(1 for s in sizes if s == 1)
    n_above_10 = sum(1 for s in sizes if s >= 10)

    print(f"\n--- Distribution des tailles de communautes ---")
    print(f"  Total communautes:      {format_number(n_communities)}")
    print(f"  Plus grande:            {format_number(largest_size)} noeuds ({largest_pct:.1f}% du reseau)")
    print(f"  Top 10 tailles:         {sizes[:10]}")
    print(f"  Singletons (taille=1):  {format_number(singletons)}")
    print(f"  Communautes >= 10:      {format_number(n_above_10)}")
    print(f"  Taille moyenne:         {np.mean(sizes):.1f}")
    print(f"  Taille mediane:         {np.median(sizes):.1f}")

    return {
        'sizes': sizes,
        'n_communities': n_communities,
        'largest_size': largest_size,
        'largest_pct': largest_pct,
        'singletons': singletons,
        'n_above_10': n_above_10,
    }


def plot_community_network(graph, communities):
    """Trace la visualisation reseau des principales communautes.

    Sous-echantillonne le graphe a 300-500 noeuds en selectionnant
    les plus grandes communautes. Les noeuds sont colores par communaute
    et dimensionnes par degre. Fond sombre (#0F172A).

    Parametres:
        graph: nx.Graph non-oriente
        communities: liste de frozensets triee par taille decroissante
    """
    print("\n  Generation de la visualisation reseau des communautes...")

    # Selectionner les noeuds pour le sous-graphe (cible: 300-500 noeuds)
    random.seed(SEED)
    selected_nodes = []
    community_indices = []  # indice de la communaute pour chaque noeud

    for i, comm in enumerate(communities[:7]):
        comm_list = list(comm)
        # Si la communaute est grande, echantillonner
        if len(comm_list) > 100:
            sampled = random.sample(comm_list, 100)
        else:
            sampled = comm_list

        selected_nodes.extend(sampled)
        community_indices.extend([i] * len(sampled))

        # Arreter si on a assez de noeuds
        if len(selected_nodes) >= 400:
            break

    # Construire le sous-graphe
    sub = graph.subgraph(selected_nodes)

    # Carte des couleurs par noeud
    node_to_comm = {}
    for node, comm_idx in zip(selected_nodes, community_indices):
        node_to_comm[node] = comm_idx

    # Couleurs des noeuds (dans l'ordre du sous-graphe)
    node_colors = [PALETTE[node_to_comm.get(n, 0) % len(PALETTE)] for n in sub.nodes()]

    # Tailles par degre dans le sous-graphe
    degrees = dict(sub.degree())
    degree_values = [degrees[n] for n in sub.nodes()]
    min_d = min(degree_values) if degree_values else 0
    max_d = max(degree_values) if degree_values else 1
    node_sizes = [20 + 180 * (d - min_d) / (max_d - min_d + 1) for d in degree_values]

    # Layout
    pos = nx.spring_layout(sub, seed=SEED, k=1.5 / np.sqrt(max(sub.number_of_nodes(), 1)))

    with dark_style():
        fig, ax = plt.subplots(figsize=(14, 10))

        # Dessiner les aretes
        nx.draw_networkx_edges(
            sub, pos, ax=ax,
            edge_color='#334155', alpha=0.15, width=0.3, arrows=False
        )

        # Dessiner les noeuds
        nx.draw_networkx_nodes(
            sub, pos, ax=ax,
            node_color=node_colors, node_size=node_sizes,
            alpha=0.8, edgecolors='none'
        )

        # Titre
        ax.set_title(
            'Structure communautaire du reseau WETH\n'
            '(sous-graphe des principales communautes)',
            color='white', fontsize=14, pad=15
        )

        # Legende
        n_legend = min(len(communities), 7)
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w',
                       markerfacecolor=PALETTE[i % len(PALETTE)],
                       markersize=8,
                       label=f'C{i+1} ({format_number(len(communities[i]))} noeuds)')
            for i in range(n_legend)
        ]
        ax.legend(
            handles=legend_elements, loc='upper left',
            fontsize=9, facecolor=BG_DARK, edgecolor='#334155',
            labelcolor='white'
        )

        ax.set_axis_off()
        save_figure(fig, 'rq3_communities.png')


def plot_community_sizes(communities, size_data):
    """Trace le diagramme en barres de la distribution des tailles de communautes.

    Affiche les communautes triees par taille decroissante. Si plus de 30
    communautes, affiche seulement les 20 plus grandes. Fond clair.

    Parametres:
        communities: liste de frozensets triee par taille decroissante
        size_data: dict retourne par analyze_community_sizes()
    """
    sizes = size_data['sizes']
    n_communities = size_data['n_communities']

    # Limiter a 20 si trop de communautes
    show_n = min(20, len(sizes))
    shown_sizes = sizes[:show_n]
    remaining = len(sizes) - show_n

    with light_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)

        # Couleurs: top-5 avec PALETTE, le reste en gris
        bar_colors = []
        for i in range(show_n):
            if i < 5:
                bar_colors.append(PALETTE[i % len(PALETTE)])
            else:
                bar_colors.append('#94A3B8')

        x_labels = [f'C{i+1}' for i in range(show_n)]
        bars = ax.bar(x_labels, shown_sizes, color=bar_colors, alpha=0.85,
                      edgecolor='white', linewidth=0.5)

        # Echelle logarithmique si le rapport est > 100x
        if len(shown_sizes) > 1 and shown_sizes[0] > 100 * shown_sizes[-1]:
            ax.set_yscale('log')

        # Ligne horizontale a la moyenne
        mean_size = np.mean(sizes)
        ax.axhline(y=mean_size, color=DANGER, linestyle='--', alpha=0.7,
                   label=f'Moyenne = {mean_size:.0f}')

        ax.set_xlabel('Communaute (ordonnee par taille decroissante)')
        ax.set_ylabel('Nombre de noeuds')
        ax.set_title('Distribution de la taille des communautes')
        ax.legend(fontsize=10)

        # Rotation des labels si nombreux
        if show_n > 10:
            plt.xticks(rotation=45, ha='right')

        # Annotation avec les statistiques cles
        # Calculer la modularite n'est pas disponible ici, mais on a les stats de taille
        annotation_text = (
            f"Total: {format_number(n_communities)} communautes\n"
            f"Singletons: {format_number(size_data['singletons'])}\n"
            f"Comm. >= 10 noeuds: {format_number(size_data['n_above_10'])}"
        )
        if remaining > 0:
            annotation_text += f"\n({remaining} autres non affichees)"

        ax.annotate(
            annotation_text,
            xy=(0.97, 0.97), xycoords='axes fraction',
            fontsize=9, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor='#CBD5E1', alpha=0.9)
        )

        save_figure(fig, 'rq3_community_sizes.png')


def run(df=None, digraph=None, graph=None):
    """Point d'entree RQ3 - Communautes.

    Detection et analyse des communautes dans le reseau WETH Polygon:
    Louvain sur graphe non-oriente, modularite, distribution des tailles,
    et 2 visualisations.

    Parametres:
        df: DataFrame pandas (charge automatiquement si None)
        digraph: nx.DiGraph (charge automatiquement si None)
        graph: nx.Graph non-oriente (charge automatiquement si None)

    Retourne:
        dict avec les metriques de communaute
    """
    if df is None:
        df, digraph, graph = load_and_build()
    apply_global_style()

    print("\n=== RQ3: Detection et analyse des communautes ===")

    # Detection de communautes (sur graphe non-oriente)
    communities = detect_communities(graph)
    Q = compute_modularity(graph, communities)
    size_data = analyze_community_sizes(communities)

    # Visualisations
    plot_community_network(graph, communities)
    plot_community_sizes(communities, size_data)

    print("\n=== RQ3 terminee ===\n")

    return {
        'n_communities': size_data['n_communities'],
        'modularity': Q,
        'largest_size': size_data['largest_size'],
        'largest_pct': size_data['largest_pct'],
        'singletons': size_data['singletons'],
        'top10_sizes': size_data['sizes'][:10],
        'communities': communities,
    }


if __name__ == "__main__":
    run()
