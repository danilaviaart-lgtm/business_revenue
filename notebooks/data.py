import pandas as pd

# 1. Leer el archivo CSV
df = pd.read_csv("data/processed/data_idname.csv")

# 2. Guardar en formato Parquet
df.to_parquet("data/processed/data_idname.parquet", engine="pyarrow", compression="snappy")