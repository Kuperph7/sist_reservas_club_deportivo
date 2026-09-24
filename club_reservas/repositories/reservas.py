from sqlalchemy import text

#Creamos la reserva nueva
def create_reserva(connection, id_socio , id_cancha , fecha_hora_inicio, fecha_hora_fin, precio_hora, precio_total):
    result = connection.execute(
        text(
            "INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total) "
            "VALUES (:id_socio, :id_cancha, :fecha_hora_inicio, :fecha_hora_fin, 'confirmada', :precio_hora, :precio_total)"
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

#Agarramos la reserva por su id para ver todos sus datos
def get_reserva_by_id(connection, reserva_id):
    result = connection.execute(
        text("SELECT * FROM reservas WHERE id = :reserva_id"),
        {"reserva_id": reserva_id},
    )
    return result.mappings().first()

#Recorremos todos los campos que vamos a modificar y revisamos cuales son esos cambios, dependiendo de si encuentra la coincidencia  
#sabemos que campo se va a modificar
def update_reserva(connection, reserva_id, changes):
    assignments = []
    params = {}
    for field in ("estado",):
        if field in changes:
            assignments.append(f"{field} = :{field}")
            params[field] = changes[field]

    params["reserva_id"] = reserva_id
    result = connection.execute(
        text(
            f"UPDATE reservas SET {', '.join(assignments)} "
            "WHERE id = :reserva_id"
        ),
        params,
    )
    return result.rowcount

#Aca listamos las reservas por el id de la cancha, el id del socio, el estado y las fechas del inicio y final de la reserva
def list_all_reservas(connection, id_socio , id_cancha ,estado, fecha_desde, fecha_hasta, limit, offset):
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
    reservas = result.mappings().all()

    return reservas, count_row["total"]
