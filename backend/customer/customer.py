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


class Customer(db.Model):
    __tablename__ = "customer"

    customer_id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.DECIMAL(10, 8), nullable=False)
    longitude = db.Column(db.DECIMAL(11, 8), nullable=False)
    loyalty_points = db.Column(db.Integer, nullable=False, default=0)
    loyalty_status = db.Column(db.Enum('Bronze', 'Silver', 'Gold'), nullable=False, default='Bronze')
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)

    def __init__(self, customer_id, username, password_hash, name, email, phone_number, latitude, longitude, 
                loyalty_points=0, loyalty_status='Bronze'):
        self.customer_id = customer_id
        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.latitude = latitude
        self.longitude = longitude
        self.loyalty_points = loyalty_points
        self.loyalty_status = loyalty_status

    def json(self):
        return {
            "customer_id": self.customer_id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "loyalty_points": self.loyalty_points,
            "loyalty_status": self.loyalty_status,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


@app.route("/customer")
def get_all():
    customerlist = db.session.scalars(db.select(Customer)).all()

    if len(customerlist):
        return jsonify(
            {
                "code": 200,
                "data": {"customers": [customer.json() for customer in customerlist]},
            }
        )
    return jsonify({"code": 404, "message": "There are no customers."}), 404


@app.route("/customer/<string:customer_id>")
def find_by_customer_id(customer_id):
    customer = db.session.scalar(db.select(Customer).filter_by(customer_id=customer_id))

    if customer:
        return jsonify({"code": 200, "data": customer.json()})
    return jsonify({"code": 404, "message": "Customer not found."}), 404


@app.route("/customer/username/<string:username>")
def find_by_username(username):
    customer = db.session.scalar(db.select(Customer).filter_by(username=username))

    if customer:
        return jsonify({"code": 200, "data": customer.json()})
    return jsonify({"code": 404, "message": "Customer not found."}), 404


@app.route("/customer/email/<string:email>")
def find_by_email(email):
    customer = db.session.scalar(db.select(Customer).filter_by(email=email))

    if customer:
        return jsonify({"code": 200, "data": customer.json()})
    return jsonify({"code": 404, "message": "Customer not found."}), 404


@app.route("/customer/<string:customer_id>", methods=["POST"])
def create_customer(customer_id):
    if db.session.scalar(db.select(Customer).filter_by(customer_id=customer_id)):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"customer_id": customer_id},
                    "message": "Customer already exists.",
                }
            ),
            400,
        )

    data = request.get_json()
    
    # Check if username already exists
    if db.session.scalar(db.select(Customer).filter_by(username=data.get('username'))):
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
    
    # Check if email already exists
    if db.session.scalar(db.select(Customer).filter_by(email=data.get('email'))):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"email": data.get('email')},
                    "message": "Email already exists.",
                }
            ),
            400,
        )

    customer = Customer(customer_id, **data)

    try:
        db.session.add(customer)
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"customer_id": customer_id},
                    "message": "An error occurred creating the customer: " + str(e),
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": customer.json()}), 201


@app.route("/customer/<string:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    customer = db.session.scalar(db.select(Customer).filter_by(customer_id=customer_id))
    
    if not customer:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"customer_id": customer_id},
                    "message": "Customer not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    # If updating username, check if it already exists
    if 'username' in data and data['username'] != customer.username:
        if db.session.scalar(db.select(Customer).filter_by(username=data['username'])):
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
    
    # If updating email, check if it already exists
    if 'email' in data and data['email'] != customer.email:
        if db.session.scalar(db.select(Customer).filter_by(email=data['email'])):
            return (
                jsonify(
                    {
                        "code": 400,
                        "data": {"email": data['email']},
                        "message": "Email already exists.",
                    }
                ),
                400,
            )

    try:
        for key, value in data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": customer.json(),
                "message": "Customer updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"customer_id": customer_id},
                    "message": "An error occurred updating the customer: " + str(e),
                }
            ),
            500,
        )


@app.route("/customer/<string:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = db.session.scalar(db.select(Customer).filter_by(customer_id=customer_id))
    
    if not customer:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"customer_id": customer_id},
                    "message": "Customer not found.",
                }
            ),
            404,
        )

    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Customer deleted successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"customer_id": customer_id},
                    "message": "An error occurred deleting the customer: " + str(e),
                }
            ),
            500,
        )


@app.route("/customer/<string:customer_id>/loyalty", methods=["PUT"])
def update_loyalty(customer_id):
    customer = db.session.scalar(db.select(Customer).filter_by(customer_id=customer_id))
    
    if not customer:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"customer_id": customer_id},
                    "message": "Customer not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'loyalty_points' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "loyalty_points field is required.",
                }
            ),
            400,
        )

    try:
        # Update loyalty points
        customer.loyalty_points = data['loyalty_points']
        
        # Update loyalty status based on points
        if customer.loyalty_points >= 300:
            customer.loyalty_status = 'Gold'
        elif customer.loyalty_points >= 100:
            customer.loyalty_status = 'Silver'
        else:
            customer.loyalty_status = 'Bronze'
        
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": customer.json(),
                "message": "Customer loyalty updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"customer_id": customer_id},
                    "message": "An error occurred updating customer loyalty: " + str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)