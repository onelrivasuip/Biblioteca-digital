from database.conexion import obtener_conexion


class UsuarioDAO:
    """Operaciones CRUD para usuarios."""

    @staticmethod
    def listar():
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
    def crear(
        nombre,
        apellido,
        cedula,
        correo,
    ):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO usuarios
                (
                    nombre,
                    apellido,
                    cedula,
                    correo
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    nombre,
                    apellido,
                    cedula,
                    correo,
                ),
            )

            conexion.commit()

            return cursor.lastrowid

        except Exception:
            conexion.rollback()
            raise

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def buscar_por_cedula(cedula):
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