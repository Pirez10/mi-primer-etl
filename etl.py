import pandas as pd
import glob
import os

# Verificar que existen los archivos CSV descargados
archivos = glob.glob('data/ecommerce_*.csv')
if not archivos:
    print("❌ No se encontraron los archivos. Asegurate de descargarlos en la carpeta data/")
    print("   Deberías tener: ecommerce_orders.csv, ecommerce_customers.csv, etc.")
else:
    print(f"📂 Archivos encontrados: {len(archivos)}")
    for f in sorted(archivos):
        print(f"  - {os.path.basename(f)}")

# Cargar los CSVs principales
df_orders = pd.read_csv('data/ecommerce_orders.csv')
df_order_items = pd.read_csv('data/ecommerce_order_items.csv')
df_customers = pd.read_csv('data/ecommerce_customers.csv')
df_products = pd.read_csv('data/ecommerce_products.csv')

# Explorar
print(f"\n📈 Resumen:")
print(f"Orders: {len(df_orders)} filas, {len(df_orders.columns)} columnas")
print(f"Order Items: {len(df_order_items)} filas")
print(f"Customers: {len(df_customers)} filas")
print(f"Products: {len(df_products)} filas")

print("\n🔍 Primeras filas de orders:")
print(df_orders.head())
print("\n📋 Info de orders:")
print(df_orders.info())


# Ver nulos por columna
print("Nulos por columna:")
print(df_orders.isnull().sum())

# Decisión: ¿eliminar o rellenar?
# Si son pocos (<5%), podemos eliminar
# Si son muchos, mejor rellenar con un valor por defecto

# Ejemplo: eliminar filas con nulos en campos críticos
df_orders_clean = df_orders.dropna(subset=['customer_id']) #, 'promotion_id']) 

# Ejemplo: rellenar con 0 en campos numéricos opcionales
df_orders_clean['promotion_id'] = df_orders_clean['promotion_id'].fillna(0)
# df_orders_clean['notes'] = df_orders_clean['notes'].fillna(0)
df_orders_clean['notes'] = df_orders_clean['notes'].fillna('')

print(f"Filas antes: {len(df_orders)}, después: {len(df_orders_clean)}")



# Ver duplicados
duplicados = df_orders_clean.duplicated().sum()
print(f"Duplicados encontrados: {duplicados}")

# Ver duplicados por columna específica (ej: order_id debería ser único)
duplicados_id = df_orders_clean.duplicated(subset=['order_id']).sum()
print(f"Order IDs duplicados: {duplicados_id}")

# Eliminar duplicados
df_orders_clean = df_orders_clean.drop_duplicates()

# Si hay IDs duplicados, quedarse con el más reciente
df_orders_clean = df_orders_clean.sort_values('order_date').drop_duplicates(
    subset=['order_id'], 
    keep='last'
)


# Ver tipos actuales
print(df_orders_clean.dtypes)

# Convertir fechas
df_orders_clean['order_date'] = pd.to_datetime(df_orders_clean['order_date'])

# Asegurar que los números sean numéricos
df_orders_clean['subtotal'] = pd.to_numeric(df_orders_clean['subtotal'], errors='coerce')
df_orders_clean['total_amount'] = pd.to_numeric(df_orders_clean['total_amount'], errors='coerce')

# Verificar
print("\nTipos después de conversión:")
print(df_orders_clean.dtypes)





# -----------------------------
# Métricas de ventas
# -----------------------------

# Ventas por cliente
ventas_cliente = df_orders_clean.groupby('customer_id')['total_amount'].sum().reset_index()

# Ventas por mes
df_orders_clean['month'] = df_orders_clean['order_date'].dt.to_period('M')
ventas_mes = df_orders_clean.groupby('month')['total_amount'].sum().reset_index()

print("📊 Métricas creadas")
print(ventas_cliente.head())
print(ventas_mes.head())






# Crear carpeta output si no existe
import os
os.makedirs('output', exist_ok=True)

# Guardar métricas en CSV
ventas_cliente.to_csv('output/ventas_por_cliente.csv', index=False)
ventas_mes.to_csv('output/ventas_por_mes.csv', index=False)

# Guardar datos limpios
df_orders_clean.to_csv('output/orders_clean.csv', index=False)

print("✅ Archivos CSV guardados en output/")




# Instalar pyarrow si no lo tenés: pip install pyarrow

# Guardar en Parquet
df_orders_clean.to_parquet('output/orders_clean.parquet', index=False)

# Comparar tamaños
csv_size = os.path.getsize('output/orders_clean.csv') / 1024
parquet_size = os.path.getsize('output/orders_clean.parquet') / 1024

print(f"Tamaño CSV: {csv_size:.1f} KB")
print(f"Tamaño Parquet: {parquet_size:.1f} KB")
print(f"Parquet es {csv_size/parquet_size:.1f}x más chico")






# Crear README.md

readme_content = """
# Mi Primer ETL con Python

## Descripción
Pipeline ETL que procesa datos de e-commerce para generar métricas de ventas.

## Cómo correr
```bash
pip install pandas pyarrow
python etl.py
```

## Decisiones de limpieza
- **Nulos**: Eliminé filas sin customer_id, product_id o total (campos críticos)
- **Duplicados**: Eliminé duplicados por order_id, quedándome con el más reciente
- **Tipos**: Convertí order_date a datetime, total y quantity a numérico

## Output
- `ventas_por_cliente.csv`: Total gastado y cantidad de órdenes por cliente
- `ventas_por_mes.csv`: Ventas totales por mes
- `orders_clean.parquet`: Dataset limpio en formato optimizado

## Autor
[Franco Pirez] - [Martes 17/03/2026]
"""

with open('README.md', 'w') as f:
    f.write(readme_content)

print("✅ README.md creado")