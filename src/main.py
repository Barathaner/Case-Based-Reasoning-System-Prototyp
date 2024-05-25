from datasetcreation.create_case_library import create_case_library
from cbr.case_library import CaseLibrary, CookingRecipe,ConstraintQueryBuilder
from cbr.retrieve import *
from utils.printutils import format_xmlrecipes_to_str
import os


CASELIBRARYPATH = os.path.join(os.path.dirname(__file__), '../data/case_library.xml')
constraints= {
        "course_type": {'include':['dessert'],'exclude':['side']},
        "ingredients": {'include': [], 'exclude':[]},
        "cuisine":{'exclude':['french'],'include':['italian','thai']}
}
query_builder = ConstraintQueryBuilder()
query = query_builder.build()
print(query)  # Outputs the constructed XPath query
recipes, sim_list, index_retrieved, retrieved_case = retrieve( constraints, cl)

#i = len(recipes) - 1
#print(f"Similarity List: {i}")
#print(f"Category: {[e.text for e in recipes[i].findall('category')]}")
#print(f"Ingredients: {[e.text for e in recipes[i].findall('.//ingredients/ingredient')]}")
#print(f"Steps: {[e.text for e in recipes[i].findall('.//instructions/step')]}")
#print(f"Similarity List: {sim_list}")
#print(f"Index Max Similarity: {index_retrieved}")
#print(f"Category-Retrieved Case: {[e.text for e in retrieved_case.findall('category')]}")
#print(f"Ingredients-Retrieved Case: {[e.text for e in retrieved_case.findall('.//ingredients/ingredient')]}")
#print(f"Steps-Retrieved Case: {[e.text for e in retrieved_case.findall('.//instructions/step')]}")

#print("Done")
