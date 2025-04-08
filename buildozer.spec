[app]

# Uygulama Bilgileri
title = Dyson Stok Takip
package.name = dysonstock
package.domain = org.kodlayan
version = 1.0

# Kaynak Ayarları
source.dir = .
source.include_exts = py,png,jpg,json,kv,ttf

# Gereksinimler (TEK BÖLÜM)
requirements = 
    python3,
    kivy==2.1.0,
    requests,
    beautifulsoup4,
    openssl,
    pyopenssl

# Android Ayarları
android.api = 33
android.ndk = 23b
android.permissions = INTERNET
android.arch = armeabi-v7a

# Oryantasyon
orientation = portrait
fullscreen = 0

# Logolama 
icon.filename = logo.png
presplash.filename = splash.png

# Diğer Ayarlar
p4a.branch = develop
android.allow_backup = true
android.wakelock = true
android.meta_data = android.app.uses_cleartext_traffic=true
