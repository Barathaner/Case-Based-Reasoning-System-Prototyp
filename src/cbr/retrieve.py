import os
import random
from pathlib import Path

import numpy as np

random.seed(10)
sim_weights={"dp_match":1,"ct_match":0.85,"cuisine_match":0.65,"ingr_match":0.5,"ingr_name_match":0.5,"ingr_basic_taste_match":0.5,"ingr_food_cat_match":0.5}

def search_ingredient(cl, name=None, basic_taste=None, food_category=None):
    """Search for an ingredient based on its name, basic taste, or food category."""
    if name:
        return random.choice(cl.root.xpath(f".//ingredient[name='{name}']"))
    if basic_taste:
        return random.choice(cl.root.xpath(f".//ingredient[@basic_taste='{basic_taste}']"))
    if food_category:
        return random.choice(cl.root.xpath(f".//ingredient[@food_category='{food_category}']"))
    return None

def similarity_recipe(constraints, recipe):
    """
    Calculate similarity between a set of constraints and a particular recipe.
    Start with similarity 0, then each constraint is evaluated one by one and increase.
    The similarity is according to the feature weight.

    Parameters
    ----------
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
            if constraints[key] is not None:
                if recipe_dietary_preference in constraints[key]['include']:
                    sim += sim_weights["dp_match"]
                    cumulative_norm_score += sim_weights["dp_match"]
                elif recipe_dietary_preference in constraints[key]['exclude']:
                    sim -= sim_weights["dp_match"]
                    cumulative_norm_score += sim_weights["dp_match"]
                else:
                    # In case the constraint is not fulfilled we add the weight to the normalization score
                    cumulative_norm_score += sim_weights["dp_match"]
            else:
                sim += sim_weights["dp_match"]
                cumulative_norm_score += sim_weights["dp_match"]
              
        if key == "course_type":
            if constraints[key] is not None:
                if recipe_course_type in constraints[key]['include']:
                    sim += sim_weights["ct_match"]
                    cumulative_norm_score += sim_weights["ct_match"]
                elif recipe_course_type in constraints[key]['exclude']:
                    sim -= sim_weights["ct_match"]
                    cumulative_norm_score += sim_weights["ct_match"]
                else:
                    # In case the constraint is not fulfilled we add the weight to the normalization score
                    cumulative_norm_score += sim_weights["ct_match"]
            else: 
                sim += sim_weights["ct_match"]
                cumulative_norm_score += sim_weights["ct_match"]
        if key == "cuisine":
            if constraints[key] is not None:
                if recipe_cuisine in constraints[key]['include']:
                    sim += sim_weights["cuisine_match"]
                    cumulative_norm_score += sim_weights["cuisine_match"]
                elif recipe_cuisine in constraints[key]['exclude']:
                    sim -= sim_weights["cuisine_match"]
                    cumulative_norm_score += sim_weights["cuisine_match"]
                else:
                    # In case the constraint is not fulfilled we add the weight to the normalization score
                    cumulative_norm_score += sim_weights["cuisine_match"]
            else:
                sim += sim_weights["cuisine_match"]
                cumulative_norm_score += sim_weights["cuisine_match"]
        if key == "ingredients":
            if constraints[key] is not None:
                for recipe_ingr in recipe_ingredients:
                    if recipe_ingr['name'] in [ingr['name'] for ingr in constraints[key]['include']]:
                        sim += sim_weights["ingr_name_match"]
                        cumulative_norm_score += sim_weights["ingr_name_match"]
                    elif recipe_ingr['name'] in [ingr['name'] for ingr in constraints[key]['exclude']]:
                        sim -= sim_weights["ingr_name_match"]
                        cumulative_norm_score += sim_weights["ingr_name_match"]
                    else:
                        # In case the constraint is not fulfilled we add the weight to the normalization score
                        cumulative_norm_score += sim_weights["ingr_name_match"]
                    if recipe_ingr['basic_taste'] in [ingr['basic_taste'] for ingr in constraints[key]['include']]:
                        sim += sim_weights["ingr_basic_taste_match"]
                        cumulative_norm_score += sim_weights["ingr_basic_taste_match"]
                    elif recipe_ingr['basic_taste'] in [ingr['basic_taste'] for ingr in constraints[key]['exclude']]:
                        sim -= sim_weights["ingr_basic_taste_match"]
                        cumulative_norm_score += sim_weights["ingr_basic_taste_match"]
                    else:                 
                        cumulative_norm_score += sim_weights["ingr_basic_taste_match"]
                    if recipe_ingr['food_category'] in [ingr['food_category'] for ingr in constraints[key]['include']]:
                        sim += sim_weights["ingr_food_cat_match"]
                        cumulative_norm_score += sim_weights["ingr_food_cat_match"]
                    elif recipe_ingr['food_category'] in [ingr['food_category'] for ingr in constraints[key]['exclude']]:
                        sim -= sim_weights["ingr_food_cat_match"]
                        cumulative_norm_score += sim_weights["ingr_food_cat_match"]
                    else:
                        cumulative_norm_score += sim_weights["ingr_food_cat_match"]
            else:  
                sim += sim_weights["ingr_match"]
                cumulative_norm_score += sim_weights["ingr_match"]     

    normalized_sim = sim / cumulative_norm_score if cumulative_norm_score else 1.0
    return normalized_sim * float(recipe.utility)

def retrieve(constraints, cl,query_builder):
    
    # Add constraints from the query
    if constraints["dietary_preference"]:
        query_builder.add_dietary_preference_constraint(include=constraints['dietary_preference']['include'],exclude=constraints['dietary_preference']['include'])
    if constraints["course_type"]:
        query_builder.add_course_type_constraint(include=constraints['course_type']['include'],exclude=constraints['course_type']['exclude'])
    if constraints["cuisine"]:
        query_builder.add_cuisine_constraint(include=constraints["cuisine"]['include'],exclude=constraints["cuisine"]['exclude'])
    if constraints["ingredients"]:
        query_builder.add_ingredients_constraint(include=constraints['ingredients']['include'],exclude=constraints['ingredients']['exclude'])

    xpath_query = query_builder.build()
    list_recipes = cl.find_recipes_by_constraint_query(xpath_query)
    relaxed_constraints=constraints.copy()
    while len(list_recipes)<5:
        #we start by removing include ingredients constraints if they are specified
        if  relaxed_constraints['ingredients'] and len(relaxed_constraints['ingredients']['include'])>0:
            for i in range(len(relaxed_constraints['ingredients']['include'])):
                # we start by relaxing the food category constraint
                if relaxed_constraints['ingredients']['include'][i]['food_category']:
                   relaxed_constraints['ingredients']['include'][i]['food_category']=None
                #then we remove the basic taste constraint
                elif relaxed_constraints['ingredients']['include'][i]['basic_taste']:
                   relaxed_constraints['ingredients']['include'][i]['basic_taste']=None
                #then we remove the ingredient name constraint
                elif relaxed_constraints['ingredients']['include'][i]['name']:
                    relaxed_constraints['ingredients']['include'][i]['name']=None
        #next we remove the exclude ingredients constraints if they are specified 
        elif relaxed_constraints['ingredients'] and len(relaxed_constraints['ingredients']['exclude'])>0:
            for i in range (len(relaxed_constraints['ingredients']['exclude'])):
                if relaxed_constraints['ingredients']['exclude'][i]['food_category']:
                    relaxed_constraints['ingredients']['exclude'][i]['food_category']=None
                elif relaxed_constraints['ingredients']['exclude'][i]['basic_taste']:
                   relaxed_constraints['ingredients']['exclude'][i]['basic_taste']=None
                elif relaxed_constraints['ingredients']['exclude'][i]['name']:
                    relaxed_constraints['ingredients']['exclude'][i]['name']=None
        #next we remove the cuisine constraints if they are specified
        elif relaxed_constraints['cuisine'] and len(relaxed_constraints['cuisine']['include'])>0:
            relaxed_constraints['cuisine']['include']=[]
        elif relaxed_constraints['cuisine'] and len(relaxed_constraints['cuisine']['exclude'])>0:
            relaxed_constraints['cuisine']['exclude']=[]
        #probably this won't happen but just in case
        elif relaxed_constraints['course_type'] and  len(relaxed_constraints['course_type']['include'])>0:
            relaxed_constraints['course_type']['include']=[]
        elif relaxed_constraints['course_type'] and len(relaxed_constraints['course_type']['exclude'])>0:
            relaxed_constraints['course_type']['exclude']=[]
        query_builder.reset()
        # Add constraints from the query
        if relaxed_constraints["dietary_preference"]:
            query_builder.add_dietary_preference_constraint(include=relaxed_constraints['dietary_preference']['include'],exclude=relaxed_constraints['dietary_preference']['include'])
        if relaxed_constraints["course_type"]:
            query_builder.add_course_type_constraint(include=relaxed_constraints['course_type']['include'],exclude=relaxed_constraints['course_type']['exclude'])
        if relaxed_constraints["cuisine"]:
            query_builder.add_cuisine_constraint(include=relaxed_constraints["cuisine"]['include'],exclude=relaxed_constraints["cuisine"]['exclude'])
        if relaxed_constraints["ingredients"]:
            query_builder.add_ingredients_constraint(include=relaxed_constraints['ingredients']['include'],exclude=relaxed_constraints['ingredients']['exclude'])
            
        xpath_query = query_builder.build()
        print(xpath_query)
        list_recipes = cl.find_recipes_by_constraint_query(xpath_query)
    
    if len(list_recipes) >0:
        print(f"Found {len(list_recipes)} recipes")
        sim_list = [similarity_recipe(constraints, rec) for rec in list_recipes]
    max_indices = np.argwhere(np.array(sim_list) == np.amax(np.array(sim_list))).flatten().tolist()
    index_retrieved = random.choice(max_indices) if len(max_indices) > 1 else max_indices[0]

    retrieved_case = list_recipes[index_retrieved]
    return list_recipes, sim_list, index_retrieved, retrieved_case
