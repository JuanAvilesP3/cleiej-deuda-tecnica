"""
P9 - Deuda tecnica en software academico latinoamericano
04g_revision_checks.py

Comprobaciones anadidas tras la revision cruzada interna (16/10/2026):
  - repositorios sin funciones medibles por lizard (explican los n de la Tabla 4);
  - repositorios con menos de 10 lineas de codigo en los tres lenguajes analizados;
  - complejidad ciclomatica maxima ajustada por tamano (OLS sobre log(cc_max) con
    log(NLOC) o log(numero de funciones) como covariable), porque el maximo crece con
    el numero de funciones y el control es algo mayor.
Salida: results/tables/revision_checks.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "results" / "tables"

m = pd.read_csv(T / "metrics_consolidado.csv")
rows = []
def add(k, v):
    rows.append({"medida": k, "valor": v})
    print(f"{k}: {v}")

for g, sub in m.groupby("group"):
    add(f"{g}_n", len(sub))
    add(f"{g}_sin_funciones_lizard", int(sub.cc_mean.isna().sum()))
    add(f"{g}_nloc_menor_10", int((sub.nloc_total < 10).sum()))
    add(f"{g}_mediana_funciones", float(sub.n_functions.median()))

d = m.dropna(subset=["cc_max", "nloc_total", "n_functions"])
d = d[(d.nloc_total > 0) & (d.n_functions > 0) & (d.cc_max > 0)].copy()
d["acad"] = (d.group == "academico").astype(int)
for name, f in [("sin_ajuste", "np.log(cc_max) ~ acad"),
                ("ajuste_log_nloc", "np.log(cc_max) ~ acad + np.log(nloc_total)"),
                ("ajuste_log_funciones", "np.log(cc_max) ~ acad + np.log(n_functions)")]:
    r = smf.ols(f, data=d).fit()
    add(f"cc_max_{name}", f"beta_acad={r.params['acad']:+.3f} p={r.pvalues['acad']:.1e} n={int(r.nobs)}")


# Prueba de la explicacion central (el control seria codigo poco maduro): si fuera asi, los
# repositorios de control con senales de madurez (estrellas) deberian ser mas complejos.
import json
from scipy.stats import mannwhitneyu, spearmanr
ctrl = pd.DataFrame([json.loads(l) for l in open(ROOT / "data" / "raw" / "control_repos.jsonl", encoding="utf-8")])
mc = m[m.group == "control"].merge(ctrl[["full_name", "stargazers"]], on="full_name", how="left").dropna(subset=["cc_mean"])
rho, p = spearmanr(mc.stargazers, mc.cc_mean)
add("control_spearman_estrellas_cc_mean", f"rho={rho:+.3f} p={p:.3f} n={len(mc)}")
for k in (1, 5):
    a, b = mc[mc.stargazers >= k].cc_mean, mc[mc.stargazers < k].cc_mean
    add(f"control_cc_mean_estrellas_ge{k}", f"n={len(a)} mediana={a.median():.2f} vs n={len(b)} mediana={b.median():.2f} p={mannwhitneyu(a, b).pvalue:.3f}")

pd.DataFrame(rows).to_csv(T / "revision_checks.csv", index=False)
