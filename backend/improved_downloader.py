#!/usr/bin/env python3
"""
Improved Freepik Downloader Backend
Enhanced version with better error handling, logging, and database management
"""

import os
import sys
import time
import json
import logging
import requests
import mysql.connector
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configuration
CONFIG = {
    'db': {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'freepik'
    },
    'freepik': {
        'email': 'tuffailxhehzad@gmail.com',
        'password': 'tuffail238',
        'login_url': 'https://www.freepik.com/login'
    },
    'chrome': {
        'driver_path': 'D:\\Downloads\\chromedriver-win64 (1)\\chromedriver-win64\\chromedriver.exe',
        'download_dir': os.path.abspath('./downloads'),
        'headless': False
    },
    'app': {
        'cookies_file': 'cookies.json',
        'log_file': 'downloader.log',
        'check_interval': 10,  # seconds
        'max_retries': 3,
        'timeout': 30
    }
}

class Logger:
    """Enhanced logging system"""
    
    def __init__(self, log_file='downloader.log'):
        self.logger = logging.getLogger('FreepikDownloader')
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)

class DatabaseManager:
    """Enhanced database management"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.logger.info("✅ Connected to database")
        except mysql.connector.Error as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def ensure_connection(self):
        """Ensure database connection is active"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
        except mysql.connector.Error as e:
            self.logger.error(f"❌ Failed to ensure database connection: {e}")
            raise
    
    def get_pending_downloads(self, limit=1):
        """Get pending downloads from database"""
        try:
            self.ensure_connection()
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT id, url, url_code, filename, retry_count 
                FROM downloads 
                WHERE status = 0 AND retry_count < %s
                ORDER BY created_at ASC 
                LIMIT %s
            """
            
            cursor.execute(query, (CONFIG['app']['max_retries'], limit))
            results = cursor.fetchall()
            cursor.close()
            
            return results
        except mysql.connector.Error as e:
            self.logger.error(f"❌ Failed to get pending downloads: {e}")
            return []
    
    def update_download_status(self, download_id, status, download_ready=None, 
                             file_path=None, error_message=None, increment_retry=False):
        """Update download status in database"""
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()
            
            updates = ['status = %s', 'updated_at = NOW()']
            params = [status]
            
            if download_ready is not None:
                updates.append('download = %s')
                params.append(download_ready)
            
            if file_path:
                updates.append('file_path = %s')
                params.append(file_path)
            
            if error_message:
                updates.append('error_message = %s')
                params.append(error_message)
            
            if increment_retry:
                updates.append('retry_count = retry_count + 1')
            
            query = f"UPDATE downloads SET {', '.join(updates)} WHERE id = %s"
            params.append(download_id)
            
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            
            self.logger.info(f"✅ Updated download {download_id} status to {status}")
            return True
            
        except mysql.connector.Error as e:
            self.logger.error(f"❌ Failed to update download status: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("🔌 Database connection closed")

class ChromeDriverManager:
    """Enhanced Chrome driver management"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.driver = None
        self.wait = None
    
    def init_driver(self):
        """Initialize Chrome driver with enhanced options"""
        try:
            # Ensure download directory exists
            os.makedirs(self.config['download_dir'], exist_ok=True)
            
            # Chrome options
            options = Options()
            
            # Download preferences
            prefs = {
                "download.default_directory": self.config['download_dir'],
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.automatic_downloads": 1
            }
            
            options.add_experimental_option("prefs", prefs)
            
            # Additional options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if self.config['headless']:
                options.add_argument("--headless")
            
            # Initialize driver
            service = Service(self.config['driver_path'])
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Initialize wait
            self.wait = WebDriverWait(self.driver, CONFIG['app']['timeout'])
            
            self.logger.info("🚗 Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Chrome driver: {e}")
            return False
    
    def save_cookies(self):
        """Save cookies to file"""
        try:
            cookies = self.driver.get_cookies()
            with open(CONFIG['app']['cookies_file'], 'w') as f:
                json.dump(cookies, f, indent=2)
            self.logger.info("💾 Cookies saved successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to save cookies: {e}")
    
    def load_cookies(self):
        """Load cookies from file"""
        try:
            if not os.path.exists(CONFIG['app']['cookies_file']):
                return False
            
            self.driver.get("https://www.freepik.com")
            
            with open(CONFIG['app']['cookies_file'], 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    # Remove problematic keys
                    cookie.pop('expiry', None)
                    cookie.pop('httpOnly', None)
                    cookie.pop('sameSite', None)
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to add cookie: {e}")
            
            self.logger.info("✅ Cookies loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load cookies: {e}")
            return False
    
    def login(self):
        """Login to Freepik"""
        try:
            # Try loading existing cookies first
            if self.load_cookies():
                # Verify login by checking for user elements
                self.driver.get("https://www.freepik.com")
                time.sleep(3)
                
                try:
                    # Check if already logged in
                    self.driver.find_element(By.CSS_SELECTOR, "[data-cy='user-menu']")
                    self.logger.info("✅ Already logged in via cookies")
                    return True
                except:
                    self.logger.info("🔄 Cookies expired, performing fresh login")
            
            # Fresh login
            self.logger.info("🔐 Starting fresh login process")
            self.driver.get(CONFIG['freepik']['login_url'])
            
            # Click "Continue with email"
            email_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Continue with email']/parent::button"))
            )
            email_btn.click()
            
            # Enter email
            email_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "email")))
            email_field.clear()
            email_field.send_keys(CONFIG['freepik']['email'])
            
            # Enter password
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(CONFIG['freepik']['password'])
            password_field.send_keys(Keys.RETURN)
            
            # Wait for potential CAPTCHA
            self.logger.info("⏳ Waiting for login completion (solve CAPTCHA if needed)")
            time.sleep(15)
            
            # Manual CAPTCHA solving
            input("🧠 If CAPTCHA appeared, solve it and press Enter to continue...")
            
            # Verify login success
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='user-menu']")))
                self.logger.info("✅ Login successful")
                self.save_cookies()
                return True
            except TimeoutException:
                self.logger.error("❌ Login verification failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login failed: {e}")
            return False
    
    def download_image(self, url, filename):
        """Download image from Freepik"""
        try:
            self.logger.info(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # Find and click download button
            download_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='download-button']"))
            )
            
            # Scroll to button and click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_btn)
            time.sleep(2)
            download_btn.click()
            
            self.logger.info("📥 Download button clicked, waiting for download...")
            
            # Wait for download to complete
            download_dir = Path(self.config['download_dir'])
            initial_files = set(download_dir.glob('*'))
            
            # Wait for new file to appear
            timeout = 60  # 60 seconds timeout
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                current_files = set(download_dir.glob('*'))
                new_files = current_files - initial_files
                
                if new_files:
                    # Check if download is complete (no .crdownload files)
                    complete_files = [f for f in new_files if not f.name.endswith('.crdownload')]
                    if complete_files:
                        downloaded_file = complete_files[0]
                        self.logger.info(f"✅ Download completed: {downloaded_file.name}")
                        return str(downloaded_file)
                
                time.sleep(2)
            
            self.logger.error("❌ Download timeout - file not found")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Download failed: {e}")
            return None
    
    def quit(self):
        """Quit Chrome driver"""
        if self.driver:
            self.driver.quit()
            self.logger.info("🔌 Chrome driver closed")

class FreepikDownloader:
    """Main downloader class"""
    
    def __init__(self):
        self.logger = Logger(CONFIG['app']['log_file'])
        self.db = DatabaseManager(CONFIG['db'], self.logger)
        self.chrome = ChromeDriverManager(CONFIG['chrome'], self.logger)
        self.running = True
    
    def start(self):
        """Start the downloader service"""
        self.logger.info("🚀 Freepik Downloader started")
        
        try:
            # Initialize Chrome driver
            if not self.chrome.init_driver():
                raise Exception("Failed to initialize Chrome driver")
            
            # Login to Freepik
            if not self.chrome.login():
                raise Exception("Failed to login to Freepik")
            
            # Main processing loop
            self.process_downloads()
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Shutdown requested by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")
        finally:
            self.cleanup()
    
    def process_downloads(self):
        """Main download processing loop"""
        while self.running:
            try:
                # Get pending downloads
                pending = self.db.get_pending_downloads(limit=1)
                
                if not pending:
                    self.logger.info("⏳ No pending downloads, waiting...")
                    time.sleep(CONFIG['app']['check_interval'])
                    continue
                
                # Process each download
                for download in pending:
                    self.process_single_download(download)
                
            except Exception as e:
                self.logger.error(f"❌ Error in processing loop: {e}")
                time.sleep(CONFIG['app']['check_interval'])
    
    def process_single_download(self, download):
        """Process a single download"""
        try:
            self.logger.info(f"🔄 Processing download ID: {download['id']}")
            
            # Update status to processing
            self.db.update_download_status(download['id'], 1)
            
            # Download the image
            file_path = self.chrome.download_image(download['url'], download['filename'])
            
            if file_path:
                # Update as completed
                self.db.update_download_status(
                    download['id'], 
                    status=1, 
                    download_ready=1, 
                    file_path=file_path
                )
                self.logger.info(f"✅ Download completed: {download['filename']}")
            else:
                # Update as failed with retry
                self.db.update_download_status(
                    download['id'], 
                    status=0, 
                    error_message="Download failed",
                    increment_retry=True
                )
                self.logger.error(f"❌ Download failed: {download['filename']}")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing download {download['id']}: {e}")
            self.db.update_download_status(
                download['id'], 
                status=0, 
                error_message=str(e),
                increment_retry=True
            )
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("🧹 Cleaning up resources...")
        self.running = False
        self.chrome.quit()
        self.db.close()
        self.logger.info("✅ Cleanup completed")

def main():
    """Main entry point"""
    try:
        downloader = FreepikDownloader()
        downloader.start()
    except Exception as e:
        print(f"❌ Failed to start downloader: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()