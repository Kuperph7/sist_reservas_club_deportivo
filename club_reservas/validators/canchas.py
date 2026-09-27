import re
from datetime import date, datetime, time

from club_reservas.validators.common import (
    parse_boolean,
    parse_non_negative_integer,
    reject_unknown_fields,
    validation_error,
)


NAME_MAX_LENGTH = 120
CREATE_FIELDS = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
UPDATE_FIELDS = {"nombre", "precio_hora", "techada", "activa"}
LIST_FIELDS = {"nombre", "id_deporte", "techada", "activa", "_limit", "_offset"}
AVAILABILITY_FIELDS = {
    "fecha",
    "hora_inicio",
    "hora_fin",
    "id_deporte",
    "techada",
    "_limit",
    "_offset",
}
HOUR_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):00:00$")


def _validate_single_query_values(args):
    for name in args:
        if len(args.getlist(name)) != 1:
            validation_error(f"El parámetro '{name}' no puede repetirse")


def _normalize_name(value):
    if not isinstance(value, str):
        validation_error("El campo 'nombre' debe ser un string")
    normalized = value.strip()
    if not normalized:
        validation_error("El campo 'nombre' no puede quedar vacío")
    if len(normalized) > NAME_MAX_LENGTH:
        validation_error(
            f"El campo 'nombre' no puede superar los {NAME_MAX_LENGTH} caracteres"
        )
    return normalized


def _positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        validation_error(f"El campo '{name}' debe ser un entero mayor a cero")
    return value


def _boolean(value, name):
    if not isinstance(value, bool):
        validation_error(f"El campo '{name}' debe ser booleano")
    return value


def validate_create(data):
    reject_unknown_fields(data, CREATE_FIELDS)
    for required in ("nombre", "id_deporte", "precio_hora"):
        if required not in data:
            validation_error(f"Falta el campo obligatorio '{required}'")

    return {
        "nombre": _normalize_name(data["nombre"]),
        "id_deporte": _positive_integer(data["id_deporte"], "id_deporte"),
        "precio_hora": _positive_integer(data["precio_hora"], "precio_hora"),
        "techada": _boolean(data.get("techada", False), "techada"),
        "activa": _boolean(data.get("activa", True), "activa"),
    }


def validate_update(data):
    if not data:
        validation_error("El cuerpo de la actualización no puede estar vacío")
    reject_unknown_fields(data, UPDATE_FIELDS)

    normalized = {}
    if "nombre" in data:
        normalized["nombre"] = _normalize_name(data["nombre"])
    if "precio_hora" in data:
        normalized["precio_hora"] = _positive_integer(
            data["precio_hora"], "precio_hora"
        )
    if "techada" in data:
        normalized["techada"] = _boolean(data["techada"], "techada")
    if "activa" in data:
        normalized["activa"] = _boolean(data["activa"], "activa")
    return normalized


def validate_list(args):
    reject_unknown_fields(args, LIST_FIELDS)
    _validate_single_query_values(args)

    nombre = args.get("nombre")
    return {
        "nombre": nombre.strip() if nombre is not None else None,
        "id_deporte": parse_non_negative_integer(
            args.get("id_deporte"), "id_deporte", None, 1
        ),
        "techada": parse_boolean(args.get("techada"), "techada"),
        "activa": parse_boolean(args.get("activa"), "activa"),
        "_limit": parse_non_negative_integer(
            args.get("_limit"), "_limit", 10, 1, 100
        ),
        "_offset": parse_non_negative_integer(
            args.get("_offset"), "_offset", 0, 0
        ),
    }


def validate_availability(args):
    reject_unknown_fields(args, AVAILABILITY_FIELDS)
    _validate_single_query_values(args)

    for required in ("fecha", "hora_inicio", "hora_fin"):
        if args.get(required) is None:
            validation_error(f"Falta el parámetro obligatorio '{required}'")

    try:
        parsed_date = date.fromisoformat(args["fecha"])
    except (TypeError, ValueError):
        validation_error("El parámetro 'fecha' debe tener formato YYYY-MM-DD")

    for name in ("hora_inicio", "hora_fin"):
        if not HOUR_PATTERN.fullmatch(args[name]):
            validation_error(f"El parámetro '{name}' debe tener formato HH:00:00")

    start_time = time.fromisoformat(args["hora_inicio"])
    end_time = time.fromisoformat(args["hora_fin"])
    if start_time >= end_time:
        validation_error("'hora_inicio' debe ser anterior a 'hora_fin'")

    return {
        "fecha_hora_inicio": datetime.combine(parsed_date, start_time),
        "fecha_hora_fin": datetime.combine(parsed_date, end_time),
        "id_deporte": parse_non_negative_integer(
            args.get("id_deporte"), "id_deporte", None, 1
        ),
        "techada": parse_boolean(args.get("techada"), "techada"),
        "_limit": parse_non_negative_integer(
            args.get("_limit"), "_limit", 10, 1, 100
        ),
        "_offset": parse_non_negative_integer(
            args.get("_offset"), "_offset", 0, 0
        ),
    }
