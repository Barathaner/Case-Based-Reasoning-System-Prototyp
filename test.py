import sqlite3
import pandas as pd
connection = sqlite3.connect('path_to_your_db.db')

query = "SELECT * FROM your_table_name"
df = pd.read_sql(query, connection)
print(df)