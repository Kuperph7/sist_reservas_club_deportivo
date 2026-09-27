from urllib.parse import urlencode

from flask import Blueprint, jsonify, request

from club_reservas.db import engine
from club_reservas.services.canchas import (
    actualizar_cancha as actualizar_cancha_service,
    borrar_cancha,
    consultar_disponibilidad,
    crear_cancha as crear_cancha_service,
    get_cancha,
    list_canchas,
)
from club_reservas.validators.canchas import (
    validate_availability,
    validate_create,
    validate_list,
    validate_update,
)
from club_reservas.validators.common import require_json_object


canchas_bp = Blueprint("canchas", __name__)


def _pagination_links(filters):
    total = filters["_total"]
    limit = filters["_limit"]
    offset = filters["_offset"]
    last_offset = 0 if total == 0 else ((total - 1) // limit) * limit
    params = request.args.to_dict(flat=True)

    def link(page_offset):
        query = urlencode({**params, "_offset": page_offset, "_limit": limit})
        return {"href": f"{request.base_url}?{query}"}

    links = {
        "_first": link(0),
        "_last": link(last_offset),
    }
    if offset > 0:
        links["_prev"] = link(max(0, offset - limit))
    if offset + limit < total:
        links["_next"] = link(offset + limit)

    return links


@canchas_bp.get("/canchas")
def listar_canchas():
    connection = engine.connect()
    try:
        filters = validate_list(request.args)
        canchas, total = list_canchas(connection, filters)
        links = _pagination_links({**filters, "_total": total})
        return jsonify({"canchas": canchas, "_links": links}), 200
    finally:
        connection.close()


@canchas_bp.post("/canchas")
def crear_cancha():
    connection = engine.connect()
    try:
        data = validate_create(require_json_object(request))
        crear_cancha_service(
            connection,
            data["nombre"],
            data["id_deporte"],
            data["precio_hora"],
            data["activa"],
            data["techada"],
        )
        return "", 201
    finally:
        connection.close()


@canchas_bp.get("/canchas/<int:id_cancha>")
def obtener_cancha(id_cancha):
    connection = engine.connect()
    try:
        cancha = get_cancha(connection, id_cancha)
        return jsonify(cancha), 200
    finally:
        connection.close()


@canchas_bp.patch("/canchas/<int:id_cancha>")
def actualizar_cancha(id_cancha):
    connection = engine.connect()
    try:
        data = validate_update(require_json_object(request))
        actualizar_cancha_service(connection, id_cancha, data)
        return "", 204
    finally:
        connection.close()


@canchas_bp.delete("/canchas/<int:id_cancha>")
def eliminar_cancha(id_cancha):
    connection = engine.connect()
    try:
        borrar_cancha(connection, id_cancha)
        return "", 204
    finally:
        connection.close()


@canchas_bp.get("/canchas/disponibles")
def listar_canchas_disponibles():
    connection = engine.connect()
    try:
        filters = validate_availability(request.args)
        canchas, total = consultar_disponibilidad(connection, filters)
        links = _pagination_links({**filters, "_total": total})
        return jsonify({"canchas": canchas, "_links": links}), 200
    finally:
        connection.close()
