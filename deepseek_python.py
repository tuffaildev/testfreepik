import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configuration - Replace with your details
FREEPIK_EMAIL = "your_premium_email@example.com"
FREEPIK_PASSWORD = "your_premium_password"
DOWNLOAD_DIR = "/path/to/your/download/folder"  # e.g., "/Users/name/Downloads/freepik"
CHROMEDRIVER_PATH = "/path/to/chromedriver"  # e.g., "/usr/local/bin/chromedriver"

def download_freepik_image(url):
    # Create download directory if not exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Chrome options setup
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize driver
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Login to Freepik
        driver.get("https://www.freepik.com/login")
        
        # Fill email
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_field.send_keys(FREEPIK_EMAIL)
        
        # Fill password
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_field.send_keys(FREEPIK_PASSWORD)
        
        # Submit login
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for login to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "avatar--menu"))
        )
        print("✅ Login successful")

        # Navigate to target URL
        driver.get(url)
        print(f"🖼️ Opened image page: {url}")
        
        # Wait and click download button
        download_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'button--download')]"))
        )
        download_btn.click()
        print("⬇️ Download triggered")
        
        # Wait for download to complete
        print("⏳ Waiting for download to complete...")
        time.sleep(10)  # Adjust based on your internet speed
        
    except TimeoutException as e:
        print(f"❌ Timed out: {str(e)}")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
    finally:
        driver.quit()
        print("🧹 Browser closed")
        print(f"✅ Check downloaded file in: {DOWNLOAD_DIR}")

if __name__ == "__main__":
    # Example Freepik URL
    image_url = "https://www.freepik.com/free-photo/html-css-collapse-concept-with-person_36295467.htm"
    download_freepik_image(image_url)