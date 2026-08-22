from flask import Flask


def crear_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)

    @app.route("/")
    def inicio():
        return "<h1>Biblioteca Digital</h1><p>Aplicación Flask funcionando correctamente.</p>"

    return app