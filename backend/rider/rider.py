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


class Rider(db.Model):
    __tablename__ = "rider"

    rider_id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.Enum('Bicycle', 'Motorcycle', 'Car'), nullable=False)
    availability_status = db.Column(db.Enum('Available', 'On Delivery', 'Offline'), nullable=False, default='Available')
    latitude = db.Column(db.DECIMAL(10, 8), nullable=False)
    longitude = db.Column(db.DECIMAL(11, 8), nullable=False)
    assigned_transaction_id = db.Column(db.String(32), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)

    def __init__(self, rider_id, name, phone_number, vehicle_type, latitude, longitude, 
                availability_status='Available', assigned_transaction_id=None):
        self.rider_id = rider_id
        self.name = name
        self.phone_number = phone_number
        self.vehicle_type = vehicle_type
        self.availability_status = availability_status
        self.latitude = latitude
        self.longitude = longitude
        self.assigned_transaction_id = assigned_transaction_id

    def json(self):
        return {
            "rider_id": self.rider_id,
            "name": self.name,
            "phone_number": self.phone_number,
            "vehicle_type": self.vehicle_type,
            "availability_status": self.availability_status,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "assigned_transaction_id": self.assigned_transaction_id,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


@app.route("/rider")
def get_all():
    riderlist = db.session.scalars(db.select(Rider)).all()

    if len(riderlist):
        return jsonify(
            {
                "code": 200,
                "data": {"riders": [rider.json() for rider in riderlist]},
            }
        )
    return jsonify({"code": 404, "message": "There are no riders."}), 404


@app.route("/rider/<string:rider_id>")
def find_by_rider_id(rider_id):
    rider = db.session.scalar(db.select(Rider).filter_by(rider_id=rider_id))

    if rider:
        return jsonify({"code": 200, "data": rider.json()})
    return jsonify({"code": 404, "message": "Rider not found."}), 404


@app.route("/rider/status/<string:status>")
def find_by_status(status):
    # Validate the status value
    valid_statuses = ['Available', 'On Delivery', 'Offline']
    if status not in valid_statuses:
        return jsonify({
            "code": 400,
            "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }), 400
        
    riders = db.session.scalars(db.select(Rider).filter_by(availability_status=status)).all()

    if len(riders):
        return jsonify({
            "code": 200,
            "data": {"riders": [rider.json() for rider in riders]}
        })
    return jsonify({"code": 404, "message": f"No riders found with status '{status}'."}), 404


@app.route("/rider/vehicle/<string:vehicle_type>")
def find_by_vehicle_type(vehicle_type):
    # Validate the vehicle type
    valid_types = ['Bicycle', 'Motorcycle', 'Car']
    if vehicle_type not in valid_types:
        return jsonify({
            "code": 400,
            "message": f"Invalid vehicle type. Must be one of: {', '.join(valid_types)}"
        }), 400
        
    riders = db.session.scalars(db.select(Rider).filter_by(vehicle_type=vehicle_type)).all()

    if len(riders):
        return jsonify({
            "code": 200,
            "data": {"riders": [rider.json() for rider in riders]}
        })
    return jsonify({"code": 404, "message": f"No riders found with vehicle type '{vehicle_type}'."}), 404


@app.route("/rider/available")
def get_available_riders():
    riders = db.session.scalars(db.select(Rider).filter_by(availability_status='Available')).all()

    if len(riders):
        return jsonify({
            "code": 200,
            "data": {"riders": [rider.json() for rider in riders]}
        })
    return jsonify({"code": 404, "message": "No available riders found."}), 404


@app.route("/rider/transaction/<string:transaction_id>")
def find_by_transaction_id(transaction_id):
    rider = db.session.scalar(db.select(Rider).filter_by(assigned_transaction_id=transaction_id))

    if rider:
        return jsonify({"code": 200, "data": rider.json()})
    return jsonify({"code": 404, "message": "No rider assigned to this transaction."}), 404


@app.route("/rider/<string:rider_id>", methods=["POST"])
def create_rider(rider_id):
    if db.session.scalar(db.select(Rider).filter_by(rider_id=rider_id)):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"rider_id": rider_id},
                    "message": "Rider already exists.",
                }
            ),
            400,
        )

    data = request.get_json()
    
    # Check required fields
    required_fields = ["name", "phone_number", "vehicle_type", "latitude", "longitude"]
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "message": f"Field '{field}' is required."}), 400
    
    # Validate vehicle_type
    valid_vehicle_types = ['Bicycle', 'Motorcycle', 'Car']
    if data["vehicle_type"] not in valid_vehicle_types:
        return jsonify({
            "code": 400,
            "message": f"Invalid vehicle type. Must be one of: {', '.join(valid_vehicle_types)}"
        }), 400

    rider = Rider(
        rider_id=rider_id,
        name=data["name"],
        phone_number=data["phone_number"],
        vehicle_type=data["vehicle_type"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        availability_status=data.get("availability_status", "Available"),
        assigned_transaction_id=data.get("assigned_transaction_id")
    )

    try:
        db.session.add(rider)
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"rider_id": rider_id},
                    "message": "An error occurred creating the rider: " + str(e),
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": rider.json()}), 201


@app.route("/rider/<string:rider_id>", methods=["PUT"])
def update_rider(rider_id):
    rider = db.session.scalar(db.select(Rider).filter_by(rider_id=rider_id))
    
    if not rider:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"rider_id": rider_id},
                    "message": "Rider not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    # Validate vehicle_type if provided
    if "vehicle_type" in data:
        valid_vehicle_types = ['Bicycle', 'Motorcycle', 'Car']
        if data["vehicle_type"] not in valid_vehicle_types:
            return jsonify({
                "code": 400,
                "message": f"Invalid vehicle type. Must be one of: {', '.join(valid_vehicle_types)}"
            }), 400
    
    # Validate availability_status if provided
    if "availability_status" in data:
        valid_statuses = ['Available', 'On Delivery', 'Offline']
        if data["availability_status"] not in valid_statuses:
            return jsonify({
                "code": 400, 
                "message": f"Invalid availability status. Must be one of: {', '.join(valid_statuses)}"
            }), 400

    try:
        # Update rider attributes
        for key, value in data.items():
            if hasattr(rider, key):
                setattr(rider, key, value)
        
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": rider.json(),
                "message": "Rider updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"rider_id": rider_id},
                    "message": "An error occurred updating the rider: " + str(e),
                }
            ),
            500,
        )


@app.route("/rider/<string:rider_id>", methods=["DELETE"])
def delete_rider(rider_id):
    rider = db.session.scalar(db.select(Rider).filter_by(rider_id=rider_id))
    
    if not rider:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"rider_id": rider_id},
                    "message": "Rider not found.",
                }
            ),
            404,
        )

    try:
        db.session.delete(rider)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Rider deleted successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"rider_id": rider_id},
                    "message": "An error occurred deleting the rider: " + str(e),
                }
            ),
            500,
        )


@app.route("/rider/<string:rider_id>/location", methods=["PUT"])
def update_location(rider_id):
    rider = db.session.scalar(db.select(Rider).filter_by(rider_id=rider_id))
    
    if not rider:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"rider_id": rider_id},
                    "message": "Rider not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'latitude' not in data or 'longitude' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "Both latitude and longitude fields are required.",
                }
            ),
            400,
        )

    try:
        rider.latitude = data['latitude']
        rider.longitude = data['longitude']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": rider.json(),
                "message": "Rider location updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"rider_id": rider_id},
                    "message": "An error occurred updating rider location: " + str(e),
                }
            ),
            500,
        )


@app.route("/rider/<string:rider_id>/status", methods=["PUT"])
def update_status(rider_id):
    rider = db.session.scalar(db.select(Rider).filter_by(rider_id=rider_id))
    
    if not rider:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"rider_id": rider_id},
                    "message": "Rider not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'availability_status' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "availability_status field is required.",
                }
            ),
            400,
        )

    # Validate the status value
    valid_statuses = ['Available', 'On Delivery', 'Offline']
    if data['availability_status'] not in valid_statuses:
        return jsonify({
            "code": 400,
            "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }), 400

    try:
        rider.availability_status = data['availability_status']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": rider.json(),
                "message": "Rider status updated successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"rider_id": rider_id},
                    "message": "An error occurred updating rider status: " + str(e),
                }
            ),
            500,
        )


@app.route("/rider/<string:rider_id>/assign", methods=["PUT"])
def assign_transaction(rider_id):
    rider = db.session.scalar(db.select(Rider).filter_by(rider_id=rider_id))
    
    if not rider:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"rider_id": rider_id},
                    "message": "Rider not found.",
                }
            ),
            404,
        )

    data = request.get_json()
    
    if 'transaction_id' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "transaction_id field is required.",
                }
            ),
            400,
        )

    try:
        # Update the assigned transaction ID and change status to On Delivery
        rider.assigned_transaction_id = data['transaction_id']
        rider.availability_status = 'On Delivery'
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": rider.json(),
                "message": "Transaction assigned to rider successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"rider_id": rider_id},
                    "message": "An error occurred assigning transaction to rider: " + str(e),
                }
            ),
            500,
        )


@app.route("/rider/<string:rider_id>/unassign", methods=["PUT"])
def unassign_transaction(rider_id):
    rider = db.session.scalar(db.select(Rider).filter_by(rider_id=rider_id))
    
    if not rider:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"rider_id": rider_id},
                    "message": "Rider not found.",
                }
            ),
            404,
        )

    try:
        # Clear the assigned transaction ID and change status to Available
        rider.assigned_transaction_id = None
        rider.availability_status = 'Available'
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": rider.json(),
                "message": "Transaction unassigned from rider successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"rider_id": rider_id},
                    "message": "An error occurred unassigning transaction from rider: " + str(e),
                }
            ),
            500,
        )


@app.route("/rider/nearest", methods=["POST"])
def find_nearest_available_rider():
    data = request.get_json()
    
    if 'latitude' not in data or 'longitude' not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "Both latitude and longitude fields are required.",
                }
            ),
            400,
        )
    
    # Get all available riders
    available_riders = db.session.scalars(db.select(Rider).filter_by(availability_status='Available')).all()
    
    if not available_riders:
        return jsonify({"code": 404, "message": "No available riders found."}), 404
    
    # Filter by vehicle type if provided
    if 'vehicle_type' in data:
        valid_vehicle_types = ['Bicycle', 'Motorcycle', 'Car']
        if data['vehicle_type'] not in valid_vehicle_types:
            return jsonify({
                "code": 400,
                "message": f"Invalid vehicle type. Must be one of: {', '.join(valid_vehicle_types)}"
            }), 400
        
        available_riders = [rider for rider in available_riders if rider.vehicle_type == data['vehicle_type']]
        
        if not available_riders:
            return jsonify({
                "code": 404, 
                "message": f"No available riders found with vehicle type '{data['vehicle_type']}'."
            }), 404
    
    # Calculate distances and find the nearest rider
    request_lat = float(data['latitude'])
    request_lon = float(data['longitude'])
    
    nearest_rider = None
    min_distance = float('inf')
    
    for rider in available_riders:
        rider_lat = float(rider.latitude)
        rider_lon = float(rider.longitude)
        
        # Use simplified distance calculation (Euclidean distance for demonstration)
        # In a real application, you might want to use the Haversine formula or a mapping API
        distance = ((rider_lat - request_lat) ** 2 + (rider_lon - request_lon) ** 2) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            nearest_rider = rider
    
    return jsonify({
        "code": 200,
        "data": {
            "rider": nearest_rider.json(),
            "distance": min_distance
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5015, debug=True)