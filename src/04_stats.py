"""
P9 - Deuda tecnica en software academico latinoamericano
04_stats.py

Mann-Whitney U por metrica (academico vs. control), con correccion de
Holm para comparaciones multiples, y Cliff's delta como tamano del
efecto (ficha tecnica, seccion 4-5: "no asumir normalidad... usar
pruebas no parametricas siempre... reportar mediana e IQR, no media").
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"

METRICS = ["cc_mean", "cc_max", "nloc_total", "duplication_pct", "test_file_ratio",
           "cbo_mean", "lcom_mean", "dit_mean", "wmc_mean"]
METRIC_LABELS = {
    "cc_mean": "Complejidad ciclomática (media)", "cc_max": "Complejidad ciclomática (máxima)",
    "nloc_total": "Líneas de código", "duplication_pct": "% duplicación",
    "test_file_ratio": "Proporción de archivos de test", "cbo_mean": "CBO (acoplamiento, solo Java)",
    "lcom_mean": "LCOM (falta de cohesión, solo Java)", "dit_mean": "DIT (profundidad herencia, solo Java)",
    "wmc_mean": "WMC (complejidad por clase, solo Java)",
}


def cliffs_delta(x, y):
    x, y = np.asarray(x), np.asarray(y)
    nx, ny = len(x), len(y)
    # O(nx*ny) directo -- las muestras aqui son chicas (<300), no hace falta optimizar
    greater = sum((xi > y).sum() for xi in x)
    less = sum((xi < y).sum() for xi in x)
    return (greater - less) / (nx * ny)


def interpret_delta(d):
    ad = abs(d)
    if ad < 0.147:
        return "insignificante"
    if ad < 0.33:
        return "pequeño"
    if ad < 0.474:
        return "mediano"
    return "grande"


def main():
    df = pd.read_csv(RESULTS_DIR / "metrics_consolidado.csv")
    academic = df[df.group == "academico"]
    control = df[df.group == "control"]

    rows = []
    for metric in METRICS:
        a = academic[metric].dropna().values
        c = control[metric].dropna().values
        if len(a) < 5 or len(c) < 5:
            continue
        stat, p = mannwhitneyu(a, c, alternative="two-sided")
        delta = cliffs_delta(a, c)
        rows.append(dict(
            metric=metric, label=METRIC_LABELS[metric],
            n_academico=len(a), n_control=len(c),
            mediana_academico=np.median(a), mediana_control=np.median(c),
            iqr_academico=np.percentile(a, 75) - np.percentile(a, 25),
            iqr_control=np.percentile(c, 75) - np.percentile(c, 25),
            U=stat, p_valor=p, cliffs_delta=delta, tamano_efecto=interpret_delta(delta),
        ))

    result = pd.DataFrame(rows)
    # Correccion de Holm para comparaciones multiples
    reject, p_adj, _, _ = multipletests(result["p_valor"], method="holm")
    result["p_ajustado_holm"] = p_adj
    result["significativo_holm_0.05"] = reject

    result = result.sort_values("p_ajustado_holm")
    result.to_csv(RESULTS_DIR / "mann_whitney_resultados.csv", index=False)

    print("=== Mann-Whitney U + corrección de Holm + Cliff's delta ===\n")
    for _, row in result.iterrows():
        sig = "significativo" if row["significativo_holm_0.05"] else "no significativo"
        direction = "académico >" if row["mediana_academico"] > row["mediana_control"] else "académico <"
        print(f"{row['label']:38s} mediana acad={row['mediana_academico']:.3f}  control={row['mediana_control']:.3f}  "
              f"({direction} control)  delta={row['cliffs_delta']:+.3f} ({row['tamano_efecto']})  "
              f"p_holm={row['p_ajustado_holm']:.4f} [{sig}]")

    print(f"\nCompletado: {RESULTS_DIR / 'mann_whitney_resultados.csv'}")


if __name__ == "__main__":
    main()
