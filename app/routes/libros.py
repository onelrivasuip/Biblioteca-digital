"""app/routes/libros.py — Rutas de la sección Libros (también la página de inicio)."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from dao.libro_dao import LibroDAO
from utils.excepciones import BibliotecaError
from utils.logger import get_logger

logger = get_logger(__name__)

libros_bp = Blueprint("libros", __name__)


@libros_bp.route("/", methods=["GET", "POST"])
def index():
    """Página de inicio: formulario para registrar un libro + inventario (con búsqueda)."""
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        isbn = request.form.get("isbn", "").strip()
        categoria = request.form.get("categoria", "").strip() or None

        if not titulo or not autor or not isbn:
            flash("Título, autor e ISBN son obligatorios.", "error")
            return redirect(url_for("libros.index"))

        try:
            LibroDAO.crear(titulo, autor, isbn, categoria)
            flash(f"«{titulo}» agregado al inventario.", "exito")
        except BibliotecaError as error:
            flash(str(error), "error")
        except Exception as error:
            logger.error("Error inesperado al crear libro: %s", error, exc_info=True)
            flash("No fue posible registrar el libro. Intenta de nuevo.", "error")

        return redirect(url_for("libros.index"))

    texto_busqueda = request.args.get("q", "").strip()
    try:
        libros = LibroDAO.buscar(texto_busqueda) if texto_busqueda else LibroDAO.listar()
    except BibliotecaError as error:
        libros = []
        flash(str(error), "error")

    return render_template("libros.html", libros=libros, texto_busqueda=texto_busqueda)


@libros_bp.route("/libros/<int:libro_id>/editar", methods=["GET", "POST"])
def editar(libro_id):
    """Muestra y procesa el formulario para editar un libro existente."""
    try:
        libro = LibroDAO.buscar_por_id(libro_id)
    except BibliotecaError as error:
        flash(str(error), "error")
        return redirect(url_for("libros.index"))

    if libro is None:
        flash("El libro solicitado no existe.", "error")
        return redirect(url_for("libros.index"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        isbn = request.form.get("isbn", "").strip()
        categoria = request.form.get("categoria", "").strip() or None

        if not titulo or not autor or not isbn:
            flash("Título, autor e ISBN son obligatorios.", "error")
            return redirect(url_for("libros.editar", libro_id=libro_id))

        try:
            LibroDAO.actualizar(libro_id, titulo, autor, isbn, categoria)
            flash("Libro actualizado correctamente.", "exito")
            return redirect(url_for("libros.index"))
        except BibliotecaError as error:
            flash(str(error), "error")
        except Exception as error:
            logger.error("Error inesperado al actualizar libro: %s", error, exc_info=True)
            flash("No fue posible actualizar el libro. Intenta de nuevo.", "error")

    return render_template("editar_libro.html", libro=libro)


@libros_bp.route("/libros/<int:libro_id>/eliminar", methods=["POST"])
def eliminar(libro_id):
    """Elimina un libro registrado (rechazado si tiene préstamos asociados)."""
    try:
        filas_eliminadas = LibroDAO.eliminar(libro_id)
        if filas_eliminadas:
            flash("Libro eliminado correctamente.", "exito")
        else:
            flash("El libro solicitado no existe.", "error")
    except BibliotecaError as error:
        flash(str(error), "error")
    except Exception as error:
        logger.error("Error inesperado al eliminar libro: %s", error, exc_info=True)
        flash("No fue posible eliminar el libro. Intenta de nuevo.", "error")

    return redirect(url_for("libros.index"))
