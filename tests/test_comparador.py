import unittest
import sys
import os

# Esto arregla el error de importación en Windows
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.comparador_precios import ComparadorPrecios

class TestComparador(unittest.TestCase):
    def setUp(self):
        self.comp = ComparadorPrecios()

    def test_calcular_descuento_valido(self):
        self.assertEqual(self.comp.calcular_descuento(100, 20), 80)

    def test_calcular_descuento_invalido(self):
        with self.assertRaises(ValueError):
            self.comp.calcular_descuento(100, 150)

    def test_mejor_opcion(self):
        self.assertEqual(self.comp.mejor_opcion([150, 120, 200]), 120)

    def test_mejor_opcion_vacia(self):
        with self.assertRaises(ValueError):
            self.comp.mejor_opcion([])

    def test_recomendar_tienda_a(self):
        self.assertEqual(self.comp.recomendar(100, 150), "Comprar en Tienda A")

    def test_recomendar_iguales(self):
        self.assertEqual(self.comp.recomendar(100, 100), "Precios iguales, elige la que tenga mejor garantía")

if __name__ == "__main__":
    unittest.main()