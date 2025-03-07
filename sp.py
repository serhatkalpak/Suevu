import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# Terminal Temizleme ve Renkli Yazılar
os.system('clear')
print("\033[1;36m" + "✪ Instagram Auto Reporter v3.0 ✪".center(50) + "\033[0m")
print("\033[90m" + "Termux Optimized - Firefox Edition".center(50) + "\033[0m\n")

def load_config():
    try:
        with open('config.json') as f:
            return json.load(f)
    except Exception as e:
        print("\033[1;31m[!] config.json Error: {}\033[0m".format(str(e)))
        exit()

def setup_driver():
    try:
        options = Options()
        options.headless = False  # GUI görüntülemek için False yapın
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        driver = webdriver.Firefox(
            executable_path='geckodriver',  # Geckodriver yolunu kontrol edin
            options=options
        )
        return driver
    except Exception as e:
        print("\033[1;31m[!] Driver Error: {}\033[0m".format(str(e)))
        exit()

def login(driver, config):
    try:
        print("\033[1;33m[~] Logging in to Instagram...\033[0m")
        driver.get("https://www.instagram.com/accounts/login/")
        
        # Çerez Kabul
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Allow essential cookies')]")
        )).click()
        time.sleep(2)

        # Giriş Bilgileri
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        username_field.send_keys(config['username'])

        password_field = driver.find_element(By.NAME, 'password')
        password_field.send_keys(config['password'])

        # Giriş Butonu
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )).click()
        time.sleep(5)

        print("\033[1;32m[✓] Login Successful!\033[0m")
        return True

    except Exception as e:
        print("\033[1;31m[!] Login Failed: {}\033[0m".format(str(e)))
        return False

def report_user(driver, username):
    try:
        print(f"\033[1;33m[~] Reporting @{username}...\033[0m")
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(3)

        # Profil Menüsü
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@aria-label='More options']")
        )).click()

        # Rapor Akışı
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(., 'Report')]")
        )).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Report Account')]")
        )).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(., 'Someone else')]")
        )).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(., 'Pretending to be someone else')]")
        )).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(., 'Submit report')]")
        )).click()

        print(f"\033[1;32m[✓] Successfully reported @{username}!\033[0m")
        return True

    except Exception as e:
        print(f"\033[1;31m[!] Report Failed: {str(e)}\033[0m")
        return False

def main():
    config = load_config()
    target = input("\033[1;34m[?] Target username: \033[0m").strip('@')
    
    driver = setup_driver()
    
    if login(driver, config):
        report_count = 0
        try:
            while True:
                if report_user(driver, target):
                    report_count += 1
                    print(f"\033[1;35m[+] Total Reports: {report_count}\033[0m")
                    print("\033[90m[~] Waiting 5 minutes...\033[0m\n")
                    time.sleep(300)  # 5 dakika bekle
                else:
                    break
        except KeyboardInterrupt:
            print("\033[1;31m[!] Process stopped by user\033[0m")
        finally:
            driver.quit()
            print("\033[1;33m[!] Browser closed\033[0m")

if __name__ == "__main__":
    main()
