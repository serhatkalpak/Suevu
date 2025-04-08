from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import smtplib
import requests
from bs4 import BeautifulSoup
import json
import random
import os

Builder.load_string('''
<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        
        canvas:
            Color:
                rgba: get_color_from_hex('#f0f2f5')
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: 'Hotmail Giriş'
            font_size: 24
            bold: True
            color: get_color_from_hex('#2d3436')
            size_hint_y: None
            height: 40
            
        TextInput:
            id: email
            hint_text: 'Hotmail Adresiniz'
            multiline: False
            size_hint_y: None
            height: 40
            background_color: get_color_from_hex('#ffffff')
            
        TextInput:
            id: password
            hint_text: 'Şifreniz'
            password: True
            multiline: False
            size_hint_y: None
            height: 40
            background_color: get_color_from_hex('#ffffff')
            
        Button:
            text: 'Giriş Yap'
            size_hint_y: None
            height: 45
            background_color: get_color_from_hex('#2ecc71')
            on_press: root.login(email.text, password.text)

<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        
        Label:
            text: 'Alıcı ve Ürün Ayarları'
            font_size: 24
            bold: True
            color: get_color_from_hex('#2d3436')
            
        TextInput:
            id: receiver
            hint_text: 'Alıcı E-posta'
            multiline: False
            size_hint_y: None
            height: 40
            
        TextInput:
            id: product_url
            hint_text: 'Ürün URL'
            multiline: False
            size_hint_y: None
            height: 40
            
        TextInput:
            id: selector
            hint_text: 'CSS Selector (Örnek: .stock-status)'
            multiline: False
            size_hint_y: None
            height: 40
            
        Button:
            text: 'Kaydet ve Başlat'
            size_hint_y: None
            height: 45
            background_color: get_color_from_hex('#3498db')
            on_press: root.save_settings(receiver.text, product_url.text, selector.text)

<StatusScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        
        Label:
            id: status_label
            text: 'Durum: Beklemede'
            font_size: 18
            color: get_color_from_hex('#2d3436')
            
        Button:
            text: 'Şimdi Kontrol Et'
            size_hint_y: None
            height: 45
            background_color: get_color_from_hex('#e67e22')
            on_press: root.check_stock()
            
        Button:
            text: 'Ayarlara Dön'
            size_hint_y: None
            height: 45
            background_color: get_color_from_hex('#95a5a6')
            on_press: app.root.current = 'settings'
''')

class LoginScreen(Screen):
    def login(self, email, password):
        try:
            # Hotmail SMTP bağlantı testi
            server = smtplib.SMTP('smtp.office365.com', 587)
            server.starttls()
            server.login(email, password)
            server.quit()
            
            self.manager.email = email
            self.manager.password = password
            self.manager.current = 'settings'
        except Exception as e:
            self.show_error(f'Giriş Başarısız: {str(e)}')

    @mainthread
    def show_error(self, message):
        from kivy.uix.popup import Popup
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        popup = Popup(title='Hata', content=content, size_hint=(0.8, 0.4))
        popup.open()

class SettingsScreen(Screen):
    def save_settings(self, receiver, product_url, selector):
        config = {
            'receiver': receiver,
            'product_url': product_url,
            'selector': selector
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)
            
        self.manager.receiver = receiver
        self.manager.product_url = product_url
        self.manager.selector = selector
        self.manager.current = 'status'

class StatusScreen(Screen):
    def on_pre_enter(self):
        self.ids.status_label.text = 'Durum: Beklemede'
        
    def check_stock(self):
        Clock.schedule_once(lambda dt: self._check_stock(), 0)

    def _check_stock(self):
        try:
            headers = {'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X)'
            ])}
            
            response = requests.get(self.manager.product_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            stock_element = soup.select_one(self.manager.selector)
            
            if stock_element:
                status = 'Stokta Hazır' if any(keyword in stock_element.text.lower() 
                                             for keyword in ['stokta', 'var', 'available']) else 'Stokta Değil'
            else:
                status = 'Bilgi Bulunamadı'
                
            self.send_email(status)
            self.update_status(status)
            
        except Exception as e:
            self.update_status(f'Hata: {str(e)}')

    def send_email(self, status):
        try:
            msg = f'''From: {self.manager.email}
To: {self.manager.receiver}
Subject: Stok Durumu Güncellemesi

{self.manager.product_url}

Ürün Durumu: {status}'''

            server = smtplib.SMTP('smtp.office365.com', 587)
            server.starttls()
            server.login(self.manager.email, self.manager.password)
            server.sendmail(self.manager.email, self.manager.receiver, msg.encode('utf-8'))
            server.quit()
        except Exception as e:
            self.update_status(f'E-posta Hatası: {str(e)}')

    @mainthread
    def update_status(self, message):
        self.ids.status_label.text = f'Durum: {message}'
        
class StockTrackerApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#ffffff')
        self.title = 'Dyson Stok Takip'
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(StatusScreen(name='status'))
        
        # Config yükleme
        if os.path.exists('config.json'):
            with open('config.json') as f:
                config = json.load(f)
                sm.receiver = config.get('receiver', '')
                sm.product_url = config.get('product_url', '')
                sm.selector = config.get('selector', '')
        
        return sm

if __name__ == '__main__':
    StockTrackerApp().run()
