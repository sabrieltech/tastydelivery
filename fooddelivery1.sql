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
  `restaurant_id` VARCHAR(32) NOT NULL,
  `item_name` VARCHAR(255) NOT NULL,
  `item_id` INT(11) NOT NULL,
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
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST001', 'Spaghetti Carbonara', 1, 10.99, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//carbonara.jpg', NOW()),
('REST001', 'Lasagna', 2, 13.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//lasagna.jpg', NOW()),
('REST001', 'Bruschetta', 3, 5.49, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//bruschetta.jpg', NOW()),
('REST001', 'Tiramisu', 4, 6.99, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//tiramisu.jpg', NOW()),
('REST001', 'Caprese Salad', 5, 8.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//caprese.jpg', NOW()),
('REST001', 'Fettuccine Alfredo', 6, 11.99, 45, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//alfredo.jpg', NOW()),
('REST001', 'Cannoli', 7, 4.99, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//cannoli.jpg', NOW());

INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST002', 'Butter Chicken', 8, 11.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//butter%20chicken.jpg', NOW()),
('REST002', 'Chicken Tikka Masala', 9, 10.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//chicken%20tikka%20masala.jpg', NOW()),
('REST002', 'Biryani', 10, 12.99, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//biryani.jpg', NOW()),
('REST002', 'Samosas', 11, 4.99, 80, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//samosas.jpg', NOW()),
('REST002', 'Paneer Tikka', 12, 8.99, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//paneer%20tikka.jpg', NOW()),
('REST002', 'Mango Lassi', 13, 3.49, 90, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//mango%20lassi.jpg', NOW()),
('REST002', 'Naan', 14, 2.49, 100, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//naan.jpg', NOW());


INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST003', 'Vegan Buddha Bowl', 15, 9.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Tofu Stir Fry', 16, 8.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Vegan Tacos', 17, 10.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Lentil Soup', 18, 7.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Vegan Burrito', 19, 11.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Falafel Wrap', 20, 9.29, 35, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST003', 'Avocado Toast', 21, 7.49, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST004 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST004', 'Pulled Pork Sandwich', 22, 9.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'BBQ Chicken Wings', 23, 10.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'Mac & Cheese', 24, 5.99, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'Smoked Brisket', 25, 14.99, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'Grilled Corn', 26, 3.49, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'BBQ Pulled Jackfruit', 27, 8.49, 35, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST004', 'Potato Salad', 28, 4.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST005 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST005', 'Dragon Roll', 29, 13.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Tuna Sashimi', 30, 12.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Shrimp Tempura', 31, 9.99, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Ramen', 32, 10.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Katsu Curry', 33, 11.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Takoyaki', 34, 6.49, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST005', 'Onigiri', 35, 3.99, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST006 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST006', 'Croissant', 36, 2.99, 100, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Quiche Lorraine', 37, 8.99, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Beef Bourguignon', 38, 15.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'French Onion Soup', 39, 6.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Ratatouille', 40, 10.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Crepe Suzette', 41, 7.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST006', 'Escargot', 42, 12.99, 25, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST007 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST007', 'Pad Thai', 43, 9.99, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Green Curry', 44, 10.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Tom Yum Soup', 45, 8.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Mango Sticky Rice', 46, 5.99, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Spring Rolls', 47, 4.49, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Papaya Salad', 48, 7.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST007', 'Thai Milk Tea', 49, 3.99, 80, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST008 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST008', 'Tacos Al Pastor', 50, 10.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Burrito Bowl', 51, 11.49, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Enchiladas', 52, 9.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Quesadilla', 53, 8.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Nachos Supreme', 54, 6.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Guacamole', 55, 4.99, 60, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST008', 'Horchata', 56, 3.99, 80, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST009 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST009', 'Bibimbap', 57, 9.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Kimchi Fried Rice', 58, 8.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Tteokbokki', 59, 6.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Bulgogi', 60, 12.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Korean Fried Chicken', 61, 11.49, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Japchae', 62, 10.49, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST009', 'Soju', 63, 3.99, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());

-- Update REST010 items
INSERT INTO `restaurant_inventory` 
(`restaurant_id`, `item_name`, `item_id`, `price`, `stock_quantity`, `image_url`, `last_updated`) 
VALUES
('REST010', 'Falafel Platter', 64, 9.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Hummus & Pita', 65, 7.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Greek Salad', 66, 8.49, 70, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Shawarma Wrap', 67, 9.99, 40, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Baklava', 68, 5.99, 30, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Tabbouleh', 69, 6.49, 50, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW()),
('REST010', 'Lemon Mint Drink', 70, 3.99, 0, 'https://dkfesmofervpcbwawjna.supabase.co/storage/v1/object/public/esdrestaurantimages//loading.jpg', NOW());


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
('NOTIF001', 'CUST001', 'Payment_Success', 'TRANS001', NULL, 10, 'Silver', 'Unread', '2025-03-02 17:35:24'),
('NOTIF002', 'CUST001', 'Payment_Success', 'TRANS002', NULL, 8, 'Silver', 'Unread', '2025-03-14 11:22:07'),
('NOTIF003', 'CUST001', 'Payment_Success', 'TRANS003', NULL, 15, 'Silver', 'Unread', '2025-03-09 19:45:33'),
('NOTIF004', 'CUST001', 'Payment_Success', 'TRANS004', NULL, 12, 'Silver', 'Unread', '2025-03-11 08:30:23'),
('NOTIF005', 'CUST001', 'Refund_Processed', 'TRANS005', 'VOUCH002', NULL, NULL, 'Unread', '2025-03-07 15:30:16'),
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

-- Notifications for Completed Transactions
INSERT INTO `notification` (`notification_id`, `customer_id`, `message_type`, `transaction_id`, `voucher_id`, `loyalty_points`, `loyalty_status`, `status`, `created_at`) VALUES
-- CUST001 Payment Notifications
('NOTIF016', 'CUST002', 'Payment_Success', 'TRANS016', NULL, 10, 'Silver', 'Unread', '2025-03-10 09:09:45'),
('NOTIF017', 'CUST001', 'Refund_Processed', 'TRANS017', 'VOUCH001', 8, 'Silver', 'Unread', '2025-03-11 14:54:22'),
('NOTIF018', 'CUST001', 'Payment_Success', 'TRANS018', 'VOUCH007', 10, 'Silver', 'Unread', '2025-03-07 10:01:26'),
('NOTIF019', 'CUST002', 'Payment_Success', 'TRANS019', 'VOUCH008', 12, 'Silver', 'Unread', NOW()),
('NOTIF020', 'CUST002', 'Payment_Success', 'TRANS020', 'VOUCH009', 11, 'Silver', 'Unread', NOW()),
('NOTIF021', 'CUST001', 'Payment_Success', 'TRANS021', 'VOUCH011', 13, 'Silver', 'Unread', '2025-03-01 21:25:53'),

-- CUST001 Cancellation/Refund Notifications
('NOTIF022', 'CUST002', 'Refund_Processed', 'TRANS022', NULL, 9, 'Silver', 'Unread', NOW()),
('NOTIF023', 'CUST003', 'Refund_Processed', 'TRANS023', NULL, 10, 'Silver', 'Unread', NOW()),
('NOTIF024', 'CUST001', 'Payment_Success', 'TRANS024', 'VOUCH003', 20, 'Gold', 'Unread', '2025-03-02 21:25:53'),
('NOTIF025', 'CUST001', 'Payment_Success', 'TRANS025', NULL, 22, 'Gold', 'Unread', '2025-03-09 17:57:43');

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

INSERT INTO `transaction` (`transaction_id`, `customer_id`, `food_cost`, `delivery_cost`, `loyalty_discount_percentage`, `total_price_after_discount`, `loyalty_points_added`, `current_loyalty_points`, `current_loyalty_status`, `status`, `voucher_id`, `rider_id`, `created_at`) VALUES
('TRANS001', 'CUST001', 10.99, 2.99, 0.00, 13.98, 10, 130, 'Silver', 'Paid', NULL, 'RIDER001', '2025-03-02 17:35:24'),
('TRANS002', 'CUST001', 11.99, 2.99, 5.00, 14.23, 8, 138, 'Silver', 'Paid', 'VOUCH001', NULL, '2025-03-14 11:22:07'),
('TRANS003', 'CUST001', 9.99, 2.99, 0.00, 12.98, 15, 153, 'Silver', 'Paid', NULL, NULL, '2025-03-09 19:45:33'),
('TRANS004', 'CUST001', 9.99, 2.99, 0.00, 12.98, 12, 165, 'Silver', 'Paid', NULL, NULL, '2025-03-11 08:30:23'),
('TRANS005', 'CUST001', 13.99, 2.99, 5.00, 16.13, 9, 174, 'Silver', 'Refunded', 'VOUCH002', NULL, '2025-03-07 15:30:16'),
('TRANS006', 'CUST002', 13.49, 2.99, 15.00, 14.01, 20, 320, 'Gold', 'Paid', 'VOUCH003', NULL, '2025-03-27 11:26:33'),
('TRANS007', 'CUST002', 10.49, 2.99, 0.00, 13.48, 18, 338, 'Gold', 'Paid', NULL, NULL, NOW()),
('TRANS008', 'CUST002', 9.99, 2.99, 0.00, 12.98, 25, 363, 'Gold', 'Paid', NULL, NULL, NOW()),
('TRANS009', 'CUST002', 14.99, 2.99, 0.00, 17.98, 22, 385, 'Gold', 'Paid', NULL, 'RIDER003', '2025-03-19 21:59:44'),
('TRANS010', 'CUST002', 9.99, 2.99, 10.00, 11.68, 30, 415, 'Gold', 'Refunded', 'VOUCH004', NULL, '2025-03-22 19:24:45'),
('TRANS011', 'CUST003', 5.49, 2.99, 0.00, 8.48, 5, 55, 'Bronze', 'Paid', NULL, NULL, '2025-03-14 17:42:06'),
('TRANS012', 'CUST003', 3.49, 2.99, 0.00, 6.48, 7, 62, 'Bronze', 'Paid', NULL, NULL, NOW()),
('TRANS013', 'CUST003', 10.49, 2.99, 0.00, 13.48, 12, 74, 'Bronze', 'Paid', NULL, NULL, NOW()),
('TRANS014', 'CUST003', 3.49, 2.99, 0.00, 6.48, 10, 84, 'Bronze', 'Paid', NULL, NULL, '2025-03-08 05:02:33'),
('TRANS015', 'CUST003', 11.99, 2.99, 3.00, 14.51, 4, 88, 'Bronze', 'Refunded', 'VOUCH005', NULL, '2025-03-16 09:09:45'),
('TRANS016', 'CUST002', 9.49, 2.99, 0.00, 12.48, 7, 177, 'Silver', 'Paid', NULL, NULL, '2025-03-10 09:09:45'),
('TRANS017', 'CUST001', 57.44, 2.99, 10.00, 54.39, 10, 184, 'Silver', 'Paid', 'VOUCH007', NULL, '2025-03-11 14:54:22'),
('TRANS018', 'CUST001', 58.94, 2.99, 20.00, 49.54, 12, 196, 'Silver', 'Paid', 'VOUCH008', NULL, '2025-03-07 10:01:26'),
('TRANS019', 'CUST002', 65.94, 2.99, 0.00, 68.93, 15, 400, 'Gold', 'Paid', NULL, NULL, NOW()),
('TRANS020', 'CUST002', 58.43, 2.99, 0.00, 61.42, 14, 414, 'Gold', 'Paid', NULL, NULL, NOW()),
('TRANS021', 'CUST001', 40.44, 2.99, 15.00, 36.91, 11, 207, 'Silver', 'Paid', 'VOUCH009', NULL, '2025-03-01 06:15:40'),
('TRANS022', 'CUST002', 65.94, 2.99, 5.00, 65.38, 13, 427, 'Gold', 'Paid', 'VOUCH010', NULL, NOW()),
('TRANS023', 'CUST003', 41.44, 2.99, 7.00, 41.31, 9, 97, 'Bronze', 'Paid', 'VOUCH011', NULL, NOW()),
('TRANS024', 'CUST001', 57.44, 2.99, 7.00, 56.20, 13, 220, 'Silver', 'Paid', 'VOUCH011', NULL, '2025-03-02 21:25:53'),
('TRANS025', 'CUST001', 57.44, 2.99, 0.00, 60.43, 10, 284, 'Silver', 'Refunded', NULL, NULL, '2025-03-09 17:57:43');

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
('TRANS002', 'REST002', 8, 1, 11.99, 11.99, NOW()),
('TRANS003', 'REST003', 15, 1, 9.99, 9.99, NOW()),
('TRANS004', 'REST004', 22, 1, 9.99, 9.99, NOW()),
('TRANS005', 'REST005', 29, 1, 13.99, 13.99, NOW()),
('TRANS006', 'REST001', 2, 1, 13.49, 13.49, NOW()),
('TRANS007', 'REST002', 9, 1, 10.49, 10.49, NOW()),
('TRANS008', 'REST003', 15, 1, 9.99, 9.99, NOW()),
('TRANS009', 'REST004', 25, 1, 14.99, 14.99, NOW()),
('TRANS010', 'REST005', 31, 1, 9.99, 9.99, NOW()),
('TRANS011', 'REST001', 3, 1, 5.49, 5.49, NOW()),
('TRANS012', 'REST002', 13, 1, 3.49, 3.49, NOW()),
('TRANS013', 'REST003', 17, 1, 10.49, 10.49, NOW()),
('TRANS014', 'REST004', 26, 1, 3.49, 3.49, NOW()),
('TRANS015', 'REST001', 6, 1, 11.99, 11.99, NOW()),
('TRANS017', 'REST001', 1, 1, 10.99, 10.99, NOW()),
('TRANS017', 'REST001', 2, 2, 13.49, 26.98, NOW()),
('TRANS017', 'REST001', 3, 1, 5.49, 5.49, NOW()),
('TRANS017', 'REST001', 4, 2, 6.99, 13.98, NOW()),
('TRANS018', 'REST008', 50, 1, 10.49, 10.49, NOW()),
('TRANS018', 'REST008', 51, 1, 11.49, 11.49, NOW()),
('TRANS018', 'REST008', 52, 2, 9.99, 19.98, NOW()),
('TRANS018', 'REST008', 53, 2, 8.49, 16.98, NOW()),
('TRANS019', 'REST009', 58, 1, 8.49, 8.49, NOW()),
('TRANS019', 'REST009', 60, 2, 12.49, 24.98, NOW()),
('TRANS019', 'REST009', 61, 1, 11.49, 11.49, NOW()),
('TRANS019', 'REST009', 62, 2, 10.49, 20.98, NOW()),
('TRANS020', 'REST010', 64, 1, 9.49, 9.49, NOW()),
('TRANS020', 'REST010', 66, 2, 8.49, 16.98, NOW()),
('TRANS020', 'REST010', 67, 2, 9.99, 19.98, NOW()),
('TRANS020', 'REST010', 68, 2, 5.99, 11.98, NOW()),
('TRANS021', 'REST004', 25, 1, 14.99, 14.99, NOW()),
('TRANS021', 'REST004', 26, 2, 3.49, 6.98, NOW()),
('TRANS021', 'REST004', 27, 1, 8.49, 8.49, NOW()),
('TRANS021', 'REST004', 28, 2, 4.99, 9.98, NOW()),
('TRANS022', 'REST009', 58, 1, 8.49, 8.49, NOW()),
('TRANS022', 'REST009', 60, 2, 12.49, 24.98, NOW()),
('TRANS022', 'REST009', 61, 1, 11.49, 11.49, NOW()),
('TRANS022', 'REST009', 62, 2, 10.49, 20.98, NOW()),
('TRANS023', 'REST002', 8, 1, 11.99, 11.99, NOW()),
('TRANS023', 'REST002', 9, 2, 10.49, 20.98, NOW()),
('TRANS023', 'REST002', 13, 1, 3.49, 3.49, NOW()),
('TRANS023', 'REST002', 14, 2, 2.49, 4.98, NOW()),
('TRANS024', 'REST001', 1, 1, 10.99, 10.99, NOW()),
('TRANS024', 'REST001', 2, 2, 13.49, 26.98, NOW()),
('TRANS024', 'REST001', 3, 1, 5.49, 5.49, NOW()),
('TRANS024', 'REST001', 4, 2, 6.99, 13.98, NOW()),
('TRANS025', 'REST001', 1, 1, 10.99, 10.99, NOW()),
('TRANS025', 'REST001', 2, 2, 13.49, 26.98, NOW()),
('TRANS025', 'REST001', 3, 1, 5.49, 5.49, NOW()),
('TRANS025', 'REST001', 4, 2, 6.99, 13.98, NOW());

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
