"""
P9 - Deuda tecnica en software academico latinoamericano
05b_figure_smells_real.py

Genera la Fig. 4 REAL de SonarQube:
Barras horizontales comparando los 10 tipos de code smell mas frecuentes
entre repositorios academicos y de control.
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


def shorten(name, n=46):
    return name if len(name) <= n else name[: n - 1] + "…"


def main():
    apply_style()
    df = pd.read_csv(RAW_DIR / "sonarqube_smell_types_by_group.csv")
    top10 = df.sort_values("count_total", ascending=False).head(10).iloc[::-1]

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    y = np.arange(len(top10))
    h = 0.38
    ax.barh(y + h / 2, top10["count_academico"], height=h, color=COLORS["primary"], label="Academic")
    ax.barh(y - h / 2, top10["count_control"], height=h, color=COLORS["secondary"], label="Control")
    ax.set_yticks(y)
    ax.set_yticklabels([shorten(n) for n in top10["rule_name"]], fontsize=9)
    ax.set_xlabel("Number of issues (SonarQube CODE_SMELL rule violations)", fontsize=10)
    # Sin ax.set_title interno para cumplir con las directrices de CLEIej
    ax.legend(loc="lower right", fontsize=9.5)
    
    save_figure(fig, FIG_DIR / "fig4_resumen_efectos")
    plt.close(fig)
    print("Fig. 4 (real, SonarQube en ingles) generada con exito")


if __name__ == "__main__":
    main()
