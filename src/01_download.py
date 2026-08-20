"""
P9 - Deuda tecnica en software academico latinoamericano
01_download.py

Estrategia de identificacion (ficha tecnica, seccion 3):
  1. Repositorios con nombre/descripcion que indiquen trabajo academico
     (tesis, proyecto integrador, trabajo de titulacion, nombres de
     materias) -- via GitHub Search API.
  2. Cruce con afiliacion latinoamericana: se revisa el campo
     "location" de los principales colaboradores de cada repo
     candidato contra una lista de paises/ciudades de la region.
  3. Filtros: lenguaje (Java, Python, JavaScript), tamano minimo,
     al menos 10 commits.
  4. Muestra de control pareada: repos NO academicos del mismo
     lenguaje y rango de tamano, elegidos al azar.

Objetivo: 300 + 300 (si no se llega, se reporta el numero real --
ficha, seccion 8, riesgo "Pocos repositorios identificables").

Requiere GITHUB_TOKEN en un archivo .env en la raiz del proyecto
(no se versiona -- ver .gitignore).
"""

import argparse
import json
import os
import random
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
ENV_PATH = ROOT / ".env"

LANGUAGES = ["Java", "Python", "JavaScript"]
ACADEMIC_KEYWORDS = [
    "tesis", "trabajo-de-titulacion", "trabajo de titulacion",
    "proyecto-integrador", "proyecto integrador", "trabajo-de-grado",
    "trabalho de conclusao", "tcc", "proyecto-final", "proyecto final",
]
LATAM_LOCATION_HINTS = [
    "argentina", "bolivia", "brazil", "brasil", "chile", "colombia",
    "costa rica", "cuba", "ecuador", "el salvador", "guatemala",
    "honduras", "mexico", "méxico", "nicaragua", "panama", "panamá",
    "paraguay", "peru", "perú", "uruguay", "venezuela",
    "quito", "guayaquil", "cuenca", "bogota", "bogotá", "lima",
    "santiago", "buenos aires", "sao paulo", "são paulo", "caracas",
    "montevideo", "asuncion", "asunción", "la paz", "espoch",
]

MIN_SIZE_KB = 200  # proxy de "> 500 lineas" (tamano del repo en KB)
MIN_COMMITS = 10
TARGET_ACADEMIC = 300
TARGET_CONTROL = 300


def load_token():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GITHUB_TOKEN no encontrado en .env")


TOKEN = load_token()
SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
})


def gh_get(url, params=None, max_retries=3):
    for attempt in range(max_retries):
        resp = SESSION.get(url, params=params, timeout=30)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - time.time(), 5)
            print(f"  Límite de tasa alcanzado, esperando {wait:.0f}s...")
            time.sleep(wait + 1)
            continue
        resp.raise_for_status()
        return resp
    raise RuntimeError(f"No se pudo completar la petición a {url} tras {max_retries} intentos")


def search_academic_candidates(languages=None, keywords=None):
    """Busca repos con indicios academicos en nombre/descripcion, por
    lenguaje y palabra clave. Devuelve una lista de full_name unicos."""
    candidates = {}
    for lang in (languages or LANGUAGES):
        for kw in (keywords or ACADEMIC_KEYWORDS):
            query = f'{kw} in:name,description language:{lang} size:>{MIN_SIZE_KB}'
            print(f"Buscando: {query}")
            for page in range(1, 4):  # hasta 300 resultados por query
                resp = gh_get(
                    "https://api.github.com/search/repositories",
                    params={"q": query, "per_page": 100, "page": page, "sort": "updated"},
                )
                items = resp.json().get("items", [])
                if not items:
                    break
                for repo in items:
                    candidates[repo["full_name"]] = repo
                time.sleep(2.1)  # respetar 30 peticiones/min de la API de busqueda
                if len(items) < 100:
                    break
    print(f"\n{len(candidates)} repositorios candidatos únicos (antes de verificar LatAm/commits)")
    return list(candidates.values())


def repo_has_latam_contributor(full_name: str) -> bool:
    try:
        resp = SESSION.get(f"https://api.github.com/repos/{full_name}/contributors", params={"per_page": 10}, timeout=30)
    except Exception:
        return False
    if resp.status_code != 200:
        return False
    for contrib in resp.json():
        if contrib.get("type") == "Bot":  # p.ej. "Copilot", "dependabot[bot]": no tienen perfil de usuario
            continue
        try:
            user_resp = SESSION.get(f"https://api.github.com/users/{contrib['login']}", timeout=30)
        except Exception:
            continue
        if user_resp.status_code != 200:
            continue
        location = (user_resp.json().get("location") or "").lower()
        if any(hint in location for hint in LATAM_LOCATION_HINTS):
            return True
        time.sleep(0.3)
    return False


def get_commit_count_estimate(full_name: str, default_branch: str) -> int:
    try:
        resp = SESSION.get(
            f"https://api.github.com/repos/{full_name}/commits",
            params={"sha": default_branch, "per_page": 1}, timeout=30,
        )
    except Exception:
        return 0
    if resp.status_code != 200:
        return 0
    link = resp.headers.get("Link", "")
    if 'rel="last"' in link:
        for part in link.split(","):
            if 'rel="last"' in part:
                last_page = int(part.split("page=")[-1].split(">")[0])
                return last_page
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Corrida chica: 1 lenguaje, 2 keywords, objetivo 5+5")
    args = parser.parse_args()

    global TARGET_ACADEMIC, TARGET_CONTROL
    langs, kws = LANGUAGES, ACADEMIC_KEYWORDS
    if args.test:
        langs, kws = ["Python"], ["tesis", "proyecto-integrador"]
        TARGET_ACADEMIC, TARGET_CONTROL = 5, 5

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    academic_out = RAW_DIR / "academic_repos.jsonl"
    control_out = RAW_DIR / "control_repos.jsonl"

    candidates = search_academic_candidates(langs, kws)
    random.Random(42).shuffle(candidates)

    # Reanudable: si ya existe una corrida previa, se cargan los que ya
    # se aceptaron y se salta a los candidatos no revisados todavia.
    academic_selected = []
    already_seen = set()
    if academic_out.exists():
        for line in academic_out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                academic_selected.append(json.loads(line))
                already_seen.add(json.loads(line)["full_name"])
        print(f"Reanudando: {len(academic_selected)} académicos ya aceptados.")

    with open(academic_out, "a" if academic_out.exists() else "w", encoding="utf-8") as f:
        for repo in candidates:
            if len(academic_selected) >= TARGET_ACADEMIC:
                break
            full_name = repo["full_name"]
            if full_name in already_seen:
                continue
            try:
                n_commits = get_commit_count_estimate(full_name, repo.get("default_branch", "main"))
                if n_commits < MIN_COMMITS:
                    continue
                if not repo_has_latam_contributor(full_name):
                    continue
            except Exception as exc:
                print(f"  (omitido por error: {full_name}: {exc})")
                continue
            record = {
                "full_name": full_name, "language": repo.get("language"),
                "size_kb": repo.get("size"), "stargazers": repo.get("stargazers_count"),
                "n_commits_estimate": n_commits, "clone_url": repo.get("clone_url"),
                "description": repo.get("description"),
            }
            academic_selected.append(record)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{len(academic_selected)}/{TARGET_ACADEMIC}] académico: {full_name}")

    print(f"\n{len(academic_selected)} repositorios académicos identificados (objetivo: {TARGET_ACADEMIC})")

    # --- Muestra de control: repos NO academicos, mismo lenguaje/tamano, al azar ---
    control_selected = []
    control_seen = set()
    if control_out.exists():
        for line in control_out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                control_selected.append(rec)
                control_seen.add(rec["full_name"])
        print(f"Reanudando control: {len(control_selected)} ya aceptados.")

    # Pareo UNO A UNO por tamano (ficha: "el pareo es lo que hace valida
    # la comparacion"). Por cada repo academico se busca un repo NO
    # academico del mismo lenguaje con tamano parecido (+/-50%),
    # ordenado por "updated" (no por estrellas -- eso sesga hacia
    # proyectos famosos y enormes tipo "java-design-patterns", que no
    # son comparables a un proyecto de curso).
    rng = random.Random(43)
    with open(control_out, "a" if control_out.exists() else "w", encoding="utf-8") as f:
        for academic in academic_selected:
            if len(control_selected) >= TARGET_CONTROL:
                break
            lang = academic.get("language")
            size = academic.get("size_kb") or MIN_SIZE_KB
            if not lang or not size:
                continue
            lo, hi = max(int(size * 0.5), 50), int(size * 1.5) + 50
            query = f"language:{lang} size:{lo}..{hi}"

            try:
                page = rng.randint(1, 3)
                resp = gh_get(
                    "https://api.github.com/search/repositories",
                    params={"q": query, "per_page": 30, "page": page, "sort": "updated"},
                )
                items = resp.json().get("items", [])
            except Exception:
                items = []
            time.sleep(2.1)

            rng.shuffle(items)
            for repo in items:
                full_name = repo["full_name"]
                if full_name in control_seen or any(full_name == a["full_name"] for a in academic_selected):
                    continue
                if any(kw.replace("-", " ") in (repo.get("description") or "").lower() for kw in ACADEMIC_KEYWORDS):
                    continue  # evitar colar academicos en el control
                record = {
                    "full_name": full_name, "language": repo.get("language"),
                    "size_kb": repo.get("size"), "stargazers": repo.get("stargazers_count"),
                    "clone_url": repo.get("clone_url"), "description": repo.get("description"),
                    "paired_with": academic["full_name"],
                }
                control_selected.append(record)
                control_seen.add(full_name)
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()
                print(f"[{len(control_selected)}/{TARGET_CONTROL}] control (pareja de {academic['full_name']}): {full_name}")
                break

    print(f"{len(control_selected)} repositorios de control identificados (objetivo: {TARGET_CONTROL})")
    print(f"\nCompletado: listas guardadas en {RAW_DIR}")


if __name__ == "__main__":
    main()
