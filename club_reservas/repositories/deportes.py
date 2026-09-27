from sqlalchemy import text

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