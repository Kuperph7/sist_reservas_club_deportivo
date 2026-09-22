#Devuelve la primera fila como un diccionario, osea clave:valor o none si no se encontro resultado
def _fetchone(connection, query, params=()):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        cursor.close()

#Agarramos el sodeportecio por su id para ver todos sus datos
def get_deporte_by_id(connection, socio_id):
    return _fetchone(
        connection,
        "SELECT * FROM deportes WHERE id = %s",
        (socio_id,),
    )