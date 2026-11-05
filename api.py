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
    # host='0.0.0.0' es OBLIGATORIO para que el contenedor de PHP pueda ver a Python
    app.run(host='0.0.0.0', port=5000)