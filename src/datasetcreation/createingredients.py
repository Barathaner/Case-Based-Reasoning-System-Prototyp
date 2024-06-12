import pandas as pd
from src.utils import openairequests
import ast


"""_summary_:
    This was only used to add the categories to the dataset. which were missing. The Dataset ReciNLG can be found on kaggle but because it is 2GB we did not upload it
    We called it dataset random because we capped it to 500 examples.
    """

df = pd.read_csv('./data/RecipeNLG_dataset_random.csv')

ingredients_df = pd.DataFrame(columns=['Recipe Name', 'Ingredient', 'Amount', 'Unit', 'Basic Taste','food category'])

for i in range(df.shape[0]):
    title = str(df.iloc[i]['title'])
    ingredients = str(df.iloc[i]['ingredients'])
    response = openairequests.evaluate_prompt(f"recipename: {title} ingredients in the recipe:{ingredients}")
    print(response)
    parsed_entries =ast.literal_eval(response)
    print(parsed_entries)

    for entry in parsed_entries:
        ingredients_df = pd.concat([ingredients_df, pd.DataFrame([entry], columns=ingredients_df.columns)], ignore_index=True)

    ingredients_df.to_csv('./data/RecipeNLG_ingredients_dataset.csv', index=False) 

print(ingredients_df.head())  

ingredients_df.to_csv('./data/RecipeNLG_ingredients_dataset.csv', index=False)  
