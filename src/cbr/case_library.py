from lxml import etree, objectify
class CookingRecipe:
    def __init__(self, name, course_type, dietary_preference, cuisine, ingredients, instructions,utility):
        self.name = str(name).lower()
        self.course_type = str(course_type).lower()
        self.dietary_preference = str(dietary_preference).lower()
        self.cuisine = str(cuisine).lower()
        self.ingredients = ingredients
        self.instructions = instructions
        #added the rest of attributes because we will need them in retrieval, adaptation, evaluation
        self.utility=utility

    def to_xml(self):
        """Converts the recipe object into an lxml element."""
        recipe_element = objectify.Element("cookingrecipe")
        recipe_element.name = self.name
        recipe_element.course_type = self.course_type
        recipe_element.dietary_preference = self.dietary_preference
        recipe_element.cuisine = self.cuisine
        #add the rest of attributes
        recipe_element.utility = self.utility 
        recipe_element.derivation = self.derivation
    
        
        ingredients_element = objectify.SubElement(recipe_element, "ingredients")
        for ingredient in self.ingredients:
            ingredient_element = objectify.SubElement(ingredients_element, "ingredient", amount=str(ingredient['amount']), unit=ingredient['unit'], basic_taste=str(ingredient['basic_taste']).lower(), food_category=str(ingredient['food_category']).lower())
            ingredient_element._setText(ingredient['name'])
        
        instructions_element = objectify.SubElement(recipe_element, "instructions")
        for step in self.instructions:
            step_element = objectify.SubElement(instructions_element, "step")
            step_element._setText(step)

        return recipe_element

    def __str__(self):
        """Returns a string representation of the recipe in a readable format."""
        ingredients_str = ', '.join([f"{ing['amount']} {ing['unit']} of {ing['name']} ({ing['basic_taste']} taste, {ing['food_category']})" for ing in self.ingredients])
        instructions_str = ' -> '.join(self.instructions)
        return (f"Recipe Name: {self.name.title()}\n"
                f"Course Type: {self.course_type.title()}\n"
                f"Dietary Preference: {self.dietary_preference.title()}\n"
                f"Cuisine: {self.cuisine.title()}\n"
                f"Ingredients: {ingredients_str}\n"
                f"Instructions: {instructions_str}\n"
                f"Utility:{self.utility}") #add the rest of attributes if needed

def parse_recipe_from_xml(xml_element):
    name = xml_element.findtext('name')
    course_type = xml_element.findtext('course_type')
    dietary_preference = xml_element.findtext('dietary_preference')
    cuisine = xml_element.findtext('cuisine')
    #add the rest of attributes if needed
    utility = xml_element.findtext('utility')

    ingredients = []
    for ingredient in xml_element.xpath('./ingredients/ingredient'):
        ing_details = {
            'name': ingredient.text,
            'amount': ingredient.get('amount'),
            'unit': ingredient.get('unit'),
            'basic_taste': ingredient.get('basic_taste'),
            'food_category': ingredient.get('food_category')
        }
        ingredients.append(ing_details)

    instructions = [step.text for step in xml_element.xpath('./instructions/step')]

    return CookingRecipe(name, course_type, dietary_preference, cuisine, ingredients, instructions,utility)


class CaseLibrary:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.tree = objectify.parse(xml_path)
        self.root = self.tree.getroot()

    def add_recipe(self, recipe):
        """Add a recipe to the XML structure at the correct hierarchy based on its attributes."""
        # Erstelle den Pfad, um den richtigen Ort für das Rezept zu finden
        path = f"./dietary_preference[@type='{recipe.dietary_preference}']/course_type[@type='{recipe.course_type}']/cuisine[@type='{recipe.cuisine}']"
        parent = self.root.xpath(path)
        
        if not parent:
            # Wenn der Pfad nicht existiert, erstelle die notwendigen Knoten
            dp_node = objectify.SubElement(self.root, "dietary_preference", type=recipe.dietary_preference)
            ct_node = objectify.SubElement(dp_node, "course_type", type=recipe.course_type)
            cuisine_node = objectify.SubElement(ct_node, "cuisine", type=recipe.cuisine)
            recipes_node = objectify.SubElement(cuisine_node, "cookingrecipes")
            #We should add the rest of attributes as default parameters ? 
            
        else:
            recipes_node = parent[0].xpath("./cookingrecipes")[0]

        # Prüfe, ob ein Rezept mit demselben Namen bereits existiert
        existing_recipe = recipes_node.xpath(f"./cookingrecipe[name='{recipe.name}']")
        if existing_recipe:
            print("This name is already taken, create a new one.")
            return False  # Rückgabe von False, um anzuzeigen, dass das Hinzufügen fehlgeschlagen ist

        # Füge das Rezept hinzu, wenn kein Duplikat gefunden wurde
        recipes_node.append(recipe.to_xml())
        self.save()
        return True  # Erfolgreich hinzugefügt

    def remove_recipe(self, recipe):
        """Remove a recipe from the XML based on its name and location."""
        query = f"./dietary_preference[@type='{recipe.dietary_preference}']/course_type[@type='{recipe.course_type}']/cuisine[@type='{recipe.cuisine}']/cookingrecipes/cookingrecipe[name='{recipe.name}']"
        recipe = self.root.xpath(query)
        if recipe:
            parent = recipe[0].getparent()
            parent.remove(recipe[0])
            self.save()

    def save(self):
        """Save changes to the XML file."""
        objectify.deannotate(self.root, cleanup_namespaces=True)
        tree = etree.ElementTree(self.root)
        tree.write(self.xml_path, pretty_print=True, encoding='utf-8')

    def find_recipes_by_constraint_query(self, query):
        """Find recipes using an XPath query and return a list of CookingRecipe objects."""
        recipe_elements = self.root.xpath(query)
        recipes = [parse_recipe_from_xml(elem) for elem in recipe_elements]
        return recipes

    
    def print_first_five_recipes(self):
        """ Druckt nur die ersten 5 Rezepte und zeigt an, wie viele insgesamt gefunden wurden """
        recipes = self.root.xpath(".//cookingrecipe")
        count = len(recipes)
        display_count = min(5, count)

        for recipe in recipes[:display_count]:
            print(etree.tostring(recipe, pretty_print=True, encoding='unicode'))

        print(f"Show {display_count} of {count} recipes.")
class ConstraintQueryBuilder:
    """Builds XPath queries based on provided constraints, offering methods for specific hierarchical attributes."""

    def __init__(self):
        self.constraints = {
            "dietary_preference": [],
            "course_type": [],
            "cuisine": [],
            "ingredients":[] #added ingredients constraints
        }

    def add_dietary_preference_constraint(self, include=None, exclude=None):
        self._add_constraint("dietary_preference", include, exclude)
        
    def add_course_type_constraint(self, include=None, exclude=None):
        self._add_constraint("course_type", include, exclude)
        
    def add_cuisine_constraint(self, include=None, exclude=None):
        self._add_constraint("cuisine", include, exclude)
        
    def add_ingredients_constraint(self,include=None,exclude=None):
        self._add_complex_ingredient_constraint(include,exclude)

    def _add_constraint(self, category, include=None, exclude=None):
        """General method to add constraints based on inclusion or exclusion lists."""
        if include:
            self.constraints[category] += [f"@type='{item.lower()}'" for item in include] # we will have to reconstruct again the include and exclude lists
        if exclude:
            self.constraints[category] += [f"@type!='{item.lower()}'" for item in exclude]
    def _add_complex_ingredient_constraint(self, include=None, exclude=None):
        """Method to add complex ingredient constraints based on name, basic taste, and food category."""
        if include:
            for ing in include:
                parts = []
                if ing['name']:
                    parts.append(f"name='{ing['name']}'")
                if ing['basic_taste']:
                    parts.append(f"@basic_taste='{ing['basic_taste']}'")
                if ing['food_category']:
                    parts.append(f"@food_category='{ing['food_category']}'")
                self.constraints["ingredients"].append(f"({' and '.join(parts)})")

        if exclude:
            for ing in exclude:
                parts = []
                if ing['name']:
                    parts.append(f"name!='{ing['name']}'")
                if ing['basic_taste']:
                    parts.append(f"@basic_taste!='{ing['basic_taste']}'")
                if ing['food_category']:
                    parts.append(f"@food_category!='{ing['food_category']}'")
                self.constraints["ingredients"].append(f"({' and '.join(parts)})")

    def build(self):
        """Build the XPath query from the accumulated constraints."""
        parts = []
        if self.constraints['dietary_preference']:
            dp_query = " or ".join(self.constraints['dietary_preference'])
            parts.append(f"dietary_preference[{dp_query}]")
        
        if self.constraints['course_type']:
            ct_query = " or ".join(self.constraints['course_type'])
            parts.append(f"course_type[{ct_query}]")
        
        if self.constraints['cuisine']:
            cuisine_query = " or ".join(self.constraints['cuisine'])
            parts.append(f"cuisine[{cuisine_query}]/cookingrecipes/cookingrecipe") #why did you add this ??
        if self.constraints['ingredients']:
            ingredients_query = " or ".join(self.constraints['ingredients'])
            parts.append(f"ingredients[{ingredients_query}]")

        if not parts:
            return ".//cookingrecipe"
        
        # Build the full path by chaining the parts
        full_query = "/".join(parts)
        xpath_query = f"//{full_query}"
        print("Debug XPath Query:", xpath_query)  # Debugging line to see the built query
        return xpath_query

    def reset(self):
        """Reset the accumulated constraints."""
        self.constraints = {"dietary_preference": [], "course_type": [], "cuisine": [], "ingredients":[]}
