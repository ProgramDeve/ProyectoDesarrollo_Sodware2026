# VISIONPRICE

## Equipo: CYBER FORGE
- JORGE ALVARO TURPO CHILO — Desarrollador Fullstack
- EMANUEL PAZ MOTOCANCHI — Ingeniero ML / IA
- KATSUMI ALBERT MAMANI CORRALES — DevOps / CI-CD
- JUAN GUSTAVO SEGURA VILLEGAS — QA / Testing

## Problema
Los compradores pierden mucho tiempo y dinero comparando precios y especificaciones de productos en distintas tiendas web , el proceso es manual , agotador y propenso a errores, lo que a menudo resulta en la compra de un producto inadecuado o a un precio mas alto de lo necesario.

## Solucion
VISIONPRICE es una aplicacion web impulsado por IA. El usuario accede desde su navegador , toma una foto del producto  en tiempo real con la camara de su dispositivo o importar una imagen desde su galeria . Nuestro modelo YOLO26 detecta el producto , luego el sistema consulta una base de datos y realiza web scraping en tiempo real para extraer especificaciones y precios de distintas tiendas . Finalmente devuelve al usuario una comparativa visual, los enlaces en las tiendas y una recomendacion personalizada de compra generada por IA.

## Modelo de IA
- **Categoria:** image-classification
- **Modelo:** [Ultralycs/YOLO26](https://huggingface.co/Ultralytics/YOLO26)
- **Input:** Imagen (JPG/PNG) de un producto tomado desde la camara web o importada desde su galeria  , redimensionada.
- **Output:** Cordenadas de las cajas delimitadoras , la clase del producto detectado  y el nivel de confianza
- **Justificacion:** Elemgimos YOLO26 por que es el estado del arte en deteccion de objetos en tiempo real , su version nano es extremadamente ligera lo que permite ejecutarla sin problemas en nuestra GPU local a diferencia de los modelos de clasificacion simple , YOLO no solo dice donde esta , lo cual es vital para recortar la imagen del producto y analizarlo , ademas ofrece una precision alticima con una latencia minima , ideal para una aplicacion web fluida.

## Dataset
- **Nombre:** VisionPrice-Products-v1
- **Registros:** 1000
- **Columnas:** el dataset no usa columnas tabulares , sino una estructura de directorios para vision artificial , contiene una carpeta images/ con los archivos JPG/PNG de los productos , contiene una carpeta label/ con los archivos de texto .txt , cada linea de texto representa un objeto con el formato YOLO : id_clase x_centro , y_centro ancho alto (cordenadas normalizadas de 0a 1)

## Stack
- **Lenguaje:** python
- **Framework:** flask
- **ML:** Hugging Face Transformers
- **Testing:** unittest + TDD
- **CI/CD:** GitHub Actions

## Instalacion
```bash
git clone https://github.com/ProgramDeve/ProyectoDesarrollo_Sodware2026
cd visionprice
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

## Tests
```bash
python -m unittest discover -s tests -v
```

---
*Proyecto Final — Construccion de Software — Universidad Continental*
