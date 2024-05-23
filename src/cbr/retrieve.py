import os
import random
from pathlib import Path

import numpy as np
from cbr.case_library import CaseLibrary, ConstraintQueryBuilder

random.seed(10)
sim_weights={"dp_match":1,"ct_match":0.85,"cuisine_match":0.65,"ingr_name_match":0.5,"ingr_basic_taste_match":0.5,"ingr_food_cat_match":0.5}
#CASELIBRARYPATH = os.path.join(os.path.dirname(__file__), '../data/case_library.xml')
CASELIBRARYPATH = r'C:\Users\AFEK\Downloads\CBR 2024\Case-Based-Reasoning-System-Prototyp\data\case_library.xml'
cl=CaseLibrary(CASELIBRARYPATH)

def search_ingredient(cl, name=None, basic_taste=None, food_category=None):
    """Search for an ingredient based on its name, basic taste, or food category."""
    if name:
        return random.choice(cl.root.xpath(f".//ingredient[name='{name}']"))
    if basic_taste:
        return random.choice(cl.root.xpath(f".//ingredient[@basic_taste='{basic_taste}']"))
    if food_category:
        return random.choice(cl.root.xpath(f".//ingredient[@food_category='{food_category}']"))
    return None

def similarity_recipe(cl, constraints, recipe):
    """
    Calculate similarity between a set of constraints and a particular recipe.
    Start with similarity 0, then each constraint is evaluated one by one and increase.
    The similarity is according to the feature weight.

    Parameters
    ----------
    cl : CaseLibrary
    constraints : dict of dictionaries
        Dictionary containing a set of constraints. Each constraint is a dictionary with keys 'include' and 'exclude' and values passed as lists.
    recipe : CookingRecipe object

    Returns
    -------
    float:
        normalized similarity
    """
    sim = 0
    cumulative_norm_score = 0
    recipe_ingredients=recipe.ingredients
    recipe_cuisine=recipe.cuisine
    recipe_course_type=recipe.course_type
    recipe_dietary_preference=recipe.dietary_preference
    

    for key in constraints:
        if key == "dietary_preference":
            for dp_constraint in constraints[key]['include']:
                if recipe_dietary_preference==dp_constraint:
                    sim += sim_weights["dp_match"]
                    cumulative_norm_score += sim_weights["dp_match"]
                else :
                    # In case the constraint is not fulfilled we add the weight to the normalization score
                    cumulative_norm_score += sim_weights["dp_match"]
            for dp_constraint in constraints[key]['exclude']:
                if recipe_dietary_preference!=dp_constraint:
                    sim += sim_weights["dp_match"]
                    cumulative_norm_score += sim_weights["dp_match"]
                else :
                    # In case the constraint is not fulfilled we add the weight to the normalization score
                    cumulative_norm_score += sim_weights["dp_match"]
        if key == "course_type":
            for ct_constraint in constraints[key]['include']:
                if recipe_course_type==value:
                    sim += sim_weights["ct_match"]
                    cumulative_norm_score += sim_weights["ct_match"]
                else :
                        # In case the constraint is not fulfilled we add the weight to the normalization score
                        cumulative_norm_score += sim_weights["ct_match"]
            for ct_constraint in constraints[key['exclude']]:
                    if recipe_course_type!=ct_constraint:
                        sim += sim_weights["ct_match"]
                        cumulative_norm_score += sim_weights["ct_match"]
                    else :
                        # In case the constraint is not fulfilled we add the weight to the normalization score
                        cumulative_norm_score += sim_weights["ct_match"]
        if key == "cuisine":
            for cuisine_constraint in constraints[key]['include']:
                if recipe_cuisine==cuisine_constraint:
                    sim += sim_weights["cuisine_match"]
                    cumulative_norm_score += sim_weights["cuisine_match"]
                else :
                    # In case the constraint is not fulfilled we add the weight to the normalization score
                    cumulative_norm_score += sim_weights["cuisine_match"]
            for cuisine_constraint in constraints[key]['exclude']:
                    if recipe_cuisine!=cuisine_constraint:
                        sim += sim_weights["cuisine_match"]
                        cumulative_norm_score += sim_weights["cuisine_match"]
                    else :
                        # In case the constraint is not fulfilled we add the weight to the normalization score
                        cumulative_norm_score += sim_weights["cuisine_match"]
        if key == "ingredients":
            for constraint_ingr in constraints[key]:
                constraint_name = constraint_ingr.get('name')
                constraint_basic_taste = constraint_ingr.get('basic_taste')
                constraint_food_category = constraint_ingr.get('food_category')
                # Parse the constraint string to extract attribute, value, and inclusion/exclusion
                attr, op, value = constraint_ingr.partition("!=" if "!=" in constraint_ingr else "=")
                is_inclusion = op == "="

                for recipe_ingr in recipe_ingredients:
                    if is_inclusion:
                        if recipe_ingr['name'] == constraint_name: 
                            sim += sim_weights["ingr_match"]
                            cumulative_norm_score += sim_weights["ingr_match"]
                        elif recipe_ingr['basic_taste'] == constraint_basic_taste:
                            sim += sim_weights["basic_taste_match"]
                            cumulative_norm_score += sim_weights["ingr_match"]
                        elif recipe_ingr['food_category'] == constraint_food_category:
                            sim += cl.sim_weights["food_category_match"]
                            cumulative_norm_score += sim_weights["ingr_match"]
                        else:
                            cumulative_norm_score += sim_weights["ingr_match"]
                    else:
                         if recipe_ingr['name'] != constraint_name: 
                            sim += sim_weights["ingr_match"]
                            cumulative_norm_score += sim_weights["ingr_match"]
                         elif recipe_ingr['basic_taste'] != constraint_basic_taste:
                            sim += sim_weights["basic_taste_match"]
                            cumulative_norm_score += sim_weights["ingr_match"]
                         elif recipe_ingr['food_category'] != constraint_food_category:
                            sim += sim_weights["food_category_match"]
                            cumulative_norm_score += sim_weights["ingr_match"]
                         else:
                            cumulative_norm_score += sim_weights["ingr_match"]

    normalized_sim = sim / cumulative_norm_score if cumulative_norm_score else 1.0
    return normalized_sim * float(recipe.find("utility").text)

def retrieve(constraints, cl):
    query_builder = ConstraintQueryBuilder()
    
    # Add constraints from the query
    if "dietary_preference" in constraints:
        query_builder.add_dietary_preference_constraint(include=constraints['dietary_preference']['include'],exclude=constraints['dietary_preference']['include'])
    if "course_type" in constraints:
        query_builder.add_course_type_constraint(include=constraints['course_type']['include'],exclude=constraints['course_type']['exclude'])
    if "cuisine" in constraints:
        query_builder.add_cuisine_constraint(include=constraints["cuisine"]['include'],exclude=constraints["cuisine"]['exclude'])
    if "ingredients" in constraints:
        query_builder.add_ingredients_constraint(include=constraints['ingredients']['include'],exclude=constraints['ingredients']['exclude'])

    xpath_query = query_builder.build()
    list_recipes = cl.find_recipes_by_constraint_query(xpath_query)
    relaxed_constraints=constraints
    while len(list_recipes)<5:
        #we start by removing include ingredients constraints if they are specified
        if  relaxed_constraints['ingredients']['include']:
            for i in range (len(relaxed_constraints['ingredients']['include'])):
                # we start by relaxing the food category constraint
                if relaxed_constraints['ingredients']['include'][i]['food_category']:
                    relaxed_constraints['ingredients']['include'][i]['food_category']=''
                #then we remove the basic taste constraint
                elif relaxed_constraints['ingredients']['include'][i]['basic_taste']:
                    relaxed_constraints['ingredients']['include'][i]['basic_taste']=''
                #then we remove the ingredient
                else:
                    relaxed_constraints['ingredients']['include'].pop(i)
        #next we remove the exclude ingredients constraints if they are specified 
        elif relaxed_constraints['ingredients']['exclude']:
            for i in range (len(relaxed_constraints['ingredients']['exclude'])):
                if relaxed_constraints['ingredients']['exclude'][i]['food_category']:
                    relaxed_constraints['ingredients']['exclude'][i]['food_category']=''
                elif relaxed_constraints['ingredients']['exclude'][i]['basic_taste']:
                    relaxed_constraints['ingredients']['exclude'][i]['basic_taste']=''
                else:
                    relaxed_constraints['ingredients']['include'].pop(i)
        elif relaxed_constraints['cuisine']['include']:
            relaxed_constraints['cuisine']['include']=[]
        elif relaxed_constraints['cuisine']['exclude']:
            relaxed_constraints['cuisine']['exclude']
        #probably this case won't happen but just in case
        elif relaxed_constraints['course_type']['include']:
            relaxed_constraints['course_type']['include']=[]
        elif relaxed_constraints['course_type']['exclude']:
            relaxed_constraints['course_type']['exclude']=[]
        query_builder = ConstraintQueryBuilder()
        # Add constraints from the query
        if "dietary_preference" in constraints:
            query_builder.add_dietary_preference_constraint(include=relaxed_constraints['dietary_preference']['include'],exclude=relaxed_constraints['dietary_preference']['include'])
        if "course_type" in constraints:
            query_builder.add_course_type_constraint(include=relaxed_constraints['course_type']['include'],exclude=relaxed_constraints['course_type']['exclude'])
        if "cuisine" in constraints:
            query_builder.add_cuisine_constraint(include=relaxed_constraints["cuisine"]['include'],exclude=relaxed_constraints["cuisine"]['exclude'])
        if "ingredients" in constraints:
            query_builder.add_ingredients_constraint(include=relaxed_constraints["ingredients"]['include'],exclude=relaxed_constraints['ingredients']['exclude'])
        xpath_query = query_builder.build()
        list_recipes = cl.find_recipes_by_constraint_query(xpath_query)
   
    sim_list = [similarity_recipe(cl, constraints, rec) for rec in list_recipes]
    max_indices = np.argwhere(np.array(sim_list) == np.amax(np.array(sim_list))).flatten().tolist()
    index_retrieved = random.choice(max_indices) if len(max_indices) > 1 else max_indices[0]

    retrieved_case = list_recipes[index_retrieved]
    return list_recipes, sim_list, index_retrieved, retrieved_case
