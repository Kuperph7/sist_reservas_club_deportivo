from club_reservas.repositories.deportes import (
    list_all_deportes,
)


def list_deportes(connection):
    deportes = list_all_deportes(connection)

    deportes_normalizados = []

    for deporte in deportes:
        deportes_normalizados.append(
            {
                "id": deporte["id"],
                "nombre": deporte["nombre"],
            }
        )

    return deportes_normalizados