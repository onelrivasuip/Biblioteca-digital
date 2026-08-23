from flask import Flask, flash, redirect, render_template, request, url_for

from dao.libro_dao import LibroDAO


def crear_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "biblioteca-clave-desarrollo"

    @app.route("/", methods=["GET", "POST"])
    def inicio():
        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            autor = request.form.get("autor", "").strip()
            isbn = request.form.get("isbn", "").strip()

            if not titulo or not autor or not isbn:
                flash("Todos los campos son obligatorios.", "error")
                return redirect(url_for("inicio"))

            try:
                if LibroDAO.buscar_por_isbn(isbn):
                    flash("Ya existe un libro con ese ISBN.", "error")
                    return redirect(url_for("inicio"))

                LibroDAO.crear(titulo, autor, isbn)
                flash("Libro registrado correctamente.", "exito")

            except Exception:
                flash(
                    "No fue posible registrar el libro en MySQL.",
                    "error",
                )

            return redirect(url_for("inicio"))

        try:
            libros = LibroDAO.listar()
        except Exception:
            libros = []
            flash(
                "No fue posible consultar los libros en MySQL.",
                "error",
            )

        total_libros = len(libros)
        disponibles = sum(
            1 for libro in libros if libro["disponible"]
        )
        prestados = total_libros - disponibles

        return render_template(
            "index.html",
            libros=libros,
            total_libros=total_libros,
            disponibles=disponibles,
            prestados=prestados,
            total_clientes=0,
        )

    @app.route("/libros/<int:libro_id>/editar", methods=["GET", "POST"])
    def editar_libro(libro_id):
        """Muestra y procesa el formulario para editar un libro."""
        libro = LibroDAO.buscar_por_id(libro_id)

        if libro is None:
            flash("El libro solicitado no existe.", "error")
            return redirect(url_for("inicio"))

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            autor = request.form.get("autor", "").strip()
            isbn = request.form.get("isbn", "").strip()
            categoria = request.form.get("categoria", "").strip() or None

            if not titulo or not autor or not isbn:
                flash("Título, autor e ISBN son obligatorios.", "error")
                return redirect(
                    url_for("editar_libro", libro_id=libro_id)
                )

            libro_con_isbn = LibroDAO.buscar_por_isbn(isbn)

            if (
                libro_con_isbn
                and libro_con_isbn["id"] != libro_id
            ):
                flash("Ya existe otro libro con ese ISBN.", "error")
                return redirect(
                    url_for("editar_libro", libro_id=libro_id)
                )

            try:
                LibroDAO.actualizar(
                    libro_id,
                    titulo,
                    autor,
                    isbn,
                    categoria,
                )
                flash("Libro actualizado correctamente.", "exito")
                return redirect(url_for("inicio"))
            except Exception:
                flash("No fue posible actualizar el libro.", "error")

        return render_template("editar_libro.html", libro=libro)

    @app.route("/libros/<int:libro_id>/eliminar", methods=["POST"])
    def eliminar_libro(libro_id):
        """Elimina un libro registrado."""
        try:
            filas_eliminadas = LibroDAO.eliminar(libro_id)

            if filas_eliminadas:
                flash("Libro eliminado correctamente.", "exito")
            else:
                flash("El libro solicitado no existe.", "error")

        except Exception:
            flash(
                "No fue posible eliminar el libro. "
                "Puede tener préstamos asociados.",
                "error",
            )

        return redirect(url_for("inicio"))
    return app