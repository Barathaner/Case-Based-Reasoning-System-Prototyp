from datasetcreation.create_case_library import create_case_library
from cbr.case_library import CaseLibrary, CookingRecipe,ConstraintQueryBuilder
from cbr.retrieve import *
from utils.printutils import format_xmlrecipes_to_str
import os


CASELIBRARYPATH = os.path.join(os.path.dirname(__file__), '../data/case_library.xml')
constraints= {"dietary_preference": None,
        "course_type": {'include':['dessert'],'exclude':['side']},
        "ingredients": None,
        "cuisine":{'exclude':['french'],'include':['italian','thai']}
}
query_builder = ConstraintQueryBuilder()
query = query_builder.build()
print(query)  # Outputs the constructed XPath query
recipes, sim_list, index_retrieved, retrieved_case = retrieve( constraints, cl)
print(format_xmlrecipes_to_str(recipes))
print(retrieved_case)
print("Done") 
#{'include': [{'name':'butter or margarine ','food_category':None,'basic_taste':None}], 'exclude':[]}