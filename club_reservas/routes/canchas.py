# Esto expone las operaciones obligatorias de canchas.
from flask import Blueprint


canchas_bp = Blueprint("canchas", __name__)


@canchas_bp.get("/canchas")
def listar_canchas():
    return {"message": "GET /canchas"}, 200


@canchas_bp.post("/canchas")
def crear_cancha():
    return {"message": "POST /canchas"}, 201


@canchas_bp.get("/canchas/<int:id_cancha>")
def obtener_cancha(id_cancha):
    return {
        "message": "GET /canchas/{id}",
        "id": id_cancha
    }, 200


@canchas_bp.patch("/canchas/<int:id_cancha>")
def actualizar_cancha(id_cancha):
    return {
        "message": "PATCH /canchas/{id}",
        "id": id_cancha
    }, 200


@canchas_bp.delete("/canchas/<int:id_cancha>")
def eliminar_cancha(id_cancha):
    return "", 204


@canchas_bp.get("/canchas/disponibles")
def listar_canchas_disponibles():
    return {"message": "GET /canchas/disponibles"}, 200