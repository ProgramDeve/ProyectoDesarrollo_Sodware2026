"""Prueba manual del módulo de scraping."""
import json
import sys
from src.scraping.price_scraper import buscar_precios

def _es_terminal_interactiva() -> bool:
    try:
        return sys.stdin.isatty()
    except Exception:
        return False

def main(termino: str) -> None:
    interactivo = _es_terminal_interactiva()
    if interactivo:
        print(f"Buscando precios para: '{termino}'\n")

    resultado = buscar_precios(termino)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    if interactivo:
        if resultado["exito"]:
            print(f"\n[OK] {resultado['total']} resultados encontrados")
            print(f"   Precio mas bajo: {resultado['resultados'][0]['precio']} {resultado['resultados'][0]['moneda']}")
        else:
            print(f"\n[!] Sin resultados. Errores: {resultado['errores']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_scraper_manual.py \"laptop lenovo\"")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))