from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/check_stock', methods=['GET'])
def check_stock():
    try:
        url = "https://www.dyson.com.tr/airwrap-id-multi-styler-dryer-straight-wavy-vinca-blue-topaz"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        stock_info = soup.find("div", class_="stock-msg")
        if stock_info and ("Stokta" in stock_info.text or "Stokta var" in stock_info.text):
            return jsonify({"status": "Stokta VAR!"})
        else:
            return jsonify({"status": "Stokta YOK!"})
    except Exception as e:
        return jsonify({"status": "Hata", "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
