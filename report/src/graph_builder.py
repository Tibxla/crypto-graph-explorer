"""Graph builder module: CSV loading and NetworkX graph construction."""

import pandas as pd
import networkx as nx

_CSV_PATH = "polygon_weth_crash_2024-08-05.csv"


def load_dataframe(csv_path=_CSV_PATH):
    """Charge le CSV et retourne un DataFrame pandas.

    Ajoute une colonne 'datetime' convertie depuis le timestamp unix 'chrono'.

    Retourne:
        pd.DataFrame avec les colonnes originales + 'datetime'.
    """
    df = pd.read_csv(csv_path)
    df['datetime'] = pd.to_datetime(df['chrono'], unit='s')
    return df


def build_digraph(df):
    """Construit un DiGraph pondere avec agregation des aretes multiples.

    Pour chaque paire (source, target), les transactions sont agregees:
    - weight: somme des montants WETH
    - tx_count: nombre de transactions

    Retourne:
        nx.DiGraph avec attributs 'weight' et 'tx_count' sur chaque arete.
    """
    G = nx.DiGraph()
    for (src, tgt), group in df.groupby(['source', 'target']):
        total_weight = group['weight'].sum()
        tx_count = len(group)
        G.add_edge(src, tgt, weight=total_weight, tx_count=tx_count)
    return G


def get_largest_component(G):
    """Retourne le sous-graphe de la plus grande composante connexe.

    Utilise les composantes faiblement connexes pour les graphes orientes,
    et les composantes connexes pour les graphes non-orientes.

    Retourne:
        nx.Graph ou nx.DiGraph (copie du sous-graphe).
    """
    if G.is_directed():
        largest = max(nx.weakly_connected_components(G), key=len)
    else:
        largest = max(nx.connected_components(G), key=len)
    return G.subgraph(largest).copy()


def load_and_build(csv_path=_CSV_PATH):
    """Point d'entree principal: charge le CSV et construit les graphes.

    Charge le DataFrame, construit le DiGraph pondere, puis cree
    une version non-orientee.

    Retourne:
        tuple (pd.DataFrame, nx.DiGraph, nx.Graph).
    """
    print("Chargement du CSV...")
    df = load_dataframe(csv_path)

    print("Construction du DiGraph...")
    digraph = build_digraph(df)
    print(f"Graphe construit: {digraph.number_of_nodes()} noeuds, {digraph.number_of_edges()} aretes")

    graph = digraph.to_undirected()
    print(f"Version non-orientee: {graph.number_of_edges()} aretes")

    return df, digraph, graph
