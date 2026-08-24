"""
P9 - Deuda tecnica en software academico latinoamericano
03e_sonarqube_smells_by_group.py

La ficha pide la Fig. 4 como "los 10 tipos de code smell mas
frecuentes, COMPARANDO AMBOS GRUPOS" -- 03d_sonarqube_metrics.py solo
saco la distribucion global (todos los proyectos juntos). Este script
la separa por grupo (academico vs control), consultando la API de
issues en lotes (componentKeys tiene un limite practico de URL) y
sumando los conteos de cada regla a traves de los lotes.
"""

import base64
import csv
import json
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SONAR_URL = "http://localhost:9000"
TOKEN = "squ_018b965ee589002faa53977f1cd11fee2b3a8fac"
CHUNK = 40


def api_get(path: str, params: dict) -> dict:
    url = f"{SONAR_URL}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    auth = base64.b64encode(f"{TOKEN}:".encode()).decode()
    req.add_header("Authorization", f"Basic {auth}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sanitize_key(full_name: str) -> str:
    import re
    key = "p9_" + full_name.replace("/", "__")
    return re.sub(r"[^A-Za-z0-9_.\-]", "_", key)[:400]


def smell_counts_for_keys(keys: list) -> Counter:
    counter = Counter()
    for i in range(0, len(keys), CHUNK):
        chunk = keys[i:i + CHUNK]
        data = api_get("/api/issues/search", {
            "types": "CODE_SMELL", "facets": "rules", "ps": 1,
            "componentKeys": ",".join(chunk),
        })
        rule_facet = next((f for f in data.get("facets", []) if f["property"] == "rules"), None)
        if rule_facet:
            for v in rule_facet["values"]:
                counter[v["val"]] += v["count"]
    return counter


def rule_name(rule_key: str, cache: dict) -> str:
    if rule_key in cache:
        return cache[rule_key]
    try:
        info = api_get("/api/rules/show", {"key": rule_key})
        name = info.get("rule", {}).get("name", rule_key)
    except Exception:
        name = rule_key
    cache[rule_key] = name
    return name


def main():
    name_cache = {}
    group_counters = {}
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
        keys = [sanitize_key(fn) for fn in ok_repos]
        print(f"[{group}] consultando smells de {len(keys)} proyectos en lotes de {CHUNK}...")
        group_counters[group] = smell_counts_for_keys(keys)
        print(f"[{group}] {len(group_counters[group])} tipos de regla distintos, "
              f"{sum(group_counters[group].values())} issues totales")

    all_rule_keys = set(group_counters["academico"]) | set(group_counters["control"])
    rows = []
    for rk in all_rule_keys:
        rows.append({
            "rule_key": rk,
            "rule_name": rule_name(rk, name_cache),
            "count_academico": group_counters["academico"].get(rk, 0),
            "count_control": group_counters["control"].get(rk, 0),
            "count_total": group_counters["academico"].get(rk, 0) + group_counters["control"].get(rk, 0),
        })
    rows.sort(key=lambda r: -r["count_total"])

    out_path = RAW_DIR / "sonarqube_smell_types_by_group.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rule_key", "rule_name", "count_academico", "count_control", "count_total"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"\nGuardado: {out_path}")
    print("\nTop 10 combinado (academico | control):")
    for row in rows[:10]:
        print(f"  acad={row['count_academico']:>5}  ctrl={row['count_control']:>5}  {row['rule_name']}")


if __name__ == "__main__":
    main()
