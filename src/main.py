from datasetcreation.create_case_library import create_case_library
from cbr.case_library import CaseLibrary, CookingRecipe,ConstraintQueryBuilder,parse_recipe_from_xml
from cbr.retrieve import *
import os


CASELIBRARYPATH = os.path.join(os.path.dirname(__file__), '../data/case_library.xml')

cl=CaseLibrary(CASELIBRARYPATH)
constraints= {"dietary_preference": None,
"course_type": {'include':['dessert'],'exclude':['side']},
"ingredients": None,
"cuisine":{'exclude':['french'],'include':['italian','thai']}
}
ingredients = [
{'name': 'Flour', 'amount': 200, 'unit': 'g', 'basic_taste': 'neutral', 'food_category': 'grain'},
{'name': 'Sugar', 'amount': 100, 'unit': 'g', 'basic_taste': 'sweet', 'food_category': 'sweetener'}
]
instructions = [
"Mix dry ingredients.",
"Add water and stir until smooth.",
"Bake at 180 degrees Celsius for 20 minutes."
]

CASELIBRARYPATH = os.path.join(os.path.dirname(__file__), '../data/case_library.xml')


if __name__ == "__main__":
        #######################EXAMPLECODE####################
        #######################EXAMPLECODE####################
        #create a case library with default inputs which are the dataset in our project
        #create_case_library()

        cl.print_first_five_recipes()
        new_recipe = CookingRecipe("Vegan Cake", "dessert", "vegan", "American", ingredients, instructions,1.0,"original","success",0,0,0,0)

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
        #CaseLibrary.remove_recipe(cl, new_recipe)
        cl.remove_recipe(new_recipe)
        
        
        #######################EXAMPLECODE_______END_____####################
        #######################EXAMPLECODE_______END_____####################
        query_builder.reset()
        recipes, sim_list, index_retrieved, retrieved_case = retrieve( constraints, cl,query_builder)
        for recipe in recipes:
                print(recipe)
        print(retrieved_case)
        print("Done") 
        #{'include': [{'name':'butter or margarine ','food_category':None,'basic_taste':None}], 'exclude':[]}