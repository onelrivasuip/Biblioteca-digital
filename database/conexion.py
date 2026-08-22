import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()


def obtener_conexion():
    """Crea y devuelve una conexión con MySQL."""
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
    except Error as error:
        raise ConnectionError(
            f"No fue posible conectar con MySQL: {error}"
        ) from error