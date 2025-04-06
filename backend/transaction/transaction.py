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


class Transaction(db.Model):
    __tablename__ = "transaction"

    transaction_id = db.Column(db.String(32), primary_key=True)
    customer_id = db.Column(db.String(32), nullable=False)
    food_cost = db.Column(db.DECIMAL(10, 2), nullable=False)
    delivery_cost = db.Column(db.DECIMAL(10, 2), nullable=False)
    loyalty_discount_percentage = db.Column(db.DECIMAL(5, 2), nullable=False, default=0.00)
    total_price_after_discount = db.Column(db.DECIMAL(10, 2), nullable=False)
    loyalty_points_added = db.Column(db.Integer, nullable=False, default=0)
    current_loyalty_points = db.Column(db.Integer, nullable=False, default=0)
    current_loyalty_status = db.Column(db.Enum('Bronze', 'Silver', 'Gold'), nullable=False, default='Bronze')
    status = db.Column(db.Enum('Pending', 'Submitted', 'Paid', 'Refunded', 'Cancelled', 'Delivered'), nullable=False, default='Pending')
    voucher_id = db.Column(db.String(32), nullable=True)
    rider_id = db.Column(db.String(32), nullable=True)
    stripe_session_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, transaction_id, customer_id, food_cost, delivery_cost, 
                loyalty_discount_percentage, total_price_after_discount, 
                loyalty_points_added, current_loyalty_points, current_loyalty_status, 
                status='Pending', voucher_id=None, rider_id=None, stripe_session_id=None):
        self.transaction_id = transaction_id
        self.customer_id = customer_id
        self.food_cost = food_cost
        self.delivery_cost = delivery_cost
        self.loyalty_discount_percentage = loyalty_discount_percentage
        self.total_price_after_discount = total_price_after_discount
        self.loyalty_points_added = loyalty_points_added
        self.current_loyalty_points = current_loyalty_points
        self.current_loyalty_status = current_loyalty_status
        self.status = status
        self.voucher_id = voucher_id
        self.rider_id = rider_id
        self.stripe_session_id = stripe_session_id

    def json(self):
        return {
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "food_cost": float(self.food_cost),
            "delivery_cost": float(self.delivery_cost),
            "loyalty_discount_percentage": float(self.loyalty_discount_percentage),
            "total_price_after_discount": float(self.total_price_after_discount),
            "loyalty_points_added": self.loyalty_points_added,
            "current_loyalty_points": self.current_loyalty_points,
            "current_loyalty_status": self.current_loyalty_status,
            "status": self.status,
            "voucher_id": self.voucher_id,
            "rider_id": self.rider_id,
            "stripe_session_id": self.stripe_session_id,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


@app.route("/transaction")
def get_all():
    transactions = db.session.scalars(db.select(Transaction)).all()

    if len(transactions):
        return jsonify(
            {
                "code": 200,
                "data": {"transactions": [transaction.json() for transaction in transactions]},
            }
        )
    return jsonify({"code": 404, "message": "There are no transactions."}), 404


@app.route("/transaction/<string:transaction_id>")
def find_by_transaction_id(transaction_id):
    transaction = db.session.scalar(db.select(Transaction).filter_by(transaction_id=transaction_id))

    if transaction:
        return jsonify({"code": 200, "data": transaction.json()})
    return jsonify({"code": 404, "message": "Transaction not found."}), 404


@app.route("/transaction/customer/<string:customer_id>")
def find_by_customer_id(customer_id):
    transactions = db.session.scalars(db.select(Transaction).filter_by(customer_id=customer_id)).all()

    if len(transactions):
        return jsonify({
            "code": 200,
            "data": {"transactions": [transaction.json() for transaction in transactions]}
        })
    return jsonify({"code": 404, "message": "No transactions found for this customer."}), 404


@app.route("/transaction/status/<string:status>")
def find_by_status(status):
    # Validate the status value
    valid_statuses = ['Pending', 'Submitted', 'Paid', 'Refunded', 'Cancelled', 'Delivered']
    if status not in valid_statuses:
        return jsonify({
            "code": 400,
            "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }), 400
        
    transactions = db.session.scalars(db.select(Transaction).filter_by(status=status)).all()

    if len(transactions):
        return jsonify({
            "code": 200,
            "data": {"transactions": [transaction.json() for transaction in transactions]}
        })
    return jsonify({"code": 404, "message": f"No transactions found with status '{status}'."}), 404


@app.route("/transaction", methods=["POST"])
def create_transaction():
    data = request.get_json()
    
    # Check if transaction_id provided and not already in use
    if 'transaction_id' not in data:
        return jsonify({"code": 400, "message": "transaction_id is required."}), 400
        
    transaction_id = data['transaction_id']
    if db.session.scalar(db.select(Transaction).filter_by(transaction_id=transaction_id)):
        return jsonify({
            "code": 400,
            "data": {"transaction_id": transaction_id},
            "message": "Transaction ID already exists."
        }), 400
    
    # Check for other required fields
    required_fields = [
        "customer_id", "food_cost", "delivery_cost", "loyalty_discount_percentage",
        "total_price_after_discount", "loyalty_points_added", "current_loyalty_points",
        "current_loyalty_status"
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "message": f"Field '{field}' is required."}), 400
    
    # Create new transaction
    transaction = Transaction(
        transaction_id=transaction_id,
        customer_id=data["customer_id"],
        food_cost=data["food_cost"],
        delivery_cost=data["delivery_cost"],
        loyalty_discount_percentage=data["loyalty_discount_percentage"],
        total_price_after_discount=data["total_price_after_discount"],
        loyalty_points_added=data["loyalty_points_added"],
        current_loyalty_points=data["current_loyalty_points"],
        current_loyalty_status=data["current_loyalty_status"],
        status=data.get("status", "Pending"),
        voucher_id=data.get("voucher_id"),
        rider_id=data.get("rider_id"),
        stripe_session_id=data.get("stripe_session_id")
    )

    try:
        db.session.add(transaction)
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"transaction_id": transaction_id},
                    "message": "An error occurred creating the transaction: " + str(e),
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": transaction.json()}), 201


@app.route("/transaction/<string:transaction_id>", methods=["PUT"])
def update_transaction(transaction_id):
    transaction = db.session.scalar(db.select(Transaction).filter_by(transaction_id=transaction_id))
    
    if not transaction:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"transaction_id": transaction_id},
                    "message": "Transaction not found.",
                }
            ),
            404,
        )

    data = request.get_json()

    try:
        for key, value in data.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": transaction.json(),
                "message": "Transaction updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"transaction_id": transaction_id},
                    "message": "An error occurred updating the transaction: " + str(e),
                }
            ),
            500,
        )


@app.route("/transaction/<string:transaction_id>/status", methods=["PUT"])
def update_status(transaction_id):
    transaction = db.session.scalar(db.select(Transaction).filter_by(transaction_id=transaction_id))
    
    if not transaction:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"transaction_id": transaction_id},
                    "message": "Transaction not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'status' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "status field is required.",
                }
            ),
            400,
        )

    # Validate the status value
    valid_statuses = ['Pending', 'Submitted', 'Paid', 'Refunded', 'Cancelled', 'Delivered']
    if data['status'] not in valid_statuses:
        return jsonify({
            "code": 400,
            "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }), 400

    try:
        transaction.status = data['status']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": transaction.json(),
                "message": "Transaction status updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"transaction_id": transaction_id},
                    "message": "An error occurred updating transaction status: " + str(e),
                }
            ),
            500,
        )


@app.route("/transaction/<string:transaction_id>/assign_rider", methods=["PUT"])
def assign_rider(transaction_id):
    transaction = db.session.scalar(db.select(Transaction).filter_by(transaction_id=transaction_id))
    
    if not transaction:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"transaction_id": transaction_id},
                    "message": "Transaction not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'rider_id' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "rider_id field is required.",
                }
            ),
            400,
        )

    try:
        transaction.rider_id = data['rider_id']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": transaction.json(),
                "message": "Rider assigned successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"transaction_id": transaction_id},
                    "message": "An error occurred assigning rider: " + str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5009, debug=True)
