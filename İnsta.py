import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc

def load_config():
    if not os.path.exists('config.json'):
        print("config.json dosyası bulunamadı!")
        print("Lütfen aşağıdaki formatı kullanarak bir config dosyası oluşturun:")
        print('''{
    "username": "your_username",
    "password": "your_password"
}''')
        exit()
    
    with open('config.json', 'r') as f:
        return json.load(f)

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--log-level=3")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Termux için özel ayarlar
    options.binary_location = '/data/data/com.termux/files/usr/bin/chromium'  # Termux'a chromium kurulu olmalı
    
    driver = uc.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
        headless=False,
        version_main=114  # Sisteminizdeki Chrome versiyonuna göre ayarlayın
    )
    return driver

def login(driver, config):
    driver.get('https://www.instagram.com/accounts/login/')
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, 'username'))
    ).send_keys(config['username'])
    
    driver.find_element(By.NAME, 'password').send_keys(config['password'])
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    
    time.sleep(5)

def report_user(driver, username):
    try:
        driver.get(f'https://www.instagram.com/{username}/')
        time.sleep(3)
        
        # Diğer düğmesini bul
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'glyphsSpriteMore_horizontal')]"))
        ).click()
        
        # Şikayet et
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Şikayet Et')]"))
        ).click()
        
        # Sebep seç
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Uygunsuz')]"))
        ).click()
        
        # Onayla
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Gönder')]"))
        ).click()
        
        return True
        
    except Exception as e:
        print(f"Hata: {str(e)}")
        return False

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    config = load_config()
    username = input("Raporlanacak kullanıcı adı: ").strip('@')
    
    driver = setup_driver()
    
    try:
        login(driver, config)
        while True:
            if report_user(driver, username):
                print("5 saniye sonra tekrar denenecek...")
                time.sleep(5)
            else:
                break
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
