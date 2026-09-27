from urllib.parse import urlencode

from flask import Blueprint, jsonify, request

from club_reservas.db import engine
from club_reservas.services.reservas import (
    actualizar_estado,
    generar_reserva,
    list_reservas,
    obtener_reserva_por_id,
)
from club_reservas.validators.common import require_json_object
from club_reservas.validators.reservas import (
    validate_create,
    validate_list,
    validate_state,
)


reservas_bp = Blueprint("reservas", __name__)


def _pagination_links(filters, total):
    limit = filters["_limit"]
    offset = filters["_offset"]
    last_offset = 0 if total == 0 else ((total - 1) // limit) * limit
    params = request.args.to_dict(flat=True)

    def link(page_offset):
        query = urlencode({**params, "_offset": page_offset, "_limit": limit})
        return {"href": f"{request.base_url}?{query}"}

    links = {"_first": link(0), "_last": link(last_offset)}
    if offset > 0:
        links["_prev"] = link(max(0, offset - limit))
    if offset + limit < total:
        links["_next"] = link(offset + limit)
    return links


@reservas_bp.get("/reservas")
def listar_reservas():
    connection = engine.connect()
    try:
        filters = validate_list(request.args)
        reservas, total = list_reservas(connection, filters)
        links = _pagination_links(filters, total)
        return jsonify({"reservas": reservas, "_links": links}), 200
    finally:
        connection.close()


@reservas_bp.post("/reservas")
def crear_reserva():
    connection = engine.connect()
    try:
        data = validate_create(require_json_object(request))
        generar_reserva(
            connection,
            data["id_socio"],
            data["id_cancha"],
            data["fecha_hora_inicio"],
            data["fecha_hora_fin"],
        )
        return "", 201
    finally:
        connection.close()


@reservas_bp.get("/reservas/<int:id_reserva>")
def obtener_reserva(id_reserva):
    connection = engine.connect()
    try:
        reserva = obtener_reserva_por_id(connection, id_reserva)
        return jsonify(reserva), 200
    finally:
        connection.close()


@reservas_bp.put("/reservas/<int:id_reserva>/estado")
def actualizar_estado_reserva(id_reserva):
    connection = engine.connect()
    try:
        data = validate_state(require_json_object(request))
        actualizar_estado(connection, id_reserva, data["estado"])
        return "", 204
    finally:
        connection.close()
