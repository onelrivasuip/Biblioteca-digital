"""dao/usuario_dao.py — Acceso a datos de la tabla `usuarios` (los clientes de la biblioteca)."""

from mysql.connector import Error as MySQLError
from mysql.connector import IntegrityError

from database.conexion import obtener_conexion
from utils.excepciones import OperacionNoPermitidaError, RegistroDuplicadoError
from utils.logger import get_logger

logger = get_logger(__name__)


class UsuarioDAO:
    """Operaciones CRUD para usuarios (clientes) de la biblioteca."""

    @staticmethod
    def listar():
        """Devuelve todos los usuarios registrados, más recientes primero."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM usuarios
                ORDER BY id DESC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def buscar(texto):
        """Busca usuarios por coincidencia parcial en nombre, apellido o cédula."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            patron = f"%{texto}%"
            cursor.execute(
                """
                SELECT *
                FROM usuarios
                WHERE nombre LIKE %s OR apellido LIKE %s OR cedula LIKE %s
                ORDER BY nombre, apellido
                """,
                (patron, patron, patron),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def buscar_por_id(usuario_id):
        """Busca un usuario por su identificador (o None si no existe)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def buscar_por_cedula(cedula):
        """Busca un usuario por su cédula exacta (o None si no existe)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM usuarios
                WHERE cedula = %s
                """,
                (cedula,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(nombre, apellido, cedula, correo=None):
        """Registra un usuario nuevo y devuelve su identificador.

        Raises:
            RegistroDuplicadoError: si ya existe un usuario con esa cédula
                (o ese correo, si se indicó uno).
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO usuarios
                    (nombre, apellido, cedula, correo)
                VALUES (%s, %s, %s, %s)
                """,
                (nombre, apellido, cedula, correo or None),
            )
            conexion.commit()
            logger.info("Usuario creado: id=%s cedula=%s", cursor.lastrowid, cedula)
            return cursor.lastrowid
        except IntegrityError as error:
            conexion.rollback()
            logger.warning("Intento de crear usuario con cédula/correo duplicado: %s", cedula)
            raise RegistroDuplicadoError(
                f"Ya existe un usuario con la cédula «{cedula}» (o ese correo)."
            ) from error
        except MySQLError as error:
            conexion.rollback()
            logger.error("Error al crear usuario: %s", error, exc_info=True)
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def eliminar(usuario_id):
        """Elimina un usuario por su identificador.

        Raises:
            OperacionNoPermitidaError: si el usuario tiene préstamos registrados.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
            conexion.commit()
            logger.info("Usuario eliminado: id=%s", usuario_id)
            return cursor.rowcount
        except MySQLError as error:
            conexion.rollback()
            if getattr(error, "errno", None) == 1451:
                raise OperacionNoPermitidaError(
                    "No se puede eliminar: este usuario tiene préstamos registrados."
                ) from error
            logger.error("Error al eliminar usuario: %s", error, exc_info=True)
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def contar():
        """Devuelve el total de usuarios registrados (para las estadísticas)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conexion.close()
