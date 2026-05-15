import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Path
from fastapi import Path as FastApiPath
from pathlib import Path as FilePath
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

# Configuración de rutas
BASE_DIR = FilePath(__file__).resolve().parent.parent.parent
RUTA_CSV = BASE_DIR / "data" / "processed" / "data_idname.csv" # direccion del csv procesado
RUTA_MODELO = BASE_DIR / "models" / "modelo_entrenado.pkl" # direccion del pickle del modelo entrenado

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_models = {}
    # Al arrancar el servidor. 
    print("Cargando modelo ...")
    try:
        ml_models["mi_modelo"] = joblib.load(RUTA_MODELO)
        print("¡Modelo optimizado cargado con éxito!")
    except FileNotFoundError:
        print("Error: El archivo del modelo no existe.")
        raise RuntimeError("Archivo de modelo no encontrado.")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        raise RuntimeError(f"Error crítico en la carga del modelo: {e}")
    
    yield  # La API se queda activa aquí
    
    #Al apagar el server se ve mensaje de liberación de memoria, aunque en este caso no es tan crítico porque el modelo se carga una sola vez.
    print("Liberando memoria RAM...")
    ml_models.clear()


#Iniciamos app FastApi con el lifespan definido para cargar el modelo al arrancar y liberar memoria al apagar.
app = FastAPI(
    title="API de Predicciones con Pipeline de ML",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def inicio():
    return {
        "status": "API en ejecución. Prueba",
        "documentacion": "/docs",
        "mensaje": "Visita /docs para probar el endpoint de predicción."
    }

@app.get("/health")
def health_check():
    status_checks = {
        "api": "up",
        "csv_file": "unknown"
    }
    
    if not os.path.exists(RUTA_CSV):
        status_checks["csv_file"] = "missing"
        raise HTTPException(
            status_code=503, 
            detail={"status": "unhealthy", "checks": status_checks, "error": "El archivo CSV no existe"}
        )
        
    try:
        # 2. Intentar leer solo las primeras filas para verificar que no esté corrupto
        # Usamos nrows=5 para que sea un check ultra rápido y no cargue gigas en memoria, el csv es enhorme si no se peta.
        df = pd.read_csv(RUTA_CSV, nrows=5)
        
        status_checks["csv_file"] = "up"
        return {
            "status": "healthy",
            "checks": status_checks,
            }
        
    except Exception as e:
        # Si el CSV está corrupto o mal formateado
        status_checks["csv_file"] = "corrupted o unreadable"
        raise HTTPException(
            status_code=503, 
            detail={"status": "unhealthy", "checks": status_checks, "error": str(e)}
        )

@app.get("/clientes/{id_cliente}")
def get_cliente_by_id(id_cliente: int):
    #datis de cliente
    return {
        "origen": "parámetro de path",
        "Id_cliente_buscado": id_cliente,
        "informacion": {
            "nombre": "Ejemplo Cliente",
            "tipo": "Premium",
        },
    }


@app.get("/datos")
def obtener_todo_el_csv(): # peta más que una escopeta de feria.
    if not os.path.exists(RUTA_CSV):
        raise HTTPException(
            status_code=404, 
            detail=f"El archivo CSV no se encontró en la ruta: {RUTA_CSV}"
        )
    try:
        df = pd.read_csv(RUTA_CSV)
        df = df.replace({np.nan: None}) # para que no pete el json al convertirlo, reemplazamos los NaN por None
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

@app.get("/datos/{id_cliente}")
def obtener_datos_cliente(
    id_cliente: int = Path(
        ..., description="El ID del cliente que quieres filtrar"
    )
):
    try:
        df = pd.read_csv(RUTA_CSV)
        columna_id = "ID_cliente"

        if columna_id not in df.columns:
            raise HTTPException(
                status_code=500,
                detail=f"La columna '{columna_id}' no existe en el archivo CSV.",
            )

        df[columna_id] = pd.to_numeric(df[columna_id], errors="coerce")
        df_filtrado = df[df[columna_id] == id_cliente]

        if df_filtrado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron registros para el ID_cliente: {id_cliente}",
            )

        df_filtrado = df_filtrado.replace({np.nan: None}) # truco maestro para que no pete el json al convertirlo, reemplazamos los NaN por None

        datos = df_filtrado.to_dict(orient="records")

        return {
            "id_cliente_buscado": id_cliente,
            "total_filas_encontradas": len(df_filtrado),
            "columnas": list(df_filtrado.columns),
            "datos": datos,
        }

    except HTTPException as http_ex:
        # Volvemos a lanzar los errores 404 que ya controlamos nosotros
        raise http_ex
    except Exception as e:
        # Captura cualquier otra escopeta de feria (formatos rotos, encodings, etc.)
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el CSV: {str(e)}"
        )




@app.get("/datos/ultimos/")
def obtener_ultimas_filas():
    if not os.path.exists(RUTA_CSV):
        raise HTTPException(
            status_code=404, 
            detail=f"El archivo CSV no se encontró en la ruta: {RUTA_CSV}"
        )
    try:
        df = pd.read_csv(RUTA_CSV)
        df_ultimos = df.tail(5)
        df_ultimos = df_ultimos.replace({np.nan: None}) # para que no pete el json al convertirlo, reemplazamos los NaN por None
        
        datos = df_ultimos.to_dict(orient="records")
        
        return {
            "total_filas_mostradas": len(df_ultimos),
            "total_filas_totales_csv": len(df),
            "columnas": list(df.columns),
            "datos": datos
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar las últimas filas del CSV: {str(e)}"
        )