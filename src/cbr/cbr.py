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
        self.EVALUATION_THRESHOLD = 6
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
        self.cumulative_norm_score=0
        self.sim=0
        self.adapted_recipe = None
        self.sim_weights = {
            "dp_match": 1.0,
            "ct_match": 0.85,
            "cuisine_match": 0.85,
            "ingr_match": 0.55,
            "ingr_name_match": 0.45,
            "ingr_basic_taste_match": 0.45,
            "ingr_food_cat_match": 0.45
        }


        if seed is not None:
            random.seed(seed)
    
    def run_query(self, query, new_name):
        self.query = copy.deepcopy(query)
        self.retrieve(query)
        self.adapt(new_name)
        print(f"Similarity of the adapted case: {self.similarity_recipe(self.adapted_recipe, self.query.get_data())}")
        return self.retrieved_recipe, self.adapted_recipe

    

    #########################################
    # Retrieve
    def update_sim1(self, sim, cumulative_norm_score, key, constraints, attribute, w):
            constrinclude=len(constraints[key]['include'])
            if (len(constraints[key]['exclude']) > 0) or (len(constraints[key]['include']) > 0):
                if (len(constraints[key]['include']) > 0) and attribute in constraints[key]['include']:
                    self.sim += self.sim_weights[w]
                    self.cumulative_norm_score += self.sim_weights[w]
                elif (len(constraints[key]['exclude']) > 0) and attribute in constraints[key]['exclude']:
                    self.sim -= self.sim_weights[w]
                    self.cumulative_norm_score += self.sim_weights[w]
                else:
                    self.cumulative_norm_score += self.sim_weights[w]

    def update_sim2(self, sim, cumulative_norm_score, constraints, attribute, w, ingredient):
        if (len(constraints['ingredients']['include'][attribute]) > 0) and ingredient[attribute] in constraints['ingredients']['include'][attribute]:
            self.sim += self.sim_weights[w]
            self.cumulative_norm_score += self.sim_weights[w]
        elif (len(constraints['ingredients']['exclude'][attribute]) > 0) and ingredient[attribute] in constraints['ingredients']['exclude'][attribute]:
            self.sim -= self.sim_weights[w]
            self.cumulative_norm_score += self.sim_weights[w]
        # In case the constraint is not fulfilled we add the weight to the normalization score
        self.cumulative_norm_score += self.sim_weights[w]

    def similarity_recipe(self, recipe, constraints):
        """
        Calculate similarity between a set of constraints and a particular recipe.
        Start with similarity 0, then each constraint is evaluated one by one 
        and increase or decrease the similarity score according to the feature weight.

        """
        self.sim = 0.0
        self.cumulative_norm_score = 0.0
        recipe_ingredients = recipe.ingredients
        recipe_cuisine = recipe.cuisine
        recipe_course_type = recipe.course_type
        recipe_dietary_preference = recipe.dietary_preference

        for key in constraints:
            if key == "dietary_preference":
                self.update_sim1(self.sim, self.cumulative_norm_score, key, constraints, recipe_dietary_preference, 'dp_match')      
            if key == "course_type":
                self.update_sim1(self.sim, self.cumulative_norm_score, key, constraints, recipe_course_type, 'ct_match')
            if key == "cuisine":
                self.update_sim1(self.sim, self.cumulative_norm_score, key, constraints, recipe_cuisine, 'cuisine_match')
            if key == "ingredients":
                if (len(constraints[key]['include']['name']) > 0) or (len(constraints[key]['exclude']['name']) > 0):
                    for ingredient in recipe_ingredients:
                        self.update_sim2(self.sim, self.cumulative_norm_score, constraints, 'name', 'ingr_name_match', ingredient)
                if (len(constraints[key]['include']['basic_taste']) > 0) or (len(constraints[key]['exclude']['basic_taste']) > 0):
                    for ingredient in recipe_ingredients:
                        self.update_sim2(self.sim, self.cumulative_norm_score, constraints, 'basic_taste', 'ingr_basic_taste_match', ingredient)
                if (len(constraints[key]['include']['food_category']) > 0) or (len(constraints[key]['exclude']['food_category']) > 0):
                    for ingredient in recipe_ingredients:
                        self.update_sim2(self.sim, self.cumulative_norm_score, constraints, 'food_category', 'ingr_food_cat_match', ingredient)
                else:  
                    self.sim += self.sim_weights["ingr_match"]
                    self.cumulative_norm_score += self.sim_weights["ingr_match"]     

        normalized_sim = self.sim / self.cumulative_norm_score if self.cumulative_norm_score else 1.0
        normalized_sim=normalized_sim * float(recipe.utility)

        self.sim = 0
        self.cumulative_norm_score = 0
        return normalized_sim

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
        relaxed_constraints = copy.deepcopy(constraints)

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
            list_recipes = self.case_library.find_recipes_by_constraint_query(xpath_query) 


        
        
        if list_recipes:
            sim_list = [self.similarity_recipe(rec,constraints) for rec in list_recipes]
            max_indices = np.argwhere(np.array(sim_list) == np.amax(np.array(sim_list))).flatten().tolist()
            index_retrieved = random.choice(max_indices) if len(max_indices) > 1 else max_indices[0]

            self.retrieved_recipe = list_recipes[index_retrieved]
            self.sim_recipes = list_recipes[:5] # Return the top 5 most similar recipes.


            self.adapted_recipe = copy.deepcopy(self.retrieved_recipe)
            self.update_ingr_list()
            ingredients = [self.search_ingredient(ingr) for ingr in self.query.get_ingredients()]
            self.query.set_ingredients(ingredients,"name")

            
            
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
        self.adapted_recipe.name = new_name
        for exc_ingr in self.query.get_exc_ingredients():
            if exc_ingr in self.ingredients:
                for rec_ingr in self.adapted_recipe.ingredients:
                    if rec_ingr['name'] == exc_ingr:
                        self.exclude_ingredient(rec_ingr)

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
        
        ingr2 = self.case_library.get_ingredient_properties(ingr2)
        if ingr1["name"] != ingr2["name"]:
            if (
                ingr1["basic_taste"] == ingr2["basic_taste"]
                and ingr1["food_category"] == ingr2["food_category"]
            ):
                self.delete_ingredient(ingr1)
                self.include_ingredient(ingr2["name"], unit=ingr2["unit"], basic_taste=ingr2["basic_taste"], food_category=ingr2["food_category"])
                return True
        return False
    
    def exclude_ingredient(self, exc_ingr):
        for ingr in self.query.get_ingredients():
            if self.replace_ingredient(exc_ingr, ingr):
                return
        for recipe in self.sim_recipes:
            for ingr in recipe.ingredients:
                if self.replace_ingredient(exc_ingr, ingr["name"]):
                    return
        for _ in range(20):
            ingr = self.search_ingredient(
                basic_taste=exc_ingr["basic_taste"], food_category=exc_ingr["food_category"]
            )
            ingr = self.case_library.get_ingredient_properties(ingr)
            if ingr is None:
                self.delete_ingredient(exc_ingr)
                return
            if exc_ingr["name"] != ingr["name"]:
                self.delete_ingredient(exc_ingr)
                self.include_ingredient(ingr["name"], unit=ingr["unit"], basic_taste=ingr["basic_taste"], food_category=ingr["food_category"])
                return
        self.delete_ingredient(exc_ingr)
        
    
    def delete_ingredient(self, ingr):
        self.adapted_recipe.ingredients.remove(ingr)
        for step in self.adapted_recipe.instructions:
            if ingr["name"] in step:
                    self.adapted_recipe.instructions.remove(step)

    
    
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
                self.include_ingredient(similar_ingr, unit=ing_properties["unit"] ,basic_taste=ing_properties["basic_taste"], food_category=ing_properties["food_category"])
                return

    @staticmethod
    def _compute_utility(case):
        return ((float(case.UaS) / (float(case.success_count) + 1e-5)) - (float(case.UaF) / (float(case.failure_count) + 1e-5)) + 1) / 2

    def forget_cases(self):
        for recipe in self.case_library.find_recipes_by_constraint_query(f".//cookingrecipe[utility < {self.UTILITY_THRESHOLD}]"):

            ingredient_constraints = []
            food_categories = [ingredient["food_category"] for ingredient in recipe.ingredients if "'" not in ingredient["food_category"]]
            basic_tastes = [ingredient["basic_taste"] for ingredient in recipe.ingredients if "'" not in ingredient["basic_taste"]]
            names = [ingredient["name"] for ingredient in recipe.ingredients if "'" not in ingredient["name"]]

            for food_category, basic_taste, name in zip(food_categories, basic_tastes, names):
                constraint = {"food_category": food_category, "basic_taste": basic_taste, "name": name}
                ingredient_constraints.append(constraint)

            query_builder = ConstraintQueryBuilder()
            query_builder.add_dietary_preference_constraint(include=[recipe.dietary_preference])
            query_builder.add_course_type_constraint(include=[recipe.course_type])
            query_builder.add_cuisine_constraint(include=[recipe.cuisine])
            query_builder.add_whole_ingredients_constraint(include=ingredient_constraints)

            query = query_builder.build()

            found_recipes = self.case_library.find_recipes_by_constraint_query(query)

            if len(found_recipes) > 1:
                self.case_library.remove_recipe(recipe)

    def learn(self):
        if self.adapted_recipe.evaluation == "success":
            self.case_library.add_recipe(self.adapted_recipe)
            self.forget_cases()
        self.case_library.save()

    def evaluate(self, user_score):
        if user_score > self.EVALUATION_THRESHOLD:
            for recipe in self.sim_recipes:
                self.adapted_recipe.evaluation = "success"
                if recipe.name == self.retrieved_recipe.name:
                    recipe.UaS = str(int(recipe.UaS) + 1)
                    recipe.success_count = str(int(recipe.success_count) + 1)
                    recipe.utility = str(self._compute_utility(recipe))
                else:
                    recipe.success_count = str(int(recipe.success_count) + 1)
                    recipe.utility = str(self._compute_utility(recipe))
                self.case_library.remove_recipe(recipe)
                self.case_library.add_recipe(recipe)
        else:
            self.adapted_recipe.evaluation = "failure"
            for recipe in self.sim_recipes:
                if recipe.name == self.retrieved_recipe.name:
                    recipe.UaF = str(int(recipe.UaF) + 1)
                    recipe.failure_count = str(int(recipe.failure_count) + 1)
                    recipe.utility = str(self._compute_utility(recipe))
                else:
                    recipe.failure_count = str(int(recipe.failure_count) + 1)
                    recipe.utility = str(self._compute_utility(recipe))
                self.case_library.remove_recipe(recipe)
                self.case_library.add_recipe(recipe)
        self.learn()
