import pandas as pd
import matplotlib.pyplot as plt

def realizar_analisis():
    try:
        # Leer el CSV
        df = pd.read_csv('data.csv')
        
        print("--- Análisis de Datos ---")
        print("\nPrimeras filas del dataset:")
        print(df.head())
        
        # Calcular estadísticas
        print("\nEstadísticas descriptivas:")
        stats = df.describe().loc[['mean', '50%', 'std']]
        stats.index = ['Media', 'Mediana', 'Desv. Estándar']
        print(stats)
        
        # Generar gráfica de dispersión
        plt.figure(figsize=(10, 6))
        plt.scatter(df['col1'], df['col2'], color='blue', alpha=0.7)
        plt.title('Gráfica de Dispersión: col1 vs col2')
        plt.xlabel('Columna 1')
        plt.ylabel('Columna 2')
        plt.grid(True, linestyle='--', alpha=0.6)
        
        print("\nGenerando gráfica...")
        plt.savefig('grafica_dispersion.png')
        print("Gráfica guardada como 'grafica_dispersion.png'")
        
        # Mostrar la gráfica
        plt.show()

    except FileNotFoundError:
        print("Error: No se encontró el archivo 'data.csv'")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    realizar_analisis()
