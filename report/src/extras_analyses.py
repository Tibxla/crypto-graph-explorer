"""Analyses complementaires inspirees du prototype interactif.

Cinq analyses qui prolongent les 6 questions de recherche, en s'appuyant
sur les memes donnees WETH/Polygon du 5 aout 2024:

1. Detection de ponts (Tarjan 1974)
2. Decomposition en k-coeurs (Seidman 1983)
3. Similarite topologique (Jaccard 1901)
4. Propagation epidemique SI (Newman 2002)
5. Robustesse par suppression cascade (Albert et al. 2000)

Produit cinq figures dans figures/extra_*.png.
"""

import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from src.graph_builder import load_and_build, get_largest_component
from src.style import (
    apply_global_style, light_style, dark_style, save_figure,
    format_number, format_address,
    PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER, INFO, PINK,
    BG_DARK, PALETTE, FIGSIZE, SEED
)


# ---------------------------------------------------------------------------
# Analyse 1 : Ponts (bridges)
# ---------------------------------------------------------------------------

def analyse_bridges(graph, lcc):
    """Detecte les ponts du graphe non oriente.

    Un pont est une arete dont la suppression augmente le nombre de
    composantes connexes. Algorithme lineaire de Tarjan en O(V+E).
    """
    print("\n[1] Detection de ponts")
    bridges = list(nx.bridges(lcc))
    n_bridges = len(bridges)
    n_edges = lcc.number_of_edges()
    ratio = 100 * n_bridges / n_edges if n_edges else 0.0

    print(f"  Aretes dans la LCC:      {format_number(n_edges)}")
    print(f"  Ponts detectes:          {format_number(n_bridges)}  ({ratio:.2f} %)")

    # Degre moyen des extremites de ponts
    deg = dict(lcc.degree())
    deg_ends = [deg[u] + deg[v] for u, v in bridges]
    if deg_ends:
        print(f"  Degre moyen des extremites: {np.mean(deg_ends):.2f}")
        print(f"  Mediane:                    {np.median(deg_ends):.2f}")

    # Figure : visualisation d'un sous-graphe contenant des ponts
    # On prend les 80 noeuds les plus connectes et on garde les aretes
    # induites, en surlignant les ponts.
    top = sorted(deg, key=deg.get, reverse=True)[:80]
    sub = lcc.subgraph(top).copy()
    sub_bridges = [e for e in nx.bridges(sub)] if sub.number_of_edges() else []

    with dark_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)
        random.seed(SEED)
        pos = nx.spring_layout(sub, seed=SEED, k=0.4)
        nx.draw_networkx_nodes(sub, pos, ax=ax, node_size=60,
                               node_color=PRIMARY, alpha=0.85,
                               edgecolors='white', linewidths=0.5)
        non_bridge = [e for e in sub.edges() if e not in sub_bridges
                      and (e[1], e[0]) not in sub_bridges]
        nx.draw_networkx_edges(sub, pos, edgelist=non_bridge, ax=ax,
                               edge_color='#94a3b8', alpha=0.5, width=0.6)
        nx.draw_networkx_edges(sub, pos, edgelist=sub_bridges, ax=ax,
                               edge_color=DANGER, alpha=0.9, width=2.2)
        ax.set_title(f"Sous-graphe des 80 noeuds les plus connectes\n"
                     f"Ponts surlignes en rouge ({len(sub_bridges)} sur "
                     f"{sub.number_of_edges()} aretes)",
                     color='white', fontsize=13)
        ax.axis('off')
        save_figure(fig, "extra_bridges_network.png")

    return {
        'n_bridges': n_bridges,
        'n_edges': n_edges,
        'ratio_pct': ratio,
    }


# ---------------------------------------------------------------------------
# Analyse 2 : Decomposition en k-coeurs
# ---------------------------------------------------------------------------

def analyse_kcore(graph, lcc):
    """Calcule la decomposition en k-coeurs.

    Le k-coeur est le sous-graphe maximal ou chaque sommet a au moins k
    voisins dans le sous-graphe (Seidman 1983). La coreness d'un noeud
    est le plus grand k tel qu'il appartient au k-coeur.
    """
    print("\n[2] Decomposition en k-coeurs")
    # core_number n'accepte pas les self-loops
    lcc_no_loops = lcc.copy()
    lcc_no_loops.remove_edges_from(nx.selfloop_edges(lcc_no_loops))
    coreness = nx.core_number(lcc_no_loops)
    max_k = max(coreness.values())
    distrib = np.zeros(max_k + 1, dtype=int)
    for v in coreness.values():
        distrib[v] += 1

    print(f"  Coreness maximale (k_max): {max_k}")
    print(f"  Noeuds dans le k_max-coeur: "
          f"{sum(1 for v in coreness.values() if v == max_k)}")
    print(f"  Noeuds dans le 2-coeur:    "
          f"{sum(1 for v in coreness.values() if v >= 2)} "
          f"({100*sum(1 for v in coreness.values() if v >= 2)/len(coreness):.1f} %)")

    apply_global_style()
    with light_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)
        ax.bar(range(max_k + 1), distrib, color=PRIMARY, alpha=0.85,
               edgecolor=SECONDARY, linewidth=0.5)
        ax.set_yscale('log')
        ax.set_xlabel("Coreness (k)")
        ax.set_ylabel("Nombre de noeuds (echelle log)")
        ax.set_title(f"Distribution des k-coeurs du reseau WETH "
                     f"(k_max = {max_k})")
        for k, n in enumerate(distrib):
            if n > 0:
                ax.text(k, n, format_number(n), ha='center', va='bottom',
                        fontsize=9)
        save_figure(fig, "extra_kcore_distribution.png")

    return {
        'max_k': max_k,
        'distribution': distrib.tolist(),
        'core_2_size': int(sum(1 for v in coreness.values() if v >= 2)),
    }


# ---------------------------------------------------------------------------
# Analyse 3 : Similarite topologique (Jaccard)
# ---------------------------------------------------------------------------

def analyse_jaccard(graph, lcc):
    """Calcule le coefficient de Jaccard entre les top hubs.

    J(u, v) = |N(u) ∩ N(v)| / |N(u) ∪ N(v)| (Jaccard 1901). Mesure le
    chevauchement des voisinages : pour deux hubs, une valeur elevee
    signifie qu'ils partagent une part importante de leurs contreparties.
    """
    print("\n[3] Similarite topologique (Jaccard) sur les top 50 hubs")
    deg = dict(lcc.degree())
    top = sorted(deg, key=deg.get, reverse=True)[:50]
    sims = []
    for i, u in enumerate(top):
        nu = set(lcc.neighbors(u))
        for v in top[i+1:]:
            nv = set(lcc.neighbors(v))
            union = nu | nv
            if not union:
                continue
            j = len(nu & nv) / len(union)
            sims.append((u, v, j, len(nu & nv)))

    sims.sort(key=lambda x: x[2], reverse=True)
    top10 = sims[:10]
    print("  Top 10 paires par Jaccard:")
    for u, v, j, k in top10:
        print(f"    {format_address(u)} / {format_address(v)}  "
              f"J = {j:.4f}  voisins communs = {k}")

    # Histogramme des valeurs de Jaccard non nulles
    all_j = [s[2] for s in sims if s[2] > 0]
    print(f"  Paires non triviales (J > 0): {len(all_j)} / {len(sims)}")
    if all_j:
        print(f"  Mediane des J non nuls:       {np.median(all_j):.4f}")
        print(f"  Maximum:                       {max(all_j):.4f}")

    apply_global_style()
    with light_style():
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Sous-figure gauche : distribution
        if all_j:
            axes[0].hist(all_j, bins=30, color=SECONDARY, alpha=0.8,
                         edgecolor='white')
            axes[0].axvline(np.median(all_j), color=DANGER, linestyle='--',
                            label=f"mediane = {np.median(all_j):.3f}")
            axes[0].set_xlabel("Coefficient de Jaccard")
            axes[0].set_ylabel("Nombre de paires")
            axes[0].set_title("Distribution des paires non triviales (J > 0)")
            axes[0].legend()

        # Sous-figure droite : top 10
        labels = [f"{format_address(u, 4)}\n{format_address(v, 4)}"
                  for u, v, _, _ in top10]
        values = [s[2] for s in top10]
        axes[1].barh(range(len(top10)), values, color=ACCENT, alpha=0.85)
        axes[1].set_yticks(range(len(top10)))
        axes[1].set_yticklabels(labels, fontsize=8)
        axes[1].invert_yaxis()
        axes[1].set_xlabel("Coefficient de Jaccard")
        axes[1].set_title("Top 10 paires de hubs les plus similaires")
        save_figure(fig, "extra_jaccard_topk.png")

    return {
        'top10': [(u, v, float(j), int(k)) for u, v, j, k in top10],
        'median_nonzero': float(np.median(all_j)) if all_j else 0.0,
        'max_jaccard': float(max(all_j)) if all_j else 0.0,
    }


# ---------------------------------------------------------------------------
# Analyse 4 : Propagation epidemique SI
# ---------------------------------------------------------------------------

def analyse_si(graph, lcc, n_runs=20, max_steps=15):
    """Simule un modele Susceptible-Infected sur la LCC.

    A chaque pas, un noeud infecte transmet a chacun de ses voisins
    sains avec probabilite p. On moyenne sur n_runs realisations.
    Source = noeud de plus grand degre.
    """
    print("\n[4] Propagation SI depuis le hub principal")
    deg = dict(lcc.degree())
    seed_node = max(deg, key=deg.get)
    print(f"  Source: {format_address(seed_node)}  (degre = {deg[seed_node]})")

    nodes_list = list(lcc.nodes())
    probas = [0.10, 0.30, 0.50]
    curves = {p: np.zeros(max_steps + 1) for p in probas}

    rng = random.Random(SEED)
    for p in probas:
        for run in range(n_runs):
            rng_run = random.Random(SEED + run)
            infected = {seed_node}
            for step in range(max_steps + 1):
                curves[p][step] += len(infected)
                if step == max_steps:
                    break
                new_inf = set()
                for u in infected:
                    for v in lcc.neighbors(u):
                        if v in infected or v in new_inf:
                            continue
                        if rng_run.random() < p:
                            new_inf.add(v)
                if not new_inf:
                    # Plateau : on remplit les pas restants avec la valeur courante
                    for s in range(step + 1, max_steps + 1):
                        curves[p][s] += len(infected)
                    break
                infected |= new_inf
        curves[p] /= n_runs

    for p in probas:
        final = curves[p][-1]
        ratio = 100 * final / len(nodes_list)
        print(f"  p = {p:.2f}: portee finale = {final:.0f} noeuds "
              f"({ratio:.1f} % de la LCC) apres {max_steps} pas")

    apply_global_style()
    with light_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)
        colors = [PRIMARY, SECONDARY, DANGER]
        for color, p in zip(colors, probas):
            ax.plot(range(max_steps + 1), curves[p], '-o',
                    color=color, linewidth=2, markersize=5,
                    label=f"p = {p:.2f}")
        ax.set_xlabel("Etape de simulation")
        ax.set_ylabel("Noeuds atteints (moyenne sur 20 runs)")
        ax.set_title("Propagation SI depuis le hub principal\n"
                     f"LCC de {format_number(lcc.number_of_nodes())} noeuds")
        ax.legend(title="Probabilite de transmission")
        ax.grid(True, alpha=0.3)
        save_figure(fig, "extra_si_propagation.png")

    return {
        'seed': seed_node,
        'final_reach': {f"p={p}": float(curves[p][-1]) for p in probas},
    }


# ---------------------------------------------------------------------------
# Analyse 5 : Robustesse par suppression cascade
# ---------------------------------------------------------------------------

def analyse_robustness(graph, lcc, n_remove=100):
    """Mesure l'effet d'une suppression cascade de noeuds.

    Compare trois strategies de retrait :
    - aleatoire (baseline) ;
    - par degre decroissant (attaque ciblee Albert et al. 2000) ;
    - par betweenness decroissante (attaque structurelle).

    On suit la taille relative de la plus grande composante connexe.
    """
    print("\n[5] Robustesse par suppression cascade")
    n0 = lcc.number_of_nodes()
    deg = dict(lcc.degree())

    # Ordre par degre decroissant
    by_deg = sorted(deg, key=deg.get, reverse=True)[:n_remove]

    # Betweenness sur un echantillon (cout reduit, suffisant pour ordonner)
    print("  Calcul de la betweenness echantillonnee (k=500)...")
    bc = nx.betweenness_centrality(lcc, k=500, seed=SEED)
    by_bc = sorted(bc, key=bc.get, reverse=True)[:n_remove]

    # Ordre aleatoire
    rng = random.Random(SEED)
    by_rand = rng.sample(list(lcc.nodes()), n_remove)

    def lcc_curve(order):
        G = lcc.copy()
        sizes = [n0]
        for v in order:
            if G.has_node(v):
                G.remove_node(v)
            if G.number_of_nodes() == 0:
                sizes.append(0)
                continue
            largest = max(nx.connected_components(G), key=len)
            sizes.append(len(largest))
        return sizes

    print("  Simulation des trois cascades...")
    curve_rand = lcc_curve(by_rand)
    curve_deg = lcc_curve(by_deg)
    curve_bc = lcc_curve(by_bc)

    drop_deg = 100 * (n0 - curve_deg[-1]) / n0
    drop_bc = 100 * (n0 - curve_bc[-1]) / n0
    drop_rand = 100 * (n0 - curve_rand[-1]) / n0
    print(f"  Apres retrait de {n_remove} noeuds:")
    print(f"    Aleatoire : LCC perd {drop_rand:.2f} %")
    print(f"    Degre     : LCC perd {drop_deg:.2f} %")
    print(f"    Betweenness: LCC perd {drop_bc:.2f} %")

    apply_global_style()
    with light_style():
        fig, ax = plt.subplots(figsize=FIGSIZE)
        x = range(n_remove + 1)
        ax.plot(x, [100*s/n0 for s in curve_rand], '-', color=INFO,
                linewidth=2, label="Aleatoire (baseline)")
        ax.plot(x, [100*s/n0 for s in curve_deg], '-', color=DANGER,
                linewidth=2, label="Top degre")
        ax.plot(x, [100*s/n0 for s in curve_bc], '-', color=SECONDARY,
                linewidth=2, label="Top betweenness")
        ax.set_xlabel("Noeuds retires")
        ax.set_ylabel("Taille relative de la LCC (%)")
        ax.set_title("Robustesse du reseau WETH face a une suppression cascade")
        ax.legend()
        ax.grid(True, alpha=0.3)
        save_figure(fig, "extra_robustness_cascade.png")

    return {
        'n_removed': n_remove,
        'drop_random_pct': drop_rand,
        'drop_degree_pct': drop_deg,
        'drop_betweenness_pct': drop_bc,
    }


# ---------------------------------------------------------------------------
# Point d'entree
# ---------------------------------------------------------------------------

def run(df=None, digraph=None, graph=None):
    """Lance les cinq analyses complementaires.

    Signature compatible avec l'orchestrateur run_all.py : si les graphes
    sont fournis, ils sont reutilises ; sinon ils sont construits depuis
    le CSV.
    """
    apply_global_style()

    if graph is None:
        df, digraph, graph = load_and_build()

    lcc = get_largest_component(graph)
    print(f"LCC: {format_number(lcc.number_of_nodes())} noeuds, "
          f"{format_number(lcc.number_of_edges())} aretes")

    res = {}
    res['bridges'] = analyse_bridges(graph, lcc)
    res['kcore'] = analyse_kcore(graph, lcc)
    res['jaccard'] = analyse_jaccard(graph, lcc)
    res['si'] = analyse_si(graph, lcc)
    res['robustness'] = analyse_robustness(graph, lcc)

    print("\nResume:")
    print(f"  Ponts        : {res['bridges']['n_bridges']} "
          f"({res['bridges']['ratio_pct']:.2f} %)")
    print(f"  k_max (kcore): {res['kcore']['max_k']}")
    print(f"  Jaccard max  : {res['jaccard']['max_jaccard']:.4f}")
    print(f"  Cascade deg  : {res['robustness']['drop_degree_pct']:.2f} % de LCC perdue")
    print(f"  Cascade rand : {res['robustness']['drop_random_pct']:.2f} % de LCC perdue")
    return res


def main():
    """Point d'entree autonome (relance le chargement CSV)."""
    print("=" * 60)
    print("Analyses complementaires - rapport WETH Polygon 2024")
    print("=" * 60)
    return run()


if __name__ == "__main__":
    main()
