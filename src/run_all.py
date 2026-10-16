"""Ejecuta el pipeline completo con un solo comando y deja registro en results/logs/.

    python src/run_all.py              # corre todos los scripts NN_*.py en orden
    python src/run_all.py --from 04    # retoma desde el script 04 (p. ej. sin re-descargar)
    python src/run_all.py --env-only   # solo registra versiones de librerias

Cada corrida escribe results/logs/run_<fecha>.log con la version de Python, la
version instalada de cada paquete de requirements.txt y el tiempo de cada script.
"""
import argparse
import datetime as dt
import importlib.metadata as md
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
LOG_DIR = ROOT / "results" / "logs"


def environment_lines():
    lines = [f"python {sys.version.split()[0]} ({platform.platform()})"]
    req = ROOT / "requirements.txt"
    for raw in req.read_text(encoding="utf-8").splitlines():
        name = re.split(r"[<>=!~\[ ]", raw.strip())[0]
        if not name or name.startswith("#"):
            continue
        try:
            lines.append(f"{name}=={md.version(name)}")
        except md.PackageNotFoundError:
            lines.append(f"{name}: NO INSTALADO")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", default="")
    ap.add_argument("--env-only", action="store_true")
    a = ap.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / (f"environment_{stamp}.log" if a.env_only else f"run_{stamp}.log")
    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"# {ROOT.name} - {dt.datetime.now().isoformat(timespec='seconds')}\n\n## Entorno\n")
        log.write("\n".join(environment_lines()) + "\n")
        if a.env_only:
            print(f"Entorno registrado en {log_path}")
            return
        scripts = sorted(p for p in SRC.glob("[0-9][0-9]*.py") if p.name >= a.start)
        log.write("\n## Scripts\n")
        total = time.time()
        for s in scripts:
            t0 = time.time()
            print(f"==> {s.name}")
            r = subprocess.run([sys.executable, str(s)], cwd=SRC)
            secs = time.time() - t0
            log.write(f"{s.name}\t{'OK' if r.returncode == 0 else 'ERROR ' + str(r.returncode)}\t{secs:.1f} s\n")
            log.flush()
            if r.returncode != 0:
                print(f"Fallo {s.name}; ver {log_path}")
                sys.exit(r.returncode)
        log.write(f"\nTotal: {time.time() - total:.1f} s\n")
    print(f"Pipeline completo. Registro: {log_path}")


if __name__ == "__main__":
    main()
