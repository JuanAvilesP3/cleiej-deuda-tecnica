"""
P9 - Deuda tecnica en software academico latinoamericano
03h_repo_age.py

La revision adversarial señalo una explicacion alternativa para la
menor complejidad academica que no se habia probado: los proyectos
de curso duran poco (terminan cuando termina el semestre) y el
codigo se acumula complejidad con el mantenimiento, asi que "mas
joven / menos mantenido", no "academico vs no-academico", podria
ser lo que realmente esta explicando el resultado.

Este script consulta la API de GitHub para cada repo del subconjunto
analizado (created_at, pushed_at) y calcula la vida util en dias
(pushed_at - created_at) para ambos grupos, para compararla
directamente y para correlacionarla con cc_mean.
"""

import json
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
ENV_PATH = ROOT / ".env"


def load_token():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GITHUB_TOKEN no encontrado")


TOKEN = load_token()
SESSION = requests.Session()
SESSION.headers.update({"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"})


def get_dates(full_name: str):
    try:
        resp = SESSION.get(f"https://api.github.com/repos/{full_name}", timeout=30)
    except Exception:
        return None, None
    if resp.status_code != 200:
        return None, None
    data = resp.json()
    return data.get("created_at"), data.get("pushed_at")


def main():
    ac = pd.read_csv(RAW_DIR / "metrics_academico.csv")
    co = pd.read_csv(RAW_DIR / "metrics_control.csv")
    ac["group"] = "academic"
    co["group"] = "control"
    combined = pd.concat([ac[["full_name", "group", "language", "cc_mean"]],
                           co[["full_name", "group", "language", "cc_mean"]]], ignore_index=True)

    out_path = RAW_DIR / "repo_age.jsonl"
    already = set()
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                already.add(json.loads(line)["full_name"])
        print(f"reanudando: {len(already)} ya resueltos")

    pending = combined[~combined["full_name"].isin(already)]
    with open(out_path, "a", encoding="utf-8") as f:
        for i, row in enumerate(pending.itertuples(), 1):
            created, pushed = get_dates(row.full_name)
            f.write(json.dumps({"full_name": row.full_name, "created_at": created, "pushed_at": pushed}) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"[{i}/{len(pending)}] ...", flush=True)

    print("\nCompletado.")


if __name__ == "__main__":
    main()
