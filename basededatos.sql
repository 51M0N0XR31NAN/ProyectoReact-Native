-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         12.2.2-MariaDB - MariaDB Server
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.14.0.7165
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para notvence
CREATE DATABASE IF NOT EXISTS `notvence` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `notvence`;

-- Volcando estructura para tabla notvence.casa
CREATE TABLE IF NOT EXISTS `casa` (
  `id_casa` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_hogar` varchar(400) NOT NULL,
  `nfc` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_casa`),
  UNIQUE KEY `uk_casa_nfc` (`nfc`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla notvence.casa: ~6 rows (aproximadamente)
INSERT INTO `casa` (`id_casa`, `nombre_hogar`, `nfc`) VALUES
	(1, 'Casa Gabriela', 'NFC-CASA-001'),
	(2, 'Casa Luna', 'NFC-CASA-002'),
	(3, 'Casa Galo', 'NFC-CASA-003'),
	(4, 'Casa Simon', 'NFC-CASA-004'),
	(5, 'Casa de simi-simi', NULL),
	(6, 'Casa de 67', NULL);

-- Volcando estructura para tabla notvence.categoria
CREATE TABLE IF NOT EXISTS `categoria` (
  `id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_categoria` varchar(100) NOT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `uk_categoria_nombre` (`nombre_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla notvence.categoria: ~5 rows (aproximadamente)
INSERT INTO `categoria` (`id_categoria`, `nombre_categoria`) VALUES
	(1, 'Alimentos'),
	(2, 'Bebidas'),
	(3, 'Medicamentos'),
	(4, 'Aseo'),
	(5, 'Otros');

-- Volcando estructura para tabla notvence.lista_compra
CREATE TABLE IF NOT EXISTS `lista_compra` (
  `id_lista` int(11) NOT NULL AUTO_INCREMENT,
  `id_casa` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL DEFAULT 1.00,
  `estado` enum('Pendiente','Comprado','Cancelado') NOT NULL DEFAULT 'Pendiente',
  `fecha_compra` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_lista`),
  KEY `fk_lista_casa` (`id_casa`),
  KEY `fk_lista_producto` (`id_producto`),
  CONSTRAINT `fk_lista_casa` FOREIGN KEY (`id_casa`) REFERENCES `casa` (`id_casa`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_lista_producto` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla notvence.lista_compra: ~0 rows (aproximadamente)

-- Volcando estructura para tabla notvence.movimiento
CREATE TABLE IF NOT EXISTS `movimiento` (
  `id_movimiento` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `tipo_movimiento` enum('Entrada','Consumo','Descarte') NOT NULL,
  `cantidad_movimiento` decimal(12,2) NOT NULL,
  `fecha_movimiento` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_movimiento`),
  KEY `idx_movimiento_producto` (`id_producto`),
  CONSTRAINT `fk_movimiento_producto` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla notvence.movimiento: ~1 rows (aproximadamente)
INSERT INTO `movimiento` (`id_movimiento`, `id_producto`, `tipo_movimiento`, `cantidad_movimiento`, `fecha_movimiento`) VALUES
	(1, 1, 'Entrada', 2.00, '2026-08-20 15:50:32');

-- Volcando estructura para tabla notvence.producto
CREATE TABLE IF NOT EXISTS `producto` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `id_casa` int(11) NOT NULL,
  `id_categoria` int(11) NOT NULL,
  `nombre_producto` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `presentacion` varchar(100) DEFAULT NULL,
  `cantidad` decimal(10,2) NOT NULL DEFAULT 0.00,
  `cantidad_minima` decimal(10,2) NOT NULL DEFAULT 0.00,
  `estado_producto` enum('Activo','Por vencer') NOT NULL DEFAULT 'Activo',
  `fecha_vencimiento` date DEFAULT NULL,
  `observacion` varchar(100) DEFAULT 'Stock bajo',
  PRIMARY KEY (`id_producto`),
  KEY `idx_producto_casa` (`id_casa`),
  KEY `idx_producto_categoria` (`id_categoria`),
  CONSTRAINT `fk_producto_casa` FOREIGN KEY (`id_casa`) REFERENCES `casa` (`id_casa`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_producto_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla notvence.producto: ~10 rows (aproximadamente)
INSERT INTO `producto` (`id_producto`, `id_casa`, `id_categoria`, `nombre_producto`, `descripcion`, `presentacion`, `cantidad`, `cantidad_minima`, `estado_producto`, `fecha_vencimiento`, `observacion`) VALUES
	(1, 1, 1, 'Leche', 'Leche netherar, 1 litro', 'Litro', 2.00, 0.00, 'Activo', '2026-08-20', 'Stock bajo'),
	(2, 1, 1, 'Leche', 'Leche de prueba', 'Litro', 2.00, 0.00, 'Activo', '2026-08-30', 'Stock bajo'),
	(3, 1, 1, 'Leche', 'Leche de prueba', 'Litro', 2.00, 0.00, 'Activo', '2026-08-30', 'Stock bajo'),
	(4, 1, 1, 'Prueba', 'Prueba Bolsa', 'Bolsa', 50.00, 0.00, 'Por vencer', '2026-08-22', 'Stock bajo'),
	(5, 1, 3, 'Jabon', 'Barra', 'Unidad', 42.00, 0.00, 'Activo', '2026-08-30', 'Stock bajo'),
	(7, 5, 1, 'simi', 'simi listo para la accion', 'Unidad', 67.00, 0.00, 'Activo', NULL, 'Stock bajo'),
	(8, 5, 1, 'arroz', 'arroz', 'Kg', 10.00, 0.00, 'Activo', '2026-12-31', 'Stock bajo'),
	(9, 5, 4, 'jabon_manos', '', 'Unidad', 3.00, 0.00, 'Por vencer', '2020-05-15', 'Stock bajo'),
	(10, 5, 2, 'cerveza aguila', 'fghjvkhl.b', 'Unidad', 12.00, 0.00, 'Por vencer', '2010-02-11', 'Stock bajo'),
	(11, 5, 3, 'acetaminofem', 'qwertyuolkjhgfd', 'Pastilla', 24.00, 0.00, 'Activo', '2027-02-23', 'Stock bajo');

-- Volcando estructura para tabla notvence.producto_ubicacion
CREATE TABLE IF NOT EXISTS `producto_ubicacion` (
  `id_producto` int(11) NOT NULL,
  `id_ubicacion` int(11) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id_producto`,`id_ubicacion`),
  KEY `fk_pu_ubicacion` (`id_ubicacion`),
  CONSTRAINT `fk_pu_producto` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_pu_ubicacion` FOREIGN KEY (`id_ubicacion`) REFERENCES `ubicacion` (`id_ubicacion`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla notvence.producto_ubicacion: ~5 rows (aproximadamente)
INSERT INTO `producto_ubicacion` (`id_producto`, `id_ubicacion`, `cantidad`) VALUES
	(7, 1, 67.00),
	(8, 2, 10.00),
	(9, 3, 3.00),
	(10, 4, 12.00),
	(11, 5, 24.00);

-- Volcando estructura para tabla notvence.ubicacion
CREATE TABLE IF NOT EXISTS `ubicacion` (
  `id_ubicacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_casa` int(11) NOT NULL,
  `nombre_ubicacion` varchar(100) NOT NULL,
  PRIMARY KEY (`id_ubicacion`),
  KEY `idx_ubicacion_casa` (`id_casa`),
  CONSTRAINT `fk_ubicacion_casa` FOREIGN KEY (`id_casa`) REFERENCES `casa` (`id_casa`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla notvence.ubicacion: ~5 rows (aproximadamente)
INSERT INTO `ubicacion` (`id_ubicacion`, `id_casa`, `nombre_ubicacion`) VALUES
	(1, 5, 'habitacion'),
	(2, 5, 'almacen1'),
	(3, 5, 'baño'),
	(4, 5, 'nevera'),
	(5, 5, 'botiquin');

-- Volcando estructura para tabla notvence.usuario
CREATE TABLE IF NOT EXISTS `usuario` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `id_casa` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `correo` varchar(255) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `uk_usuario_correo` (`correo`),
  KEY `idx_usuario_casa` (`id_casa`),
  CONSTRAINT `fk_usuario_casa` FOREIGN KEY (`id_casa`) REFERENCES `casa` (`id_casa`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla notvence.usuario: ~4 rows (aproximadamente)
INSERT INTO `usuario` (`id_usuario`, `id_casa`, `nombre`, `correo`, `contrasena`) VALUES
	(1, 1, 'Gabriel', 'lauraespinosag@gmail.com', '98987'),
	(2, 2, 'Luna', 'lunasanchez120808@gmail.com', '654321209'),
	(3, 3, 'Simon', 'simonadel@gmail.com', '38347'),
	(4, 5, 'simi-simi', 'simi@gmail.com', 'six_seven');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
