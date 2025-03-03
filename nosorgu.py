import requests

   API_KEY = "a214d50e6c99e1c17a90cd474ede7191"  # Burayı kendi API key'inle değiştir!
   API_URL = "http://apilayer.net/api/validate"

   def numara_sorgula(numara):
       parametreler = {
           "api_key": API_KEY,
           "phone": numara
       }
       response = requests.get(API_URL, params=parametreler)
       return response.json()

   if __name__ == "__main__":
       girdi = input("Numarayı gir (Ülke kodu ile, örnek: +905551112233): ")
       veri = numara_sorgula(girdi)
       
       if veri.get("valid"):
           print("Ülke:", veri["country"]["name"])
           print("Operatör:", veri["carrier"])
           print("Tip:", veri["type"])  # Sabit/Mobil
       else:
           print("Geçersiz numara veya hata!")