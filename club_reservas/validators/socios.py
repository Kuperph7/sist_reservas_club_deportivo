#importamos los validadores generales y tambien el re para poder usar las regex
import re
from app.validators.common import (
    parse_boolean,
    parse_non_negative_integer,
    reject_unknown_fields,
    validation_error,
)

#Estos son unos validadores especificos segun las tablas de socios
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
NAME_MAX_LENGTH = 120
EMAIL_MAX_LENGTH = 255
CREATE_FIELDS = {"nombre", "email"}
UPDATE_FIELDS = {"nombre", "email", "activo"}
LIST_FIELDS = {"nombre", "activo", "_limit", "_offset"}


#Validamos los nombres para que no vengan vacios ni algo que no sea un string
def _normalize_name(value):
    if not isinstance(value, str):
        validation_error("El campo 'nombre' debe ser un string")
    normalized = value.strip()
    if not normalized:
        validation_error("El campo 'nombre' no puede quedar vacío")
    if len(normalized) > NAME_MAX_LENGTH:
        validation_error(
            f"El campo 'nombre' no puede superar los {NAME_MAX_LENGTH} caracteres"
        )
    return normalized

#Validamos que el mail sea  correcto , ya sea por su longitud y por el regex para mantener el formato de mail comun
def _normalize_email(value):
    if not isinstance(value, str):
        validation_error("El campo 'email' debe ser un string")
    normalized = value.strip().lower()
    if len(normalized) > EMAIL_MAX_LENGTH:
        validation_error(
            f"El campo 'email' no puede superar los {EMAIL_MAX_LENGTH} caracteres"
        )
    if not EMAIL_PATTERN.fullmatch(normalized):
        validation_error("El campo 'email' debe contener un correo válido")
    return normalized

#Validamos que la creacion de datos sea correcta y que vengan todos los campos necesarios (se mostraron los validadores arriba)
def validate_create(data):
    reject_unknown_fields(data, CREATE_FIELDS)
    missing = sorted(CREATE_FIELDS - set(data))
    if missing:
        validation_error(f"Campos obligatorios faltantes: {', '.join(missing)}")
    return {
        "nombre": _normalize_name(data["nombre"]),
        "email": _normalize_email(data["email"]),
    }

#Aca estamos haciendo lo mismo que ocn el create pero para la actualizacion de los datos, corroboramos que todos sean correctos mediante
#las normalizaciones previamente explicadas
def validate_update(data):
    reject_unknown_fields(data, UPDATE_FIELDS)
    if not data:
        validation_error("El cuerpo de la actualización no puede estar vacío")

    normalized = {}
    if "nombre" in data:
        normalized["nombre"] = _normalize_name(data["nombre"])
    if "email" in data:
        normalized["email"] = _normalize_email(data["email"])
    if "activo" in data:
        if not isinstance(data["activo"], bool):
            validation_error("El campo 'activo' debe ser booleano")
        normalized["activo"] = data["activo"]
    return normalized

#Aca validamos los filtros y el paginado de los listados
def validate_list(args):
    reject_unknown_fields(args, LIST_FIELDS)
    for name in args:
        if len(args.getlist(name)) != 1:
            validation_error(f"El parámetro '{name}' no puede repetirse")

    nombre = args.get("nombre")
    return {
        "nombre": nombre.strip() if nombre is not None else None,
        "activo": parse_boolean(args.get("activo"), "activo"),
        "_limit": parse_non_negative_integer(
            args.get("_limit"), "_limit", 10, 1, 100
        ),
        "_offset": parse_non_negative_integer(
            args.get("_offset"), "_offset", 0, 0
        ),
    }