-- 1. Preparación de la Base de Datos
CREATE DATABASE IF NOT EXISTS rfid_access;
USE rfid_access;

-- 2. Limpieza de tablas anteriores
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- 3. Tabla de Usuarios (Adaptada a P-C3 con TOKEN)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(64) UNIQUE NOT NULL, -- Sustituye a UID, para tokens alfanuméricos
    name VARCHAR(100) NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE', 'BLOCKED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_token (token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tabla de Logs (Adaptada a P-C3)
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(64) NOT NULL, -- Se registra el token que intentó acceder
    access_status VARCHAR(50) NOT NULL, -- Ejemplo: "Permitido", "Denegado" o "ERROR"
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_token (token),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Datos Iniciales de Prueba (Ejemplos de Tokens alfanuméricos)
INSERT INTO users (token, name, status) VALUES
('BT-GRUPO3-2024', 'Grupo 3 Bluetooth', 'ACTIVE'),
('ADMIN-TOKEN-99', 'Administrador', 'ACTIVE'),
('USER-TEST-456', 'Usuario de Prueba', 'INACTIVE');

-- Mensaje de confirmación
SELECT '✅ Base de datos P-C3 (Bluetooth Tokens) inicializada con éxito' AS Info;