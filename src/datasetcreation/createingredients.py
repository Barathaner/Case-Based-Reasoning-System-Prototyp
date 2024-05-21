import pandas as pd
from src.utils import openairequests
import ast

# DataFrame laden
df = pd.read_csv('./data/RecipeNLG_dataset_random.csv')

# Neuen DataFrame für die Zutaten erstellen
ingredients_df = pd.DataFrame(columns=['Recipe Name', 'Ingredient', 'Amount', 'Unit', 'Basic Taste','food category'])

# Funktion zum Bereinigen und Konvertieren des Antwortstrings in eine Liste von Listen
for i in range(df.shape[0]):
    # API-Anfrage
    title = str(df.iloc[i]['title'])
    ingredients = str(df.iloc[i]['ingredients'])
    response = openairequests.evaluate_prompt(f"recipename: {title} ingredients in the recipe:{ingredients}")
    print(response)
    # Antwort verarbeiten
    parsed_entries =ast.literal_eval(response)
    print(parsed_entries)

    # Jede Antwort in den neuen DataFrame einfügen
    for entry in parsed_entries:
        ingredients_df = pd.concat([ingredients_df, pd.DataFrame([entry], columns=ingredients_df.columns)], ignore_index=True)

    ingredients_df.to_csv('./data/RecipeNLG_ingredients_dataset.csv', index=False)  # Speichern des aktualisierten DataFrames
# DataFrame speichern oder weiterverwenden
print(ingredients_df.head())  # Zum Überprüfen der ersten paar Zeilen

ingredients_df.to_csv('./data/RecipeNLG_ingredients_dataset.csv', index=False)  # Speichern des aktualisierten DataFrames
