class Query:
    def __init__(self, data=None):
        if data is not None:
            self.data = data
        else:
            self.data = {
                "ingredients": {
                    "include": {"name": [], "food_category": [], "basic_taste": []},
                    "exclude": {"name": [], "food_category": [], "basic_taste": []}
                },
                "course_type": {"include": [], "exclude": []},
                "cuisine": {"include": [], "exclude": []},
                "dietary_preference": {"include": [], "exclude": []}
            }
    
    def set_course_type(self, values, exclude=False):
        key = "exclude" if exclude else "include"
        self.data["course_type"][key] = values

    def set_dietary_preference(self, values, exclude=False):
        key = "exclude" if exclude else "include"
        self.data["dietary_preference"][key] = values

    def set_cuisine(self, values, exclude=False):
        key = "exclude" if exclude else "include"
        self.data["cuisine"][key] = values


    def set_ingredients(self, values,category, exclude=False):
        key = "exclude" if exclude else "include"
        self.data["ingredients"][key][category] = values


    def get_ingredients(self):
        return self.data["ingredients"]["include"]["name"]
    
    def get_exc_ingredients(self):
        return self.data["ingredients"]["exclude"]["name"]
    
    def get_food_category(self):
        return self.data["ingredients"]["include"]["food_category"]
    
    def get_basic_taste(self):
        return self.data["ingredients"]["include"]["basic_taste"]
    
    def get_data(self):
        return self.data
    
    def build_query(self):
        return self.data
