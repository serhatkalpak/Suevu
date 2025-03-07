import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Terminali temizle
os.system('clear')

def load_config():
    if not os.path.exists('config.json'):
        print("[!] config.json bulunamadı!")
        print("""Aşağıdaki formatla config.json oluşturun:
{
    "username": "kullanici_adiniz",
    "password": "sifreniz"
}""")
        exit()
    
    with open('config.json') as f:
        return json.load(f)

def setup_driver():
    print("[~] ChromeDriver hazırlanıyor...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        print("[✓] ChromeDriver başarıyla yüklendi!")
        return driver
    except Exception as e:
        print(f"[!] Driver hatası: {str(e)}")
        exit()

def login(driver, config):
    print("[~] Instagram'a giriş yapılıyor...")
    try:
        driver.get('https://www.instagram.com/accounts/login/')
        
        # Çerezleri kabul et
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow essential and optional cookies')]"))
        ).click()
        time.sleep(2)
        
        # Giriş bilgilerini doldur
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        username_field.send_keys(config['username'])
        
        password_field = driver.find_element(By.NAME, 'password')
        password_field.send_keys(config['password'])
        
        # Giriş butonuna tıkla
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # 2FA kontrolü
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, 'verificationCode'))
            print("[!] 2FA aktif! Manuel giriş gerekli.")
            input("[?] 2FA kodunu girdikten sonra Enter'a basın...")
        except:
            pass
        
        print("[✓] Başarıyla giriş yapıldı!")
        time.sleep(3)
        
    except Exception as e:
        print(f"[!] Giriş hatası: {str(e)}")
        exit()

def report_user(driver, username):
    try:
        print(f"[~] @{username} raporlanıyor...")
        driver.get(f'https://www.instagram.com/{username}/')
        time.sleep(3)
        
        # Profil menüsünü aç
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@aria-label='Daha fazla seçenek']"))
        ).click()
        
        # Rapor butonu
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Hesabı Bildir')]"))
        ).click()
        
        # Rapor sebebi
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Uygunsuz')]"))
        ).click()
        
        # Alt sebep
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Taklit Hesap')]"))
        ).click()
        
        # Gönder
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Gönder')]"))
        ).click()
        
        print("[✓] Başarıyla raporlandı!")
        return True
        
    except Exception as e:
        print(f"[!] Raporlama hatası: {str(e)}")
        return False

def main():
    config = load_config()
    username = input("[?] Raporlanacak kullanıcı adı: ").strip('@')
    
    driver = setup_driver()
    
    try:
        login(driver, config)
        report_count = 0
        
        while True:
            if report_user(driver, username):
                report_count += 1
                print(f"[+] Toplam rapor: {report_count}")
                print("[~] 30 saniye beklenecek...")
                time.sleep(30)
            else:
                break
                
    finally:
        driver.quit()
        print("[!] Program sonlandırıldı")

if __name__ == "__main__":
    main()
