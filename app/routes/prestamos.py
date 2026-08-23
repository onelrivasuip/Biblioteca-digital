"""app/routes/prestamos.py — Rutas de la sección Préstamos."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from dao.libro_dao import LibroDAO
from dao.prestamo_dao import PrestamoDAO
from dao.usuario_dao import UsuarioDAO
from utils.excepciones import BibliotecaError
from utils.logger import get_logger

logger = get_logger(__name__)

prestamos_bp = Blueprint("prestamos", __name__, url_prefix="/prestamos")


@prestamos_bp.route("", methods=["GET", "POST"])
def index():
    """Formulario para registrar un préstamo + lista de préstamos activos."""
    if request.method == "POST":
        libro_id = request.form.get("libro_id", type=int)
        usuario_id = request.form.get("usuario_id", type=int)

        if not libro_id or not usuario_id:
            flash("Selecciona un libro disponible y un cliente.", "error")
            return redirect(url_for("prestamos.index"))

        try:
            PrestamoDAO.crear(usuario_id, libro_id)
            flash("Préstamo registrado correctamente.", "exito")
        except BibliotecaError as error:
            flash(str(error), "error")
        except Exception as error:
            logger.error("Error inesperado al registrar préstamo: %s", error, exc_info=True)
            flash("No fue posible registrar el préstamo. Intenta de nuevo.", "error")

        return redirect(url_for("prestamos.index"))

    try:
        libros_disponibles = LibroDAO.listar_disponibles()
        clientes = UsuarioDAO.listar()
        prestamos_activos = PrestamoDAO.listar_activos()
    except BibliotecaError as error:
        libros_disponibles, clientes, prestamos_activos = [], [], []
        flash(str(error), "error")

    return render_template(
        "prestamos.html",
        libros_disponibles=libros_disponibles,
        clientes=clientes,
        prestamos=prestamos_activos,
    )


@prestamos_bp.route("/<int:prestamo_id>/devolver", methods=["POST"])
def devolver(prestamo_id):
    """Marca un préstamo como devuelto; genera multa automáticamente si hay atraso."""
    try:
        dias_atraso, monto_multa = PrestamoDAO.devolver(prestamo_id)
        if dias_atraso > 0:
            flash(
                f"Devolución registrada con {dias_atraso} día(s) de atraso. "
                f"Se generó una multa de ${monto_multa:.2f}.",
                "error",
            )
        else:
            flash("Devolución registrada a tiempo, sin multa.", "exito")
    except BibliotecaError as error:
        flash(str(error), "error")
    except ValueError as error:
        flash(str(error), "error")
    except Exception as error:
        logger.error("Error inesperado al devolver préstamo: %s", error, exc_info=True)
        flash("No fue posible registrar la devolución. Intenta de nuevo.", "error")

    return redirect(url_for("prestamos.index"))
