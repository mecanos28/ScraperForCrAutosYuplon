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
    df.loc[:, 'Precio'] = df['Precio'].replace('[\$,]', '', regex=True).astype(float)
    # Convertir el año a entero
    df.loc[:, 'Año'] = df['Año'].astype(int)
    return df

def get_average_price_by_year(df):
    # Obtener el precio promedio por año
    return df.groupby('Año')['Precio'].mean()

def get_most_common_models(df, top_n=10):
    # Obtener los modelos de carros más comunes
    return df['Version'].value_counts().head(top_n)

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
    most_common_models.plot(kind='bar')

    # Ajustar los valores del eje y
    max_y = most_common_models.max() + 10  # Un poco más alto que el valor máximo para mejor visualización
    plt.ylim(0, max_y)

    # Título y etiquetas
    plt.title(f'Top {top_n} Modelos de carros Más Comunes')
    plt.xlabel('Modelo de Carro')
    plt.ylabel('Cantidad')

    # Rotar las etiquetas del eje x para mejor visualización
    plt.xticks(rotation=45)

    # Añadir cuadrícula para facilitar la lectura de valores
    plt.grid(True, axis='y')

    # Guardar la gráfica
    plt.savefig('modelos_mas_comunes.png')
