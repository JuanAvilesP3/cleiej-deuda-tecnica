"""
P9 - Deuda tecnica en software academico latinoamericano
03c_sonarqube_scan.py

Corre sonar-scanner contra cada uno de los repositorios re-clonados en
data/raw/repos_sonar/{academico,control}/ apuntando a un servidor
SonarQube Community local (sin Docker, instalado desde el .zip en
_shared/tools/sonarqube/, ver README para el detalle de la instalacion).

Resumible: guarda el resultado de cada repo en un .jsonl de log; si se
corta a la mitad, correrlo de nuevo retoma donde quedo (solo salta los
que ya tuvieron exito -- los que fallaron se reintentan).

GOTCHA REAL encontrado en la primera corrida (documentar si se repite
en otro proyecto): sonar-scanner.bat en Windows lanza DOS procesos
java.exe encadenados (el CLI launcher, que a su vez descarga y lanza
un segundo JRE propio para el "scanner engine" real). subprocess.run
con timeout=N solo mata el proceso .bat/cmd inmediato al vencer el
timeout -- los dos java.exe nietos quedan huerfanos corriendo para
siempre. Con varios repos en paralelo, cada timeout dejaba 2 procesos
zombis consumiendo CPU/memoria, lo que hacia mas lentos a los repos
siguientes, causando mas timeouts -- una espiral que en ~60 repos dejo
la maquina tan sobrecargada que hasta comandos como "tasklist" tardaban
minutos. Fix: usar Popen + taskkill /F /T /PID (mata el arbol completo,
no solo el proceso hijo directo) en vez de subprocess.run(timeout=).
"""

import json
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
REPOS_DIR = RAW_DIR / "repos_sonar"
TOOLS_DIR = ROOT.parent / "_shared" / "tools"

SCANNER_BAT = TOOLS_DIR / "sonar-scanner-6.2.1.4610-windows-x64" / "bin" / "sonar-scanner.bat"
JAVA21 = TOOLS_DIR / "jdk-21.0.12.1+1" / "bin" / "java.exe"
EMPTY_BINARIES = TOOLS_DIR / "empty_binaries"
EMPTY_BINARIES.mkdir(parents=True, exist_ok=True)

SONAR_URL = "http://localhost:9000"
TOKEN = "squ_018b965ee589002faa53977f1cd11fee2b3a8fac"

SCAN_TIMEOUT = 150
N_WORKERS = 2


def sanitize_key(full_name: str) -> str:
    key = "p9_" + full_name.replace("/", "__")
    return re.sub(r"[^A-Za-z0-9_.\-]", "_", key)[:400]


def kill_tree(pid: int):
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def scan_one(repo_dir: Path, project_key: str) -> bool:
    import os
    env = os.environ.copy()
    env["SONAR_SCANNER_JAVA_PATH"] = str(JAVA21)
    args = [str(SCANNER_BAT),
            f"-Dsonar.projectKey={project_key}",
            "-Dsonar.sources=.",
            f"-Dsonar.java.binaries={EMPTY_BINARIES}",
            f"-Dsonar.host.url={SONAR_URL}",
            f"-Dsonar.token={TOKEN}"]
    proc = subprocess.Popen(args, cwd=str(repo_dir), env=env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        rc = proc.wait(timeout=SCAN_TIMEOUT)
        return rc == 0
    except subprocess.TimeoutExpired:
        kill_tree(proc.pid)
        return False
    except Exception:
        kill_tree(proc.pid)
        return False


def process_group(group_name: str, log_jsonl: Path, reclone_log: Path):
    ok_repos = []
    for line in reclone_log.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            if rec.get("ok"):
                ok_repos.append(rec["full_name"])

    already_done = set()
    if log_jsonl.exists():
        for line in log_jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get("ok"):
                    already_done.add(rec["full_name"])
        print(f"[{group_name}] reanudando: {len(already_done)} ya escaneados con exito", flush=True)

    pending = [fn for fn in ok_repos if fn not in already_done]
    write_lock = threading.Lock()

    with open(log_jsonl, "a", encoding="utf-8") as logf:
        done_count = 0
        with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
            futures = {}
            for full_name in pending:
                repo_dir = REPOS_DIR / group_name / full_name.replace("/", "__")
                project_key = sanitize_key(full_name)
                futures[executor.submit(scan_one, repo_dir, project_key)] = (full_name, project_key)

            for future in as_completed(futures):
                done_count += 1
                full_name, project_key = futures[future]
                try:
                    ok = future.result()
                except Exception:
                    ok = False
                with write_lock:
                    logf.write(json.dumps({"full_name": full_name, "project_key": project_key, "ok": ok}) + "\n")
                    logf.flush()
                status = "OK" if ok else "FALLO"
                print(f"[{group_name} {done_count}/{len(pending)}] {status} {full_name}", flush=True)


def main():
    process_group("academico", RAW_DIR / "sonar_scan_log_academico.jsonl", RAW_DIR / "reclone_log_academico.jsonl")
    process_group("control", RAW_DIR / "sonar_scan_log_control.jsonl", RAW_DIR / "reclone_log_control.jsonl")
    print("\nCompletado.", flush=True)


if __name__ == "__main__":
    main()
