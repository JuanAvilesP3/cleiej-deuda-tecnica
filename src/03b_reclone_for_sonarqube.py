"""
P9 - Deuda tecnica en software academico latinoamericano
03b_reclone_for_sonarqube.py

Vuelve a clonar los 600 repositorios (academico + control) ya
seleccionados en academic_repos.jsonl / control_repos.jsonl, esta vez
SIN borrar los archivos al terminar -- 02_preprocess.py los borraba
para ahorrar espacio despues de extraer las metricas con
lizard/jscpd/ck, lo que dejo el proyecto sin el codigo fuente
disponible para correr SonarQube despues.

Reusa la misma logica de clonado ya validada en 02_preprocess.py
(limpieza forzada de directorios parciales, 3 reintentos, 3 workers en
paralelo -- ese valor especifico bajo la tasa de fallo por contencion
de red de ~45% a un nivel razonable, confirmado en la corrida original).
"""

import json
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = RAW_DIR / "repos_sonar"

CLONE_TIMEOUT = 60  # un poco mas generoso que el original (45s); no hay
# presion de espacio esta vez para limpiar rapido, así que preferimos
# menos fallos por timeout a costa de un poco mas de tiempo.
N_WORKERS = 3


def _force_rmtree(path: Path, attempts=3):
    for i in range(attempts):
        shutil.rmtree(path, ignore_errors=True)
        if not path.exists():
            return
        time.sleep(0.5 * (i + 1))


def clone_repo(clone_url: str, dest: Path, max_retries=3) -> bool:
    if dest.exists():
        _force_rmtree(dest)
    for attempt in range(max_retries):
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--quiet", clone_url, str(dest)],
                timeout=CLONE_TIMEOUT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
            )
            if dest.exists() and any(dest.iterdir()):
                return True
        except Exception:
            pass
        _force_rmtree(dest)
        if attempt < max_retries - 1:
            time.sleep(1.5 * (attempt + 1))
    return False


def process_group(jsonl_path: Path, group_name: str, log_path: Path):
    repos = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    group_dir = OUT_DIR / group_name
    group_dir.mkdir(parents=True, exist_ok=True)

    already_done = set()
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get("ok"):
                    already_done.add(rec["full_name"])
        print(f"[{group_name}] reanudando: {len(already_done)} ya clonados", flush=True)

    pending = [r for r in repos if r["full_name"] not in already_done]
    write_lock = threading.Lock()

    with open(log_path, "a", encoding="utf-8") as logf:
        done_count = 0
        with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
            futures = {}
            for repo in pending:
                dest = group_dir / repo["full_name"].replace("/", "__")
                futures[executor.submit(clone_repo, repo["clone_url"], dest)] = (repo, dest)

            for future in as_completed(futures):
                done_count += 1
                repo, dest = futures[future]
                try:
                    ok = future.result()
                except Exception:
                    ok = False
                with write_lock:
                    logf.write(json.dumps({"full_name": repo["full_name"], "ok": ok}) + "\n")
                    logf.flush()
                status = "OK" if ok else "FALLO"
                print(f"[{group_name} {done_count}/{len(pending)}] {status} {repo['full_name']}", flush=True)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    process_group(RAW_DIR / "academic_repos.jsonl", "academico", RAW_DIR / "reclone_log_academico.jsonl")
    process_group(RAW_DIR / "control_repos.jsonl", "control", RAW_DIR / "reclone_log_control.jsonl")
    print("\nCompletado.", flush=True)


if __name__ == "__main__":
    main()
