import xml.etree.ElementTree as ET
import os
import pandas as pd
import ast

# Define paths for the files involved in the process.
CASEBASEPATH = os.path.join(os.path.dirname(__file__), '../../data/case_base.xml')
CASELIBRARYPATH = os.path.join(os.path.dirname(__file__), '../../data/case_library.xml')
RECIPESAPATH = os.path.join(os.path.dirname(__file__), '../../data/Recipes.csv')
INGREDIENTSPATH = os.path.join(os.path.dirname(__file__), '../../data/ingredients.csv')

def create_case_base(recipespath=RECIPESAPATH, ingredientspath=INGREDIENTSPATH):
    """
    Reads recipes and their ingredients from CSV files and constructs an XML structure that represents
    each recipe with its detailed attributes and instructions.

    Parameters:
        recipespath (str): File path to the CSV file containing recipe data. Default is RECIPESAPATH.
        ingredientspath (str): File path to the CSV file containing ingredients data. Default is INGREDIENTSPATH.
    
    This function constructs an XML tree with root element "cookingrecipes", where each "cookingrecipe" element
    contains detailed nodes for name, course type, dietary preference, cuisine, ingredients, and cooking instructions.
    Ingredients and instructions are read from related data structures and converted into sub-elements under their
    respective parent elements. Text values are converted to lowercase to maintain consistency.
    """
    dfrecipes = pd.read_csv(recipespath)
    dfingredients = pd.read_csv(ingredientspath)
    root = ET.Element("cookingrecipes")
    for index, row in dfrecipes.iterrows():
        recipe = ET.SubElement(root, "cookingrecipe")
        ET.SubElement(recipe, "name").text = str(row['recipename']).lower()
        ET.SubElement(recipe, "course_type").text = str(row['course_type']).lower()
        ET.SubElement(recipe, "dietary_preference").text = str(row['dietary_preference']).lower()
        ET.SubElement(recipe, "cuisine").text = str(row['cuisine']).lower()
        
        ingredients = ET.SubElement(recipe, "ingredients")
        dfrecipeingredients = dfingredients[dfingredients['recipename'] == row['recipename']]
        for ingindex, ingrow in dfrecipeingredients.iterrows():
            ingredient = ET.SubElement(ingredients, "ingredient", amount=str(ingrow['amount']),
                                       unit=str(ingrow['unit']).lower(), basic_taste=str(ingrow['basictaste']).lower(),
                                       food_category=str(ingrow['foodcategory']).lower())
            ingredient.text = str(ingrow['ingredient']).lower()
        
        instructions = ET.SubElement(recipe, "instructions")
        instructionslist = ast.literal_eval(str(row['instructions']))
        for instruction in instructionslist:
            ET.SubElement(instructions, "step").text = instruction
        
        # Setting default values for various aspects of the recipe's utility and evaluation.
        ET.SubElement(recipe, "utility").text = "1.0"
        ET.SubElement(recipe, "derivation").text = "original"
        ET.SubElement(recipe, "evaluation").text = "success"
        ET.SubElement(recipe, "UaS").text = "0"
        ET.SubElement(recipe, "UaF").text = "0"
        ET.SubElement(recipe, "success_count").text = "0"
        ET.SubElement(recipe, "failure_count").text = "0"
        
    tree = ET.ElementTree(root)
    tree.write(CASEBASEPATH, encoding='utf-8', xml_declaration=True)
    
def create_case_library():
    """
    Constructs a structured XML library that categorizes recipes from the existing case base XML file by
    dietary preference, course type, and cuisine, facilitating easier access and organization.

    This function checks if the case base XML exists. If not, it creates one using create_case_base(). 
    It then reads the XML and organizes recipes into a hierarchical structure based on their attributes,
    writing the result into a new XML file.
    """
    if not os.path.exists(CASEBASEPATH):
        create_case_base()
    else:
        print("Case base already exists")

    root = ET.parse(CASEBASEPATH).getroot()
    case_library = ET.Element("case_library")
    for dp in {elem.text for elem in root.findall(".//dietary_preference")}:
        dp_elem = ET.SubElement(case_library, "dietary_preference", type=dp)
        for ct in {elem.text for elem in root.findall(".//course_type")}:
            ct_elem = ET.SubElement(dp_elem, "course_type", type=ct)
            for cs in {elem.text for elem in root.findall(".//cuisine")}:
                cs_elem = ET.SubElement(ct_elem, "cuisine", type=cs)
                recipes = [r for r in root.findall(".//cookingrecipe") if
                           r.find("course_type").text.lower() == ct.lower() and
                           r.find("dietary_preference").text.lower() == dp.lower() and
                           r.find("cuisine").text.lower() == cs.lower()]
                if recipes:
                    recipes_elem = ET.SubElement(cs_elem, "cookingrecipes")
                    for recipe in recipes:
                        recipes_elem.append(recipe)

    tree = ET.ElementTree(case_library)
    tree.write(CASELIBRARYPATH, encoding='utf-8', xml_declaration=True)
    
    