"""
Módulo de scraping de precios multi-tienda para VisionPrice.

Tiendas soportadas:
  - Plaza Vea (API VTEX pública, JSON directo)
  - Ripley Perú (JSON embebido __NEXT_DATA__)
  - Coolbox Perú (API VTEX pública, JSON directo)
  - Oechsle Perú (API VTEX pública, JSON directo)
  - Hiraoka Perú (HTML parsing)

Responsabilidad única: dado un término de búsqueda, consultar tiendas
y devolver una lista normalizada de precios.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------
USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
HEADERS: dict[str, str] = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
REQUEST_TIMEOUT: int = 15
DELAY_ENTRE_TIENDAS: float = 1.5
MAX_RESULTADOS_POR_TIENDA: int = 5

# Lista de palabras que indican que el producto es un accesorio, no el producto principal
PALABRAS_EXCLUIDAS = [
    # Accesorios
    "mochila", "funda", "estuche", "maletín", "case", "carcasa", 
    "cargador", "cable", "protector", "audífonos", "mouse", "teclado",
    "soporte", "base", "adaptador", "hub", "bolso",
    # Electrónica que no es laptop (si buscas laptop)
    "altavoz", "parlante", "echo", "alexa", "tablet", "celular", 
    "smartwatch", "reloj", "monitor", "impresora"
]

# ---------------------------------------------------------------------------
# UTILIDADES INTERNAS
# ---------------------------------------------------------------------------
def _normalizar_precio(texto_precio: str) -> float | None:
    """Convierte 'S/ 2.499' o '$ 1,299.00' a float."""
    if not texto_precio:
        return None
    limpio = re.sub(r"[^\d.,]", "", texto_precio)
    if "," in limpio and "." in limpio:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "," in limpio:
        partes = limpio.split(",")
        if len(partes[-1]) == 2:
            limpio = limpio.replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "." in limpio:
        if limpio.count(".") > 1:
            limpio = limpio.replace(".", "")
        elif len(limpio.split(".")[-1]) == 3:
            limpio = limpio.replace(".", "")
    try:
        return float(limpio)
    except ValueError:
        return None


def _construir_resultado(
    tienda: str, titulo: str, precio: float | None, moneda: str, url: str
) -> dict[str, Any] | None:
    if precio is None or precio <= 0:
        return None
        
    titulo_lower = titulo.lower()
    
    # Si el título contiene alguna palabra de accesorio, lo ignoramos
    for palabra in PALABRAS_EXCLUIDAS:
        if palabra in titulo_lower:
            logger.debug("Descartado por ser accesorio: %s", titulo)
            return None

    return {
        "tienda": tienda,
        "titulo": titulo.strip()[:200],
        "precio": round(precio, 2),
        "moneda": moneda,
        "url": url,
    }


# ---------------------------------------------------------------------------
# SCRAPER 1: PLAZA VEA (API VTEX — JSON directo)
# ---------------------------------------------------------------------------
def _scrapear_plazavea(termino: str) -> list[dict[str, Any]]:
    url = (
        f"https://www.plazavea.com.pe/api/catalog_system/pub/products/search"
        f"?ft={quote(termino)}"
    )
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code not in (200, 206):
            logger.warning("Plaza Vea status %d para '%s'", response.status_code, termino)
            return []
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        logger.warning("Plaza Vea falló para '%s': %s", termino, e)
        return []

    if not isinstance(data, list):
        return []

    resultados: list[dict[str, Any]] = []
    for item in data[:MAX_RESULTADOS_POR_TIENDA]:
        try:
            nombre = item.get("productName", "")
            link_text = item.get("linkText", "")
            producto_url = f"https://www.plazavea.com.pe/{link_text}/p" if link_text else ""

            precio = None
            items = item.get("items", [])
            if items and isinstance(items, list):
                sellers = items[0].get("sellers", [])
                if sellers and isinstance(sellers, list):
                    offer = sellers[0].get("commertialOffer", {})
                    precio = offer.get("Price")

            resultado = _construir_resultado("Plaza Vea", nombre, precio, "S/", producto_url)
            if resultado:
                resultados.append(resultado)
        except Exception as e:
            logger.debug("Error parseando item de Plaza Vea: %s", e)
            continue

    return resultados


# ---------------------------------------------------------------------------
# SCRAPER 2: RIPLEY PERÚ (JSON embebido __NEXT_DATA__)
# ---------------------------------------------------------------------------
def _scrapear_ripley(termino: str) -> list[dict[str, Any]]:
    url = f"https://simple.ripley.com.pe/search/{quote(termino)}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning("Ripley falló para '%s': %s", termino, e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    next_data_script = soup.find("script", id="__NEXT_DATA__")
    if not next_data_script or not next_data_script.string:
        logger.warning("Ripley: no se encontró __NEXT_DATA__ para '%s'", termino)
        return []

    try:
        data = json.loads(next_data_script.string)
    except json.JSONDecodeError as e:
        logger.warning("Ripley: JSON inválido en __NEXT_DATA__: %s", e)
        return []

    def _buscar_lista_productos(nodo):
        if isinstance(nodo, list) and nodo:
            primer = nodo[0]
            if isinstance(primer, dict):
                claves = set(primer.keys())
                if ("name" in claves or "productName" in claves or "title" in claves) and any("price" in k.lower() for k in claves):
                    return nodo
            for hijo in nodo:
                encontrado = _buscar_lista_productos(hijo)
                if encontrado: return encontrado
        elif isinstance(nodo, dict):
            for valor in nodo.values():
                encontrado = _buscar_lista_productos(valor)
                if encontrado: return encontrado
        return None

    productos = _buscar_lista_productos(data)
    if not productos:
        return []

    resultados: list[dict[str, Any]] = []
    vistos: set[str] = set()

    for prod in productos[:MAX_RESULTADOS_POR_TIENDA]:
        try:
            nombre = prod.get("name") or prod.get("productName") or prod.get("title") or ""
            if not nombre or nombre in vistos: continue

            precio = None
            for clave, valor in prod.items():
                if "price" in clave.lower() and isinstance(valor, (int, float)) and valor > 0:
                    precio = float(valor)
                    break
            if precio is None: continue

            url_prod = prod.get("url") or prod.get("link") or prod.get("slug") or ""
            if url_prod and not url_prod.startswith("http"):
                url_prod = "https://simple.ripley.com.pe" + url_prod

            vistos.add(nombre)
            resultado = _construir_resultado("Ripley", nombre, precio, "S/", url_prod)
            if resultado: resultados.append(resultado)
        except Exception:
            continue

    return resultados


# ---------------------------------------------------------------------------
# SCRAPER 3: COOLBOX (API VTEX — JSON directo)
# ---------------------------------------------------------------------------
def _scrapear_coolbox(termino: str) -> list[dict[str, Any]]:
    url = f"https://www.coolbox.pe/api/catalog_system/pub/products/search?ft={quote(termino)}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code not in (200, 206):
            return []
        data = response.json()
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    resultados: list[dict[str, Any]] = []
    for item in data[:MAX_RESULTADOS_POR_TIENDA]:
        try:
            nombre = item.get("productName", "")
            link_text = item.get("linkText", "")
            producto_url = f"https://www.coolbox.pe/{link_text}/p" if link_text else ""

            precio = None
            items = item.get("items", [])
            if items and isinstance(items, list):
                sellers = items[0].get("sellers", [])
                if sellers and isinstance(sellers, list):
                    offer = sellers[0].get("commertialOffer", {})
                    precio = offer.get("Price")

            resultado = _construir_resultado("Coolbox", nombre, precio, "S/", producto_url)
            if resultado: resultados.append(resultado)
        except Exception:
            continue

    return resultados


# ---------------------------------------------------------------------------
# SCRAPER 4: OECHSLE (API VTEX — JSON directo)
# ---------------------------------------------------------------------------
def _scrapear_oechsle(termino: str) -> list[dict[str, Any]]:
    url = f"https://www.oechsle.pe/api/catalog_system/pub/products/search?ft={quote(termino)}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code not in (200, 206):
            return []
        data = response.json()
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    resultados: list[dict[str, Any]] = []
    for item in data[:MAX_RESULTADOS_POR_TIENDA]:
        try:
            nombre = item.get("productName", "")
            link_text = item.get("linkText", "")
            producto_url = f"https://www.oechsle.pe/{link_text}/p" if link_text else ""

            precio = None
            items = item.get("items", [])
            if items and isinstance(items, list):
                sellers = items[0].get("sellers", [])
                if sellers and isinstance(sellers, list):
                    offer = sellers[0].get("commertialOffer", {})
                    precio = offer.get("Price")

            resultado = _construir_resultado("Oechsle", nombre, precio, "S/", producto_url)
            if resultado: resultados.append(resultado)
        except Exception:
            continue

    return resultados

# ---------------------------------------------------------------------------
# SCRAPER EXTRA: METRO (API VTEX — JSON directo)
# ---------------------------------------------------------------------------
def _scrapear_metro(termino: str) -> list[dict[str, Any]]:
    """
    Consulta Metro Perú vía API VTEX pública (JSON).
    Mismo patrón que Plaza Vea, Coolbox y Oechsle.
    """
    url = f"https://www.metro.pe/api/catalog_system/pub/products/search?ft={quote(termino)}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code not in (200, 206):
            logger.warning("Metro status %d para '%s'", response.status_code, termino)
            return []
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        logger.warning("Metro falló para '%s': %s", termino, e)
        return []

    if not isinstance(data, list):
        return []

    resultados: list[dict[str, Any]] = []
    for item in data[:MAX_RESULTADOS_POR_TIENDA]:
        try:
            nombre = item.get("productName", "")
            link_text = item.get("linkText", "")
            producto_url = f"https://www.metro.pe/{link_text}/p" if link_text else ""

            precio = None
            items = item.get("items", [])
            if items and isinstance(items, list):
                sellers = items[0].get("sellers", [])
                if sellers and isinstance(sellers, list):
                    offer = sellers[0].get("commertialOffer", {})
                    precio = offer.get("Price")

            resultado = _construir_resultado("Metro", nombre, precio, "S/", producto_url)
            if resultado:
                resultados.append(resultado)
        except Exception as e:
            logger.debug("Error parseando item de Metro: %s", e)
            continue

    logger.info("Metro: %d resultados para '%s'", len(resultados), termino)
    return resultados
# ---------------------------------------------------------------------------
# SCRAPER 5: HIRAOKA (HTML parsing)
# ---------------------------------------------------------------------------
def _scrapear_hiraoka(termino: str) -> list[dict[str, Any]]:
    url = f"https://www.hiraoka.com.pe/catalogsearch/result/?q={quote(termino)}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("li.item.product")
    if not items:
        return []

    resultados: list[dict[str, Any]] = []
    vistos: set[str] = set()

    for item in items:
        if len(resultados) >= MAX_RESULTADOS_POR_TIENDA:
            break
        try:
            titulo_el = item.select_one("h3") or item.select_one("h2") or item.select_one("a.product-item-link")
            titulo = titulo_el.get_text(strip=True) if titulo_el else ""
            if not titulo or len(titulo) < 5 or titulo in vistos:
                continue

            precio_el = item.select_one("span.price")
            if not precio_el:
                price_box = item.select_one(".price-box")
                if price_box:
                    precio_el = price_box.select_one("[class*='price']")
            if not precio_el:
                continue
            
            precio = _normalizar_precio(precio_el.get_text(strip=True))
            if precio is None:
                continue

            link_el = item.select_one("a[href]")
            producto_url = link_el["href"] if link_el else ""
            if producto_url and not producto_url.startswith("http"):
                producto_url = "https://www.hiraoka.com.pe" + producto_url

            vistos.add(titulo)
            resultado = _construir_resultado("Hiraoka", titulo, precio, "S/", producto_url)
            if resultado:
                resultados.append(resultado)
        except Exception:
            continue

    return resultados


# ---------------------------------------------------------------------------
# FUNCIÓN PÚBLICA
# ---------------------------------------------------------------------------
def buscar_precios(termino: str) -> dict[str, Any]:
    if not termino or not termino.strip():
        return {
            "exito": False, "termino": termino, "total": 0,
            "resultados": [], "errores": ["El término no puede estar vacío"],
        }

    termino = termino.strip()
    errores: list[str] = []
    resultados: list[dict[str, Any]] = []

    # --- Plaza Vea ---
    try:
        resultados.extend(_scrapear_plazavea(termino))
    except Exception as e:
        errores.append(f"Plaza Vea: {str(e)}")
    time.sleep(DELAY_ENTRE_TIENDAS)

    # --- Ripley ---
    try:
        resultados.extend(_scrapear_ripley(termino))
    except Exception as e:
        errores.append(f"Ripley: {str(e)}")
    time.sleep(DELAY_ENTRE_TIENDAS)

    # --- Coolbox ---
    try:
        resultados.extend(_scrapear_coolbox(termino))
    except Exception as e:
        errores.append(f"Coolbox: {str(e)}")
    time.sleep(DELAY_ENTRE_TIENDAS)

    # --- Oechsle ---
    try:
        resultados.extend(_scrapear_oechsle(termino))
    except Exception as e:
        errores.append(f"Oechsle: {str(e)}")
    time.sleep(DELAY_ENTRE_TIENDAS)

    # --- Hiraoka ---
    try:
        resultados.extend(_scrapear_hiraoka(termino))
    except Exception as e:
        errores.append(f"Hiraoka: {str(e)}")
    time.sleep(DELAY_ENTRE_TIENDAS)

    # --- Metro ---
    try:
        resultados.extend(_scrapear_metro(termino))
    except Exception as e:
        logger.exception("Error inesperado en Metro")
        errores.append(f"Metro: {str(e)}")
    # Ordenar por precio ascendente
    resultados.sort(key=lambda r: r["precio"])

    return {
        "exito": len(resultados) > 0,
        "termino": termino,
        "total": len(resultados),
        "resultados": resultados,
        "errores": errores,
    }