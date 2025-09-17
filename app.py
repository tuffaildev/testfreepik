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

def download_freepik_image(user_image_url):
    login_url = 'https://www.freepik.com/login'
    username = 'tuffailxhehzad@gmail.com'
    password = 'tuffail238'
    chromedriver_path = 'D:\\Downloads\\chromedriver-win64 (1)\\chromedriver-win64\\chromedriver.exe'

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    try:
        # Login
        driver.get(login_url)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Continue with email']/parent::button"))).click()
        wait.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
        time.sleep(20)

        # Pause for manual CAPTCHA solving
        input("If there is a CAPTCHA, please solve it in the browser, then press Enter here to continue...")

        # Go to user image page
        driver.get(user_image_url)
        time.sleep(5)

        # Click download button
        download_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='download-button']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_btn)
        time.sleep(1)
        download_btn.click()
        time.sleep(25)

        # Get cookies for requests session
        cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        # Parse download link
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        download_link = None
        for a in soup.find_all('a', href=True):
            if 'download' in a['href']:
                download_link = a['href']
                break

        if not download_link:
            print("Download link not found in page source.")
            return False

        if download_link.startswith('/'):
            download_link = 'https://www.freepik.com' + download_link

        # Get file extension
        parsed_url = urlparse(download_link)
        _, ext = os.path.splitext(parsed_url.path)
        if not ext:
            ext = '.jpg'

        # Save to Downloads
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        filename = f'downloaded_image{ext}'
        filepath = os.path.join(downloads_dir, filename)

        # Download image
        image_response = session.get(download_link)
        with open(filepath, 'wb') as f:
            f.write(image_response.content)
            f.flush()
            os.fsync(f.fileno())

        print(f'Image downloaded successfully as {filepath}!')
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        driver.quit()