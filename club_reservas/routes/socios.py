# Esto expone las operaciones obligatorias de socios.
from flask import Blueprint


socios_bp = Blueprint("socios", __name__)


@socios_bp.get("/socios")
def listar_socios():
    return {"message": "GET /socios"}, 200


@socios_bp.post("/socios")
def crear_socio():
    return {"message": "POST /socios"}, 201


@socios_bp.get("/socios/<int:id_socio>")
def obtener_socio(id_socio):
    return {
        "message": "GET /socios/{id}",
        "id": id_socio
    }, 200


@socios_bp.patch("/socios/<int:id_socio>")
def actualizar_socio(id_socio):
    return {
        "message": "PATCH /socios/{id}",
        "id": id_socio
    }, 200