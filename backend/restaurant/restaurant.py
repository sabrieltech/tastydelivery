from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/fooddelivery1"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Restaurant(db.Model):
    __tablename__ = "restaurant"

    restaurant_id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.DECIMAL(10, 8), nullable=False)
    longitude = db.Column(db.DECIMAL(11, 8), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    cuisine_type = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.DECIMAL(2, 1), nullable=False, default=0.0)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)

    def __init__(self, restaurant_id, username, password_hash, name, latitude, longitude, 
                contact_number, cuisine_type, rating=0.0):
        self.restaurant_id = restaurant_id
        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.contact_number = contact_number
        self.cuisine_type = cuisine_type
        self.rating = rating

    def json(self):
        return {
            "restaurant_id": self.restaurant_id,
            "username": self.username,
            "name": self.name,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "contact_number": self.contact_number,
            "cuisine_type": self.cuisine_type,
            "rating": float(self.rating),
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


@app.route("/restaurant")
def get_all():
    restaurantlist = db.session.scalars(db.select(Restaurant)).all()

    if len(restaurantlist):
        return jsonify(
            {
                "code": 200,
                "data": {"restaurants": [restaurant.json() for restaurant in restaurantlist]},
            }
        )
    return jsonify({"code": 404, "message": "There are no restaurants."}), 404


@app.route("/restaurant/<string:restaurant_id>")
def find_by_restaurant_id(restaurant_id):
    restaurant = db.session.scalar(db.select(Restaurant).filter_by(restaurant_id=restaurant_id))

    if restaurant:
        return jsonify({"code": 200, "data": restaurant.json()})
    return jsonify({"code": 404, "message": "Restaurant not found."}), 404


@app.route("/restaurant/username/<string:username>")
def find_by_username(username):
    restaurant = db.session.scalar(db.select(Restaurant).filter_by(username=username))

    if restaurant:
        return jsonify({"code": 200, "data": restaurant.json()})
    return jsonify({"code": 404, "message": "Restaurant not found."}), 404


@app.route("/restaurant/cuisine/<string:cuisine_type>")
def find_by_cuisine(cuisine_type):
    restaurants = db.session.scalars(db.select(Restaurant).filter_by(cuisine_type=cuisine_type)).all()

    if len(restaurants):
        return jsonify({
            "code": 200,
            "data": {"restaurants": [restaurant.json() for restaurant in restaurants]}
        })
    return jsonify({"code": 404, "message": "No restaurants found with this cuisine type."}), 404


@app.route("/restaurant/<string:restaurant_id>", methods=["POST"])
def create_restaurant(restaurant_id):
    if db.session.scalar(db.select(Restaurant).filter_by(restaurant_id=restaurant_id)):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"restaurant_id": restaurant_id},
                    "message": "Restaurant already exists.",
                }
            ),
            400,
        )

    data = request.get_json()
    
    # Check if username already exists
    if db.session.scalar(db.select(Restaurant).filter_by(username=data.get('username'))):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"username": data.get('username')},
                    "message": "Username already exists.",
                }
            ),
            400,
        )
    
    restaurant = Restaurant(restaurant_id, **data)

    try:
        db.session.add(restaurant)
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"restaurant_id": restaurant_id},
                    "message": "An error occurred creating the restaurant: " + str(e),
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": restaurant.json()}), 201


@app.route("/restaurant/<string:restaurant_id>", methods=["PUT"])
def update_restaurant(restaurant_id):
    restaurant = db.session.scalar(db.select(Restaurant).filter_by(restaurant_id=restaurant_id))
    
    if not restaurant:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"restaurant_id": restaurant_id},
                    "message": "Restaurant not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    # If updating username, check if it already exists
    if 'username' in data and data['username'] != restaurant.username:
        if db.session.scalar(db.select(Restaurant).filter_by(username=data['username'])):
            return (
                jsonify(
                    {
                        "code": 400,
                        "data": {"username": data['username']},
                        "message": "Username already exists.",
                    }
                ),
                400,
            )

    try:
        for key, value in data.items():
            if hasattr(restaurant, key):
                setattr(restaurant, key, value)
        
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": restaurant.json(),
                "message": "Restaurant updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"restaurant_id": restaurant_id},
                    "message": "An error occurred updating the restaurant: " + str(e),
                }
            ),
            500,
        )


@app.route("/restaurant/<string:restaurant_id>", methods=["DELETE"])
def delete_restaurant(restaurant_id):
    restaurant = db.session.scalar(db.select(Restaurant).filter_by(restaurant_id=restaurant_id))
    
    if not restaurant:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"restaurant_id": restaurant_id},
                    "message": "Restaurant not found.",
                }
            ),
            404,
        )

    try:
        db.session.delete(restaurant)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Restaurant deleted successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"restaurant_id": restaurant_id},
                    "message": "An error occurred deleting the restaurant: " + str(e),
                }
            ),
            500,
        )


@app.route("/restaurant/<string:restaurant_id>/rating", methods=["PUT"])
def update_rating(restaurant_id):
    restaurant = db.session.scalar(db.select(Restaurant).filter_by(restaurant_id=restaurant_id))
    
    if not restaurant:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"restaurant_id": restaurant_id},
                    "message": "Restaurant not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'rating' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "Rating field is required.",
                }
            ),
            400,
        )

    try:
        # Validate rating is between 0 and 5
        rating = float(data['rating'])
        if rating < 0 or rating > 5:
            return (
                jsonify(
                    {
                        "code": 400,
                        "message": "Rating must be between 0 and 5.",
                    }
                ),
                400,
            )
            
        restaurant.rating = rating
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": restaurant.json(),
                "message": "Restaurant rating updated successfully."
            }
        )
    except ValueError:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "Rating must be a number.",
                }
            ),
            400,
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"restaurant_id": restaurant_id},
                    "message": "An error occurred updating restaurant rating: " + str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=True)