import copy
import os
import random
from pathlib import Path

random.seed(10)


def subsumed(a, b):
    return a in b


def search_ingredient(cl, ingr_text=None, basic_taste=None, food_category=None):
    if ingr_text:
        return random.choice(cl.findall(f".//ingredient[.='{ingr_text}']"))
    if basic_taste:
        return random.choice(cl.findall(f".//ingredient[@basic_taste='{basic_taste}']"))
    if food_category:
        return random.choice(cl.findall(f".//ingredient[@food_category='{food_category}']"))
    else:
        return

def adapt_cat_and_tastes(cl, exc_ingrs, recipe, recipes, food_category="", basic_taste=""):
    for rec in recipes[1:]:
        similar_ingrs = [
            ingr for ingr in rec.ingredients
            if ingr["basic_taste"] == basic_taste and ingr["food_category"] == food_category
        ]
        for si in similar_ingrs:
            if not subsumed(si, exc_ingrs):
                include_ingredient(si, recipe, si.get("measure", "some"))
                return
    while True:
        similar_ingr = search_ingredient(cl, basic_taste=basic_taste, food_category=food_category)
        if not subsumed(similar_ingr, exc_ingrs):
            include_ingredient(similar_ingr, recipe)
            return


def include_ingredient(ingr, recipe, measure="some"):
    recipe.ingredients.append(ingr)
    step = f"add {ingr} and mix well" if measure == "some" else f"add {measure} of {ingr}"
    recipe.instructions.insert(1, step)


def replace_ingredient(ingr1, ingr2):
    if ingr1 != ingr2 and subsumed(ingr1["basic_taste"], ingr2["basic_taste"]) and subsumed(
            ingr1["food_category"], ingr2["food_category"]
    ):
        ingr1 = ingr2
        return True
    return False


def count_ingr_ids(step):
    return step.count("ingr")


def delete_ingredient(ingr_text, recipe):
    if ingr_text in recipe.ingredients:
        recipe.ingredients.remove(ingr_text)
        for step in recipe.instructions:
            if ingr_text in step:
                if count_ingr_ids(step) > 1:
                    recipe.instructions.remove(step.replace(ingr_text, "[IGNORE]"))
                else:
                    recipe.instructions.remove(step)
        return


def exclude_ingredient(exc_ingr_text, recipe, inc_ingrs, recipes):
    for inc_ingr in inc_ingrs:
        if replace_ingredient(exc_ingr_text, inc_ingr):
            return
    for rec in recipes[1:]:
        for ingr in rec.ingredients:
            if replace_ingredient(exc_ingr_text, ingr):
                return
    for _ in range(20):
        similar_ingr = search_ingredient(
            basic_taste=exc_ingr_text["basic_taste"], food_category=exc_ingr_text["food_category"]
        )
        if similar_ingr is None:
            delete_ingredient(exc_ingr_text, recipe)
            return
        if exc_ingr_text != similar_ingr:
            exc_ingr_text = similar_ingr
            return
    delete_ingredient(exc_ingr_text, recipe)


def update_ingr_list(recipe):
    food_categories = set()
    basic_tastes = set()
    ingredients = set()
    for ing in recipe.ingredients:
        for key, value in ing.items():
            if key == 'food_category' and value:
                food_categories.add(value)
            elif key == 'basic_taste' and value:
                basic_tastes.add(value)
            elif key == 'name' and value:
                ingredients.add(value)
    return food_categories, basic_tastes, ingredients



def adapt(cl, query, recipes):
    recipe = copy.deepcopy(recipes[0])
    food_categories, basic_tastes, ingredients = update_ingr_list(recipe)

    for exc_ingr_text in query["ingredients"]["exclude"]:
        if exc_ingr_text is not None:
            delete_ingredient(exc_ingr_text, recipe)

    food_categories, basic_tastes, ingredients = update_ingr_list(recipe)

    for ingr_text in query["ingredients"]["include"]:
        ingr = search_ingredient(cl, ingr_text)
        if ingr is not None and ingr not in ingredients and (
                measure := search_ingr_measure(ingr_text, recipes[1:])):
            include_ingredient(ingr, recipe, measure)
        elif ingr is not None and ingr not in ingredients:
            include_ingredient(ingr, recipe)

    food_categories, basic_tastes, ingredients = update_ingr_list(recipe)

    for food_category in query["food_category"]:
        if food_category not in food_categories:
            adapt_cat_and_tastes(cl, query["ingredients"]["exclude"], recipe, recipes, food_category=food_category)

    for basic_taste in query["basic_taste"]:
        if basic_taste not in basic_tastes:
            adapt_cat_and_tastes(cl, query["ingredients"]["exclude"], recipe, recipes, basic_taste=basic_taste)

    return recipe


def search_ingr_measure(ingr_text, recipes):
    for rec in recipes:
        for ingr in rec.ingredients:
            if ingr["name"] == ingr_text:
                return ingr.get("measure")
    return None


"""
if __name__ == "__main__":
    data_folder = os.path.join(Path(os.path.dirname(__file__)).parent.parent, "data")
    CASE_LIBRARY_PATH = os.path.join(data_folder, "case_library.xml")

    constraints = {
        "dietary_preference": [],
        "course_type": {'include': ['dessert'], 'exclude': ['side']},
        "cuisine": {'exclude': ['french'], 'include': ['italian', 'thai']},
        "ingredients": {'include': ['egg'], 'exclude': ['flour']}
    }

    query = {
        "ingredients": {'include': ['egg'], 'exclude': ['flour']},
        "food_category": ["sweetener", "fruit"],
        "basic_taste": ["umami", "spicy"]
    }

    CONSTRAINT = ConstraintQueryBuilder()
    CASE_LIBRARY = CaseLibrary(CASE_LIBRARY_PATH)

    # Retrieve random recipes based on constraints
    recipes = random.choices(CASE_LIBRARY.findall(CONSTRAINT.build()), k=5)

    # Displaying the ingredients and steps of the original recipe
    print(f"Ingredients before: {recipes[0].ingredients}")
    print("Steps before:")
    for step in recipes[0].instructions:
        step_text = step
        if step_text is not None:
            step_text = step_text.replace("\n", "")
        print(step_text)

    # Adapt the recipe based on the query
    output = adapt(query, recipes)
    print("--------------------")

    # Displaying the adapted ingredients and steps
    print(f"Ingredients after: {output.ingredients}")
    print("Steps after:")
    for step in output.instructions:
        step_text = step
        if step_text is not None:
            step_text = step_text.replace("\n", "")
        print(step_text)

    print("Done")
    """