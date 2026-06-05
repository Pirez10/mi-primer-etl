# =========================================
# 📦 IMPORTS
# =========================================

# pandas: librería principal para manipulación de datos tabulares (DataFrames)
# La usamos para leer CSV, limpiar datos, hacer joins y agregaciones
import pandas as pd  

# glob: permite buscar archivos usando patrones (ej: ecommerce_*.csv)
# Lo usamos para cargar automáticamente todas las tablas del dataset
import glob  

# os: manejo del sistema de archivos (crear carpetas, rutas, tamaños de archivos)
# Lo usamos para crear la carpeta output y comparar tamaños CSV vs Parquet
import os  


# =========================================
# 📥 EXTRACT
# =========================================

def extract():
    """
    Extrae todos los archivos CSV del dataset.

    Estrategia:
    - Usamos glob para evitar hardcodear nombres de archivos
    - Esto permite escalar si se agregan nuevas tablas
    """

    archivos = glob.glob('data/ecommerce_*.csv')

    if not archivos:
        print("❌ No se encontraron archivos en /data")
        return {}

    print(f"📂 Archivos encontrados: {len(archivos)}")

    data = {}

    for file in archivos:
        # Convertimos el nombre del archivo en nombre de tabla
        # ecommerce_orders.csv → orders
# os.path.basename funciona tanto en Windows como Linux/Mac
        nombre_tabla = os.path.basename(file) \
                    .replace('ecommerce_', '') \
                    .replace('.csv', '')

        # Leemos el CSV en un DataFrame
        data[nombre_tabla] = pd.read_csv(file)

        print(f"✔ Cargado: {nombre_tabla}")

    return data

# =========================================
# 🔄 TRANSFORM
# =========================================

def transform(data):
    """
    Limpia, transforma y genera métricas.

    Incluye:
    - Exploración inicial
    - Manejo de nulos
    - Eliminación de duplicados
    - Corrección de tipos
    - Joins entre tablas
    - Métricas de negocio
    """

    # Seleccionamos tablas principales
    df_orders = data['orders']
    df_order_items = data['order_items']
    df_customers = data['customers']
    df_products = data['products']

    # ---------------------------------
    # 🔍 EXPLORACIÓN
    # ---------------------------------

    # info(): muestra tipos de datos y nulos
    print("\n📋 Info de orders:")
    print(df_orders.info())

    # isnull().sum(): cuenta nulos por columna
    print("\n🔍 Nulos por columna:")
    print(df_orders.isnull().sum())


    # ---------------------------------
    # 🧹 LIMPIEZA
    # ---------------------------------

    # 📌 NULOS
    # customer_id es crítico → no podemos analizar ventas sin cliente
    df_orders = df_orders.dropna(subset=['customer_id'])

    # promotion_id es opcional → rellenamos con 0 (sin promoción)
    df_orders['promotion_id'] = df_orders['promotion_id'].fillna(0)

    # notes es texto → evitamos NaN para no romper joins/exportaciones
    df_orders['notes'] = df_orders['notes'].fillna('')


    # 📌 DUPLICADOS

    # Detectamos duplicados completos
    duplicados = df_orders.duplicated().sum()
    print(f"\nDuplicados encontrados: {duplicados}")

    # Detectamos duplicados por clave de negocio
    duplicados_id = df_orders.duplicated(subset=['order_id']).sum()
    print(f"Order_id duplicados: {duplicados_id}")

    # Estrategia:
    # - Ordenamos por fecha
    # - Nos quedamos con el registro más reciente
    df_orders = df_orders.sort_values('order_date') \
                         .drop_duplicates(subset=['order_id'], keep='last')


    # 📌 TIPOS DE DATOS

    # Convertimos fechas (muchas veces vienen como string en CSV)
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])

    # Convertimos montos a numérico
    df_orders['total_amount'] = pd.to_numeric(df_orders['total_amount'], errors='coerce')


    # ---------------------------------
    # 🔗 JOINS (INTEGRACIÓN DE DATOS)
    # ---------------------------------

    """
    Unimos tablas para tener un dataset analítico completo.

    order_items = detalle de productos por orden
    orders = información general de la orden
    products = info del producto
    customers = info del cliente
    """

    df = df_order_items.merge(df_orders, on='order_id', how='left') \
                       .merge(df_products, on='product_id', how='left') \
                       .merge(df_customers, on='customer_id', how='left')


    # ---------------------------------
    # 📊 MÉTRICAS DE NEGOCIO
    # ---------------------------------
    # Guardamos métricas en CSV (uso negocio / Excel)
    # 🎯 1. Top 5 clientes que más gastaron
    top_clientes = df.groupby('customer_id').agg(
        total_gastado=('total_amount', 'sum'),
        total_ordenes=('order_id', 'nunique')
    ).reset_index().sort_values('total_gastado', ascending=False).head(5)


    # 🎯 2. Producto más vendido (por cantidad)
    top_productos = df.groupby('product_id').agg(
        unidades_vendidas=('quantity', 'sum')
    ).reset_index().sort_values('unidades_vendidas', ascending=False)


    # 🎯 3. Evolución de ventas mes a mes

    # Creamos columna mes a partir de la fecha
    df['month'] = df['order_date'].dt.to_period('M')

    ventas_mes = df.groupby('month').agg(
        ventas_totales=('total_amount', 'sum'),
        ordenes=('order_id', 'nunique')
    ).reset_index().sort_values('month')


    # ✅ MOSTRAR RESULTADOS (VALIDACIÓN)
    print("\n🏆 Top 5 clientes:")
    print(top_clientes)

    print("\n📦 Top productos:")
    print(top_productos.head())

    print("\n📈 Ventas mensuales:")
    print(ventas_mes.head())

    print("\n📊 Métricas generadas correctamente")

    return df_orders, top_clientes, top_productos, ventas_mes


# =========================================
# 📤 LOAD
# =========================================

def load(df_orders, top_clientes, top_productos, ventas_mes):
    """
    Guarda los resultados del pipeline.

    - CSV: formato universal (Excel-friendly)
    - Parquet: optimizado para análisis (más liviano y rápido)
    """

    # Creamos carpeta output si no existe
    os.makedirs('output', exist_ok=True)

    # Guardamos dataset limpio en formato eficiente (uso analítico)
    df_orders.to_parquet('output/orders_clean.parquet', index=False)

    # Guardamos métricas en CSV (para usuarios no técnicos)
    top_clientes.to_csv('output/top_clientes.csv', index=False)
    top_productos.to_csv('output/top_productos.csv', index=False)
    ventas_mes.to_csv('output/ventas_mensuales.csv', index=False)

    print("✅ Datos guardados en /output")


# =========================================
# ▶ MAIN
# =========================================

def main():
    """
    Orquesta el pipeline completo ETL
    """

    data = extract()
    df_orders, top_clientes, top_productos, ventas_mes = transform(data)
    load(df_orders, top_clientes, top_productos, ventas_mes)


# Punto de entrada del script
if __name__ == "__main__":
    main()