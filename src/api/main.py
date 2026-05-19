import os
import joblib
import numpy as np
import pandas as pd
import pyarrow as pq
from fastapi import FastAPI, APIRouter, HTTPException, Path, Query, Request
from pathlib import Path as FilePath
from contextlib import asynccontextmanager
from .schemas import PredictInput  #con esto llamamos a schemas.py para usar los modelos de datos que definimos allí, como PredictInput para la predicción. Evitamos así tener un main.py gigante y desordenado, y mantenemos la estructura modular y limpia.


# Configuración de rutas
BASE_DIR = FilePath(__file__).resolve().parent.parent.parent
RUTA_CSV = BASE_DIR / "data" / "processed" / "data_idname.csv" # direccion del csv procesado
RUTA_MODELO = BASE_DIR / "models" / "modelo_entrenado.pkl" # direccion del pickle del modelo entrenado
RUTA_PARQUET = BASE_DIR / "data" / "processed" / "data_idname.parquet"
# Por si pasamos por rutas relativas
router = APIRouter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # arrancar servidor mensaje informe
    print("Cargando modelo ...")
    try:
        # Guardamos el modelo directamente en el state de la app para que no se recargue siempre
        app.state.modelo = joblib.load(RUTA_MODELO)
        print("¡Modelo optimizado cargado con éxito!")
        modelocargado = True
    except FileNotFoundError:
        print("Error: El archivo del modelo no existe.")
        raise RuntimeError("Archivo de modelo no encontrado.")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        raise RuntimeError(f"Error crítico en la carga del modelo: {e}")
    
    yield  # La API se queda activa aquí
    
    print("Liberando memoria RAM...")
    #eliminar modelo y liberamos RAM. apagar server
    if hasattr(app.state, "modelo"):
        del app.state.modelo

#Iniciamos app FastApi con el lifespan definido para cargar el modelo al arrancar y liberar memoria al apagar.
app = FastAPI(
    title="API de Predicciones con Pipeline de ML",
    version="1.0.0",
    lifespan=lifespan
)

# Principal
@app.get("/")
def inicio(request: Request):
    return {
        "status": "API en ejecución /health para check de salud",
        "mensaje": "Este proyecto desarrolla una API REST con Machine Learning para predecir la intención de compra de usuarios en un ecommerce a partir de su comportamiento de navegación.",
        "documentacion": str(request.base_url) + "docs",
        "query revenue": str(request.base_url) + "datos/revenue?valor=true",
        "query cliente": str(request.base_url) + "datos/450",
        "Check": str(request.base_url) + "health",
    }

#Ver salud del servidor
@app.get("/health")
def health_check():
    status_checks = {
        "Api": "UP",
        "parquet_file": "unknown"
    }
    
    if not os.path.exists(RUTA_PARQUET):
        status_checks["parquet_file"] = "No encontrado"
        raise HTTPException(
            status_code=503, 
            detail={"status": "unhealthy", "checks": status_checks, "error": "El archivo Parquet no existe"}
        )
    try:
        import pyarrow.parquet as pq
        
        pq.read_metadata(RUTA_PARQUET)
        
        status_checks["parquet_file"] = "Archivo ok"
        return {
            "status": "healthy",
            "checks": status_checks,
        }
        
    except Exception as e:
        status_checks["parquet_file"] = "corrupted o unreadable"
        raise HTTPException(
            status_code=503, 
            detail={"status": "unhealthy", "checks": status_checks, "error": str(e)}
        )

# Endpoint para filtrar por Revenue
@app.get("/datos/revenue")
def filtrar_por_revenue(
    valor: str = Query(
        ...,
        description="Valor booleano a buscar en la columna Revenue (true/false)",
    ),
):
    if not os.path.exists(RUTA_PARQUET):
        raise HTTPException(
            status_code=404, detail="El archivo Parquet no se encontró."
        )

    # 1. Normalización y validación del input del usuario
    valor_limpio = valor.strip().lower()
    if valor_limpio in ("true", "1", "yes", "t"):
        valor_buscado = True
    elif valor_limpio in ("false", "0", "no", "f"):
        valor_buscado = False
    else:
        raise HTTPException(
            status_code=400,
            detail="El valor debe ser un booleano válido (e.g., 'true' o 'false').",
        )
    try:
        columnas_requeridas = ["Revenue", "Nombre_cliente"]
        
        df_resultado = pd.read_parquet(
            RUTA_PARQUET,
            columns=columnas_requeridas,
            filters=[("Revenue", "==", valor_buscado)]
        )

        if df_resultado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron registros donde Revenue sea {valor_buscado}",
            )

        # 4. Limpieza de NaN a None (para JSON válido) y selección de la columna final
        df_resultado = df_resultado[["Nombre_cliente"]].replace({np.nan: None})
        
        return {
            "columna_filtro": "Revenue",
            "valor_buscado": valor_buscado,
            "total_filas": len(df_resultado),
            "datos": df_resultado.to_dict(orient="records"),
        }

    except HTTPException as http_ex:
        raise http_ex
    except ValueError as val_err:
        raise HTTPException(
            status_code=400, detail=f"Error en la estructura del archivo Parquet: {str(val_err)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el archivo Parquet: {str(e)}"
        )

# Visionar todos los datos del parquet con paginación (limit y offset)
@app.get("/datos/all/")
def obtener_todo_el_parquet(
    limit: int = Query(100, ge=1, le=1000, description="Número de filas a retornar"),
    offset: int = Query(0, ge=0, description="Número de filas a saltar")
):
    if not os.path.exists(RUTA_PARQUET):
        raise HTTPException(
            status_code=404, 
            detail=f"El archivo Parquet no se encontró en la ruta: {RUTA_PARQUET}"
        )
    try:
        import pyarrow.parquet as pq
        
        archivo_parquet = pq.ParquetFile(RUTA_PARQUET)
        total_filas = archivo_parquet.metadata.num_rows
        columnas = archivo_parquet.metadata.schema.names

        if offset >= total_filas:
            return {
                "total_filas": total_filas,
                "columnas": columnas,
                "datos": []
            }

        df = pd.read_parquet(RUTA_PARQUET)
        df_paginado = df.iloc[offset : offset + limit]
        df_paginado = df_paginado.replace({np.nan: None})
        
        return {
            "total_filas": total_filas,
            "columnas": columnas,
            "limite_pagina": limit,
            "desplazamiento": offset,
            "datos": df_paginado.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al leer el archivo Parquet: {str(e)}"
        )
#busqueda por ID cliente
@app.get("/datos/{id_cliente}")
def obtener_datos_cliente(
    id_cliente: int = Path(..., description="El ID del cliente que quieres filtrar")
):
    if not os.path.exists(RUTA_PARQUET):
        raise HTTPException(
            status_code=404, 
            detail=f"El archivo Parquet no se encontró."
        )
    try:
        columna_id = "ID_cliente"

        # Leemos aplicando el filtro directamente sobre los bytes del archivo Parquet
        df_filtrado = pd.read_parquet(
            RUTA_PARQUET,
            filters=[(columna_id, "==", id_cliente)]
        )

        if df_filtrado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron registros para el ID_cliente: {id_cliente}",
            )

        df_filtrado = df_filtrado.replace({np.nan: None})
        datos = df_filtrado.to_dict(orient="records")

        return {
            "id_cliente_buscado": id_cliente,
            "total_filas_encontradas": len(df_filtrado),
            "columnas": list(df_filtrado.columns),
            "datos": datos,
        }

    except HTTPException as http_ex:
        raise http_ex
    except ValueError as val_err:
        raise HTTPException(
            status_code=400, 
            detail=f"La columna '{columna_id}' no existe o tiene un tipo incompatible en el archivo Parquet."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar el archivo Parquet: {str(e)}"
        )

#Últimos 5 valores del parquet
@app.get("/datos/ultimos/")
def obtener_ultimas_filas():
    if not os.path.exists(RUTA_PARQUET):
        raise HTTPException(
            status_code=404, 
            detail=f"El archivo Parquet no se encontró en la ruta: {RUTA_PARQUET}"
        )
    try:
        import pyarrow.parquet as pq
        
        archivo_parquet = pq.ParquetFile(RUTA_PARQUET)
        total_filas = archivo_parquet.metadata.num_rows
        columnas = archivo_parquet.metadata.schema.names

        filas_a_mostrar = 5
        offset = max(0, total_filas - filas_a_mostrar)

        df = pd.read_parquet(RUTA_PARQUET)
        df_ultimos = df.iloc[offset:]
        df_ultimos = df_ultimos.replace({np.nan: None})
        
        datos = df_ultimos.to_dict(orient="records")
        
        return {
            "total_filas_mostradas": len(df_ultimos),
            "total_filas_totales_parquet": total_filas,
            "columnas": columnas,
            "datos": datos
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar las últimas filas del Parquet: {str(e)}"
        )

# Predecircion con el modelo de ML entrenado
@app.post("/predict", summary="Genera una predicción con el modelo de ML entrenado")
def predict(request: Request, input_data: PredictInput):
    try:
        modelo = request.app.state.modelo
    except AttributeError:
        raise HTTPException(
            status_code=503,
            detail="El modelo no está disponible en el servidor."
        )

    try:
        input_dict = input_data.model_dump()
        df_registro = pd.DataFrame([input_dict])
        
        prediccion = modelo.predict(df_registro)
        resultado_prediccion = prediccion[0]
        
        if isinstance(resultado_prediccion, (np.integer, np.floating)):
            resultado_prediccion = resultado_prediccion.item()

        #guardamos el resultado en el dataframe
        df_registro["resultado_prediccion"] = resultado_prediccion
        
        nombre_archivo = "data/processed/historico_predicciones.csv"
        
        archivo_existe = os.path.isfile(nombre_archivo)
        
        # Guardamos en el CSV
        df_registro.to_csv(
            nombre_archivo, 
            mode='a',
            index=False, 
            header=not archivo_existe, 
            encoding='utf-8'
        )
        
        return {
            "status": "Sin fallo en la predicción.",
            "VisitorType": input_data.VisitorType,
            "accion_recomendada": "Si el resultado es 1, descuento 10%. Si es 0, no se recomienda.",
            "prediccion": resultado_prediccion
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno durante la predicción: {str(e)}"
        )