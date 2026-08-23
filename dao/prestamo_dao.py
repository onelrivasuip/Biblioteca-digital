"""dao/prestamo_dao.py — Acceso a datos de la tabla `prestamos`.

Esta es la DAO más importante: conecta libros y usuarios, y aplica las
reglas de negocio de prestar/devolver dentro de una sola transacción, para
que nunca quede un libro marcado como no disponible sin su préstamo
correspondiente (o viceversa).
"""

from datetime import date, timedelta

from mysql.connector import Error as MySQLError

from config import DIAS_PRESTAMO, MULTA_POR_DIA
from dao.multa_dao import MultaDAO
from database.conexion import obtener_conexion
from utils.excepciones import LibroNoDisponibleError, RegistroNoEncontradoError
from utils.logger import get_logger

logger = get_logger(__name__)

# Consulta base reutilizada por varios métodos: trae el préstamo ya
# "enriquecido" con el título del libro y el nombre del usuario.
_SELECT_BASE = """
    SELECT
        p.id, p.usuario_id, p.libro_id,
        p.fecha_prestamo, p.fecha_limite, p.fecha_devolucion, p.estado,
        l.titulo AS libro_titulo, l.isbn AS libro_isbn,
        CONCAT(u.nombre, ' ', u.apellido) AS usuario_nombre
    FROM prestamos p
    INNER JOIN usuarios u ON p.usuario_id = u.id
    INNER JOIN libros l ON p.libro_id = l.id
"""


class PrestamoDAO:
    """Gestiona préstamos de libros: crearlos, devolverlos y reportarlos."""

    @staticmethod
    def listar():
        """Devuelve el historial completo de préstamos, más recientes primero."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(_SELECT_BASE + " ORDER BY p.id DESC")
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def listar_activos():
        """Devuelve los préstamos que todavía no se han devuelto."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                _SELECT_BASE + " WHERE p.estado = 'ACTIVO' ORDER BY p.fecha_limite"
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(usuario_id, libro_id):
        """Registra un préstamo nuevo, si el libro está disponible.

        El plazo se calcula automáticamente (DIAS_PRESTAMO en config.py).

        Raises:
            RegistroNoEncontradoError: si el libro no existe.
            LibroNoDisponibleError: si el libro ya está prestado.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # SELECT ... FOR UPDATE evita que dos usuarios presten el mismo
            # libro al mismo tiempo (bloquea la fila hasta que termine la transacción).
            cursor.execute("SELECT disponible FROM libros WHERE id = %s FOR UPDATE", (libro_id,))
            fila = cursor.fetchone()
            if fila is None:
                raise RegistroNoEncontradoError(f"No existe un libro con id={libro_id}.")
            if not fila[0]:
                raise LibroNoDisponibleError("Ese libro ya no está disponible.")

            fecha_prestamo = date.today()
            fecha_limite = fecha_prestamo + timedelta(days=DIAS_PRESTAMO)

            cursor.execute(
                """
                INSERT INTO prestamos (usuario_id, libro_id, fecha_prestamo, fecha_limite)
                VALUES (%s, %s, %s, %s)
                """,
                (usuario_id, libro_id, fecha_prestamo, fecha_limite),
            )
            prestamo_id = cursor.lastrowid

            cursor.execute("UPDATE libros SET disponible = FALSE WHERE id = %s", (libro_id,))

            conexion.commit()
            logger.info("Préstamo registrado: id=%s libro_id=%s usuario_id=%s",
                        prestamo_id, libro_id, usuario_id)
            return prestamo_id
        except MySQLError as error:
            conexion.rollback()
            logger.error("Error al registrar préstamo: %s", error, exc_info=True)
            raise
        except (RegistroNoEncontradoError, LibroNoDisponibleError):
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def devolver(prestamo_id):
        """Marca un préstamo como devuelto, libera el libro y, si hay atraso,
        genera la multa correspondiente (a través de MultaDAO).

        Returns:
            (dias_atraso, monto_multa) — (0, 0.0) si se devolvió a tiempo.

        Raises:
            RegistroNoEncontradoError: si el préstamo no existe.
            ValueError: si el préstamo ya estaba devuelto.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM prestamos WHERE id = %s FOR UPDATE", (prestamo_id,)
            )
            prestamo = cursor.fetchone()
            if prestamo is None:
                raise RegistroNoEncontradoError(f"No existe un préstamo con id={prestamo_id}.")
            if prestamo["estado"] != "ACTIVO":
                raise ValueError("Este préstamo ya fue devuelto anteriormente.")

            hoy = date.today()
            dias_atraso = max((hoy - prestamo["fecha_limite"]).days, 0)
            nuevo_estado = "DEVUELTO"

            cursor.execute(
                """
                UPDATE prestamos
                SET estado = %s, fecha_devolucion = %s
                WHERE id = %s
                """,
                (nuevo_estado, hoy, prestamo_id),
            )
            cursor.execute(
                "UPDATE libros SET disponible = TRUE WHERE id = %s", (prestamo["libro_id"],)
            )

            conexion.commit()
        except MySQLError as error:
            conexion.rollback()
            logger.error("Error al devolver préstamo: %s", error, exc_info=True)
            raise
        finally:
            cursor.close()
            conexion.close()

        monto_multa = 0.0
        if dias_atraso > 0:
            monto_multa = round(dias_atraso * MULTA_POR_DIA, 2)
            MultaDAO.crear(prestamo_id, dias_atraso, monto_multa)

        logger.info("Préstamo devuelto: id=%s dias_atraso=%s multa=%s",
                    prestamo_id, dias_atraso, monto_multa)
        return dias_atraso, monto_multa

    # ---------------------------------------------------------------------
    # Reportes
    # ---------------------------------------------------------------------

    @staticmethod
    def reporte_atrasados():
        """Reporte: préstamos activos cuya fecha límite ya pasó."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                _SELECT_BASE + """
                WHERE p.estado = 'ACTIVO' AND p.fecha_limite < CURDATE()
                ORDER BY p.fecha_limite
                """
            )
            filas = cursor.fetchall()
            for fila in filas:
                fila["dias_atraso"] = (date.today() - fila["fecha_limite"]).days
            return filas
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def reporte_libros_mas_prestados(limite=5):
        """Reporte: los libros con más préstamos históricos, de mayor a menor."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT l.titulo, l.autor, COUNT(*) AS veces_prestado
                FROM prestamos p
                INNER JOIN libros l ON l.id = p.libro_id
                GROUP BY l.id, l.titulo, l.autor
                ORDER BY veces_prestado DESC, l.titulo
                LIMIT %s
                """,
                (limite,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def contar_activos():
        """Devuelve cuántos préstamos siguen activos (para las estadísticas)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM prestamos WHERE estado = 'ACTIVO'")
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conexion.close()
