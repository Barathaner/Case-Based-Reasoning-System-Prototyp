import pandas as pd
from src.utils import openairequests

# DataFrame laden
df = pd.read_csv('./data/RecipeNLG_dataset_random.csv')

# Spalten für Küche, Kursart und Ernährungsart hinzufügen
df['cuisine'] = pd.NA
df['course_type'] = pd.NA
df['dietary_classification'] = pd.NA


# Funktion zum Bereinigen und Konvertieren des Antwortstrings in eine Liste
def parse_response(response):
    # Entfernen der Anführungszeichen und der eckigen Klammern
    clean_response = response.strip("[]").replace('"', '')
    # Umwandeln in Liste
    return [item.strip() for item in clean_response.split(",")]


for i in range(df.shape[0]):
    # API-Anfrage
    response = openairequests.evaluate_prompt(df.iloc[i].to_string())

    # Antwort verarbeiten
    parsed_response = parse_response(response)

    # Überprüfung, ob die Antwort korrekt geparsed wurde und drei Elemente enthält
    if len(parsed_response) == 3:
        # Werte zu den entsprechenden Spalten hinzufügen
        df.at[i, 'cuisine'] = parsed_response[0]
        df.at[i, 'course_type'] = parsed_response[1]
        df.at[i, 'dietary_classification'] = parsed_response[2]

# DataFrame speichern oder weiterverwenden
print(df.head())  # Zum Überprüfen der ersten paar Zeilen

df.to_csv('./data/Recipes.csv', index=False)  # Speichern des aktualisierten DataFrames
