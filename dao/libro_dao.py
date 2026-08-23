from database.conexion import obtener_conexion


class LibroDAO:
    """Gestiona las operaciones de libros en MySQL."""

    @staticmethod
    def listar():
        """Devuelve todos los libros registrados."""
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
    def buscar_por_isbn(isbn):
        """Busca un libro por su ISBN."""
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
    def crear(titulo, autor, isbn, categoria=None):
        """Registra un libro nuevo y devuelve su identificador."""
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
            return cursor.lastrowid
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()
    @staticmethod
    def buscar_por_id(libro_id):
        """Busca un libro por su identificador."""
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
    def actualizar(libro_id, titulo, autor, isbn, categoria=None):
        """Actualiza los datos de un libro."""
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
            return cursor.rowcount
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def eliminar(libro_id):
        """Elimina un libro mediante su identificador."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "DELETE FROM libros WHERE id = %s",
                (libro_id,),
            )
            conexion.commit()
            return cursor.rowcount
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()