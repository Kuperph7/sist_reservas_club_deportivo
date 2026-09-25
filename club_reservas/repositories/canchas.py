import sqlalchemy

#Creamos la cancha nueva
def create_cancha(connection, nombre, id_deporte, precio_hora, activa=True, techada=False):
    result = connection.execute(
        sqlalchemy.text(
            "INSERT INTO canchas (nombre, id_deporte, precio_hora, activa, techada) "
            "VALUES (:nombre, :id_deporte, :precio_hora, :activa, :techada)"
        ),
        {
            "nombre": nombre,
            "id_deporte": id_deporte,
            "precio_hora": precio_hora,
            "activa": activa,
            "techada": techada,
        },
    )
    return result.lastrowid

#Agarramos la cancha por su id para ver todos sus datos
def get_cancha_by_id(connection, cancha_id):
    result = connection.execute(
        sqlalchemy.text("SELECT * FROM canchas WHERE id = :cancha_id"),
        {"cancha_id": cancha_id},
    )
    return result.mappings().first()

#Recorremos todos los campos que vamos a modificar y revisamos cuales son esos cambios, dependiendo de si encuentra la coincidencia  
#sabemos que campo se va a modificar
def update_cancha(connection, cancha_id, changes):
    assignments = []
    params = {}
    for field in ("nombre", "precio_hora", "activa", "techada"):
        if field in changes:
            assignments.append(f"{field} = :{field}")
            params[field] = changes[field]

    params["cancha_id"] = cancha_id
    result = connection.execute(
        sqlalchemy.text(
            f"UPDATE canchas SET {', '.join(assignments)} "
            "WHERE id = :cancha_id"
        ),
        params,
    )
    return result.rowcount


#Aca listamos las canchas por nombre, estado, id del deporte y si esta techada
def list_all_canchas(connection, nombre, activa, id_deporte, techada, limit, offset):
    conditions = []
    params = {}

    if nombre is not None:
        conditions.append("LOWER(nombre) LIKE :nombre")
        params["nombre"] = f"%{nombre.lower()}%"
    if activa is not None:
        conditions.append("activa = :activa")
        params["activa"] = activa
    if id_deporte is not None:
        conditions.append("id_deporte = :id_deporte")
        params["id_deporte"] = id_deporte
    if techada is not None:
        conditions.append("techada = :techada")
        params["techada"] = techada


    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    count_result = connection.execute(
        sqlalchemy.text(f"SELECT COUNT(*) AS total FROM canchas{where}"),
        params,
    )
    count_row = count_result.mappings().first()

    list_params = {**params, "limit": limit, "offset": offset}
    result = connection.execute(
        sqlalchemy.text(
            f"SELECT * FROM canchas{where} "
            "ORDER BY id ASC LIMIT :limit OFFSET :offset"
        ),
        list_params,
    )
    canchas = result.mappings().all()

    return canchas, count_row["total"]

#Aca listamos las canchas que no tengan reservas durante el horario que ingrese el usuario
def consulta_disponibilidad(connection, fecha_hora_inicio, fecha_hora_fin, id_deporte, limit, offset):
    conditions = []
    params = {}

    conditions.append("fecha_hora_inicio >= :fecha_hora_inicio")
    params["fecha_hora_inicio"] = fecha_hora_inicio

    conditions.append(
        "fecha_hora_inicio < DATE_ADD(:fecha_hora_fin, INTERVAL 1 DAY)"
    )
    params["fecha_hora_fin"] = fecha_hora_fin

    conditions.append("activa = :activa")
    params["activa"] = True

    if id_deporte is not None:
        conditions.append["id_deporte = :id_deporte"]
        params["id_deporte"] = id_deporte

        
    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    count_result = connection.execute(
        sqlalchemy.text(f"SELECT COUNT(*) AS total FROM canchas{where}"),
        params,
    )
    count_row = count_result.mappings().first()

    list_params = {**params, "limit": limit, "offset": offset}
    result = connection.execute(
        sqlalchemy.text(
            f"SELECT * FROM canchas{where} "
            "ORDER BY id ASC LIMIT :limit OFFSET :offset"
        ),
        list_params,
    )
    canchas = result.mappings().all()

    return canchas, count_row["total"]

# Verifica si la cancha tiene al menos una reserva asociada.
def has_reservas(connection, cancha_id):
    result = connection.execute(
        sqlalchemy.text("SELECT 1 FROM reservas WHERE id_cancha = :cancha_id LIMIT 1"),
        {"cancha_id": cancha_id},
    )
    return result.first() is not None


# Elimina una cancha por su ID.
def delete_cancha(connection, cancha_id):
    result = connection.execute(
        sqlalchemy.text("DELETE FROM canchas WHERE id = :cancha_id"),
        {"cancha_id": cancha_id},
    )
    return result.rowcount
