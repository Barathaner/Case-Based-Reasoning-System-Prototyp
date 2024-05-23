from flask import Flask, render_template, request, redirect, url_for


class CBR:
    def generate_recipe(self, name, course_type, dietary_preference, cuisine_origin,
                        basic_taste_include, basic_taste_exclude,
                        food_category_include, food_category_exclude):
        # Generate a new recipe based on the input criteria
        # For simplicity, return a dummy recipe
        adapted_recipe = {
            "name": name,
            "course_type": course_type,
            "dietary_preference": dietary_preference,
            "cuisine_origin": cuisine_origin,
            "basic_taste_include": basic_taste_include,
            "basic_taste_exclude": basic_taste_exclude,
            "food_category_include": food_category_include,
            "food_category_exclude": food_category_exclude,
            "details": "Generated recipe details..."
        }
        return adapted_recipe

    def learn_new_recipe(self, recipe_name, score):
        # Learn the new recipe by adding it to the case base with the evaluation score
        print(f"New recipe added: {recipe_name} with score {score}")


app = Flask(__name__)
cbr = CBR()

options = {
    "course_types": ["Appetizer", "Main Course", "Dessert"],
    "dietary_preferences": ["Vegetarian", "Vegan", "Gluten-Free", "None"],
    "cuisine_origins": ["Italian", "Chinese", "Mexican", "Indian"],
    "basic_tastes": ["Sweet", "Sour", "Salty", "Bitter", "Umami"],
    "food_categories": ["Fruit", "Vegetable", "Meat", "Dairy", "Grain"]
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        recipe_name = request.form['recipe_name']
        course_type = request.form['course_type']
        dietary_preference = request.form['dietary_preference']
        cuisine_origin = request.form['cuisine_origin']
        basic_taste_include = ', '.join(request.form.getlist('basic_taste_include'))
        basic_taste_exclude = ', '.join(request.form.getlist('basic_taste_exclude'))
        food_category_include = ', '.join(request.form.getlist('food_category_include'))
        food_category_exclude = ', '.join(request.form.getlist('food_category_exclude'))

        adapted_recipe = cbr.generate_recipe(recipe_name, course_type, dietary_preference, cuisine_origin,
                                             basic_taste_include, basic_taste_exclude,
                                             food_category_include, food_category_exclude)

        return render_template('index.html', options=options, adapted_recipe=adapted_recipe)
    return render_template('index.html', options=options)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    recipe_name = request.form['recipe_name']
    score = request.form['score']
    cbr.learn_new_recipe(recipe_name, int(score))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
