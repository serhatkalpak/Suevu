import os
import time
import json
import requests

# Terminal Temizleme ve Başlık
os.system('clear')
print("\033[1;36mInstagram Reporter v5.0 (API Tabanlı)\033[0m")

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        print("\033[1;31m[!] config.json bulunamadı veya okunamadı!\033[0m")
        exit()

def login(config):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Termux) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
    })

    # Giriş yap
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    response = session.post(login_url, data={
        "username": config["username"],
        "password": config["password"],
        "queryParams": "{}",
        "optIntoOneTap": "false"
    })

    if response.status_code == 200 and "authenticated" in response.text:
        print("\033[1;32m[✓] Giriş başarılı!\033[0m")
        return session
    else:
        print("\033[1;31m[!] Giriş başarısız!\033[0m")
        exit()

def report_user(session, username):
    try:
        # Kullanıcı ID'sini al
        user_info_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
        response = session.get(user_info_url)
        user_id = response.json()["graphql"]["user"]["id"]

        # Rapor gönder
        report_url = "https://www.instagram.com/users/report/"
        response = session.post(report_url, data={
            "source_name": "",
            "reason_id": "1",  # 1: Uygunsuz, 2: Taklit Hesap, vb.
            "user_id": user_id
        })

        if response.status_code == 200:
            print(f"\033[1;32m[✓] @{username} başarıyla raporlandı!\033[0m")
            return True
        else:
            print(f"\033[1;31m[!] Raporlama başarısız: {response.status_code}\033[0m")
            return False

    except Exception as e:
        print(f"\033[1;31m[!] Raporlama hatası: {str(e)}\033[0m")
        return False

def main():
    config = load_config()
    username = input("\033[1;33m[?] Raporlanacak kullanıcı adı: \033[0m").strip('@')
    
    session = login(config)
    
    report_count = 0
    while True:
        if report_user(session, username):
            report_count += 1
            print(f"\033[1;34m[+] Toplam Rapor: {report_count}\033[0m")
            time.sleep(300)  # 5 dakika bekleme süresi
        else:
            break

if __name__ == "__main__":
    main()
