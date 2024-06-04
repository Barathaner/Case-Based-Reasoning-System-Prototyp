from lxml import etree, objectify


class CookingRecipe:
    def __init__(self, name, course_type, dietary_preference, cuisine, ingredients, instructions, utility, derivation,
                 evaluation, UaS, UaF, success_count, failure_count):
        self.name = str(name).lower()
        self.course_type = str(course_type).lower()
        self.dietary_preference = str(dietary_preference).lower()
        self.cuisine = str(cuisine).lower()
        self.ingredients = ingredients
        self.instructions = instructions
        # add missing attributes
        self.utility = utility
        self.derivation = derivation
        self.evaluation = evaluation
        self.UaS = UaS
        self.UaF = UaF
        self.success_count = success_count
        self.failure_count = failure_count

    def to_xml(self):
        """Converts the recipe object into an lxml element."""
        recipe_element = objectify.Element("cookingrecipe")
        recipe_element.name = self.name
        recipe_element.course_type = self.course_type
        recipe_element.dietary_preference = self.dietary_preference
        recipe_element.cuisine = self.cuisine
        recipe_element.utility = str(self.utility)
        recipe_element.derivation = str(self.derivation)
        recipe_element.evaluation = str(self.evaluation)
        recipe_element.UaS = str(self.UaS)
        recipe_element.UaF = str(self.UaF)
        recipe_element.success_count = str(self.success_count)
        recipe_element.failure_count = str(self.failure_count)

        ingredients_element = objectify.SubElement(recipe_element, "ingredients")
        for ingredient in self.ingredients:
            ingredient_element = objectify.SubElement(ingredients_element, "ingredient",
                                                      amount=str(ingredient['amount']), unit=ingredient['unit'],
                                                      basic_taste=str(ingredient['basic_taste']).lower(),
                                                      food_category=str(ingredient['food_category']).lower())
            ingredient_element._setText(ingredient['name'])

        instructions_element = objectify.SubElement(recipe_element, "instructions")
        for step in self.instructions:
            step_element = objectify.SubElement(instructions_element, "step")
            step_element._setText(step)

        return recipe_element

    def __str__(self):
        """Returns a string representation of the recipe in a readable format."""
        ingredients_str = ""
        if self.ingredients is not None and len(self.ingredients) > 0:
            ingredients_str = ', '.join(
                [f"{ing['amount']} {ing['unit']} of {ing['name']} ({ing['basic_taste']} taste, {ing['food_category']})"
                 for ing in self.ingredients])
        instructions_str = ' -> '.join(self.instructions)
        return (f"Recipe Name: {self.name.title()}\n"
                f"Course Type: {self.course_type.title()}\n"
                f"Dietary Preference: {self.dietary_preference.title()}\n"
                f"Cuisine: {self.cuisine.title()}\n"
                f"utility: {self.utility.title()}\n"
                f"derivation: {self.derivation.title()}\n"
                f"evaluation: {self.evaluation.title()}\n"
                f"UaS: {self.UaS.title()}\n"
                f"UaF: {self.UaF.title()}\n"
                f"failure_count: {self.failure_count.title()}\n"
                f"success_count: {self.success_count.title()}\n"
                f"Ingredients: {ingredients_str}\n"
                f"Instructions: {instructions_str}\n"
                f"Utility:{self.utility}")  # add the rest of attributes if needed


def parse_recipe_from_xml(xml_element):
    name = xml_element.findtext('name')
    course_type = xml_element.findtext('course_type')
    dietary_preference = xml_element.findtext('dietary_preference')
    cuisine = xml_element.findtext('cuisine')
    utility = xml_element.findtext('utility')
    derivation = xml_element.findtext('derivation')
    evaluation = xml_element.findtext('evaluation')
    UaS = xml_element.findtext('UaS')
    UaF = xml_element.findtext('UaF')
    failure_count = xml_element.findtext('failure_count')
    success_count = xml_element.findtext('success_count')

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

    return CookingRecipe(name, course_type, dietary_preference, cuisine, ingredients, instructions, utility, derivation,
                         evaluation, UaS, UaF, failure_count, success_count)


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
            # We should add the rest of attributes as default parameters ?

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
            "dietary_preference": {'include': [], 'exclude': []},
            "course_type": {'include': [], 'exclude': []},
            "cuisine": {'include': [], 'exclude': []},
            "ingredients": {
                'include': {"name": [],
                            "food_category": [],
                            "basic_taste": []},
                'exclude': {"name": [],
                            "food_category": [],
                            "basic_taste": []}
            }
        }

    def add_dietary_preference_constraint(self, include=None, exclude=None):
        self._add_constraint("dietary_preference", include, exclude)

    def add_course_type_constraint(self, include=None, exclude=None):
        self._add_constraint("course_type", include, exclude)

    def add_cuisine_constraint(self, include=None, exclude=None):
        self._add_constraint("cuisine", include, exclude)

    def add_ingredients_constraint(self, include=None, exclude=None):
        self._add_complex_ingredient_constraint(include, exclude)

    def _add_constraint(self, category, include=None, exclude=None):
        """General method to add constraints based on inclusion or exclusion lists."""
        if include:
            self.constraints[category]['include'] += [f"@type='{item.lower()}'" for item in include] 
        if exclude:
            self.constraints[category]['exclude'] += [f"@type!='{item.lower()}'" for item in exclude]

    def _add_complex_ingredient_constraint(self, include=None, exclude=None):
        """Method to add complex ingredient constraints based on name, basic taste, and food category."""
        if include:
            if include['name']:
                self.constraints["ingredients"]['include']['name']+=[f"@type='{item.lower()}'" for item in include['name']]
            if include['basic_taste']:
                self.constraints["ingredients"]['include']['basic_taste']+=[f"@type='{item.lower()}'" for item in include['basic_taste']]
            if include['food_category']:
                self.constraints["ingredients"]['include']['food_category']+=[f"@type='{item.lower()}'" for item in include['food_category']]

        if exclude:
            if exclude['name']:
                self.constraints["ingredients"]['exclude']['name']+=[f"@type!='{item.lower()}'" for item in exclude['name']]
            if exclude['basic_taste']: 
                self.constraints["ingredients"]['exclude']['basic_taste']+=[f"@type!='{item.lower()}'" for item in exclude['basic_taste']]
            if exclude['food_category']:
                self.constraints["ingredients"]['exclude']['food_category']+=[f"@type!='{item.lower()}'" for item in exclude['food_category']]

    def build(self):
        """Build the XPath query from the accumulated constraints."""
        parts = []
        if self.constraints['dietary_preference']['include']:
            dp_query = " or ".join(self.constraints['dietary_preference']['include'])
            parts.append(f"dietary_preference[{dp_query}]")
        if self.constraints['dietary_preference']['exclude']:
            dp_query = " and ".join(self.constraints['dietary_preference']['exclude'])
            parts.append(f"dietary_preference[{dp_query}]")

        if self.constraints['course_type']['include']:
            ct_query = " or ".join(self.constraints['course_type']['include'])
            parts.append(f"course_type[{ct_query}]")
        if self.constraints['course_type']['exclude']:
            ct_query = " and ".join(self.constraints['course_type']['exclude'])
            parts.append(f"course_type[{ct_query}]")

        if self.constraints['cuisine']['include']:
            cuisine_query = " or ".join(self.constraints['cuisine']['include'])
            parts.append(f"cuisine[{cuisine_query}]/cookingrecipes//cookingrecipe")
        if self.constraints['cuisine']['exclude']:
            cuisine_query = " and ".join(self.constraints['cuisine']['exclude'])
            parts.append(f"cuisine[{cuisine_query}]/cookingrecipes//cookingrecipe")

        if any(lst for lst in self.constraints['ingredients']['include'].values()):
            if self.constraints['ingredients']['include']['name']:
                for ing_name in self.constraints['ingredients']['include']['name']:
                    parts[-1] += f"[descendant::ingredient[text()={ing_name}]]"
            if self.constraints['ingredients']['include']['basic_taste']:
                for basic_taste in self.constraints['ingredients']['include']['basic_taste']:
                    parts[-1] += f"[descendant::ingredient[@basic_taste={basic_taste}]]"
            if self.constraints['ingredients']['include']['food_category']:
                for food_category in self.constraints['ingredients']['include']['food_category']:
                    parts[-1] += f"[descendant::ingredient[@food_category={food_category}]]"

        if any(lst for lst in self.constraints['ingredients']['exclude'].values()):
            if self.constraints['ingredients']['exclude']['name']:
                for ing_name in self.constraints['ingredients']['exclude']['name']:
                    parts[-1] += f"[descendant::ingredient[text()!={ing_name}]]"
            if self.constraints['ingredients']['exclude']['basic_taste']:
                for basic_taste in self.constraints['ingredients']['exclude']['basic_taste']:
                    parts[-1] += f"[descendant::ingredient[@basic_taste!={basic_taste}]]"
            if self.constraints['ingredients']['exclude']['food_category']:
                for food_category in self.constraints['ingredients']['exclude']['food_category']:
                    parts[-1] += f"[descendant::ingredient[@food_category!={food_category}]]"

        if not parts:
            return ".//cookingrecipe"

        # Build the full path by chaining the parts
        full_query = "/".join(parts)
        xpath_query = f"./{full_query}"
        print("Debug XPath Query:", xpath_query)  # Debugging line to see the built query
        return xpath_query

    def reset(self):
        """Reset the accumulated constraints."""
        self.constraints = {"dietary_preference": [], "course_type": [], "cuisine": [], "ingredients": []}
