
# Business Revenue - Purchase Intention API

**Equipo:**  Esther Barranco Motos & Dani Lavia Gaya

**Repositorio:** [github.com/danilaviaart-lgtm/business_revenue](https://github.com/danilaviaart-lgtm/business_revenue)

---

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