from lxml import etree, objectify
import xml.etree.ElementTree as ET


class CookingRecipe:
    def __init__(self, name, course_type, dietary_preference, cuisine, ingredients, instructions, utility, derivation,
                 evaluation, UaS, UaF, success_count, failure_count):
        self.name = str(name).lower()
        self.course_type = str(course_type).lower()
        self.dietary_preference = str(dietary_preference).lower()
        self.cuisine = str(cuisine).lower()
        self.ingredients = ingredients
        self.instructions = instructions
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
            ingredient_element._setText(str(ingredient['name']))

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
                f"Utility:{self.utility}") 

    def compare_with(self, other):
        """Compares the current recipe with another recipe and returns the differences."""
        differences = []

        if self.course_type != other.course_type:
            differences.append(f"Course Type: {self.course_type} != {other.course_type}")
        if self.dietary_preference != other.dietary_preference:
            differences.append(f"Dietary Preference: {self.dietary_preference} != {other.dietary_preference}")
        if self.cuisine != other.cuisine:
            differences.append(f"Cuisine: {self.cuisine} != {other.cuisine}")

        ingredients1 = sorted(self.ingredients, key=lambda x: x['name'])
        ingredients2 = sorted(other.ingredients, key=lambda x: x['name'])

        diff_ingredients = []
        for ing1, ing2 in zip(ingredients1, ingredients2):
            if ing1['name'] != ing2['name']:
                diff_ingredients.append(f"{ing1['name']} != {ing2['name']}")
        if len(ingredients1) > len(ingredients2):
            diff_ingredients.extend([f"{ing['name']} != None" for ing in ingredients1[len(ingredients2):]])
        elif len(ingredients2) > len(ingredients1):
            diff_ingredients.extend([f"None != {ing['name']}" for ing in ingredients2[len(ingredients1):]])

        if diff_ingredients:
            differences.append(f"Ingredients: {', '.join(diff_ingredients)}")

        instructions1 = self.instructions
        instructions2 = other.instructions

        diff_instructions = []
        for step1, step2 in zip(instructions1, instructions2):
            if step1 != step2:
                diff_instructions.append(f"{step1} != {step2}")
        if len(instructions1) > len(instructions2):
            diff_instructions.extend([f"{step} != None" for step in instructions1[len(instructions2):]])
        elif len(instructions2) > len(instructions1):
            diff_instructions.extend([f"None != {step}" for step in instructions2[len(instructions1):]])

        if diff_instructions:
            differences.append(f"Instructions: {', '.join(diff_instructions)}")

        return '\n'.join(differences)


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

        self.course_types = []
        self.dietary_preferences_types = []
        self.cuisines_types = []
        self.ingredients = []
        self.basic_tastes_types = []
        self.food_categories_types = []
        
        self.initialize_type_sets()

    def add_recipe(self, recipe):
        """Add a recipe to the XML structure at the correct hierarchy based on its attributes."""
        path = f"./dietary_preference[@type='{recipe.dietary_preference}']/course_type[@type='{recipe.course_type}']/cuisine[@type='{recipe.cuisine}']"
        parent = self.root.xpath(path)

        if not parent:
            dp_node = objectify.SubElement(self.root, "dietary_preference", type=recipe.dietary_preference)
            ct_node = objectify.SubElement(dp_node, "course_type", type=recipe.course_type)
            cuisine_node = objectify.SubElement(ct_node, "cuisine", type=recipe.cuisine)
            recipes_node = objectify.SubElement(cuisine_node, "cookingrecipes")
        else:
            recipes_node = parent[0].xpath("./cookingrecipes")[0]

        existing_recipe = recipes_node.xpath(f"./cookingrecipe[name='{recipe.name}']")
        if existing_recipe:
            print("This name is already taken, create a new one.")
            return False  

        recipes_node.append(recipe.to_xml())

        return True  
    def remove_recipe(self, recipe):
        """Remove a recipe from the XML based on its name and location."""
        query = f"./dietary_preference[@type='{recipe.dietary_preference}']/course_type[@type='{recipe.course_type}']/cuisine[@type='{recipe.cuisine}']/cookingrecipes/cookingrecipe[name='{recipe.name}']"
        recipe = self.root.xpath(query)
        if recipe:
            parent = recipe[0].getparent()
            parent.remove(recipe[0])

    def get_length(self):
        recipes = self.root.xpath(".//cookingrecipe")
        count = len(recipes)
        return count

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
    
    def findall(self, constraints):
        if isinstance(constraints, str):
            return self.root.xpath(constraints)
        elif isinstance(constraints, ConstraintQueryBuilder):
            return self.root.xpath(constraints.build())
        else:
            raise TypeError("constraints must be string or ConstraintsQueryBuilder.")
        
    def get_ingredient_properties(self, ingredient_name):
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        for ingredient in root.iter("ingredient"):
            if ingredient.text == ingredient_name:
                properties = ingredient.attrib
                properties['name'] = ingredient.text
                return properties
        
        return None
    
    def initialize_type_sets(self):
        self.course_types = []
        self.dietary_preferences_types = []
        self.cuisines_types = []
        self.ingredients = []
        self.basic_tastes_types = []
        self.food_categories_types = []
        

        for recipe in self.root.xpath(".//cookingrecipe"):
            course_type = recipe.course_type.text
            dietary_preference = recipe.dietary_preference.text
            cuisine = recipe.cuisine.text

            if course_type not in self.course_types:
                self.course_types.append(course_type)
            if dietary_preference not in self.dietary_preferences_types:
                self.dietary_preferences_types.append(dietary_preference)
            if cuisine not in self.cuisines_types:
                self.cuisines_types.append(cuisine)


            for ingredient in recipe.ingredients.iterchildren():
                name = ingredient.text
                food_category = ingredient.attrib["food_category"]
                basic_taste = ingredient.attrib["basic_taste"]

                if name not in self.ingredients:
                    self.ingredients.append(name)
                if food_category not in self.food_categories_types:
                    self.food_categories_types.append(food_category)
                if basic_taste not in self.basic_tastes_types:
                    self.basic_tastes_types.append(basic_taste)
                

        self.course_types = sorted(self.course_types)
        self.dietary_preferences_types = sorted(self.dietary_preferences_types)
        self.cuisines_types = sorted(self.cuisines_types)
        self.ingredients = sorted(self.ingredients)
        self.basic_tastes_types = sorted(self.basic_tastes_types)
        self.food_categories_types = sorted(self.food_categories_types)




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

    def add_whole_ingredients_constraint(self, include=None, exclude=None):
        self._add_whole_complex_ingredient_constraint(include, exclude)

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

    def _add_whole_complex_ingredient_constraint(self, include=None, exclude=None):
        """Method to add complex ingredient constraints based on name, basic taste, and food category."""
        if include:
            for ing in include:
                if ing['name']:
                    self.constraints["ingredients"]['include']['name'].append(f"'{ing['name']}'")
                if ing['basic_taste']:
                    self.constraints["ingredients"]['include']['basic_taste'].append(f"'{ing['basic_taste']}'")
                if ing['food_category']:
                    self.constraints["ingredients"]['include']['food_category'].append(f"'{ing['food_category']}'")

        if exclude:
            for ing in exclude:
                if ing['name']:
                    self.constraints["ingredients"]['exclude']['name'].append(f"'{ing['name']}'")
                if ing['basic_taste']:
                    self.constraints["ingredients"]['exclude']['basic_taste'].append(f"'{ing['basic_taste']}'")
                if ing['food_category']:
                    self.constraints["ingredients"]['exclude']['food_category'].append(f"'{ing['food_category']}'")

    def build(self):
        """Build the XPath query from the accumulated constraints."""
        parts = []
        if self.constraints['dietary_preference']['include']:
            dp_query = " or ".join(self.constraints['dietary_preference']['include'])
            parts.append(f"dietary_preference[{dp_query}]")
        if self.constraints['dietary_preference']['exclude']:
            dp_query = " and ".join(self.constraints['dietary_preference']['exclude'])
            parts.append(f"dietary_preference[{dp_query}]")

        if len(parts) == 0:
            parts.append('dietary_preference')
        elif 'dietary_preference' not in parts[-1]:
            parts.append('dietary_preference')

        if self.constraints['course_type']['include']:
            ct_query = " or ".join(self.constraints['course_type']['include'])
            parts.append(f"course_type[{ct_query}]")
        if self.constraints['course_type']['exclude']:
            ct_query = " and ".join(self.constraints['course_type']['exclude'])
            parts.append(f"course_type[{ct_query}]")

        if len(parts) == 0:
            parts.append('course_type')
        elif 'course_type' not in parts[-1]:
            parts.append('course_type')

        if self.constraints['cuisine']['include']:
            cuisine_query = " or ".join(self.constraints['cuisine']['include'])
            parts.append(f"cuisine[{cuisine_query}]/cookingrecipes//cookingrecipe")
        if self.constraints['cuisine']['exclude']:
            cuisine_query = " and ".join(self.constraints['cuisine']['exclude'])
            parts.append(f"cuisine[{cuisine_query}]/cookingrecipes//cookingrecipe")

        if len(parts) == 0:
            parts.append('cuisine/cookingrecipes//cookingrecipe')
        elif 'cookingrecipes//cookingrecipe' not in parts[-1]:
            parts.append('cuisine/cookingrecipes//cookingrecipe')


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
        return xpath_query

    def reset(self):
        """Reset the accumulated constraints."""
        self.constraints = {"dietary_preference": {'include':[],'exclude':[]}, 
                            "course_type": {'include':[],'exclude':[]}, 
                            "cuisine": {'include':[],'exclude':[]}, 
                            "ingredients": {'include':{"name":[],"food_category":[],"basic_taste":[]},'exclude':{"name":[],"food_category":[],"basic_taste":[]}}}
