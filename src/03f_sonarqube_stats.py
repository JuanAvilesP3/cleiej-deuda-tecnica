"""
P9 - Deuda tecnica en software academico latinoamericano
03f_sonarqube_stats.py

Compara academico vs. control sobre las metricas REALES de SonarQube
(complejidad normalizada por funcion, complejidad cognitiva, %
duplicacion, code smells por KLOC, sqale_debt_ratio), con el mismo
metodo que 04_stats.py aplico a lizard/jscpd/ck: Mann-Whitney U +
correccion de Holm + Cliff's delta.
"""

import numpy as np
import pandas as pd
from scipy import stats

ROOT_RAW = r"C:\Users\Juan\Desktop\PAPERS\09-cleiej-deuda-tecnica\data\raw"


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    n1, n2 = len(a), len(b)
    gt = sum((x > y) for x in a for y in b)
    lt = sum((x < y) for x in a for y in b)
    return (gt - lt) / (n1 * n2)


def effect_label(d):
    ad = abs(d)
    if ad < 0.147:
        return "negligible"
    elif ad < 0.33:
        return "small"
    elif ad < 0.474:
        return "medium"
    return "large"


df = pd.read_csv(f"{ROOT_RAW}/metrics_sonarqube.csv")
df["complexity_per_function"] = df["complexity"] / df["functions"].replace(0, np.nan)
df["cognitive_per_function"] = df["cognitive_complexity"] / df["functions"].replace(0, np.nan)
df["smells_per_kloc"] = df["code_smells"] / (df["ncloc"].replace(0, np.nan) / 1000)

metrics = [
    ("complexity_per_function", "Complejidad ciclomatica por funcion (SonarQube)"),
    ("cognitive_per_function", "Complejidad cognitiva por funcion (SonarQube)"),
    ("duplicated_lines_density", "% lineas duplicadas (SonarQube)"),
    ("sqale_debt_ratio", "Ratio de deuda tecnica, sqale_debt_ratio (SonarQube)"),
    ("smells_per_kloc", "Code smells por 1000 lineas (SonarQube)"),
]

acad = df[df.group == "academico"]
ctrl = df[df.group == "control"]

results = []
for col, label in metrics:
    a = acad[col].dropna().values
    c = ctrl[col].dropna().values
    if len(a) < 5 or len(c) < 5:
        continue
    u, p = stats.mannwhitneyu(a, c, alternative="two-sided")
    d = cliffs_delta(a, c)
    results.append({
        "metric": label, "n_acad": len(a), "n_ctrl": len(c),
        "median_acad": np.median(a), "median_ctrl": np.median(c),
        "cliffs_delta": d, "effect": effect_label(d), "p_raw": p,
    })

# Holm correction
pvals = [r["p_raw"] for r in results]
order = np.argsort(pvals)
m = len(pvals)
holm = [None] * m
running_max = 0
for rank, idx in enumerate(order):
    adj = (m - rank) * pvals[idx]
    running_max = max(running_max, adj)
    holm[idx] = min(running_max, 1.0)
for r, h in zip(results, holm):
    r["p_holm"] = h

print(f"{'metric':<55} {'n_a':>5} {'n_c':>5} {'med_a':>10} {'med_c':>10} {'delta':>8} {'effect':>12} {'p_holm':>10}")
for r in results:
    print(f"{r['metric']:<55} {r['n_acad']:>5} {r['n_ctrl']:>5} {r['median_acad']:>10.3f} "
          f"{r['median_ctrl']:>10.3f} {r['cliffs_delta']:>8.3f} {r['effect']:>12} {r['p_holm']:>10.4g}")

pd.DataFrame(results).to_csv(f"{ROOT_RAW}/sonarqube_comparacion_academico_control.csv", index=False)
print(f"\nGuardado: {ROOT_RAW}\\sonarqube_comparacion_academico_control.csv")
