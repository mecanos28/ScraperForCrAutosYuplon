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


## Dependencias

### Selenium

[Selenium](https://www.selenium.dev/) es una herramienta para la automatización de navegadores web. Se usa en este proyecto para abrir y navegar por las páginas web de CRautos y Yuplon, interactuar con elementos de las páginas (como botones y enlaces), y extraer el contenido necesario.

### BeautifulSoup

[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) es una biblioteca de Python para analizar documentos HTML y XML. Se usa junto con Selenium para extraer y analizar datos de las páginas web, permitiendo localizar y extraer información específica de las estructuras HTML de CRautos.

### pandas

[pandas](https://pandas.pydata.org/) es una biblioteca de Python para el análisis y manipulación de datos. En este proyecto se usa para almacenar los datos extraídos en estructuras de datos (DataFrames), facilitando la manipulación y el análisis de los datos. También se usa para exportar los datos a archivos Excel.

### openpyxl

[openpyxl](https://openpyxl.readthedocs.io/) es una biblioteca de Python para leer y escribir archivos Excel (xlsx). Se utiliza en este proyecto para guardar los datos extraídos de CRautos y Yuplon en archivos Excel, permitiendo un fácil acceso y análisis de los datos.


------




Contacto: ferojasmel@hotmail.com

