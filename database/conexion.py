"""
database/conexion.py

Abre una conexión con MySQL usando las credenciales del archivo .env
(ver .env.example). No se comparte una sola conexión global entre requests:
cada función de DAO pide su propia conexión con obtener_conexion() y la
cierra al terminar (Flask puede atender varias peticiones a la vez, así que
una conexión global se prestaría a condiciones de carrera).
"""

import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

from utils.excepciones import BibliotecaError
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


class ConexionError(BibliotecaError):
    """No se pudo conectar a la base de datos MySQL."""


def obtener_conexion():
    """Crea y devuelve una conexión nueva con MySQL, usando las variables
    de entorno DB_HOST, DB_PORT, DB_USER, DB_PASSWORD y DB_NAME.

    Raises:
        ConexionError: si no fue posible conectar (servidor apagado,
            credenciales incorrectas, base de datos inexistente, etc.).
    """
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "biblioteca_digital"),
            # Charset explícito: evita que los acentos (á, é, í, ó, ú, ñ) se
            # guarden mal si la terminal o el cliente usa otra codificación.
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
        )
    except Error as error:
        logger.error("No se pudo conectar a MySQL: %s", error, exc_info=True)
        raise ConexionError(
            "No fue posible conectar con la base de datos. Verifica que MySQL "
            "esté corriendo y que las credenciales en tu archivo .env sean correctas."
        ) from error
