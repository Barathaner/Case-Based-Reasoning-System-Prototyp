import os
import random
from pathlib import Path

import numpy as np

random.seed(10)
sim_weights = {
    "dp_match": 1,
    "ct_match": 0.85,
    "cuisine_match": 0.65,
    "ingr_match": 0.5,
    "ingr_name_match": 0.5,
    "ingr_basic_taste_match": 0.5,
    "ingr_food_cat_match": 0.5
}

def update_sim1(sim, cumulative_norm_score, key, constraints, attribute, w):
    if (len(constraints[key]['exclude']) > 0) or len(constraints[key]['include']) > 0:
        if (len(constraints[key]['include']) > 0) and attribute in constraints[key]['include']:
            sim += sim_weights[w]
            cumulative_norm_score += sim_weights[w]
        elif (len(constraints[key]['exclude']) > 0) and attribute in constraints[key]['exclude']:
            sim -= sim_weights[w]
            cumulative_norm_score += sim_weights[w]
        else:
            # In case the constraint is not fulfilled we add the weight to the normalization score
            cumulative_norm_score += sim_weights[w]
    else:
        sim += sim_weights[w]
        cumulative_norm_score += sim_weights[w]

def update_sim2(sim, cumulative_norm_score, constraints, attribute, w, ingredient):
    if (len(constraints['ingredients']['include'][attribute]) > 0) and ingredient[attribute] in constraints['ingredients']['include'][attribute]:
        sim += sim_weights[w]
        cumulative_norm_score += sim_weights[w]
    elif (len(constraints['ingredients']['exclude'][attribute]) > 0) and ingredient[attribute] in constraints['ingredients']['exclude'][attribute]:
        sim -= sim_weights[w]
        cumulative_norm_score += sim_weights[w]
    else:
        # In case the constraint is not fulfilled we add the weight to the normalization score
        cumulative_norm_score += sim_weights[w]

def similarity_recipe(constraints, recipe):
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
            update_sim1(sim, cumulative_norm_score, key, constraints, recipe_dietary_preference, 'dp_match')      
        if key == "course_type":
            update_sim1(sim, cumulative_norm_score, key, constraints, recipe_course_type, 'ct_match')
        if key == "cuisine":
            update_sim1(sim, cumulative_norm_score, key, constraints, recipe_cuisine, 'cuisine_match')
        if key == "ingredients":
            if (len(constraints[key]['include']['name']) > 0) or (len(constraints[key]['exclude']['name']) > 0):
                for ingredient in recipe_ingredients:
                    update_sim2(sim, cumulative_norm_score, constraints, 'name', 'ingr_name_match', ingredient)
            if len(constraints[key]['include']['basic_taste']) > 0 or len(constraints[key]['exclude']['basic_taste']) > 0:
                for ingredient in recipe_ingredients:
                    update_sim2(sim, cumulative_norm_score, constraints, 'basic_taste', 'ingr_basic_taste_match', ingredient)
            if len(constraints[key]['include']['food_category']) > 0 or len(constraints[key]['exclude']['food_category']) > 0:
                for ingredient in recipe_ingredients:
                    update_sim2(sim, cumulative_norm_score, constraints, 'food_category', 'ingr_food_cat_match', ingredient)
            else:  
                sim += sim_weights["ingr_match"]
                cumulative_norm_score += sim_weights["ingr_match"]     

    normalized_sim = sim / cumulative_norm_score if cumulative_norm_score else 1.0
    return normalized_sim * float(recipe.utility)

def retrieve(constraints, cl, query_builder):
    # Add constraints from the query
    query_builder.add_dietary_preference_constraint(include=constraints['dietary_preference']['include'], exclude=constraints['dietary_preference']['exclude'])
    query_builder.add_course_type_constraint(include=constraints['course_type']['include'], exclude=constraints['course_type']['exclude'])
    query_builder.add_cuisine_constraint(include=constraints["cuisine"]['include'], exclude=constraints["cuisine"]['exclude'])
    query_builder.add_ingredients_constraint(include=constraints['ingredients']['include'], exclude=constraints['ingredients']['exclude'])

    xpath_query = query_builder.build()
    list_recipes = cl.find_recipes_by_constraint_query(xpath_query)
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
        
        query_builder.reset()

        # Add constraints from the relaxed query
        query_builder.add_dietary_preference_constraint(include=relaxed_constraints['dietary_preference']['include'], exclude=relaxed_constraints['dietary_preference']['exclude'])
        query_builder.add_course_type_constraint(include=relaxed_constraints['course_type']['include'], exclude=relaxed_constraints['course_type']['exclude'])
        query_builder.add_cuisine_constraint(include=relaxed_constraints['cuisine']['include'], exclude=relaxed_constraints['cuisine']['exclude'])
        query_builder.add_ingredients_constraint(include=relaxed_constraints['ingredients']['include'], exclude=relaxed_constraints['ingredients']['exclude'])

        xpath_query = query_builder.build()
        print(xpath_query)
        list_recipes = cl.find_recipes_by_constraint_query(xpath_query)
    
    if list_recipes:
        print(f"Found {len(list_recipes)} recipes")
        sim_list = [similarity_recipe(constraints, rec) for rec in list_recipes]
        max_indices = np.argwhere(np.array(sim_list) == np.amax(np.array(sim_list))).flatten().tolist()
        index_retrieved = random.choice(max_indices) if len(max_indices) > 1 else max_indices[0]
        retrieved_case = list_recipes[index_retrieved]
        return list_recipes, sim_list, index_retrieved, retrieved_case
    else:
        return [], [], None, None

