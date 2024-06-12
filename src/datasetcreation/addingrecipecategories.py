import pandas as pd
from src.utils import openairequests



""""_summary:
This was only used to add the categories to the dataset. which were missing. The Dataset ReciNLG can be found on kaggle but because it is 2GB we did not upload it

"""
df = pd.read_csv('./data/RecipeNLG_dataset_random.csv')

df['cuisine'] = pd.NA
df['course_type'] = pd.NA
df['dietary_classification'] = pd.NA


def parse_response(response):
    clean_response = response.strip("[]").replace('"', '')
    return [item.strip() for item in clean_response.split(",")]


for i in range(df.shape[0]):
    response = openairequests.evaluate_prompt(df.iloc[i].to_string())

    parsed_response = parse_response(response)

    if len(parsed_response) == 3:
        df.at[i, 'cuisine'] = parsed_response[0]
        df.at[i, 'course_type'] = parsed_response[1]
        df.at[i, 'dietary_classification'] = parsed_response[2]

print(df.head())  

df.to_csv('./data/Recipes.csv', index=False) 
