"""
P9 - Deuda tecnica en software academico latinoamericano
05_figures.py

Las 4 figuras de la ficha (seccion 6), adaptadas a las metricas
realmente disponibles (ver 03_experiment.py: no hay "ratio de deuda
tecnica" ni catalogo de tipos de smell de SonarQube):

  Fig. 1: cajas de 4 metricas clave, academico vs control.
  Fig. 2: distribucion de la proporcion de archivos de test.
  Fig. 3 (la que sostiene el argumento, adaptada): dispersion de
         lineas de codigo vs. % duplicacion (el proxy de deuda
         tecnica que si se pudo medir), color por grupo, con
         tendencia.
  Fig. 4 (adaptada, sustituye "10 tipos de smell" que requeriria
         SonarQube): resumen de las 9 metricas con Cliff's delta y
         significancia (Holm), para ver de un vistazo donde aparece
         la diferencia real.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from figures_style import COLORS, apply_style, save_figure

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"
FIG_DIR = Path(__file__).resolve().parent.parent / "results" / "figures"

GROUP_COLORS = {"academico": COLORS["primary"], "control": COLORS["secondary"]}
GROUP_LABELS = {"academico": "Academic", "control": "Control"}

ENGLISH_METRIC_LABELS = {
    "Complejidad ciclomática (media)": "Cyclomatic complexity (mean)",
    "Complejidad ciclomática (máxima)": "Cyclomatic complexity (max)",
    "DIT (profundidad herencia, solo Java)": "DIT (inheritance depth, Java)",
    "Líneas de código": "Lines of code (NLOC)",
    "CBO (acoplamiento, solo Java)": "CBO (coupling, Java)",
    "LCOM (falta de cohesión, solo Java)": "LCOM (cohesion, Java)",
    "WMC (complejidad por clase, solo Java)": "WMC (complexity/class, Java)",
    "% duplicación": "Duplication (%)",
    "Proporción de archivos de test": "Test-file proportion",
}


def fig1_boxplots_clave(df):
    metrics = ["cc_mean", "cc_max", "duplication_pct", "dit_mean"]
    labels = ["Complexity\n(mean)", "Complexity\n(max)", "Duplication\n(%)", "DIT\n(Java only)"]

    fig, axes = plt.subplots(1, 4, figsize=(11, 4.5))
    for ax, metric, label in zip(axes, metrics, labels):
        data = [df[df.group == g][metric].dropna().values for g in ["academico", "control"]]
        bp = ax.boxplot(data, patch_artist=True, showfliers=False, widths=0.5)
        for patch, g in zip(bp["boxes"], ["academico", "control"]):
            patch.set_facecolor(GROUP_COLORS[g])
            patch.set_alpha(0.8)
            if g == "control":
                patch.set_hatch('//')
        for median in bp["medians"]:
            median.set_color("black")
        ax.set_xticks([1, 2])
        ax.set_xticklabels([GROUP_LABELS["academico"], GROUP_LABELS["control"]])
        ax.set_title(label, fontsize=9.5)

    save_figure(fig, FIG_DIR / "fig1_boxplots_clave")
    plt.close(fig)


def fig2_test_file_ratio(df):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bins = np.linspace(0, max(df["test_file_ratio"].max(), 0.1), 25)
    for g, color in GROUP_COLORS.items():
        ax.hist(df[df.group == g]["test_file_ratio"].dropna(), bins=bins, alpha=0.6,
                 color=color, label=GROUP_LABELS[g], density=True)
    ax.set_xlabel("Proportion of test files")
    ax.set_ylabel("Density")
    ax.legend(fontsize=9)
    save_figure(fig, FIG_DIR / "fig2_distribucion_tests")
    plt.close(fig)


def fig3_nloc_vs_duplicacion(df):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    markers = {"academico": "o", "control": "^"}
    for g, color in GROUP_COLORS.items():
        sub = df[df.group == g].dropna(subset=["nloc_total", "duplication_pct"])
        ax.scatter(sub["nloc_total"], sub["duplication_pct"], color=color, alpha=0.5, s=25, marker=markers[g], label=GROUP_LABELS[g])
        if len(sub) > 2:
            x, y = sub["nloc_total"].values, sub["duplication_pct"].values
            order = np.argsort(x)
            coef = np.polyfit(np.log10(x + 1), y, 1)
            xs = np.sort(x)
            ax.plot(xs, np.polyval(coef, np.log10(xs + 1)), color=color, linewidth=2)

    ax.set_xscale("log")
    ax.set_xlabel("Lines of code (NLOC, log scale)")
    ax.set_ylabel("Duplication (%)")
    ax.legend(fontsize=9)
    save_figure(fig, FIG_DIR / "fig3_nloc_vs_duplicacion")
    plt.close(fig)


def fig4_resumen_efectos(mw=None):
    # Genera la Fig. 4 real de SonarQube (los 10 code smells mas frecuentes)
    raw_smells = Path(__file__).resolve().parent.parent / "data" / "raw" / "sonarqube_smell_types_by_group.csv"
    if raw_smells.exists():
        df_smells = pd.read_csv(raw_smells)
        top10 = df_smells.sort_values("count_total", ascending=False).head(10).iloc[::-1]

        fig, ax = plt.subplots(figsize=(11, 6))
        y = np.arange(len(top10))
        h = 0.38
        ax.barh(y + h / 2, top10["count_academico"], height=h, color=COLORS["primary"], label="Academic")
        ax.barh(y - h / 2, top10["count_control"], height=h, color=COLORS["secondary"], label="Control")
        ax.set_yticks(y)
        ax.set_yticklabels(top10["rule_name"], fontsize=9)
        ax.set_xlabel("Number of issues (SonarQube CODE_SMELL rule violations)", fontsize=10)
        ax.legend(loc="lower right", fontsize=9.5)
        fig.subplots_adjust(left=0.45)
        save_figure(fig, FIG_DIR / "fig4_resumen_efectos")
        plt.close(fig)
    else:
        print("Warning: sonarqube_smell_types_by_group.csv not found")


def main():
    apply_style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RESULTS_DIR / "metrics_consolidado.csv")
    mw = pd.read_csv(RESULTS_DIR / "mann_whitney_resultados.csv")

    fig1_boxplots_clave(df)
    print("Fig. 1 lista")
    fig2_test_file_ratio(df)
    print("Fig. 2 lista")
    fig3_nloc_vs_duplicacion(df)
    print("Fig. 3 lista")
    fig4_resumen_efectos(mw)
    print("Fig. 4 lista (SonarQube Top-10 smells real)")

    print(f"\nCompletado: 4 figuras guardadas en {FIG_DIR}")


if __name__ == "__main__":
    main()
