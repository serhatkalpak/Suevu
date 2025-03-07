import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Terminal Temizleme ve Başlık
os.system('cls' if os.name == 'nt' else 'clear')
print("\033[1;36mInstagram Reporter v2.0\033[0m")

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        print("\033[1;31m[!] config.json bulunamadı veya okunamadı!\033[0m")
        exit()

def setup_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    except Exception as e:
        print(f"\033[1;31m[!] Driver hatası: {str(e)}\033[0m")
        exit()

def login(driver, config):
    try:
        driver.get('https://www.instagram.com/accounts/login/')
        
        # Çerez Kabul
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Allow essential and optional cookies')]")
        )).click()
        time.sleep(2)

        # Giriş Bilgileri
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys(config['username'])

        password_field = driver.find_element(By.NAME, 'password')
        password_field.send_keys(config['password'])

        # Giriş Butonu
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )).click()
        time.sleep(5)

        # Giriş Sonrası Pop-up'lar
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[text()='Şimdi Değil']")
            )).click()
        except:
            pass

        return True

    except Exception as e:
        print(f"\033[1;31m[!] Giriş hatası: {str(e)}\033[0m")
        return False

def report_user(driver, username):
    try:
        driver.get(f'https://www.instagram.com/{username}/')
        time.sleep(3)

        # Profil Menüsü
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//span[@aria-label='Daha fazla seçenek']")
        )).click()

        # Raporlama Akışı
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Hesabı Bildir')]")
        )).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Uygunsuz')]")
        )).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Taklit Hesap')]")
        )).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Gönder')]")
        )).click()

        print(f"\033[1;32m[✓] @{username} başarıyla raporlandı!\033[0m")
        return True

    except Exception as e:
        print(f"\033[1;31m[!] Raporlama hatası: {str(e)}\033[0m")
        return False

def main():
    config = load_config()
    username = input("\033[1;33m[?] Raporlanacak kullanıcı adı: \033[0m").strip('@')
    
    driver = setup_driver()
    
    if login(driver, config):
        report_count = 0
        while True:
            if report_user(driver, username):
                report_count += 1
                print(f"\033[1;34m[+] Toplam Rapor: {report_count}\033[0m")
                time.sleep(120)  # Instagram rate limit için 2 dakika bekleme
            else:
                break
                
    driver.quit()

if __name__ == "__main__":
    main()
