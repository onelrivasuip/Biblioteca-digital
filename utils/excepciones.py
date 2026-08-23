"""
utils/excepciones.py

Excepciones propias del dominio de la aplicación. En vez de dejar que las
rutas de Flask atrapen `Exception` a ciegas (que oculta tanto errores de
validación como errores reales de MySQL por igual), cada DAO lanza una de
estas excepciones específicas para que las rutas sepan exactamente qué pasó
y puedan mostrar un mensaje claro al usuario.
"""


class BibliotecaError(Exception):
    """Clase base de todas las excepciones propias de la aplicación."""


class RegistroDuplicadoError(BibliotecaError):
    """Ya existe un registro con ese identificador único (ISBN, cédula, etc.)."""


class RegistroNoEncontradoError(BibliotecaError):
    """No existe ningún registro con el id indicado."""


class LibroNoDisponibleError(BibliotecaError):
    """Se intentó prestar un libro que ya está prestado."""


class OperacionNoPermitidaError(BibliotecaError):
    """La operación no se puede completar por una regla de negocio (p. ej.
    borrar un libro o usuario que ya tiene préstamos registrados)."""
