"""
app/__init__.py

Application factory de Flask: crea la app, la configura y registra cada
sección (Libros, Clientes, Préstamos, Multas, Reportes) como su propio
blueprint — así cada archivo de rutas se puede leer y mantener por separado
en vez de tener todas las rutas mezcladas en un solo módulo.
"""

import os

from flask import Flask
from dotenv import load_dotenv

from dao.libro_dao import LibroDAO
from dao.multa_dao import MultaDAO
from dao.usuario_dao import UsuarioDAO
from dao.prestamo_dao import PrestamoDAO
from utils.excepciones import BibliotecaError
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


def crear_app():
    """Crea y configura la aplicación Flask (application factory)."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "biblioteca-clave-desarrollo")

    from app.routes.libros import libros_bp
    from app.routes.clientes import clientes_bp
    from app.routes.prestamos import prestamos_bp
    from app.routes.multas import multas_bp
    from app.routes.reportes import reportes_bp

    app.register_blueprint(libros_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(prestamos_bp)
    app.register_blueprint(multas_bp)
    app.register_blueprint(reportes_bp)

    @app.context_processor
    def inyectar_resumen():
        """Calcula las estadísticas de la barra superior en cada request, para
        que todas las plantillas (que extienden base.html) las tengan
        disponibles sin que cada ruta tenga que pasarlas a mano."""
        try:
            total_libros, disponibles, prestados = LibroDAO.contar_por_disponibilidad()
            return {
                "resumen": {
                    "total_libros": total_libros,
                    "disponibles": disponibles,
                    "prestados": prestados,
                    "total_usuarios": UsuarioDAO.contar(),
                    "prestamos_activos": PrestamoDAO.contar_activos(),
                    "multas_pendientes": MultaDAO.total_pendiente(),
                }
            }
        except BibliotecaError as error:
            logger.error("No se pudo calcular el resumen de estadísticas: %s", error)
            return {"resumen": None}

    @app.errorhandler(404)
    def pagina_no_encontrada(_error):
        """Página de error 404 simple (evita el traceback genérico de Flask)."""
        return "Página no encontrada.", 404

    @app.errorhandler(500)
    def error_interno(error):
        """Registra el error interno en el log y muestra un mensaje genérico."""
        logger.error("Error interno no manejado: %s", error, exc_info=True)
        return "Ocurrió un error interno. Revisa logs/app.log para más detalle.", 500

    return app
