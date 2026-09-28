from flask import current_app, jsonify


# Excepción personalizada utilizada por validators y services.
class ApiError(Exception):
    def __init__(
        self,
        status,
        code,
        message,
        description,
        level="error",
    ):
        super().__init__(description)
        self.status = status
        self.code = code
        self.message = message
        self.description = description
        self.level = level


# Construye el cuerpo JSON (clave:valor) como lo indica el contrato
def error_response(
    status,
    code,
    message,
    description,
    level="error",
):
    return (
        jsonify(
            {
                "errors": [
                    {
                        "code": code,
                        "message": message,
                        "level": level,
                        "description": description,
                    }
                ]
            }
        ),
        status,
    )

#Maneja los errores con el formato json
def handle_api_error(error):
    return error_response(
        error.status,
        error.code,
        error.message,
        error.description,
        error.level,
    )


# Maneja los errores inesperados
def handle_unexpected_error(error):
    current_app.logger.exception(
        "Error no controlado",
        exc_info=error,
    )
    return error_response(
        500,
        "ERROR_INTERNO",
        "Error interno del servidor",
        "Ocurrió un error inesperado al procesar la solicitud",
    )


# Le indica a Flask qué hacer cuando se lanza ApiError
def register_error_handlers(app):
    app.register_error_handler(ApiError, handle_api_error)
    app.register_error_handler(500, handle_unexpected_error)
