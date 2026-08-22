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

    return app