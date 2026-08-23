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

-- -----------------------------------------------------------------------------
-- Índices adicionales (mejoran las búsquedas y los reportes)
-- -----------------------------------------------------------------------------
CREATE INDEX idx_libros_titulo    ON libros(titulo);
CREATE INDEX idx_usuarios_cedula  ON usuarios(cedula);
CREATE INDEX idx_prestamos_estado ON prestamos(estado);
CREATE INDEX idx_multas_pagada    ON multas(pagada);

-- -----------------------------------------------------------------------------
-- Datos semilla de prueba
-- -----------------------------------------------------------------------------
INSERT INTO libros (titulo, autor, isbn, categoria) VALUES
    ('Cien años de soledad', 'Gabriel García Márquez', '9780307474728', 'Novela'),
    ('El principito', 'Antoine de Saint-Exupéry', '9780156012195', 'Infantil'),
    ('1984', 'George Orwell', '9780451524935', 'Ciencia ficción'),
    ('Rayuela', 'Julio Cortázar', '9788437604572', 'Novela'),
    ('Don Quijote de la Mancha', 'Miguel de Cervantes', '9788424116381', 'Clásico')
ON DUPLICATE KEY UPDATE titulo = VALUES(titulo);

INSERT INTO usuarios (nombre, apellido, cedula, correo) VALUES
    ('Ana', 'Pérez', '8-123-456', 'ana.perez@correo.com'),
    ('Luis', 'Gómez', '8-234-567', 'luis.gomez@correo.com'),
    ('María', 'Rodríguez', '8-345-678', 'maria.rodriguez@correo.com')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- Un préstamo de ejemplo ya activo, para que "Préstamos" y "Reportes" no arranquen vacíos.
INSERT INTO prestamos (usuario_id, libro_id, fecha_prestamo, fecha_limite, estado)
SELECT u.id, l.id, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'ACTIVO'
FROM usuarios u, libros l
WHERE u.cedula = '8-123-456' AND l.isbn = '9780451524935'
LIMIT 1;

UPDATE libros SET disponible = FALSE WHERE isbn = '9780451524935';