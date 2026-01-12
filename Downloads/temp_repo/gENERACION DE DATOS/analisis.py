"""
Análisis de Ventas Mensuales
Script para analizar datos de ventas desde un archivo CSV
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para evitar problemas con backends gráficos

# Configuración de estilo para las gráficas
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        pass  # Usar estilo por defecto

# 1. Cargar datos del CSV
print("=" * 60)
print("ANÁLISIS DE VENTAS MENSUALES")
print("=" * 60)
print("\n1. Cargando datos...")
df = pd.read_csv('ventas.csv', parse_dates=['fecha'])

# Verificar tipos de datos
print(f"Registros cargados: {len(df)}")
print(f"Rango de fechas: {df['fecha'].min().date()} a {df['fecha'].max().date()}")
print(f"\nTipos de datos:")
print(df.dtypes)

# 2. Calcular ventas totales por mes
print("\n" + "=" * 60)
print("2. Calculando ventas totales por mes...")
print("=" * 60)

# Crear columna de mes
df['mes'] = df['fecha'].dt.to_period('M')

# Calcular ingresos (cantidad * precio)
df['ingreso'] = df['cantidad'] * df['precio']

# Agrupar por mes y sumar ingresos
ventas_por_mes = df.groupby('mes')['ingreso'].sum()
ventas_por_mes = ventas_por_mes.sort_index()

print("\nVentas por mes:")
print(ventas_por_mes.to_frame('Ventas (€)'))
print(f"\nTotal de ventas: {ventas_por_mes.sum():,.2f} €")
print(f"Promedio mensual: {ventas_por_mes.mean():,.2f} €")

# 3. Determinar producto más vendido y con mayor ingresos
print("\n" + "=" * 60)
print("3. Análisis por producto...")
print("=" * 60)

# Agrupar por producto
ventas_prod = df.groupby('producto').agg({
    'cantidad': 'sum',
    'ingreso': 'sum'
}).sort_values('ingreso', ascending=False)

print("\nResumen por producto:")
print(ventas_prod)

# Producto más vendido en cantidad
mas_vendido_cantidad = ventas_prod['cantidad'].idxmax()
total_cantidad = ventas_prod.loc[mas_vendido_cantidad, 'cantidad']

# Producto con mayores ingresos
mayor_ingreso = ventas_prod['ingreso'].idxmax()
total_ingreso = ventas_prod.loc[mayor_ingreso, 'ingreso']

print(f"\n{'='*60}")
print(f"Producto más vendido (en unidades): {mas_vendido_cantidad}")
print(f"  Total vendido: {int(total_cantidad)} unidades")
print(f"\nProducto con mayores ingresos: {mayor_ingreso}")
print(f"  Total ingresos: {total_ingreso:,.2f} €")
print(f"{'='*60}")

# 4. Graficar ventas por mes
print("\n4. Generando gráfico de ventas por mes...")
fig, ax = plt.subplots(figsize=(10, 6))

# Convertir índice Period a string para mejor visualización
meses_str = ventas_por_mes.index.astype(str)

ax.bar(meses_str, ventas_por_mes.values, color='steelblue', edgecolor='black', linewidth=1.2)
ax.set_title("Ventas por Mes", fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("Mes", fontsize=12)
ax.set_ylabel("Ventas (€)", fontsize=12)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Agregar valores en las barras
for i, v in enumerate(ventas_por_mes.values):
    ax.text(i, v, f'{v:,.0f} €', ha='center', va='bottom', fontsize=9)

plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("ventas_por_mes.png", dpi=300, bbox_inches='tight')
print("  [OK] Grafico guardado: ventas_por_mes.png")
plt.close()

# 5. Graficar top 5 productos por ingresos
print("\n5. Generando gráfico de top 5 productos por ingresos...")
top5 = ventas_prod.nlargest(5, 'ingreso')

fig, ax = plt.subplots(figsize=(10, 6))

colors = plt.cm.viridis(range(len(top5)))
bars = ax.barh(top5.index, top5['ingreso'], color=colors, edgecolor='black', linewidth=1.2)
ax.set_title("Top 5 Productos por Ingresos", fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("Ingresos (€)", fontsize=12)
ax.set_ylabel("Producto", fontsize=12)
ax.grid(axis='x', alpha=0.3, linestyle='--')

# Agregar valores en las barras
for i, (idx, row) in enumerate(top5.iterrows()):
    ax.text(row['ingreso'], i, f'{row["ingreso"]:,.0f} €', 
            va='center', ha='left', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig("top5_productos.png", dpi=300, bbox_inches='tight')
print("  [OK] Grafico guardado: top5_productos.png")
plt.close()

# Gráfico adicional: Comparación cantidad vs ingresos (top 5)
print("\n6. Generando gráfico comparativo (cantidad vs ingresos)...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Top 5 por cantidad
top5_cantidad = ventas_prod.nlargest(5, 'cantidad')
ax1.barh(top5_cantidad.index, top5_cantidad['cantidad'], color='coral', edgecolor='black')
ax1.set_title("Top 5 Productos por Cantidad Vendida", fontsize=14, fontweight='bold')
ax1.set_xlabel("Cantidad (unidades)", fontsize=11)
ax1.grid(axis='x', alpha=0.3)

# Top 5 por ingresos (reutilizar variable top5)
ax2.barh(top5.index, top5['ingreso'], color='steelblue', edgecolor='black')
ax2.set_title("Top 5 Productos por Ingresos", fontsize=14, fontweight='bold')
ax2.set_xlabel("Ingresos (€)", fontsize=11)
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig("comparacion_productos.png", dpi=300, bbox_inches='tight')
print("  [OK] Grafico guardado: comparacion_productos.png")
plt.close()

print("\n" + "=" * 60)
print("ANÁLISIS COMPLETADO")
print("=" * 60)
print("\nGráficos generados:")
print("  - ventas_por_mes.png")
print("  - top5_productos.png")
print("  - comparacion_productos.png")
