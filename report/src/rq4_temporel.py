"""RQ4: Analyse de la dynamique temporelle du reseau.

Analyse l'evolution du reseau WETH Polygon heure par heure pendant
le crash du 5 aout 2024 (Lundi Noir):
- Decoupage en 24 fenetres horaires (UTC)
- Metriques par fenetre: noeuds, aretes, densite, degre moyen, volume WETH
- Identification des pics d'activite
- Evolution temporelle des metriques

Produit 2 figures:
- figures/rq4_temporal_evolution.png : Evolution temporelle multi-metriques (fond clair)
- figures/rq4_heatmap.png : Heatmap d'activite (heure x metrique, fond clair)
"""

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from src.graph_builder import load_and_build
from src.style import (
    apply_global_style, light_style, save_figure,
    format_number,
    PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER, INFO,
    PALETTE, FIGSIZE
)


def prepare_temporal_data(df):
    """Prepare les donnees temporelles avec timestamps UTC.

    Convertit la colonne 'chrono' (epoch Unix) en datetime UTC-aware
    et extrait l'heure pour le decoupage en fenetres horaires.

    IMPORTANT (Pitfall P7): utilise utc=True pour eviter les problemes
    de fuseau horaire. Ne PAS utiliser datetime.fromtimestamp() qui
    retourne l'heure locale.

    Parametres:
        df: DataFrame avec colonne 'chrono' (Unix timestamp en secondes)

    Retourne:
        DataFrame avec colonnes ajoutees 'datetime_utc' et 'hour'
    """
    # Copie pour ne pas modifier l'original
    df = df.copy()

    # Conversion UTC-aware (Pitfall P7)
    df['datetime_utc'] = pd.to_datetime(df['chrono'], unit='s', utc=True)
    df['hour'] = df['datetime_utc'].dt.hour

    # Verification de la plage temporelle
    date_min = df['datetime_utc'].min()
    date_max = df['datetime_utc'].max()

    print(f"\n--- Preparation des donnees temporelles ---")
    print(f"  Plage temporelle: {date_min} -> {date_max}")
    print(f"  Transactions totales: {format_number(len(df))}")
    print(f"  Date:                 {date_min.strftime('%Y-%m-%d')} (UTC)")

    return df


def compute_hourly_metrics(df):
    """Calcule les metriques reseau pour chaque fenetre horaire (0-23h UTC).

    Pour chaque heure, construit un DiGraph temporaire a partir des
    transactions de cette heure et calcule:
    - Nombre de transactions
    - Nombre de noeuds
    - Nombre d'aretes (agregees par paire source/target)
    - Densite du graphe
    - Degre moyen
    - Volume total WETH transfere

    Les heures sans transactions sont gerees avec des valeurs nulles (0).

    Parametres:
        df: DataFrame avec colonnes 'source', 'target', 'weight', 'hour'

    Retourne:
        pd.DataFrame indexe par heure (0-23) avec les 6 metriques
    """
    print(f"\n--- Calcul des metriques horaires ---")

    results = []
    for hour in range(24):
        hour_df = df[df['hour'] == hour]

        if len(hour_df) == 0:
            # Heure vide: toutes les metriques a zero
            results.append({
                'hour': hour,
                'transactions': 0,
                'nodes': 0,
                'edges': 0,
                'density': 0.0,
                'mean_degree': 0.0,
                'volume_weth': 0.0
            })
            continue

        # Construire un DiGraph temporaire pour cette heure
        G_hour = nx.DiGraph()
        for (src, tgt), group in hour_df.groupby(['source', 'target']):
            G_hour.add_edge(src, tgt, weight=group['weight'].sum())

        n_nodes = G_hour.number_of_nodes()
        n_edges = G_hour.number_of_edges()
        density = nx.density(G_hour) if n_nodes > 1 else 0.0
        mean_deg = (2 * n_edges / n_nodes) if n_nodes > 0 else 0.0
        volume = hour_df['weight'].sum()

        results.append({
            'hour': hour,
            'transactions': len(hour_df),
            'nodes': n_nodes,
            'edges': n_edges,
            'density': density,
            'mean_degree': mean_deg,
            'volume_weth': volume
        })

    hourly_df = pd.DataFrame(results).set_index('hour')

    # Affichage du tableau recapitulatif
    print(f"\n  {'Heure':>5} | {'Trans':>8} | {'Noeuds':>7} | {'Aretes':>7} | {'Densite':>9} | {'Volume WETH':>14}")
    print(f"  {'-'*5}-+-{'-'*8}-+-{'-'*7}-+-{'-'*7}-+-{'-'*9}-+-{'-'*14}")
    for hour in range(24):
        row = hourly_df.loc[hour]
        print(f"  {hour:02d}h   | {int(row['transactions']):>8} | {int(row['nodes']):>7} | "
              f"{int(row['edges']):>7} | {row['density']:>9.6f} | {row['volume_weth']:>14.2f}")

    print(f"\n  Total transactions: {format_number(int(hourly_df['transactions'].sum()))}")
    print(f"  Total volume WETH:  {hourly_df['volume_weth'].sum():.2f}")

    return hourly_df


def identify_peaks(hourly_df):
    """Identifie les heures de pic d'activite pendant le crash.

    Determine l'heure de pic pour chaque metrique (transactions, noeuds,
    volume) et identifie la periode de pic contigue ou les transactions
    depassent 50% du maximum.

    Parametres:
        hourly_df: DataFrame indexe par heure avec les metriques

    Retourne:
        dict avec les heures de pic et la periode de pic
    """
    print(f"\n--- Identification des pics d'activite ---")

    # Heures de pic pour chaque metrique
    peak_tx_hour = int(hourly_df['transactions'].idxmax())
    peak_nodes_hour = int(hourly_df['nodes'].idxmax())
    peak_edges_hour = int(hourly_df['edges'].idxmax())
    peak_volume_hour = int(hourly_df['volume_weth'].idxmax())

    max_tx = int(hourly_df['transactions'].max())
    max_volume = float(hourly_df['volume_weth'].max())

    print(f"  Pic transactions: {peak_tx_hour:02d}h UTC ({format_number(max_tx)} transactions)")
    print(f"  Pic noeuds:       {peak_nodes_hour:02d}h UTC ({format_number(int(hourly_df['nodes'].max()))} noeuds)")
    print(f"  Pic aretes:       {peak_edges_hour:02d}h UTC ({format_number(int(hourly_df['edges'].max()))} aretes)")
    print(f"  Pic volume WETH:  {peak_volume_hour:02d}h UTC ({hourly_df['volume_weth'].max():.2f} WETH)")

    # Periode de pic: heures contigues ou les transactions > 50% du max
    threshold = max_tx * 0.5
    above_threshold = hourly_df['transactions'] >= threshold
    peak_hours = [h for h in range(24) if above_threshold.loc[h]]

    if peak_hours:
        # Trouver la plus longue sequence contigues
        sequences = []
        current_seq = [peak_hours[0]]
        for i in range(1, len(peak_hours)):
            if peak_hours[i] == peak_hours[i-1] + 1:
                current_seq.append(peak_hours[i])
            else:
                sequences.append(current_seq)
                current_seq = [peak_hours[i]]
        sequences.append(current_seq)

        # Plus longue sequence
        longest = max(sequences, key=len)
        peak_period = (longest[0], longest[-1])
        print(f"  Periode de pic (>50% du max): {peak_period[0]:02d}h-{peak_period[1]:02d}h UTC")
        print(f"    Heures au-dessus du seuil ({format_number(int(threshold))} tx): {[f'{h:02d}h' for h in peak_hours]}")
    else:
        peak_period = (peak_tx_hour, peak_tx_hour)
        print(f"  Periode de pic: {peak_tx_hour:02d}h UTC (heure isolee)")

    return {
        'peak_transactions_hour': peak_tx_hour,
        'peak_nodes_hour': peak_nodes_hour,
        'peak_edges_hour': peak_edges_hour,
        'peak_volume_hour': peak_volume_hour,
        'peak_period': peak_period,
        'max_transactions': max_tx,
        'max_volume': max_volume,
    }


def plot_temporal_evolution(hourly_df, peaks):
    """Trace l'evolution temporelle multi-metriques sur 24 heures.

    Figure a 2 sous-graphiques superposes:
    - Haut: activite du reseau (transactions en barres, noeuds/aretes en lignes)
    - Bas: metriques structurelles (densite, degre moyen) et volume WETH

    La zone de pic est mise en evidence par un aplat colore.
    Fond clair (graphique analytique).

    Parametres:
        hourly_df: DataFrame indexe par heure avec les metriques
        peaks: dict retourne par identify_peaks()
    """
    hours = list(range(24))

    with light_style():
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        # --- Sous-graphique superieur: Activite du reseau ---

        # Transactions en barres
        ax1.bar(hours, hourly_df['transactions'], color=PRIMARY, alpha=0.4,
                label='Transactions', zorder=2)

        # Axe secondaire pour noeuds et aretes
        ax1_twin = ax1.twinx()
        ax1_twin.plot(hours, hourly_df['nodes'], color=SECONDARY, marker='o',
                      markersize=4, linewidth=2, label='Noeuds', zorder=3)
        ax1_twin.plot(hours, hourly_df['edges'], color=ACCENT, marker='s',
                      markersize=4, linewidth=2, label='Aretes', zorder=3)

        # Zone de pic
        pp = peaks['peak_period']
        ax1.axvspan(pp[0] - 0.5, pp[1] + 0.5, alpha=0.1, color=DANGER,
                    label='Periode de pic', zorder=1)

        ax1.set_ylabel('Nombre de transactions')
        ax1_twin.set_ylabel('Noeuds / Aretes')
        ax1.set_title("Evolution temporelle de l'activite du reseau WETH (5 aout 2024)")

        # Legende combinee des deux axes
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

        # Grille seulement sur l'axe principal
        ax1.grid(True, alpha=0.3)
        ax1_twin.grid(False)

        # --- Sous-graphique inferieur: Metriques structurelles + Volume ---

        # Densite sur l'axe principal
        ax2.plot(hours, hourly_df['density'], color=SUCCESS, marker='D',
                 markersize=4, linewidth=2, label='Densite', zorder=3)
        ax2.set_ylabel('Densite')

        # Degre moyen sur axe secondaire
        ax2_twin = ax2.twinx()
        ax2_twin.plot(hours, hourly_df['mean_degree'], color=INFO, marker='^',
                      markersize=4, linewidth=2, label='Degre moyen', zorder=3)
        ax2_twin.set_ylabel('Degre moyen')

        # Volume WETH en aire remplie sur un troisieme axe
        ax2_vol = ax2.twinx()
        # Decaler le troisieme axe vers la droite
        ax2_vol.spines['right'].set_position(('axes', 1.12))
        ax2_vol.fill_between(hours, hourly_df['volume_weth'], alpha=0.15,
                             color=DANGER, label='Volume WETH', zorder=1)
        ax2_vol.plot(hours, hourly_df['volume_weth'], color=DANGER, alpha=0.5,
                     linewidth=1, zorder=2)
        ax2_vol.set_ylabel('Volume WETH')

        ax2.set_xlabel('Heure (UTC)')

        # Legende combinee
        lines_a, labels_a = ax2.get_legend_handles_labels()
        lines_b, labels_b = ax2_twin.get_legend_handles_labels()
        lines_c, labels_c = ax2_vol.get_legend_handles_labels()
        ax2.legend(lines_a + lines_b + lines_c, labels_a + labels_b + labels_c,
                   loc='upper left', fontsize=9)

        ax2.grid(True, alpha=0.3)
        ax2_twin.grid(False)
        ax2_vol.grid(False)

        # Ticks de l'axe X: heures formatees
        ax2.set_xticks(range(24))
        ax2.set_xticklabels([f'{h:02d}h' for h in range(24)], rotation=45, ha='right')

        save_figure(fig, 'rq4_temporal_evolution.png')


def plot_heatmap(hourly_df):
    """Trace la carte de chaleur de l'activite du reseau par heure.

    Normalise chaque metrique en [0, 1] (min-max scaling) et affiche
    une matrice 6 metriques x 24 heures. Permet d'identifier visuellement
    les periodes d'activite intense. Fond clair.

    Parametres:
        hourly_df: DataFrame indexe par heure avec les metriques
    """
    with light_style():
        fig, ax = plt.subplots(figsize=(16, 6))

        # Colonnes a normaliser et leurs noms francais
        metric_cols = ['transactions', 'nodes', 'edges', 'density', 'mean_degree', 'volume_weth']
        metric_names = ['Transactions', 'Noeuds', 'Aretes', 'Densite', 'Degre moyen', 'Volume WETH']

        # Normalisation min-max par colonne
        normalized = pd.DataFrame(index=hourly_df.index)
        for col in metric_cols:
            col_min = hourly_df[col].min()
            col_max = hourly_df[col].max()
            if col_max > col_min:
                normalized[col] = (hourly_df[col] - col_min) / (col_max - col_min)
            else:
                # Colonne constante (ou tout a zero)
                normalized[col] = 0.0

        # Matrice: lignes = metriques, colonnes = heures
        data_matrix = np.array([normalized[col].values for col in metric_cols])

        im = ax.imshow(data_matrix, aspect='auto', cmap='YlOrRd', interpolation='nearest')

        # Axes
        ax.set_yticks(range(len(metric_names)))
        ax.set_yticklabels(metric_names, fontsize=11)
        ax.set_xticks(range(24))
        ax.set_xticklabels([f'{h:02d}h' for h in range(24)], rotation=45, ha='right', fontsize=9)
        ax.set_xlabel('Heure (UTC)')

        # Barre de couleur
        cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
        cbar.set_label('Intensite normalisee', fontsize=11)

        ax.set_title("Carte de chaleur de l'activite du reseau WETH par heure\n(5 aout 2024, UTC)",
                      fontsize=13)

        # Ajouter les valeurs dans les cellules pour lisibilite
        for i in range(len(metric_names)):
            for j in range(24):
                val = data_matrix[i, j]
                # Texte blanc si fond sombre, noir si fond clair
                color = 'white' if val > 0.6 else 'black'
                ax.text(j, i, f'{val:.1f}', ha='center', va='center',
                        fontsize=6, color=color)

        save_figure(fig, 'rq4_heatmap.png')


def run(df=None, digraph=None, graph=None):
    """Point d'entree RQ4 - Dynamique temporelle.

    Analyse l'evolution du reseau WETH Polygon heure par heure pendant
    le crash du 5 aout 2024: metriques horaires, pics d'activite,
    et 2 visualisations.

    Parametres:
        df: DataFrame pandas (charge automatiquement si None)
        digraph: nx.DiGraph (charge automatiquement si None)
        graph: nx.Graph non-oriente (charge automatiquement si None)

    Retourne:
        dict avec les metriques temporelles
    """
    if df is None:
        df, digraph, graph = load_and_build()
    apply_global_style()

    print("\n=== RQ4: Analyse de la dynamique temporelle ===")

    # Preparation des donnees temporelles
    df_temporal = prepare_temporal_data(df)

    # Metriques par fenetre horaire
    hourly_df = compute_hourly_metrics(df_temporal)

    # Identification des pics
    peaks = identify_peaks(hourly_df)

    # Visualisations
    plot_temporal_evolution(hourly_df, peaks)
    plot_heatmap(hourly_df)

    print("\n=== RQ4 terminee ===\n")

    return {
        'hourly_metrics': hourly_df,
        'peak_transactions_hour': peaks['peak_transactions_hour'],
        'peak_volume_hour': peaks['peak_volume_hour'],
        'max_transactions': peaks['max_transactions'],
        'max_volume': peaks['max_volume'],
        'peak_period': peaks['peak_period'],
        'total_hours_active': int((hourly_df['transactions'] > 0).sum()),
    }


if __name__ == "__main__":
    run()
