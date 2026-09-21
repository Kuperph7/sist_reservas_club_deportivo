# Esto expone las operaciones obligatorias de reservas.
from flask import Blueprint


reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.get("/reservas")
def listar_reservas():
    return {"message": "GET /reservas"}, 200


@reservas_bp.post("/reservas")
def crear_reserva():
    return {"message": "POST /reservas"}, 201


@reservas_bp.get("/reservas/<int:id_reserva>")
def obtener_reserva(id_reserva):
    return {
        "message": "GET /reservas/{id}",
        "id": id_reserva
    }, 200


@reservas_bp.put("/reservas/<int:id_reserva>/estado")
def actualizar_estado_reserva(id_reserva):
    return {
        "message": "PUT /reservas/{id}/estado",
        "id": id_reserva
    }, 200