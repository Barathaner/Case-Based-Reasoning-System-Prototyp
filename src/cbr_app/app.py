from flask import Flask, render_template, request, redirect, url_for

from src.cbr.cbr import CBR
from src.cbr.query import Query

app = Flask(__name__)
cbr = CBR()

options = {
    "course_types": cbr.case_library.course_types,
    "dietary_preferences": cbr.case_library.dietary_preferences_types,
    "cuisine_origins": cbr.case_library.cuisines_types,
    "basic_tastes": cbr.case_library.basic_tastes_types,
    "food_categories": cbr.case_library.food_categories_types
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            "dietary_preference": {'include': [request.form['dietary_preference']], 'exclude': []},
            "course_type": {'include': [request.form['course_type']], 'exclude': []},
            "ingredients": {
                "include": {"name": [], "food_category": request.form.getlist('food_category_include'),
                            "basic_taste": request.form.getlist('basic_taste_include')},
                "exclude": {"name": [], "food_category": request.form.getlist('food_category_exclude'),
                            "basic_taste": request.form.getlist('basic_taste_exclude')}
            },
            "cuisine": {'exclude': [], 'include': [request.form['cuisine_origin']]}
        }

        print(data)

        query_format = Query(data)

        retrieved_recipe, adapted_recipe = cbr.run_query(query_format, request.form['recipe_name'])

        return render_template('index.html', options=options, adapted_recipe=adapted_recipe)
    return render_template('index.html', options=options)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    score = request.form['score']
    cbr.evaluate(int(score))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
