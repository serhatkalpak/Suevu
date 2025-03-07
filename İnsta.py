import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--log-level=3")
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def login(driver, config):
    driver.get('https://www.instagram.com/accounts/login/')
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, 'username'))
    ).send_keys(config['username'])
    
    driver.find_element(By.NAME, 'password').send_keys(config['password'])
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    
    time.sleep(5)  # Login işleminin tamamlanmasını bekle

def report_user(driver, username):
    driver.get(f'https://www.instagram.com/{username}/')
    
    try:
        # Profil sayfası elementlerini bul
        menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Diğer')]"))
        )
        menu_button.click()
        
        report_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Şikayet Et')]"))
        )
        report_button.click()
        
        # Raporlama adımları
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Hesabı bildir')]"))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Uygunsuz']"))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Gönder')]"))
        ).click()
        
        print("Başarıyla raporlandı!")
        return True
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
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
