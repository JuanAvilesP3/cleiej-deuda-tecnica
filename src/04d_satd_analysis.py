"""
P9 - Deuda tecnica en software academico latinoamericano
04d_satd_analysis.py

Deuda tecnica auto-declarada (SATD, self-admitted technical debt):
cuenta comentarios de codigo que contienen marcadores estandar
(TODO, FIXME, HACK, XXX, BUG, "technical debt") en el subconjunto de
415 repositorios ya re-clonados para la corroboracion con SonarQube
(03b_reclone_for_sonarqube.py), normalizado por lineas de codigo no
comentario/no vacias (NCLOC, tomado de metrics_sonarqube.csv para
evitar re-contar lineas con una heuristica distinta).

Solo cubre el subconjunto de 415 repos (no los 549 de la muestra
primaria), porque los clones originales de la muestra primaria fueron
borrados para ahorrar espacio (ver Limitaciones del manuscrito) y estos
son los unicos que siguen en disco.
"""

import os
import re
import sys
import time
from pathlib import Path

import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
RESULTS_DIR = ROOT / "results" / "tables"

CODE_EXT = {".java", ".py", ".js", ".jsx", ".ts", ".tsx"}
SATD_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX|BUG)\b|technical debt|deuda t[ée]cnica", re.IGNORECASE)
SKIP_DIRS = {".git", "node_modules", "venv", "__pycache__", "build", "dist", "target",
             ".idea", ".vscode", "vendor", "bower_components", ".next", "coverage"}
MAX_FILE_BYTES = 2_000_000


def cliffs_delta(a, b):
    a, b = list(a), list(b)
    n_a, n_b = len(a), len(b)
    more = sum(1 for x in a for y in b if x > y)
    less = sum(1 for x in a for y in b if x < y)
    return (more - less) / (n_a * n_b)


def count_satd(repo_dir: Path) -> int:
    total = 0
    for dirpath, dirnames, filenames in os.walk(repo_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if Path(fname).suffix.lower() not in CODE_EXT:
                continue
            fpath = Path(dirpath) / fname
            try:
                if fpath.stat().st_size > MAX_FILE_BYTES:
                    continue
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            total += len(SATD_PATTERN.findall(text))
    return total


def main():
    sonar = pd.read_csv(RAW_DIR / "metrics_sonarqube.csv")
    sonar = sonar.dropna(subset=["ncloc"])
    sonar = sonar[sonar["ncloc"] > 0]

    rows = []
    t0 = time.time()
    n = len(sonar)
    for i, (_, row) in enumerate(sonar.iterrows(), 1):
        folder = row["full_name"].replace("/", "__")
        for group_dir_name in ("academico", "control"):
            repo_dir = RAW_DIR / "repos_sonar" / group_dir_name / folder
            if repo_dir.is_dir():
                n_satd = count_satd(repo_dir)
                rows.append({
                    "full_name": row["full_name"],
                    "group": row["group"],
                    "ncloc": row["ncloc"],
                    "n_satd": n_satd,
                    "satd_per_kloc": n_satd / (row["ncloc"] / 1000.0),
                })
                break
        if i % 25 == 0 or i == n:
            print(f"  {i}/{n} repos escaneados ({time.time()-t0:.0f}s)", flush=True)

    df = pd.DataFrame(rows)
    print(f"Repos con clon local y NCLOC valido: {len(df)} de {len(sonar)} en metrics_sonarqube.csv")
    df.to_csv(RESULTS_DIR / "satd_por_repo.csv", index=False)

    acad = df[df.group == "academico"]["satd_per_kloc"]
    ctrl = df[df.group == "control"]["satd_per_kloc"]
    n_acad = df[df.group == "academico"]["n_satd"]
    n_ctrl = df[df.group == "control"]["n_satd"]
    stat, p = mannwhitneyu(acad, ctrl, alternative="two-sided")
    delta = cliffs_delta(acad, ctrl)

    # La mediana es cero en ambos grupos (la mayoria de repos no tiene ningun
    # marcador SATD), asi que el resumen tambien reporta la proporcion de
    # repos con AL MENOS un marcador, la media (sensible a outliers, a
    # diferencia de Cliff's delta) y el maximo observado por grupo -- los
    # numeros que el manuscrito cita en la seccion 4.4 ("Self-admitted
    # technical debt") ademas de la mediana/IQR/delta/p ya calculados arriba.
    pct_al_menos_uno_acad = (n_acad >= 1).mean() * 100
    pct_al_menos_uno_ctrl = (n_ctrl >= 1).mean() * 100

    summary = pd.DataFrame([{
        "metric": "SATD comments per 1,000 lines of code",
        "n_academico": len(acad),
        "n_control": len(ctrl),
        "median_academico": acad.median(),
        "median_control": ctrl.median(),
        "iqr_academico": f"{acad.quantile(.25):.2f}--{acad.quantile(.75):.2f}",
        "iqr_control": f"{ctrl.quantile(.25):.2f}--{ctrl.quantile(.75):.2f}",
        "cliffs_delta": delta,
        "mannwhitney_u": stat,
        "p_value": p,
        "pct_con_al_menos_1_satd_academico": pct_al_menos_uno_acad,
        "pct_con_al_menos_1_satd_control": pct_al_menos_uno_ctrl,
        "media_academico": acad.mean(),
        "media_control": ctrl.mean(),
        "maximo_academico": acad.max(),
        "maximo_control": ctrl.max(),
    }])
    print(summary.to_string(index=False))
    summary.to_csv(RESULTS_DIR / "satd_resumen.csv", index=False)
    print(f"\nAl menos 1 marcador SATD: academico {pct_al_menos_uno_acad:.1f}% vs. control {pct_al_menos_uno_ctrl:.1f}%")
    print(f"Media SATD/kloc: academico {acad.mean():.2f} vs. control {ctrl.mean():.2f} "
          f"(maximo observado: academico {acad.max():.1f}, control {ctrl.max():.1f})")
    print(f"\nCompletado: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
