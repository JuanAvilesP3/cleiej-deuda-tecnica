"""
P9 - Deuda tecnica en software academico latinoamericano
02_preprocess.py

Clona cada repositorio (academico y control) y ejecuta las
herramientas de analisis estatico.

DESVIACION DOCUMENTADA respecto a la ficha tecnica (importante para el
manuscrito, seccion de metodologia/limitaciones): la ficha pide
SonarQube Community + la herramienta "ck" para las metricas. En este
entorno no hay Docker ni permisos de administrador para desplegar un
servidor SonarQube completo (inviable ademas a escala de 600
repositorios por tiempo de analisis). Se sustituye por un conjunto de
herramientas equivalentes, mas livianas y sin servidor:

  - lizard: complejidad ciclomatica y NLOC, cross-language (Java,
    Python, JavaScript). Sustituye el rol de SonarQube para la metrica
    central de la hipotesis.
  - jscpd: deteccion de codigo duplicado, cross-language.
  - ck (si, la misma herramienta de la ficha -- funciona standalone
    con un .jar, sin necesitar SonarQube; se obtuvo de Maven Central).
    Solo aplica a los repositorios en Java (es un parser especifico
    de Java): cbo, lcom, dit, wmc por clase.
  - Cobertura de pruebas: no se ejecutan los tests reales (600
    repositorios arbitrarios, la mayoria no compilarian sin ajustes
    manuales). Se usa una PROXY: proporcion de archivos que son
    archivos de prueba (por convencion de nombre), documentada como
    aproximacion, no coverage real.
"""

import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
REPOS_DIR = RAW_DIR / "repos"
TOOLS_DIR = ROOT.parent / "_shared" / "tools"

JAVA_BIN = next((TOOLS_DIR / p for p in ["jdk-17.0.20+8/bin/java.exe", "jdk-17.0.20+8/bin/java"] if (TOOLS_DIR / p).exists()), "java")
CK_JAR = TOOLS_DIR / "ck.jar"

TEST_FILE_PATTERNS = ("test_", "_test.", "test.", "tests.", ".test.", ".spec.", "Test.java", "Tests.java")
CLONE_TIMEOUT = 60
TOOL_TIMEOUT = 90


def clone_repo(clone_url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--quiet", clone_url, str(dest)],
            timeout=CLONE_TIMEOUT, capture_output=True, check=True,
        )
        return True
    except Exception:
        shutil.rmtree(dest, ignore_errors=True)
        return False


def run_lizard(repo_path: Path) -> dict:
    try:
        result = subprocess.run(
            ["lizard", str(repo_path), "-l", "java", "-l", "python", "-l", "javascript", "--csv"],
            timeout=TOOL_TIMEOUT, capture_output=True, text=True,
        )
        lines = [l for l in result.stdout.strip().split("\n") if l and not l.startswith("NLOC")]
        if not lines:
            return dict(cc_mean=None, cc_max=None, nloc_total=0, n_functions=0)
        ccns, nlocs = [], []
        for line in lines:
            parts = line.split(",")
            if len(parts) < 3:
                continue
            try:
                nlocs.append(float(parts[0]))
                ccns.append(float(parts[1]))
            except ValueError:
                continue
        if not ccns:
            return dict(cc_mean=None, cc_max=None, nloc_total=0, n_functions=0)
        return dict(
            cc_mean=sum(ccns) / len(ccns), cc_max=max(ccns),
            nloc_total=sum(nlocs), n_functions=len(ccns),
        )
    except Exception:
        return dict(cc_mean=None, cc_max=None, nloc_total=0, n_functions=0)


def run_jscpd(repo_path: Path) -> dict:
    out_dir = repo_path.parent / f"{repo_path.name}_jscpd"
    try:
        subprocess.run(
            ["jscpd", str(repo_path), "--reporters", "json", "--output", str(out_dir), "--silent"],
            timeout=TOOL_TIMEOUT, capture_output=True,
        )
        report_path = out_dir / "jscpd-report.json"
        if not report_path.exists():
            return dict(duplication_pct=0.0)
        report = json.loads(report_path.read_text(encoding="utf-8", errors="ignore"))
        pct = report.get("statistics", {}).get("total", {}).get("percentage", 0.0)
        return dict(duplication_pct=pct)
    except Exception:
        return dict(duplication_pct=None)
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def run_ck(repo_path: Path, language: str) -> dict:
    if language != "Java" or not CK_JAR.exists():
        return dict(cbo_mean=None, lcom_mean=None, dit_mean=None, wmc_mean=None)
    out_prefix = repo_path.parent / f"{repo_path.name}_ck_"
    try:
        subprocess.run(
            [str(JAVA_BIN), "-jar", str(CK_JAR), str(repo_path), "false", "0", "false", str(out_prefix)],
            timeout=TOOL_TIMEOUT, capture_output=True,
        )
        class_csv = Path(f"{out_prefix}class.csv")
        if not class_csv.exists():
            return dict(cbo_mean=None, lcom_mean=None, dit_mean=None, wmc_mean=None)
        import pandas as pd
        df = pd.read_csv(class_csv)
        return dict(
            cbo_mean=df["cbo"].mean(), lcom_mean=df["lcom"].mean(),
            dit_mean=df["dit"].mean(), wmc_mean=df["wmc"].mean(),
        )
    except Exception:
        return dict(cbo_mean=None, lcom_mean=None, dit_mean=None, wmc_mean=None)
    finally:
        for suffix in ("class.csv", "method.csv", "field.csv", "variable.csv"):
            Path(f"{out_prefix}{suffix}").unlink(missing_ok=True)


def test_file_ratio(repo_path: Path) -> float:
    all_files, test_files = 0, 0
    for f in repo_path.rglob("*"):
        if f.is_file() and f.suffix in (".java", ".py", ".js", ".ts", ".jsx", ".tsx"):
            all_files += 1
            name_lower = f.name.lower()
            if any(pat.lower() in name_lower for pat in TEST_FILE_PATTERNS):
                test_files += 1
    return test_files / all_files if all_files else 0.0


def process_group(jsonl_path: Path, group_name: str, out_path: Path):
    repos = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    group_dir = REPOS_DIR / group_name
    group_dir.mkdir(parents=True, exist_ok=True)

    already_done = set()
    if out_path.exists():
        import pandas as pd
        already_done = set(pd.read_csv(out_path)["full_name"])

    with open(out_path, "a" if out_path.exists() else "w", encoding="utf-8") as f:
        if out_path.stat().st_size == 0 if out_path.exists() else True:
            f.write("full_name,group,language,size_kb,cc_mean,cc_max,nloc_total,n_functions,"
                    "duplication_pct,test_file_ratio,cbo_mean,lcom_mean,dit_mean,wmc_mean\n")

        for i, repo in enumerate(repos):
            full_name = repo["full_name"]
            if full_name in already_done:
                continue
            dest = group_dir / full_name.replace("/", "__")

            if not clone_repo(repo["clone_url"], dest):
                print(f"[{group_name} {i+1}/{len(repos)}] clon falló: {full_name}")
                continue

            lizard_r = run_lizard(dest)
            jscpd_r = run_jscpd(dest)
            ck_r = run_ck(dest, repo.get("language", ""))
            tfr = test_file_ratio(dest)

            row = [
                full_name, group_name, repo.get("language", ""), repo.get("size_kb", ""),
                lizard_r["cc_mean"], lizard_r["cc_max"], lizard_r["nloc_total"], lizard_r["n_functions"],
                jscpd_r["duplication_pct"], tfr,
                ck_r["cbo_mean"], ck_r["lcom_mean"], ck_r["dit_mean"], ck_r["wmc_mean"],
            ]
            f.write(",".join("" if v is None else str(v) for v in row) + "\n")
            f.flush()

            shutil.rmtree(dest, ignore_errors=True)  # ahorrar espacio: ya se extrajeron las metricas
            print(f"[{group_name} {i+1}/{len(repos)}] {full_name} listo")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    process_group(RAW_DIR / "academic_repos.jsonl", "academico", RAW_DIR / "metrics_academico.csv")
    process_group(RAW_DIR / "control_repos.jsonl", "control", RAW_DIR / "metrics_control.csv")
    print("\nCompletado.")


if __name__ == "__main__":
    main()
