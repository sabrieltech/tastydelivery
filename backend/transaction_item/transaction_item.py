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


class TransactionItem(db.Model):
    __tablename__ = "transaction_item"

    transaction_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.String(32), nullable=False)
    restaurant_id = db.Column(db.String(32), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(db.DECIMAL(10, 2), nullable=False)
    total_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)

    def __init__(self, transaction_id, restaurant_id, item_id, quantity, price_per_item, total_price):
        self.transaction_id = transaction_id
        self.restaurant_id = restaurant_id
        self.item_id = item_id
        self.quantity = quantity
        self.price_per_item = price_per_item
        self.total_price = total_price

    def json(self):
        return {
            "transaction_item_id": self.transaction_item_id,
            "transaction_id": self.transaction_id,
            "restaurant_id": self.restaurant_id,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "price_per_item": float(self.price_per_item),
            "total_price": float(self.total_price),
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


@app.route("/transaction_item")
def get_all():
    transaction_items = db.session.scalars(db.select(TransactionItem)).all()

    if len(transaction_items):
        return jsonify(
            {
                "code": 200,
                "data": {"transaction_items": [item.json() for item in transaction_items]},
            }
        )
    return jsonify({"code": 404, "message": "There are no transaction items."}), 404


@app.route("/transaction_item/<int:transaction_item_id>")
def find_by_transaction_item_id(transaction_item_id):
    transaction_item = db.session.scalar(db.select(TransactionItem).filter_by(transaction_item_id=transaction_item_id))

    if transaction_item:
        return jsonify({"code": 200, "data": transaction_item.json()})
    return jsonify({"code": 404, "message": "Transaction item not found."}), 404


@app.route("/transaction_item/transaction/<string:transaction_id>")
def find_by_transaction_id(transaction_id):
    transaction_items = db.session.scalars(db.select(TransactionItem).filter_by(transaction_id=transaction_id)).all()

    if len(transaction_items):
        return jsonify({
            "code": 200,
            "data": {"transaction_items": [item.json() for item in transaction_items]}
        })
    return jsonify({"code": 404, "message": "No transaction items found for this transaction."}), 404


@app.route("/transaction_item/restaurant/<string:restaurant_id>")
def find_by_restaurant_id(restaurant_id):
    transaction_items = db.session.scalars(db.select(TransactionItem).filter_by(restaurant_id=restaurant_id)).all()

    if len(transaction_items):
        return jsonify({
            "code": 200,
            "data": {"transaction_items": [item.json() for item in transaction_items]}
        })
    return jsonify({"code": 404, "message": "No transaction items found for this restaurant."}), 404


@app.route("/transaction_item", methods=["POST"])
def create_transaction_item():
    data = request.get_json()
    
    # Check for required fields
    required_fields = ["transaction_id", "restaurant_id", "item_id", "quantity", "price_per_item", "total_price"]
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "message": f"Field '{field}' is required."}), 400
    
    # Create new transaction item
    transaction_item = TransactionItem(
        transaction_id=data["transaction_id"],
        restaurant_id=data["restaurant_id"],
        item_id=data["item_id"],
        quantity=data["quantity"],
        price_per_item=data["price_per_item"],
        total_price=data["total_price"]
    )

    try:
        db.session.add(transaction_item)
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "message": "An error occurred creating the transaction item: " + str(e),
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": transaction_item.json()}), 201


@app.route("/transaction_item/<int:transaction_item_id>", methods=["PUT"])
def update_transaction_item(transaction_item_id):
    transaction_item = db.session.scalar(db.select(TransactionItem).filter_by(transaction_item_id=transaction_item_id))
    
    if not transaction_item:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"transaction_item_id": transaction_item_id},
                    "message": "Transaction item not found.",
                }
            ),
            404,
        )

    data = request.get_json()

    try:
        for key, value in data.items():
            if hasattr(transaction_item, key):
                setattr(transaction_item, key, value)
        
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": transaction_item.json(),
                "message": "Transaction item updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"transaction_item_id": transaction_item_id},
                    "message": "An error occurred updating the transaction item: " + str(e),
                }
            ),
            500,
        )


@app.route("/transaction_item/<int:transaction_item_id>", methods=["DELETE"])
def delete_transaction_item(transaction_item_id):
    transaction_item = db.session.scalar(db.select(TransactionItem).filter_by(transaction_item_id=transaction_item_id))
    
    if not transaction_item:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"transaction_item_id": transaction_item_id},
                    "message": "Transaction item not found.",
                }
            ),
            404,
        )

    try:
        db.session.delete(transaction_item)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Transaction item deleted successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"transaction_item_id": transaction_item_id},
                    "message": "An error occurred deleting the transaction item: " + str(e),
                }
            ),
            500,
        )


@app.route("/transaction_item/batch", methods=["POST"])
def create_batch_transaction_items():
    data = request.get_json()
    
    if 'items' not in data or not isinstance(data['items'], list):
        return jsonify({"code": 400, "message": "Field 'items' is required and must be a list."}), 400
    
    if len(data['items']) == 0:
        return jsonify({"code": 400, "message": "Items list cannot be empty."}), 400
    
    created_items = []
    
    try:
        for item_data in data['items']:
            # Check for required fields
            required_fields = ["transaction_id", "restaurant_id", "item_id", "quantity", "price_per_item", "total_price"]
            for field in required_fields:
                if field not in item_data:
                    return jsonify({"code": 400, "message": f"Field '{field}' is required for each item."}), 400
            
            # Create new transaction item
            transaction_item = TransactionItem(
                transaction_id=item_data["transaction_id"],
                restaurant_id=item_data["restaurant_id"],
                item_id=item_data["item_id"],
                quantity=item_data["quantity"],
                price_per_item=item_data["price_per_item"],
                total_price=item_data["total_price"]
            )
            
            db.session.add(transaction_item)
            created_items.append(transaction_item)
        
        db.session.commit()
        return jsonify({
            "code": 201, 
            "data": {"transaction_items": [item.json() for item in created_items]},
            "message": f"Successfully created {len(created_items)} transaction items."
        }), 201
    except Exception as e:
        db.session.rollback()
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "message": "An error occurred creating the transaction items: " + str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)