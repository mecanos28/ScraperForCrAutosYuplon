# Scraper para CRautos y Yuplon

Este proyecto incluye dos scripts de web scraping para extraer datos de sitios web populares en Costa Rica: CRautos y Yuplon. Los datos se almacenan en archivos Excel para su posterior análisis.

## Requisitos

- Python 3.x
- Selenium
- BeautifulSoup
- pandas
- openpyxl

## Instalación

1. Clona el repositorio:

    ```bash
    git clone https://github.com/mecanos28/ScraperForCrAutosYuplon.git
    cd ScraperForCrAutosYuplon
    ```

2. Crea un entorno virtual e instala las dependencias:

    ```bash
    python -m venv env
    source env/bin/activate  # En Windows: env\Scripts\activate
    pip install -r requirements.txt
    ```

3. Descarga el ChromeDriver compatible con tu versión de Chrome y tu sistema operativo desde [aquí](https://sites.google.com/chromium.org/driver/).

4. Coloca el ejecutable de ChromeDriver en la carpeta `chromedriver` dentro del directorio del proyecto.

## Uso

### Scraper para CRautos

Este script navega por las listas de vehículos en CRautos y extrae datos relevantes como modelo, año, precio, kilometraje, etc.

1. Ejecuta el script:

    ```bash
    python3 crautos/crautos.py
    ```

2. Los datos extraídos se guardarán en un archivo Excel en la carpeta `output`.

### Scraper para Yuplon

Este script navega por las campañas en Yuplon y extrae detalles de las ofertas, incluyendo título principal, subtítulos, precios, descuentos y fechas de validez.

1. Ejecuta el script:

    ```bash
    python3 yuplon/yuplon.py
    ```

2. Los datos extraídos se guardarán en exceles y generaran plots con datos relevantes.


Contacto: ferojasmel@hotmail.com

