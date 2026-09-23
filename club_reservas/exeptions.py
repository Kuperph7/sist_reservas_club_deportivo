from flask import jsonify


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


# Le indica a Flask qué hacer cuando se lanza ApiError
def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return error_response(
            error.status,
            error.code,
            error.message,
            error.description,
            error.level,
        )