from flask import Flask, redirect, render_template, request, url_for


def crear_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)

    libros = []

    @app.route("/", methods=["GET", "POST"])
    def inicio():
        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            autor = request.form.get("autor", "").strip()
            isbn = request.form.get("isbn", "").strip()

            if titulo and autor and isbn:
                libros.append(
                    {
                        "titulo": titulo,
                        "autor": autor,
                        "isbn": isbn,
                        "disponible": True,
                    }
                )

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