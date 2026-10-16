"""Configuracion de SonarQube compartida por 03c, 03d y 03e.

El token NO va en el codigo: se lee de la variable de entorno SONAR_TOKEN o
de la linea SONAR_TOKEN=... del archivo .env en la raiz del proyecto (ignorado
por git). Ver .env.example.
"""

import os
from pathlib import Path

SONAR_URL = os.environ.get("SONAR_URL", "http://localhost:9000")
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_sonar_token() -> str:
    token = os.environ.get("SONAR_TOKEN")
    if token:
        return token
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if line.startswith("SONAR_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("SONAR_TOKEN no definido (variable de entorno o archivo .env)")
