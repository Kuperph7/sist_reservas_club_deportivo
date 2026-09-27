from club_reservas.exeptions import ApiError
from club_reservas.repositories.canchas import (
    consulta_disponibilidad,
    create_cancha,
    delete_cancha,
    get_cancha_by_id,
    has_reservas,
    list_all_canchas,
    update_cancha,
)
from club_reservas.repositories.deportes import get_deporte_by_id


def _serialize_cancha(cancha):
    return {
        "id": cancha["id"],
        "nombre": cancha["nombre"],
        "activa": bool(cancha["activa"]),
        "id_deporte": cancha["id_deporte"],
        "techada": bool(cancha["techada"]),
        "precio_hora": cancha["precio_hora"],
    }


def crear_cancha(
    connection,
    nombre,
    id_deporte,
    precio_hora,
    activa=True,
    techada=False,
):
    if get_deporte_by_id(connection, id_deporte) is None:
        raise ApiError(
            404,
            "DEPORTE_NO_ENCONTRADO",
            "Recurso no encontrado",
            f"No existe un deporte con id {id_deporte}",
        )

    cancha_id = create_cancha(
        connection,
        nombre,
        id_deporte,
        precio_hora,
        activa,
        techada,
    )
    connection.commit()
    return cancha_id


def list_canchas(connection, filters):
    canchas, total = list_all_canchas(
        connection,
        filters["nombre"],
        filters["activa"],
        filters["id_deporte"],
        filters["techada"],
        filters["_limit"],
        filters["_offset"],
    )
    return [_serialize_cancha(cancha) for cancha in canchas], total


def get_cancha(connection, cancha_id):
    cancha = get_cancha_by_id(connection, cancha_id)
    if cancha is None:
        raise ApiError(
            404,
            "CANCHA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una cancha con id {cancha_id}",
        )
    return _serialize_cancha(cancha)


def actualizar_cancha(connection, cancha_id, updates):
    if get_cancha_by_id(connection, cancha_id) is None:
        raise ApiError(
            404,
            "CANCHA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una cancha con id {cancha_id}",
        )

    updated_rows = update_cancha(connection, cancha_id, updates)
    connection.commit()
    return updated_rows


def consultar_disponibilidad(connection, filters):
    canchas, total = consulta_disponibilidad(
        connection,
        filters["fecha_hora_inicio"],
        filters["fecha_hora_fin"],
        filters["id_deporte"],
        filters["techada"],
        filters["_limit"],
        filters["_offset"],
    )
    return [_serialize_cancha(cancha) for cancha in canchas], total


def borrar_cancha(connection, cancha_id):
    if get_cancha_by_id(connection, cancha_id) is None:
        raise ApiError(
            404,
            "CANCHA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una cancha con id {cancha_id}",
        )
    if has_reservas(connection, cancha_id):
        raise ApiError(
            409,
            "NO_SE_PUEDE_BORRAR_LA_CANCHA",
            "Conflicto de negocio",
            "No se puede borrar esta cancha porque tiene una reserva",
        )

    deleted_rows = delete_cancha(connection, cancha_id)
    connection.commit()
    return deleted_rows
