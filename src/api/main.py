import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

# Configuración de rutas
RUTA_CSV = "../data/processed/data.csv" # ruta de csv
RUTA_MODELO = "models/modelo_entrenado.pkl"


# 3. INICIALIZACIÓN DE FASTAPI
app = FastAPI(
    title="API de Predicciones con Pipeline de ML",
    version="1.0.0",
)

@app.get("/")
def inicio():
    return {
        "status": "API en ejecución. Prueba",
        "documentacion": "/docs",
        "mensaje": "Visita /docs para probar el endpoint de predicción."
    }

@app.get("/datos")
def obtener_todo_el_csv():
    if not os.path.exists(RUTA_CSV):
        raise HTTPException(
            status_code=404, 
            detail=f"El archivo CSV no se encontró en la ruta: {RUTA_CSV}"
        )
    try:
        # 2. Leer el CSV con Pandas
        df = pd.read_csv(RUTA_CSV)
        
        # Opcional: Reemplazar valores NaN/Nulos por None para que no rompa el JSON
        # df = df.replace({np.nan: None})
        
        datos = df.to_dict(orient="records")
        
        return {
            "total_filas": len(df),
            "columnas": list(df.columns),
            "datos": datos
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al leer el archivo CSV: {str(e)}"
        )