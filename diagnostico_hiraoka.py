"""Diagnóstico rápido para saber si Hiraoka permite scraping simple."""
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-PE,es;q=0.9",
}

url = "https://www.hiraoka.com.pe/catalogsearch/result/?q=laptop"
print("URL:", url)
try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    print("Status:", r.status_code)
    print("Length:", len(r.text))
    soup = BeautifulSoup(r.text, "html.parser")
    print("Title:", soup.title.string if soup.title else "NO TITLE")
    for sel in [
        "div.product-item",
        "li.item.product",
        "[class*='product']",
        "[class*='price']",
        "div.product-item-info",
    ]:
        print(f"{sel}: {len(soup.select(sel))}")
    texto = r.text.lower()
    if any(k in texto for k in ["cloudflare", "captcha", "verifica", "challenge"]):
        print("⚠️ Posible protección anti-bot detectada")
except Exception as e:
    print("ERROR:", e)