from sqlalchemy import text


def get_deporte_by_id(connection, deporte_id):
    result = connection.execute(
        text("SELECT * FROM deportes WHERE id = :deporte_id"),
        {"deporte_id": deporte_id},
    )
    return result.mappings().first()


#Listamos los deportes de esta manera ya que no nos piden paginacion ni filtros para ellos
def list_all_deportes(connection):
    result = connection.execute(
        text(
            "SELECT id, nombre "
            "FROM deportes "
            "ORDER BY id ASC"
        )
    )

    return result.mappings().all()
