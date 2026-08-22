from flask import Flask, render_template


def crear_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)

    @app.route("/")
    def inicio():
        return render_template(
            "index.html",
            total_libros=0,
            disponibles=0,
            prestados=0,
            total_clientes=0,
            libros=[],
        )

    return app