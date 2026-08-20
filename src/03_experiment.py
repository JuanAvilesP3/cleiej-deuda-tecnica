"""
P9 - Deuda tecnica en software academico latinoamericano
03_experiment.py

Consolida las metricas de los dos grupos (academico/control) en una
sola tabla (ficha tecnica, seccion 4). Ver 02_preprocess.py para la
lista completa de sustituciones de herramientas (SonarQube -> lizard +
jscpd + ck) y sus limitaciones documentadas.

Metricas consolidadas, mapeadas a lo que pide la ficha:
  - complejidad ciclomatica media y maxima -> cc_mean, cc_max (lizard)
  - duplicacion -> duplication_pct (jscpd)
  - cobertura -> test_file_ratio (PROXY: no es cobertura real medida
    ejecutando pruebas, es la proporcion de archivos que son archivos
    de test por convencion de nombre)
  - acoplamiento/cohesion/herencia (solo repos Java) -> cbo_mean,
    lcom_mean, dit_mean, wmc_mean (ck)

NO se reconstruye la "densidad de smells" ni el "ratio de deuda
tecnica" especificos de SonarQube (son metricas propietarias basadas
en tiempos de remediacion estimados; sin SonarQube no hay forma
honesta de reproducirlos). El analisis estadistico se hace
directamente sobre las metricas de arriba, que ya prueban la hipotesis
del articulo.
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"

METRICS = ["cc_mean", "cc_max", "nloc_total", "duplication_pct", "test_file_ratio",
           "cbo_mean", "lcom_mean", "dit_mean", "wmc_mean"]


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    academic = pd.read_csv(RAW_DIR / "metrics_academico.csv")
    control = pd.read_csv(RAW_DIR / "metrics_control.csv")

    df = pd.concat([academic, control], ignore_index=True)
    df["group"] = df["group"].map({"academico": "academico", "control": "control"})

    out_path = RESULTS_DIR / "metrics_consolidado.csv"
    df.to_csv(out_path, index=False)

    print(f"Consolidado: {len(df)} repos ({(df.group=='academico').sum()} académicos, "
          f"{(df.group=='control').sum()} control)")
    print(f"\nPor lenguaje:\n{df.groupby(['group','language']).size().unstack(fill_value=0)}")

    print("\nResumen por métrica y grupo (mediana):")
    summary = df.groupby("group")[METRICS].median().T
    print(summary.round(3))
    summary.to_csv(RESULTS_DIR / "resumen_medianas.csv")

    print(f"\nCompletado: {out_path}")


if __name__ == "__main__":
    main()
