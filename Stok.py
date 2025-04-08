# stock_server.py
from flask import Flask, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

def check_stock():
    # Örnek olarak sabit döndürüyoruz
    stock_available = True  # Burada siteleri scrape edersin
    return stock_available

def send_email_notification():
    sender = "serhatkaplaann@gmail.com"
    password = "uygulama_şifresi"  # Google için 'uygulama şifresi' kullan!
    recipient = "serhatkalpak40@gmail.com@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "Stok Bildirimi"
    body = "Mavi Dyson ürün stokta!"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipient, msg.as_string())
    server.quit()

@app.route('/check_stock')
def check_stock_api():
    if check_stock():
        send_email_notification()
        return jsonify(status="Stokta! E-posta gönderildi.")
    else:
        return jsonify(status="Stok yok.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
