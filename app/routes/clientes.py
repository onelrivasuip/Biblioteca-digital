"""app/routes/clientes.py — Rutas de la sección Clientes (usuarios de la biblioteca)."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from dao.usuario_dao import UsuarioDAO
from utils.excepciones import BibliotecaError
from utils.logger import get_logger

logger = get_logger(__name__)

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@clientes_bp.route("", methods=["GET", "POST"])
def index():
    """Formulario para registrar un cliente + lista de clientes (con búsqueda)."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        cedula = request.form.get("cedula", "").strip()
        correo = request.form.get("correo", "").strip() or None

        if not nombre or not apellido or not cedula:
            flash("Nombre, apellido y cédula son obligatorios.", "error")
            return redirect(url_for("clientes.index"))

        try:
            UsuarioDAO.crear(nombre, apellido, cedula, correo)
            flash(f"{nombre} {apellido} agregado.", "exito")
        except BibliotecaError as error:
            flash(str(error), "error")
        except Exception as error:
            logger.error("Error inesperado al crear usuario: %s", error, exc_info=True)
            flash("No fue posible registrar el cliente. Intenta de nuevo.", "error")

        return redirect(url_for("clientes.index"))

    texto_busqueda = request.args.get("q", "").strip()
    try:
        clientes = UsuarioDAO.buscar(texto_busqueda) if texto_busqueda else UsuarioDAO.listar()
    except BibliotecaError as error:
        clientes = []
        flash(str(error), "error")

    return render_template("clientes.html", clientes=clientes, texto_busqueda=texto_busqueda)


@clientes_bp.route("/<int:usuario_id>/eliminar", methods=["POST"])
def eliminar(usuario_id):
    """Elimina un cliente registrado (rechazado si tiene préstamos asociados)."""
    try:
        filas_eliminadas = UsuarioDAO.eliminar(usuario_id)
        if filas_eliminadas:
            flash("Cliente eliminado correctamente.", "exito")
        else:
            flash("El cliente solicitado no existe.", "error")
    except BibliotecaError as error:
        flash(str(error), "error")
    except Exception as error:
        logger.error("Error inesperado al eliminar usuario: %s", error, exc_info=True)
        flash("No fue posible eliminar el cliente. Intenta de nuevo.", "error")

    return redirect(url_for("clientes.index"))
