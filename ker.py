
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
Copyright (C) 2024 [Your Name]
"""

import os
import sys
import json
import time
import random
import logging
import hashlib
import base64
import argparse
from getpass import getpass
from typing import Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

#region Global Configurations
VERSION = "3.2.1"
MAX_RETRIES = 3
DELAY_RANGE = (5, 15)  # Rastgele bekleme süresi (saniye)
#endregion

#region Security
class SecureConfig:
    def __init__(self):
        self.config_file = "config.json"
        self.salt = "termux_secure_salt_"

    def _simple_encrypt(self, data: str, password: str) -> str:
        """Basit XOR şifreleme"""
        key = hashlib.sha256(password.encode()).digest()
        encrypted = bytearray()
        for i, c in enumerate(data.encode()):
            encrypted.append(c ^ key[i % len(key)])
        return base64.urlsafe_b64encode(encrypted).decode()

    def _simple_decrypt(self, encrypted_data: str, password: str) -> str:
        """Şifre çözme"""
        key = hashlib.sha256(password.encode()).digest()
        decoded = base64.urlsafe_b64decode(encrypted_data)
        return bytes([c ^ key[i % len(key)] for i, c in enumerate(decoded)]).decode()

    def save_config(self, data: Dict, password: str) -> None:
        """Config dosyasını kaydet"""
        data["password"] = self._simple_encrypt(data["password"], password)
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_config(self, password: str) -> Dict:
        """Config dosyasını yükle"""
        with open(self.config_file) as f:
            data = json.load(f)
        data["password"] = self._simple_decrypt(data["password"], password)
        return data

    def config_exists(self) -> bool:
        return os.path.exists(self.config_file)
#endregion

#region Core Functionality
class InstaReporterBot:
    def __init__(self, config: Dict):
        self.config = config
        self.driver = self._init_driver()
        self.logger = self._init_logger()

    def _init_driver(self) -> webdriver.Firefox:
        options = Options()
        options.headless = True
        options.set_preference("privacy.trackingprotection.enabled", True)
        
        return webdriver.Firefox(
            service=Service(
                GeckoDriverManager().install(),
                log_path=os.devnull
            ),
            options=options
        )

    def _init_logger(self) -> logging.Logger:
        logger = logging.getLogger('InstaReporter')
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        file_handler = logging.FileHandler('activity.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger

    def _human_like_delay(self) -> None:
        time.sleep(random.uniform(*DELAY_RANGE))
        self.driver.execute_script(f"window.scrollBy(0, {random.randint(50, 200)})")

    def login(self) -> bool:
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            # Çerez Kabulü
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow essential cookies')]"))
            ).click()
            self._human_like_delay()

            # Giriş İşlemi
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            username_field.send_keys(self.config['username'])
            
            password_field = self.driver.find_element(By.NAME, 'password')
            password_field.send_keys(self.config['password'])
            
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            submit_button.click()
            self._human_like_delay()

            return True
        except Exception as e:
            self.logger.error(f"Login hatası: {str(e)}")
            return False

    def report_user(self, target: str) -> bool:
        try:
            self.driver.get(f"https://www.instagram.com/{target}/")
            self._human_like_delay()

            report_flow = [
                ("//div[@aria-label='Diğer seçenekler']", "Menü açılıyor"),
                ("//span[contains(., 'Şikayet Et')]", "Rapor başlatılıyor"),
                ("//button[contains(., 'Hesabı Bildir')]", "Hesap seçiliyor"),
                ("//span[text()='Uygunsuz']", "Sebep belirleniyor"),
                ("//span[text()='Taklit Hesap']", "Detay seçimi"),
                ("//span[text()='Gönder']", "Rapor gönderiliyor")
            ]

            for xpath, action in report_flow:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                element.click()
                self.logger.info(action)
                self._human_like_delay()

            self.logger.info(f"{target} başarıyla raporlandı")
            return True
        except Exception as e:
            self.logger.error(f"Raporlama hatası: {str(e)}")
            return False

    def run(self, target: str) -> None:
        if self.login():
            for attempt in range(1, MAX_RETRIES + 1):
                if self.report_user(target):
                    break
                self.logger.warning(f"Tekrar deneniyor ({attempt}/{MAX_RETRIES})")
                time.sleep(60)
        self.driver.quit()
#endregion

#region Main Execution
def main():
    parser = argparse.ArgumentParser(description='Instagram Profil Rapor Botu')
    parser.add_argument('-t', '--target', required=True, help='Raporlanacak kullanıcı adı')
    args = parser.parse_args()

    secure_config = SecureConfig()
    
    if not secure_config.config_exists():
        print("İlk kurulum yapılıyor...")
        config_data = {
            "username": input("Instagram kullanıcı adı: "),
            "password": getpass("Şifre: ")
        }
        master_pwd = getpass("Config şifresi belirleyin: ")
        secure_config.save_config(config_data, master_pwd)
        print("Yapılandırma tamamlandı!")
        return

    master_pwd = getpass("Config şifresi: ")
    try:
        config = secure_config.load_config(master_pwd)
        bot = InstaReporterBot(config)
        bot.run(args.target.strip('@'))
    except Exception as e:
        print(f"Hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print(f"""
\033[94m
███████╗██╗░░██╗███████╗██████╗░███████╗██████╗░
██╔════╝╚██╗██╔╝██╔════╝██╔══██╗██╔════╝██╔══██╗
█████╗░░░╚███╔╝░█████╗░░██████╔╝█████╗░░██████╔╝
██╔══╝░░░██╔██╗░██╔══╝░░██╔═══╝░██╔══╝░░██╔══██╗
███████╗██╔╝╚██╗███████╗██║░░░░░███████╗██║░░██║
╚══════╝╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝
\033[0m
Termux Optimized | Version {VERSION} | GPLv3 Licensed
""")
    main()
#endregion
