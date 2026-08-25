"""
P9 - Deuda tecnica en software academico latinoamericano
04f_sonarqube_attrition_bias.py

Robustez (revision adversarial, seguimiento): la Discusion original
dejaba como pregunta abierta si la atricion diferencial hacia la
sub-muestra de SonarQube (415 de 546 repos re-clonados) sesga sus
resultados. Se prueba directamente: se cruza la muestra primaria
(metrics_consolidado.csv, 549 repos, metricas lizard) contra la lista
de repos retenidos en la sub-muestra de SonarQube
(data/raw/metrics_sonarqube.csv) para comparar, dentro de cada grupo,
los repos atricionados (fallaron el analisis SonarQube) contra los
retenidos, en tamanno (NLOC) y en complejidad ciclomatica media.
"""

from pathlib import Path

import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results" / "tables"
RAW_DIR = ROOT / "data" / "raw"


def main():
    primary = pd.read_csv(RESULTS_DIR / "metrics_consolidado.csv")
    sonar = pd.read_csv(RAW_DIR / "metrics_sonarqube.csv")
    retained_names = set(sonar["full_name"])
    primary["retained_en_sonarqube"] = primary["full_name"].isin(retained_names)

    rows = []
    for group in ("academico", "control"):
        sub = primary[primary.group == group]
        ret, att = sub[sub.retained_en_sonarqube], sub[~sub.retained_en_sonarqube]

        for metric in ("nloc_total", "cc_mean"):
            r, a = ret[metric].dropna(), att[metric].dropna()
            stat, p = mannwhitneyu(a, r, alternative="two-sided")
            rows.append(dict(
                group=group, metric=metric,
                n_retenidos=len(r), n_atricionados=len(a),
                mediana_retenidos=r.median(), mediana_atricionados=a.median(),
                mannwhitney_u=stat, p_value=p,
            ))
            print(f"[{group}][{metric}] retenidos n={len(r)} mediana={r.median():.2f} | "
                  f"atricionados n={len(a)} mediana={a.median():.2f} | p={p:.4f}")

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS_DIR / "sonarqube_atricion_sesgo.csv", index=False)
    print(f"\nCompletado: {RESULTS_DIR / 'sonarqube_atricion_sesgo.csv'}")


if __name__ == "__main__":
    main()
