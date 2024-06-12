import re
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.', '..')))
from src.cbr.cbr import CBR
from cbr.query import Query

query = Query()
cbr = CBR()

def all_inputs_exist(elements, possible_values):
    for element in elements:
        if element not in possible_values:
            print(f'-- Error. "{element}" is not in the library. Another value must be specified.')
            return False
    return True

def score_is_valid(score):
    try:
        score = float(score)
        if 0 <= score <= 10:
            return True
        else:
            print("-- Error. The score must be between 0 and 10.")
            return False
    except ValueError:
        print("-- Error. The score must be a float.")
        return False

print("- Welcome to CBR Cooking Recipe.")
print('- Please, enter the name of the recipe and your preferences.\n')

messages = [
    "- Type of course type (include): ",
    "- Type of course type (exclude): ",
    "- Type of dietary preference (include): ",
    "- Type of dietary preference (exclude): ",
    "- Type of cuisine (include): ",
    "- Type of cuisine (exclude): ",
    "- Ingredients to include (name): ",
    "- Ingredients to exclude (name): ",
    "- Ingredients to include (food category): ",
    "- Ingredients to exclude (food category): ",
    "- Ingredients to include (basic taste): ",
    "- Ingredients to exclude (basic taste): "
]

actions = [
    lambda x: query.set_course_type(x, exclude=False),
    lambda x: query.set_course_type(x, exclude=True),
    lambda x: query.set_dietary_preference(x, exclude=False),
    lambda x: query.set_dietary_preference(x, exclude=True),
    lambda x: query.set_cuisine(x, exclude=False),
    lambda x: query.set_cuisine(x, exclude=True),
    lambda x: query.set_ingredients(x, category="name", exclude=False),
    lambda x: query.set_ingredients(x, category="name", exclude=True),
    lambda x: query.set_ingredients(x, category="food_category", exclude=False),
    lambda x: query.set_ingredients(x, category="food_category", exclude=True),
    lambda x: query.set_ingredients(x, category="basic_taste", exclude=False),
    lambda x: query.set_ingredients(x, category="basic_taste", exclude=True)
]

suggestion_pools = [
    list(map(str, cbr.case_library.course_types)),
    list(map(str, cbr.case_library.course_types)),
    list(map(str, cbr.case_library.dietary_preferences_types)),
    list(map(str, cbr.case_library.dietary_preferences_types)),
    list(map(str, cbr.case_library.cuisines_types)),
    list(map(str, cbr.case_library.cuisines_types)),
    list(map(str, cbr.case_library.ingredients)),
    list(map(str, cbr.case_library.ingredients)),
    list(map(str, cbr.case_library.food_categories_types)),
    list(map(str, cbr.case_library.food_categories_types)),
    list(map(str, cbr.case_library.basic_tastes_types)),
    list(map(str, cbr.case_library.basic_tastes_types))
]


while True:
    recipe_name = input("- Name of the recipe: ")
    if recipe_name:
        break
    else:
        print("-- Error. A name must be specified.")

for message, action, suggestion_pool in zip(messages, actions, suggestion_pools):
    print("")
    while True:
        print(suggestion_pool)
        x = list(set(filter(None, re.sub(" +", " ", input(message)).split(", "))))
        if not x:
            break
        elif action == query.set_ingredients:
            if any(map(lambda i: i in x, query.get_ingredients())):
                print("-- Error. Ingredients to exclude cannot be present in the ingredients to include list.")
            elif all_inputs_exist(x, suggestion_pool):
                action(x)
                break
        else:
            if all_inputs_exist(x, suggestion_pool):
                action(x)
                break



retrieved_case, adapted_case = cbr.run_query(query, recipe_name)

print("\n- Here is the retrieved recipe:")
print(retrieved_case)
print("\n- Here is the adapted recipe:")
print(adapted_case)

while True:
    score = input("- Evaluate this recipe with a score from 1 to 10 (e.g.: 7.5): ")
    if score_is_valid(score):
        score = float(score)
        cbr.evaluate(score / 10)
        break

print("\n- Evaluation sent.")
print("- Done.")
