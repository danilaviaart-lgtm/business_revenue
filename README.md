# Business Revenue - Purchase Intention Prediction API

**Descripción del proyecto**

Este proyecto desarrolla una API REST con Machine Learning para predecir la intención de compra de usuarios en un ecommerce a partir de su comportamiento de navegación.

El objetivo es transformar datos de navegación en decisiones comerciales accionables. A partir de variables como páginas visitadas, duración de la sesión, tasas de rebote, tipo de visitante o mes de navegación, el sistema puede estimar si un usuario tiene probabilidad de realizar una compra.

La variable objetivo del modelo es:

```text
Revenue
```

Donde:

- `0` → el usuario no realiza una compra
- `1` → el usuario realiza una compra

---

*Integrantes del equipo*

- Dani Lavia Gaya
- Esther Barranco Motos

---

## 1. Objetivo business

El proyecto puede ayudar a un ecommerce a:

- identificar usuarios con mayor intención de compra
- segmentar clientes según comportamiento
- optimizar campañas de marketing
- activar emails o push notifications
- priorizar usuarios con alta probabilidad de conversión
- evitar acciones masivas poco eficientes

La idea principal es pasar de campañas genéricas a acciones más personalizadas basadas en datos.

---

### 1.1 Repositorio

```text
https://github.com/danilaviaart-lgtm/business_revenue
```

---

### 1.2 Dataset utilizado

Se utiliza el dataset:

```text
Online Shoppers Purchasing Intention Dataset
```

procedente de:

```text
UCI Machine Learning Repository
```
URL: https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset

El dataset contiene información sobre sesiones de navegación en ecommerce, incluyendo:

- páginas administrativas visitadas
- duración en páginas administrativas
- páginas informativas visitadas
- duración en páginas informativas
- páginas de producto visitadas
- duración en páginas de producto
- tasa de rebote
- tasa de salida
- valor de página
- mes de navegación
- sistema operativo
- navegador
- región
- tipo de tráfico
- tipo de visitante
- navegación en fin de semana
- resultado final de compra (`Revenue`)

---

## 2. Proceso de Machine Learning

### 2.1 Limpieza de datos

Se realizó una revisión inicial del dataset para validar la calidad de los datos:

- comprobación de valores nulos
- detección de duplicados
- eliminación de registros duplicados
- revisión de tipos de variables
- análisis del desbalanceo de la variable objetivo

La variable objetivo `Revenue` fue convertida a formato binario.

---

### 2.2 Preprocesamiento

Las variables categóricas fueron transformadas mediante `OneHotEncoder`.

Variables categóricas utilizadas:

- `Month`
- `VisitorType`
- `Weekend`

También se aplicó `SMOTE` para balancear la clase minoritaria, ya que el dataset contiene muchas más sesiones sin compra que con compra.

---

### 2.3 Modelos entrenados

Se compararon dos modelos de Machine Learning:

#### Logistic Regression

Modelo lineal utilizado como baseline inicial.

#### Random Forest Classifier

Modelo ensemble basado en múltiples árboles de decisión.

*Fue seleccionado como modelo final por obtener mejor rendimiento general.*

---
**Comparación de modelos**

Las métricas utilizadas para comparar los modelos fueron:

- ROC-AUC
- Precision
- Recall

| Modelo | ROC-AUC | Precision | Recall |
|---|---:|---:|---:|
| Logistic Regression | 0.91 | 0.51 | 0.80 |
| Random Forest | 0.93 | 0.65 | 0.74 |

Aunque Logistic Regression obtuvo mayor recall, Random Forest consiguió mejor ROC-AUC y mayor precision, por lo que se seleccionó como modelo final.

---
*Modelo final*:

El modelo final seleccionado fue: Random Forest Classifier


El pipeline final incluye:

- OneHotEncoder
- SMOTE
- Random Forest Classifier

El modelo entrenado se guarda en:

```text
models/purchase_prediction_model.pkl
```
---

## 3. API REST

La API fue desarrollada utilizando:

- FastAPI: se utiliza para crear la API REST y generar automáticamente la documentación interactiva.
- Pydantic: se utiliza para validar los datos de entrada, especialmente en el endpoint de predicción.
- Uvicorn: se utiliza para ejecutar la aplicación en local.

---

### 3.1 Endpoints de la API

Una vez ejecutada la API en local, se puede acceder desde:

```text
http://127.0.0.1:8000/
```

La documentación interactiva de FastAPI está disponible en:

```text
http://127.0.0.1:8000/docs
```
---

#### 3.1.1 GET `/`

**Descripción:**  Ruta principal de la API. Sirve para comprobar que la aplicación está en ejecución y orientar al usuario hacia la documentación.

**Ejemplo de acceso:** http://127.0.0.1:8000/

**Ejemplo de respuesta:**

```json
{
  "status": "API en ejecución. Prueba",
  "documentacion": "/docs",
  "mensaje": "Visita /docs para probar el endpoint de predicción."
}
```
---

#### 3.1.2  GET `/health`

**Descripción:** Endpoint de estado del servicio. Se utiliza para comprobar que la API está funcionando correctamente. Es útil para pruebas, monitorización y despliegue.

**Ejemplo de acceso:** http://127.0.0.1:8000/health
---

#### 3.1.3 GET `/datos/revenue`

**Descripción:** Endpoint con parámetro en la query. Filtra los registros según el valor de la columna `Revenue`.

**Uso:** Permite obtener usuarios que han comprado o usuarios que no han comprado.

**Parámetro query:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `valor` | string | Valor booleano a buscar en `Revenue`: `true` o `false` |

**Ejemplo usuarios que han comprado:** http://127.0.0.1:8000/datos/revenue?valor=true


**Ejemplo usuarios que no han comprado:** http://127.0.0.1:8000/datos/revenue?valor=false

**Uso business:**

Este endpoint sirve para segmentar usuarios según si han comprado o no.

Por ejemplo:

- usuarios con `Revenue = true` → candidatos a fidelización, email post-compra o push notification
- usuarios con `Revenue = false` → candidatos a campañas de recuperación o retargeting

#### 3.1.4 GET `/datos/all`

**Descripción:** Devuelve todos los registros del CSV cargado en la API. Este endpoint permite visualizar el dataset completo desde la API REST.

**Ejemplo de acceso:** http://127.0.0.1:8000/datos/all

**Uso:** Se puede utilizar para comprobar que los datos se han cargado correctamente y para explorar todos los registros disponibles.
---

#### 3.1.5 GET `/datos/{id_cliente}`

**Descripción:** Endpoint con parámetro en el path. Permite consultar la información de un cliente concreto utilizando su identificador.

**Parámetro path:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `id_cliente` | integer | ID del cliente que se desea consultar |

**Ejemplo de acceso:** http://127.0.0.1:8000/datos/1001

**Uso:** Se utiliza para recuperar información individual de un cliente y simular una consulta tipo CRM.


#### 3.1.6 GET `/datos/ultimos/`

**Descripción:** Devuelve las últimas filas del dataset. Este endpoint es útil para visualizar rápidamente algunos registros sin cargar todo el archivo.

**Ejemplo de acceso:** http://127.0.0.1:8000/datos/ultimos/

**Uso:** Se utiliza como consulta rápida de datos y como endpoint de prueba para verificar que la API está leyendo correctamente el CSV.

---

#### 3.1.7 POST `/predict`

**Descripción:** Endpoint principal del modelo de Machine Learning. Recibe en el cuerpo de la petición un JSON con las variables de navegación de un usuario y devuelve una predicción de intención de compra.

**Uso:** Este endpoint carga el modelo entrenado y lo utiliza para predecir si el usuario comprará o no.

**Ejemplo de acceso:** http://127.0.0.1:8000/predict


**Ejemplo de petición JSON:**

```json
{
  "Administrative": 0,
  "Administrative_Duration": 0,
  "Informational": 0,
  "Informational_Duration": 0,
  "ProductRelated": 1,
  "ProductRelated_Duration": 11.25,
  "BounceRates": 0,
  "ExitRates": 0.1,
  "PageValues": 0,
  "SpecialDay": 0,
  "Month": "May",
  "OperatingSystems": 2,
  "Browser": 2,
  "Region": 1,
  "TrafficType": 1,
  "VisitorType": "Returning_Visitor",
  "Weekend": true
}
```

**Ejemplo de respuesta:**

```json
{
  "prediction": 0,
  "purchase_probability": 0.32
}
```

**Interpretación de la respuesta:**

- `prediction = 1` → el modelo predice que el usuario comprará
- `prediction = 0` → el modelo predice que el usuario no comprará
- `purchase_probability` → probabilidad estimada de compra

**Uso business:**

Este endpoint permite que una empresa tome decisiones en tiempo real.

Por ejemplo:

- si la probabilidad de compra es alta → enviar email personalizado
- si el usuario es recurrente y tiene alta intención → enviar push notification
- si la probabilidad es baja → evitar impacto comercial innecesario
- si el usuario abandona rápido → activar campaña de recuperación

*Las predicciones se guardan en un archivo*
---

### 3.2 Validación automática

La API utiliza Pydantic para validar los datos de entrada.

Esto permite controlar:

- tipos de datos incorrectos
- campos obligatorios
- errores en parámetros
- formatos inválidos

Cuando los datos no cumplen el formato esperado, FastAPI devuelve automáticamente un error:

```text
422 Validation Error
```
---

## 4. Instalación y ejecución en local

**Clonar el repositorio:** git clone https://github.com/danilaviaart-lgtm/business_revenue.git

**Entrar en la carpeta del proyecto:**

```bash
cd business_revenue
```

**Crear entorno virtual:**

```bash
python -m venv .venv
```

**Activar entorno virtual:**

*Windows*

```bash
.venv\Scripts\activate
```
*Mac/Linux*

```bash
source .venv/bin/activate
```

**Instalar dependencias:**

```bash
pip install -r requirements.txt
```
---

**Ejecutar la API:**

Desde la carpeta inicial del repositorio ejecutar:

```bash
python -m uvicorn src.api.main:app --reload
```

Una vez ejecutado, la API estará disponible en: http://127.0.0.1:8000/

La documentación interactiva estará disponible en:http://127.0.0.1:8000/docs
```
---

Ejecutar el cliente:

Desde la carpeta inicial del repositorio ejecutar:

```bash
python src/client/client.py
```

El cliente sirve para probar la API desde un script Python sin necesidad de utilizar el navegador.

---

**URL del servicio desplegado:**

Pendiente de añadir:

```text
URL_DEPLOY
```
---

## 5. Estructura del proyecto

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