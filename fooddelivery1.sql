-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: CURRENT_TIMESTAMP
-- Server version: 5.7.19
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fooddelivery1`
--
CREATE DATABASE IF NOT EXISTS `fooddelivery1` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `fooddelivery1`;

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
CREATE TABLE IF NOT EXISTS `customer` (
  `customer_id` VARCHAR(32) NOT NULL,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `phone_number` VARCHAR(20) NOT NULL,
  `latitude` DECIMAL(10,8) NOT NULL,
  `longitude` DECIMAL(11,8) NOT NULL,
  `loyalty_points` INT(11) NOT NULL DEFAULT 0,
  `loyalty_status` ENUM('Bronze', 'Silver', 'Gold') NOT NULL DEFAULT 'Bronze',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`customer_id`, `username`, `password_hash`, `name`, `email`, `phone_number`, `latitude`, `longitude`, `loyalty_points`, `loyalty_status`, `created_at`) VALUES
('CUST001', 'alice_j', 'hashed_password_1', 'Alice Johnson', 'alice@example.com', '+1234567890', 40.712776, -74.005974, 120, 'Silver', NOW()),
('CUST002', 'bob_s', 'hashed_password_2', 'Bob Smith', 'bob@example.com', '+1987654321', 34.052235, -118.243683, 300, 'Gold', NOW()),
('CUST003', 'charlie_l', 'hashed_password_3', 'Charlie Lee', 'charlie@example.com', '+1122334455', 41.878113, -87.629799, 50, 'Bronze', NOW());

--
-- Table structure for table `restaurant`
--

DROP TABLE IF EXISTS `restaurant`;
CREATE TABLE IF NOT EXISTS `restaurant` (
  `restaurant_id` VARCHAR(32) NOT NULL,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `latitude` DECIMAL(10,8) NOT NULL,
  `longitude` DECIMAL(11,8) NOT NULL,
  `contact_number` VARCHAR(20) NOT NULL,
  `cuisine_type` VARCHAR(100) NOT NULL,
  `rating` DECIMAL(2,1) NOT NULL DEFAULT 0.0,
  `image_url` VARCHAR(255) NOT NULL,  -- Added image URL column
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`restaurant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Dumping data for table `restaurant`
--

INSERT INTO `restaurant` (
  `restaurant_id`, `username`, `password_hash`, `name`, `latitude`, `longitude`, 
  `contact_number`, `cuisine_type`, `rating`, `created_at`, `image_url`
) VALUES
('REST001', 'gourmet_delight', 'hashed_password_1', 'Gourmet Delight', 40.712776, -74.005974, '+1122334455', 'Italian', 5.0, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//italian.jpg'),

('REST002', 'spicy_fusion', 'hashed_password_2', 'Spicy Fusion', 34.052235, -118.243683, '+2233445566', 'Indian', 4.9, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//indian.jpg'),

('REST003', 'green_eats', 'hashed_password_3', 'Green Eats', 37.774929, -122.419418, '+3344556677', 'Vegan', 4.8, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//vegan.jpg'),

('REST004', 'bbq_haven', 'hashed_password_4', 'BBQ Haven', 41.878113, -87.629799, '+4455667788', 'BBQ', 4.6, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//bbq.jpg'),

('REST005', 'sushi_world', 'hashed_password_5', 'Sushi World', 35.689487, 139.691711, '+5566778899', 'Japanese', 4.7, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//japanese.jpg'),

('REST006', 'french_bistro', 'hashed_password_6', 'French Bistro', 48.856613, 2.352222, '+6677889900', 'French', 4.6, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//french.jpg'),

('REST007', 'thai_express', 'hashed_password_7', 'Thai Express', 13.756331, 100.501762, '+7788990011', 'Thai', 4.4, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//thai.jpg'),

('REST008', 'mexican_fiesta', 'hashed_password_8', 'Mexican Fiesta', 19.432608, -99.133209, '+8899001122', 'Mexican', 4.3, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//mexican.jpg'),

('REST009', 'korean_bbq', 'hashed_password_9', 'Korean BBQ', 37.566536, 126.977966, '+9900112233', 'Korean', 4.6, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//korean.jpg'),

('REST010', 'mediterranean_delight', 'hashed_password_10', 'Mediterranean Delight', 36.721274, -4.421398, '+0011223344', 'Mediterranean', 4.5, NOW(), 
'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//mediterranean.jpg');


--
-- Table structure for table `restaurant_inventory`
--

DROP TABLE IF EXISTS `restaurant_inventory`;
CREATE TABLE IF NOT EXISTS `restaurant_inventory` (
  `item_id` INT(11) NOT NULL AUTO_INCREMENT,
  `restaurant_id` VARCHAR(32) NOT NULL,
  `item_name` VARCHAR(255) NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `stock_quantity` INT(11) NOT NULL,
  `image_url` VARCHAR(255) NOT NULL,
  `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Dumping data for table `restaurant_inventory`
--
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST001', 'Spaghetti Carbonara', 10.99, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//carbonara.jpg', NOW()),
('REST001', 'Lasagna', 13.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//lasagna.jpg', NOW()),
('REST001', 'Bruschetta', 5.49, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//bruschetta.jpg', NOW()),
('REST001', 'Tiramisu', 6.99, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//tiramisu.jpg', NOW()),
('REST001', 'Caprese Salad', 8.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//caprese.jpg', NOW()),
('REST001', 'Fettuccine Alfredo', 11.99, 45, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//alfredo.jpg', NOW()),
('REST001', 'Cannoli', 4.99, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//cannoli.jpg', NOW());

INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST002', 'Butter Chicken', 11.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//butter%20chicken.jpg', NOW()),
('REST002', 'Chicken Tikka Masala', 10.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//chicken%20tikka%20masala.jpg', NOW()),
('REST002', 'Biryani', 12.99, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//biryani.jpg', NOW()),
('REST002', 'Samosas', 4.99, 80, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//samosas.jpg', NOW()),
('REST002', 'Paneer Tikka', 8.99, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//paneer%20tikka.jpg', NOW()),
('REST002', 'Mango Lassi', 3.49, 90, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//mango%20lassi.jpg', NOW()),
('REST002', 'Naan', 2.49, 100, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//naan.jpg', NOW());


INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST003', 'Vegan Buddha Bowl', 9.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Tofu Stir Fry', 8.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Vegan Tacos', 10.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Lentil Soup', 7.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Vegan Burrito', 11.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Falafel Wrap', 9.29, 35, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Avocado Toast', 7.49, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST004 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST004', 'Pulled Pork Sandwich', 9.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'BBQ Chicken Wings', 10.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'Mac & Cheese', 5.99, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'Smoked Brisket', 14.99, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'Grilled Corn', 3.49, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'BBQ Pulled Jackfruit', 8.49, 35, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'Potato Salad', 4.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST005 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST005', 'Dragon Roll', 13.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Tuna Sashimi', 12.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Shrimp Tempura', 9.99, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Ramen', 10.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Katsu Curry', 11.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Takoyaki', 6.49, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Onigiri', 3.99, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST006 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST006', 'Croissant', 2.99, 100, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Quiche Lorraine', 8.99, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Beef Bourguignon', 15.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'French Onion Soup', 6.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Ratatouille', 10.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Crepe Suzette', 7.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Escargot', 12.99, 25, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST007 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST007', 'Pad Thai', 9.99, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Green Curry', 10.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Tom Yum Soup', 8.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Mango Sticky Rice', 5.99, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Spring Rolls', 4.49, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Papaya Salad', 7.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Thai Milk Tea', 3.99, 80, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST008 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST008', 'Tacos Al Pastor', 10.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Burrito Bowl', 11.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Enchiladas', 9.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Quesadilla', 8.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Nachos Supreme', 6.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Guacamole', 4.99, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Horchata', 3.99, 80, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST009 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST009', 'Bibimbap', 9.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Kimchi Fried Rice', 8.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Tteokbokki', 6.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Bulgogi', 12.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Korean Fried Chicken', 11.49, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Japchae', 10.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Soju', 3.99, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST010 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST010', 'Falafel Platter', 9.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Hummus & Pita', 7.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Greek Salad', 8.49, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Shawarma Wrap', 9.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Baklava', 5.99, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Tabbouleh', 6.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Lemon Mint Drink', 3.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());


--
-- Table structure for table `voucher`
--

DROP TABLE IF EXISTS `voucher`;
CREATE TABLE IF NOT EXISTS `voucher` (
  `voucher_id` VARCHAR(32) NOT NULL,
  `code` VARCHAR(50) NOT NULL UNIQUE,
  `discount_percentage` DECIMAL(5,2) NOT NULL,
  `max_discount_amount` DECIMAL(10,2) NOT NULL,
  `expiry_date` DATE NOT NULL,
  `status` ENUM('Active', 'Expired', 'Used') NOT NULL DEFAULT 'Active',
  `customer_id` VARCHAR(32) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`voucher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `voucher`
--

INSERT INTO `voucher` (`voucher_id`, `code`, `discount_percentage`, `max_discount_amount`, `expiry_date`, `status`, `customer_id`, `created_at`) VALUES
('VOUCH001', 'DISCOUNT10', 10.00, 5.00, '2025-12-31', 'Active', 'CUST001', NOW()),
('VOUCH002', 'WELCOME5', 5.00, 3.00, '2025-11-30', 'Active', 'CUST001', NOW()),
('VOUCH003', 'GOLD15', 15.00, 7.50, '2025-12-31', 'Active', 'CUST002', NOW()),
('VOUCH004', 'FREESHIP10', 10.00, 5.00, '2025-10-31', 'Active', 'CUST002', NOW()),
('VOUCH005', 'BRONZE3', 3.00, 2.00, '2025-09-30', 'Active', 'CUST003', NOW()),
('VOUCH006', 'LOYALTY7', 7.00, 4.00, '2025-12-31', 'Active', 'CUST003', NOW()),
('VOUCH007', 'SILVER10', 10.00, 5.00, '2025-12-31', 'Active', 'CUST001', NOW()),
('VOUCH008', 'FLASH20', 20.00, 10.00, '2025-11-30', 'Active', 'CUST001', NOW()),
('VOUCH009', 'SPEND50', 15.00, 7.50, '2025-12-31', 'Active', 'CUST001', NOW()),
('VOUCH010', 'BIGSAVE', 5.00, 3.00, '2025-10-31', 'Active', 'CUST002', NOW()),
('VOUCH011', 'EXTRASAVER', 7.00, 4.00, '2025-12-31', 'Active', 'CUST003', NOW());


--
-- Table structure for table `rider`
--

DROP TABLE IF EXISTS `rider`;
CREATE TABLE IF NOT EXISTS `rider` (
  `rider_id` VARCHAR(32) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `phone_number` VARCHAR(20) NOT NULL,
  `vehicle_type` ENUM('Bicycle', 'Motorcycle', 'Car') NOT NULL,
  `availability_status` ENUM('Available', 'On Delivery', 'Offline') NOT NULL DEFAULT 'Available',
  `latitude` DECIMAL(10,8) NOT NULL,
  `longitude` DECIMAL(11,8) NOT NULL,
  `assigned_transaction_id` VARCHAR(32) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rider_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `rider`
--

INSERT INTO `rider` (`rider_id`, `name`, `phone_number`, `vehicle_type`, `availability_status`, `latitude`, `longitude`, `assigned_transaction_id`, `created_at`) VALUES
('RIDER001', 'John Doe', '+1111111111', 'Motorcycle', 'On Delivery', 40.754932, -73.984016, 'TRANS001', NOW()),
('RIDER002', 'Jane Smith', '+2222222222', 'Bicycle', 'Available', 34.044727, -118.249283, NULL, NOW()),
('RIDER003', 'Mike Johnson', '+3333333333', 'Car', 'On Delivery', 41.878113, -87.629799, 'TRANS009', NOW());

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
CREATE TABLE IF NOT EXISTS `notification` (
  `notification_id` VARCHAR(32) NOT NULL,
  `customer_id` VARCHAR(32) NOT NULL,
  `message_type` ENUM('Payment_Success', 'Refund_Processed', 'Loyalty_Updated') NOT NULL,
  `transaction_id` VARCHAR(32) DEFAULT NULL,
  `voucher_id` VARCHAR(32) DEFAULT NULL,
  `loyalty_points` INT(11) DEFAULT NULL,
  `loyalty_status` ENUM('Bronze', 'Silver', 'Gold') DEFAULT NULL,
  `status` ENUM('Unread', 'Read') NOT NULL DEFAULT 'Unread',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `notification`
--

INSERT INTO `notification` (`notification_id`, `customer_id`, `message_type`, `transaction_id`, `voucher_id`, `loyalty_points`, `loyalty_status`, `status`, `created_at`) VALUES
('NOTIF001', 'CUST001', 'Payment_Success', 'TRANS001', NULL, 10, 'Silver', 'Unread', NOW()),
('NOTIF002', 'CUST001', 'Payment_Success', 'TRANS002', NULL, 8, 'Silver', 'Unread', NOW()),
('NOTIF003', 'CUST001', 'Payment_Success', 'TRANS003', NULL, 15, 'Silver', 'Unread', NOW()),
('NOTIF004', 'CUST001', 'Payment_Success', 'TRANS004', NULL, 12, 'Silver', 'Unread', NOW()),
('NOTIF005', 'CUST001', 'Refund_Processed', 'TRANS005', 'VOUCH002', NULL, NULL, 'Unread', NOW()),
('NOTIF006', 'CUST002', 'Payment_Success', 'TRANS006', NULL, 20, 'Gold', 'Unread', NOW()),
('NOTIF007', 'CUST002', 'Payment_Success', 'TRANS007', NULL, 18, 'Gold', 'Unread', NOW()),
('NOTIF008', 'CUST002', 'Payment_Success', 'TRANS008', NULL, 25, 'Gold', 'Unread', NOW()),
('NOTIF009', 'CUST002', 'Payment_Success', 'TRANS009', NULL, 22, 'Gold', 'Unread', NOW()),
('NOTIF010', 'CUST002', 'Refund_Processed', 'TRANS010', 'VOUCH004', NULL, NULL, 'Unread', NOW()),
('NOTIF011', 'CUST003', 'Payment_Success', 'TRANS011', NULL, 5, 'Bronze', 'Unread', NOW()),
('NOTIF012', 'CUST003', 'Payment_Success', 'TRANS012', NULL, 7, 'Bronze', 'Unread', NOW()),
('NOTIF013', 'CUST003', 'Payment_Success', 'TRANS013', NULL, 12, 'Bronze', 'Unread', NOW()),
('NOTIF014', 'CUST003', 'Payment_Success', 'TRANS014', NULL, 10, 'Bronze', 'Unread', NOW()),
('NOTIF015', 'CUST003', 'Refund_Processed', 'TRANS015', 'VOUCH005', NULL, NULL, 'Unread', NOW());

--
-- Table structure for table `transaction`
--

DROP TABLE IF EXISTS `transaction`;
CREATE TABLE IF NOT EXISTS `transaction` (
  `transaction_id` VARCHAR(32) NOT NULL,
  `customer_id` VARCHAR(32) NOT NULL,
  `food_cost` DECIMAL(10,2) NOT NULL,
  `delivery_cost` DECIMAL(10,2) NOT NULL,
  `loyalty_discount_percentage` DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  `total_price_after_discount` DECIMAL(10,2) NOT NULL,
  `loyalty_points_added` INT(11) NOT NULL DEFAULT 0,
  `current_loyalty_points` INT(11) NOT NULL DEFAULT 0,
  `current_loyalty_status` ENUM('Bronze', 'Silver', 'Gold') NOT NULL DEFAULT 'Bronze',
  `status` ENUM('Pending', 'Submitted', 'Paid', 'Refunded', 'Cancelled') NOT NULL DEFAULT 'Pending',
  `voucher_id` VARCHAR(32) DEFAULT NULL,
  `rider_id` VARCHAR(32) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`transaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Dumping data for table `transaction`
--

INSERT INTO `transaction` (`transaction_id`, `customer_id`, `food_cost`, `delivery_cost`, `loyalty_discount_percentage`, `total_price_after_discount`, `loyalty_points_added`, `current_loyalty_points`, `current_loyalty_status`, `status`, `voucher_id`, `rider_id`, `created_at`, `updated_at`) VALUES
('TRANS001', 'CUST001', 10.99, 5.00, 5.00, 15.24, 10, 130, 'Silver', 'Paid', NULL, 'RIDER001', '2025-03-02 17:34:24', '2025-03-02 17:34:24'),
('TRANS002', 'CUST001', 4.99, 4.00, 5.00, 8.54, 8, 138, 'Silver', 'Paid', 'VOUCH001', 'RIDER002', '2025-03-14 11:21:07', '2025-03-14 11:21:07'),
('TRANS003', 'CUST001', 7.49, 6.00, 5.00, 12.82, 15, 153, 'Silver', 'Pending', NULL, NULL, '2025-03-29 16:34:17', '2025-03-29 16:34:17'),
('TRANS004', 'CUST001', 5.99, 5.50, 5.00, 10.91, 12, 165, 'Silver', 'Submitted', 'VOUCH002', 'RIDER003', '2025-03-22 06:16:45', '2025-03-22 06:16:45'),
('TRANS005', 'CUST001', 12.49, 4.50, 5.00, 16.14, 9, 174, 'Silver', 'Cancelled', NULL, NULL, '2025-03-07 15:29:16', '2025-03-07 15:29:16'),
('TRANS006', 'CUST002', 13.49, 5.50, 10.00, 17.09, 20, 320, 'Gold', 'Paid', 'VOUCH003', 'RIDER002', '2025-03-27 11:25:33', '2025-03-27 11:25:33'),
('TRANS007', 'CUST002', 8.99, 4.00, 10.00, 11.69, 18, 338, 'Gold', 'Submitted', NULL, 'RIDER001', '2025-03-09 05:40:11', '2025-03-09 05:40:11'),
('TRANS008', 'CUST002', 9.99, 7.00, 10.00, 15.29, 25, 363, 'Gold', 'Pending', NULL, NULL, '2025-03-21 18:51:28', '2025-03-21 18:51:28'),
('TRANS009', 'CUST002', 14.99, 5.00, 10.00, 17.99, 22, 385, 'Gold', 'Paid', NULL, 'RIDER003', '2025-03-19 21:58:44', '2025-03-19 21:58:44'),
('TRANS010', 'CUST002', 11.49, 6.00, 10.00, 15.74, 30, 415, 'Gold', 'Refunded', 'VOUCH004', NULL, '2025-03-22 19:23:45', '2025-03-22 19:23:45'),
('TRANS011', 'CUST003', 5.49, 4.50, 0.00, 9.99, 5, 55, 'Bronze', 'Paid', NULL, 'RIDER001', '2025-03-14 17:41:06', '2025-03-14 17:41:06'),
('TRANS012', 'CUST003', 3.49, 5.00, 0.00, 8.49, 7, 62, 'Bronze', 'Submitted', 'VOUCH005', 'RIDER002', '2025-03-03 11:01:39', '2025-03-03 11:01:39'),
('TRANS013', 'CUST003', 8.99, 7.50, 0.00, 16.49, 12, 74, 'Bronze', 'Pending', NULL, NULL, '2025-03-22 00:55:31', '2025-03-22 00:55:31'),
('TRANS014', 'CUST003', 3.49, 6.50, 0.00, 9.99, 10, 84, 'Bronze', 'Paid', NULL, 'RIDER003', '2025-03-08 05:01:33', '2025-03-08 05:01:33'),
('TRANS015', 'CUST003', 8.49, 3.50, 0.00, 11.99, 4, 88, 'Bronze', 'Cancelled', NULL, NULL, '2025-03-16 09:08:45', '2025-03-16 09:08:45'),
('TRANS017', 'CUST001', 53.44, 4.50, 5.00, 55.03, 10, 199, 'Silver', 'Paid', 'VOUCH007', 'RIDER001', '2025-03-11 14:53:22', '2025-03-11 14:53:22'),
('TRANS018', 'CUST001', 49.93, 5.00, 5.00, 52.18, 12, 211, 'Silver', 'Paid', 'VOUCH008', 'RIDER002', '2025-03-07 10:00:26', '2025-03-07 10:00:26'),
('TRANS019', 'CUST001', 58.93, 3.50, 5.00, 59.31, 9, 220, 'Silver', 'Submitted', NULL, 'RIDER003', '2025-03-22 08:38:32', '2025-03-22 08:38:32'),
('TRANS020', 'CUST001', 53.94, 4.00, 5.00, 54.94, 8, 228, 'Silver', 'Pending', NULL, NULL, '2025-03-22 13:38:44', '2025-03-22 13:38:44'),
('TRANS021', 'CUST001', 57.44, 5.50, 5.00, 59.79, 11, 239, 'Silver', 'Paid', 'VOUCH009', 'RIDER001', '2025-03-01 06:14:40', '2025-03-01 06:14:40'),
('TRANS022', 'CUST001', 58.94, 6.00, 5.00, 61.74, 15, 254, 'Silver', 'Submitted', 'VOUCH010', 'RIDER002', '2025-03-06 18:18:51', '2025-03-06 18:18:51'),
('TRANS023', 'CUST001', 41.44, 3.00, 5.00, 42.22, 7, 261, 'Silver', 'Pending', NULL, NULL, '2025-03-23 01:44:53', '2025-03-23 01:44:53'),
('TRANS024', 'CUST001', 53.44, 5.00, 5.00, 55.52, 13, 274, 'Silver', 'Paid', 'VOUCH011', 'RIDER003', '2025-03-01 21:24:53', '2025-03-01 21:24:53'),
('TRANS025', 'CUST001', 53.44, 4.50, 5.00, 55.03, 10, 284, 'Silver', 'Refunded', NULL, NULL, '2025-03-09 17:56:43', '2025-03-09 17:56:43');


--
-- Table structure for table `transaction_item`
--

DROP TABLE IF EXISTS `transaction_item`;
CREATE TABLE IF NOT EXISTS `transaction_item` (
  `transaction_item_id` INT(11) NOT NULL AUTO_INCREMENT,
  `transaction_id` VARCHAR(32) NOT NULL,
  `restaurant_id` VARCHAR(32) NOT NULL,
  `item_id` INT(11) NOT NULL,
  `quantity` INT(11) NOT NULL,
  `price_per_item` DECIMAL(10,2) NOT NULL,
  `total_price` DECIMAL(10,2) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`transaction_item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `transaction_item`
--

INSERT INTO `transaction_item` (`transaction_id`, `restaurant_id`, `item_id`, `quantity`, `price_per_item`, `total_price`, `created_at`) VALUES
('TRANS001', 'REST001', 1, 1, 10.99, 10.99, NOW()),
('TRANS002', 'REST002', 4, 1, 4.99, 4.99, NOW()),
('TRANS003', 'REST003', 7, 1, 7.49, 7.49, NOW()),
('TRANS004', 'REST004', 10, 1, 5.99, 5.99, NOW()),
('TRANS005', 'REST005', 13, 1, 12.49, 12.49, NOW()),
('TRANS006', 'REST001', 2, 1, 13.49, 13.49, NOW()),
('TRANS007', 'REST002', 5, 1, 8.99, 8.99, NOW()),
('TRANS008', 'REST003', 8, 1, 9.99, 9.99, NOW()),
('TRANS009', 'REST004', 11, 1, 14.99, 14.99, NOW()),
('TRANS010', 'REST005', 14, 1, 11.49, 11.49, NOW()),
('TRANS011', 'REST001', 3, 1, 5.49, 5.49, NOW()),
('TRANS012', 'REST002', 6, 1, 3.49, 3.49, NOW()),
('TRANS013', 'REST003', 9, 1, 8.99, 8.99, NOW()),
('TRANS014', 'REST004', 12, 1, 3.49, 3.49, NOW()),
('TRANS015', 'REST001', 15, 1, 8.49, 8.49, NOW()),
('TRANS017', 'REST001', 1, 1, 10.99, 10.99, NOW()),
('TRANS017', 'REST001', 2, 2, 13.49, 26.98, NOW()),
('TRANS017', 'REST001', 3, 1, 5.49, 5.49, NOW()),
('TRANS017', 'REST001', 4, 2, 4.99, 9.98, NOW()),
('TRANS018', 'REST001', 5, 1, 8.99, 8.99, NOW()),
('TRANS018', 'REST008', 30, 1, 9.99, 9.99, NOW()),
('TRANS018', 'REST008', 31, 2, 8.49, 16.98, NOW()),
('TRANS018', 'REST008', 32, 2, 6.99, 13.98, NOW()),
('TRANS019', 'REST009', 33, 1, 9.99, 9.99, NOW()),
('TRANS019', 'REST009', 34, 2, 8.49, 16.98, NOW()),
('TRANS019', 'REST009', 35, 1, 6.99, 6.99, NOW()),
('TRANS019', 'REST009', 36, 2, 12.49, 24.98, NOW()),
('TRANS020', 'REST010', 37, 1, 9.49, 9.49, NOW()),
('TRANS020', 'REST010', 38, 2, 7.99, 15.98, NOW()),
('TRANS020', 'REST010', 39, 1, 8.49, 8.49, NOW()),
('TRANS020', 'REST010', 40, 2, 9.99, 19.98, NOW()),
('TRANS021', 'REST004', 11, 1, 14.99, 14.99, NOW()),
('TRANS021', 'REST004', 12, 2, 3.49, 6.98, NOW()),
('TRANS021', 'REST004', 13, 1, 12.49, 12.49, NOW()),
('TRANS021', 'REST004', 14, 2, 11.49, 22.98, NOW()),
('TRANS022', 'REST009', 33, 1, 9.99, 9.99, NOW()),
('TRANS022', 'REST009', 34, 2, 8.49, 16.98, NOW()),
('TRANS022', 'REST009', 35, 1, 6.99, 6.99, NOW()),
('TRANS022', 'REST009', 36, 2, 12.49, 24.98, NOW()),
('TRANS023', 'REST002', 4, 1, 4.99, 4.99, NOW()),
('TRANS023', 'REST002', 5, 2, 8.99, 17.98, NOW()),
('TRANS023', 'REST002', 6, 1, 3.49, 3.49, NOW()),
('TRANS023', 'REST002', 7, 2, 7.49, 14.98, NOW()),
('TRANS024', 'REST001', 1, 1, 10.99, 10.99, NOW()),
('TRANS024', 'REST001', 2, 2, 13.49, 26.98, NOW()),
('TRANS024', 'REST001', 3, 1, 5.49, 5.49, NOW()),
('TRANS024', 'REST001', 4, 2, 4.99, 9.98, NOW()),
('TRANS025', 'REST001', 1, 1, 10.99, 10.99, NOW()),
('TRANS025', 'REST001', 2, 2, 13.49, 26.98, NOW()),
('TRANS025', 'REST001', 3, 1, 5.49, 5.49, NOW()),
('TRANS025', 'REST001', 4, 2, 4.99, 9.98, NOW());

-- Add foreign keys to the transaction table
ALTER TABLE `transaction` 
ADD CONSTRAINT `fk_transaction_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`customer_id`) ON DELETE CASCADE,
ADD CONSTRAINT `fk_transaction_voucher` FOREIGN KEY (`voucher_id`) REFERENCES `voucher` (`voucher_id`) ON DELETE SET NULL,
ADD CONSTRAINT `fk_transaction_rider` FOREIGN KEY (`rider_id`) REFERENCES `rider` (`rider_id`) ON DELETE SET NULL;

-- Add foreign keys to the transaction_item table
ALTER TABLE `transaction_item`
ADD CONSTRAINT `fk_transaction_item_transaction` FOREIGN KEY (`transaction_id`) REFERENCES `transaction` (`transaction_id`) ON DELETE CASCADE,
ADD CONSTRAINT `fk_transaction_item_restaurant` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant` (`restaurant_id`) ON DELETE CASCADE,
ADD CONSTRAINT `fk_transaction_item_item` FOREIGN KEY (`item_id`) REFERENCES `restaurant_inventory` (`item_id`) ON DELETE CASCADE;

-- Add foreign key to the restaurant_inventory table
ALTER TABLE `restaurant_inventory`
ADD CONSTRAINT `fk_restaurant_inventory_restaurant` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant` (`restaurant_id`) ON DELETE CASCADE;

-- Add foreign key to the rider table
ALTER TABLE `rider`
ADD CONSTRAINT `fk_rider_transaction` FOREIGN KEY (`assigned_transaction_id`) REFERENCES `transaction` (`transaction_id`) ON DELETE SET NULL;

-- Add foreign keys to the notification table
ALTER TABLE `notification`
ADD CONSTRAINT `fk_notification_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`customer_id`) ON DELETE CASCADE,
ADD CONSTRAINT `fk_notification_transaction` FOREIGN KEY (`transaction_id`) REFERENCES `transaction` (`transaction_id`) ON DELETE SET NULL,
ADD CONSTRAINT `fk_notification_voucher` FOREIGN KEY (`voucher_id`) REFERENCES `voucher` (`voucher_id`) ON DELETE SET NULL;

COMMIT;
