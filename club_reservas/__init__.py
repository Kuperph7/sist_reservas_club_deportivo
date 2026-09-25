from flask import Flask

from club_reservas.routes.deportes import deportes_bp
from club_reservas.routes.canchas import canchas_bp
from club_reservas.routes.socios import socios_bp
from club_reservas.routes.reservas import reservas_bp
from club_reservas.exeptions import register_error_handlers

def create_app():
    app = Flask(__name__)#__name__ = __init__

    app.register_blueprint(deportes_bp)
    app.register_blueprint(canchas_bp)
    app.register_blueprint(socios_bp)
    app.register_blueprint(reservas_bp)
    #Manejamos los errores despues de terminar las rutas
    register_error_handlers(app)

    return app