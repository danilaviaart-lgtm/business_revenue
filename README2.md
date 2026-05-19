
# Business Revenue - Purchase Intention API

**Equipo:**  Esther Barranco Motos & Dani Lavia Gaya

**Repositorio:** [github.com/danilaviaart-lgtm/business_revenue](https://github.com/danilaviaart-lgtm/business_revenue)

## ¿Qué hace?

Predice si un usuario de ecommerce va a comprar (`Revenue` = 1) o no (`Revenue` = 0).

**Modelo:** Random Forest | **ROC-AUC:** 0.93

###  Uso business:

- si la probabilidad de compra es alta → enviar email personalizado
- si el usuario es recurrente y tiene alta intención → enviar push notification
- si la probabilidad es baja → evitar impacto comercial innecesario
- si el usuario abandona rápido → activar campaña de recuperación
- ...
**Las predicciones se guardan en un archivo.**

## Desarrollo

Para exponer el modelo de Machine Learning y permitir su consumo en tiempo real por otras aplicaciones, se desarrolló una API REST con FastAPI.

### Componentes Core del Desarrollo

- **FastAPI:** Framework principal utilizado para la construcción de la API. Se seleccionó por su alto rendimiento (comparable a NodeJS y Go) y su capacidad para generar documentación interactiva automática (Swagger UI y ReDoc), lo que facilita enormemente las pruebas de los endpoints.
- **Pydantic:** Encargado de la validación de datos y la gestión de configuraciones. Define las estructuras de los datos de entrada (*features* que requiere el modelo) y de salida (*predictions*), garantizando que la API solo procese peticiones con el formato y tipo de datos correctos.
- **Uvicorn:** Servidor ASGI de velocidad ultra rápida empleado para ejecutar la aplicación, permitiendo el manejo de peticiones de forma asíncrona.

------

### Flujo de Funcionamiento

1. **Recepción de Datos (Request):** El cliente envía una petición HTTP (normalmente `POST`) con los datos del caso a evaluar en formato JSON.
2. **Validación:** **Pydantic** intercepta los datos, asegurando que cumplen estrictamente con los tipos esperados (ej. flotantes, enteros, strings). Si los datos son inválidos, devuelve un error automático al cliente sin sobrecargar el modelo.
3. **Predicción (Inferencia):** Los datos validados se introducen en el *pipeline* del modelo de Machine Learning previamente entrenado y cargado en memoria. El modelo procesa la información y genera la predicción.
4. **Respuesta (Response):** **FastAPI** emite una respuesta HTTP estructurada con el resultado de la predicción y sus métricas asociadas (como la probabilidad).

> **Nota de Arquitectura:** Esta estructura modular separa por completo la lógica de negocio y validación de la lógica propia del modelo predictivo, facilitando el mantenimiento, el escalado y futuras actualizaciones del modelo de Machine Learning sin alterar la estructura de la API.



---

## Endpoints principales

| Método | Endpoint | Qué hace |
|--------|----------|----------|
| GET | `/` | Estado de la API |
| GET | `/health` | Health check |
| GET | `/datos/revenue?valor=true/false` | Filtrar por compra/no compra |
| GET | `/datos/all` | Todos los datos |
| GET | `/datos/{id_cliente}` | Cliente por ID |
| GET | `/datos/ultimos/` | Últimos registros |
| POST | `/predict` | Predicción de compra |

---

## Ejemplo `curl`

```bash
curl -X 'POST' \
  'https://business.1morecoffee.cc/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Administrative": 0,
  "Administrative_Duration": 0,
  "Informational": 0,
  "Informational_Duration": 0,
  "ProductRelated": 1,
  "ProductRelated_Duration": 11.25,
  "BounceRates": 0,
  "ExitRates": 0.1,
  "PageValues": 0,
  "Nombre_cliente": "Beatriz Barreda",
  "SpecialDay": 0,
  "Month": "May",
  "OperatingSystems": 2,
  "Browser": 2,
  "Region": 1,
  "TrafficType": 1,
  "VisitorType": "Returning_Visitor",
  "Weekend": true
}'
```
### Respuesta

```bash
{
  "prediction": 0,
  "purchase_probability": 0.32
}
```
## Instalación y ejecución

### Opción Docker

```bash
# Clonar el repositorio
git clone [https://github.com/danilaviaart-lgtm/business_revenue](https://github.com/danilaviaart-lgtm/business_revenue)
cd business_revenue

# Docker Compose
docker-compose up --build
```

### Opción Local

```bash
# Clonar el repositorio
git clone [https://github.com/danilaviaart-lgtm/business_revenue](https://github.com/danilaviaart-lgtm/business_revenue)
cd business_revenue

# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias y arrancar
pip install -r requirements.txt
python -m uvicorn src.api.main:app --reload
```

## Acceso

- API: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs

( Recuerda intercambiar el localhost por tu ip )