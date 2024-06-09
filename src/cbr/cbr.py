import os
import random
import numpy as np
import copy
from cbr.case_library import *


def subsumed(a, b):
    return a in b

CASE_LIBRARY_PATH = os.path.join(os.path.dirname(__file__), '../../data/case_library.xml')

class CBR:
    def __init__(self, case_library_file=None, seed=None):
        self.UTILITY_THRESHOLD = 0.8
        self.EVALUATION_THRESHOLD = 0.6
        if case_library_file is not None:
            self.case_library = CaseLibrary(case_library_file)
        else:
            self.case_library = CaseLibrary(CASE_LIBRARY_PATH)
        self.food_category = set()
        self.basic_tastes = set()
        self.ingredients = set()
        self.query = None
        self.retrieved_recipe = None
        self.sim_recipes = []
        self.adapted_recipe = None
        self.sim_weights = {
            "dp_match": 1,
            "ct_match": 0.85,
            "cuisine_match": 0.65,
            "ingr_match": 0.5,
            "ingr_name_match": 0.5,
            "ingr_basic_taste_match": 0.5,
            "ingr_food_cat_match": 0.5
        }


        if seed is not None:
            random.seed(seed)
    
    def run_query(self, query, new_name):
        self.query = copy.deepcopy(query)
        self.retrieve(query)
        self.adapt(new_name)
        print(f"Similarity of the adapted case: {self._similarity_cocktail(self.adapted_recipe)}")
        retrieved_case = CookingRecipe().from_element(self.retrieved_recipe)
        adapted_case = CookingRecipe().from_element(self.adapted_recipe)
        return retrieved_case, adapted_case
    

    #########################################
    # Retrieve
    def update_sim1(self, sim, cumulative_norm_score, key, constraints, attribute, w):
        if (len(constraints[key]['exclude']) > 0) or len(constraints[key]['include']) > 0:
            if (len(constraints[key]['include']) > 0) and attribute in constraints[key]['include']:
                sim += self.sim_weights[w]
                cumulative_norm_score += self.sim_weights[w]
            elif (len(constraints[key]['exclude']) > 0) and attribute in constraints[key]['exclude']:
                sim -= self.sim_weights[w]
                cumulative_norm_score += self.sim_weights[w]
        else:
            sim += self.sim_weights[w]
            cumulative_norm_score += self.sim_weights[w]

    def update_sim2(self, sim, cumulative_norm_score, constraints, attribute, w, ingredient):
        if (len(constraints['ingredients']['include'][attribute]) > 0) and ingredient[attribute] in constraints['ingredients']['include'][attribute]:
            sim += self.sim_weights[w]
        elif (len(constraints['ingredients']['exclude'][attribute]) > 0) and ingredient[attribute] in constraints['ingredients']['exclude'][attribute]:
            sim -= self.sim_weights[w]
        # In case the constraint is not fulfilled we add the weight to the normalization score
        cumulative_norm_score += self.sim_weights[w]

    def similarity_recipe(self, constraints, recipe):
        """
        Calculate similarity between a set of constraints and a particular recipe.
        Start with similarity 0, then each constraint is evaluated one by one 
        and increase or decrease the similarity score according to the feature weight.

        Parameters
        ----------
        constraints : dict of dictionaries
            Dictionary containing a set of constraints. 
            Each constraint is a dictionary with keys 'include' and 'exclude' and values passed as lists.
        recipe : CookingRecipe object

        Returns
        -------
        float:
            normalized similarity
        """
        sim = 0
        cumulative_norm_score = 0
        recipe_ingredients = recipe.ingredients
        recipe_cuisine = recipe.cuisine
        recipe_course_type = recipe.course_type
        recipe_dietary_preference = recipe.dietary_preference

        for key in constraints:
            if key == "dietary_preference":
                self.update_sim1(sim, cumulative_norm_score, key, constraints, recipe_dietary_preference, 'dp_match')      
            if key == "course_type":
                self.update_sim1(sim, cumulative_norm_score, key, constraints, recipe_course_type, 'ct_match')
            if key == "cuisine":
                self.update_sim1(sim, cumulative_norm_score, key, constraints, recipe_cuisine, 'cuisine_match')
            if key == "ingredients":
                if (len(constraints[key]['include']['name']) > 0) or (len(constraints[key]['exclude']['name']) > 0):
                    for ingredient in recipe_ingredients:
                        self.update_sim2(sim, cumulative_norm_score, constraints, 'name', 'ingr_name_match', ingredient)
                if len(constraints[key]['include']['basic_taste']) > 0 or len(constraints[key]['exclude']['basic_taste']) > 0:
                    for ingredient in recipe_ingredients:
                        self.update_sim2(sim, cumulative_norm_score, constraints, 'basic_taste', 'ingr_basic_taste_match', ingredient)
                if len(constraints[key]['include']['food_category']) > 0 or len(constraints[key]['exclude']['food_category']) > 0:
                    for ingredient in recipe_ingredients:
                        self.update_sim2(sim, cumulative_norm_score, constraints, 'food_category', 'ingr_food_cat_match', ingredient)
                else:  
                    sim += self.sim_weights["ingr_match"]
                    cumulative_norm_score += self.sim_weights["ingr_match"]     

        normalized_sim = sim / cumulative_norm_score if cumulative_norm_score else 1.0
        return normalized_sim * float(recipe.utility)

    def retrieve(self, query):
        constraints = query.get_data()

        CQB = ConstraintQueryBuilder()

        # Add constraints from the query
        CQB.add_dietary_preference_constraint(include=constraints['dietary_preference']['include'], exclude=constraints['dietary_preference']['exclude'])
        CQB.add_course_type_constraint(include=constraints['course_type']['include'], exclude=constraints['course_type']['exclude'])
        CQB.add_cuisine_constraint(include=constraints["cuisine"]['include'], exclude=constraints["cuisine"]['exclude'])
        CQB.add_ingredients_constraint(include=constraints['ingredients']['include'], exclude=constraints['ingredients']['exclude'])

        xpath_query = CQB.build()
        list_recipes = self.case_library.find_recipes_by_constraint_query(xpath_query)
        relaxed_constraints = constraints.copy()

        while len(list_recipes) < 5:
            # We start by removing include ingredients constraints if they are specified
            if any(len(relaxed_constraints['ingredients']['include'][attr]) > 0 for attr in relaxed_constraints['ingredients']['include']):
                # We start by relaxing the food category constraints
                if len(relaxed_constraints['ingredients']['include']['food_category']) > 0:
                    relaxed_constraints['ingredients']['include']['food_category'] = []
                # Then we remove the basic taste constraints
                elif len(relaxed_constraints['ingredients']['include']['basic_taste']) > 0:
                    relaxed_constraints['ingredients']['include']['basic_taste'] = []
                # Then we remove the ingredient name constraints
                elif len(relaxed_constraints['ingredients']['include']['name']) > 0:
                    relaxed_constraints['ingredients']['include']['name'] = []
            # Next we remove the exclude ingredients constraints if they are specified 
            elif any(len(relaxed_constraints['ingredients']['exclude'][attr]) > 0 for attr in relaxed_constraints['ingredients']['exclude']):
                if len(relaxed_constraints['ingredients']['exclude']['food_category']) > 0:
                    relaxed_constraints['ingredients']['exclude']['food_category'] = []
                elif len(relaxed_constraints['ingredients']['exclude']['basic_taste']) > 0:
                    relaxed_constraints['ingredients']['exclude']['basic_taste'] = []
                elif len(relaxed_constraints['ingredients']['exclude']['name']) > 0:
                    relaxed_constraints['ingredients']['exclude']['name'] = []
            # Next we remove the cuisine constraints if they are specified
            elif len(relaxed_constraints['cuisine']['include']) > 0:
                relaxed_constraints['cuisine']['include'] = []
            elif len(relaxed_constraints['cuisine']['exclude']) > 0:
                relaxed_constraints['cuisine']['exclude'] = []
            # Probably this won't happen but just in case
            elif len(relaxed_constraints['course_type']['include']) > 0:
                relaxed_constraints['course_type']['include'] = []
            elif len(relaxed_constraints['course_type']['exclude']) > 0:
                relaxed_constraints['course_type']['exclude'] = []
            
            CQB.reset()

            # Add constraints from the relaxed query
            CQB.add_dietary_preference_constraint(include=relaxed_constraints['dietary_preference']['include'], exclude=relaxed_constraints['dietary_preference']['exclude'])
            CQB.add_course_type_constraint(include=relaxed_constraints['course_type']['include'], exclude=relaxed_constraints['course_type']['exclude'])
            CQB.add_cuisine_constraint(include=relaxed_constraints['cuisine']['include'], exclude=relaxed_constraints['cuisine']['exclude'])
            CQB.add_ingredients_constraint(include=relaxed_constraints['ingredients']['include'], exclude=relaxed_constraints['ingredients']['exclude'])

            xpath_query = CQB.build()
            list_recipes = self.case_library.find_recipes_by_constraint_query(xpath_query) #TODO: check that instead of "=" i should be "append"


        
        
        if list_recipes:
            print(f"Found {len(list_recipes)} recipes")
            sim_list = [self.similarity_recipe(constraints, rec) for rec in list_recipes] #TODO: if the constraints are too restricted, error un similarity_recipe()
            max_indices = np.argwhere(np.array(sim_list) == np.amax(np.array(sim_list))).flatten().tolist()
            index_retrieved = random.choice(max_indices) if len(max_indices) > 1 else max_indices[0]

            self.retrieved_recipe = list_recipes[index_retrieved]
            self.sim_recipes = list_recipes[:4] # Return the top 4 most similar recipes. TODO: I think that the list_recipes should only be 5, according to the while. Check this.


            self.adapted_recipe = copy.deepcopy(self.retrieved_recipe)
            self.update_ingr_list()
            
            self.query.set_ingredients([self.search_ingredient(ingr) for ingr in self.query.get_ingredients()])

            
            
    def update_ingr_list(self):
        for ing in self.adapted_recipe.ingredients:
            for key, value in ing.items():
                if key == 'food_category' and value:
                    self.food_category.add(value)
                elif key == 'basic_taste' and value:
                    self.basic_tastes.add(value)
                elif key == 'name' and value:
                    self.ingredients.add(value)
    
    def search_ingredient(self, ingr_text=None, basic_taste=None, food_category=None):
        if ingr_text:
            ingr_name = self.case_library.findall(f".//ingredient[.='{ingr_text}']")
            if ingr_name:
                return random.choice(ingr_name)
        if basic_taste:
            ingr_basic_taste = self.case_library.findall(f".//ingredient[@basic_taste='{basic_taste}']")
            if ingr_basic_taste:
                return random.choice(ingr_basic_taste)
        if food_category:
            ingr_food_category = self.case_library.findall(f".//ingredient[@food_category='{food_category}']")
            if ingr_food_category:
                return random.choice(ingr_food_category)
        else:
            return

    def adapt(self, new_name):
        """
        Adapts the recipe according the user requirements
        by excluding ingredients and including other ingredients,
        alcohol types and basic tastes.

        Parameters
        ----------
        new_name : str
            The name for the adapted recipe.
        """
        self.adapted_recipe.name = new_name
        for exc_ingr in self.query.get_exc_ingredients():
            if exc_ingr in self.ingredients:
                exc_ingr = self.adapted_recipe.find(f"ingredients/ingredient[.='{exc_ingr}']")
                self.exclude_ingredient(exc_ingr)

        self.update_ingr_list()

        for ingr in self.query.get_ingredients():
            if ingr not in self.ingredients:
                ing_properties = self.case_library.get_ingredient_properties(ingr)
                self.include_ingredient(ingr, unit=ing_properties["unit"], basic_taste=ing_properties["basic_taste"], food_category=ing_properties["food_category"])
                

        self.update_ingr_list()

        for food_category in self.query.get_food_category():
            if food_category not in self.food_category:
                self.adapt_cat_and_tastes(food_category==food_category)

        for basic_taste in self.query.get_basic_taste():
            if basic_taste not in self.basic_tastes:
                self.adapt_cat_and_tastes(basic_taste=basic_taste)

    def replace_ingredient(self, ingr1, ingr2):
        if ingr1.text != ingr2.text:
            if (
                ingr1.attrib["basic_taste"] == ingr2.attrib["basic_taste"]
                and ingr1.attrib["food_category"] == ingr2.attrib["food_category"]
            ):
                ingr1._setText(ingr2.text)
                return True
        return False
    
    def exclude_ingredient(self, exc_ingr):
        if not exc_ingr.attrib["alc_type"]:
            for ingr in self.query.get_ingredients():
                if self.replace_ingredient(exc_ingr, ingr):
                    return
            for recipe in self.sim_recipes:
                for ingr in recipe.ingredients.iterchildren():
                    if self.replace_ingredient(exc_ingr, ingr):
                        return
            for _ in range(20):
                ingr = self._search_ingredient(
                    basic_taste=exc_ingr.attrib["basic_taste"], alc_type=exc_ingr.attrib["alc_type"]
                )
                if ingr is None:
                    self.delete_ingredient(exc_ingr)
                    return
                if exc_ingr.text != ingr.text:
                    exc_ingr._setText(ingr.text)
                    return
        self.delete_ingredient(exc_ingr)
        return
    
    
    def include_ingredient(self, ingr, measure="some", unit="g", basic_taste="general", food_category="general"):
        ingredient_format = {"name": "", "amount": "", "unit": "", "basic_taste": "", "food_category": ""}
        ingredient_format["name"] = ingr
        ingredient_format["amount"] = measure
        ingredient_format["unit"] = unit
        ingredient_format['basic_taste'] = basic_taste
        ingredient_format['food_category'] = food_category

        self.adapted_recipe.ingredients.append(ingredient_format)
        step = f"add {ingr} and mix well" if measure == "some" else f"add {measure} of {ingr}"
        self.adapted_recipe.instructions.insert(1, step)



    def adapt_cat_and_tastes(self, food_category="", basic_taste=""):
        exc_ingrs = self.query.get_exc_ingredients()
        for rec in self.sim_recipes:
            similar_ingrs = [
                ingr for ingr in rec.ingredients
                if ingr["basic_taste"] == basic_taste and ingr["food_category"] == food_category
            ]
            for si in similar_ingrs:
                print(si)
                if not subsumed(si, exc_ingrs):
                    ing_properties = self.case_library.get_ingredient_properties(si)
                    self.include_ingredient(si, measure=si.get("measure", "some"), unit=ing_properties["unit"], basic_taste=ing_properties["basic_taste"], food_category=ing_properties["food_category"])
                    return
        while True:
            similar_ingr = self.search_ingredient(basic_taste=basic_taste, food_category=food_category)
            if similar_ingr is None:
                return
            if not subsumed(similar_ingr, exc_ingrs) :
                ing_properties = self.case_library.get_ingredient_properties(similar_ingr)
                print(ing_properties)
                self.include_ingredient(similar_ingr, unit=ing_properties["unit"] ,basic_taste=ing_properties["basic_taste"], food_category=ing_properties["food_category"])
                return