import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_banner():
    os.system('clear')
    print(f"""{Color.CYAN}
███████╗██╗░░██╗███████╗██████╗░███████╗██████╗░
██╔════╝╚██╗██╔╝██╔════╝██╔══██╗██╔════╝██╔══██╗
█████╗░░░╚███╔╝░█████╗░░██████╔╝█████╗░░██████╔╝
██╔══╝░░░██╔██╗░██╔══╝░░██╔═══╝░██╔══╝░░██╔══██╗
███████╗██╔╝╚██╗███████╗██║░░░░░███████╗██║░░██║
╚══════╝╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝
{Color.END}
{Color.YELLOW}➤ Termux Optimized Instagram Reporter v5.0{Color.END}
{Color.DARKCYAN}➤ Created with ♥ by Python Experts{Color.END}
""")

def load_config():
    try:
        with open('config.json') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Color.RED}✘ Config Error: {str(e)}{Color.END}")
        exit()

def setup_driver():
    try:
        options = Options()
        options.headless = False
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        print(f"{Color.BLUE}⚙️ Initializing Firefox Driver...{Color.END}")
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        print(f"{Color.GREEN}✓ Firefox Ready!{Color.END}")
        return driver
    except Exception as e:
        print(f"{Color.RED}✘ Driver Error: {str(e)}{Color.END}")
        exit()

def login(driver, config):
    try:
        print(f"\n{Color.YELLOW}🔑 Attempting Login...{Color.END}")
        driver.get("https://www.instagram.com/accounts/login/")
        
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Allow essential cookies')]")
        )).click()
        print(f"{Color.GREEN}✓ Cookies Accepted!{Color.END}")
        time.sleep(2)

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys(config['username'])

        password_field = driver.find_element(By.NAME, 'password')
        password_field.send_keys(config['password'])

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )).click()
        print(f"{Color.GREEN}✓ Login Attempted!{Color.END}")
        time.sleep(5)

        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), 'Not Now')]")
            )).click()
            print(f"{Color.GREEN}✓ Skipped Save Login!{Color.END}")
        except:
            pass

        print(f"{Color.CYAN}✅ Login Successful!{Color.END}")
        return True

    except Exception as e:
        print(f"{Color.RED}✘ Login Failed: {str(e)}{Color.END}")
        return False

def execute_report(driver, username):
    try:
        print(f"\n{Color.PURPLE}⚡ Starting Report Process for @{username}{Color.END}")
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(3)

        print(f"{Color.BLUE}➤ Opening Profile Menu...{Color.END}")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@aria-label='More options']")
        )).click()

        steps = [
            ("📝 Initializing Report...", "//span[contains(., 'Report')]"),
            ("🔨 Selecting Report Type...", "//button[contains(., 'Report Account')]"),
            ("🎯 Choosing Reason...", "//span[contains(., 'Someone else')]"),
            ("📌 Specifying Issue...", "//span[contains(., 'Pretending to be someone else')]"),
            ("🚀 Submitting Report...", "//span[contains(., 'Submit report')]")
        ]

        for desc, xpath in steps:
            print(f"{Color.YELLOW}{desc}{Color.END}")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
            time.sleep(1)

        print(f"{Color.GREEN}✅ Successfully Reported @{username}!{Color.END}")
        return True

    except Exception as e:
        print(f"{Color.RED}✘ Report Failed: {str(e)}{Color.END}")
        return False

def main_flow():
    print_banner()
    config = load_config()
    
    target = input(f"{Color.CYAN}🎯 Enter Target Username: {Color.END}").strip('@')
    print(f"{Color.DARKCYAN}➤ Target Selected: @{target}{Color.END}")
    
    driver = setup_driver()
    
    if login(driver, config):
        report_count = 0
        try:
            while True:
                if execute_report(driver, target):
                    report_count += 1
                    print(f"\n{Color.BOLD}📊 Total Reports: {Color.GREEN}{report_count}{Color.END}")
                    print(f"{Color.YELLOW}⏳ Cooling Down for 5 Minutes...{Color.END}\n")
                    time.sleep(300)
                else:
                    break
        except KeyboardInterrupt:
            print(f"\n{Color.RED}⚠️  Process Interrupted by User!{Color.END}")
        finally:
            driver.quit()
            print(f"{Color.CYAN}🛑 Browser Session Closed{Color.END}")

if __name__ == "__main__":
    main_flow()
