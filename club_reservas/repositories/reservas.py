#Devuelve la primera fila como un diccionario, osea clave:valor o none si no se encontro resultado
def _fetchone(connection, query, params=()):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        cursor.close()

#Creamos la reserva nueva
def create_reserva(connection, id_socio , id_cancha , fecha_hora_inicio, fecha_hora_fin, precio_hora, precio_total):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total) VALUES (%s, %s, %s, %s, 'confirmada', %s, %s)",
            (id_socio , id_cancha , fecha_hora_inicio, fecha_hora_fin, precio_hora, precio_total),
        )
        return cursor.lastrowid
    finally:
        cursor.close()

#Agarramos la reserva por su id para ver todos sus datos
def get_reserva_by_id(connection, reserva_id):
    return _fetchone(
        connection,
        "SELECT *  FROM reservas WHERE id = %s",
        (reserva_id,),
    )

#Recorremos todos los campos que vamos a modificar y revisamos cuales son esos cambios, dependiendo de si encuentra la coincidencia  
#sabemos que campo se va a modificar
def update_reserva(connection, reserva_id, changes):
    assignments = []
    params = []
    for field in ("nombre", "id_socio" , "id_cancha" , "fecha_hora_inicio", "fecha_hora_fin", "estado", "precio_hora", "precio_total"):
        if field in changes:
            assignments.append(f"{field} = %s")
            params.append(changes[field])

    params.append(reserva_id)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"UPDATE canchas SET {', '.join(assignments)} WHERE id = %s",
            tuple(params),
        )
    finally:
        cursor.close()

#Aca listamos las reservas por el id de la cancha, el id del socio, el estado y las fechas del inicio y final de la reserva
def list_all_reservas(connection, id_socio , id_cancha ,estado, fecha_desde, fecha_hasta, limit, offset):
    conditions = []
    params = []

    
    if id_cancha is not None:
        conditions.append("id_cancha = %s")
        params.append(id_cancha)
    if id_socio is not None:
        conditions.append("id_socio = %s")
        params.append(id_socio)
    if estado is not None:
        conditions.append("estado = %s")
        params.append(estado)
    if fecha_desde is not None:
        conditions.append("fecha_hora_inicio >= %s")
        params.append(fecha_desde)

    if fecha_hasta is not None:
        conditions.append(
            "fecha_hora_inicio < DATE_ADD(%s, INTERVAL 1 DAY)"
        )
        params.append(fecha_hasta)


    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    count_row = _fetchone(
        connection,
        f"SELECT COUNT(*) AS total FROM reservas{where}",
        tuple(params),
    )

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT * FROM reservas{where} "
            "ORDER BY id ASC LIMIT %s OFFSET %s",
            tuple([*params, limit, offset]),
        )
        reservas = cursor.fetchall()
    finally:
        cursor.close()

    return reservas, count_row["total"]
