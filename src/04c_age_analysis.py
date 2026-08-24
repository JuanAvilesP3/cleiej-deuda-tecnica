"""
P9 - Deuda tecnica en software academico latinoamericano
04c_age_analysis.py

Prueba directa de la explicacion alternativa que senalo la revision
adversarial: si el codigo academico es simplemente mas joven / con
menos historial de mantenimiento (los proyectos de curso terminan
cuando termina el semestre), eso -- no "academico vs no-academico"
per se -- podria explicar la menor complejidad observada.

Usa created_at/pushed_at de la API de GitHub (03h_repo_age.py) para
calcular la vida util de cada repo en dias, compara esa vida util
entre grupos, y corre una regresion de cc_mean sobre group + log(vida
util + 1) para ver si el efecto de grupo sobrevive controlando por
vida util.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
import statsmodels.formula.api as smf

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"


def main():
    ages = [json.loads(l) for l in (RAW_DIR / "repo_age.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ages_df = pd.DataFrame(ages)
    ages_df["created_at"] = pd.to_datetime(ages_df["created_at"], utc=True, errors="coerce")
    ages_df["pushed_at"] = pd.to_datetime(ages_df["pushed_at"], utc=True, errors="coerce")
    ages_df["lifespan_days"] = (ages_df["pushed_at"] - ages_df["created_at"]).dt.total_seconds() / 86400

    ac = pd.read_csv(RAW_DIR / "metrics_academico.csv")
    co = pd.read_csv(RAW_DIR / "metrics_control.csv")
    ac["group"] = "academic"
    co["group"] = "control"
    combined = pd.concat([ac[["full_name", "group", "language", "cc_mean"]],
                           co[["full_name", "group", "language", "cc_mean"]]], ignore_index=True)
    merged = combined.merge(ages_df[["full_name", "lifespan_days"]], on="full_name", how="left")
    n_missing = merged["lifespan_days"].isna().sum()
    merged = merged.dropna(subset=["lifespan_days", "cc_mean"])
    merged = merged[merged["lifespan_days"] >= 0]

    print(f"n total={len(combined)}, resueltos con fecha valida={len(merged)}, "
          f"sin fecha o invalida={n_missing + (combined.shape[0]-len(merged)-n_missing)}")

    a_life = merged.loc[merged.group == "academic", "lifespan_days"]
    c_life = merged.loc[merged.group == "control", "lifespan_days"]
    u, p = mannwhitneyu(a_life, c_life, alternative="two-sided")
    print(f"\nVida util (dias): academico mediana={a_life.median():.1f} (n={len(a_life)}), "
          f"control mediana={c_life.median():.1f} (n={len(c_life)}), Mann-Whitney p={p:.4g}")

    merged["log_lifespan"] = np.log1p(merged["lifespan_days"])
    merged["group_academic"] = (merged["group"] == "academic").astype(int)

    model_group_only = smf.ols("cc_mean ~ group_academic", data=merged).fit()
    model_with_age = smf.ols("cc_mean ~ group_academic + log_lifespan", data=merged).fit()

    print("\n=== OLS: cc_mean ~ group (sin controlar edad) ===")
    print(model_group_only.params.round(4), "\np-values:", model_group_only.pvalues.round(4).to_dict())
    print("\n=== OLS: cc_mean ~ group + log(vida_util_dias + 1) ===")
    print(model_with_age.params.round(4), "\np-values:", model_with_age.pvalues.round(4).to_dict())

    out = pd.DataFrame({
        "term": ["group_academic (no controla edad)", "group_academic (controla log-vida util)", "log_lifespan"],
        "coef": [model_group_only.params["group_academic"], model_with_age.params["group_academic"], model_with_age.params["log_lifespan"]],
        "p_value": [model_group_only.pvalues["group_academic"], model_with_age.pvalues["group_academic"], model_with_age.pvalues["log_lifespan"]],
    })
    out.to_csv(RESULTS_DIR / "age_control_regression.csv", index=False)

    life_summary = pd.DataFrame({
        "group": ["academic", "control"],
        "n": [len(a_life), len(c_life)],
        "median_lifespan_days": [a_life.median(), c_life.median()],
        "mean_lifespan_days": [a_life.mean(), c_life.mean()],
    })
    life_summary.to_csv(RESULTS_DIR / "age_summary.csv", index=False)
    print(f"\nCompletado: guardado en {RESULTS_DIR / 'age_control_regression.csv'} y age_summary.csv")


if __name__ == "__main__":
    main()
