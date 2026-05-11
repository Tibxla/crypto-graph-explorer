"""Style module: global matplotlib configuration, color palettes, and figure helpers."""

import matplotlib.pyplot as plt
from contextlib import contextmanager
import os

# Couleurs principales
PRIMARY = "#2563EB"
SECONDARY = "#7C3AED"
ACCENT = "#F59E0B"
SUCCESS = "#10B981"
DANGER = "#EF4444"
INFO = "#06B6D4"
PINK = "#EC4899"

# Fonds et textes
BG_DARK = "#0F172A"
BG_LIGHT = "#FFFFFF"
TEXT_LIGHT = "#F8FAFC"
TEXT_DARK = "#1E293B"
GRID_COLOR = "#E2E8F0"

# Palette ordonnee pour les series de donnees
PALETTE = [PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER, INFO, PINK]

# Parametres globaux
DPI = 200
FIGSIZE = (12, 8)
SEED = 42


def apply_global_style():
    """Applique le style global matplotlib pour toutes les figures du projet."""
    plt.rcParams.update({
        'figure.figsize': FIGSIZE,
        'figure.dpi': DPI,
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'figure.constrained_layout.use': True,
        'axes.spines.top': False,
        'axes.spines.right': False,
    })


@contextmanager
def dark_style():
    """Contexte pour graphes reseau avec fond sombre (#0F172A).

    Utilise le theme 'dark_background' de matplotlib et applique
    les couleurs de fond du projet.
    """
    with plt.style.context('dark_background'):
        plt.rcParams['axes.facecolor'] = BG_DARK
        plt.rcParams['figure.facecolor'] = BG_DARK
        yield


@contextmanager
def light_style():
    """Contexte pour graphiques analytiques avec fond clair.

    Applique un fond blanc, texte sombre, et grille legere.
    Restaure les parametres precedents a la sortie.
    """
    # Sauvegarder les parametres actuels
    saved = dict(plt.rcParams)
    try:
        plt.rcParams['axes.facecolor'] = BG_LIGHT
        plt.rcParams['figure.facecolor'] = BG_LIGHT
        plt.rcParams['axes.edgecolor'] = TEXT_DARK
        plt.rcParams['text.color'] = TEXT_DARK
        plt.rcParams['axes.labelcolor'] = TEXT_DARK
        plt.rcParams['xtick.color'] = TEXT_DARK
        plt.rcParams['ytick.color'] = TEXT_DARK
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.color'] = GRID_COLOR
        plt.rcParams['grid.alpha'] = 0.3
        yield
    finally:
        # Restaurer les parametres originaux
        plt.rcParams.update(saved)


def save_figure(fig, filename, figures_dir="figures"):
    """Sauvegarde coherente d'une figure avec les parametres du projet.

    Cree le dossier de destination si necessaire. Utilise le DPI global
    et preserve la couleur de fond de la figure.
    """
    os.makedirs(figures_dir, exist_ok=True)
    fig.savefig(
        os.path.join(figures_dir, filename),
        dpi=DPI,
        bbox_inches='tight',
        facecolor=fig.get_facecolor(),
        edgecolor='none'
    )
    plt.close(fig)
    print(f"Figure sauvegardee: {filename}")


def format_number(n):
    """Formate un nombre avec des espaces comme separateur de milliers (convention francaise).

    Exemple: 401709 -> '401 709'
    """
    return f"{n:,}".replace(",", " ")


def format_address(addr, n=6):
    """Tronque une adresse hexadecimale pour affichage lisible.

    Exemple: '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619' -> '0x7ceb23...f1b9f619'
    """
    if len(addr) <= 2 * n + 2:
        return addr
    return f"{addr[:n+2]}...{addr[-n:]}"
