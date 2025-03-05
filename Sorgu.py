import requests

API_KEY = "a214d50e6c99e1c17a90cd474ede7191" 
API_URL = "http://apilayer.net/api/validate"

ULKELER = {
    '1': {'ülke': 'Türkiye', 'kod': '+90', 'örnek': '5551234567'},
    '2': {'ülke': 'ABD', 'kod': '+1', 'örnek': '2015550123'},
    '3': {'ülke': 'Almanya', 'kod': '+49', 'örnek': '15112345678'}
}

def numara_sorgula(numara):
    parametreler = {
        "access_key": API_KEY,
        "number": numara,
        "country_code": "",
        "format": 1
    }
    try:
        response = requests.get(API_URL, params=parametreler, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\033[31mHata: {str(e)}\033[0m")
        return None
    except ValueError:
        print("\033[31mGeçersiz API yanıtı!\033[0m")
        return None

def ana_menu():
    print("\n\033[1;36mAna Menü\033[0m")
    print("\033[34m1\033[0m - Numarayı Elle Gir")
    print("\033[34m2\033[0m - Ülkeden Seç")
    print("\033[34mq\033[0m - Çıkış")
    return input("\033[33mSeçiminiz (1/2/q): \033[0m").strip()

def ulke_secimi():
    print("\n\033[1;36mÜlke Seçimi\033[0m")
    for key, value in ULKELER.items():
        print(f"\033[34m{key}\033[0m - {value['ülke']} ({value['kod']})")
    print("\033[34m0\033[0m - Geri Dön")
    
    while True:
        secim = input("\033[33mSeçiminiz (1-3/0): \033[0m").strip()
        if secim == '0':
            return None
        if secim in ULKELER:
            return ULKELER[secim]
        print("\033[31mGeçersiz seçim! Tekrar deneyin.\033[0m")

if __name__ == "__main__":
    if API_KEY == "a214d50e6c99e1c17a90cd474ede7191":
        print("\033[93mUYARI: Varsayılan API anahtarı kullanılıyor. Lütfen geçerli bir anahtar ekleyin.\033[0m")
    
    print("\033[1;36mTelefon Numarası Sorgulama Aracı\033[0m")
    print("="*40)
    
    while True:
        secim = ana_menu()
        
        if secim.lower() == 'q':
            break
            
        elif secim == '1':
            numara = input("\n\033[33mTelefon numarası (Ülke kodu ile): \033[0m").strip()
            if not numara.startswith('+'):
                print("\033[31mHata: Lütfen ülke kodunu '+' ile başlatın\033[0m")
                continue
            
        elif secim == '2':
            secilen_ulke = ulke_secimi()
            if not secilen_ulke:
                continue
            numara = f"{secilen_ulke['kod']}{secilen_ulke['örnek']}"
            print(f"\n\033[32mSeçilen ülke: {secilen_ulke['ülke']}\033[0m")
            print(f"\033[33mSorgulanan numara: {numara}\033[0m")
            
        else:
            print("\033[31mGeçersiz seçim! Tekrar deneyin.\033[0m")
            continue
        
        veri = numara_sorgula(numara)
        
        if not veri:
            continue
            
        if veri.get("valid"):
            print("\n\033[1;32m✓ GEÇERLİ NUMARA\033[0m")
            print(f"\033[34mUluslararası Format:\033[0m {veri.get('international_format', 'Bilgi yok')}")
            print(f"\033[34mÜlke:\033[0m {veri.get('country_name', 'Bilgi yok')} ({veri.get('country_code', '')})")
            print(f"\033[34mOperatör:\033[0m {veri.get('carrier', 'Bilgi yok')}")
        else:
            print("\n\033[1;31m✗ GEÇERSİZ NUMARA!\033[0m")
            if veri.get("error"):
                print(f"\033[31mHata Detayı: {veri['error'].get('info', 'Bilgi yok')}\033[0m")

    print("\n\033[36mProgram sonlandırıldı.\033[0m")
