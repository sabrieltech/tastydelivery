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


class RestaurantInventory(db.Model):
    __tablename__ = "restaurant_inventory"

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(db.String(32), nullable=False)
    item_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, restaurant_id, item_name, price, stock_quantity):
        self.restaurant_id = restaurant_id
        self.item_name = item_name
        self.price = price
        self.stock_quantity = stock_quantity

    def json(self):
        return {
            "item_id": self.item_id,
            "restaurant_id": self.restaurant_id,
            "item_name": self.item_name,
            "price": float(self.price),
            "stock_quantity": self.stock_quantity,
            "last_updated": self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }


@app.route("/restaurant_inventory")
def get_all():
    inventory_items = db.session.scalars(db.select(RestaurantInventory)).all()

    if len(inventory_items):
        return jsonify(
            {
                "code": 200,
                "data": {"inventory_items": [item.json() for item in inventory_items]},
            }
        )
    return jsonify({"code": 404, "message": "There are no inventory items."}), 404


@app.route("/restaurant_inventory/<int:item_id>")
def find_by_item_id(item_id):
    inventory_item = db.session.scalar(db.select(RestaurantInventory).filter_by(item_id=item_id))

    if inventory_item:
        return jsonify({"code": 200, "data": inventory_item.json()})
    return jsonify({"code": 404, "message": "Inventory item not found."}), 404


@app.route("/restaurant_inventory/restaurant/<string:restaurant_id>")
def find_by_restaurant_id(restaurant_id):
    inventory_items = db.session.scalars(db.select(RestaurantInventory).filter_by(restaurant_id=restaurant_id)).all()

    if len(inventory_items):
        return jsonify({
            "code": 200,
            "data": {"inventory_items": [item.json() for item in inventory_items]}
        })
    return jsonify({"code": 404, "message": "No inventory items found for this restaurant."}), 404


@app.route("/restaurant_inventory", methods=["POST"])
def create_inventory_item():
    data = request.get_json()
    
    # Check if required fields are provided
    required_fields = ["restaurant_id", "item_name", "price", "stock_quantity"]
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "message": f"Field '{field}' is required."}), 400
    
    # Create new inventory item
    inventory_item = RestaurantInventory(
        restaurant_id=data["restaurant_id"],
        item_name=data["item_name"],
        price=data["price"],
        stock_quantity=data["stock_quantity"]
    )

    try:
        db.session.add(inventory_item)
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "message": "An error occurred creating the inventory item: " + str(e),
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": inventory_item.json()}), 201


@app.route("/restaurant_inventory/<int:item_id>", methods=["PUT"])
def update_inventory_item(item_id):
    inventory_item = db.session.scalar(db.select(RestaurantInventory).filter_by(item_id=item_id))
    
    if not inventory_item:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"item_id": item_id},
                    "message": "Inventory item not found.",
                }
            ),
            404,
        )

    data = request.get_json()

    try:
        for key, value in data.items():
            if hasattr(inventory_item, key):
                setattr(inventory_item, key, value)
        
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": inventory_item.json(),
                "message": "Inventory item updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"item_id": item_id},
                    "message": "An error occurred updating the inventory item: " + str(e),
                }
            ),
            500,
        )


@app.route("/restaurant_inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    inventory_item = db.session.scalar(db.select(RestaurantInventory).filter_by(item_id=item_id))
    
    if not inventory_item:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"item_id": item_id},
                    "message": "Inventory item not found.",
                }
            ),
            404,
        )

    try:
        db.session.delete(inventory_item)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Inventory item deleted successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"item_id": item_id},
                    "message": "An error occurred deleting the inventory item: " + str(e),
                }
            ),
            500,
        )


@app.route("/restaurant_inventory/update_stock/<int:item_id>", methods=["PUT"])
def update_stock(item_id):
    inventory_item = db.session.scalar(db.select(RestaurantInventory).filter_by(item_id=item_id))
    
    if not inventory_item:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"item_id": item_id},
                    "message": "Inventory item not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'stock_quantity' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "stock_quantity field is required.",
                }
            ),
            400,
        )

    try:
        inventory_item.stock_quantity = data['stock_quantity']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": inventory_item.json(),
                "message": "Stock quantity updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"item_id": item_id},
                    "message": "An error occurred updating stock quantity: " + str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008, debug=True)