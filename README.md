# Business Revenue - Purchase Intention Prediction API

## Descripción del proyecto

Este proyecto desarrolla un sistema de Machine Learning capaz de predecir la intención de compra de usuarios en un ecommerce a partir de su comportamiento de navegación.

El objetivo principal es ayudar a las empresas a identificar usuarios con alta probabilidad de conversión y facilitar acciones como:

- personalización de contenido
- optimización de campañas de marketing
- retargeting inteligente
- segmentación de clientes
- automatización de acciones comerciales
- envío de emails o push notifications

La variable objetivo del modelo es:

```text
Revenue
```

donde:

- `0` → el usuario no realiza una compra
- `1` → el usuario realiza una compra

---

# Integrantes del equipo

- Dani Lavia Gaya
- Esther Barranco Motos

---

# Repositorio

Repositorio del proyecto:

```text
https://github.com/danilaviaart-lgtm/business_revenue
```

---

# Dataset utilizado

Se utiliza el dataset:

```text
Online Shoppers Purchasing Intention Dataset
```

procedente de:

```text
UCI Machine Learning Repository
```

URL : https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset

El dataset contiene información sobre sesiones de navegación en ecommerce, incluyendo:

- páginas visitadas
- duración de la sesión
- páginas de producto
- tasas de rebote
- tasas de salida
- tipo de visitante
- mes de navegación
- navegación en fin de semana
- intención final de compra

---

# Proceso de Machine Learning

## 1. Limpieza de datos

Se realizó una revisión inicial del dataset para validar la calidad de los datos:

- comprobación de valores nulos
- detección y eliminación de duplicados
- revisión de tipos de variables
- análisis del balanceo de clases

La variable objetivo `Revenue` fue convertida a formato binario.

---

## 2. Preprocesamiento

Las variables categóricas fueron transformadas mediante:

```text
OneHotEncoder
```

Variables categóricas utilizadas:

- `Month`
- `VisitorType`
- `Weekend`

Además, se aplicó:

```text
SMOTE
```

para balancear la clase minoritaria, ya que el dataset presentaba más sesiones sin compra que con compra.

---

# Modelos entrenados

Se compararon dos modelos de Machine Learning:

## Logistic Regression

Modelo lineal utilizado como baseline inicial.

---

## Random Forest Classifier

Modelo ensemble basado en múltiples árboles de decisión.

Este modelo fue seleccionado como modelo final debido a su mejor rendimiento general.

---

# Comparación de modelos

Las métricas utilizadas para comparar los modelos fueron:

- ROC-AUC
- Precision
- Recall

Resultados obtenidos:

| Modelo | ROC-AUC | Precision | Recall |
|---|---|---|---|
| Logistic Regression | 0.91 | 0.51 | 0.80 |
| Random Forest | 0.93 | 0.65 | 0.74 |

---

# Modelo final

El modelo seleccionado fue:

```text
Random Forest Classifier
```

debido a:

- mejor rendimiento general
- mayor capacidad predictiva
- mejor precision
- comportamiento más robusto

El pipeline final incluye:

- OneHotEncoder
- SMOTE
- Random Forest Classifier

---

# Guardado del modelo

El modelo entrenado se guarda en:

```text
models/purchase_prediction_model.pkl
```

---

# API

La API fue desarrollada utilizando:

- FastAPI
- Pydantic
- Uvicorn

---

## FastAPI

Framework utilizado para crear la API REST.

Permite crear endpoints rápidos, eficientes y documentados automáticamente.

---

## Pydantic

Utilizado para validar automáticamente los datos de entrada antes de realizar las predicciones.

---

# Endpoints de la API

Una vez ejecutada la API en local, se puede acceder desde el navegador a:

```text
http://127.0.0.1:8000/
```

La API genera automáticamente una documentación interactiva donde se pueden visualizar y probar todos los endpoints disponibles.

---

# Documentación interactiva

## Swagger UI

Permite probar todos los endpoints directamente desde el navegador.

### URL

```text
http://127.0.0.1:8000/docs
```

---

# OpenAPI Schema

Documentación técnica generada automáticamente por FastAPI.

### URL

```text
http://127.0.0.1:8000/openapi.json
```

---

# Endpoint `/`

## Método

```text
GET /
```

## Descripción

Ruta principal de la API.

Sirve para comprobar que el servicio está funcionando correctamente y mostrar información básica sobre la aplicación.

### Ejemplo de respuesta

```json
{
  "status": "API en ejecución. Prueba",
  "documentacion": "/docs",
  "mensaje": "Visita /docs para probar el endpoint de predicción."
}
```

---

# Endpoint `/health`

## Método

```text
GET /health
```

## Descripción

Endpoint de comprobación del estado del servicio.

Se utiliza para verificar que la API está activa y funcionando correctamente.

### Ejemplo de acceso

```text
http://127.0.0.1:8000/health
```

---

# Endpoint `/datos/revenue`

## Método

```text
GET /datos/revenue
```

## Descripción

Filtra el dataset según el valor de la columna `Revenue`.

Permite obtener únicamente los usuarios que han comprado (`true`) o los que no han comprado (`false`).

Este endpoint resulta útil para segmentación de clientes y acciones de marketing.

---

## Parámetro query

| Parámetro | Tipo | Descripción |
|---|---|---|
| `valor` | boolean | Valor de Revenue a filtrar (`true` o `false`) |

---

## Ejemplo de acceso

Usuarios que han comprado:

```text
http://127.0.0.1:8000/datos/revenue?valor=true
```

Usuarios que no han comprado:

```text
http://127.0.0.1:8000/datos/revenue?valor=false
```

---

# Endpoint `/datos/all`

## Método

```text
GET /datos/all
```

## Descripción

Devuelve todos los registros del archivo CSV cargado por la API.

Permite visualizar el dataset completo desde la API REST.

---

## Ejemplo de acceso

```text
http://127.0.0.1:8000/datos/all
```

---

# Endpoint `/datos/{id_cliente}`

## Método

```text
GET /datos/{id_cliente}
```

## Descripción

Endpoint con parámetro dinámico en el path.

Permite obtener la información de un cliente concreto utilizando su identificador (`id_cliente`).

---

## Parámetro path

| Parámetro | Tipo | Descripción |
|---|---|---|
| `id_cliente` | integer | ID del cliente que se desea consultar |

---

## Ejemplo de acceso

```text
http://127.0.0.1:8000/datos/1001
```

En este ejemplo:

```text
1001
```

corresponde al identificador del cliente.

---

# Endpoint `/datos/ultimos`

## Método

```text
GET /datos/ultimos
```

## Descripción

Devuelve las últimas filas del dataset cargado en la API.

Se utiliza para comprobar rápidamente los últimos registros disponibles sin necesidad de cargar el CSV completo.

---

## Ejemplo de acceso

```text
http://127.0.0.1:8000/datos/ultimos
```

---

# Validación automática

La API utiliza:

- FastAPI
- Pydantic

para validar automáticamente:

- tipos de datos
- parámetros obligatorios
- errores de entrada
- formatos incorrectos

Cuando un parámetro no es válido, FastAPI devuelve automáticamente un error:

```text
422 Validation Error
```

---

# Instalación y ejecución en local

## 1. Clonar repositorio

```bash
git clone https://github.com/danilaviaart-lgtm/business_revenue.git
```

---

## 2. Entrar en la carpeta del proyecto

```bash
cd business_revenue
```

---

## 3. Crear entorno virtual

```bash
python -m venv .venv
```

---

## 4. Activar entorno virtual

### Windows

```bash
.venv\Scripts\activate
```

### Mac/Linux

```bash
source .venv/bin/activate
```

---

## 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Ejecutar la API

Desde la carpeta inicial del repositorio ejecutar:

```bash
python -m uvicorn src.api.main:app --reload
```

---

# Ejecutar el cliente

Desde la carpeta inicial del repositorio ejecutar:

```bash
python src/client/client.py
```

---

# Acceder a la documentación interactiva

Abrir en el navegador:

```text
http://127.0.0.1:8000/docs
```

---

# URL del servicio desplegado

Pendiente de añadir:

```text
URL_DEPLOY
```

---

# Estructura del proyecto

```text
business_revenue/
│
├── data/
│   └── raw/
│       ├── data.csv
│       └── enriched_online_shoppers.csv
│
├── models/
│   └── purchase_prediction_model.pkl
│
├── notebooks/
│   └── purchase_prediction_model.ipynb
│
├── src/
│   ├── api/
│   │   └── main.py
│   │
│   └── client/
│       └── client.py
│
├── requirements.txt
├── README.md
└── pyproject.toml
```