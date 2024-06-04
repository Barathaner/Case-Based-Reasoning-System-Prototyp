from datasetcreation.create_case_library import create_case_library
from cbr.case_library import CaseLibrary, CookingRecipe,ConstraintQueryBuilder,parse_recipe_from_xml
from cbr.retrieve import *
import os
from cbr.adaptation import *


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
        #for recipe in recipes:
                #print(recipe)
        print("---------------retrieve case---------------")
        print(retrieved_case)
        print("Done") 
        #{'include': [{'name':'butter or margarine ','food_category':None,'basic_taste':None}], 'exclude':[]}
        




        print("---------------adapted case---------------")
        query = {
        "ingredients": {'include':['egg'],'exclude':['flour']},
        "food_category": ["sweetener", "fruit"],
        "basic_taste": ["umami", "spicy"]
        }
        CONSTRAINT = ConstraintQueryBuilder()
        CASE_LIBRARY = CaseLibrary(CASELIBRARYPATH)

        query["ingredients"]["include"] = [search_ingredient(cl, ingr) for ingr in query["ingredients"]["include"]]
        #recipes = random.choices(cl.findall(CONSTRAINT), k=5)

        # Displaying the ingredients and steps of the original recipe
        #print(f"Ingredients before: {[e.text for e in recipes[0].ingredients]}")
        print("Ingredients before:")
        for e in recipes[0].ingredients:
                print(e["name"])
        print("Steps before:")
        print(recipes[0].instructions)
        """
        for step in recipes[0].instructions:
                step_text = step
                if step_text is not None:
                        step_text = step_text.replace("\n", "")
                print(step_text)
        """

        # Adapt the recipe based on the query
        adapted_recipe = adapt(cl, query, recipes)
        print("--------------------")

        # Displaying the adapted ingredients and steps
        #print(f"Ingredients after: {[e.text for e in adapted_recipe.ingredients]}")
        print("Ingredients after:")
        for e in adapted_recipe.ingredients:
                for key, value in e.items():
                        if key=="name":
                                print(value)
        print("Steps after:")
        print(adapted_recipe.instructions)

        adapted_recipe = CookingRecipe(
                name="New recipe",
                course_type=recipes[0].course_type,
                dietary_preference=recipes[0].dietary_preference,
                cuisine=recipes[0].cuisine,
                ingredients=adapted_recipe.ingredients,
                instructions=adapted_recipe.instructions,
                utility=1.0,
                derivation="Adapted",
                evaluation=None,
                UaS=0,
                UaF=0,
                failure_count=0,
                success_count=0
        )
        print(adapted_recipe)

        """
        for step in output.instructions:
                step_text = step
                if step_text is not None:
                        step_text = step_text.replace("\n", "")
                print(step_text)
        """

        print("Done")
