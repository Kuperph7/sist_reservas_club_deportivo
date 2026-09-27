from flask import Blueprint, jsonify

from club_reservas.db import engine
from club_reservas.services.deportes import list_deportes


deportes_bp = Blueprint("deportes", __name__)


@deportes_bp.get("/deportes")
def listar_deportes():
    connection = engine.connect()

    try:
        deportes = list_deportes(connection)

        return jsonify(
            {
                "deportes": deportes,
            }
        ), 200

    finally:
        connection.close()