from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define metadata with a naming convention for foreign keys
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy with the custom metadata
db = SQLAlchemy(metadata=metadata)

# Restaurant model representing the 'restaurants' table
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String)  # Restaurant name
    address = db.Column(db.String)  # Restaurant address

    # Relationship with RestaurantPizza
    # When a Restaurant is deleted, associated RestaurantPizza records are also deleted
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', 
        back_populates='restaurant', 
        cascade='all, delete-orphan'
    )

    # Serialization rules to exclude certain attributes
    serialize_rules = ['-restaurant_pizzas.restaurant']

    def __repr__(self):
        return f"<Restaurant {self.name}>"  # String representation


# Pizza model representing the 'pizzas' table
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String)  # Pizza name
    ingredients = db.Column(db.String)  # Pizza ingredients

    # Relationship with RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza')

    # Serialization rules to exclude certain attributes
    serialize_rules = ['-restaurant_pizzas.pizza']

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"  # String representation


# RestaurantPizza model representing the 'restaurant_pizzas' table
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    price = db.Column(db.Integer, nullable=False)  # Price of the pizza
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))  # Foreign key to Pizza
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))  # Foreign key to Restaurant

    # Relationships with Restaurant and Pizza
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')

    # Serialization rules to exclude certain attributes
    serialize_rules = ['-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas']

    # Validation for the price field
    @validates('price')
    def validates_price(self, key, new_price):
        if not (1 <= new_price <= 30):
            raise ValueError('Price must be between 1 and 30.')  # Raise error if price is out of bounds
        else:
            return new_price  # Return the validated price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"  # String representation
