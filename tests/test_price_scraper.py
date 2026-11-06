"""
Tests unitarios para src/scraping/price_scraper.py.

Todos los tests usan unittest.mock para simular respuestas HTTP,
por lo que NO dependen de internet. Esto permite que el pipeline
de GitHub Actions corra en ~0.1 segundos y siempre pase.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from src.scraping import price_scraper as ps


# ---------------------------------------------------------------------------
# Tests de _normalizar_precio
# ---------------------------------------------------------------------------
class TestNormalizarPrecio(unittest.TestCase):
    def test_soles_con_punto_miles(self):
        self.assertEqual(ps._normalizar_precio("S/ 2.499"), 2499.0)

    def test_europeo_coma_decimal(self):
        self.assertEqual(ps._normalizar_precio("1.299,00"), 1299.0)

    def test_americano_coma_miles(self):
        self.assertEqual(ps._normalizar_precio("$1,299.00"), 1299.0)

    def test_solo_decimal(self):
        self.assertEqual(ps._normalizar_precio("359.00"), 359.0)

    def test_texto_invalido(self):
        self.assertIsNone(ps._normalizar_precio("Consultar precio"))

    def test_vacio(self):
        self.assertIsNone(ps._normalizar_precio(""))


# ---------------------------------------------------------------------------
# Tests de _normalizar_precio — ramas adicionales
# ---------------------------------------------------------------------------
class TestNormalizarPrecioRamas(unittest.TestCase):
    def test_multiples_puntos_miles(self):
        self.assertEqual(ps._normalizar_precio("S/ 1.299.999"), 1299999.0)

    def test_coma_decimal_dos_digitos(self):
        self.assertEqual(ps._normalizar_precio("1,50"), 1.5)

    def test_coma_miles_tres_digitos(self):
        self.assertEqual(ps._normalizar_precio("1,299"), 1299.0)


# ---------------------------------------------------------------------------
# Tests de _construir_resultado
# ---------------------------------------------------------------------------
class TestConstruirResultado(unittest.TestCase):
    def test_valido(self):
        r = ps._construir_resultado("TiendaX", "Producto Y", 199.0, "S/", "http://x")
        self.assertIsNotNone(r)
        self.assertEqual(r["tienda"], "TiendaX")
        self.assertEqual(r["precio"], 199.0)
        self.assertEqual(r["moneda"], "S/")

    def test_precio_cero_devuelve_none(self):
        self.assertIsNone(ps._construir_resultado("T", "P", 0, "S/", ""))

    def test_precio_negativo_devuelve_none(self):
        self.assertIsNone(ps._construir_resultado("T", "P", -5, "S/", ""))

    def test_precio_none_devuelve_none(self):
        self.assertIsNone(ps._construir_resultado("T", "P", None, "S/", ""))

    def test_titulo_se_trunca_a_200(self):
        titulo_largo = "X" * 500
        r = ps._construir_resultado("T", titulo_largo, 10.0, "S/", "")
        self.assertEqual(len(r["titulo"]), 200)


# ---------------------------------------------------------------------------
# Tests de buscar_precios (validación de entrada)
# ---------------------------------------------------------------------------
class TestBuscarPreciosValidacion(unittest.TestCase):
    def test_termino_vacio(self):
        r = ps.buscar_precios("")
        self.assertFalse(r["exito"])
        self.assertEqual(r["total"], 0)
        self.assertTrue(len(r["errores"]) > 0)

    def test_termino_solo_espacios(self):
        r = ps.buscar_precios("   ")
        self.assertFalse(r["exito"])


# ---------------------------------------------------------------------------
# Tests de _scrapear_plazavea (mock HTTP)
# ---------------------------------------------------------------------------
class TestScrapearPlazaVea(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_respuesta_valida(self, mock_get):
        fake_json = [
            {
                "productName": "Laptop Test",
                "linkText": "laptop-test",
                "items": [
                    {"sellers": [{"commertialOffer": {"Price": 1499.0}}]}
                ],
            }
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.json.return_value = fake_json
        mock_get.return_value = mock_resp

        resultados = ps._scrapear_plazavea("laptop")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["tienda"], "Plaza Vea")
        self.assertEqual(resultados[0]["precio"], 1499.0)
        self.assertIn("plazavea.com.pe", resultados[0]["url"])

    @patch("src.scraping.price_scraper.requests.get")
    def test_error_http(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_plazavea("laptop"), [])


class TestScrapearPlazaVeaRamas(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_excepcion_red(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.ConnectionError("sin red")
        self.assertEqual(ps._scrapear_plazavea("x"), [])

    @patch("src.scraping.price_scraper.requests.get")
    def test_json_no_lista(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.json.return_value = {"error": "no es lista"}
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_plazavea("x"), [])

    @patch("src.scraping.price_scraper.requests.get")
    def test_item_sin_precio(self, mock_get):
        fake = [{"productName": "X", "linkText": "x", "items": []}]
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.json.return_value = fake
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_plazavea("x"), [])

    @patch("src.scraping.price_scraper.requests.get")
    def test_item_malformado_no_rompe(self, mock_get):
        fake = [{"productName": "Y", "linkText": "y", "items": "no-es-lista"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.json.return_value = fake
        mock_get.return_value = mock_resp
        resultado = ps._scrapear_plazavea("x")
        self.assertIsInstance(resultado, list)


# ---------------------------------------------------------------------------
# Tests de _scrapear_ripley (mock HTTP con __NEXT_DATA__)
# ---------------------------------------------------------------------------
class TestScrapearRipley(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_next_data_valido(self, mock_get):
        next_data = {
            "props": {
                "pageProps": {
                    "data": {
                        "products": [
                            {
                                "name": "Laptop Ripley Test",
                                "price": 2199.0,
                                "url": "/laptop-ripley-test/p",
                            }
                        ]
                    }
                }
            }
        }
        html = (
            '<html><body><script id="__NEXT_DATA__" type="application/json">'
            + json.dumps(next_data)
            + "</script></body></html>"
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_get.return_value = mock_resp

        resultados = ps._scrapear_ripley("laptop")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["tienda"], "Ripley")
        self.assertEqual(resultados[0]["precio"], 2199.0)


class TestScrapearRipleyRamas(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_sin_next_data(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body>sin next data</body></html>"
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_ripley("x"), [])

    @patch("src.scraping.price_scraper.requests.get")
    def test_json_invalido_en_next_data(self, mock_get):
        html = '<script id="__NEXT_DATA__">NO ES JSON{{{</script>'
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_ripley("x"), [])

    @patch("src.scraping.price_scraper.requests.get")
    def test_excepcion_red(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.Timeout("timeout")
        self.assertEqual(ps._scrapear_ripley("x"), [])


# ---------------------------------------------------------------------------
# Tests de _scrapear_coolbox (mock HTTP)
# ---------------------------------------------------------------------------
class TestScrapearCoolbox(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_respuesta_valida(self, mock_get):
        fake_json = [
            {
                "productName": "Coolbox Test",
                "linkText": "coolbox-test",
                "items": [
                    {"sellers": [{"commertialOffer": {"Price": 999.0}}]}
                ],
            }
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = fake_json
        mock_get.return_value = mock_resp

        resultados = ps._scrapear_coolbox("test")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["tienda"], "Coolbox")
        self.assertEqual(resultados[0]["precio"], 999.0)


class TestScrapearCoolboxRamas(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_status_500(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_coolbox("x"), [])

    @patch("src.scraping.price_scraper.requests.get")
    def test_json_no_lista(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"no": "es lista"}
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_coolbox("x"), [])


# ---------------------------------------------------------------------------
# Tests de _scrapear_oechsle (mock HTTP) — NUEVA TIENDA
# ---------------------------------------------------------------------------
class TestScrapearOechsle(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_respuesta_valida(self, mock_get):
        fake_json = [
            {
                "productName": "Producto Oechsle",
                "linkText": "producto-oechsle",
                "items": [
                    {"sellers": [{"commertialOffer": {"Price": 1499.0}}]}
                ],
            }
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.json.return_value = fake_json
        mock_get.return_value = mock_resp

        resultados = ps._scrapear_oechsle("test")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["tienda"], "Oechsle")
        self.assertEqual(resultados[0]["precio"], 1499.0)


class TestScrapearOechsleRamas(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_status_500(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_oechsle("x"), [])

    @patch("src.scraping.price_scraper.requests.get")
    def test_json_no_lista(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"no": "es lista"}
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_oechsle("x"), [])


# ---------------------------------------------------------------------------
# Tests de _scrapear_hiraoka (mock HTTP) — NUEVA TIENDA
# ---------------------------------------------------------------------------
class TestScrapearHiraoka(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_respuesta_valida(self, mock_get):
        html = """
        <html><body>
        <li class="item product">
            <h3>Laptop Hiraoka Test</h3>
            <span class="price">S/ 2,199.00</span>
            <a href="/laptop-hiraoka-test">Ver</a>
        </li>
        </body></html>
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_get.return_value = mock_resp

        resultados = ps._scrapear_hiraoka("test")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["tienda"], "Hiraoka")
        self.assertEqual(resultados[0]["precio"], 2199.0)


class TestScrapearHiraokaRamas(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_excepcion_red(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.ConnectionError("sin red")
        self.assertEqual(ps._scrapear_hiraoka("x"), [])

    @patch("src.scraping.price_scraper.requests.get")
    def test_html_sin_items(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body>sin productos</body></html>"
        mock_get.return_value = mock_resp
        self.assertEqual(ps._scrapear_hiraoka("x"), [])


# ---------------------------------------------------------------------------
# Tests de las tiendas nuevas (Metro, Tottus, Wong)
# ---------------------------------------------------------------------------
class TestScrapearMetro(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_respuesta_valida(self, mock_get):
        fake_json = [{"productName": "Metro Test", "linkText": "metro-test", "items": [{"sellers": [{"commertialOffer": {"Price": 100.0}}]}]}]
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.json.return_value = fake_json
        mock_get.return_value = mock_resp
        self.assertEqual(len(ps._scrapear_metro("test")), 1)

class TestScrapearTottus(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_respuesta_valida(self, mock_get):
        fake_json = [{"productName": "Tottus Test", "linkText": "tottus-test", "items": [{"sellers": [{"commertialOffer": {"Price": 200.0}}]}]}]
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.json.return_value = fake_json
        mock_get.return_value = mock_resp
        self.assertEqual(len(ps._scrapear_tottus("test")), 1)

class TestScrapearWong(unittest.TestCase):
    @patch("src.scraping.price_scraper.requests.get")
    def test_respuesta_valida(self, mock_get):
        fake_json = [{"productName": "Wong Test", "linkText": "wong-test", "items": [{"sellers": [{"commertialOffer": {"Price": 300.0}}]}]}]
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.json.return_value = fake_json
        mock_get.return_value = mock_resp
        self.assertEqual(len(ps._scrapear_wong("test")), 1)


# ---------------------------------------------------------------------------
# Test de integración: buscar_precios ordena por precio (8 tiendas mockeadas)
# ---------------------------------------------------------------------------
class TestBuscarPreciosIntegracion(unittest.TestCase):
    @patch("src.scraping.price_scraper._scrapear_wong")
    @patch("src.scraping.price_scraper._scrapear_tottus")
    @patch("src.scraping.price_scraper._scrapear_metro")
    @patch("src.scraping.price_scraper._scrapear_hiraoka")
    @patch("src.scraping.price_scraper._scrapear_oechsle")
    @patch("src.scraping.price_scraper._scrapear_coolbox")
    @patch("src.scraping.price_scraper._scrapear_ripley")
    @patch("src.scraping.price_scraper._scrapear_plazavea")
    @patch("src.scraping.price_scraper.time.sleep")
    def test_ordenamiento_por_precio(
        self, mock_sleep, mock_pv, mock_rp, mock_cb, mock_oe, mock_hk, mock_metro, mock_tottus, mock_wong
    ):
        mock_pv.return_value = [{"tienda": "Plaza Vea", "titulo": "A", "precio": 800.0, "moneda": "S/", "url": ""}]
        mock_rp.return_value = [{"tienda": "Ripley", "titulo": "B", "precio": 600.0, "moneda": "S/", "url": ""}]
        mock_cb.return_value = [{"tienda": "Coolbox", "titulo": "C", "precio": 700.0, "moneda": "S/", "url": ""}]
        mock_oe.return_value = [{"tienda": "Oechsle", "titulo": "D", "precio": 500.0, "moneda": "S/", "url": ""}]
        mock_hk.return_value = [{"tienda": "Hiraoka", "titulo": "E", "precio": 400.0, "moneda": "S/", "url": ""}]
        mock_metro.return_value = [{"tienda": "Metro", "titulo": "F", "precio": 300.0, "moneda": "S/", "url": ""}]
        mock_tottus.return_value = [{"tienda": "Tottus", "titulo": "G", "precio": 200.0, "moneda": "S/", "url": ""}]
        mock_wong.return_value = [{"tienda": "Wong", "titulo": "H", "precio": 100.0, "moneda": "S/", "url": ""}]

        r = ps.buscar_precios("test")
        self.assertTrue(r["exito"])
        self.assertEqual(r["total"], 8)
        precios = [x["precio"] for x in r["resultados"]]
        self.assertEqual(precios, [100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0])


# ---------------------------------------------------------------------------
# Tests de excepciones: si una tienda falla, las demás siguen
# ---------------------------------------------------------------------------
class TestBuscarPreciosExcepciones(unittest.TestCase):
    @patch("src.scraping.price_scraper._scrapear_wong")
    @patch("src.scraping.price_scraper._scrapear_tottus")
    @patch("src.scraping.price_scraper._scrapear_metro")
    @patch("src.scraping.price_scraper._scrapear_hiraoka")
    @patch("src.scraping.price_scraper._scrapear_oechsle")
    @patch("src.scraping.price_scraper._scrapear_coolbox")
    @patch("src.scraping.price_scraper._scrapear_ripley")
    @patch("src.scraping.price_scraper._scrapear_plazavea")
    @patch("src.scraping.price_scraper.time.sleep")
    def test_tiendas_lanzan_excepcion(
        self, mock_sleep, mock_pv, mock_rp, mock_cb, mock_oe, mock_hk, mock_metro, mock_tottus, mock_wong
    ):
        mock_pv.side_effect = RuntimeError("fallo PV")
        mock_rp.side_effect = RuntimeError("fallo RP")
        mock_cb.side_effect = RuntimeError("fallo CB")
        mock_oe.side_effect = RuntimeError("fallo OE")
        mock_hk.side_effect = RuntimeError("fallo HK")
        mock_metro.side_effect = RuntimeError("fallo MET")
        mock_tottus.side_effect = RuntimeError("fallo TOT")
        mock_wong.side_effect = RuntimeError("fallo WON")

        r = ps.buscar_precios("test")
        self.assertFalse(r["exito"])
        self.assertEqual(r["total"], 0)
        self.assertEqual(len(r["errores"]), 8)

    @patch("src.scraping.price_scraper._scrapear_wong")
    @patch("src.scraping.price_scraper._scrapear_tottus")
    @patch("src.scraping.price_scraper._scrapear_metro")
    @patch("src.scraping.price_scraper._scrapear_hiraoka")
    @patch("src.scraping.price_scraper._scrapear_oechsle")
    @patch("src.scraping.price_scraper._scrapear_coolbox")
    @patch("src.scraping.price_scraper._scrapear_ripley")
    @patch("src.scraping.price_scraper._scrapear_plazavea")
    @patch("src.scraping.price_scraper.time.sleep")
    def test_una_tienda_falla_otras_siguen(
        self, mock_sleep, mock_pv, mock_rp, mock_cb, mock_oe, mock_hk, mock_metro, mock_tottus, mock_wong
    ):
        mock_pv.side_effect = RuntimeError("fallo PV")
        mock_rp.return_value = [{"tienda": "Ripley", "titulo": "A", "precio": 100.0, "moneda": "S/", "url": ""}]
        mock_cb.return_value = [{"tienda": "Coolbox", "titulo": "B", "precio": 200.0, "moneda": "S/", "url": ""}]
        mock_oe.return_value = []
        mock_hk.return_value = []
        mock_metro.return_value = []
        mock_tottus.return_value = []
        mock_wong.return_value = []

        r = ps.buscar_precios("test")
        self.assertTrue(r["exito"])
        self.assertEqual(r["total"], 2)
        self.assertEqual(len(r["errores"]), 1)


if __name__ == "__main__":
    unittest.main()