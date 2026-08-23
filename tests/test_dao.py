"""tests/test_dao.py — Pruebas de la capa DAO contra una base de datos real.

Requieren que MySQL/MariaDB esté corriendo y que el esquema (database/schema.sql)
ya se haya importado, con las credenciales configuradas en .env (ver README).

Cada prueba crea sus propios datos con valores únicos (uuid) para no chocar
entre corridas ni con los datos de ejemplo del schema.sql, y limpia lo que
crea al terminar.
"""

import uuid

import pytest

from dao.libro_dao import LibroDAO
from dao.multa_dao import MultaDAO
from dao.prestamo_dao import PrestamoDAO
from dao.usuario_dao import UsuarioDAO
from database.conexion import obtener_conexion
from utils.excepciones import LibroNoDisponibleError, RegistroDuplicadoError


def _isbn_unico():
    """Genera un ISBN de prueba único para no chocar con datos existentes."""
    return f"TEST-{uuid.uuid4().hex[:12]}"


def _cedula_unica():
    """Genera una cédula de prueba única para no chocar con datos existentes."""
    return f"T-{uuid.uuid4().hex[:10]}"


@pytest.fixture
def libro():
    """Crea un libro de prueba y lo elimina al terminar la prueba."""
    libro_id = LibroDAO.crear("Libro de prueba", "Autor de prueba", _isbn_unico(), "Prueba")
    yield LibroDAO.buscar_por_id(libro_id)
    try:
        LibroDAO.eliminar(libro_id)
    except Exception:
        pass


@pytest.fixture
def usuario():
    """Crea un usuario de prueba y lo elimina al terminar la prueba."""
    usuario_id = UsuarioDAO.crear("Nombre", "Apellido", _cedula_unica(), None)
    yield UsuarioDAO.buscar_por_id(usuario_id)
    try:
        UsuarioDAO.eliminar(usuario_id)
    except Exception:
        pass


class TestLibroDAO:
    """Pruebas del CRUD de libros."""

    def test_crear_y_buscar_por_id(self, libro):
        """El libro recién creado se puede volver a encontrar por id."""
        assert libro is not None
        assert libro["titulo"] == "Libro de prueba"
        assert libro["disponible"] in (1, True)

    def test_isbn_duplicado_lanza_error(self, libro):
        """Crear dos libros con el mismo ISBN debe fallar con un error claro."""
        with pytest.raises(RegistroDuplicadoError):
            LibroDAO.crear("Otro título", "Otro autor", libro["isbn"])

    def test_actualizar_libro(self, libro):
        """Actualizar un libro cambia sus datos."""
        LibroDAO.actualizar(libro["id"], "Título editado", libro["autor"], libro["isbn"], None)
        actualizado = LibroDAO.buscar_por_id(libro["id"])
        assert actualizado["titulo"] == "Título editado"

    def test_buscar_coincidencia_parcial(self, libro):
        """buscar() encuentra el libro por una parte del título."""
        resultados = LibroDAO.buscar("Libro de prueba")
        assert any(fila["id"] == libro["id"] for fila in resultados)


class TestUsuarioDAO:
    """Pruebas del CRUD de usuarios."""

    def test_crear_y_buscar_por_cedula(self, usuario):
        """El usuario recién creado se puede encontrar por su cédula."""
        encontrado = UsuarioDAO.buscar_por_cedula(usuario["cedula"])
        assert encontrado is not None
        assert encontrado["id"] == usuario["id"]

    def test_cedula_duplicada_lanza_error(self, usuario):
        """Crear dos usuarios con la misma cédula debe fallar con un error claro."""
        with pytest.raises(RegistroDuplicadoError):
            UsuarioDAO.crear("Otro", "Nombre", usuario["cedula"])


class TestPrestamoDAOyMultaDAO:
    """Pruebas del flujo completo de préstamo → devolución → multa."""

    def test_prestar_y_devolver_a_tiempo_no_genera_multa(self, libro, usuario):
        """Devolver un préstamo antes de la fecha límite no genera multa."""
        prestamo_id = PrestamoDAO.crear(usuario["id"], libro["id"])

        libro_prestado = LibroDAO.buscar_por_id(libro["id"])
        assert libro_prestado["disponible"] in (0, False)

        dias_atraso, monto_multa = PrestamoDAO.devolver(prestamo_id)
        assert dias_atraso == 0
        assert monto_multa == 0.0

        libro_devuelto = LibroDAO.buscar_por_id(libro["id"])
        assert libro_devuelto["disponible"] in (1, True)

    def test_no_se_puede_prestar_libro_no_disponible(self, libro, usuario):
        """Prestar un libro ya prestado debe lanzar LibroNoDisponibleError."""
        PrestamoDAO.crear(usuario["id"], libro["id"])

        with pytest.raises(LibroNoDisponibleError):
            PrestamoDAO.crear(usuario["id"], libro["id"])

    def test_devolucion_atrasada_genera_multa(self, libro, usuario):
        """Si la fecha límite ya pasó, devolver el préstamo debe generar una multa."""
        prestamo_id = PrestamoDAO.crear(usuario["id"], libro["id"])

        # Simulamos el atraso moviendo la fecha límite al pasado directamente en la BD.
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "UPDATE prestamos SET fecha_limite = DATE_SUB(CURDATE(), INTERVAL 3 DAY) "
                "WHERE id = %s",
                (prestamo_id,),
            )
            conexion.commit()
        finally:
            cursor.close()
            conexion.close()

        dias_atraso, monto_multa = PrestamoDAO.devolver(prestamo_id)
        assert dias_atraso == 3
        assert monto_multa == pytest.approx(1.5)

        pendientes = MultaDAO.listar_pendientes()
        assert any(m["prestamo_id"] == prestamo_id for m in pendientes)
