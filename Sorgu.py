import requests

API_KEY = "a214d50e6c99e1c17a90cd474ede7191"  # Kendi API key'inizi ekleyin!
API_URL = "http://apilayer.net/api/validate"

ULKELER = {
    '1': {'ülke': 'Türkiye', 'kod': '+90', 'uzunluk': 10},
    '2': {'ülke': 'ABD', 'kod': '+1', 'uzunluk': 10},
    '3': {'ülke': 'Almanya', 'kod': '+49', 'uzunluk': 11}
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

def numara_al(ulke_bilgisi):
    while True:
        numara = input(f"\n\033[33m{ulke_bilgisi['ülke']} için numarayı girin ({ulke_bilgisi['uzunluk']} haneli): \033[0m").strip()
        if not numara.isdigit():
            print("\033[31mHata: Sadece rakam girin!\033[0m")
            continue
        if len(numara) != ulke_bilgisi['uzunluk']:
            print(f"\033[31mHata: {ulke_bilgisi['ülke']} numarası {ulke_bilgisi['uzunluk']} haneli olmalı!\033[0m")
            continue
        return f"{ulke_bilgisi['kod']}{numara}"

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
            numara = numara_al(secilen_ulke)
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
            
            # Türkiye için ek bilgiler
            if veri.get('country_code') == 'TR':
                print(f"\033[34mDetaylı Konum:\033[0m {veri.get('location', 'Bilgi yok')}")
                print(f"\033[34mHat Tipi:\033[0m {veri.get('line_type', 'Bilgi yok').title()}")
                print(f"\033[34mAlan Kodu:\033[0m {numara[3:5]}")  # Türkiye için ilk iki rakam
        else:
            print("\n\033[1;31m✗ GEÇERSİZ NUMARA!\033[0m")
            if veri.get("error"):
                print(f"\033[31mHata Detayı: {veri['error'].get('info', 'Bilgi yok')}\033[0m")

    print("\n\033[36mProgram sonlandırıldı.\033[0m")

ULKELER = {
    '1': {'ülke': 'Türkiye', 'kod': '+90', 'uzunluk': 10, 'operator_aralik': {
        '505': 'Turkcell',
        '506': 'Turkcell',
        '507': 'Turkcell',
        '551': 'Turkcell',
        '552': 'Turkcell',
        '553': 'Turkcell',
        '554': 'Turkcell',
        '555': 'Turkcell',
        '559': 'Turkcell',
        '530': 'Vodafone',
        # ... Diğer operatör kodları
    }},
    # Diğer ülkeler...
}

def operator_bul(numara, ulke_kodu):
    if ulke_kodu != 'TR':
        return None
    
    ilk_uc = numara[3:6]
    return ULKELER['1']['operator_aralik'].get(ilk_uc, "Bilinmeyen Operatör")

# ... (Önceki fonksiyonlar aynı kalıyor)

if veri.get("valid"):
    print("\n\033[1;32m✓ GEÇERLİ NUMARA\033[0m")
    print(f"\033[34mUluslararası Format:\033[0m {veri.get('international_format', 'Bilgi yok')}")
    
    # Türkiye'ye özel detaylar
    if veri.get('country_code') == 'TR':
        operator = operator_bul(numara, 'TR')
        print(f"\033[34mTahmini Operatör:\033[0m {operator}")
        print(f"\033[34mNumara Tipi:\033[0m {'Mobil' if veri.get('line_type') == 'mobile' else 'Sabit Hat'}")
        print(f"\033[34mİl Kodu:\033[0m {numara[3:5]}")  # İlk iki hane
        
    print(f"\033[34mOperatör (API):\033[0m {veri.get('carrier', 'Bilgi yok')}")
    print(f"\033[34mKayıtlı İsim:\033[0m \033[31mBu bilgi gizlilik politikası gereği gösterilemez\033[0m")

else:
    #... Hata mesajları
