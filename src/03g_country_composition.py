"""
P9 - Deuda tecnica en software academico latinoamericano
03g_country_composition.py

La ficha pide una Tabla 1 de "composicion de la muestra por pais y
lenguaje" que nunca se guardo en el pipeline original (01_download.py
solo verificaba si CUALQUIER colaborador tenia ubicacion LatAm, sin
persistir cual pais). Este script reconstruye esa informacion
re-consultando la misma API con la misma logica, esta vez guardando
el pais que hizo match en vez de descartarlo.
"""

import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
ENV_PATH = ROOT / ".env"

COUNTRY_HINTS = {
    "argentina": "Argentina", "bolivia": "Bolivia", "brazil": "Brazil", "brasil": "Brazil",
    "chile": "Chile", "colombia": "Colombia", "costa rica": "Costa Rica", "cuba": "Cuba",
    "ecuador": "Ecuador", "el salvador": "El Salvador", "guatemala": "Guatemala",
    "honduras": "Honduras", "mexico": "Mexico", "méxico": "Mexico",
    "nicaragua": "Nicaragua", "panama": "Panama", "panamá": "Panama",
    "paraguay": "Paraguay", "peru": "Peru", "perú": "Peru", "uruguay": "Uruguay",
    "venezuela": "Venezuela",
    "quito": "Ecuador", "guayaquil": "Ecuador", "cuenca": "Ecuador", "espoch": "Ecuador",
    "bogota": "Colombia", "bogotá": "Colombia",
    "lima": "Peru", "santiago": "Chile", "buenos aires": "Argentina",
    "sao paulo": "Brazil", "são paulo": "Brazil", "caracas": "Venezuela",
    "montevideo": "Uruguay", "asuncion": "Paraguay", "asunción": "Paraguay",
    "la paz": "Bolivia",
}


def load_token():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GITHUB_TOKEN no encontrado")


TOKEN = load_token()
SESSION = requests.Session()
SESSION.headers.update({"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"})


def find_country(full_name: str):
    try:
        resp = SESSION.get(f"https://api.github.com/repos/{full_name}/contributors", params={"per_page": 10}, timeout=30)
    except Exception:
        return None
    if resp.status_code != 200:
        return None
    for contrib in resp.json():
        if contrib.get("type") == "Bot":
            continue
        try:
            user_resp = SESSION.get(f"https://api.github.com/users/{contrib['login']}", timeout=30)
        except Exception:
            continue
        if user_resp.status_code != 200:
            continue
        location = (user_resp.json().get("location") or "").lower()
        for hint, country in COUNTRY_HINTS.items():
            if hint in location:
                return country
        time.sleep(0.2)
    return None


def main():
    repos = [json.loads(l) for l in (RAW_DIR / "academic_repos.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    out_path = RAW_DIR / "academic_country.jsonl"
    already = set()
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                already.add(json.loads(line)["full_name"])
        print(f"reanudando: {len(already)} ya resueltos")

    pending = [r for r in repos if r["full_name"] not in already]
    with open(out_path, "a", encoding="utf-8") as f:
        for i, r in enumerate(pending, 1):
            country = find_country(r["full_name"])
            f.write(json.dumps({"full_name": r["full_name"], "language": r.get("language"), "country": country}) + "\n")
            f.flush()
            print(f"[{i}/{len(pending)}] {r['full_name']}: {country}", flush=True)

    print("\nCompletado.")


if __name__ == "__main__":
    main()
