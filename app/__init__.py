from flask import Flask, flash, redirect, render_template, request, url_for


def crear_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "biblioteca-clave-desarrollo"

    libros = []

    @app.route("/", methods=["GET", "POST"])
    def inicio():
        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            autor = request.form.get("autor", "").strip()
            isbn = request.form.get("isbn", "").strip()

            if not titulo or not autor or not isbn:
                flash("Todos los campos son obligatorios.", "error")
                return redirect(url_for("inicio"))

            isbn_duplicado = any(
                libro["isbn"].lower() == isbn.lower()
                for libro in libros
            )

            if isbn_duplicado:
                flash("Ya existe un libro con ese ISBN.", "error")
                return redirect(url_for("inicio"))

            libros.append(
                {
                    "titulo": titulo,
                    "autor": autor,
                    "isbn": isbn,
                    "disponible": True,
                }
            )

            flash("Libro registrado correctamente.", "exito")
            return redirect(url_for("inicio"))

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