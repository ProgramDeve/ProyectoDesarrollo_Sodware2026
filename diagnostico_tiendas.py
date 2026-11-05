import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
}

termino = "laptop"
urls = {
    "Coolbox": f"https://www.coolbox.pe/catalogsearch/result/?q={quote_plus(termino)}",
    "Ripley": f"https://simple.ripley.com.pe/search/{quote_plus(termino)}",
    "PlazaVea (VTEX API)": f"https://www.plazavea.com.pe/api/catalog_system/pub/products/search?ft={quote_plus(termino)}&_from=0&_to=4",
}

for tienda, url in urls.items():
    print(f"\n{'='*60}")
    print(f"TIENDA: {tienda}")
    print(f"URL: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {r.status_code} | Length: {len(r.text)}")
        if "api/catalog" in url:
            # Plaza Vea devuelve JSON
            data = r.json()
            print(f"JSON items: {len(data) if isinstance(data, list) else 'NO ES LISTA'}")
            if isinstance(data, list) and data:
                print(f"Primer item keys: {list(data[0].keys())[:8]}")
        else:
            soup = BeautifulSoup(r.text, "html.parser")
            print(f"Title: {soup.title.string if soup.title else 'NO TITLE'}")
            # Probar selectores genéricos
            for sel in ["div.product-item", "li.item.product", "div.catalog-product-item", "div[class*='product']"]:
                n = len(soup.select(sel))
                if n > 0:
                    print(f"  Selector '{sel}': {n} elementos")
    except Exception as e:
        print(f"ERROR: {e}")