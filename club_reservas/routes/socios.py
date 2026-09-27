# Esto expone las operaciones obligatorias de socios.
from urllib.parse import urlencode

from club_reservas.db import engine

from flask import Blueprint, jsonify, request

from club_reservas.services.socios import (
    crear_socio,
    list_socios,
    get_socio,
    actualizar_socio
)
from club_reservas.validators.socios import (
    validate_create,
    validate_update,
    validate_list
)
from club_reservas.validators.common import (
    require_json_object
)

socios_bp = Blueprint("socios", __name__)



@socios_bp.get("/socios")
def listar_socios():
    connection = engine.connect()
    try:
        filters = validate_list(request.args)
        socios, total = list_socios(connection, filters)

        limit = filters["_limit"]
        offset = filters["_offset"]
        last_offset = 0 if total == 0 else ((total - 1) // limit) * limit
        params = request.args.to_dict(flat=True)

        first_params = {
            **params,
            "_offset": 0,
            "_limit": limit,
        }
        last_params = {
            **params,
            "_offset": last_offset,
            "_limit": limit,
        }

        links = {
            "_first": {
                "href": f"{request.base_url}?{urlencode(first_params)}"
            },
            "_last": {
                "href": f"{request.base_url}?{urlencode(last_params)}"
            },
        }

        if offset > 0:
            previous_params = {
                **params,
                "_offset": max(0, offset - limit),
                "_limit": limit,
            }
            links["_prev"] = {
                "href": f"{request.base_url}?{urlencode(previous_params)}"
            }

        if offset + limit < total:
            next_params = {
                **params,
                "_offset": offset + limit,
                "_limit": limit,
            }
            links["_next"] = {
                "href": f"{request.base_url}?{urlencode(next_params)}"
            }

        return jsonify({"socios": socios, "_links": links}), 200
    finally:
        connection.close()



@socios_bp.post("/socios")
def create_socio():
    connection = engine.connect()
    try:
        data = validate_create(require_json_object(request))
        socio_id = crear_socio(connection, data["nombre"], data["email"])
        return "", 201
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
def update_socio(id_socio):
    connection = engine.connect()
    try:
        data = validate_update(require_json_object(request))
        actualizar_socio(connection, id_socio, data)
        return "", 204
    finally:
        connection.close()
