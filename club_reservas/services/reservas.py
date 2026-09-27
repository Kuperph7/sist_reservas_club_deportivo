from club_reservas.repositories.socios import get_socio_by_id
from club_reservas.repositories.canchas import get_cancha_by_id
from club_reservas.repositories.reservas import (get_reservas,create_reserva, get_reserva_by_id,update_reserva)
from datetime import (datetime, time)
from club_reservas.exeptions import ApiError


#Crear la reserva / Post Reservas
def generar_reserva(connection,id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin):
    socio = get_socio_by_id(connection, id_socio)

    #Validaciones de socio
    if socio is None:
        raise ApiError(
            404,
            "SOCIO_NO_ENCONTRADO",
            "Recurso no encontrado",
            f"No existe un socio con id {id_socio}"
        )
    
    if not socio["activo"]:
        raise ApiError(
            409,
            "SOCIO_NO_ACTIVO",
            "Conflico de negocio",
            f"El socio con id:{id_socio} no esta activo"
        )

    cancha = get_cancha_by_id(connection, id_cancha)

    #Validaciones de cancha
    if cancha is None:
        raise ApiError(
            404,
            "CANCHA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una cancha con id {id_cancha}"
        )

    if not cancha["activa"]:
        raise ApiError(
            409,
            "CANCHA_NO_ACTIVA",
            "Conflico de negocio",
            f"La cancha con id:{id_cancha} no esta activa"
        )

    #Validacion horario despues del mismo de la request

    ahora = datetime.now(fecha_hora_inicio.tzinfo)

    if fecha_hora_inicio <= ahora:
        raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflicto de negocio",
            "La reserva debe comenzar después del momento de la solicitud"
        )
    
    #Validacion horarios en punto
    if fecha_hora_inicio.minute != 0 or fecha_hora_inicio.second != 0 or fecha_hora_inicio.microsecond != 0:
        raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflicto de negocio",
            "La hora de inicio debe ser en punto"
    )

    if fecha_hora_fin.minute != 0 or fecha_hora_fin.second != 0 or fecha_hora_fin.microsecond != 0:
        raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflicto de negocio",
            "La hora de fin debe ser en punto"
        )
    
    #Validacion duracion entre 1 y 3 horas
    duracion = fecha_hora_fin - fecha_hora_inicio
    horas = duracion.total_seconds() / 3600

    if horas < 1 or horas > 3:
        raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflico de negocio",
            f"La duracion de la reserva tiene que ser entre 1 y 3 horas"
        )

    #Validacion inicio anterior al fin 
    if fecha_hora_inicio >= fecha_hora_fin:
        raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflico de negocio",
            "La fecha de inicio debe ser anterior a la fecha de fin"
        )

    #Validacion horario entre 8:00 y 23:00
    if fecha_hora_inicio.time() < time(8, 0) or fecha_hora_fin.time() > time(23, 0):
        raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflicto de negocio",
            "El horario de la reserva debe estar entre las 08:00 y 23:00 horas"
        )
    reservas = get_reservas(connection)

    #Evaluacion de superposicion horaria 
    for reserva in reservas:

            if reserva["estado"] != "confirmada":
                continue

            inicio_reserva = reserva["fecha_hora_inicio"]
            fin_reserva = reserva["fecha_hora_fin"]

            # La cancha ya está ocupada
            if reserva["id_cancha"] == id_cancha:
                if (
                    fecha_hora_inicio < fin_reserva
                    and fecha_hora_fin > inicio_reserva
                ):
                    raise ApiError(
                        409,
                        "CANCHA_NO_DISPONIBLE",
                        "Conflicto de negocio",
                        "La cancha ya está reservada en ese horario"
                    )

            # El socio ya tiene otra reserva
            if reserva["id_socio"] == id_socio:
                if (
                    fecha_hora_inicio < fin_reserva
                    and fecha_hora_fin > inicio_reserva
                ):
                    raise ApiError(
                        409,
                        "SOCIO_NO_DISPONIBLE",
                        "Conflicto de negocio",
                        "El socio ya tiene una reserva en ese horario"
                    )


    #Calculo del precio
    precio_hora = cancha["precio_hora"]

    precio_total = int(precio_hora * horas)

    #Creacion de la reserva (create_reserva() debe devolver el id creado)
    id_reserva = create_reserva(connection,id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,precio_hora,precio_total)

    return {
        "id": id_reserva,
        "id_socio": id_socio,
        "id_cancha": id_cancha,
        "fecha_hora_inicio": fecha_hora_inicio,
        "fecha_hora_fin": fecha_hora_fin,
        "estado": "confirmada",
        "precio_hora": precio_hora,
        "precio_total": precio_total,
    }

#Obtener la reserva por la id 
def obtener_reserva_por_id(connection, reserva_id: int):
    reserva = get_reserva_by_id(connection, reserva_id)
    if reserva is None:
        raise ValueError("La reserva no existe")
        return reserva

#Actualizar el estado de la reserva / Put reservas id 
def actualizar_estado(connection, id_reserva, estado_solicitado):

    reserva = get_reserva_by_id(connection, id_reserva)

    # La reserva debe existir
    if reserva is None:
        raise ApiError(
            404,
            "RESERVA_NO_ENCONTRADA",
            "Recurso no encontrado",
            f"No existe una reserva con id {id_reserva}"
        )

    # El estado solicitado debe ser válido
    estados_validos = ("confirmada", "cancelada", "finalizada")

    if estado_solicitado not in estados_validos:
        raise ApiError(
            400,
            "ESTADO_INVALIDO",
            "Datos inválidos",
            f"El estado {estado_solicitado} no es válido"
        )

    estado_actual = reserva["estado"]

    # Si ya tiene ese estado
    if estado_actual == estado_solicitado:
        return "exito"

    ahora = datetime.now(reserva["fecha_hora_inicio"].tzinfo)

    # Confirmada → cancelada
    if estado_actual == "confirmada" and estado_solicitado == "cancelada":

        if ahora >= reserva["fecha_hora_inicio"]:
            raise ApiError(
                409,
                "CANCELACION_NO_PERMITIDA",
                "Conflicto de negocio",
                "No se puede cancelar una reserva que ya comenzó"
            )

    # Confirmada → finalizada
    elif estado_actual == "confirmada" and estado_solicitado == "finalizada":

        if ahora < reserva["fecha_hora_fin"]:
            raise ApiError(
                409,
                "FINALIZACION_NO_PERMITIDA",
                "Conflicto de negocio",
                "No se puede finalizar una reserva que todavía no terminó"
            )

    # Cualquier otra transición
    else:
        raise ApiError(
            409,
            "CAMBIO_ESTADO_NO_PERMITIDO",
            "Conflicto de negocio",
            f"No se puede cambiar el estado de {estado_actual} a {estado_solicitado}"
        )

    update_reserva(
        connection,
        id_reserva,
        estado_solicitado
    )

    return "exito"