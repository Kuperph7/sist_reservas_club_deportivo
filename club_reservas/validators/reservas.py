import re
from datetime import date, datetime

from club_reservas.validators.common import (
    parse_non_negative_integer,
    reject_unknown_fields,
    validation_error,
)


CREATE_FIELDS = {
    "id_socio",
    "id_cancha",
    "fecha_hora_inicio",
    "fecha_hora_fin",
}
LIST_FIELDS = {
    "id_socio",
    "id_cancha",
    "estado",
    "fecha_desde",
    "fecha_hasta",
    "_limit",
    "_offset",
}
ESTADOS = {"confirmada", "cancelada", "finalizada"}
DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00$"
)


def _positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        validation_error(f"El campo '{name}' debe ser un entero mayor a cero")
    return value


def _datetime_gmt3(value, name):
    if not isinstance(value, str) or not DATETIME_PATTERN.fullmatch(value):
        validation_error(
            f"El campo '{name}' debe tener formato "
            "YYYY-MM-DDTHH:MM:SS.ffffff-03:00"
        )
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f-03:00")
    except ValueError:
        validation_error(f"El campo '{name}' contiene una fecha u hora inválida")


def _date(value, name):
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        validation_error(f"El parámetro '{name}' debe tener formato YYYY-MM-DD")


def _validate_single_query_values(args):
    for name in args:
        if len(args.getlist(name)) != 1:
            validation_error(f"El parámetro '{name}' no puede repetirse")


def validate_create(data):
    reject_unknown_fields(data, CREATE_FIELDS)
    for required in CREATE_FIELDS:
        if required not in data:
            validation_error(f"Falta el campo obligatorio '{required}'")

    start = _datetime_gmt3(data["fecha_hora_inicio"], "fecha_hora_inicio")
    end = _datetime_gmt3(data["fecha_hora_fin"], "fecha_hora_fin")
    if start >= end:
        validation_error("'fecha_hora_inicio' debe ser anterior a 'fecha_hora_fin'")

    return {
        "id_socio": _positive_integer(data["id_socio"], "id_socio"),
        "id_cancha": _positive_integer(data["id_cancha"], "id_cancha"),
        "fecha_hora_inicio": start,
        "fecha_hora_fin": end,
    }


def validate_list(args):
    reject_unknown_fields(args, LIST_FIELDS)
    _validate_single_query_values(args)

    estado = args.get("estado")
    if estado is not None and estado not in ESTADOS:
        validation_error(
            "El parámetro 'estado' debe ser confirmada, cancelada o finalizada"
        )

    fecha_desde = _date(args.get("fecha_desde"), "fecha_desde")
    fecha_hasta = _date(args.get("fecha_hasta"), "fecha_hasta")
    if fecha_desde is not None and fecha_hasta is not None:
        if fecha_desde > fecha_hasta:
            validation_error("'fecha_desde' no puede ser posterior a 'fecha_hasta'")

    return {
        "id_socio": parse_non_negative_integer(
            args.get("id_socio"), "id_socio", None, 1
        ),
        "id_cancha": parse_non_negative_integer(
            args.get("id_cancha"), "id_cancha", None, 1
        ),
        "estado": estado,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "_limit": parse_non_negative_integer(
            args.get("_limit"), "_limit", 10, 1, 100
        ),
        "_offset": parse_non_negative_integer(
            args.get("_offset"), "_offset", 0, 0
        ),
    }


def validate_state(data):
    reject_unknown_fields(data, {"estado"})
    if "estado" not in data:
        validation_error("Falta el campo obligatorio 'estado'")
    if not isinstance(data["estado"], str) or data["estado"] not in ESTADOS:
        validation_error(
            "El campo 'estado' debe ser confirmada, cancelada o finalizada"
        )
    return {"estado": data["estado"]}
