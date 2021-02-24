SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS `mini_project`;
CREATE DATABASE `mini_project` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `mini_project`;

DELIMITER ;;

CREATE DEFINER=`root`@`localhost` PROCEDURE `get_order_status_summary`()
SELECT UPPER(s.code) AS status, COUNT(o.status) AS count FROM orders o LEFT OUTER JOIN status s ON o.status = s.id GROUP BY status;;

CREATE DEFINER=`root`@`localhost` PROCEDURE `get_order_totals`()
SELECT o.id, UPPER(o.name) AS Name, SUM((b.quantity * p.price)) AS Total FROM basket b LEFT OUTER JOIN orders o ON b.order_id=o.id LEFT OUTER JOIN products p ON b.item=p.id GROUP BY o.id;;

CREATE PROCEDURE `get_unassigned_couriers`()
SELECT c.id, c.name 
FROM couriers c 
LEFT OUTER JOIN orders o 
ON o.courier=c.id 
WHERE o.courier is NULL;;

CREATE DEFINER=`root`@`localhost` PROCEDURE `get_unassigned_orders`()
SELECT id, name FROM orders WHERE courier is NULL;;

DELIMITER ;

DROP TABLE IF EXISTS `basket`;
CREATE TABLE `basket` (
  `order_id` int NOT NULL,
  `item` int NOT NULL,
  `quantity` int NOT NULL,
  KEY `item` (`item`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `basket_ibfk_1` FOREIGN KEY (`item`) REFERENCES `products` (`id`),
  CONSTRAINT `basket_ibfk_3` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `basket` (`order_id`, `item`, `quantity`) VALUES
(1,	27,	1),
(1,	28,	1),
(1,	33,	1),
(1,	59,	2),
(2,	40,	1),
(2,	3,	1),
(2,	26,	1),
(2,	38,	2),
(2,	1,	1),
(3,	1,	1),
(3,	3,	1),
(3,	5,	1),
(3,	6,	1),
(3,	7,	1),
(5,	2,	1),
(5,	3,	1),
(5,	9,	1),
(6,	3,	1),
(6,	1,	1),
(6,	5,	1),
(6,	14,	1),
(6,	20,	1),
(6,	21,	1),
(6,	37,	1),
(6,	66,	1),
(6,	67,	2),
(8,	27,	1),
(8,	31,	1),
(8,	34,	1),
(8,	59,	2),
(8,	61,	1),
(8,	41,	1),
(9,	1,	1),
(9,	7,	1),
(10,	5,	1),
(10,	13,	2),
(10,	70,	1),
(11,	21,	1),
(11,	35,	1),
(11,	63,	1),
(11,	59,	2),
(1,	60,	2),
(1,	64,	1);

DROP TABLE IF EXISTS `catagories`;
CREATE TABLE `catagories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `catagories` (`id`, `name`) VALUES
(1,	'soft drinks'),
(2,	'hot drinks'),
(3,	'breakfast'),
(4,	'main meals'),
(5,	'lighter lunch'),
(6,	'kids meals'),
(7,	'desserts'),
(8,	'sundries'),
(9,	'other');

DROP TABLE IF EXISTS `couriers`;
CREATE TABLE `couriers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `couriers` (`id`, `name`, `phone`) VALUES
(1,	'gary',	'07088047684'),
(2,	'michelle',	'07003658602'),
(3,	'paul',	'07080263774'),
(4,	'michael',	'07972946358'),
(5,	'stephanie',	'07905979618'),
(6,	'roger',	'07589654874'),
(7,	'william',	'07988805560'),
(8,	'christine',	'07981783894'),
(9,	'dawn',	'07737855293'),
(10,	'mark',	'07737855293'),
(11,	'glen',	'07835203237'),
(12,	'jemma',	'07863505523'),
(13,	'miller',	'07856987458');

DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `address` varchar(100) NOT NULL,
  `area` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `courier` int DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `courier` (`courier`),
  KEY `status` (`status`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`courier`) REFERENCES `couriers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `orders_ibfk_4` FOREIGN KEY (`status`) REFERENCES `status` (`id`) ON DELETE SET DEFAULT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orders` (`id`, `name`, `address`, `area`, `phone`, `courier`, `status`) VALUES
(1,	'rebecca k ingram',	'128 north promenade',	'hr18pa',	'07033918495',	NULL,	1),
(2,	'niamh l mahmood',	'140 thompsons lane',	'ph28wn',	'07031221095',	NULL,	1),
(3,	'declan j lane',	'102 newmarket road',	'de562ad',	'07705692817',	1,	2),
(4,	'poppy d clements',	'116 glenurquhart road',	'yo71fh',	'07858838750',	5,	2),
(5,	'maisie s read',	'74 cheriton road',	'dl61hy',	'07711870333',	3,	2),
(6,	'joe p bloggs',	'1 some town',	'wh12er',	'07514875451',	4,	2),
(7,	'sean k holden',	'110 redcliffe way',	'b603rq',	'07930379341',	8,	3),
(8,	'kai m chamberlain',	'82 shore street',	'ca58xz',	'07027310489',	2,	3),
(9,	'john f doe',	'100 someplace',	'ts149ae',	'01635154874',	2,	4),
(10,	'connor c stewart',	'75 mill lane',	'dg91hd',	'07001194616',	1,	5),
(11,	'alice d bloggs',	'24 grove green road',	'ec19tl',	'07854875414',	11,	6),
(12,	'connor p reynolds',	'57 ploughy rd',	'ab415wn',	'07889801334',	13,	5),
(13,	'samuel s marsh',	'90 holburn lane',	'yo413ge',	'07070257322',	7,	6),
(14,	'matthew k russell',	'117 scrimshire lane',	'hs28ae',	'07858629795',	4,	6),
(15,	'jamie e haynes',	'57 gloucester road',	'dd86hd',	'07831598038',	12,	5),
(16,	'jude p simmons',	'73 emmerson road',	'dn71gw',	'07886666963',	3,	6),
(17,	'ruby l bryan',	'129 warner close',	'ts234ua',	'07935461600',	8,	3),
(18,	'callum j shepherd',	'58 wressle road',	'ox81jy',	'07769988834',	11,	3),
(19,	'amelia m oliver',	'26 osborne road',	'pa617ha',	'07881772765',	7,	4),
(20,	'george g franklin',	'104 station rd',	'ld3 9pw',	'07075727617',	6,	4),
(21,	'lauren s naylor',	'105 emerson road',	'hd87sg',	'07756413950',	10,	4);

DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `catagory` int NOT NULL DEFAULT '9',
  `price` decimal(5,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `catagory` (`catagory`),
  CONSTRAINT `products_ibfk_2` FOREIGN KEY (`catagory`) REFERENCES `catagories` (`id`) ON DELETE SET DEFAULT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `products` (`id`, `name`, `catagory`, `price`) VALUES
(1,	'smoked salmon & scrambled eggs',	3,	3.99),
(2,	'big breakfast',	3,	4.99),
(3,	'halloumi breakfast',	3,	4.99),
(4,	'super scrambled eggs',	3,	3.99),
(5,	'eggs & bacon',	3,	2.99),
(6,	'bitesize breakfast',	3,	2.99),
(7,	'smashed avacado',	3,	2.50),
(8,	'breakfast omlette',	3,	2.50),
(9,	'breakfast baguette',	3,	2.99),
(10,	'breakfast sandwich',	3,	2.99),
(11,	'toast & topping',	3,	1.50),
(12,	'scottish oat porridge',	3,	0.99),
(13,	'toasted teacake & butter',	3,	1.50),
(14,	'fish fingers',	6,	2.99),
(15,	'kids sausage and mash',	6,	2.99),
(16,	'chicken nuggets',	6,	2.99),
(17,	'pasta bolognese',	6,	2.99),
(18,	'mac & cheese',	6,	2.99),
(19,	'cheese & tomato pizza',	6,	2.99),
(20,	'crunchy veg sticks',	6,	0.79),
(21,	'1/2 jacket potato',	6,	1.50),
(22,	'hot chicken baguette',	5,	3.99),
(23,	'omlette',	5,	2.50),
(24,	'sweet potato fries',	5,	1.49),
(25,	'chips',	5,	1.49),
(26,	'jacket potato',	5,	2.50),
(27,	'soup of the day',	5,	2.50),
(28,	'fresh salmon fillet',	4,	4.99),
(29,	'spicy bean burger',	4,	4.99),
(30,	'bigger breakfast',	4,	5.99),
(31,	'bigger halloumi breakfast',	4,	5.99),
(32,	'sweet potato katsu curry',	4,	4.99),
(33,	'steak and red wine gravy pie',	4,	5.50),
(34,	'hand battered fish and chips',	4,	5.99),
(35,	'sausage and mash',	4,	4.99),
(36,	'cottage pie',	4,	4.99),
(37,	'beef lasagne',	4,	4.99),
(38,	'mediterranean vegetable lasagne',	4,	4.99),
(39,	'latte',	2,	2.15),
(40,	'flavoured latte',	2,	2.35),
(41,	'cappuccino',	2,	2.00),
(42,	'americano',	2,	2.15),
(43,	'flat white',	2,	2.15),
(44,	'cortado',	2,	2.15),
(45,	'mocha',	2,	2.15),
(46,	'esspresso',	2,	1.99),
(47,	'filter coffee',	2,	1.50),
(48,	'chai latte',	2,	1.99),
(49,	'hot chocolate',	2,	2.15),
(50,	'flavoured hot chocolate',	2,	2.35),
(51,	'luxury hot chocolate',	2,	2.75),
(52,	'tea',	2,	0.99),
(53,	'speciality tea',	2,	1.15),
(54,	'iced latte',	2,	2.15),
(55,	'frappe',	2,	2.75),
(56,	'smoothie',	2,	3.50),
(57,	'babyccino',	2,	0.50),
(58,	'milk',	1,	0.50),
(59,	'pepsi',	1,	1.35),
(60,	'pepsi max',	1,	1.35),
(61,	'j20 raspberry',	1,	1.50),
(62,	'j20 orange',	1,	1.50),
(63,	'fruit shoot',	1,	0.99),
(64,	'water',	1,	0.80),
(65,	'sprite',	1,	1.35),
(66,	'apple pie',	7,	1.99),
(67,	'ice cream',	7,	1.50),
(68,	'sticky toffee pudding',	7,	1.99),
(69,	'tiramissu',	7,	2.50),
(70,	'butter portion',	8,	0.50),
(71,	'honey',	8,	0.50),
(72,	'kettle crisps',	8,	0.90);

DROP TABLE IF EXISTS `status`;
CREATE TABLE `status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `style` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `status` (`id`, `code`, `style`) VALUES
(1,	'pending',	'Blue'),
(2,	'accepted',	'Cyan'),
(3,	'preparing',	'Yellow'),
(4,	'dispatched',	'Green'),
(5,	'cancelled',	'Red'),
(6,	'delivered',	'White');
