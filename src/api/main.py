import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi import Path as FastApiPath
from pathlib import Path as FilePath
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from sqlmodel import Field, SQLModel, Session, create_engine, select
from .schemas import PredictInput  #con esto llamamos a schemas.py para usar los modelos de datos que definimos allí, como PredictInput para la predicción. Evitamos así tener un main.py gigante y desordenado, y mantenemos la estructura modular y limpia.
'''
#Conexión a base de datos
postgres_url = "postgresql://business:esther@192.168.0.20:5432/business_revenue_db"
# En Postgres ya no necesitas el connect_args de SQLite
engine = create_engine(postgres_url)
'''


# Configuración de rutas
BASE_DIR = FilePath(__file__).resolve().parent.parent.parent
RUTA_CSV = BASE_DIR / "data" / "processed" / "data_idname.csv" # direccion del csv procesado
RUTA_MODELO = BASE_DIR / "models" / "modelo_entrenado.pkl" # direccion del pickle del modelo entrenado


@asynccontextmanager
async def lifespan(app: FastAPI):
    # arrancar servidor mensaje informe
    print("Cargando modelo ...")
    try:
        # Guardamos el modelo directamente en el state de la app
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

@app.get("/")
def inicio():
    return {
        "status": "API en ejecución /health para check de salud",
        "documentacion": "/docs",
        "query revenue": "http://127.0.0.1:8000/datos/revenue?valor=true",
        "query cliente": "http://127.0.0.1:8000/datos/450",
        "Check": "http://127.0.0.1:8000/health",
    }

@app.get("/health")
def health_check():
    status_checks = {
        "Api": "UP",
        "csv_file": "unknown"
    }
    
    if not os.path.exists(RUTA_CSV):
        status_checks["csv_file"] = "No encontrado"
        raise HTTPException(
            status_code=503, 
            detail={"status": "unhealthy", "checks": status_checks, "error": "El archivo CSV no existe"}
        )
    try:
        # 2. Intentar leer solo las primeras filas para verificar que no esté corrupto
        # Usamos nrows=5 para que sea un check ultra rápido y no cargue gigas en memoria, el csv es enhorme si no se peta.
        df = pd.read_csv(RUTA_CSV, nrows=5)
        
        status_checks["csv_file"] = "Archivo ok"
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

@app.get("/datos/clientes_por_revenue")
def filtrar_por_revenue(
    valor: str = Query(
        ...,
        description="Valor booleano a buscar en la columna Revenue (true/false)",
    ),
):
    """Filtra el archivo CSV leyendo solo las columnas necesarias."""
    if not os.path.exists(RUTA_CSV):
        raise HTTPException(
            status_code=404, detail="El archivo CSV no se encontró."
        )

    try:
        valor_limpio = valor.strip().lower()
        if valor_limpio in ("true", "1", "yes", "t"):
            valor_buscado = True
        elif valor_limpio in ("false", "0", "no", "f"):
            valor_buscado = False
        else:
            raise HTTPException(
                status_code=400,
                detail="El valor debe ser un booleano válido: 'true' o 'false'.",
            )

        columnas_requeridas = ["Revenue", "Nombre_cliente"]
        
        df = pd.read_csv(RUTA_CSV, usecols=columnas_requeridas)
        df_filtrado = df[df["Revenue"].astype(bool) == valor_buscado]
        df_resultado = df_filtrado[["Nombre_cliente"]]

        if df_resultado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron registros donde Revenue sea {valor_buscado}",
            )

        df_resultado = df_resultado.replace({np.nan: None})
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
            status_code=400, detail=f"Error en la estructura del CSV: {str(val_err)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el CSV: {str(e)}"
        )


@app.get("/datos/revenue")
def filtrar_por_revenue(
    valor: str = Query(
        ...,
        description="Valor booleano a buscar en la columna Revenue (true/false)",
    ),
):
    if not os.path.exists(RUTA_CSV):
        raise HTTPException(
            status_code=404, detail="El archivo CSV no se encontró."
        )

    try:
        df = pd.read_csv(RUTA_CSV)
        if "Revenue" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="La columna 'Revenue' no existe en este archivo CSV.",
            )
        valor_limpio = valor.strip().lower()
        if valor_limpio in ("true", "1", "yes", "t"):
            valor_buscado = True
        elif valor_limpio in ("false", "0", "no", "f"):
            valor_buscado = False
        else:
            raise HTTPException(
                status_code=400,
                detail="El valor debe ser un booleano válido: 'true' o 'false'.",
            )
        df_filtrado = df[df["Revenue"].astype(bool) == valor_buscado]

        if df_filtrado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron registros donde Revenue sea {valor_buscado}",
            )

        df_filtrado = df_filtrado.replace({np.nan: None})
        return {
            "columna": "Revenue",
            "valor_buscado": valor_buscado,
            "total_filas": len(df_filtrado),
            "datos": df_filtrado.to_dict(orient="records"),
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el CSV: {str(e)}"
        )

@app.get("/datos/all/")
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
    

@app.post("/predict", summary="Genera una predicción con el modelo de ML entrenado")
def predict(request: Request, input_data: PredictInput):
    # 1. Verificación del modelo (tu código actual)
    try:
        modelo = request.app.state.modelo
    except AttributeError:
        raise HTTPException(
            status_code=503,
            detail="El modelo no está disponible en el servidor."
        )

    try:
        # 2. Preparación de datos y predicción
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