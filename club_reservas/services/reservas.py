from club_reservas.repositories.socios import get_socio_by_id
from club_reservas.repositories.canchas import get_cancha_by_id
from club_reservas.repositories.reservas import (get_reservas,create_reserva, get_reserva_by_id,update_reserva)
from datetime import datetime

#Crear la reserva / Post Reservas
def generar_reserva(connection,id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin):
    socio = get_socio_by_id(connection, id_socio)

    fecha_hora_inicio = datetime.isoformat(fecha_hora_inicio)
    fecha_hora_fin = datetime.isoformat(fecha_hora_fin)
    
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

    #Validacion de horarios
    duracion = fecha_hora_fin - fecha_hora_inicio
    horas = duracion.total_seconds() / 3600

    if horas < 1 or horas > 3:
        raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflico de negocio",
            f"La duracion de la reserva tiene que ser entre 1 y 3 horas"
        )

    if fecha_hora_inicio >= fecha_hora_fin:
        raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflico de negocio",
            "La fecha de inicio debe ser anterior a la fecha de fin"
        )

    reservas = get_reservas(connection)

    #Evaluacion de superposicion horaria
    for reserva in reservas:

        if reserva["id_cancha"] != id_cancha:
            continue

        if reserva["estado"] != "confirmada":
            continue

        inicio_reserva = reserva["fecha_hora_inicio"]
        
        fin_reserva = reserva["fecha_hora_fin"]

        if (fecha_hora_inicio < fin_reserva and fecha_hora_fin > inicio_reserva):
            raise ApiError(
            409,
            "HORARIO_INVALIDO",
            "Conflico de negocio",
            "La cancha ya está reservada en ese horario"
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

def obtener_reserva_por_id(connection, reserva_id: int):
    reserva = get_reserva_by_id(connection, reserva_id)
    if reserva is None:
        raise ValueError("La reserva no existe")
        return reserva

#Actualizar el estado de la reserva / Put reservas id 
def actualizar_estado(connection,id_reserva, estado_solicitado):
    reserva= get_reserva_by_id(connection,id_reserva)
    #Habria que hacer una funcion que valide la existencia de la reserva? 
    permitir = False 

    estado_actual = reserva["estado"]

    if estado_actual == estado_solicitado:
        return "exito"

    if estado_actual == "confirmada" and (estado_solicitado == "cancelada" or estado_solicitado == "finalizada"): 
        permitir = True
    else:
        return "no permitido"

    if permitir: update_reserva(connection, id_reserva, estado_solicitado)
