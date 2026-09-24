from club_reservas.exeptions import ApiError

#Error de validacion simple por siu algun parametro es erroneo
def validation_error(description):
    raise ApiError(
        400,
        "ERROR_VALIDACION",
        "El cuerpo o los parámetros de la solicitud son inválidos",
        description,
    )

#Error que nos indica si estamos mandando algo que no es un json 
#ademas controlamos el error si el json esta mal escrito, asi no lo maneja flask
def require_json_object(request):
    if not request.is_json:
        validation_error("El cuerpo debe enviarse como application/json")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        validation_error("El cuerpo de la solicitud debe ser un objeto JSON")
    return data

#Esto es para  el offset y para el limit del paginado
def parse_non_negative_integer(value,name,default,minimum,maximum=None,):
    if value is None:
        return default

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        validation_error(
            f"El parámetro '{name}' debe ser un entero"
        )

    if parsed < minimum:
        validation_error(
            f"El parámetro '{name}' debe ser mayor o igual a {minimum}"
        )

    if maximum is not None and parsed > maximum:
        validation_error(
            f"El parámetro '{name}' debe estar entre {minimum} y {maximum}"
        )

    return parsed

#Aca normalizamos las respuestas de los true o false de json para que sean utilizables en python
def parse_boolean(value, name):
    if value is None:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    validation_error(f"El parámetro '{name}' solo admite true o false")


#Rechazamos los campos desconocidos, para que no manden datos que no correspondan
def reject_unknown_fields(data, allowed):
    for field in data:
        if field not in allowed:
            validation_error(
                f"Campo desconocido: {field}"
            )