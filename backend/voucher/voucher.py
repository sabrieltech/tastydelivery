from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, date

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/fooddelivery1"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Voucher(db.Model):
    __tablename__ = "voucher"

    voucher_id = db.Column(db.String(32), primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    discount_percentage = db.Column(db.DECIMAL(5, 2), nullable=False)
    max_discount_amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Active', 'Expired', 'Used'), nullable=False, default='Active')
    customer_id = db.Column(db.String(32), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)

    def __init__(self, voucher_id, code, discount_percentage, max_discount_amount, 
                expiry_date, status='Active', customer_id=None):
        self.voucher_id = voucher_id
        self.code = code
        self.discount_percentage = discount_percentage
        self.max_discount_amount = max_discount_amount
        self.expiry_date = expiry_date
        self.status = status
        self.customer_id = customer_id

    def json(self):
        return {
            "voucher_id": self.voucher_id,
            "code": self.code,
            "discount_percentage": float(self.discount_percentage),
            "max_discount_amount": float(self.max_discount_amount),
            "expiry_date": self.expiry_date.strftime('%Y-%m-%d'),
            "status": self.status,
            "customer_id": self.customer_id,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


@app.route("/voucher")
def get_all():
    vouchers = db.session.scalars(db.select(Voucher)).all()

    if len(vouchers):
        return jsonify(
            {
                "code": 200,
                "data": {"vouchers": [voucher.json() for voucher in vouchers]},
            }
        )
    return jsonify({"code": 404, "message": "There are no vouchers."}), 404


@app.route("/voucher/<string:voucher_id>")
def find_by_voucher_id(voucher_id):
    voucher = db.session.scalar(db.select(Voucher).filter_by(voucher_id=voucher_id))

    if voucher:
        return jsonify({"code": 200, "data": voucher.json()})
    return jsonify({"code": 404, "message": "Voucher not found."}), 404


@app.route("/voucher/code/<string:code>")
def find_by_code(code):
    voucher = db.session.scalar(db.select(Voucher).filter_by(code=code))

    if voucher:
        return jsonify({"code": 200, "data": voucher.json()})
    return jsonify({"code": 404, "message": "Voucher not found."}), 404


@app.route("/voucher/customer/<string:customer_id>")
def find_by_customer_id(customer_id):
    vouchers = db.session.scalars(db.select(Voucher).filter_by(customer_id=customer_id)).all()

    if len(vouchers):
        return jsonify({
            "code": 200,
            "data": {"vouchers": [voucher.json() for voucher in vouchers]}
        })
    return jsonify({"code": 404, "message": "No vouchers found for this customer."}), 404


@app.route("/voucher/active/customer/<string:customer_id>")
def find_active_by_customer_id(customer_id):
    current_date = date.today()
    vouchers = db.session.scalars(
        db.select(Voucher).filter_by(customer_id=customer_id, status='Active').filter(Voucher.expiry_date >= current_date)
    ).all()

    if len(vouchers):
        return jsonify({
            "code": 200,
            "data": {"vouchers": [voucher.json() for voucher in vouchers]}
        })
    return jsonify({"code": 404, "message": "No active vouchers found for this customer."}), 404


@app.route("/voucher/validate", methods=["POST"])
def validate_voucher():
    data = request.get_json()
    
    if 'code' not in data:
        return jsonify({"code": 400, "message": "Voucher code is required."}), 400
    
    voucher_code = data['code']
    voucher = db.session.scalar(db.select(Voucher).filter_by(code=voucher_code))
    
    if not voucher:
        return jsonify({"code": 404, "message": "Voucher not found."}), 404
    
    # Check if voucher is expired
    current_date = date.today()
    if voucher.expiry_date < current_date:
        return jsonify({
            "code": 400, 
            "data": {"voucher_id": voucher.voucher_id, "status": "Expired"},
            "message": "Voucher has expired."
        }), 400
    
    # Check if voucher is already used
    if voucher.status == 'Used':
        return jsonify({
            "code": 400, 
            "data": {"voucher_id": voucher.voucher_id, "status": "Used"},
            "message": "Voucher has already been used."
        }), 400
    
    # Check if voucher belongs to the customer (if customer_id is provided)
    if 'customer_id' in data and voucher.customer_id is not None:
        if voucher.customer_id != data['customer_id']:
            return jsonify({
                "code": 400, 
                "data": {"voucher_id": voucher.voucher_id},
                "message": "Voucher does not belong to this customer."
            }), 400
    
    # Voucher is valid
    return jsonify({
        "code": 200, 
        "data": voucher.json(),
        "message": "Voucher is valid."
    })


@app.route("/voucher/<string:voucher_id>", methods=["POST"])
def create_voucher(voucher_id):
    if db.session.scalar(db.select(Voucher).filter_by(voucher_id=voucher_id)):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"voucher_id": voucher_id},
                    "message": "Voucher already exists.",
                }
            ),
            400,
        )

    data = request.get_json()
    
    # Check for required fields
    required_fields = ["code", "discount_percentage", "max_discount_amount", "expiry_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "message": f"Field '{field}' is required."}), 400
    
    # Check if code is unique
    if db.session.scalar(db.select(Voucher).filter_by(code=data.get('code'))):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"code": data.get('code')},
                    "message": "Voucher code already exists.",
                }
            ),
            400,
        )
    
    # Parse expiry date
    try:
        expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"code": 400, "message": "Invalid date format. Use YYYY-MM-DD."}), 400
    
    # Create new voucher
    voucher = Voucher(
        voucher_id=voucher_id,
        code=data["code"],
        discount_percentage=data["discount_percentage"],
        max_discount_amount=data["max_discount_amount"],
        expiry_date=expiry_date,
        status=data.get("status", "Active"),
        customer_id=data.get("customer_id")
    )

    try:
        db.session.add(voucher)
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"voucher_id": voucher_id},
                    "message": "An error occurred creating the voucher: " + str(e),
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": voucher.json()}), 201


@app.route("/voucher/<string:voucher_id>/status", methods=["PUT"])
def update_voucher_status(voucher_id):
    voucher = db.session.scalar(db.select(Voucher).filter_by(voucher_id=voucher_id))
    
    if not voucher:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"voucher_id": voucher_id},
                    "message": "Voucher not found.",
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

    # Validate status
    valid_statuses = ['Active', 'Expired', 'Used']
    if data['status'] not in valid_statuses:
        return jsonify({
            "code": 400,
            "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }), 400

    try:
        voucher.status = data['status']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": voucher.json(),
                "message": "Voucher status updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"voucher_id": voucher_id},
                    "message": "An error occurred updating voucher status: " + str(e),
                }
            ),
            500,
        )


@app.route("/voucher/<string:voucher_id>/assign", methods=["PUT"])
def assign_voucher_to_customer(voucher_id):
    voucher = db.session.scalar(db.select(Voucher).filter_by(voucher_id=voucher_id))
    
    if not voucher:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"voucher_id": voucher_id},
                    "message": "Voucher not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'customer_id' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "customer_id field is required.",
                }
            ),
            400,
        )

    try:
        voucher.customer_id = data['customer_id']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": voucher.json(),
                "message": "Voucher assigned to customer successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"voucher_id": voucher_id},
                    "message": "An error occurred assigning voucher to customer: " + str(e),
                }
            ),
            500,
        )


@app.route("/voucher/<string:voucher_id>", methods=["DELETE"])
def delete_voucher(voucher_id):
    voucher = db.session.scalar(db.select(Voucher).filter_by(voucher_id=voucher_id))
    
    if not voucher:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"voucher_id": voucher_id},
                    "message": "Voucher not found.",
                }
            ),
            404,
        )

    try:
        db.session.delete(voucher)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Voucher deleted successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"voucher_id": voucher_id},
                    "message": "An error occurred deleting the voucher: " + str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=True)