import pandas as pd
from sqlalchemy import create_engine
import os
import joblib
import numpy as np
import pandas as pd

csv = './data/processed/data_idname.csv'
RUTA_CSV = os.path.join(os.path.dirname(__file__), csv)

df = pd.read_csv(csv, index_col=0)

engine = create_engine('postgresql://business:esther@192.168.0.20:6432/business_revenue_db')

if 'ID_cliente' in df.columns:
    df.set_index('ID_cliente', inplace=True)
else:
 
    raise KeyError("La columna 'ID_cliente' no se encuentra en el archivo CSV")

df.to_sql(
    name='business', 
    con=engine, 
    if_exists='replace', 
    index=True,       
    index_label='ID_cliente', 
    chunksize=10000
)
print("¡CSV subido con éxito!")