"""
P9 - Deuda tecnica en software academico latinoamericano
03d_sonarqube_metrics.py

Extrae, via la API web de SonarQube, las metricas reales de cada
repositorio analizado con exito en 03c_sonarqube_scan.py:
  - complejidad ciclomatica y cognitiva
  - % de lineas duplicadas
  - code smells (cantidad)
  - sqale_index (indice de deuda tecnica, en minutos)
  - sqale_debt_ratio (ratio de deuda tecnica, %) -- la metrica propia
    de SonarQube que lizard/jscpd/ck no pueden reproducir
  - ncloc, clases, funciones

Ademas extrae, a nivel de toda la instancia (los 415 proyectos
analizados), el conteo de issues por tipo de regla (para la Fig. 4 que
pide la ficha: "los 10 tipos de code smell mas frecuentes").
"""

import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"

SONAR_URL = "http://localhost:9000"
TOKEN = "squ_018b965ee589002faa53977f1cd11fee2b3a8fac"

METRIC_KEYS = ("complexity,cognitive_complexity,duplicated_lines_density,ncloc,"
               "sqale_index,sqale_debt_ratio,code_smells,classes,functions,bugs,vulnerabilities")


def api_get(path: str, params: dict) -> dict:
    url = f"{SONAR_URL}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    import base64
    auth = base64.b64encode(f"{TOKEN}:".encode()).decode()
    req.add_header("Authorization", f"Basic {auth}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sanitize_key(full_name: str) -> str:
    import re
    key = "p9_" + full_name.replace("/", "__")
    return re.sub(r"[^A-Za-z0-9_.\-]", "_", key)[:400]


def get_measures(project_key: str) -> dict:
    try:
        data = api_get("/api/measures/component", {"component": project_key, "metricKeys": METRIC_KEYS})
        measures = {m["metric"]: m.get("value") for m in data.get("component", {}).get("measures", [])}
        return measures
    except Exception as e:
        print(f"  error midiendo {project_key}: {e}")
        return {}


def main():
    rows = []
    for group in ("academico", "control"):
        log_path = RAW_DIR / f"sonar_scan_log_{group}.jsonl"
        seen = set()
        ok_repos = []
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get("ok") and rec["full_name"] not in seen:
                    seen.add(rec["full_name"])
                    ok_repos.append(rec["full_name"])

        print(f"[{group}] extrayendo metricas de {len(ok_repos)} repos...")
        for i, full_name in enumerate(ok_repos, 1):
            project_key = sanitize_key(full_name)
            measures = get_measures(project_key)
            row = {"full_name": full_name, "group": group, "project_key": project_key}
            row.update(measures)
            rows.append(row)
            if i % 50 == 0:
                print(f"  [{group} {i}/{len(ok_repos)}]")
            time.sleep(0.05)

    # Guardar CSV
    import csv
    fieldnames = ["full_name", "group", "project_key", "complexity", "cognitive_complexity",
                  "duplicated_lines_density", "ncloc", "sqale_index", "sqale_debt_ratio",
                  "code_smells", "classes", "functions", "bugs", "vulnerabilities"]
    out_path = RAW_DIR / "metrics_sonarqube.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    print(f"\nGuardado: {out_path} ({len(rows)} filas)")

    # Facetas de issues (tipos de code smell mas frecuentes), a nivel de toda la instancia
    print("\nExtrayendo facetas de tipos de code smell (instancia completa)...")
    facet_data = api_get("/api/issues/search", {"types": "CODE_SMELL", "facets": "rules", "ps": 1})
    rule_facet = next((f for f in facet_data.get("facets", []) if f["property"] == "rules"), None)
    smell_rows = []
    if rule_facet:
        for v in rule_facet["values"]:
            rule_key = v["val"]
            count = v["count"]
            try:
                rule_info = api_get("/api/rules/show", {"key": rule_key})
                rule_name = rule_info.get("rule", {}).get("name", rule_key)
            except Exception:
                rule_name = rule_key
            smell_rows.append({"rule_key": rule_key, "rule_name": rule_name, "count": count})
    smell_rows.sort(key=lambda r: -r["count"])

    smell_out = RAW_DIR / "sonarqube_smell_types.csv"
    with open(smell_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rule_key", "rule_name", "count"])
        writer.writeheader()
        for row in smell_rows:
            writer.writerow(row)
    print(f"Guardado: {smell_out} ({len(smell_rows)} tipos de regla distintos)")
    print("\nTop 10 tipos de code smell mas frecuentes:")
    for row in smell_rows[:10]:
        print(f"  {row['count']:>6}  {row['rule_name']}")


if __name__ == "__main__":
    main()
