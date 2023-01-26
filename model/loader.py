import pandas as pd
from pathlib import Path

filename = Path("data/_combined_datasets.xlsx")
df = pd.read_excel(filename, engine='openpyxl')

print(df)