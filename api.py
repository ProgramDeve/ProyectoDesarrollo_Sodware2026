# Constantes de configuración (UPPER_CASE para evitar magic numbers)
PUERTO_API: int = 5000
HOST_API: str = '0.0.0.0'
DEBUG_MODE: bool = False

from flask import Flask, request, jsonify
from src.scraping.price_scraper import buscar_precios

app = Flask(__name__)

@app.route('/buscar', methods=['POST'])
def buscar():
    data = request.get_json()
    termino = data.get('termino', '')
    resultado = buscar_precios(termino)
    return jsonify(resultado)

if __name__ == '__main__':
    # Inicia el servidor usando las constantes
    app.run(host=HOST_API, port=PUERTO_API, debug=DEBUG_MODE)