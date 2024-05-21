class CaseLibrary:
    def __init__(self,case_library_path):
        self.case_library_path = case_library_path
        self.case_library = self.load_case_library()
    
    def load_case_library(self):
        with open(self.case_library_path, 'r') as file:
            case_library = json.load(file)
        return case_library
    
    def add_case(self,case):
        self.case_library.append(case)
        
    def remove_case(self,case):
        self.case_library.remove(case)
        
    