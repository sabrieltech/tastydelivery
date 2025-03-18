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
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`restaurant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `restaurant`
--

INSERT INTO `restaurant` (`restaurant_id`, `username`, `password_hash`, `name`, `latitude`, `longitude`, `contact_number`, `cuisine_type`, `rating`, `created_at`) VALUES
('REST001', 'gourmet_delight', 'hashed_password_1', 'Gourmet Delight', 40.712776, -74.005974, '+1122334455', 'Italian', 4.5, NOW()),
('REST002', 'spicy_fusion', 'hashed_password_2', 'Spicy Fusion', 34.052235, -118.243683, '+2233445566', 'Indian', 4.2, NOW()),
('REST003', 'green_eats', 'hashed_password_3', 'Green Eats', 37.774929, -122.419418, '+3344556677', 'Vegan', 4.8, NOW()),
('REST004', 'bbq_haven', 'hashed_password_4', 'BBQ Haven', 41.878113, -87.629799, '+4455667788', 'BBQ', 4.6, NOW()),
('REST005', 'sushi_world', 'hashed_password_5', 'Sushi World', 35.689487, 139.691711, '+5566778899', 'Japanese', 4.7, NOW());

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
  `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `restaurant_inventory`
--

INSERT INTO `restaurant_inventory` (`restaurant_id`, `item_name`, `price`, `stock_quantity`, `last_updated`) VALUES
('REST001', 'Cheeseburger', 8.99, 50, NOW()),
('REST001', 'French Fries', 3.49, 100, NOW()),
('REST001', 'Coke', 1.99, 200, NOW()),
('REST002', 'Margherita Pizza', 12.99, 30, NOW()),
('REST002', 'Garlic Bread', 4.99, 80, NOW()),
('REST002', 'Lemonade', 2.99, 150, NOW()),
('REST003', 'Sushi Roll', 14.99, 40, NOW()),
('REST003', 'Miso Soup', 2.99, 90, NOW()),
('REST003', 'Green Tea', 1.49, 120, NOW()),
('REST004', 'BBQ Ribs', 18.99, 25, NOW()),
('REST004', 'Cornbread', 3.99, 70, NOW()),
('REST004', 'Iced Tea', 2.49, 130, NOW()),
('REST005', 'Salmon Nigiri', 16.99, 35, NOW()),
('REST005', 'Tempura', 9.99, 60, NOW()),
('REST005', 'Matcha Latte', 4.49, 90, NOW());

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
('VOUCH004', 'FREESHIP', 10.00, 5.00, '2025-10-31', 'Active', 'CUST002', NOW()),
('VOUCH005', 'BRONZE3', 3.00, 2.00, '2025-09-30', 'Active', 'CUST003', NOW()),
('VOUCH006', 'LOYALTY7', 7.00, 4.00, '2025-12-31', 'Active', 'CUST003', NOW());

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
('TRANS001', 'CUST001', 25.00, 5.00, 5.00, 28.50, 10, 130, 'Silver', 'Paid', NULL, 'RIDER001', NOW(), NOW()),
('TRANS002', 'CUST001', 15.00, 4.00, 5.00, 18.05, 8, 138, 'Silver', 'Paid', 'VOUCH001', 'RIDER002', NOW(), NOW()),
('TRANS003', 'CUST001', 40.00, 6.00, 5.00, 43.70, 15, 153, 'Silver', 'Pending', NULL, NULL, NOW(), NOW()),
('TRANS004', 'CUST001', 30.00, 5.50, 5.00, 33.53, 12, 165, 'Silver', 'Submitted', 'VOUCH002', 'RIDER003', NOW(), NOW()),
('TRANS005', 'CUST001', 20.00, 4.50, 5.00, 23.28, 9, 174, 'Silver', 'Cancelled', NULL, NULL, NOW(), NOW()),
('TRANS006', 'CUST002', 22.00, 5.50, 10.00, 24.75, 20, 320, 'Gold', 'Paid', 'VOUCH003', 'RIDER002', NOW(), NOW()),
('TRANS007', 'CUST002', 18.00, 4.00, 10.00, 19.80, 18, 338, 'Gold', 'Submitted', NULL, 'RIDER001', NOW(), NOW()),
('TRANS008', 'CUST002', 50.00, 7.00, 10.00, 57.60, 25, 363, 'Gold', 'Pending', NULL, NULL, NOW(), NOW()),
('TRANS009', 'CUST002', 28.00, 5.00, 10.00, 29.70, 22, 385, 'Gold', 'Paid', NULL, 'RIDER003', NOW(), NOW()),
('TRANS010', 'CUST002', 35.00, 6.00, 10.00, 37.80, 30, 415, 'Gold', 'Refunded', 'VOUCH004', NULL, NOW(), NOW()),
('TRANS011', 'CUST003', 19.00, 4.50, 0.00, 23.50, 5, 55, 'Bronze', 'Paid', NULL, 'RIDER001', NOW(), NOW()),
('TRANS012', 'CUST003', 21.00, 5.00, 0.00, 26.00, 7, 62, 'Bronze', 'Submitted', 'VOUCH005', 'RIDER002', NOW(), NOW()),
('TRANS013', 'CUST003', 45.00, 7.50, 0.00, 52.50, 12, 74, 'Bronze', 'Pending', NULL, NULL, NOW(), NOW()),
('TRANS014', 'CUST003', 33.00, 6.50, 0.00, 39.50, 10, 84, 'Bronze', 'Paid', NULL, 'RIDER003', NOW(), NOW()),
('TRANS015', 'CUST003', 12.00, 3.50, 0.00, 15.50, 4, 88, 'Bronze', 'Cancelled', NULL, NULL, NOW(), NOW());

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
('TRANS001', 'REST001', 1, 1, 12.99, 12.99, NOW()),
('TRANS002', 'REST002', 4, 1, 9.99, 9.99, NOW()),
('TRANS003', 'REST003', 7, 1, 14.99, 14.99, NOW()),
('TRANS004', 'REST004', 10, 1, 19.99, 19.99, NOW()),
('TRANS005', 'REST005', 13, 1, 8.99, 8.99, NOW()),
('TRANS006', 'REST001', 2, 1, 6.99, 6.99, NOW()),
('TRANS007', 'REST002', 5, 1, 7.99, 7.99, NOW()),
('TRANS008', 'REST003', 8, 1, 11.99, 11.99, NOW()),
('TRANS009', 'REST004', 11, 1, 13.99, 13.99, NOW()),
('TRANS010', 'REST005', 14, 1, 9.49, 9.49, NOW()),
('TRANS011', 'REST001', 3, 1, 10.99, 10.99, NOW()),
('TRANS012', 'REST002', 6, 1, 5.99, 5.99, NOW()),
('TRANS013', 'REST003', 9, 1, 7.49, 7.49, NOW()),
('TRANS014', 'REST004', 12, 1, 15.99, 15.99, NOW()),
('TRANS015', 'REST005', 15, 1, 12.49, 12.49, NOW());

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
