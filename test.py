import sqlite3
import pandas as pd
connection = sqlite3.connect('./data/recipe_ingredients.db')

query = "SELECT * FROM descriptiveRecipe"
df = pd.read_sql(query, connection)
df.to_csv('./data/recipe_ingredients.csv', index=False)
print(df.head())