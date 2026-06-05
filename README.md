
# 🛒 ETL de E-commerce con Python

## 📌 Descripción

Este proyecto implementa un pipeline ETL (Extract, Transform, Load) sobre un dataset de e-commerce compuesto por 11 tablas relacionadas (orders, customers, products, order_items, entre otras).

El objetivo es simular un escenario real de ingeniería de datos donde se:

* Ingestan múltiples fuentes de datos
* Limpian y validan los datos
* Integran diferentes tablas
* Generan métricas de negocio relevantes

---

## ⚙️ Tecnologías utilizadas

* Python
* Pandas
* PyArrow (para formato Parquet)

---

## ▶️ Cómo ejecutar el proyecto

1. Clonar el repositorio:

```bash
git clone <tu-repo>
cd mi-primer-etl
```

2. Instalar dependencias:

```bash
pip install pandas pyarrow
```

3. Ejecutar el pipeline:

```bash
python etl.py
```

---

## 🔄 Estructura del pipeline

El flujo sigue una arquitectura ETL clásica:

### 1. Extract

* Carga automática de archivos CSV usando `glob`
* Permite escalar fácilmente si se agregan nuevas tablas

### 2. Transform

Incluye:

* Exploración de datos (`df.info()`, nulos)
* Limpieza:

  * Eliminación de nulos en campos críticos (`customer_id`)
  * Relleno de campos opcionales (`promotion_id`, `notes`)
* Eliminación de duplicados:

  * Validación global y por clave de negocio (`order_id`)
* Corrección de tipos:

  * Fechas → datetime
  * Montos → numéricos
* Integración de datos:

  * Joins entre `orders`, `order_items`, `products` y `customers`

### 3. Load

* Persistencia de datos en:

  * **Parquet** (dataset limpio)
  * **CSV** (métricas de negocio)

---

## 📊 Métricas generadas

El pipeline responde a preguntas reales de negocio:

### 🏆 Top 5 clientes

Clientes con mayor gasto total y cantidad de órdenes.

### 📦 Producto más vendido

Productos con mayor cantidad de unidades vendidas.

### 📈 Ventas mensuales

Evolución de ingresos y cantidad de órdenes a lo largo del tiempo.

---

## 💾 Formatos de salida

### Parquet

* `orders_clean.parquet`
* Uso: análisis y procesamiento eficiente
* Ventaja: formato columnar y comprimido (más rápido y liviano)

### CSV

* `top_clientes.csv`
* `top_productos.csv`
* `ventas_mensuales.csv`
* Uso: consumo por usuarios no técnicos (Excel, BI tools)

---

## 🧠 Decisiones técnicas

### Manejo de nulos

* Se eliminaron registros sin `customer_id` por ser un campo crítico
* Se rellenaron valores opcionales (`promotion_id`, `notes`) para mantener consistencia

### Duplicados

* Se validaron duplicados a nivel fila y por `order_id`
* En caso de duplicados, se conserva el registro más reciente

### Tipos de datos

* Conversión explícita para evitar errores de inferencia de Pandas

### Integración de datos

* Uso de joins para construir un dataset analítico unificado

### Formatos de almacenamiento

* Parquet para eficiencia en procesamiento
* CSV para accesibilidad

---

## 🚀 Posibles mejoras

* Implementar logging en lugar de prints
* Agregar validaciones de calidad de datos (data quality checks)
* Modularizar el pipeline en múltiples archivos
* Orquestación con herramientas como Airflow
* Versionado de datos

---

## 👤 Autor

Franco Pirez
Proyecto de portfolio – Ingeniería de Datos
