import mysql.connector

from club_reservas.exeptions import ApiError
from club_reservas.repositories.canchas import (
    create_cancha,
    get_cancha_by_id,
    list_all_canchas,
    update_cancha,
    consulta_disponibilidad,
    has_reservas,
    delete_cancha
)

def crear_cancha(connection, nombre, id_deporte, precio_hora, activa=True, techada=False):
    cancha_id = create_cancha(
        connection,
        nombre,
        id_deporte,
        precio_hora,
        activa,
        techada,
    )

    connection.commit
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

    canchas_normalizadas = []

    for cancha in canchas:
        canchas_normalizadas.append(
            {
                "id": cancha["id"],
                "nombre": cancha["nombre"],
                "activa": bool(cancha["activa"]),
                "id_deporte": cancha["id_deporte"],
                "techada": bool(cancha["techada"]),
                "precio_hora": cancha["precio_hora"]
            }
        )

    return canchas_normalizadas, total

def get_cancha(connection, cancha_id):
    cancha = get_cancha_by_id(connection, cancha_id)
    if cancha is None:
        raise ApiError(
            404,
            "CANCHA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una cancha con id {cancha_id}",
        )
    return {
        "id": cancha["id"],
        "nombre": cancha["nombre"],
        "activa": bool(cancha["activa"]),
        "id_deporte": cancha["id_deporte"],
        "techada": bool(cancha["techada"]),
        "precio_hora": cancha["precio_hora"]
    }

def actualizar_socio(connection, cancha_id, updates):
    cancha = get_cancha_by_id(connection, cancha_id)
    if cancha is None:
        raise ApiError(
            404,
            "CANCHA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una cancha con id {cancha_id}"
        )
    actualizaciones = update_cancha(connection, cancha_id, updates)
    connection.commit()
    return actualizaciones

def consultar_diponibilidad(connection, filters):
    canchas, total = consulta_disponibilidad(
        connection,
        filters["activa"],
        filters["id_deporte"],
        filters["fecha_hora_inicio"],
        filters["fecha_hora_fin"],
        filters["_limit"],
        filters["_offset"],
    )

    canchas_normalizadas = []

    for cancha in canchas:
        canchas_normalizadas.append(
            {
                "id": cancha["id"],
                "nombre": cancha["nombre"],
                "activa": bool(cancha["activa"]),
                "id_deporte": cancha["id_deporte"],
                "techada": bool(cancha["techada"]),
                "precio_hora": cancha["precio_hora"]
            }
        )

    return canchas_normalizadas, total

def borrar_cancha(connection, cancha_id):
    cancha = get_cancha_by_id(connection, cancha_id)
    if has_reservas(connection, cancha_id) is not None:
        raise ApiError(
            409,
            "NO_SE_PUEDE_BORRAR_LA_CANCHA",
            "Conflicto",
            f"No se puede borrar esta cancha porque tiene una reserva"
        )
    
    if cancha is None:
        raise ApiError(
            404,
            "CANCHA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una cancha con id {cancha_id}"
        )