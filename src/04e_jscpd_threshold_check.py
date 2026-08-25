"""
P9 - Deuda tecnica en software academico latinoamericano
04e_jscpd_threshold_check.py

Robustez (revision adversarial ronda 2): la Discusion del manuscrito
deja como discrepancia sin resolver que jscpd (umbral por defecto,
~50 tokens) no encuentra diferencia de duplicacion academico/control,
mientras SonarQube (umbral tipico ~100 tokens / 10 lineas para Java) si
encuentra mas duplicacion en academico -- y que ninguna de las dos
posibles causas (muestra distinta, 549 vs 415; umbral distinto) se
habia aislado. Este script aisla el factor "umbral": re-corre jscpd con
--min-tokens 100 (igualando el umbral tipico de SonarQube) sobre el
MISMO subconjunto de 415 repos ya re-clonados para la comparacion con
SonarQube (repos_sonar/), manteniendo la muestra identica a la de la
Tabla 3 (SonarQube) y aislando el umbral como la unica variable que
cambia frente al jscpd original (Tabla 2, umbral por defecto ~50).
"""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
RESULTS_DIR = ROOT / "results" / "tables"

JSCPD_BIN = shutil.which("jscpd") or shutil.which("jscpd.cmd") or "jscpd"
TOOL_TIMEOUT = 120
MIN_TOKENS = 100  # aproxima el umbral tipico de SonarQube para Java


def cliffs_delta(a, b):
    a, b = list(a), list(b)
    n_a, n_b = len(a), len(b)
    more = sum(1 for x in a for y in b if x > y)
    less = sum(1 for x in a for y in b if x < y)
    return (more - less) / (n_a * n_b)


def run_jscpd_threshold(repo_path: Path) -> float:
    out_dir = repo_path.parent / f"{repo_path.name}_jscpd100"
    try:
        subprocess.run(
            [JSCPD_BIN, str(repo_path), "--min-tokens", str(MIN_TOKENS),
             "--reporters", "json", "--output", str(out_dir), "--silent"],
            timeout=TOOL_TIMEOUT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        report_path = out_dir / "jscpd-report.json"
        if not report_path.exists():
            return 0.0
        report = json.loads(report_path.read_text(encoding="utf-8", errors="ignore"))
        return report.get("statistics", {}).get("total", {}).get("percentage", 0.0)
    except Exception:
        return None
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def main():
    sonar = pd.read_csv(RAW_DIR / "metrics_sonarqube.csv")
    n = len(sonar)
    rows = []
    t0 = time.time()

    for i, (_, row) in enumerate(sonar.iterrows(), 1):
        folder = row["full_name"].replace("/", "__")
        for group_dir_name in ("academico", "control"):
            repo_dir = RAW_DIR / "repos_sonar" / group_dir_name / folder
            if repo_dir.is_dir():
                pct = run_jscpd_threshold(repo_dir)
                rows.append({"full_name": row["full_name"], "group": row["group"], "duplication_pct_k100": pct})
                break
        if i % 25 == 0 or i == n:
            print(f"  {i}/{n} repos escaneados ({time.time()-t0:.0f}s)", flush=True)

    df = pd.DataFrame(rows).dropna(subset=["duplication_pct_k100"])
    df.to_csv(RESULTS_DIR / "jscpd_k100_por_repo.csv", index=False)
    print(f"Repos con resultado valido: {len(df)} de {n}")

    acad = df[df.group == "academico"]["duplication_pct_k100"]
    ctrl = df[df.group == "control"]["duplication_pct_k100"]
    stat, p = mannwhitneyu(acad, ctrl, alternative="two-sided")
    delta = cliffs_delta(acad, ctrl)

    summary = pd.DataFrame([{
        "metric": "jscpd duplication %% (min-tokens=100, matching SonarQube's typical Java threshold)",
        "n_academico": len(acad), "n_control": len(ctrl),
        "median_academico": acad.median(), "median_control": ctrl.median(),
        "iqr_academico": f"{acad.quantile(.25):.2f}--{acad.quantile(.75):.2f}",
        "iqr_control": f"{ctrl.quantile(.25):.2f}--{ctrl.quantile(.75):.2f}",
        "cliffs_delta": delta, "mannwhitney_u": stat, "p_value": p,
    }])
    print(summary.to_string(index=False))
    summary.to_csv(RESULTS_DIR / "jscpd_k100_resumen.csv", index=False)
    print(f"\nCompletado: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
