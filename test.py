import sqlite3
import pandas as pd
connection = sqlite3.connect('data/WebCrawledSandwichRecipes/recipes.sql')

query = "SELECT * FROM recipes"
df = pd.read_sql(query, connection)
print(df)