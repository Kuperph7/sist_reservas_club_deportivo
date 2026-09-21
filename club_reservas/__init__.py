from flask import Flask

from club_reservas.routes.deportes import deportes_bp
from club_reservas.routes.canchas import canchas_bp
from club_reservas.routes.socios import socios_bp
from club_reservas.routes.reservas import reservas_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(deportes_bp)
    app.register_blueprint(canchas_bp)
    app.register_blueprint(socios_bp)
    app.register_blueprint(reservas_bp)

    return app