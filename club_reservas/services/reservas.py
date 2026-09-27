from club_reservas.repositories.socios import get_socio_by_id
from club_reservas.repositories.canchas import get_cancha_by_id
from club_reservas.repositories.reservas import (get_reservas,create_reserva,get_reserva_by_id,update_reserva)
from datetime import datetime

#Crear la reserva / Post Reservas
def generar_reserva(connection,id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin):
    socio = get_socio_by_id(connection, id_socio)

    fecha_hora_inicio = datetime.isoformat(fecha_hora_inicio)
    fecha_hora_fin = datetime.isoformat(fecha_hora_fin)
    
    #Validaciones de socio
    if socio is None:
        raise ValueError("El socio no existe")

    if not socio["activo"]:
        raise ValueError("El socio está inactivo")

    cancha = get_cancha_by_id(connection, id_cancha)

    #Validaciones de cancha
    if cancha is None:
        raise ValueError("La cancha no existe")

    if not cancha["activa"]:
        raise ValueError("La cancha está inactiva")

    if fecha_hora_inicio >= fecha_hora_fin:
        raise ValueError(
            "La fecha de inicio debe ser anterior a la fecha de fin"
        )

    reservas_json= get_reservas(connection)

    reservas = reservas_json["reservas"]

    #Evaluacion de superposicion horaria
    for reserva in reservas:

        if reserva["id_cancha"] != id_cancha:
            continue

        if reserva["estado"] != "confirmada":
            continue

        inicio_reserva = reserva["fecha_hora_inicio"]
        
        fin_reserva = reserva["fecha_hora_fin"]

        if (fecha_hora_inicio < fin_reserva and fecha_hora_fin > inicio_reserva):
            raise ValueError("La cancha ya está reservada en ese horario")

    #Calculo del precio
    precio_hora = cancha["precio_hora"]

    duracion = fecha_hora_fin - fecha_hora_inicio
    horas = duracion.total_seconds() / 3600

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

