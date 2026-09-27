from sqlalchemy import text


# Crea una cancha y devuelve su ID.
def create_cancha(connection, nombre, id_deporte, precio_hora, activa=True, techada=False):
    result = connection.execute(
        text(
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


# Obtiene una cancha por su ID.
def get_cancha_by_id(connection, cancha_id):
    result = connection.execute(
        text("SELECT * FROM canchas WHERE id = :cancha_id"),
        {"cancha_id": cancha_id},
    )
    return result.mappings().first()


# Actualiza los campos recibidos de una cancha.
def update_cancha(connection, cancha_id, changes):
    assignments = []
    params = {}
    for field in ("nombre", "precio_hora", "activa", "techada"):
        if field in changes:
            assignments.append(f"{field} = :{field}")
            params[field] = changes[field]

    params["cancha_id"] = cancha_id
    result = connection.execute(
        text(
            f"UPDATE canchas SET {', '.join(assignments)} "
            "WHERE id = :cancha_id"
        ),
        params,
    )
    return result.rowcount


# Lista canchas con filtros y paginación.
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
        text(f"SELECT COUNT(*) AS total FROM canchas{where}"),
        params,
    )
    count_row = count_result.mappings().first()

    list_params = {**params, "limit": limit, "offset": offset}
    result = connection.execute(
        text(
            f"SELECT * FROM canchas{where} "
            "ORDER BY id ASC LIMIT :limit OFFSET :offset"
        ),
        list_params,
    )
    canchas = result.mappings().all()

    return canchas, count_row["total"]


# Lista canchas activas sin reservas ni bloqueos que se superpongan al intervalo.
def consulta_disponibilidad(
    connection,
    fecha_hora_inicio,
    fecha_hora_fin,
    id_deporte,
    techada,
    limit,
    offset,
):
    conditions = [
        "c.activa = TRUE",
        "NOT EXISTS ("
        "SELECT 1 FROM reservas r "
        "WHERE r.id_cancha = c.id "
        "AND r.estado = 'confirmada' "
        "AND r.fecha_hora_inicio < :fecha_hora_fin "
        "AND r.fecha_hora_fin > :fecha_hora_inicio"
        ")",
        "NOT EXISTS ("
        "SELECT 1 FROM bloqueos b "
        "WHERE b.id_cancha = c.id "
        "AND b.fecha = DATE(:fecha_hora_inicio) "
        "AND b.hora_inicio < TIME(:fecha_hora_fin) "
        "AND b.hora_fin > TIME(:fecha_hora_inicio)"
        ")",
    ]
    params = {
        "fecha_hora_inicio": fecha_hora_inicio,
        "fecha_hora_fin": fecha_hora_fin,
    }

    if id_deporte is not None:
        conditions.append("c.id_deporte = :id_deporte")
        params["id_deporte"] = id_deporte
    if techada is not None:
        conditions.append("c.techada = :techada")
        params["techada"] = techada

    where = f" WHERE {' AND '.join(conditions)}"
    count_result = connection.execute(
        text(f"SELECT COUNT(*) AS total FROM canchas c{where}"),
        params,
    )
    count_row = count_result.mappings().first()

    list_params = {**params, "limit": limit, "offset": offset}
    result = connection.execute(
        text(
            f"SELECT c.* FROM canchas c{where} "
            "ORDER BY c.id ASC LIMIT :limit OFFSET :offset"
        ),
        list_params,
    )
    canchas = result.mappings().all()

    return canchas, count_row["total"]


# Verifica si la cancha tiene al menos una reserva asociada.
def has_reservas(connection, cancha_id):
    result = connection.execute(
        text("SELECT 1 FROM reservas WHERE id_cancha = :cancha_id LIMIT 1"),
        {"cancha_id": cancha_id},
    )
    return result.first() is not None


# Elimina una cancha por su ID.
def delete_cancha(connection, cancha_id):
    result = connection.execute(
        text("DELETE FROM canchas WHERE id = :cancha_id"),
        {"cancha_id": cancha_id},
    )
    return result.rowcount
