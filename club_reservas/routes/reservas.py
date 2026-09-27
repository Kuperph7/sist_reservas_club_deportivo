# Esto expone las operaciones obligatorias de reservas.
from flask import Blueprint, jsonify
from club_reservas.db import get_db_connection
from club_reservas.db.services import reservas as reservas_service


reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.get("/reservas")
def listar_reservas():
    return {"message": "GET /reservas"}, 200


@reservas_bp.post("/reservas")
def crear_reserva():
    connection = engine.connect()

    try:
        data = request.get_json()
        
        reserva = generar_reserva(
            connection,
            data["id_socio"],
            data["id_cancha"],
            data["fecha_hora_inicio"],
            data["fecha_hora_fin"]
        )
        return {"message": "Creado", "reserva": reserva}, 201
    
    finally:
        connection.close()
    
    
@reservas_bp.get("/reservas/<int:id_reserva>")
def obtener_reserva(id_reserva):
    connection = get_db_connection()
    try:
        reserva = reservas_service.obtener_reserva_por_id(connection, id_reserva)
        return jsonify(reserva), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        conenection.close()


@reservas_bp.put("/reservas/<int:id_reserva>/estado")
def actualizar_estado_reserva(id_reserva):

    connection = engine.connect()

    try:
        data = request.get_json()

        actualizar_estado(
            connection,
            id_reserva,
            data
        )

        return {
            "message": "Reserva actualizada",
            "id": id_reserva
        }, 200

    finally:
        connection.close()