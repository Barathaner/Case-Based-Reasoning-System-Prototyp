from datasetcreation.create_case_library import create_case_library
from cbr.case_library import CaseLibrary, CookingRecipe,ConstraintQueryBuilder
from cbr.retrieve import *
from utils.printutils import format_xmlrecipes_to_str
import os


CASELIBRARYPATH = os.path.join(os.path.dirname(__file__), '../data/case_library.xml')


if __name__ == "__main__":
    #create a case library with default inputs which are the dataset in our project
    #create_case_library()
    
    cl=CaseLibrary(CASELIBRARYPATH)
    cl.print_first_five_recipes()
    
    """         # Create a new recipe
    ingredients = [
        {'name': 'Flour', 'amount': 200, 'unit': 'g', 'basic_taste': 'neutral', 'food_category': 'grain'},
        {'name': 'Sugar', 'amount': 100, 'unit': 'g', 'basic_taste': 'sweet', 'food_category': 'sweetener'}
    ]
    instructions = [
        "Mix dry ingredients.",
        "Add water and stir until smooth.",
        "Bake at 180 degrees Celsius for 20 minutes."
    ]
    new_recipe = CookingRecipe("Vegan Cake", "dessert", "vegan", "American", ingredients, instructions)

    CaseLibrary.add_recipe(cl, new_recipe)
    # Create an instance of the query builder
    query_builder = ConstraintQueryBuilder()

    # Add constraints for various attributes
    query_builder.add_dietary_preference_constraint(include=['vegetarian'], exclude=[])
    query_builder.add_course_type_constraint(include=['main'])
    query_builder.add_cuisine_constraint(include=['thai'], exclude=[])

    # Build the query
    query = query_builder.build()
    print(query)  # Outputs the constructed XPath query


    #finds recipes as xml and parses them to cookingrecipe objects
    found_recipes = cl.find_recipes_by_constraint_query(query)
    for recipe in found_recipes:
        #prints the recipes formatted with the string format for the cookingrecipe object
        print(recipe) 
                """
    
    constraints= {
        "course_type": {'include':['side'],'exclude':[]},
        "ingredients": {'include': [{"name": "sea salt", "basic_taste": None, "food_category": }, 
                                    {"name": "garlic", "basic_taste": "pungent", "food_category": None}],'exclude':[]},
        "cuisine":{'exclude':['thai'],'include':[]}
    }
    query_builder = ConstraintQueryBuilder()
    query = query_builder.build()
    print(query)  # Outputs the constructed XPath query
    recipes, sim_list, index_retrieved, retrieved_case = retrieve( constraints, cl)

    i = len(recipes) - 1
    print(f"Similarity List: {i}")
    print(f"Category: {[e.text for e in recipes[i].findall('category')]}")
    print(f"Ingredients: {[e.text for e in recipes[i].findall('.//ingredients/ingredient')]}")
    print(f"Steps: {[e.text for e in recipes[i].findall('.//instructions/step')]}")
    print(f"Similarity List: {sim_list}")
    print(f"Index Max Similarity: {index_retrieved}")
    print(f"Category-Retrieved Case: {[e.text for e in retrieved_case.findall('category')]}")
    print(f"Ingredients-Retrieved Case: {[e.text for e in retrieved_case.findall('.//ingredients/ingredient')]}")
    print(f"Steps-Retrieved Case: {[e.text for e in retrieved_case.findall('.//instructions/step')]}")

    print("Done")

    #CaseLibrary.remove_recipe(cl, new_recipe)
    cl.remove_recipe(new_recipe)