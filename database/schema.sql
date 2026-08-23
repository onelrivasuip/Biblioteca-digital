CREATE DATABASE IF NOT EXISTS biblioteca_digital
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE biblioteca_digital;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    cedula VARCHAR(30) NOT NULL UNIQUE,
    correo VARCHAR(120) UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS libros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    autor VARCHAR(120) NOT NULL,
    isbn VARCHAR(30) NOT NULL UNIQUE,
    categoria VARCHAR(80),
    disponible BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    libro_id INT NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_limite DATE NOT NULL,
    fecha_devolucion DATE,
    estado ENUM('ACTIVO', 'DEVUELTO', 'VENCIDO') DEFAULT 'ACTIVO',

    CONSTRAINT fk_prestamo_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id),

    CONSTRAINT fk_prestamo_libro
        FOREIGN KEY (libro_id)
        REFERENCES libros(id)
);

CREATE TABLE IF NOT EXISTS multas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prestamo_id INT NOT NULL UNIQUE,
    dias_atraso INT NOT NULL DEFAULT 0,
    monto DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    pagada BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_multa_prestamo
        FOREIGN KEY (prestamo_id)
        REFERENCES prestamos(id)
);