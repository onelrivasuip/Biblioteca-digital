"""dao/libro_dao.py — Acceso a datos de la tabla `libros`."""

from mysql.connector import Error as MySQLError
from mysql.connector import IntegrityError

from database.conexion import obtener_conexion
from utils.excepciones import OperacionNoPermitidaError, RegistroDuplicadoError
from utils.logger import get_logger

logger = get_logger(__name__)


class LibroDAO:
    """Gestiona las operaciones de libros en MySQL (siempre con SQL parametrizado)."""

    @staticmethod
    def listar():
        """Devuelve todos los libros registrados, más recientes primero."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id, titulo, autor, isbn, categoria, disponible
                FROM libros
                ORDER BY id DESC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def buscar(texto):
        """Busca libros por coincidencia parcial en título, autor o ISBN."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            patron = f"%{texto}%"
            cursor.execute(
                """
                SELECT id, titulo, autor, isbn, categoria, disponible
                FROM libros
                WHERE titulo LIKE %s OR autor LIKE %s OR isbn LIKE %s
                ORDER BY titulo
                """,
                (patron, patron, patron),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def buscar_por_isbn(isbn):
        """Busca un libro por su ISBN exacto (o None si no existe)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM libros WHERE isbn = %s",
                (isbn,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def buscar_por_id(libro_id):
        """Busca un libro por su identificador (o None si no existe)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id, titulo, autor, isbn, categoria, disponible
                FROM libros
                WHERE id = %s
                """,
                (libro_id,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def listar_disponibles():
        """Devuelve solo los libros con disponible=TRUE (para el formulario de préstamos)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id, titulo, autor, isbn
                FROM libros
                WHERE disponible = TRUE
                ORDER BY titulo
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(titulo, autor, isbn, categoria=None):
        """Registra un libro nuevo y devuelve su identificador.

        Raises:
            RegistroDuplicadoError: si ya existe un libro con ese ISBN.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO libros
                    (titulo, autor, isbn, categoria, disponible)
                VALUES (%s, %s, %s, %s, TRUE)
                """,
                (titulo, autor, isbn, categoria),
            )
            conexion.commit()
            logger.info("Libro creado: id=%s isbn=%s", cursor.lastrowid, isbn)
            return cursor.lastrowid
        except IntegrityError as error:
            conexion.rollback()
            logger.warning("Intento de crear libro con ISBN duplicado: %s", isbn)
            raise RegistroDuplicadoError(f"Ya existe un libro con el ISBN «{isbn}».") from error
        except MySQLError as error:
            conexion.rollback()
            logger.error("Error al crear libro: %s", error, exc_info=True)
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def actualizar(libro_id, titulo, autor, isbn, categoria=None):
        """Actualiza los datos de un libro existente.

        Raises:
            RegistroDuplicadoError: si el nuevo ISBN choca con otro libro.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                UPDATE libros
                SET titulo = %s,
                    autor = %s,
                    isbn = %s,
                    categoria = %s
                WHERE id = %s
                """,
                (titulo, autor, isbn, categoria, libro_id),
            )
            conexion.commit()
            logger.info("Libro actualizado: id=%s", libro_id)
            return cursor.rowcount
        except IntegrityError as error:
            conexion.rollback()
            raise RegistroDuplicadoError(f"Ya existe otro libro con el ISBN «{isbn}».") from error
        except MySQLError as error:
            conexion.rollback()
            logger.error("Error al actualizar libro: %s", error, exc_info=True)
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def actualizar_disponibilidad(libro_id, disponible):
        """Cambia solo el campo disponible de un libro (usado por PrestamoDAO)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "UPDATE libros SET disponible = %s WHERE id = %s",
                (disponible, libro_id),
            )
            conexion.commit()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def eliminar(libro_id):
        """Elimina un libro por su identificador.

        Raises:
            OperacionNoPermitidaError: si el libro tiene préstamos registrados
                (no se puede perder ese historial).
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "DELETE FROM libros WHERE id = %s",
                (libro_id,),
            )
            conexion.commit()
            logger.info("Libro eliminado: id=%s", libro_id)
            return cursor.rowcount
        except MySQLError as error:
            conexion.rollback()
            if getattr(error, "errno", None) == 1451:  # FK constraint fails
                raise OperacionNoPermitidaError(
                    "No se puede eliminar: este libro tiene préstamos registrados."
                ) from error
            logger.error("Error al eliminar libro: %s", error, exc_info=True)
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def contar_por_disponibilidad():
        """Devuelve (total, disponibles, prestados) para las tarjetas de estadísticas."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT COUNT(*), SUM(disponible) FROM libros")
            total, disponibles = cursor.fetchone()
            total = total or 0
            disponibles = int(disponibles or 0)
            return total, disponibles, total - disponibles
        finally:
            cursor.close()
            conexion.close()
