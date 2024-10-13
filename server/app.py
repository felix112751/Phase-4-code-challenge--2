#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

# Set up the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


# Initialize the Flask application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE  # Configure the database URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable track modifications
app.json.compact = False  # Set JSON output formatting

# Set up database migration support
migrate = Migrate(app, db)
db.init_app(app)  # Initialize the database with the app

# Initialize Flask-RESTful API
api = Api(app)

# Create the tables if they don't exist
with app.app_context():
    db.create_all()

# Define a simple index route
@app.route("/")
def index():
    print("Index route accessed")
    return "<h1>Code challenge</h1>"

# Endpoint to get all restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()  # Query all restaurants
    # Return a list of restaurants without restaurant_pizzas details
    return [restaurant.to_dict(rules=['-restaurant_pizzas']) for restaurant in restaurants], 200

# Endpoint to get or delete a restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()  # Find restaurant by ID

    if request.method == 'GET':
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404  # Return error if not found
        else:
            return restaurant.to_dict(), 200  # Return restaurant details

    elif request.method == 'DELETE':
        if not restaurant:
            return {'error': 'Restaurant not found'}  # Return error if not found
        else: 
            db.session.delete(restaurant)  # Delete the restaurant
            db.session.commit()  # Commit changes to the database
            return {}, 204  # Return no content response

# Endpoint to get all pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()  # Query all pizzas
    # Return a list of pizzas without restaurant_pizzas details
    return [pizza.to_dict(rules=['-restaurant_pizzas']) for pizza in pizzas]

# Endpoint to create a new restaurant-pizza association
@app.route('/restaurant_pizzas', methods=['GET', 'POST'])
def create_new_pizza():
    json_data = request.get_json()  # Get JSON data from request

    try: 
        new_restaurant_pizza = RestaurantPizza(
            price=json_data.get('price'),  # Get price from JSON
            pizza_id=json_data.get('pizza_id'),  # Get pizza ID from JSON
            restaurant_id=json_data.get('restaurant_id')  # Get restaurant ID from JSON
        )
    except ValueError as e:
        return {'errors': ['validation errors']}, 400  # Return validation error

    db.session.add(new_restaurant_pizza)  # Add new association to the session
    db.session.commit()  # Commit changes to the database
    return new_restaurant_pizza.to_dict(), 201  # Return created association details

# Run the app if this script is executed
if __name__ == "__main__":
    app.run(port=5555, debug=True)
