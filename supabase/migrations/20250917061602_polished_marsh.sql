-- Freepik Downloader Database Schema
-- Run this SQL to create the required database structure

CREATE DATABASE IF NOT EXISTS freepik CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE freepik;

-- Downloads table with improved structure
CREATE TABLE IF NOT EXISTS downloads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT NOT NULL,
    url_code VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NULL,
    status TINYINT DEFAULT 0 COMMENT '0=pending, 1=processed',
    download TINYINT DEFAULT 0 COMMENT '0=not ready, 1=ready for download',
    download_count INT DEFAULT 0,
    file_size BIGINT NULL,
    mime_type VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_checked TIMESTAMP NULL,
    last_downloaded TIMESTAMP NULL,
    error_message TEXT NULL,
    retry_count INT DEFAULT 0,
    
    INDEX idx_url_code (url_code),
    INDEX idx_status (status),
    INDEX idx_download (download),
    INDEX idx_created_at (created_at),
    UNIQUE KEY unique_url_code (url_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add some sample data (optional)
-- INSERT INTO downloads (url, url_code, filename, status, download) VALUES
-- ('https://www.freepik.com/free-photo/sample_123456.htm', '123456', 'sample-image', 1, 1);

-- Create downloads directory structure
-- Note: This should be created by the PHP application, but you can create it manually:
-- mkdir downloads/
-- chmod 755 downloads/