"""dao/multa_dao.py — Acceso a datos de la tabla `multas`.

Las multas se generan automáticamente desde PrestamoDAO.devolver() cuando un
préstamo se devuelve tarde; esta clase no expone un método para crearlas a
mano desde las rutas de Flask.
"""

from database.conexion import obtener_conexion
from utils.excepciones import RegistroNoEncontradoError
from utils.logger import get_logger

logger = get_logger(__name__)

_SELECT_BASE = """
    SELECT
        m.id, m.dias_atraso, m.monto, m.pagada, m.fecha_generacion,
        p.id AS prestamo_id, l.titulo AS libro_titulo,
        CONCAT(u.nombre, ' ', u.apellido) AS usuario_nombre
    FROM multas m
    INNER JOIN prestamos p ON m.prestamo_id = p.id
    INNER JOIN libros l ON l.id = p.libro_id
    INNER JOIN usuarios u ON u.id = p.usuario_id
"""


class MultaDAO:
    """Gestiona las multas de la biblioteca."""

    @staticmethod
    def listar():
        """Devuelve el historial completo de multas, más recientes primero."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(_SELECT_BASE + " ORDER BY m.id DESC")
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def listar_pendientes():
        """Devuelve las multas que todavía no se han pagado."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(_SELECT_BASE + " WHERE m.pagada = FALSE ORDER BY m.fecha_generacion")
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(prestamo_id, dias_atraso, monto):
        """Registra una multa nueva asociada a un préstamo y devuelve su id."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO multas (prestamo_id, dias_atraso, monto)
                VALUES (%s, %s, %s)
                """,
                (prestamo_id, dias_atraso, monto),
            )
            conexion.commit()
            logger.info("Multa creada: prestamo_id=%s dias_atraso=%s monto=%s",
                        prestamo_id, dias_atraso, monto)
            return cursor.lastrowid
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def marcar_pagada(multa_id):
        """Marca una multa como pagada.

        Raises:
            RegistroNoEncontradoError: si el id no existe.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("UPDATE multas SET pagada = TRUE WHERE id = %s", (multa_id,))
            conexion.commit()
            if cursor.rowcount == 0:
                raise RegistroNoEncontradoError(f"No existe una multa con id={multa_id}.")
            logger.info("Multa marcada como pagada: id=%s", multa_id)
            return cursor.rowcount
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def total_pendiente():
        """Suma el monto de todas las multas todavía no pagadas."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM multas WHERE pagada = FALSE")
            return float(cursor.fetchone()[0])
        finally:
            cursor.close()
            conexion.close()
