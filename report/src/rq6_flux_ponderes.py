"""RQ6: Analyse des flux ponderes et de la concentration.

Quantifie la distribution des volumes de transfert WETH sur le reseau
Polygon pendant le crash du 5 aout 2024 (Lundi Noir):
- Distribution des poids des aretes (echelle logarithmique)
- Coefficient de Gini mesurant la concentration des flux
- Courbe de Lorenz avec ligne d'egalite parfaite
- Identification des "whales" (top transferts)

Produit 2 figures:
- figures/rq6_weight_distribution.png : Histogramme des poids (echelle log)
- figures/rq6_lorenz_curve.png : Courbe de Lorenz avec coefficient de Gini
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from src.graph_builder import load_and_build
from src.style import (
    apply_global_style, light_style, dark_style, save_figure,
    format_number, format_address,
    PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER,
    BG_DARK, PALETTE, FIGSIZE, SEED
)
import matplotlib.colors as mcolors

# Constantes de l'analyse
DUST_THRESHOLD = 1e-12    # Seuil de filtrage des transactions poussiere
TOP_N_WHALES = 10         # Nombre de top transferts a identifier


def extract_weights(digraph, threshold=DUST_THRESHOLD):
    """Extrait et analyse les poids des aretes du DiGraph.

    Recupere tous les poids (weight = somme WETH par paire source/target),
    filtre les transactions poussiere sous le seuil, et calcule les
    statistiques descriptives de la distribution.

    IMPORTANT (Pitfall P4): les poids sont deja agreges dans le DiGraph
    (somme par paire). Ne PAS re-agreger depuis le DataFrame.

    Parametres:
        digraph: nx.DiGraph avec attribut 'weight' sur chaque arete
        threshold: seuil de filtrage poussiere (defaut: 1e-12 WETH)

    Retourne:
        dict avec 'weights_all', 'weights_clean', 'total_volume',
        'n_total', 'n_clean', 'n_dust', 'threshold', 'stats'
    """
    # Extraction de tous les poids des aretes
    weights = np.array([d['weight'] for u, v, d in digraph.edges(data=True)])
    total_volume = float(np.sum(weights))
    n_total = len(weights)

    print(f"  Aretes totales: {format_number(n_total)}")
    print(f"  Volume total WETH: {total_volume:.4f}")

    # Filtrage des transactions poussiere (Pitfall P16)
    weights_clean = weights[weights > threshold]
    n_clean = len(weights_clean)
    n_dust = n_total - n_clean

    print(f"  Seuil poussiere: {threshold:.0e} WETH")
    print(f"  Aretes poussiere filtrees: {format_number(n_dust)}")
    print(f"  Aretes apres filtrage: {format_number(n_clean)}")

    # Statistiques descriptives
    stats = {
        'min': float(np.min(weights_clean)),
        'max': float(np.max(weights_clean)),
        'mean': float(np.mean(weights_clean)),
        'median': float(np.median(weights_clean)),
        'std': float(np.std(weights_clean)),
        'p25': float(np.percentile(weights_clean, 25)),
        'p75': float(np.percentile(weights_clean, 75)),
        'p90': float(np.percentile(weights_clean, 90)),
        'p95': float(np.percentile(weights_clean, 95)),
        'p99': float(np.percentile(weights_clean, 99)),
    }

    print(f"\n  Statistiques descriptives (apres filtrage):")
    print(f"    Min:       {stats['min']:.10f} WETH")
    print(f"    Max:       {stats['max']:.4f} WETH")
    print(f"    Moyenne:   {stats['mean']:.4f} WETH")
    print(f"    Mediane:   {stats['median']:.6f} WETH")
    print(f"    Ecart-type: {stats['std']:.4f} WETH")
    print(f"    P25:       {stats['p25']:.6f} WETH")
    print(f"    P75:       {stats['p75']:.6f} WETH")
    print(f"    P90:       {stats['p90']:.4f} WETH")
    print(f"    P95:       {stats['p95']:.4f} WETH")
    print(f"    P99:       {stats['p99']:.4f} WETH")

    return {
        'weights_all': weights,
        'weights_clean': weights_clean,
        'total_volume': total_volume,
        'n_total': n_total,
        'n_clean': n_clean,
        'n_dust': n_dust,
        'threshold': threshold,
        'stats': stats,
    }


def compute_gini(weights):
    """Calcule le coefficient de Gini a partir d'un tableau de poids.

    Utilise la formule standard basee sur les poids tries:
    G = (2 * sum(i * w_i)) / (n * sum(w_i)) - (n+1)/n

    Un Gini de 0 signifie egalite parfaite (tous les flux identiques),
    un Gini de 1 signifie concentration totale (un seul flux porte tout).
    Pour les reseaux blockchain, on attend typiquement G > 0.9.

    Parametres:
        weights: np.array des poids des aretes (filtres)

    Retourne:
        float: coefficient de Gini (entre 0 et 1)
    """
    sorted_w = np.sort(weights)
    n = len(sorted_w)
    cumulative = np.cumsum(sorted_w)
    gini = (2 * np.sum((np.arange(1, n + 1) * sorted_w))) / (n * np.sum(sorted_w)) - (n + 1) / n

    print(f"  Coefficient de Gini: {gini:.4f}")
    print(f"  Interpretation: 0 = egalite parfaite, 1 = concentration totale")

    if gini > 0.9:
        print(f"  -> G = {gini:.4f} > 0.9 : concentration EXTREME des flux")
    elif gini > 0.7:
        print(f"  -> G = {gini:.4f} > 0.7 : concentration elevee des flux")
    elif gini > 0.5:
        print(f"  -> G = {gini:.4f} > 0.5 : concentration moderee des flux")
    else:
        print(f"  -> G = {gini:.4f} < 0.5 : distribution relativement equitable")

    return gini


def compute_lorenz(weights):
    """Calcule les donnees de la courbe de Lorenz.

    Trie les poids par ordre croissant et calcule les parts cumulees
    de la population (aretes) et du volume (WETH). Le point (0, 0) est
    ajoute comme origine de la courbe.

    La courbe de Lorenz montre quelle fraction du volume total est portee
    par les x% d'aretes les plus faibles. Plus la courbe s'ecarte de la
    diagonale (egalite parfaite), plus la concentration est forte.

    Parametres:
        weights: np.array des poids des aretes (filtres)

    Retourne:
        dict avec 'lorenz_x' (fractions population), 'lorenz_y' (fractions volume)
    """
    sorted_w = np.sort(weights)
    n = len(sorted_w)
    cumulative_volume = np.cumsum(sorted_w) / np.sum(sorted_w)
    cumulative_population = np.arange(1, n + 1) / n

    # Ajouter l'origine (0, 0) pour completer la courbe
    lorenz_x = np.concatenate(([0], cumulative_population))
    lorenz_y = np.concatenate(([0], cumulative_volume))

    # Quelques points remarquables
    # Quelle fraction du volume est portee par les 90% d'aretes les plus faibles ?
    idx_90 = int(0.9 * n) - 1
    if idx_90 >= 0:
        vol_90 = cumulative_volume[idx_90]
        print(f"  90% des aretes portent {vol_90*100:.1f}% du volume")
        print(f"  10% des aretes portent {(1-vol_90)*100:.1f}% du volume")

    idx_99 = int(0.99 * n) - 1
    if idx_99 >= 0 and idx_99 < n:
        vol_99 = cumulative_volume[idx_99]
        print(f"  99% des aretes portent {vol_99*100:.1f}% du volume")
        print(f"  1% des aretes portent {(1-vol_99)*100:.1f}% du volume")

    return {
        'lorenz_x': lorenz_x,
        'lorenz_y': lorenz_y,
    }


def identify_whales(digraph, top_n=TOP_N_WHALES):
    """Identifie les plus gros transferts individuels (whales).

    Trie toutes les aretes par poids decroissant et retourne les top_n
    transferts les plus importants. Calcule la part du volume total
    representee par ces top transferts.

    Parametres:
        digraph: nx.DiGraph avec attributs 'weight' et 'tx_count'
        top_n: nombre de whales a identifier (defaut: 10)

    Retourne:
        list de dicts avec 'source', 'target', 'weight', 'tx_count'
    """
    # Extraire toutes les aretes avec leurs poids
    edges_data = [(u, v, d['weight'], d.get('tx_count', 1))
                  for u, v, d in digraph.edges(data=True)]
    edges_sorted = sorted(edges_data, key=lambda x: x[2], reverse=True)
    top_whales = edges_sorted[:top_n]

    # Volume total pour calculer les pourcentages
    total_volume = sum(d['weight'] for u, v, d in digraph.edges(data=True))

    # Tableau des whales
    print(f"\n  {'Rang':>4} | {'Source':>16} | {'Cible':>16} | {'Poids (WETH)':>14} | {'Tx':>5} | {'% Volume':>9}")
    print(f"  {'-'*4}-+-{'-'*16}-+-{'-'*16}-+-{'-'*14}-+-{'-'*5}-+-{'-'*9}")

    whales_list = []
    cumul_volume = 0.0
    for i, (src, tgt, weight, tx_count) in enumerate(top_whales, 1):
        pct = weight / total_volume * 100
        cumul_volume += weight
        print(f"  {i:>4} | {format_address(src):>16} | {format_address(tgt):>16} | "
              f"{weight:>14.4f} | {tx_count:>5} | {pct:>8.2f}%")
        whales_list.append({
            'source': src,
            'target': tgt,
            'weight': weight,
            'tx_count': tx_count,
        })

    top_pct = cumul_volume / total_volume * 100
    print(f"\n  Top-{top_n} representent {top_pct:.1f}% du volume total ({cumul_volume:.4f} / {total_volume:.4f} WETH)")

    return whales_list


def plot_weight_distribution(weight_data):
    """Trace l'histogramme de la distribution des poids (echelle logarithmique).

    CRITIQUE (Pitfall P10): utilise une echelle logarithmique sur l'axe X
    avec des bins espaces logarithmiquement (np.logspace). Une echelle
    lineaire produirait une seule barre visible a cause de la distribution
    extremement asymetrique des poids blockchain.

    Fond clair (graphique analytique, pas reseau).

    Parametres:
        weight_data: dict retourne par extract_weights()
    """
    weights_clean = weight_data['weights_clean']

    with light_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)

        # Bins logarithmiques pour la distribution a queue lourde (Pitfall P10)
        log_min = np.log10(weights_clean.min())
        log_max = np.log10(weights_clean.max())
        bins = np.logspace(log_min, log_max, 50)

        ax.hist(weights_clean, bins=bins, color=PRIMARY, edgecolor='white', alpha=0.85)
        ax.set_xscale('log')

        # Lignes verticales pour la moyenne et la mediane
        ax.axvline(weight_data['stats']['mean'], color=DANGER, linestyle='--', linewidth=2,
                   label=f"Moyenne = {weight_data['stats']['mean']:.4f} WETH")
        ax.axvline(weight_data['stats']['median'], color=ACCENT, linestyle='--', linewidth=2,
                   label=f"Mediane = {weight_data['stats']['median']:.6f} WETH")

        ax.set_title("Distribution des poids des transferts WETH (echelle logarithmique)")
        ax.set_xlabel("Poids du transfert (WETH)")
        ax.set_ylabel("Nombre d'aretes")
        ax.legend(loc='upper right', fontsize=10)

        # Annotation avec les statistiques de filtrage
        annotation_text = (
            f"Aretes totales: {format_number(weight_data['n_total'])}\n"
            f"Apres filtrage: {format_number(weight_data['n_clean'])}\n"
            f"Poussiere filtree: {format_number(weight_data['n_dust'])}\n"
            f"Seuil: {weight_data['threshold']:.0e} WETH"
        )
        ax.annotate(
            annotation_text,
            xy=(0.97, 0.75), xycoords='axes fraction',
            fontsize=9, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor='#CBD5E1', alpha=0.9)
        )

        save_figure(fig, 'rq6_weight_distribution.png')


def plot_lorenz_curve(lorenz_data, gini, weight_data):
    """Trace la courbe de Lorenz avec la ligne d'egalite et l'annotation Gini.

    La courbe de Lorenz montre la part cumulee du volume WETH en fonction
    de la part cumulee des aretes (triees par poids croissant). La zone
    entre la diagonale (egalite parfaite) et la courbe est proportionnelle
    au coefficient de Gini.

    Fond clair (graphique analytique, pas reseau).

    Parametres:
        lorenz_data: dict retourne par compute_lorenz()
        gini: float retourne par compute_gini()
        weight_data: dict retourne par extract_weights()
    """
    with light_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)

        # Ligne d'egalite parfaite (diagonale a 45 degres)
        ax.plot([0, 1], [0, 1], color=SECONDARY, linestyle='--', linewidth=1.5,
                label='Egalite parfaite', alpha=0.7)

        # Courbe de Lorenz
        ax.plot(lorenz_data['lorenz_x'], lorenz_data['lorenz_y'],
                color=PRIMARY, linewidth=2.5, label='Courbe de Lorenz')

        # Zone entre egalite et Lorenz (aire de Gini)
        ax.fill_between(lorenz_data['lorenz_x'], lorenz_data['lorenz_y'],
                        lorenz_data['lorenz_x'],  # ligne d'egalite y = x
                        alpha=0.15, color=PRIMARY)

        # Annotation du coefficient de Gini
        ax.annotate(f'Gini = {gini:.4f}',
                    xy=(0.55, 0.25), fontsize=18, fontweight='bold',
                    color=PRIMARY,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                              edgecolor=PRIMARY, alpha=0.9))

        ax.set_title("Courbe de Lorenz des flux WETH")
        ax.set_xlabel("Part cumulee des aretes (triees par poids croissant)")
        ax.set_ylabel("Part cumulee du volume WETH")
        ax.legend(loc='upper left', fontsize=10)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        save_figure(fig, 'rq6_lorenz_curve.png')


def plot_whale_network(digraph):
    """Trace le sous-graphe des plus gros flux WETH (fond sombre).

    Extrait les top-50 aretes par volume et leurs noeuds.
    L'epaisseur des aretes est proportionnelle au log du poids,
    les noeuds sont dimensionnes par flux total et colores par
    direction nette (source = bleu, puits = rouge).

    Parametres:
        digraph: nx.DiGraph avec attribut 'weight' sur chaque arete
    """
    # Top-50 aretes par poids
    edges_data = [(u, v, d['weight']) for u, v, d in digraph.edges(data=True)]
    edges_sorted = sorted(edges_data, key=lambda x: x[2], reverse=True)
    top_edges = edges_sorted[:50]

    # Sous-graphe: noeuds impliques dans les top-50 aretes
    sub_nodes = set()
    for u, v, w in top_edges:
        sub_nodes.add(u)
        sub_nodes.add(v)

    sub = digraph.subgraph(sub_nodes).copy()
    # Garder seulement les aretes dans le top-50
    edges_to_keep = set((u, v) for u, v, _ in top_edges)
    edges_to_remove = [(u, v) for u, v in sub.edges() if (u, v) not in edges_to_keep]
    sub.remove_edges_from(edges_to_remove)

    print(f"\n  Sous-graphe whales: {sub.number_of_nodes()} noeuds, {sub.number_of_edges()} aretes")

    # Layout
    pos = nx.spring_layout(sub, seed=SEED, k=2.5 / np.sqrt(max(sub.number_of_nodes(), 1)),
                           weight='weight')

    # Tailles des noeuds par flux total (in + out)
    node_flow = {}
    for n in sub.nodes():
        flow_in = sum(d['weight'] for _, _, d in sub.in_edges(n, data=True))
        flow_out = sum(d['weight'] for _, _, d in sub.out_edges(n, data=True))
        node_flow[n] = flow_in + flow_out

    flow_vals = list(node_flow.values())
    min_f, max_f = min(flow_vals), max(flow_vals)
    node_sizes = [30 + 370 * (node_flow[n] - min_f) / (max_f - min_f + 1e-12) for n in sub.nodes()]

    # Couleurs des noeuds: source nette (bleu) vs puits net (rouge)
    net_flow = {}
    for n in sub.nodes():
        flow_in = sum(d['weight'] for _, _, d in sub.in_edges(n, data=True))
        flow_out = sum(d['weight'] for _, _, d in sub.out_edges(n, data=True))
        total = flow_in + flow_out
        net_flow[n] = (flow_out - flow_in) / (total + 1e-12)  # >0 = source, <0 = puits

    cmap_nodes = mcolors.LinearSegmentedColormap.from_list('flow_cmap', [DANGER, '#FFFFFF', PRIMARY])
    nf_vals = np.array([net_flow[n] for n in sub.nodes()])
    nf_norm = (nf_vals + 1) / 2  # normaliser [-1, 1] -> [0, 1]
    node_colors = [cmap_nodes(v) for v in nf_norm]

    # Epaisseur des aretes par log du poids
    edge_weights = [sub[u][v]['weight'] for u, v in sub.edges()]
    log_weights = np.log10(np.array(edge_weights) + 1)
    min_lw, max_lw = log_weights.min(), log_weights.max()
    edge_widths = [0.5 + 4.5 * (lw - min_lw) / (max_lw - min_lw + 1e-12) for lw in log_weights]

    # Couleurs aretes par poids (gradient)
    cmap_edges = mcolors.LinearSegmentedColormap.from_list('edge_cmap', ['#475569', ACCENT])
    edge_norm = (log_weights - min_lw) / (max_lw - min_lw + 1e-12)
    edge_colors = [cmap_edges(v) for v in edge_norm]

    with dark_style():
        fig, ax = plt.subplots(figsize=(14, 10))

        nx.draw_networkx_edges(
            sub, pos, ax=ax,
            edge_color=edge_colors, width=edge_widths,
            alpha=0.7, arrows=True, arrowsize=8, arrowstyle='->'
        )

        nx.draw_networkx_nodes(
            sub, pos, ax=ax,
            node_color=node_colors, node_size=node_sizes,
            alpha=0.9, edgecolors='#1E293B', linewidths=0.5
        )

        # Labels pour les plus gros noeuds (top-8 par flux)
        top_flow = sorted(node_flow.items(), key=lambda x: x[1], reverse=True)[:8]
        labels = {n: format_address(n, 4) for n, _ in top_flow}
        nx.draw_networkx_labels(sub, pos, labels, ax=ax,
                                font_size=7, font_color='white', font_weight='bold')

        ax.set_title(
            'Flux WETH : sous-graphe des 50 plus gros transferts\n'
            '(epaisseur = volume, couleur noeud = source/puits)',
            color='white', fontsize=14, pad=15
        )

        # Legende simplifiee
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w',
                       markerfacecolor=PRIMARY, markersize=10, label='Source nette (emetteur)'),
            plt.Line2D([0], [0], marker='o', color='w',
                       markerfacecolor=DANGER, markersize=10, label='Puits net (recepteur)'),
            plt.Line2D([0], [0], color=ACCENT, linewidth=3, label='Fort volume'),
            plt.Line2D([0], [0], color='#475569', linewidth=1, label='Faible volume'),
        ]
        ax.legend(
            handles=legend_elements, loc='upper left',
            fontsize=9, facecolor=BG_DARK, edgecolor='#334155',
            labelcolor='white'
        )

        ax.set_axis_off()
        save_figure(fig, 'rq6_whale_network.png')


def run(df=None, digraph=None, graph=None):
    """Point d'entree RQ6 - Flux ponderes.

    Analyse des flux ponderes et de la concentration: distribution
    des poids, Gini, courbe de Lorenz, whales.

    Parametres:
        df: DataFrame pandas (charge automatiquement si None)
        digraph: nx.DiGraph (charge automatiquement si None)
        graph: nx.Graph non-oriente (charge automatiquement si None)

    Retourne:
        dict avec les metriques de concentration et les donnees whales
    """
    if df is None:
        df, digraph, graph = load_and_build()
    apply_global_style()

    print("\n=== RQ6: Analyse des flux ponderes ===")

    # 1. Extraction et statistiques des poids
    print("\n--- Extraction des poids des aretes ---")
    weight_data = extract_weights(digraph)

    # 2. Coefficient de Gini
    print("\n--- Coefficient de Gini ---")
    gini = compute_gini(weight_data['weights_clean'])

    # 3. Courbe de Lorenz
    print("\n--- Courbe de Lorenz ---")
    lorenz_data = compute_lorenz(weight_data['weights_clean'])

    # 4. Identification des whales
    print("\n--- Top whales (plus gros transferts) ---")
    whales = identify_whales(digraph)

    # 5. Visualisations
    print("\n--- Generation des figures ---")
    plot_weight_distribution(weight_data)
    plot_lorenz_curve(lorenz_data, gini, weight_data)

    # Figure 3 - Graphe reseau des whales (fond sombre)
    plot_whale_network(digraph)

    # 6. Resume console
    print("\n--- Resume RQ6 ---")
    print(f"Aretes totales: {format_number(weight_data['n_total'])}")
    print(f"Aretes apres filtrage poussiere (>{weight_data['threshold']}): {format_number(weight_data['n_clean'])}")
    print(f"Volume total WETH: {weight_data['total_volume']:.4f}")
    print(f"Coefficient de Gini: {gini:.4f}")
    top_pct = sum(w['weight'] for w in whales[:10]) / weight_data['total_volume'] * 100
    print(f"Top-10 whales: {top_pct:.1f}% du volume total")

    print("\n=== RQ6 terminee ===\n")

    return {
        'gini': gini,
        'total_volume': weight_data['total_volume'],
        'n_edges_total': weight_data['n_total'],
        'n_edges_clean': weight_data['n_clean'],
        'n_dust': weight_data['n_dust'],
        'stats': weight_data['stats'],
        'top_whales': whales[:10],
        'top10_volume_pct': top_pct,
    }


if __name__ == "__main__":
    run()
