from datetime import datetime
from club_reservas.exeptions import ApiError
from club_reservas.validators.common import require_json_object

def validate_create(data):

    if "id_socio" not in data:
        raise ApiError(
            400,
            "CAMPO_REQUERIDO",
            "Datos inválidos",
            "Falta el campo id_socio"
        )

    if "id_cancha" not in data:
        raise ApiError(
            400,
            "CAMPO_REQUERIDO",
            "Datos inválidos",
            "Falta el campo id_cancha"
        )

    if "fecha_hora_inicio" not in data:
        raise ApiError(
            400,
            "CAMPO_REQUERIDO",
            "Datos inválidos",
            "Falta el campo fecha_hora_inicio"
        )

    if "fecha_hora_fin" not in data:
        raise ApiError(
            400,
            "CAMPO_REQUERIDO",
            "Datos inválidos",
            "Falta el campo fecha_hora_fin"
        )

    try:
        fecha_hora_inicio = datetime.fromisoformat(
            data["fecha_hora_inicio"]
        )

        fecha_hora_fin = datetime.fromisoformat(
            data["fecha_hora_fin"]
        )

    except (TypeError, ValueError):
        raise ApiError(
            400,
            "FECHA_INVALIDA",
            "Datos inválidos",
            "Las fechas deben tener un formato ISO 8601 válido"
        )

    return {
        "id_socio": data["id_socio"],
        "id_cancha": data["id_cancha"],
        "fecha_hora_inicio": fecha_hora_inicio,
        "fecha_hora_fin": fecha_hora_fin
    }

def validate_update(data):
    require_json_object(data)

    if "estado" not in data:
        raise ApiError(
            400,
            "CAMPO_REQUERIDO",
            "Datos inválidos",
            "El campo estado es obligatorio"
        )

    if not isinstance(data["estado"], str):
        raise ApiError(
            400,
            "ESTADO_INVALIDO",
            "Datos inválidos",
            "El estado debe ser un texto"
        )
    
    return data