import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi import Path as FastApiPath
from pathlib import Path as FilePath
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

# Configuración de rutas
BASE_DIR = FilePath(__file__).resolve().parent.parent.parent
RUTA_CSV = BASE_DIR / "data" / "processed" / "data_idname.csv" # direccion del csv procesado
RUTA_MODELO = BASE_DIR / "models" / "modelo_entrenado.pkl" # direccion del pickle del modelo entrenado

class PredictInput(BaseModel):
    Administrative: int = Field(..., description="Número de páginas administrativas visitadas", example=0)
    Administrative_Duration: float = Field(..., description="Tiempo total en páginas administrativas", example=0.0)
    Informational: int = Field(..., description="Número de páginas informativas visitadas", example=0)
    Informational_Duration: float = Field(..., description="Tiempo total en páginas informativas", example=0.0)
    ProductRelated: int = Field(..., description="Número de páginas relacionadas con productos visitadas", example=1)
    ProductRelated_Duration: float = Field(..., description="Tiempo total en páginas de productos", example=11.25)
    BounceRates: float = Field(..., description="Porcentaje de rebote de la página", example=0.0)
    ExitRates: float = Field(..., description="Porcentaje de salida de la página", example=0.1)
    PageValues: float = Field(..., description="Valor medio de la página web", example=0.0)
    SpecialDay: float = Field(..., description="Cercanía a una fecha especial o festivo (0.0 a 1.0)", example=0.0)
    Month: str = Field(..., description="Mes de la sesión (ej: Feb, Mar, May, Nov)", example="May")
    OperatingSystems: int = Field(..., description="ID del sistema operativo del usuario", example=2)
    Browser: int = Field(..., description="ID del navegador utilizado", example=2)
    Region: int = Field(..., description="ID de la región del usuario", example=1)
    TrafficType: int = Field(..., description="ID del tipo de tráfico de origen", example=1)
    VisitorType: str = Field(..., description="Tipo de visitante: Returning_Visitor, New_Visitor, Other", example="Returning_Visitor")
    Weekend: bool = Field(..., description="Indica si la sesión ocurrió en fin de semana", example=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # arrancar servidor mensaje informe
    print("Cargando modelo ...")
    try:
        # Guardamos el modelo directamente en el state de la app
        app.state.modelo = joblib.load(RUTA_MODELO)
        print("¡Modelo optimizado cargado con éxito!")
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
        "status": "API en ejecución. Prueba",
        "documentacion": "/docs",
        "mensaje": "Visita /docs para probar el endpoint de predicción."
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

@app.get("/datos/revenue")
def filtrar_por_revenue(
    valor: str = Query(
        ...,
        description="Valor booleano a buscar en la columna Revenue (true/false)",
    ),
):
    """Filtra el archivo CSV específicamente por la columna booleana 'Revenue'."""

    # 1. Verificar si el archivo existe
    if not os.path.exists(RUTA_CSV):
        raise HTTPException(
            status_code=404, detail="El archivo CSV no se encontró."
        )

    try:
        df = pd.read_csv(RUTA_CSV)

        # 2. Verificar si la columna 'Revenue' existe en el CSV
        if "Revenue" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="La columna 'Revenue' no existe en este archivo CSV.",
            )

        # 3. Convertir el texto recibido ("true"/"false") a un booleano real de Python
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

        # 4. Asegurar que la columna de Pandas se evalúe como booleana y filtrar
        # Convertimos la columna a .astype(bool) para evitar fallos si venía como texto o enteros (0/1)
        df_filtrado = df[df["Revenue"].astype(bool) == valor_buscado]

        # 5. Verificar si hay resultados
        if df_filtrado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron registros donde Revenue sea {valor_buscado}",
            )

        # 6. Limpiar valores Nulos/NaN para no romper el JSON y devolver la respuesta
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
    #devolvemos el modelo cargado en el estado de la app. Si no que lance error y no acabe de arrancar.
    try:
        modelo = request.app.state.modelo
    except AttributeError:
        raise HTTPException(
            status_code=503,
            detail="El modelo no está disponible en el servidor. Revisa los logs de arranque."
        )

    try:
        # 2. Convertir los datos de entrada en un DataFrame de Pandas (evita fallos de nombres de columnas)
        # .dict() convierte el Pydantic a diccionario, y [dict] lo prepara para DataFrame
        input_dict = input_data.model_dump()
        df_registro = pd.DataFrame([input_dict])

        # ejecutamos prediccion
        # Si tu modelo devuelve probabilidades (ej. clasificación binaria) podrías usar modelo.predict_proba()
        prediccion = modelo.predict(df_registro)

        # convertimos a tipo nativo de Python para que FastAPI no pete con tipos de numpy
        resultado_prediccion = prediccion[0]
        if isinstance(resultado_prediccion, (np.integer, np.floating)):
            resultado_prediccion = resultado_prediccion.item()

        return {
            "status": "Sin fallo en la predicción.",
            "VisitorType": input_data.VisitorType,
            "accion_recomendada": "Si el resultado es 1, se recomienda descuento 10%. Si es 0, no se recomienda.",
            "prediccion": resultado_prediccion
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno durante la predicción: {str(e)}"
        )