def _compute_utility(case):
    return ((case.UaS / (case.success_count + 1e-5)) - (case.UaF / (case.failure_count + 1e-5)) + 1) / 2

def evaluate(user_score):
    if user_score > EVALUATION_THRESHOLD:
        adapted_recipe.evaluation = "success"
        retrieved_recipe.UaS += 1
        retrieved_recipe.success_count += 1
        retrieved_recipe.utility = _compute_utility(retrieved_recipe)
        for recipe in similar_recipes:
            recipe.success_count += 1
            recipe.utility = _compute_utility(recipe)
    else:
        adapted_recipe.evaluation = "failure"
        retrieved_recipe.UaF += 1
        retrieved_recipe.failure_count += 1
        retrieved_recipe.utility = _compute_utility(retrieved_recipe)
        for recipe in sim_recipes:
            recipe.failure_count += 1
            recipe.utility = _compute_utility(recipe)


