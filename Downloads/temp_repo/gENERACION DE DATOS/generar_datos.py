"""
Script para generar datos sintéticos de ventas
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configurar semilla para reproducibilidad
np.random.seed(42)

# Definir productos
productos = ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Auriculares', 'Webcam', 'Tablet', 'Smartphone']

# Definir precios base por producto
precios_base = {
    'Laptop': 800.0,
    'Mouse': 25.0,
    'Teclado': 60.0,
    'Monitor': 200.0,
    'Auriculares': 80.0,
    'Webcam': 50.0,
    'Tablet': 300.0,
    'Smartphone': 500.0
}

# Generar datos para 6 meses (enero a junio 2025)
fecha_inicio = datetime(2025, 1, 1)
fecha_fin = datetime(2025, 6, 30)

datos = []

fecha_actual = fecha_inicio
while fecha_actual <= fecha_fin:
    # Generar entre 5 y 15 ventas por día
    num_ventas = np.random.randint(5, 16)
    
    for _ in range(num_ventas):
        producto = np.random.choice(productos)
        cantidad = np.random.randint(1, 6)  # Entre 1 y 5 unidades
        precio_unitario = precios_base[producto] * np.random.uniform(0.9, 1.1)  # Variación de precio
        
        datos.append({
            'fecha': fecha_actual.date(),
            'producto': producto,
            'cantidad': cantidad,
            'precio': round(precio_unitario, 2)
        })
    
    fecha_actual += timedelta(days=1)

# Crear DataFrame
df = pd.DataFrame(datos)

# Guardar a CSV
df.to_csv('ventas.csv', index=False)
print(f"Datos generados exitosamente: {len(df)} registros")
print(f"Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
print(f"\nPrimeras filas:")
print(df.head(10))
