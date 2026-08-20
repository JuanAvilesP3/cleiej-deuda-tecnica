"""Plantilla base de estilo de figuras, compartida por los 10 proyectos.

Copiar este archivo a src/figures_style.py de cada proyecto e importarlo
desde 05_figures.py. Mantiene consistencia visual entre los 10 artículos
y garantiza legibilidad en impresión blanco y negro (ver Fase 2, punto 6).
"""

import matplotlib

matplotlib.use("Agg")  # backend no interactivo: evita cuelgues/crashes de
# Tkinter al generar figuras en procesos en segundo plano (Windows)
import matplotlib.pyplot as plt

COLORS = {
    "primary": "#1b4965",
    "secondary": "#5fa8d3",
    "accent": "#bee9e8",
    "highlight": "#cae9ff",
    "neutral": "#62929e",
}

LINESTYLES = ["-", "--", "-.", ":"]
MARKERS = ["o", "s", "^", "D", "v"]

RC_PARAMS = {
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 10,
    "font.family": "serif",
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.bbox": "tight",
}


def apply_style():
    plt.rcParams.update(RC_PARAMS)


def save_figure(fig, path, formats=("pdf", "png")):
    """Guarda la figura en los formatos indicados; PDF para LaTeX, PNG para revisión."""
    for fmt in formats:
        fig.savefig(f"{path}.{fmt}")
