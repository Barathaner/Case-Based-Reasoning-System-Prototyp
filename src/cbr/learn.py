# Create a function to learn the cases adapted to the case_library
def learn():
    if adapted_recipe.evaluation == "success":
        case_library.add_case(adapted_recipe)
        forget_cases()


# Create a function to forget the case from the case library that has less success or with the highest similarity
def forget_cases():
    for recipe in case_library.find_recipes_by_constraint_query(f".//cookingrecipe[utility < {0.8}]"):
        food_categories = (ingredient.attrib["food_category"] for ingredient in recipe.ingredients.iterchildren())
        basic_tastes = (ingredient.attrib["basic_taste"] for ingredient in recipe.ingredients.iterchildren())

        query_builder = ConstraintQueryBuilder()
        query_builder.add_dietary_preference_constraint(include=[recipe.dietary_preference], exclude=[])
        query_builder.add_course_type_constraint(include=[recipe.course_type])
        query_builder.add_cuisine_constraint(include=[recipe.cuisine], exclude=[])

        query = query_builder.build()

        found_recipes = case_library.find_recipes_by_constraint_query(query)

        if len(found_recipes) > 1:
            case_library.remove_recipe(new_recipe)

        if (len(case_library.findall(ConstraintsBuilder(recipe.course_type, recipe.dietary_preference, recipe.cuisine)
                                             .filter_food_category(list(food_categories))
                                             .filter_basic_taste(list(basic_tastes)))) > 1):
            case_library.remove_case(recipe)
