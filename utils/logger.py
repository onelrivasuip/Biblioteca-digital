"""
utils/logger.py

Configura un logger compartido por toda la aplicación que escribe a
logs/app.log además de a la consola. Cualquier módulo que necesite
registrar un evento o un error debe hacer:

    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("...")
    logger.error("...", exc_info=True)
"""

import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

_configurado = False


def _configurar_logging_raiz():
    """Configura el logger raíz una sola vez, aunque get_logger() se llame
    muchas veces desde distintos módulos."""
    global _configurado
    if _configurado:
        return

    os.makedirs(LOG_DIR, exist_ok=True)

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    manejador_archivo = logging.FileHandler(LOG_FILE, encoding="utf-8")
    manejador_archivo.setFormatter(formato)
    manejador_archivo.setLevel(logging.INFO)

    manejador_consola = logging.StreamHandler()
    manejador_consola.setFormatter(formato)
    manejador_consola.setLevel(logging.WARNING)

    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    raiz.addHandler(manejador_archivo)
    raiz.addHandler(manejador_consola)

    _configurado = True


def get_logger(nombre: str) -> logging.Logger:
    """Devuelve un logger configurado para escribir en logs/app.log.

    Args:
        nombre: normalmente __name__ del módulo que llama.
    """
    _configurar_logging_raiz()
    return logging.getLogger(nombre)
