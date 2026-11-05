"""Prueba manual del módulo de scraping (sin Flask, sin YOLO).

Si se ejecuta desde una terminal interactiva, muestra emojis y resumen.
Si se ejecuta desde PHP (sin TTY), imprime SOLO JSON limpio para que
PHP lo pueda parsear sin errores de encoding (cp1252 en Windows).
"""

import json
import sys

from src.scraping.price_scraper import buscar_precios


def _es_terminal_interactiva() -> bool:
    """Detecta si stdin es una terminal (True) o un pipe/PHP (False)."""
    try:
        return sys.stdin.isatty()
    except Exception:
        return False


def main(termino: str) -> None:
    interactivo = _es_terminal_interactiva()

    if interactivo:
        print(f"Buscando precios para: '{termino}'\n")

    resultado = buscar_precios(termino)

    # JSON siempre se imprime (PHP lo necesita)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    if interactivo:
        if resultado["exito"]:
            print(f"\n[OK] {resultado['total']} resultados encontrados")
            print(
                f"   Precio mas bajo: "
                f"{resultado['resultados'][0]['precio']} "
                f"{resultado['resultados'][0]['moneda']}"
            )
        else:
            print(f"\n[!] Sin resultados. Errores: {resultado['errores']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_scraper_manual.py \"laptop lenovo\"")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))

# api.py
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
    # host='0.0.0.0' es CRUCIAL para que otros contenedores puedan conectarse [citation:7]
    app.run(host='0.0.0.0', port=5000)