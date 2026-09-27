from datetime import datetime, timedelta, timezone
from decimal import Decimal

from club_reservas.exeptions import ApiError
from club_reservas.repositories.reservas import (
    create_reserva,
    get_cancha_for_update,
    get_reserva_by_id,
    get_socio_for_update,
    has_bloqueo_overlap,
    has_reserva_overlap,
    has_socio_overlap,
    list_all_reservas,
    update_reserva_state,
)


GMT_MINUS_3 = timezone(timedelta(hours=-3))


def _format_datetime(value):
    return value.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00")


def _serialize_reserva(reserva):
    return {
        "id": reserva["id"],
        "id_socio": reserva["id_socio"],
        "id_cancha": reserva["id_cancha"],
        "fecha_hora_inicio": _format_datetime(reserva["fecha_hora_inicio"]),
        "fecha_hora_fin": _format_datetime(reserva["fecha_hora_fin"]),
        "estado": reserva["estado"],
        "precio_hora": reserva["precio_hora"],
        "precio_total": reserva["precio_total"],
    }


def generar_reserva(
    connection,
    id_socio,
    id_cancha,
    fecha_hora_inicio,
    fecha_hora_fin,
):
    socio = get_socio_for_update(connection, id_socio)
    if socio is None:
        raise ApiError(
            404,
            "SOCIO_NO_ENCONTRADO",
            "Recurso no encontrado",
            f"No existe un socio con id {id_socio}",
        )
    if not socio["activo"]:
        raise ApiError(
            409,
            "SOCIO_NO_ACTIVO",
            "Conflicto de negocio",
            f"El socio con id {id_socio} no está activo",
        )

    cancha = get_cancha_for_update(connection, id_cancha)
    if cancha is None:
        raise ApiError(
            404,
            "CANCHA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una cancha con id {id_cancha}",
        )
    if not cancha["activa"]:
        raise ApiError(
            409,
            "CANCHA_NO_ACTIVA",
            "Conflicto de negocio",
            f"La cancha con id {id_cancha} no está activa",
        )

    duration = fecha_hora_fin - fecha_hora_inicio
    duration_seconds = Decimal(str(duration.total_seconds()))
    if duration_seconds < 3600 or duration_seconds > 10800:
        raise ApiError(
            409,
            "DURACION_INVALIDA",
            "Conflicto de negocio",
            "La duración de la reserva debe ser de entre 1 y 3 horas",
        )

    if has_reserva_overlap(
        connection,
        id_cancha,
        fecha_hora_inicio,
        fecha_hora_fin,
    ):
        raise ApiError(
            409,
            "CANCHA_NO_DISPONIBLE",
            "Conflicto de negocio",
            "La cancha ya tiene una reserva confirmada en ese intervalo",
        )

    if has_socio_overlap(
        connection,
        id_socio,
        fecha_hora_inicio,
        fecha_hora_fin,
    ):
        raise ApiError(
            409,
            "SOCIO_NO_DISPONIBLE",
            "Conflicto de negocio",
            "El socio ya tiene una reserva confirmada en ese intervalo",
        )

    if has_bloqueo_overlap(
        connection,
        id_cancha,
        fecha_hora_inicio,
        fecha_hora_fin,
    ):
        raise ApiError(
            409,
            "CANCHA_BLOQUEADA",
            "Conflicto de negocio",
            "La cancha tiene un bloqueo en ese intervalo",
        )

    precio_hora = cancha["precio_hora"]
    precio_total = int(Decimal(precio_hora) * duration_seconds / Decimal(3600))
    reserva_id = create_reserva(
        connection,
        id_socio,
        id_cancha,
        fecha_hora_inicio,
        fecha_hora_fin,
        precio_hora,
        precio_total,
    )
    connection.commit()

    return {
        "id": reserva_id,
        "id_socio": id_socio,
        "id_cancha": id_cancha,
        "fecha_hora_inicio": _format_datetime(fecha_hora_inicio),
        "fecha_hora_fin": _format_datetime(fecha_hora_fin),
        "estado": "confirmada",
        "precio_hora": precio_hora,
        "precio_total": precio_total,
    }


def list_reservas(connection, filters):
    reservas, total = list_all_reservas(
        connection,
        filters["id_socio"],
        filters["id_cancha"],
        filters["estado"],
        filters["fecha_desde"],
        filters["fecha_hasta"],
        filters["_limit"],
        filters["_offset"],
    )
    return [_serialize_reserva(reserva) for reserva in reservas], total


def obtener_reserva_por_id(connection, reserva_id):
    reserva = get_reserva_by_id(connection, reserva_id)
    if reserva is None:
        raise ApiError(
            404,
            "RESERVA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una reserva con id {reserva_id}",
        )
    return _serialize_reserva(reserva)


def actualizar_estado(connection, reserva_id, estado_solicitado):
    reserva = get_reserva_by_id(connection, reserva_id)
    if reserva is None:
        raise ApiError(
            404,
            "RESERVA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una reserva con id {reserva_id}",
        )

    estado_actual = reserva["estado"]
    if estado_actual == estado_solicitado:
        return 0

    if estado_actual != "confirmada" or estado_solicitado == "confirmada":
        raise ApiError(
            409,
            "TRANSICION_ESTADO_INVALIDA",
            "Conflicto de negocio",
            f"No se puede cambiar una reserva de {estado_actual} a {estado_solicitado}",
        )

    now = datetime.now(GMT_MINUS_3).replace(tzinfo=None)
    if estado_solicitado == "cancelada" and now >= reserva["fecha_hora_inicio"]:
        raise ApiError(
            409,
            "CANCELACION_NO_PERMITIDA",
            "Conflicto de negocio",
            "No se puede cancelar una reserva que ya comenzó",
        )
    if estado_solicitado == "finalizada" and now < reserva["fecha_hora_fin"]:
        raise ApiError(
            409,
            "FINALIZACION_NO_PERMITIDA",
            "Conflicto de negocio",
            "No se puede finalizar una reserva antes de que termine",
        )

    updated_rows = update_reserva_state(
        connection,
        reserva_id,
        estado_solicitado,
    )
    connection.commit()
    return updated_rows
