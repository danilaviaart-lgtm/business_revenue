# Business Revenue - Purchase Intention Prediction API

## Descripción del proyecto

Este proyecto desarrolla un sistema de Machine Learning capaz de predecir la intención de compra de usuarios en un ecommerce a partir de su comportamiento de navegación.

El objetivo principal es ayudar a las empresas a identificar usuarios con alta probabilidad de conversión y facilitar acciones como:

- personalización de contenido
- optimización de campañas de marketing
- retargeting inteligente
- priorización de usuarios con intención de compra
- mejora de estrategias comerciales

La variable objetivo del modelo es:

```text
Revenue
```

donde:

- `0` → el usuario no realiza una compra
- `1` → el usuario realiza una compra

---

# Integrantes del equipo

- Nombre Apellido
- Nombre Apellido
- Nombre Apellido

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

Utilizado para validar los datos de entrada antes de realizar las predicciones.

---

# Endpoints

## Documentación automática

### Endpoint

```text
GET /docs
```

### URL

```text
http://127.0.0.1:8000/docs
```

---

# OpenAPI Schema

### Endpoint

```text
GET /openapi.json
```

---

# Health Check

Endpoint para comprobar que la API funciona correctamente.

### Endpoint

```text

http://127.0.0.1:8000/helth

```

### Ejemplo de respuesta

```json
{
  "status": "ok"
}
```

---

# Obtener últimos datos

Endpoint utilizado para consultar los últimos registros del dataset.

### Endpoint

```text
GET /datos/ultimos
```

### Ejemplo de respuesta

```json
[
  {
    "Customer_ID": 1001,
    "Customer_Name": "Laura Garcia",
    "Revenue": 1
  }
]
```

---

# Predicción de intención de compra

Endpoint principal para realizar predicciones.

### Endpoint

```text
POST /predict
```

---

# Ejemplo de petición

```json
{
  "Administrative": 0,
  "Administrative_Duration": 0,
  "Informational": 0,
  "Informational_Duration": 0,
  "ProductRelated": 20,
  "ProductRelated_Duration": 300,
  "BounceRates": 0.01,
  "ExitRates": 0.03,
  "PageValues": 25,
  "SpecialDay": 0,
  "Month": "May",
  "OperatingSystems": 2,
  "Browser": 1,
  "Region": 1,
  "TrafficType": 2,
  "VisitorType": "Returning_Visitor",
  "Weekend": false
}
```

---

# Ejemplo de respuesta

```json
{
  "prediction": 1,
  "purchase_probability": 0.84
}
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

# Acceder a la documentación de FastAPI

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