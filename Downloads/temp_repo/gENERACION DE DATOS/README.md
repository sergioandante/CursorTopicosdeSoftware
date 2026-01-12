# Generación de Datos - Análisis de Ventas Mensuales

Proyecto de análisis de datos de ventas utilizando Python, pandas y matplotlib para generar reportes y visualizaciones.

## Descripción

Este proyecto analiza datos de ventas desde un archivo CSV para obtener:
- **Ventas totales por mes**
- **Producto más vendido** (en cantidad) y **producto con mayores ingresos**
- **Visualizaciones**: gráfico de ventas por mes, gráfico de ventas por producto (top 5)

## Características

- Generación de datos sintéticos de ventas
- Análisis de ventas mensuales
- Identificación de productos destacados
- Generación de gráficos y visualizaciones
- Reportes en formato texto y gráficos PNG

## Requisitos

- Python 3.7 o superior
- pandas >= 1.3.0
- matplotlib >= 3.3.0
- numpy >= 1.20.0

## Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install pandas matplotlib numpy
```

## Uso

### 1. Generar datos sintéticos

Si no tienes un archivo `ventas.csv`, puedes generar datos de ejemplo:

```bash
python generar_datos.py
```

Esto creará un archivo `ventas.csv` con datos de ventas sintéticos para 6 meses (enero a junio 2025).

### 2. Ejecutar análisis

Ejecuta el script principal de análisis:

```bash
python analisis.py
```

El script generará:
- **Reporte en consola** con estadísticas y resúmenes
- **ventas_por_mes.png** - Gráfico de barras con ventas mensuales
- **top5_productos.png** - Gráfico horizontal con los 5 productos con mayores ingresos
- **comparacion_productos.png** - Comparación entre productos más vendidos por cantidad vs ingresos

## Estructura del Proyecto

```
gENERACION DE DATOS/
├── generar_datos.py           # Script para generar datos sintéticos
├── analisis.py                # Script principal de análisis
├── ventas.csv                 # Datos de ventas (generado o proporcionado)
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Este archivo
├── ventas_por_mes.png         # Gráfico generado: ventas por mes
├── top5_productos.png         # Gráfico generado: top 5 productos
└── comparacion_productos.png  # Gráfico generado: comparación productos
```

## Formato de Datos CSV

El archivo `ventas.csv` debe tener las siguientes columnas:

- `fecha`: Fecha de la venta (formato YYYY-MM-DD)
- `producto`: Nombre del producto
- `cantidad`: Cantidad vendida (número entero)
- `precio`: Precio unitario (número decimal)

Ejemplo:
```csv
fecha,producto,cantidad,precio
2025-01-05,Laptop,3,800.0
2025-01-20,Smartphone,1,500.0
2025-02-13,Mouse,5,25.0
```

## Resultados del Análisis

El script de análisis proporciona:

1. **Ventas totales por mes**: Suma de todos los ingresos (cantidad × precio) agrupados por mes
2. **Producto más vendido**: Producto con mayor cantidad total de unidades vendidas
3. **Producto con mayores ingresos**: Producto que genera más ingresos totales (puede diferir del más vendido)
4. **Visualizaciones**: Gráficos que facilitan la interpretación de los datos

## Ejemplo de Salida

```
============================================================
ANÁLISIS DE VENTAS MENSUALES
============================================================

1. Cargando datos...
Registros cargados: 1721
Rango de fechas: 2025-01-01 a 2025-06-30

2. Calculando ventas totales por mes...
Ventas por mes:
         Ventas (€)
mes                
2025-01   224690.60
2025-02   209718.40
...

3. Análisis por producto...
Producto más vendido (en unidades): Smartphone
  Total vendido: 700 unidades

Producto con mayores ingresos: Laptop
  Total ingresos: 510,894.16 €
```

## Extensión del Proyecto

Posibles mejoras futuras:
- Generación de informe en formato HTML/PDF
- Análisis de tendencias y pronósticos
- Integración con bases de datos
- Dashboard interactivo
- Análisis de estacionalidad

## Autor

Proyecto desarrollado como parte de ejercicios de análisis de datos.
