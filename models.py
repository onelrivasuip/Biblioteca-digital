from __future__ import annotations

ESTADO_DISPONIBLE = "Disponible"
ESTADO_PRESTADO = "Prestado"


class Libro:
    """Representa un libro del inventario de la biblioteca."""

    def __init__(self, titulo: str, autor: str, isbn: str):
        self.titulo = titulo.strip()
        self.autor = autor.strip()
        self.isbn = isbn.strip()
        self.estado = ESTADO_DISPONIBLE
        # Cédula del cliente que actualmente tiene el libro (o None si está disponible)
        self.cliente_cedula: str | None = None

    @property
    def disponible(self) -> bool:
        return self.estado == ESTADO_DISPONIBLE

    def prestar_a(self, cedula: str) -> None:
        self.estado = ESTADO_PRESTADO
        self.cliente_cedula = cedula

    def devolver(self) -> None:
        self.estado = ESTADO_DISPONIBLE
        self.cliente_cedula = None

    def __repr__(self) -> str:  # útil para depurar
        return f"Libro(titulo={self.titulo!r}, isbn={self.isbn!r}, estado={self.estado!r})"


class Cliente:
    """Representa a un cliente/usuario registrado en la biblioteca."""

    def __init__(self, nombre: str, apellido: str, cedula: str):
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.cedula = cedula.strip()

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def __repr__(self) -> str:
        return f"Cliente(nombre_completo={self.nombre_completo!r}, cedula={self.cedula!r})"
