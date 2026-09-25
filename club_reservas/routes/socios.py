# Esto expone las operaciones obligatorias de socios.
from club_reservas.db import engine

from flask import Blueprint, jsonify, request

from club_reservas.services.socios import (
    crear_socio,
    list_socios,
    get_socio,
    update_socio
)
from club_reservas.validators.socios import (
    validate_create,
    validate_update,
    validate_list
)
from club_reservas.validators.socios import (
    require_json_object
)

socios_bp = Blueprint("socios", __name__)



@socios_bp.get("/socios")
def listar_socios():
    connection = engine.connect()
    try:
        filters = validate_list(request.args)
        socios, total = list_socios(connection, filters)
        return jsonify({"socios": socios, "total": total}), 200
    finally:
        connection.close()



@socios_bp.post("/socios")
def create_socio():
    connection = engine.connect()
    try:
        data = validate_create(require_json_object(request))
        socio_id = crear_socio(connection, data["nombre"], data["email"])
        return jsonify({"id": socio_id}), 201
    finally:
        connection.close()
    


@socios_bp.get("/socios/<int:id_socio>")
def obtener_socio(id_socio):
    connection = engine.connect()
    try:
        data = get_socio(connection, id_socio)
        return jsonify(data), 200
    finally:
        connection.close()


@socios_bp.patch("/socios/<int:id_socio>")
def actualizar_socio(id_socio):
    connection = engine.connect()
    try:
        data = validate_update(require_json_object(request))
        update_socio(connection, id_socio, data)
        return "", 204
    finally:
        connection.close()