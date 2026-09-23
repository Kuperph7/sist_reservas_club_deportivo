import mysql.connector

from club_reservas.exeptions import ApiError
from club_reservas.repositories.socios import (
    create_socio,
    get_socio_by_email,
    get_socio_by_id,
    list_all_socios,
    update_socio
)



def crear_socio(connection, nombre, email):
    if get_socio_by_email(connection, email) is not None:
        raise ApiError(
            409,
            "EMAIL_DUPLICADO",
            "Conflicto de negocio",
            "Ya existe un socio registrado con ese email",
        )

    socio_id = create_socio(
        connection,
        nombre,
        email,
    )

    connection.commit()
    return socio_id
    

def list_socios(connection, filters):
    socios, total = list_all_socios(
        connection,
        filters["nombre"],
        filters["activo"],
        filters["_limit"],
        filters["_offset"],
    )

    socios_normalizados = []

    for socio in socios:
        socios_normalizados.append(
            {
                "id": socio["id"],
                "nombre": socio["nombre"],
                "email": socio["email"],
                "activo": bool(socio["activo"]),
            }
        )

    return socios_normalizados, total

def get_socio(connection, socio_id):
    socio = get_socio_by_id(connection, socio_id)
    if socio is None:
        raise ApiError(
            404,
            "SOCIO_NO_ENCONTRADO",
            "Recurso no encontrado",
            f"No existe un socio con id {socio_id}",
        )
    return {
        "id": socio["id"],
        "nombre": socio["nombre"],
        "email": socio["email"],
        "activo": bool(socio["activo"]),
    }

def actualizar_socio(connection, socio_id, updates):
    socio = get_socio_by_id(connection, socio_id)
    if socio is None:
        raise ApiError(
            404,
            "SOCIO_NO_ENCONTRADO",
            "Recurso no encontrado",
            f"No existe un socio con id {socio_id}"
        )
    if "email" in updates:
        socio_por_email = get_socio_by_email(connection, updates["email"])
        if socio_por_email is not None and socio_por_email["id"] != socio_id:
            raise ApiError(
                409,
                "EMAIL_DUPLICADO",
                "Conflicto de negocio",
                "Ya existe un socio registrado con este email"
            )
    actualizaciones = update_socio(connection, socio_id, updates)
    connection.commit()
    return actualizaciones

