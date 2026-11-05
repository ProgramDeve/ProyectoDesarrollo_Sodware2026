import requests
from bs4 import BeautifulSoup
from src.scraping.price_scraper import HEADERS, REQUEST_TIMEOUT
from urllib.parse import quote_plus

termino = "laptop lenovo"
url = f"https://listado.mercadolibre.com.pe/{quote_plus(termino)}_NoIndex_True"

print("URL:", url)
r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
print("Status:", r.status_code)
print("Length:", len(r.text))

soup = BeautifulSoup(r.text, "html.parser")
print("Title:", soup.title.string if soup.title else "NO TITLE")

# Probar varios selectores candidatos
for sel in [
    "li.ui-search-layout__item",
    "div.poly-card",
    "div.ui-search-result__wrapper",
    "li.ui-search-result",
]:
    print(f"{sel}: {len(soup.select(sel))}")

# Ver si hay indicadores de página de verificación
texto = soup.get_text().lower()
if "verificación" in texto or "verifica" in texto or "captcha" in texto:
    print("⚠️ Posible página de verificación detectada")
elif len(r.text) < 20000:
    print("⚠️ Página demasiado corta, posible redirección o bloqueo")

# Si hay poly-card, mostrar el título del primero
cards = soup.select("div.poly-card")
if cards:
    print("\n--- Primer poly-card (título y precio) ---")
    titulo = cards[0].select_one("a.poly-component__title")
    precio = cards[0].select_one(".andes-money-amount__fraction")
    print("Título:", titulo.get_text(strip=True) if titulo else "NO TITLE")
    print("Precio:", precio.get_text(strip=True) if precio else "NO PRICE")