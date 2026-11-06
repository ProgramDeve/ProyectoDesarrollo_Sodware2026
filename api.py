from flask import Flask, request, jsonify
from src.scraping.price_scraper import buscar_precios

# Definimos constantes (UPPER_CASE) para evitar números mágicos
PUERTO_API = 5000
HOST_API = '0.0.0.0'

app = Flask(__name__)

@app.route('/buscar', methods=['POST'])
def buscar():
    data = request.get_json()
    termino = data.get('termino', '')
    resultado = buscar_precios(termino)
    return jsonify(resultado)

if __name__ == '__main__':
    # host='0.0.0.0' es OBLIGATORIO para que el contenedor de PHP pueda ver a Python
    app.run(host=HOST_API, port=PUERTO_API)