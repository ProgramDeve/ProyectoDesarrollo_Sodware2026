import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
}

termino = "laptop"

# ============ PLAZA VEA: probar diferentes variantes de la API ============
print("\n" + "="*70)
print("PLAZA VEA — probando variantes de URL")
print("="*70)
variantes = [
    f"https://www.plazavea.com.pe/api/catalog_system/pub/products/search?ft={quote_plus(termino)}",
    f"https://www.plazavea.com.pe/api/catalog_system/pub/products/search/?ft={quote_plus(termino)}&_from=0&_to=4",
    f"https://www.plazavea.com.pe/api/catalog_system/pub/products/search?ft={quote_plus(termino)}&_from=0&_to=4",
    f"https://www.plazavea.com.pe/api/catalog_system/pub/products/search/{quote_plus(termino)}?_from=0&_to=4",
]
for i, u in enumerate(variantes, 1):
    try:
        r = requests.get(u, headers=HEADERS, timeout=10)
        print(f"\n[{i}] Status {r.status_code} | Length {len(r.text)} | URL {u}")
        if r.status_code == 200:
            data = r.json()
            print(f"    JSON items: {len(data) if isinstance(data, list) else 'NO LISTA'}")
            if isinstance(data, list) and data:
                print(f"    Primer item: {json.dumps(data[0], indent=2)[:600]}")
                break
        else:
            print(f"    Body: {r.text[:200]}")
    except Exception as e:
        print(f"[{i}] ERROR: {e}")

# ============ RIPLEY: inspeccionar estructura real ============
print("\n" + "="*70)
print("RIPLEY — inspeccionando HTML real")
print("="*70)
try:
    r = requests.get(f"https://simple.ripley.com.pe/search/{quote_plus(termino)}", headers=HEADERS, timeout=15)
    print(f"Status: {r.status_code} | Length: {len(r.text)}")
    soup = BeautifulSoup(r.text, "html.parser")
    # Buscar todos los divs con 'product' en la clase y contar por clase exacta
    from collections import Counter
    clases = Counter()
    for div in soup.find_all(class_=True):
        for c in div.get("class", []):
            if "product" in c.lower() or "price" in c.lower() or "name" in c.lower():
                clases[c] += 1
    print("\nClases más frecuentes (product/price/name):")
    for c, n in clases.most_common(15):
        print(f"  .{c}: {n}")
    # Mostrar el HTML del primer div con clase que contenga 'product'
    primer = soup.select_one("div[class*='product']")
    if primer:
        print("\n--- Primer div[class*='product'] (primeros 1500 chars) ---")
        print(str(primer)[:1500])
except Exception as e:
    print(f"ERROR: {e}")

# ============ COOLBOX: ver estructura del bloque de precios ============
print("\n" + "="*70)
print("COOLBOX — inspeccionando bloque de precios")
print("="*70)
try:
    r = requests.get(f"https://www.coolbox.pe/catalogsearch/result/?q={quote_plus(termino)}", headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    print(f"Status: {r.status_code} | Length: {len(r.text)}")
    # Buscar contenedores con 'product' y ver sus clases
    from collections import Counter
    clases = Counter()
    for div in soup.find_all(class_=True):
        for c in div.get("class", []):
            if "product" in c.lower() or "price" in c.lower():
                clases[c] += 1
    print("\nClases frecuentes (product/price):")
    for c, n in clases.most_common(15):
        print(f"  .{c}: {n}")
    # Buscar todos los elementos con 'price' y mostrar los 5 primeros
    print("\n--- Elementos con 'price' en clase (primeros 5) ---")
    for el in soup.select("[class*='price']")[:5]:
        print(f"  <{el.name} class='{' '.join(el.get('class', []))}'> → {el.get_text(strip=True)[:80]!r}")
except Exception as e:
    print(f"ERROR: {e}")