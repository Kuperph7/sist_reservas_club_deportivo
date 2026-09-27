from sqlalchemy import text


def create_reserva(
    connection,
    id_socio,
    id_cancha,
    fecha_hora_inicio,
    fecha_hora_fin,
    precio_hora,
    precio_total,
):
    result = connection.execute(
        text(
            "INSERT INTO reservas ("
            "id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, "
            "estado, precio_hora, precio_total"
            ") VALUES ("
            ":id_socio, :id_cancha, :fecha_hora_inicio, :fecha_hora_fin, "
            "'confirmada', :precio_hora, :precio_total"
            ")"
        ),
        {
            "id_socio": id_socio,
            "id_cancha": id_cancha,
            "fecha_hora_inicio": fecha_hora_inicio,
            "fecha_hora_fin": fecha_hora_fin,
            "precio_hora": precio_hora,
            "precio_total": precio_total,
        },
    )
    return result.lastrowid


def get_reserva_by_id(connection, reserva_id):
    result = connection.execute(
        text("SELECT * FROM reservas WHERE id = :reserva_id"),
        {"reserva_id": reserva_id},
    )
    return result.mappings().first()


def get_socio_for_update(connection, socio_id):
    result = connection.execute(
        text("SELECT * FROM socios WHERE id = :socio_id FOR UPDATE"),
        {"socio_id": socio_id},
    )
    return result.mappings().first()


def get_cancha_for_update(connection, cancha_id):
    result = connection.execute(
        text("SELECT * FROM canchas WHERE id = :cancha_id FOR UPDATE"),
        {"cancha_id": cancha_id},
    )
    return result.mappings().first()


def has_reserva_overlap(
    connection,
    cancha_id,
    fecha_hora_inicio,
    fecha_hora_fin,
):
    result = connection.execute(
        text(
            "SELECT 1 FROM reservas "
            "WHERE id_cancha = :cancha_id "
            "AND estado = 'confirmada' "
            "AND fecha_hora_inicio < :fecha_hora_fin "
            "AND fecha_hora_fin > :fecha_hora_inicio "
            "LIMIT 1"
        ),
        {
            "cancha_id": cancha_id,
            "fecha_hora_inicio": fecha_hora_inicio,
            "fecha_hora_fin": fecha_hora_fin,
        },
    )
    return result.first() is not None


def has_socio_overlap(
    connection,
    socio_id,
    fecha_hora_inicio,
    fecha_hora_fin,
):
    result = connection.execute(
        text(
            "SELECT 1 FROM reservas "
            "WHERE id_socio = :socio_id "
            "AND estado = 'confirmada' "
            "AND fecha_hora_inicio < :fecha_hora_fin "
            "AND fecha_hora_fin > :fecha_hora_inicio "
            "LIMIT 1"
        ),
        {
            "socio_id": socio_id,
            "fecha_hora_inicio": fecha_hora_inicio,
            "fecha_hora_fin": fecha_hora_fin,
        },
    )
    return result.first() is not None


def has_bloqueo_overlap(
    connection,
    cancha_id,
    fecha_hora_inicio,
    fecha_hora_fin,
):
    result = connection.execute(
        text(
            "SELECT 1 FROM bloqueos "
            "WHERE id_cancha = :cancha_id "
            "AND TIMESTAMP(fecha, hora_inicio) < :fecha_hora_fin "
            "AND TIMESTAMP(fecha, hora_fin) > :fecha_hora_inicio "
            "LIMIT 1"
        ),
        {
            "cancha_id": cancha_id,
            "fecha_hora_inicio": fecha_hora_inicio,
            "fecha_hora_fin": fecha_hora_fin,
        },
    )
    return result.first() is not None


def update_reserva_state(connection, reserva_id, estado):
    result = connection.execute(
        text(
            "UPDATE reservas SET estado = :estado "
            "WHERE id = :reserva_id"
        ),
        {"estado": estado, "reserva_id": reserva_id},
    )
    return result.rowcount


def list_all_reservas(
    connection,
    id_socio,
    id_cancha,
    estado,
    fecha_desde,
    fecha_hasta,
    limit,
    offset,
):
    conditions = []
    params = {}

    if id_cancha is not None:
        conditions.append("id_cancha = :id_cancha")
        params["id_cancha"] = id_cancha
    if id_socio is not None:
        conditions.append("id_socio = :id_socio")
        params["id_socio"] = id_socio
    if estado is not None:
        conditions.append("estado = :estado")
        params["estado"] = estado
    if fecha_desde is not None:
        conditions.append("fecha_hora_inicio >= :fecha_desde")
        params["fecha_desde"] = fecha_desde
    if fecha_hasta is not None:
        conditions.append(
            "fecha_hora_inicio < DATE_ADD(:fecha_hasta, INTERVAL 1 DAY)"
        )
        params["fecha_hasta"] = fecha_hasta

    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    count_result = connection.execute(
        text(f"SELECT COUNT(*) AS total FROM reservas{where}"),
        params,
    )
    count_row = count_result.mappings().first()

    list_params = {**params, "limit": limit, "offset": offset}
    result = connection.execute(
        text(
            f"SELECT * FROM reservas{where} "
            "ORDER BY id ASC LIMIT :limit OFFSET :offset"
        ),
        list_params,
    )
    return result.mappings().all(), count_row["total"]
