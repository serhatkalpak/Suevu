import os
import sys
import json
import time
import random
import logging
import sqlite3
from datetime import datetime
from functools import wraps
from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

#region ANSI Renk Kodları
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
#endregion

#region Loglama Sistemi
class AdvancedFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Color.OKBLUE,
        logging.INFO: Color.OKCYAN,
        logging.WARNING: Color.WARNING,
        logging.ERROR: Color.FAIL,
        logging.CRITICAL: Color.FAIL + Color.BOLD
    }

    def format(self, record):
        color = self.FORMATS.get(record.levelname, Color.ENDC)
        message = super().format(record)
        return f"{color}{message}{Color.ENDC}"

logger = logging.getLogger('InstaGuardPro')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(AdvancedFormatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(console_handler)
#endregion

#region Veritabanı Yönetimi
class ReportDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('reports.db', check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT NOT NULL
                )
            ''')

    def log_report(self, target: str, status: str, session_id: str):
        with self.conn:
            self.conn.execute('''
                INSERT INTO reports (target, status, session_id)
                VALUES (?, ?, ?)
            ''', (target, status, session_id))
#endregion

#region Ana Sınıf
class InstaReporterPro:
    def __init__(self):
        self.db = ReportDatabase()
        self.session_id = Fernet.generate_key().decode()[:8]
        self.driver = self._initialize_driver()
        self.config = self._load_config()

    def _initialize_driver(self):
        try:
            options = webdriver.FirefoxOptions()
            options.headless = True
            options.set_preference("privacy.trackingprotection.enabled", True)
            options.set_preference("privacy.resistFingerprinting", True)
            
            return webdriver.Firefox(
                service=Service(
                    GeckoDriverManager().install(),
                    log_path=os.devnull
                ),
                options=options
            )
        except Exception as e:
            logger.error(f"{Color.FAIL}Driver başlatma hatası: {str(e)}{Color.ENDC}")
            sys.exit(1)

    def _load_config(self):
        try:
            with open('config.enc', 'rb') as f:
                cipher_suite = Fernet(os.environ['INSTA_KEY'])
                return json.loads(cipher_suite.decrypt(f.read()))
        except Exception as e:
            logger.error(f"{Color.FAIL}Config yükleme hatası: {str(e)}{Color.ENDC}")
            sys.exit(1)

    def _human_interaction(self):
        time.sleep(random.uniform(1.2, 2.8))
        self.driver.execute_script("window.scrollBy(0, random.randint(50, 150))")

    def retry(max_attempts=3, delay=15):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts+1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts:
                            raise
                        logger.warning(f"{Color.WARNING}Yeniden deniyor ({attempt}/{max_attempts})...{Color.ENDC}")
                        time.sleep(delay)
            return wrapper
        return decorator

    @retry()
    def login(self):
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow essential cookies')]")
            ).click()
            
            username = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'username'))
            username.send_keys(self.config['username'])
            
            password = self.driver.find_element(By.NAME, 'password')
            password.send_keys(self.config['password'])
            
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Ana Sayfa']"))
            )
            logger.info(f"{Color.OKGREEN}✓ Başarıyla giriş yapıldı{Color.ENDC}")
            return True
            
        except Exception as e:
            logger.error(f"{Color.FAIL}Giriş hatası: {str(e)}{Color.ENDC}")
            return False

    @retry()
    def report_user(self, username: str):
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            steps = [
                ("//div[@aria-label='Diğer seçenekler']", "Menü açılıyor"),
                ("//span[contains(., 'Şikayet Et')]", "Rapor başlatılıyor"),
                ("//button[contains(., 'Hesabı Bildir')]", "Hesap seçiliyor"),
                ("//span[text()='Uygunsuz']", "Sebep belirleniyor"),
                ("//span[text()='Taklit Hesap']", "Detay seçimi"),
                ("//span[text()='Gönder']", "Onaylanıyor")
            ]
            
            for xpath, desc in steps:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                self._human_interaction()
                element.click()
                logger.info(f"{Color.OKCYAN}➤ {desc}{Color.ENDC}")
                time.sleep(random.uniform(0.8, 1.5))
            
            self.db.log_report(username, "SUCCESS", self.session_id)
            logger.info(f"{Color.OKGREEN}✓ @{username} başarıyla raporlandı{Color.ENDC}")
            return True
            
        except Exception as e:
            self.db.log_report(username, "FAILED", self.session_id)
            logger.error(f"{Color.FAIL}Raporlama hatası: {str(e)}{Color.ENDC}")
            return False

    def generate_report(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT target, status, timestamp 
            FROM reports 
            WHERE session_id = ?
        ''', (self.session_id,))
        
        print(f"\n{Color.HEADER}{'Hedef':<20} {'Durum':<10} {'Zaman':<25}{Color.ENDC}")
        for row in cursor.fetchall():
            color = Color.OKGREEN if row[1] == "SUCCESS" else Color.FAIL
            print(f"{color}{row[0]:<20} {row[1]:<10} {row[2]:<25}{Color.ENDC}")

    def run(self):
        try:
            target = input(f"{Color.OKCYAN}Hedef kullanıcı adı: {Color.ENDC}").strip('@')
            
            if self.login():
                while True:
                    if self.report_user(target):
                        logger.info(f"{Color.WARNING}⏳ 5 dakika bekleme süresi...{Color.ENDC}")
                        time.sleep(300)
        except KeyboardInterrupt:
            logger.warning(f"{Color.WARNING}İşlem kullanıcı tarafından durduruldu{Color.ENDC}")
        finally:
            self.driver.quit()
            self.generate_report()

if __name__ == "__main__":
    os.system('clear')
    print(f"""
{Color.HEADER}
█▀▀ █▀█ █▀▄ █▀▀ █▀▀ ▀█▀ █ █▀█ █▄░█ █▀▀
█▄▄ █▄█ █▄▀ ██▄ █▀░ ░█░ █ █▄█ █░▀█ ██▄
{Color.ENDC}
{Color.OKCYAN}Termux Professional Instagram Reporter v3.0{Color.ENDC}
{Color.WARNING}⚠ Sadece eğitim amaçlıdır!{Color.ENDC}
""")
    
    if not os.path.exists('config.enc'):
        key = Fernet.generate_key()
        os.environ['INSTA_KEY'] = key.decode()
        data = {
            "username": input("Kullanıcı adı: "),
            "password": input("Şifre: ")
        }
        cipher_suite = Fernet(key)
        with open('config.enc', 'wb') as f:
            f.write(cipher_suite.encrypt(json.dumps(data).encode()))
    
    InstaReporterPro().run()
