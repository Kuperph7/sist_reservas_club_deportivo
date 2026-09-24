from sqlalchemy import text

#Agarramos el socio por su id para ver todos sus datos
def get_socio_by_id(connection, socio_id):
    result = connection.execute(
        text("SELECT * FROM socios WHERE id = :socio_id"),
        {"socio_id": socio_id},
    )
    return result.mappings().first()



#Agarramos el socio por el mail
def get_socio_by_email(connection, email):
    result = connection.execute(
        text("SELECT * FROM socios WHERE email = :email"),
        {"email": email},
    )
    return result.mappings().first()



#Creamos al socio nuevo
def create_socio(connection, nombre, email):
    result = connection.execute(
        text(
            "INSERT INTO socios (nombre, email, activo) "
            "VALUES (:nombre, :email, TRUE)"
        ),
        {"nombre": nombre, "email": email},
    )
    return result.lastrowid

#Recorremos todos los campos que vamos a modificar y revisamos cuales son esos cambios, dependiendo de si encuentra la coincidencia  
#sabemos que campo se va a modificar
def update_socio(connection, socio_id, changes):
    assignments = []
    params = {}
    for field in ("nombre", "email", "activo"):
        if field in changes:
            assignments.append(f"{field} = :{field}")
            params[field] = changes[field]

    params["socio_id"] = socio_id
    result = connection.execute(
        text(
            f"UPDATE socios SET {', '.join(assignments)} "
            "WHERE id = :socio_id"
        ),
        params,
    )
    return result.rowcount


#Aca listamos los socios con filtros por nombre y estado, tambien contamos el total
def list_all_socios(connection, nombre, activo, limit, offset):
    conditions = []
    params = {}

    if nombre is not None:
        conditions.append("LOWER(nombre) LIKE :nombre")
        params["nombre"] = f"%{nombre.lower()}%"
    if activo is not None:
        conditions.append("activo = :activo")
        params["activo"] = activo

    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    count_result = connection.execute(
        text(f"SELECT COUNT(*) AS total FROM socios{where}"),
        params,
    )
    count_row = count_result.mappings().first()

    list_params = {**params, "limit": limit, "offset": offset}
    result = connection.execute(
        text(
            f"SELECT * FROM socios{where} "
            "ORDER BY id ASC LIMIT :limit OFFSET :offset"
        ),
        list_params,
    )
    socios = result.mappings().all()

    return socios, count_row["total"]


