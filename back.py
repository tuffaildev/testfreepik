import time
import os
import json
import requests
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ====== Configuration ======
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'freepik'
}

EMAIL = 'tuffailxhehzad@gmail.com'
PASSWORD = 'tuffail238'
CHROMEDRIVER_PATH = 'D:\\Downloads\\chromedriver-win64 (1)\\chromedriver-win64\\chromedriver.exe'
LOGIN_URL = 'https://www.freepik.com/login'
COOKIES_FILE = 'cookies.json'

# ====== Init Driver ======
def init_driver():
    print("🚗 Starting Chrome driver...")
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    return driver, wait

# ====== Save and Load Cookies ======
def save_cookies(driver):
    with open(COOKIES_FILE, 'w') as f:
        json.dump(driver.get_cookies(), f)
    print("💾 Cookies saved.")

def load_cookies(driver):
    if not os.path.exists(COOKIES_FILE):
        return False
    with open(COOKIES_FILE, 'r') as f:
        cookies = json.load(f)
        driver.get("https://www.freepik.com")  # Load domain first
        for cookie in cookies:
            driver.add_cookie(cookie)
    print("✅ Session loaded from cookies.")
    return True

# ====== Login Handling ======
def login(driver, wait):
    if load_cookies(driver):
        return

    print("🔐 Logging in manually...")
    driver.get(LOGIN_URL)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Continue with email']/parent::button"))).click()
    wait.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.RETURN)
    time.sleep(15)
    input("🧠 Solve CAPTCHA if needed, then press Enter to continue...")
    save_cookies(driver)

# ====== Database Functions ======
def connect_db():
    print("🗄️ Connecting to database...")
    return mysql.connector.connect(**DB_CONFIG)

def get_pending_image(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM downloads WHERE status = 0 LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    return row

def mark_as_downloaded(conn, image_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE downloads SET status = 1 WHERE id = %s", (image_id,))
    conn.commit()
    cursor.close()
    print(f"✅ Marked ID {image_id} as downloaded.")

# ====== Image Download Function ======
def download_image(driver, wait, url):
    try:
        print(f"🌐 Visiting URL: {url}")
        driver.get(url)
        time.sleep(5)
        download_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='download-button']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_btn)
        time.sleep(1)
        download_btn.click()
        print("📥 Clicked download button.")
        time.sleep(20)
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

# ====== Main Loop ======
def main(driver, wait):
    conn = connect_db()

    while True:
        row = get_pending_image(conn)
        if row:
            print(f"\n🔄 Found image to download (ID: {row['id']})")
            success = download_image(driver, wait, row['url'])
            if success:
                mark_as_downloaded(conn, row['id'])
        else:
            print("⏳ No pending images. Waiting 20 seconds...")
        time.sleep(20)

# ====== Entry Point ======
if __name__ == "__main__":
    print("🚀 Script started.")
    driver, wait = init_driver()
    login(driver, wait)
    main(driver, wait)
