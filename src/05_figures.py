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
PAPER_FIG_DIR = Path(__file__).resolve().parent.parent / "paper" / "figures"
PAPER_FIG_DIR.mkdir(parents=True, exist_ok=True)

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
    save_figure(fig, PAPER_FIG_DIR / "fig1_boxplots_clave")
    plt.close(fig)


def fig2_test_file_ratio(df):
    # Revision cruzada (16/10): contornos y trama distintos para distinguir los grupos en B/N.
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bins = np.linspace(0, max(df["test_file_ratio"].max(), 0.1), 25)
    styles = {"academico": dict(histtype="stepfilled", alpha=0.45, edgecolor="black", linewidth=1.0),
              "control": dict(histtype="step", hatch="///", linewidth=1.6, linestyle="--")}
    for g, color in GROUP_COLORS.items():
        ax.hist(df[df.group == g]["test_file_ratio"].dropna(), bins=bins, color=color,
                label=GROUP_LABELS[g], density=True, **styles[g])
    ax.set_xlabel("Proportion of test files")
    ax.set_ylabel("Density")
    ax.legend(fontsize=9)
    save_figure(fig, FIG_DIR / "fig2_distribucion_tests")
    save_figure(fig, PAPER_FIG_DIR / "fig2_distribucion_tests")
    plt.close(fig)


def fig3_nloc_vs_duplicacion(df):
    # Revision cruzada (16/10): recta continua (academico) y discontinua (control), ajustada por
    # minimos cuadrados sobre log10(NLOC), con banda de confianza del 95 % por bootstrap.
    fig, ax = plt.subplots(figsize=(7.5, 5))
    markers = {"academico": "o", "control": "^"}
    lines = {"academico": "-", "control": "--"}
    rng = np.random.RandomState(42)
    for g, color in GROUP_COLORS.items():
        sub = df[df.group == g].dropna(subset=["nloc_total", "duplication_pct"])
        ax.scatter(sub["nloc_total"], sub["duplication_pct"], color=color, alpha=0.45, s=22, marker=markers[g],
                   edgecolors="black", linewidths=0.3, label=GROUP_LABELS[g])
        if len(sub) > 2:
            lx, y = np.log10(sub["nloc_total"].values + 1), sub["duplication_pct"].values
            xs = np.linspace(lx.min(), lx.max(), 100)
            boots = []
            for _ in range(1000):
                i = rng.randint(0, len(lx), len(lx))
                boots.append(np.polyval(np.polyfit(lx[i], y[i], 1), xs))
            lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
            ax.fill_between(10 ** xs, lo, hi, color=color, alpha=0.18, linewidth=0)
            ax.plot(10 ** xs, np.polyval(np.polyfit(lx, y, 1), xs), color=color, linewidth=2.2, linestyle=lines[g],
                    label=f"{GROUP_LABELS[g]} trend")

    ax.set_xscale("log")
    ax.set_xlabel("Lines of code (NLOC, log scale)")
    ax.set_ylabel("Duplication (%)")
    ax.legend(fontsize=9)
    save_figure(fig, FIG_DIR / "fig3_nloc_vs_duplicacion")
    save_figure(fig, PAPER_FIG_DIR / "fig3_nloc_vs_duplicacion")
    plt.close(fig)


def fig4_resumen_efectos(mw=None):
    # Fig. 4: los 10 tipos de code smell mas frecuentes. Revision cruzada (16/10): los conteos se
    # normalizan por 1.000 lineas de codigo (NCLOC total de cada grupo en SonarQube), porque los
    # grupos tienen distinto numero de repositorios (223 vs 192) y distinto volumen de codigo.
    raw_smells = RESULTS_DIR / "sonarqube_smell_types_by_group.csv"
    if not raw_smells.exists():
        print("Warning: sonarqube_smell_types_by_group.csv not found")
        return
    df_smells = pd.read_csv(raw_smells)
    sonar = pd.read_csv(RESULTS_DIR / "metrics_sonarqube.csv")
    kloc = sonar.groupby("group")["ncloc"].sum() / 1000
    top10 = df_smells.sort_values("count_total", ascending=False).head(10).iloc[::-1].copy()
    top10["rate_academico"] = top10["count_academico"] / kloc["academico"]
    top10["rate_control"] = top10["count_control"] / kloc["control"]
    top10.to_csv(RESULTS_DIR / "sonarqube_smell_types_top10_per_kloc.csv", index=False)

    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(top10))
    h = 0.38
    ax.barh(y + h / 2, top10["rate_academico"], height=h, color=COLORS["primary"], edgecolor="black", linewidth=0.5, label="Academic")
    ax.barh(y - h / 2, top10["rate_control"], height=h, color=COLORS["secondary"], edgecolor="black", linewidth=0.5,
            hatch="///", label="Control")
    ax.set_yticks(y)
    ax.set_yticklabels(top10["rule_name"], fontsize=9)
    ax.set_xlabel("Issues per 1,000 lines of code (SonarQube CODE_SMELL rule violations)", fontsize=10)
    ax.legend(loc="lower right", fontsize=9.5)
    fig.subplots_adjust(left=0.45)
    save_figure(fig, FIG_DIR / "fig4_resumen_efectos")
    save_figure(fig, PAPER_FIG_DIR / "fig4_resumen_efectos")
    plt.close(fig)


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
