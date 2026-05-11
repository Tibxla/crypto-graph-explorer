"""Orchestrateur: execute les 6 analyses de questions de recherche et les analyses complementaires."""
import time
from src.graph_builder import load_and_build
from src import rq1_topologie, rq2_centralite, rq3_communautes
from src import rq4_temporel, rq5_petitmonde, rq6_flux_ponderes
from src import extras_analyses


def main():
    """Execute toutes les analyses sequentiellement."""
    debut = time.time()

    print("=" * 60)
    print("  Analyse du reseau WETH Polygon - Lundi Noir (5 aout 2024)")
    print("=" * 60)

    print("\nChargement des donnees...")
    df, digraph, graph = load_and_build()

    modules = [
        ("RQ1 - Topologie", rq1_topologie),
        ("RQ2 - Centralite", rq2_centralite),
        ("RQ3 - Communautes", rq3_communautes),
        ("RQ4 - Temporel", rq4_temporel),
        ("RQ5 - Petit-monde", rq5_petitmonde),
        ("RQ6 - Flux ponderes", rq6_flux_ponderes),
        ("Analyses complementaires", extras_analyses),
    ]

    for nom, module in modules:
        print(f"\n{'=' * 60}")
        print(f"  {nom}")
        print(f"{'=' * 60}")
        module.run(df=df, digraph=digraph, graph=graph)

    duree = time.time() - debut
    print(f"\n{'=' * 60}")
    print(f"  Termine en {duree:.1f} secondes")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
