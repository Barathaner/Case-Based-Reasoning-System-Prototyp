from src.cbr.cbr import CBR
from src.cbr.query import Query
import random
import string
import time


def random_subset(items: list):
    # Generate a random subset size between 1 and the maximum possible number
    subset_size = random.randint(1, min(len(items), 5))

    # Get a random subset
    subset = random.sample(items, subset_size)

    return subset


def random_item(items: list):
    subset_size = random.randint(0, 1)

    if subset_size == 0:
        return []

    # Get a random subset
    subset = random.sample(items, subset_size)

    return subset


def random_query(cbr: CBR):
    options = {
        "course_types": cbr.case_library.course_types,
        "dietary_preferences": cbr.case_library.dietary_preferences_types,
        "cuisine_origins": cbr.case_library.cuisines_types,
        "basic_tastes": cbr.case_library.basic_tastes_types,
        "food_categories": cbr.case_library.food_categories_types
    }

    data = {
        "dietary_preference": {'include': random_item(options["dietary_preferences"]),
                               'exclude': []},
        "course_type": {'include': random_item(options["course_types"]),
                        'exclude': []},
        "ingredients": {
            "include": {"name": [], "food_category": random_subset(options["food_categories"]),
                        "basic_taste": random_subset(options["food_categories"])},
            "exclude": {"name": [], "food_category": [],
                        "basic_taste": []}
        },
        "cuisine": {'exclude': random_item(options["cuisine_origins"]),
                    'include': []}
    }

    query_format = Query(data)

    # Define the pool of characters (letters and digits)
    characters = string.ascii_letters + string.digits

    # Generate a random string of length 20
    random_string = ''.join(random.choices(characters, k=10))

    t0 = time.time()

    _, _ = cbr.run_query(query_format, random_string)

    score = random.randint(1, 10)
    cbr.evaluate(int(score))

    return time.time()-t0


cbr = CBR()

for i in range(100):
    print(random_query(cbr))
