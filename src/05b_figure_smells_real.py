"""
P9 - Deuda tecnica en software academico latinoamericano
05b_figure_smells_real.py

Reemplaza la Fig. 4 adaptada (tamano de efecto por metrica) por la
version REAL que pide la ficha: "Barras horizontales: los 10 tipos de
code smell mas frecuentes, comparando ambos grupos" -- ahora posible
porque se corrio SonarQube de verdad (ver 03c/03d/03e_sonarqube_*.py).

Sobrescribe results/figures/fig4_resumen_efectos.png para no romper
las referencias ya existentes en el manuscrito (main.tex), pero el
contenido y el pie de figura cambian por completo.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figures_style import COLORS, apply_style, save_figure

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
FIG_DIR = Path(__file__).resolve().parent.parent / "results" / "figures"


def shorten(name, n=48):
    return name if len(name) <= n else name[: n - 1] + "…"


def main():
    apply_style()
    df = pd.read_csv(RAW_DIR / "sonarqube_smell_types_by_group.csv")
    top10 = df.sort_values("count_total", ascending=False).head(10).iloc[::-1]

    fig, ax = plt.subplots(figsize=(10, 6.5))
    y = np.arange(len(top10))
    h = 0.38
    ax.barh(y + h / 2, top10["count_academico"], height=h, color=COLORS["primary"], label="Académico")
    ax.barh(y - h / 2, top10["count_control"], height=h, color=COLORS["secondary"], label="Control")
    ax.set_yticks(y)
    ax.set_yticklabels([shorten(n) for n in top10["rule_name"]], fontsize=9)
    ax.set_xlabel("Número de issues (SonarQube, tipo CODE_SMELL)")
    ax.set_title("Fig. 4 — Los 10 tipos de code smell más frecuentes, académico vs. control\n(SonarQube Community, 415 repositorios analizados)", fontsize=11)
    ax.legend(loc="lower right", fontsize=9)
    save_figure(fig, FIG_DIR / "fig4_resumen_efectos")
    plt.close(fig)
    print("Fig. 4 (real, SonarQube) lista")


if __name__ == "__main__":
    main()
