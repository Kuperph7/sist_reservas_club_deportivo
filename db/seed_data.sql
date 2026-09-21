-- seed.sql
-- Datos ficticios para desarrollo y pruebas.
-- Ejecutar después de init_db.sql.
--
-- Los INSERT IGNORE permiten volver a ejecutar el archivo sin duplicar
-- los registros que ya tengan el mismo ID o, en socios, el mismo email.

USE club_reservas;


-- =========================================================
-- 1. DEPORTES INICIALES
-- =========================================================
-- Son los tres deportes mencionados en el enunciado.

INSERT IGNORE INTO deportes (id, nombre) VALUES
    (1, 'Fútbol'),
    (2, 'Tenis'),
    (3, 'Pádel');


-- =========================================================
-- 2. CANCHAS DE PRUEBA
-- =========================================================
-- Los precios están expresados en centavos.

INSERT IGNORE INTO canchas
    (id, nombre, id_deporte, precio_hora, techada, activa)
VALUES
    (1, 'Cancha 1 - Fútbol 5', 1, 1000000, FALSE, TRUE),
    (2, 'Tenis Central',        2,  800000, FALSE, TRUE),
    (3, 'Pádel Techada',        3, 1200000, TRUE,  TRUE),
    (4, 'Cancha Auxiliar',      1,  900000, FALSE, FALSE);


-- =========================================================
-- 3. SOCIOS DE PRUEBA
-- =========================================================

INSERT IGNORE INTO socios
    (id, nombre, email, activo)
VALUES
    (1, 'Juan Pérez',   'juan.perez@example.com', TRUE),
    (2, 'Ana López',    'ana.lopez@example.com',  TRUE),
    (3, 'Carlos Gómez', 'carlos.gomez@example.com', FALSE);


-- =========================================================
-- 4. RESERVAS DE PRUEBA
-- =========================================================
-- Se incluyen distintos estados para facilitar pruebas de listado,
-- filtros, disponibilidad y transiciones.
--
-- Reserva 1:
-- 2 horas x 1.000.000 centavos/hora = 2.000.000 centavos.
--
-- Reserva 2:
-- ejemplo histórico ya finalizado.
--
-- Reserva 3:
-- ejemplo cancelado; no debe bloquear disponibilidad.

INSERT IGNORE INTO reservas
    (
        id,
        id_socio,
        id_cancha,
        fecha_hora_inicio,
        fecha_hora_fin,
        estado,
        precio_hora,
        precio_total
    )
VALUES
    (
        1,
        1,
        1,
        '2026-10-15 18:00:00.000000',
        '2026-10-15 20:00:00.000000',
        'confirmada',
        1000000,
        2000000
    ),
    (
        2,
        2,
        2,
        '2026-09-10 18:00:00.000000',
        '2026-09-10 19:00:00.000000',
        'finalizada',
        800000,
        800000
    ),
    (
        3,
        1,
        3,
        '2026-10-16 19:00:00.000000',
        '2026-10-16 20:00:00.000000',
        'cancelada',
        1200000,
        1200000
    );


-- =========================================================
-- 5. BLOQUEO DE PRUEBA - EXTENSIÓN OPCIONAL
-- =========================================================
-- Si el grupo no implementa la extensión opcional, este INSERT puede
-- eliminarse junto con la tabla bloqueos de init_db.sql.

INSERT IGNORE INTO bloqueos
    (id, id_cancha, fecha, hora_inicio, hora_fin, motivo)
VALUES
    (
        1,
        2,
        '2026-10-20',
        '08:00:00',
        '12:00:00',
        'Mantenimiento de iluminación'
    );
