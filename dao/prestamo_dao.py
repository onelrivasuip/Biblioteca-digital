from database.conexion import obtener_conexion


class PrestamoDAO:
    """Gestiona préstamos de libros."""

    @staticmethod
    def listar():
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    p.id,
                    u.nombre,
                    u.apellido,
                    l.titulo,
                    p.fecha_prestamo,
                    p.fecha_limite,
                    p.fecha_devolucion,
                    p.estado
                FROM prestamos p
                INNER JOIN usuarios u
                    ON p.usuario_id = u.id
                INNER JOIN libros l
                    ON p.libro_id = l.id
                ORDER BY p.id DESC
                """
            )
            return cursor.fetchall()

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(
        usuario_id,
        libro_id,
        fecha_prestamo,
        fecha_limite,
    ):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO prestamos
                (
                    usuario_id,
                    libro_id,
                    fecha_prestamo,
                    fecha_limite
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
                    usuario_id,
                    libro_id,
                    fecha_prestamo,
                    fecha_limite,
                ),
            )

            cursor.execute(
                """
                UPDATE libros
                SET disponible = FALSE
                WHERE id = %s
                """,
                (libro_id,),
            )

            conexion.commit()

            return cursor.lastrowid

        except Exception:
            conexion.rollback()
            raise

        finally:
            cursor.close()
            conexion.close()