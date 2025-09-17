import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Config
login_url = 'https://www.freepik.com/login'
image_url = 'https://www.freepik.com/free-photo/view-old-tree-lake-with-snow-covered-mountains-cloudy-day_12947430.htm#fromView=search&page=1&position=4&uuid=661c846d-afe6-4093-819b-e8a839b03eb3&query=nature'
#image url in array = [image_url]  # Add more URLs as needed

username = 'tuffailxhehzad@gmail.com'
password = 'tuffail238'
chromedriver_path = 'D:\\Downloads\\chromedriver-win64 (1)\\chromedriver-win64\\chromedriver.exe'

# Start driver
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 20)

# Login
driver.get(login_url)
wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Continue with email']/parent::button"))).click()
wait.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys(username)
driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
time.sleep(20)

# Pause for manual CAPTCHA solving
input("If there is a CAPTCHA, please solve it in the browser, then press Enter here to continue...")

# Go to image page
driver.get(image_url)
time.sleep(5)

# Scroll the download button into view and click
try:
    download_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='download-button']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_btn)
    time.sleep(1)
    download_btn.click()
    time.sleep(25)
except Exception as e:
    print(f"Download button not found or not clickable: {e}")
    driver.quit()
    exit()

# Get cookies for requests session
cookies = driver.get_cookies()
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])
