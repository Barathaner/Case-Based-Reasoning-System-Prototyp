from case_library import ConstraintQueryBuilder, CaseLibrary
CASELIBRARYPATH = r"C:\Users\gerar\PycharmProjects\Case-Based-Reasoning-System-Prototyp\data\case_library.xml"
cl=CaseLibrary(CASELIBRARYPATH)

UTILITY_THRESHOLD = 0.8


# Create a function to learn the cases adapted to the case_library
def learn(case_library, adapted_recipe):
    if adapted_recipe.evaluation == "success":
        case_library.add_case(adapted_recipe)
        forget_cases(case_library)


# Create a function to forget the case from the case library that has less success or with the highest similarity
def forget_cases(case_library: CaseLibrary):
    for recipe in case_library.find_recipes_by_constraint_query(f".//cookingrecipe[utility < {2}]"):

        ingredient_constraints = []
        food_categories = [ingredient["food_category"] for ingredient in recipe.ingredients]
        basic_tastes = [ingredient["basic_taste"] for ingredient in recipe.ingredients]
        names = [ingredient["name"] for ingredient in recipe.ingredients]

        for food_category, basic_taste, name in zip(food_categories, basic_tastes, names):
            constraint = {"food_category": food_category, "basic_taste": basic_taste, "name": name}
            ingredient_constraints.append(constraint)

        query_builder = ConstraintQueryBuilder()
        query_builder.add_dietary_preference_constraint(include=[recipe.dietary_preference])
        query_builder.add_course_type_constraint(include=[recipe.course_type])
        query_builder.add_cuisine_constraint(include=[recipe.cuisine])
        query_builder.add_ingredients_constraint(include=ingredient_constraints)

        query = query_builder.build()

        found_recipes = case_library.find_recipes_by_constraint_query(query)

        print(found_recipes[0].name)
        exit()

        if len(found_recipes) > 1:
            case_library.remove_recipe(recipe)
            case_library.save()

forget_cases(cl)