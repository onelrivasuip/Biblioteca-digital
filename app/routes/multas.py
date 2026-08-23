"""app/routes/multas.py — Rutas de la sección Multas."""

from flask import Blueprint, flash, redirect, render_template, url_for

from dao.multa_dao import MultaDAO
from utils.excepciones import BibliotecaError
from utils.logger import get_logger

logger = get_logger(__name__)

multas_bp = Blueprint("multas", __name__, url_prefix="/multas")


@multas_bp.route("")
def index():
    """Lista las multas pendientes de pago y el total adeudado."""
    try:
        multas = MultaDAO.listar_pendientes()
        total_pendiente = MultaDAO.total_pendiente()
    except BibliotecaError as error:
        multas, total_pendiente = [], 0.0
        flash(str(error), "error")

    return render_template("multas.html", multas=multas, total_pendiente=total_pendiente)


@multas_bp.route("/<int:multa_id>/pagar", methods=["POST"])
def pagar(multa_id):
    """Marca una multa como pagada."""
    try:
        MultaDAO.marcar_pagada(multa_id)
        flash("Multa marcada como pagada.", "exito")
    except BibliotecaError as error:
        flash(str(error), "error")
    except Exception as error:
        logger.error("Error inesperado al pagar multa: %s", error, exc_info=True)
        flash("No fue posible registrar el pago. Intenta de nuevo.", "error")

    return redirect(url_for("multas.index"))
