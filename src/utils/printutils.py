def format_xmlrecipes_to_str(recipes):
    for recipe in recipes:
        # Extract basic information
        name = recipe.findtext('name')
        course_type = recipe.findtext('course_type')
        dietary_preference = recipe.findtext('dietary_preference')
        cuisine = recipe.findtext('cuisine')
        
        # Gather ingredient details
        ingredients = []
        for ing in recipe.xpath('./ingredients/ingredient'):
            amount = ing.get('amount')
            unit = ing.get('unit')
            taste = ing.get('basic_taste')
            food_category = ing.get('food_category')
            ingredient_name = ing.text
            ingredients.append(f"{amount} {unit} of {ingredient_name} ({taste} taste, {food_category})")
        
        # Gather instructions
        instructions = ' -> '.join([step.text for step in recipe.xpath('./instructions/step')])
        
        # Create a formatted string for each recipe
        formatted_recipe = (
            f"Recipe Name: {name}\n"
            f"Course Type: {course_type}\n"
            f"Dietary Preference: {dietary_preference}\n"
            f"Cuisine: {cuisine}\n"
            f"Ingredients:\n  {'; '.join(ingredients)}\n"
            f"Instructions:\n  {instructions}\n"
            "--------------------------------------"
        )
        
        # Print the formatted recipe
        return formatted_recipe