"""RQ5: Analyse des proprietes petit-monde du reseau.

Evalue si le reseau WETH Polygon presente les proprietes petit-monde
(small-world) decrites par Watts et Strogatz (1998):
- Coefficient de clustering eleve par rapport a un graphe aleatoire
- Longueur moyenne des chemins comparable a un graphe aleatoire
- Quotient sigma = (C/C_rand) / (L/L_rand) >> 1

Calcul sur le graphe non-oriente, comparaison avec 10 graphes
Erdos-Renyi de memes parametres (n, p).

Produit 2 figures:
- figures/rq5_small_world_comparison.png : Comparaison C et L observe vs aleatoire
- figures/rq5_clustering_distribution.png : Distribution des coefficients de clustering par noeud
"""

import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from src.graph_builder import load_and_build, get_largest_component
from src.style import (
    apply_global_style, light_style, dark_style, save_figure,
    format_number,
    PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER,
    BG_DARK, PALETTE, FIGSIZE, SEED
)
import matplotlib.colors as mcolors

# Constantes de l'analyse
N_RANDOM_GRAPHS = 10    # Nombre de graphes ER pour la comparaison
N_PATH_SAMPLES = 1000   # Nombre de paires aleatoires pour estimer L


def compute_clustering(graph):
    """Calcule les coefficients de clustering sur le graphe non-oriente.

    Mesure la tendance des noeuds a former des triangles:
    - Transitivite globale: ratio triangles / triplets (metrique globale)
    - Clustering moyen: moyenne des coefficients locaux par noeud
    - Coefficients par noeud: dictionnaire {noeud: coefficient}

    Parametres:
        graph: nx.Graph non-oriente

    Retourne:
        dict avec 'transitivity', 'average_clustering', 'per_node_clustering'
    """
    # Transitivite globale (ratio de triangles fermes)
    C_trans = nx.transitivity(graph)

    # Clustering moyen (moyenne des coefficients locaux)
    C_avg = nx.average_clustering(graph)

    # Coefficients par noeud (pour la distribution)
    clustering_dict = nx.clustering(graph)

    print(f"  Transitivite globale:          {C_trans:.6f}")
    print(f"  Clustering moyen (par noeud):  {C_avg:.6f}")
    print(f"  Noeuds avec clustering = 0:    {sum(1 for v in clustering_dict.values() if v == 0)}")
    print(f"  Noeuds avec clustering > 0:    {sum(1 for v in clustering_dict.values() if v > 0)}")

    return {
        'transitivity': C_trans,
        'average_clustering': C_avg,
        'per_node_clustering': clustering_dict,
    }


def estimate_path_length(graph, n_samples=N_PATH_SAMPLES):
    """Estime la longueur moyenne des chemins par echantillonnage.

    Travaille sur la plus grande composante connexe (LCC) pour eviter
    les erreurs de graphe non-connexe. Echantillonne n_samples paires
    aleatoires et calcule le plus court chemin entre chaque paire.

    Parametres:
        graph: nx.Graph non-oriente
        n_samples: nombre de paires a echantillonner (defaut: 1000)

    Retourne:
        dict avec 'L_actual', 'lcc_nodes', 'lcc_edges', 'n_samples_used', 'path_lengths'
    """
    # Extraire la plus grande composante connexe (Pitfall P2)
    lcc = get_largest_component(graph)
    lcc_n = lcc.number_of_nodes()
    lcc_e = lcc.number_of_edges()
    print(f"  Plus grande composante connexe: {format_number(lcc_n)} noeuds, {format_number(lcc_e)} aretes")

    # Echantillonnage de paires aleatoires
    random.seed(SEED)
    nodes = list(lcc.nodes())
    pairs = []
    while len(pairs) < n_samples:
        u, v = random.sample(nodes, 2)
        pairs.append((u, v))

    # Calcul des plus courts chemins
    lengths = []
    for u, v in pairs:
        try:
            length = nx.shortest_path_length(lcc, u, v)
            lengths.append(length)
        except nx.NetworkXNoPath:
            pass  # Ne devrait pas arriver dans une composante connexe

    L_actual = np.mean(lengths)

    print(f"  Paires echantillonnees:        {len(pairs)}")
    print(f"  Chemins trouves:               {len(lengths)}")
    print(f"  Longueur moyenne (L):          {L_actual:.4f}")
    print(f"  Longueur min / max:            {min(lengths)} / {max(lengths)}")
    print(f"  Ecart-type:                    {np.std(lengths):.4f}")

    return {
        'L_actual': L_actual,
        'lcc_nodes': lcc_n,
        'lcc_edges': lcc_e,
        'n_samples_used': len(lengths),
        'path_lengths': lengths,
    }


def generate_er_comparison(graph, n_random=N_RANDOM_GRAPHS):
    """Genere des graphes Erdos-Renyi de reference et calcule leurs metriques.

    Cree n_random graphes aleatoires avec les memes parametres (n, p)
    que le graphe observe. Pour chaque graphe ER, calcule la transitivite
    et estime la longueur moyenne des chemins sur sa plus grande CC.

    Parametres:
        graph: nx.Graph non-oriente (graphe observe)
        n_random: nombre de graphes ER a generer (defaut: 10)

    Retourne:
        dict avec 'C_rand', 'L_rand', 'n', 'p', 'er_results', 'C_rand_std', 'L_rand_std'
    """
    # Parametres du graphe observe (Pitfall P8)
    n = graph.number_of_nodes()
    p = nx.density(graph)

    print(f"  Parametres ER: n={format_number(n)}, p={p:.6f}")
    print(f"  Generation de {n_random} graphes Erdos-Renyi...")

    er_results = []
    for i in range(n_random):
        # Generer le graphe ER (seed deterministe)
        G_er = nx.erdos_renyi_graph(n, p, seed=SEED + i, directed=False)

        # Transitivite du graphe ER (Pitfall P9: meme metrique que l'observe)
        C_er = nx.transitivity(G_er)

        # Longueur des chemins sur la plus grande CC du graphe ER
        lcc_er = get_largest_component(G_er)

        # Echantillonner les chemins sur la CC du graphe ER
        random.seed(SEED + i)
        er_nodes = list(lcc_er.nodes())
        max_pairs = min(N_PATH_SAMPLES, len(er_nodes) * (len(er_nodes) - 1) // 2)
        er_pairs = [random.sample(er_nodes, 2) for _ in range(max_pairs)]

        er_lengths = []
        for u, v in er_pairs:
            try:
                er_lengths.append(nx.shortest_path_length(lcc_er, u, v))
            except nx.NetworkXNoPath:
                pass

        L_er = np.mean(er_lengths) if er_lengths else float('inf')

        er_results.append({
            'C_rand': C_er,
            'L_rand': L_er,
            'lcc_size': lcc_er.number_of_nodes(),
            'n_edges': G_er.number_of_edges(),
        })

        print(f"  ER graph {i+1}/{n_random}: C={C_er:.6f}, L={L_er:.4f}, LCC={format_number(lcc_er.number_of_nodes())}")

    # Moyennes et ecarts-types sur tous les graphes ER
    C_rand = np.mean([r['C_rand'] for r in er_results])
    L_rand = np.mean([r['L_rand'] for r in er_results])
    C_rand_std = np.std([r['C_rand'] for r in er_results])
    L_rand_std = np.std([r['L_rand'] for r in er_results])

    print(f"\n  Moyennes ER ({n_random} graphes):")
    print(f"    C_rand = {C_rand:.6f} (+/- {C_rand_std:.6f})")
    print(f"    L_rand = {L_rand:.4f} (+/- {L_rand_std:.4f})")

    return {
        'C_rand': C_rand,
        'L_rand': L_rand,
        'n': n,
        'p': p,
        'er_results': er_results,
        'C_rand_std': C_rand_std,
        'L_rand_std': L_rand_std,
    }


def compute_sigma(C_actual, C_rand, L_actual, L_rand):
    """Calcule le quotient sigma de petit-monde (Watts-Strogatz 1998).

    sigma = (C_actual / C_rand) / (L_actual / L_rand)

    Un sigma >> 1 indique des proprietes petit-monde:
    clustering eleve par rapport au hasard ET chemins courts comparables.

    IMPORTANT: NE PAS utiliser nx.sigma() (Pitfall P5).

    Parametres:
        C_actual: transitivite du graphe observe
        C_rand: transitivite moyenne des graphes ER
        L_actual: longueur moyenne des chemins du graphe observe
        L_rand: longueur moyenne des chemins des graphes ER

    Retourne:
        float: quotient sigma
    """
    # Calcul MANUEL du sigma (Pitfall P5: ne JAMAIS utiliser nx.sigma())
    sigma = (C_actual / C_rand) / (L_actual / L_rand)

    print(f"  Sigma = (C/C_rand) / (L/L_rand)")
    print(f"        = ({C_actual:.6f} / {C_rand:.6f}) / ({L_actual:.4f} / {L_rand:.4f})")
    print(f"        = {C_actual/C_rand:.4f} / {L_actual/L_rand:.4f}")
    print(f"        = {sigma:.4f}")

    if sigma > 5:
        print(f"  -> sigma = {sigma:.2f} >> 1 : proprietes petit-monde FORTES")
    elif sigma > 1:
        print(f"  -> sigma = {sigma:.2f} > 1 : proprietes petit-monde presentes")
    else:
        print(f"  -> sigma = {sigma:.2f} ~ 1 : pas de proprietes petit-monde")

    return sigma


def plot_comparison(clustering_data, path_data, er_data, sigma):
    """Trace le diagramme comparatif observe vs Erdos-Renyi.

    Figure avec 2 sous-graphiques cote a cote:
    - Gauche: comparaison des coefficients de clustering (transitivite)
    - Droite: comparaison des longueurs moyennes des chemins

    Barres avec barres d'erreur (ecart-type) pour les valeurs ER.
    Fond clair (graphique analytique).

    Parametres:
        clustering_data: dict retourne par compute_clustering()
        path_data: dict retourne par estimate_path_length()
        er_data: dict retourne par generate_er_comparison()
        sigma: float retourne par compute_sigma()
    """
    with light_style():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        labels = ['Reseau\nobserve', 'Erdos-Renyi\n(moy.)']
        x = np.arange(len(labels))
        width = 0.5

        # --- Gauche: Coefficient de clustering (transitivite) ---
        C_obs = clustering_data['transitivity']
        C_rand = er_data['C_rand']
        C_rand_std = er_data['C_rand_std']

        bars1 = ax1.bar(x, [C_obs, C_rand], width,
                        color=[PRIMARY, SECONDARY], alpha=0.85,
                        edgecolor='white', linewidth=0.5)
        # Barre d'erreur sur ER uniquement
        ax1.errorbar(x[1], C_rand, yerr=C_rand_std,
                     fmt='none', ecolor='black', capsize=8, capthick=1.5, linewidth=1.5)

        # Valeurs au-dessus des barres
        for bar, val in zip(bars1, [C_obs, C_rand]):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                     f'{val:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Annotation du ratio
        ratio_C = C_obs / C_rand if C_rand > 0 else float('inf')
        ax1.annotate(f'Ratio: {ratio_C:.1f}x',
                     xy=(0.5, 0.92), xycoords='axes fraction',
                     fontsize=12, ha='center', fontweight='bold',
                     color=DANGER,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEE2E2',
                               edgecolor=DANGER, alpha=0.9))

        ax1.set_ylabel('Coefficient de clustering (transitivite)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels)
        ax1.set_title('Clustering')

        # --- Droite: Longueur moyenne des chemins ---
        L_obs = path_data['L_actual']
        L_rand = er_data['L_rand']
        L_rand_std = er_data['L_rand_std']

        bars2 = ax2.bar(x, [L_obs, L_rand], width,
                        color=[PRIMARY, SECONDARY], alpha=0.85,
                        edgecolor='white', linewidth=0.5)
        # Barre d'erreur sur ER uniquement
        ax2.errorbar(x[1], L_rand, yerr=L_rand_std,
                     fmt='none', ecolor='black', capsize=8, capthick=1.5, linewidth=1.5)

        # Valeurs au-dessus des barres
        for bar, val in zip(bars2, [L_obs, L_rand]):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                     f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Annotation du ratio
        ratio_L = L_obs / L_rand if L_rand > 0 else float('inf')
        ax2.annotate(f'Ratio: {ratio_L:.2f}x',
                     xy=(0.5, 0.92), xycoords='axes fraction',
                     fontsize=12, ha='center', fontweight='bold',
                     color=SUCCESS,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='#D1FAE5',
                               edgecolor=SUCCESS, alpha=0.9))

        ax2.set_ylabel('Longueur moyenne des chemins')
        ax2.set_xticks(x)
        ax2.set_xticklabels(labels)
        ax2.set_title('Longueur des chemins')

        # Titre global avec sigma
        fig.suptitle(f'Comparaison petit-monde : sigma = {sigma:.2f}',
                     fontsize=14, fontweight='bold')

        save_figure(fig, 'rq5_small_world_comparison.png')


def plot_clustering_distribution(clustering_data):
    """Trace l'histogramme de la distribution des coefficients de clustering par noeud.

    Montre la distribution des coefficients de clustering locaux avec
    des lignes verticales pour la transitivite globale et le clustering
    moyen. Fond clair (graphique analytique).

    Parametres:
        clustering_data: dict retourne par compute_clustering()
    """
    values = list(clustering_data['per_node_clustering'].values())

    with light_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)

        # Histogramme des coefficients de clustering par noeud
        ax.hist(values, bins=50, color=PRIMARY, edgecolor='white', alpha=0.8)

        # Lignes verticales pour les metriques globales
        ax.axvline(clustering_data['transitivity'], color=DANGER, linestyle='--', linewidth=2,
                   label=f"Transitivite globale = {clustering_data['transitivity']:.4f}")
        ax.axvline(clustering_data['average_clustering'], color=ACCENT, linestyle='--', linewidth=2,
                   label=f"Clustering moyen = {clustering_data['average_clustering']:.4f}")

        ax.set_title('Distribution des coefficients de clustering par noeud')
        ax.set_xlabel('Coefficient de clustering local')
        ax.set_ylabel('Nombre de noeuds')
        ax.legend(fontsize=10)

        # Annotation avec statistiques
        n_zero = sum(1 for v in values if v == 0)
        n_one = sum(1 for v in values if v == 1.0)
        annotation_text = (
            f"Noeuds: {format_number(len(values))}\n"
            f"Clustering = 0: {format_number(n_zero)} ({n_zero/len(values)*100:.1f}%)\n"
            f"Clustering = 1: {format_number(n_one)} ({n_one/len(values)*100:.1f}%)"
        )
        ax.annotate(
            annotation_text,
            xy=(0.97, 0.97), xycoords='axes fraction',
            fontsize=9, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor='#CBD5E1', alpha=0.9)
        )

        save_figure(fig, 'rq5_clustering_distribution.png')


def plot_clustering_network(graph, clustering_data):
    """Trace le sous-graphe colore par coefficient de clustering (fond sombre).

    Echantillonne ~500 noeuds de la plus grande composante connexe.
    Les noeuds sont colores par coefficient de clustering local
    (bleu = faible, rouge = eleve) et dimensionnes par degre.

    Parametres:
        graph: nx.Graph non-oriente
        clustering_data: dict retourne par compute_clustering()
    """
    # Plus grande composante connexe
    lcc = get_largest_component(graph)

    # Echantillonner ~500 noeuds en privilegiant les noeuds avec clustering > 0
    random.seed(SEED)
    all_nodes = list(lcc.nodes())
    clustering_dict = clustering_data['per_node_clustering']

    # Separer noeuds avec clustering > 0 et = 0
    high_c = [n for n in all_nodes if clustering_dict.get(n, 0) > 0]
    low_c = [n for n in all_nodes if clustering_dict.get(n, 0) == 0]

    # Prendre max 300 noeuds high-C + max 200 noeuds low-C (par degre)
    random.shuffle(high_c)
    random.shuffle(low_c)
    sample_nodes = high_c[:300] + low_c[:200]

    sub = lcc.subgraph(sample_nodes).copy()
    # Retirer les noeuds isoles dans le sous-graphe
    isolates = list(nx.isolates(sub))
    sub.remove_nodes_from(isolates)

    print(f"\n  Sous-graphe clustering: {sub.number_of_nodes()} noeuds, {sub.number_of_edges()} aretes")

    # Layout
    pos = nx.spring_layout(sub, seed=SEED, k=2.0 / np.sqrt(max(sub.number_of_nodes(), 1)))

    # Tailles par degre
    degrees = dict(sub.degree())
    deg_vals = list(degrees.values())
    min_d, max_d = min(deg_vals) if deg_vals else 0, max(deg_vals) if deg_vals else 1
    node_sizes = [15 + 185 * (degrees[n] - min_d) / (max_d - min_d + 1) for n in sub.nodes()]

    # Couleurs par clustering coefficient (bleu froid -> rouge chaud)
    c_vals = np.array([clustering_dict.get(n, 0) for n in sub.nodes()])
    cmap = mcolors.LinearSegmentedColormap.from_list('clust_cmap', [PRIMARY, ACCENT, DANGER])

    with dark_style():
        fig, ax = plt.subplots(figsize=(14, 10))

        nx.draw_networkx_edges(
            sub, pos, ax=ax,
            edge_color='#334155', alpha=0.12, width=0.3, style='solid'
        )

        nodes = nx.draw_networkx_nodes(
            sub, pos, ax=ax,
            node_color=c_vals, cmap=cmap, vmin=0, vmax=1,
            node_size=node_sizes, alpha=0.85, edgecolors='none'
        )

        ax.set_title(
            'Structure petit-monde du reseau WETH\n'
            '(couleur = coefficient de clustering local)',
            color='white', fontsize=14, pad=15
        )

        # Barre de couleurs
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
        cbar.set_label('Coefficient de clustering', color='white', fontsize=10)
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

        ax.set_axis_off()
        save_figure(fig, 'rq5_clustering_network.png')


def run(df=None, digraph=None, graph=None):
    """Point d'entree RQ5 - Petit-monde.

    Analyse des proprietes petit-monde du reseau WETH Polygon:
    clustering, longueur des chemins, comparaison Erdos-Renyi,
    et quotient sigma (Watts-Strogatz 1998).

    Parametres:
        df: DataFrame pandas (charge automatiquement si None)
        digraph: nx.DiGraph (charge automatiquement si None)
        graph: nx.Graph non-oriente (charge automatiquement si None)

    Retourne:
        dict avec les metriques petit-monde
    """
    if df is None:
        df, digraph, graph = load_and_build()
    apply_global_style()

    print("\n=== RQ5: Analyse des proprietes petit-monde ===")

    # 1. Clustering sur graphe non-oriente
    print("\n--- Coefficients de clustering ---")
    clustering_data = compute_clustering(graph)

    # 2. Longueur des chemins (echantillonnage sur plus grande CC)
    print("\n--- Longueur moyenne des chemins (echantillonnage) ---")
    path_data = estimate_path_length(graph)

    # 3. Comparaison Erdos-Renyi
    print("\n--- Generation de graphes Erdos-Renyi ---")
    er_data = generate_er_comparison(graph)

    # 4. Calcul du sigma (MANUAL -- NOT nx.sigma)
    print("\n--- Quotient sigma ---")
    sigma = compute_sigma(
        clustering_data['transitivity'],
        er_data['C_rand'],
        path_data['L_actual'],
        er_data['L_rand']
    )

    # 5. Visualisations
    print("\n--- Generation des figures ---")
    plot_comparison(clustering_data, path_data, er_data, sigma)
    plot_clustering_distribution(clustering_data)

    # Figure 3 - Graphe reseau colore par clustering (fond sombre)
    plot_clustering_network(graph, clustering_data)

    # 6. Tableau comparatif console
    print("\n--- Tableau comparatif ---")
    print(f"{'Metrique':<35} {'Observe':>12} {'ER (moy.)':>12} {'Ratio':>10}")
    print("-" * 72)
    print(f"{'Transitivite (C)':<35} {clustering_data['transitivity']:>12.6f} {er_data['C_rand']:>12.6f} {clustering_data['transitivity']/er_data['C_rand']:>10.2f}")
    print(f"{'Clustering moyen':<35} {clustering_data['average_clustering']:>12.6f} {'--':>12} {'--':>10}")
    print(f"{'Longueur moy. chemins (L)':<35} {path_data['L_actual']:>12.4f} {er_data['L_rand']:>12.4f} {path_data['L_actual']/er_data['L_rand']:>10.2f}")
    print(f"{'Sigma = (C/Cr)/(L/Lr)':<35} {sigma:>12.2f}")
    print(f"\nConclusion: sigma = {sigma:.2f} {'>> 1 : proprietes petit-monde CONFIRMEES' if sigma > 1 else '~ 1 : pas de proprietes petit-monde'}")

    print("\n=== RQ5 terminee ===\n")

    return {
        'transitivity': clustering_data['transitivity'],
        'average_clustering': clustering_data['average_clustering'],
        'L_actual': path_data['L_actual'],
        'lcc_nodes': path_data['lcc_nodes'],
        'C_rand': er_data['C_rand'],
        'L_rand': er_data['L_rand'],
        'sigma': sigma,
        'n': graph.number_of_nodes(),
        'p': nx.density(graph),
        'n_random_graphs': N_RANDOM_GRAPHS,
    }


if __name__ == "__main__":
    run()
