"""
P9 - Deuda tecnica en software academico latinoamericano
04b_language_stratified.py

La revision adversarial señalo que el grupo control se parea por
lenguaje Y tamano, pero nunca se reporta si el efecto de complejidad
sobrevive DENTRO de cada lenguaje por separado -- si un lenguaje
domina la composicion y tiene su propia complejidad tipica, el
efecto agregado podria ser un artefacto de composicion (Simpson).

Este script repite la comparacion de complejidad ciclomatica
(cc_mean, la metrica del hallazgo central) por separado para cada
uno de los 3 lenguajes (Java, JavaScript, Python), con Mann-Whitney U
+ Holm (3 comparaciones) + Cliff's delta, exactamente el mismo
procedimiento que 04_stats.py usa para la comparacion agregada.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"


def cliffs_delta(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    n_a, n_b = len(a), len(b)
    # Formula O(n log n) via ranking, equivalente a la version O(n^2)
    all_vals = np.concatenate([a, b])
    ranks = pd.Series(all_vals).rank().values
    rank_a = ranks[:n_a]
    delta = (2 * rank_a.sum() - n_a * (n_a + n_b + 1)) / (n_a * n_b)
    return delta


def main():
    ac = pd.read_csv(RAW_DIR / "metrics_academico.csv")
    co = pd.read_csv(RAW_DIR / "metrics_control.csv")

    print(f"Academico: n={len(ac)}, Control: n={len(co)}")
    print("Composicion por lenguaje:")
    print(pd.DataFrame({"academico": ac["language"].value_counts(), "control": co["language"].value_counts()}))

    rows = []
    for lang in ["Java", "JavaScript", "Python"]:
        a = ac.loc[ac.language == lang, "cc_mean"].dropna()
        c = co.loc[co.language == lang, "cc_mean"].dropna()
        u, p = mannwhitneyu(a, c, alternative="two-sided")
        delta = cliffs_delta(a.values, c.values)
        rows.append(dict(
            language=lang, n_academic=len(a), n_control=len(c),
            median_academic=a.median(), median_control=c.median(),
            u_stat=u, p_raw=p, cliffs_delta=delta,
        ))

    out = pd.DataFrame(rows)
    _, p_holm, _, _ = multipletests(out["p_raw"], method="holm")
    out["p_holm"] = p_holm
    out.to_csv(RESULTS_DIR / "language_stratified_complexity.csv", index=False)

    print("\n=== Complejidad ciclomatica (cc_mean), academico vs control, por lenguaje ===")
    print(out.round(4).to_string(index=False))
    print(f"\nCompletado: guardado en {RESULTS_DIR / 'language_stratified_complexity.csv'}")


if __name__ == "__main__":
    main()
