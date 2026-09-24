from sqlalchemy import text

#Agarramos el deporte por su id para ver todos sus datos
def get_deporte_by_id(connection, deporte_id):
    result = connection.execute(
        text("SELECT * FROM deportes WHERE id = :deporte_id"),
        {"deporte_id": deporte_id},
    )
    return result.mappings().first()
