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

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
RESULTS_DIR = ROOT / "results" / "tables"
ENV_PATH = ROOT / ".env"

# Paises con menos de este numero de repos se agrupan en "Other" en la
# Tabla 1 del manuscrito (ver pie de tabla); "Unresolved" (sin match de
# ubicacion) se mantiene como fila propia en vez de agruparse en "Other".
OTHER_THRESHOLD = 3

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


def build_composition_table():
    """Agrega academic_country.jsonl (un pais resuelto por repo, guardado
    arriba) en la Tabla 1 del manuscrito (pais x lenguaje, n y %). Este paso
    de agregacion nunca se habia guardado en un script versionado -- solo
    quedaba el jsonl per-repo -- asi que los numeros de la Tabla 1 no eran
    reproducibles desde el codigo hasta este agregado."""
    rows = [json.loads(l) for l in (RAW_DIR / "academic_country.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    df["country"] = df["country"].fillna("Unresolved")

    counts = df["country"].value_counts()
    # Paises con < OTHER_THRESHOLD repos van a "Other" (excepto Unresolved,
    # que queda como fila propia -- ver comentario junto a OTHER_THRESHOLD).
    small = counts[(counts < OTHER_THRESHOLD) & (counts.index != "Unresolved")].index
    df["country_grouped"] = df["country"].where(~df["country"].isin(small), "Other")

    pivot = df.pivot_table(index="country_grouped", columns="language", values="full_name",
                            aggfunc="count", fill_value=0)
    for lang in ("Java", "JavaScript", "Python"):
        if lang not in pivot.columns:
            pivot[lang] = 0
    pivot["n"] = pivot[["Java", "JavaScript", "Python"]].sum(axis=1)
    pivot["pct"] = (pivot["n"] / len(df) * 100).round(1)
    pivot = pivot.reset_index().rename(columns={"country_grouped": "country"})

    # Orden: paises individuales por n descendente, luego Other, luego
    # Unresolved al final (mismo orden que la Tabla 1 del manuscrito).
    pivot["_sort_key"] = pivot["country"].map({"Other": -1, "Unresolved": -2}).fillna(pivot["n"])
    pivot = pivot.sort_values("_sort_key", ascending=False).drop(columns="_sort_key")
    pivot = pivot[["country", "n", "pct", "Java", "JavaScript", "Python"]]

    pivot.to_csv(RESULTS_DIR / "country_composition.csv", index=False)
    print("\n=== Composicion de la muestra academica por pais y lenguaje (Tabla 1) ===")
    print(pivot.to_string(index=False))
    print(f"\nGuardado: {RESULTS_DIR / 'country_composition.csv'}")


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
    build_composition_table()


if __name__ == "__main__":
    main()
