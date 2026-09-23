#Devuelve la primera fila como un diccionario, osea clave:valor o none si no se encontro resultado
def _fetchone(connection, query, params=()):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        cursor.close()

#Agarramos el socio por su id para ver todos sus datos
def get_socio_by_id(connection, socio_id):
    return _fetchone(
        connection,
        "SELECT * FROM socios WHERE id = %s",
        (socio_id,),
    )

#Creamos al socio nuevo
def create_socio(connection, nombre, email):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, TRUE)",
            (nombre, email),
        )
        return cursor.lastrowid
    finally:
        cursor.close()

#Recorremos todos los campos que vamos a modificar y revisamos cuales son esos cambios, dependiendo de si encuentra la coincidencia  
#sabemos que campo se va a modificar
def update_socio(connection, socio_id, changes):
    assignments = []
    params = []
    for field in ("nombre", "email", "activo"):
        if field in changes:
            assignments.append(f"{field} = %s")
            params.append(changes[field])

    params.append(socio_id)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"UPDATE socios SET {', '.join(assignments)} WHERE id = %s",
            tuple(params),
        )
    finally:
        cursor.close()


#Aca listamos los socios con filtros por nombre y estado, tambien contamos el total
def list_all_socios(connection, nombre, activo, limit, offset):
    conditions = []
    params = []

    if nombre is not None:
        conditions.append("LOWER(nombre) LIKE %s")
        params.append(f"%{nombre.lower()}%")
    if activo is not None:
        conditions.append("activo = %s")
        params.append(activo)

    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    count_row = _fetchone(
        connection,
        f"SELECT COUNT(*) AS total FROM socios{where}",
        tuple(params),
    )

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT * FROM socios{where} "
            "ORDER BY id ASC LIMIT %s OFFSET %s",
            tuple([*params, limit, offset]),
        )
        socios = cursor.fetchall()
    finally:
        cursor.close()

    return socios, count_row["total"]