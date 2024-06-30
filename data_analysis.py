import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')


def load_data(file_path):
    # Cargar datos desde un archivo Excel
    return pd.read_excel(file_path)


def clean_data(df):
    # Eliminar filas donde "Precio" es "ND"
    df = df[df['Precio'] != '$ND'].copy()

    # Convertir el precio a float después de eliminar caracteres no deseados
    df['Precio'] = df['Precio'].replace('[\$,]', '', regex=True)

    # Identificar y eliminar filas donde "Precio" no es numérico
    df = df[pd.to_numeric(df['Precio'], errors='coerce').notnull()]
    df['Precio'] = df['Precio'].astype(float)

    # Convertir el año a entero
    df['Año'] = df['Año'].astype(int)

    return df

def get_average_price_by_year(df):
    # Obtener el precio promedio por año
    return df.groupby('Año')['Precio'].mean()


def get_most_common_models(df, top_n=10):
    # Obtener los modelos de carros más comunes
    return df['Version'].value_counts().head(top_n)


def get_most_expensive_models(df, top_n=10):
    # Obtener los modelos de carros más caros
    return df.groupby('Version')['Precio'].max().nlargest(top_n)


def get_cheapest_models(df, top_n=10):
    # Obtener los modelos de carros más baratos
    return df.groupby('Version')['Precio'].min().nsmallest(top_n)


def plot_average_price_by_year(df):
    # Graficar el precio promedio por año
    avg_price_by_year = get_average_price_by_year(df)
    avg_price_by_year.plot(kind='line')
    plt.title('Precio Promedio de carros por Año')
    plt.xlabel('Año')
    plt.ylabel('Precio Promedio')
    plt.grid(True)
    plt.savefig('precio_promedio_por_año.png')


def plot_most_common_models(df, top_n=10):
    # Obtener los modelos de coches más comunes
    most_common_models = get_most_common_models(df, top_n)

    # Crear la gráfica de barras
    plt.figure(figsize=(10, 6))
    bars = most_common_models.plot(kind='bar')

    # Ajustar los valores del eje y
    max_y = most_common_models.max() + 10  # Un poco más alto que el valor máximo para mejor visualización
    plt.ylim(0, max_y)

    # Título y etiquetas
    plt.title(f'Top {top_n} Modelos de carros Más Comunes')
    plt.xlabel('Modelo de Carro')
    plt.ylabel('Cantidad')

    # Rotar las etiquetas del eje x para mejor visualización
    plt.xticks(rotation=45, ha="right")

    # Ajustar el margen inferior para evitar que las etiquetas se corten
    plt.subplots_adjust(bottom=0.25)

    # Añadir etiquetas de conteo encima de cada barra
    for bar in bars.patches:
        plt.annotate(format(bar.get_height(), ',d'),
                     (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='center',
                     size=10, xytext=(0, 8),
                     textcoords='offset points')

    # Añadir cuadrícula para facilitar la lectura de valores
    plt.grid(True, axis='y')

    # Guardar la gráfica
    plt.savefig('modelos_mas_comunes.png')


def plot_most_expensive_models(df, top_n=10):
    # Obtener los modelos de coches más caros
    most_expensive_models = get_most_expensive_models(df, top_n)

    # Crear la gráfica de barras
    plt.figure(figsize=(10, 6))
    bars = most_expensive_models.plot(kind='bar')

    # Ajustar los valores del eje y
    max_y = most_expensive_models.max() + 1000  # Un poco más alto que el valor máximo para mejor visualización
    plt.ylim(0, max_y)

    # Título y etiquetas
    plt.title(f'Top {top_n} Modelos de carros Más Caros')
    plt.xlabel('Modelo de Carro')
    plt.ylabel('Precio')

    # Rotar las etiquetas del eje x para mejor visualización
    plt.xticks(rotation=45, ha="right")

    # Ajustar el margen inferior para evitar que las etiquetas se corten
    plt.subplots_adjust(bottom=0.25)

    # Añadir etiquetas de precio encima de cada barra
    for bar in bars.patches:
        plt.annotate(f"${bar.get_height():,}",
                     (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='center',
                     size=10, xytext=(0, 8),
                     textcoords='offset points')

    # Añadir cuadrícula para facilitar la lectura de valores
    plt.grid(True, axis='y')

    # Guardar la gráfica
    plt.savefig('modelos_mas_caros.png')


def plot_cheapest_models(df, top_n=10):
    # Obtener los modelos de coches más baratos
    cheapest_models = get_cheapest_models(df, top_n)

    # Crear la gráfica de barras
    plt.figure(figsize=(10, 6))
    bars = cheapest_models.plot(kind='bar')

    # Ajustar los valores del eje y
    max_y = cheapest_models.max() + 1000  # Un poco más alto que el valor máximo para mejor visualización
    plt.ylim(0, max_y)

    # Título y etiquetas
    plt.title(f'Top {top_n} Modelos de carros Más Baratos')
    plt.xlabel('Modelo de Carro')
    plt.ylabel('Precio')

    # Rotar las etiquetas del eje x para mejor visualización
    plt.xticks(rotation=45, ha="right")

    # Ajustar el margen inferior para evitar que las etiquetas se corten
    plt.subplots_adjust(bottom=0.25)

    # Añadir etiquetas de precio encima de cada barra
    for bar in bars.patches:
        plt.annotate(f"${bar.get_height():,}",
                     (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='center',
                     size=10, xytext=(0, 8),
                     textcoords='offset points')

    # Añadir cuadrícula para facilitar la lectura de valores
    plt.grid(True, axis='y')

    # Guardar la gráfica
    plt.savefig('modelos_mas_baratos.png')


def clean_data(df):
    # Remove rows where "Precio" is "ND"
    df = df[df['Precio'] != '$ND'].copy()

    # Convert the "Precio" column to float after removing unwanted characters
    df['Precio'] = df['Precio'].replace('[\$,]', '', regex=True)

    # Identify and remove rows where "Precio" is not numeric
    df = df[pd.to_numeric(df['Precio'], errors='coerce').notnull()]
    df['Precio'] = df['Precio'].astype(float)

    # Convert the "Año" column to integer
    df['Año'] = df['Año'].astype(int)

    return df


def clean_data_yuplon(df):
    # Clean the Price and Discount columns
    df['Price'] = df['Price'].str.replace('₡', '').str.replace(' ', '').str.split(',', expand=True)[
        0]
    df['Price'] = df['Price'].astype(float)
    df['Original Price'] = \
    df['Original Price'].str.replace('₡', '').str.replace(' ', '').str.split(',', expand=True)[0]
    df['Original Price'] = df['Original Price'].astype(float)
    df['Discount'] = df['Discount'].replace('%', '', regex=True).astype(float)
    df['Vendidas'] = df['Vendidas'].replace('[,]', '', regex=True).astype(int)
    return df


def plot_most_discount_offers(df):
    # Offers with most discount
    most_discount_offers = df.sort_values(by='Discount', ascending=False).head(10)
    plt.figure(figsize=(14, 10))
    plt.barh(most_discount_offers['Main Offer'], most_discount_offers['Discount'], color='skyblue')
    plt.xlabel('Porcentaje de Descuento')
    plt.title('Top 10 Ofertas con Mayor Descuento')
    plt.tight_layout(pad=3)
    plt.savefig('top_10_ofertas_mayor_descuento.png')


def plot_relation_price_vendidas_discount(df):
    # Relation between Vendidas, Price, and Discount
    plt.figure(figsize=(14, 10))
    plt.scatter(df['Price'], df['Vendidas'], c=df['Discount'], cmap='viridis', alpha=0.6)
    plt.colorbar(label='Porcentaje de Descuento')
    plt.xlabel('Precio')
    plt.ylabel('Vendidas')
    plt.title('Relación entre Vendidas, Precio y Descuento')
    plt.tight_layout(pad=3)
    plt.savefig('relacion_vendidas_precio_descuento.png')


def plot_least_discount_offers(df):
    # Offers with least discount
    worse_discount_offers = df.sort_values(by='Discount', ascending=True).head(10)
    plt.figure(figsize=(14, 10))
    plt.barh(worse_discount_offers['Main Offer'], worse_discount_offers['Discount'], color='salmon')
    plt.xlabel('Porcentaje de Descuento')
    plt.title('Top 10 Ofertas con Menor Descuento')
    plt.tight_layout(pad=3)
    plt.savefig('top_10_ofertas_menor_descuento.png')


def plot_most_expensive_offers(df):
    # Aggregate by Main Offer to ensure uniqueness and sum the prices if there are multiple entries
    most_expensive_offers = df.groupby('Main Offer').agg({'Price': 'sum'}).sort_values(by='Price',
                                                                                       ascending=False).head(
        10).reset_index()

    plt.figure(figsize=(14, 10))
    bars = plt.barh(most_expensive_offers['Main Offer'], most_expensive_offers['Price'],
                    color='orange')
    plt.xlabel('Precio')
    plt.title('Top 10 Ofertas Más Caras')
    plt.xticks(rotation=45)
    plt.tight_layout(pad=5)

    # Format price labels with additional margin to the left
    for bar in bars:
        plt.annotate(f"₡{int(bar.get_width()):,}",
                     xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                     xytext=(10, 0), textcoords="offset points",
                     ha='left', va='center')

    plt.subplots_adjust(left=0.35)  # Adjust left margin
    plt.savefig('top_10_ofertas_mas_caras.png')


def plot_least_expensive_offers(df):
    # Aggregate by Main Offer to ensure uniqueness and sum the prices if there are multiple entries
    least_expensive_offers = df.groupby('Main Offer').agg({'Price': 'sum'}).sort_values(by='Price',
                                                                                        ascending=True).head(
        10).reset_index()

    plt.figure(figsize=(14, 10))
    bars = plt.barh(least_expensive_offers['Main Offer'], least_expensive_offers['Price'],
                    color='lightgreen')
    plt.xlabel('Precio')
    plt.title('Top 10 Ofertas Más Baratas')
    plt.xticks(rotation=45)
    plt.tight_layout(pad=5)

    # Format price labels with additional margin to the left
    for bar in bars:
        plt.annotate(f"₡{int(bar.get_width()):,}",
                     xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                     xytext=(10, 0), textcoords="offset points",
                     ha='left', va='center')

    plt.subplots_adjust(left=0.35)  # Adjust left margin
    plt.savefig('top_10_ofertas_mas_baratas.png')


