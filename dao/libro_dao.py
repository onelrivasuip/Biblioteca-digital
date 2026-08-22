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