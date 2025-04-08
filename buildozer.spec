[app]

# Temel Ayarlar
title = Dyson Stok Takip
package.name = dyson_stock
package.domain = com.example
version = 1.0

# Mimari Ayarları (Yeni format)
android.archs = armeabi-v7a

# Gereksinimler
requirements = 
    python3,
    kivy==2.1.0,
    requests,
    beautifulsoup4,
    openssl

# Android Özel Ayarları
android.api = 33
android.ndk = 23b
android.permissions = INTERNET

# Diğer Ayarlar
orientation = portrait
fullscreen = 0
source.dir = .
source.include_exts = py,png,jpg,kv,json
