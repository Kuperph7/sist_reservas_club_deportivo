# Expone: GET /deportes
from flask import Blueprint


deportes_bp = Blueprint("deportes", __name__)


@deportes_bp.get("/deportes")
def listar_deportes():
    return {"message": "GET /deportes"}, 200