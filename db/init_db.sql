-- init_db.sql
-- Proyecto Backend - Sistema de Reservas de Club Deportivo
-- MySQL 8.x
--
-- Modelo obligatorio:
--   deportes -> canchas -> reservas <- socios
--
-- La tabla bloqueos corresponde a la extensión opcional del enunciado.
-- Si el grupo decide no implementar esa extensión, puede eliminarse esa sección.
--
-- Nota sobre fechas:
-- La API trabaja siempre con GMT-3 y no realiza conversiones de zona horaria.
-- Por eso se usa DATETIME(6), conservando los microsegundos pero no un offset de zona.

CREATE DATABASE IF NOT EXISTS club_reservas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE club_reservas;


-- =========================================================
-- 1. DEPORTES
-- =========================================================
-- Los deportes se precargan desde seed.sql.
-- El enunciado no requiere endpoints para alta, modificación o eliminación.

CREATE TABLE IF NOT EXISTS deportes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,

    CONSTRAINT chk_deportes_nombre_no_vacio
        CHECK (CHAR_LENGTH(TRIM(nombre)) > 0)
) ENGINE=InnoDB;


-- =========================================================
-- 2. CANCHAS
-- =========================================================

CREATE TABLE IF NOT EXISTS canchas (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    id_deporte INT UNSIGNED NOT NULL,
    precio_hora BIGINT UNSIGNED NOT NULL,
    techada BOOLEAN NOT NULL DEFAULT FALSE,
    activa BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_canchas_deportes
        FOREIGN KEY (id_deporte)
        REFERENCES deportes(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT chk_canchas_nombre_no_vacio
        CHECK (CHAR_LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT chk_canchas_precio_hora_positivo
        CHECK (precio_hora > 0),

    CONSTRAINT chk_canchas_techada_boolean
        CHECK (techada IN (0, 1)),

    CONSTRAINT chk_canchas_activa_boolean
        CHECK (activa IN (0, 1)),

    INDEX idx_canchas_deporte (id_deporte),
    INDEX idx_canchas_filtros (id_deporte, techada, activa)
) ENGINE=InnoDB;


-- =========================================================
-- 3. SOCIOS
-- =========================================================
-- El email se almacena en minúsculas y sin espacios.
-- La validación completa del formato de email debe realizarse en Flask.

CREATE TABLE IF NOT EXISTS socios (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_socios_email UNIQUE (email),

    CONSTRAINT chk_socios_nombre_no_vacio
        CHECK (CHAR_LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT chk_socios_email_normalizado
        CHECK (email = LOWER(TRIM(email))),

    CONSTRAINT chk_socios_activo_boolean
        CHECK (activo IN (0, 1)),

    INDEX idx_socios_activo (activo)
) ENGINE=InnoDB;


-- =========================================================
-- 4. RESERVAS
-- =========================================================
-- precio_hora y precio_total se guardan en la reserva para conservar
-- el valor histórico aunque luego cambie el precio de la cancha.
--
-- Las reglas de superposición NO pueden resolverse correctamente con
-- una UNIQUE convencional. Deben validarse desde la aplicación, dentro
-- de la misma transacción en la que se inserta la reserva.

CREATE TABLE IF NOT EXISTS reservas (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_socio INT UNSIGNED NOT NULL,
    id_cancha INT UNSIGNED NOT NULL,
    fecha_hora_inicio DATETIME(6) NOT NULL,
    fecha_hora_fin DATETIME(6) NOT NULL,
    estado ENUM('confirmada', 'cancelada', 'finalizada')
        NOT NULL DEFAULT 'confirmada',
    precio_hora BIGINT UNSIGNED NOT NULL,
    precio_total BIGINT UNSIGNED NOT NULL,

    CONSTRAINT fk_reservas_socios
        FOREIGN KEY (id_socio)
        REFERENCES socios(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT fk_reservas_canchas
        FOREIGN KEY (id_cancha)
        REFERENCES canchas(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT chk_reservas_intervalo
        CHECK (fecha_hora_inicio < fecha_hora_fin),

    CONSTRAINT chk_reservas_precio_hora_positivo
        CHECK (precio_hora > 0),

    CONSTRAINT chk_reservas_precio_total_positivo
        CHECK (precio_total > 0),

    INDEX idx_reservas_cancha_estado_intervalo
        (id_cancha, estado, fecha_hora_inicio, fecha_hora_fin),

    INDEX idx_reservas_socio_estado_intervalo
        (id_socio, estado, fecha_hora_inicio, fecha_hora_fin),

    INDEX idx_reservas_fecha_inicio
        (fecha_hora_inicio)
) ENGINE=InnoDB;


-- =========================================================
-- 5. BLOQUEOS - EXTENSIÓN OPCIONAL
-- =========================================================
-- No es necesaria para cumplir el alcance obligatorio.
-- La validación de horario, horas en punto, fecha futura y
-- superposiciones debe realizarse en la capa de negocio.

CREATE TABLE IF NOT EXISTS bloqueos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_cancha INT UNSIGNED NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    motivo VARCHAR(255) NOT NULL,

    CONSTRAINT fk_bloqueos_canchas
        FOREIGN KEY (id_cancha)
        REFERENCES canchas(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT chk_bloqueos_intervalo
        CHECK (hora_inicio < hora_fin),

    CONSTRAINT chk_bloqueos_motivo_no_vacio
        CHECK (CHAR_LENGTH(TRIM(motivo)) > 0),

    INDEX idx_bloqueos_cancha_fecha_intervalo
        (id_cancha, fecha, hora_inicio, hora_fin)
) ENGINE=InnoDB;