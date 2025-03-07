import os
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_banner():
    os.system('clear')
    print(f"""{Color.CYAN}
░█▀▀░█▀█░█▀▄░█▀▀░█▀▄░▀█▀
░█▀▀░█▀█░█▀▄░█▀▀░█░█░░█░
░▀▀▀░▀░▀░▀▀░░▀▀▀░▀▀░░▀▀▀
{Color.END}{Color.YELLOW}Termux Instagram Reporter v2.1{Color.END}
""")

def get_credentials():
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"username": "", "password": ""}, f)
        print(f"{Color.RED}config.json oluşturuldu, lütfen bilgilerinizi doldurun!{Color.END}")
        exit()
    
    with open('config.json') as f:
        return json.load(f)

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = True
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/117.0 Firefox/117.0")
    
    return webdriver.Firefox(
        service=Service(
            GeckoDriverManager().install(),
            log_path=os.devnull
        ),
        options=options
    )

def human_delay(min_t=1, max_t=3):
    time.sleep(random.uniform(min_t, max_t))

def login(driver, username, password):
    try:
        driver.get("https://www.instagram.com/accounts/login/")
        
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Allow essential cookies')]")
        )).click()
        print(f"{Color.GREEN}✓ Çerezler kabul edildi{Color.END}")
        human_delay(2, 3)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.NAME, 'username')
        )).send_keys(username)
        
        driver.find_element(By.NAME, 'password').send_keys(password)
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )).click()
        print(f"{Color.GREEN}✓ Giriş denemesi yapılıyor...{Color.END}")
        human_delay(5, 7)

        return True

    except Exception as e:
        print(f"{Color.RED}⨯ Giriş hatası: {str(e)}{Color.END}")
        return False

def report_user(driver, username):
    try:
        driver.get(f"https://www.instagram.com/{username}/")
        human_delay(3, 5)

        steps = [
            ("//div[contains(@aria-label, 'Diğer seçenekler')]", "Menü açılıyor"),
            ("//span[contains(., 'Şikayet Et')]", "Rapor başlatılıyor"),
            ("//button[contains(., 'Hesabı Bildir')]", "Hesap seçiliyor"),
            ("//span[contains(text(), 'Uygunsuz')]", "Sebep belirleniyor"),
            ("//span[contains(text(), 'Taklit Hesap')]", "Detay seçimi"),
            ("//span[contains(text(), 'Gönder')]", "Rapor gönderiliyor")
        ]

        for xpath, desc in steps:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, xpath)
            )).click()
            print(f"{Color.YELLOW}➤ {desc}{Color.END}")
            human_delay(1, 2)

        print(f"{Color.GREEN}✓ @{username} raporlandı{Color.END}")
        return True

    except Exception as e:
        print(f"{Color.RED}⨯ Raporlama hatası: {str(e)}{Color.END}")
        return False

def main():
    print_banner()
    config = get_credentials()
    target = input(f"{Color.CYAN}Raporlanacak kullanıcı: {Color.END}").strip('@')
    
    driver = setup_driver()
    
    try:
        if login(driver, config['username'], config['password']):
            report_count = 0
            while True:
                if report_user(driver, target):
                    report_count += 1
                    print(f"{Color.CYAN}Toplam rapor: {report_count}{Color.END}")
                    print(f"{Color.YELLOW}5 dakika bekleme...{Color.END}\n")
                    time.sleep(300)
    finally:
        driver.quit()
        print(f"{Color.CYAN}Oturum sonlandırıldı{Color.END}")

if __name__ == "__main__":
    main()
