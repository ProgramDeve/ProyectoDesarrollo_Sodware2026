class ComparadorPrecios:
    """Módulo para calcular la mejor oferta y recomendaciones."""
    
    DESCUENTO_MAXIMO = 100
    
    def calcular_descuento(self, precio, porcentaje):
        self._validar_porcentaje(porcentaje)
        descuento_aplicado = precio * (porcentaje / self.DESCUENTO_MAXIMO)
        return precio - descuento_aplicado

    def _validar_porcentaje(self, porcentaje):
        if porcentaje < 0 or porcentaje > self.DESCUENTO_MAXIMO:
            raise ValueError(f"El porcentaje debe estar entre 0 y {self.DESCUENTO_MAXIMO}")

    def mejor_opcion(self, lista_precios):
        self._validar_lista(lista_precios)
        return min(lista_precios)
        
    def _validar_lista(self, lista):
        if not lista:
            raise ValueError("La lista de precios no puede estar vacía")

    def recomendar(self, precio_tienda_a, precio_tienda_b):
        if precio_tienda_a < precio_tienda_b:
            return "Comprar en Tienda A"
        elif precio_tienda_b < precio_tienda_a:
            return "Comprar en Tienda B"
        else:
            return "Precios iguales, elige la que tenga mejor garantía"