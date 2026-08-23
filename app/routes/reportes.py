"""app/routes/reportes.py — Rutas de la sección Reportes.

Reúne en una sola página los reportes que pide la rúbrica: préstamos
atrasados, libros más prestados y multas pendientes.
"""

from flask import Blueprint, flash, render_template

from dao.multa_dao import MultaDAO
from dao.prestamo_dao import PrestamoDAO
from utils.excepciones import BibliotecaError
from utils.logger import get_logger

logger = get_logger(__name__)

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@reportes_bp.route("")
def index():
    """Muestra los reportes: atrasados, más prestados y multas pendientes."""
    try:
        atrasados = PrestamoDAO.reporte_atrasados()
        mas_prestados = PrestamoDAO.reporte_libros_mas_prestados()
        multas_pendientes = MultaDAO.listar_pendientes()
        total_pendiente = MultaDAO.total_pendiente()
    except BibliotecaError as error:
        atrasados, mas_prestados, multas_pendientes = [], [], []
        total_pendiente = 0.0
        flash(str(error), "error")

    return render_template(
        "reportes.html",
        atrasados=atrasados,
        mas_prestados=mas_prestados,
        multas_pendientes=multas_pendientes,
        total_pendiente=total_pendiente,
    )
