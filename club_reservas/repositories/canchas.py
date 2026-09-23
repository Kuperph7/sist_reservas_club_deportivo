#Devuelve la primera fila como un diccionario, osea clave:valor o none si no se encontro resultado
def _fetchone(connection, query, params=()):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        cursor.close()

#Creamos la cancha nueva
def create_cancha(connection, nombre, id_deporte, precio_hora, activa=True, techada=False):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO canchas (nombre, id_deporte, precio_hora, activa, techada) VALUES (%s, %s, %s, %s, %s)",
            (nombre, id_deporte, precio_hora, activa, techada),
        )
        return cursor.lastrowid
    finally:
        cursor.close()

#Agarramos la cancha por su id para ver todos sus datos
def get_cancha_by_id(connection, cancha_id):
    return _fetchone(
        connection,
        "SELECT *  FROM canchas WHERE id = %s",
        (cancha_id,),
    )

#Recorremos todos los campos que vamos a modificar y revisamos cuales son esos cambios, dependiendo de si encuentra la coincidencia  
#sabemos que campo se va a modificar
def update_cancha(connection, cancha_id, changes):
    assignments = []
    params = []
    for field in ("nombre", "precio_hora", "activa", "techada"):
        if field in changes:
            assignments.append(f"{field} = %s")
            params.append(changes[field])

    params.append(cancha_id)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"UPDATE canchas SET {', '.join(assignments)} WHERE id = %s",
            tuple(params),
        )
    finally:
        cursor.close()


#Aca listamos las canchas por nombre, estado, id del deporte y si esta techada
def list_all_canchas(connection, nombre, activa, id_deporte, techada, limit, offset):
    conditions = []
    params = []

    if nombre is not None:
        conditions.append("LOWER(nombre) LIKE %s")
        params.append(f"%{nombre.lower()}%")
    if activa is not None:
        conditions.append("activa = %s")
        params.append(activa)
    if id_deporte is not None:
        conditions.append("id_deporte = %s")
        params.append(id_deporte)
    if techada is not None:
        conditions.append("techada = %s")
        params.append(techada)


    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    count_row = _fetchone(
        connection,
        f"SELECT COUNT(*) AS total FROM canchas{where}",
        tuple(params),
    )

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT * FROM canchas{where} "
            "ORDER BY id ASC LIMIT %s OFFSET %s",
            tuple([*params, limit, offset]),
        )
        canchas = cursor.fetchall()
    finally:
        cursor.close()

    return canchas, count_row["total"]

# Verifica si la cancha tiene al menos una reserva asociada (para validar el DELETE)
def has_reservas(connection, cancha_id):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1 FROM reservas WHERE id_cancha = %s LIMIT 1 ",(cancha_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()

    
# Elimina la cancha de la base de datos
def delete_cancha(connection, cancha_id):
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM canchas WHERE id = %s",(cancha_id,))
    finally:
        cursor.close(