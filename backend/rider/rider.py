from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from os import environ
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Base URL for the REST API
API_BASE_URL = environ.get("API_URL") or "https://personal-g86bdbq5.outsystemscloud.com/Rider/rest/v1"

# Helper function to make API requests
def api_request(method, endpoint, data=None, params=None):
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request error: {str(e)}")
        return None

@app.route("/rider")
def get_all():
    response = api_request("GET", "riders")
    
    if response and "riders" in response:
        return jsonify({
            "code": 200,
            "data": {"riders": response["riders"]}
        })
    return jsonify({"code": 404, "message": "There are no riders."}), 404

@app.route("/rider/<string:rider_id>")
def find_by_rider_id(rider_id):
    response = api_request("GET", f"riders/{rider_id}")
    
    if response:
        return jsonify({"code": 200, "data": response})
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
    
    response = api_request("GET", "riders", params={"availability_status": status})
    
    if response and "riders" in response and len(response["riders"]) > 0:
        return jsonify({
            "code": 200,
            "data": {"riders": response["riders"]}
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
    
    response = api_request("GET", "riders", params={"vehicle_type": vehicle_type})
    
    if response and "riders" in response and len(response["riders"]) > 0:
        return jsonify({
            "code": 200,
            "data": {"riders": response["riders"]}
        })
    return jsonify({"code": 404, "message": f"No riders found with vehicle type '{vehicle_type}'."}), 404

@app.route("/rider/available")
def get_available_riders():
    response = api_request("GET", "riders", params={"availability_status": "Available"})
    
    if response and "riders" in response and len(response["riders"]) > 0:
        return jsonify({
            "code": 200,
            "data": {"riders": response["riders"]}
        })
    return jsonify({"code": 404, "message": "No available riders found."}), 404

@app.route("/rider/transaction/<string:transaction_id>")
def find_by_transaction_id(transaction_id):
    response = api_request("GET", "riders", params={"assigned_transaction_id": transaction_id})
    
    if response and "riders" in response and len(response["riders"]) > 0:
        return jsonify({"code": 200, "data": response["riders"][0]})
    return jsonify({"code": 404, "message": "No rider assigned to this transaction."}), 404

@app.route("/rider/<string:rider_id>", methods=["POST"])
def create_rider(rider_id):
    # Check if rider exists first
    existing = api_request("GET", f"riders/{rider_id}")
    if existing:
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

    # Add rider_id to data
    rider_data = data.copy()
    rider_data["rider_id"] = rider_id
    
    # Set defaults if not provided
    if "availability_status" not in rider_data:
        rider_data["availability_status"] = "Available"

    response = api_request("POST", "riders", data=rider_data)
    
    if response:
        return jsonify({"code": 201, "data": response}), 201
    return (
        jsonify(
            {
                "code": 500,
                "data": {"rider_id": rider_id},
                "message": "An error occurred creating the rider.",
            }
        ),
        500,
    )

@app.route("/rider/<string:rider_id>", methods=["PUT"])
def update_rider(rider_id):
    # Check if rider exists
    existing = api_request("GET", f"riders/{rider_id}")
    if not existing:
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

    response = api_request("PUT", f"riders/{rider_id}", data=data)
    
    if response:
        return jsonify(
            {
                "code": 200,
                "data": response,
                "message": "Rider updated successfully."
            }
        )
    return (
        jsonify(
            {
                "code": 500,
                "data": {"rider_id": rider_id},
                "message": "An error occurred updating the rider.",
            }
        ),
        500,
    )

@app.route("/rider/<string:rider_id>", methods=["DELETE"])
def delete_rider(rider_id):
    # Check if rider exists
    existing = api_request("GET", f"riders/{rider_id}")
    if not existing:
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

    response = api_request("DELETE", f"riders/{rider_id}")
    
    if response:
        return jsonify(
            {
                "code": 200,
                "message": "Rider deleted successfully."
            }
        )
    return (
        jsonify(
            {
                "code": 500,
                "data": {"rider_id": rider_id},
                "message": "An error occurred deleting the rider.",
            }
        ),
        500,
    )

@app.route("/rider/<string:rider_id>/location", methods=["PUT"])
def update_location(rider_id):
    # Check if rider exists
    existing = api_request("GET", f"riders/{rider_id}")
    if not existing:
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

    update_data = {
        "latitude": data['latitude'],
        "longitude": data['longitude']
    }
    
    response = api_request("PUT", f"riders/{rider_id}/location", data=update_data)
    
    if response:
        return jsonify(
            {
                "code": 200,
                "data": response,
                "message": "Rider location updated successfully."
            }
        )
    return (
        jsonify(
            {
                "code": 500,
                "data": {"rider_id": rider_id},
                "message": "An error occurred updating rider location.",
            }
        ),
        500,
    )

@app.route("/rider/<string:rider_id>/status", methods=["PUT"])
def update_status(rider_id):
    # Check if rider exists
    existing = api_request("GET", f"riders/{rider_id}")
    if not existing:
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

    update_data = {
        "availability_status": data['availability_status']
    }
    
    response = api_request("PUT", f"riders/{rider_id}/status", data=update_data)
    
    if response:
        return jsonify(
            {
                "code": 200,
                "data": response,
                "message": "Rider status updated successfully."
            }
        )
    return (
        jsonify(
            {
                "code": 500,
                "data": {"rider_id": rider_id},
                "message": "An error occurred updating rider status.",
            }
        ),
        500,
    )

@app.route("/rider/<string:rider_id>/assign", methods=["PUT"])
def assign_transaction(rider_id):
    # Check if rider exists
    existing = api_request("GET", f"riders/{rider_id}")
    if not existing:
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

    update_data = {
        "transaction_id": data['transaction_id']
    }
    
    response = api_request("PUT", f"riders/{rider_id}/assign", data=update_data)
    
    if response:
        return jsonify(
            {
                "code": 200,
                "data": response,
                "message": "Transaction assigned to rider successfully."
            }
        )
    return (
        jsonify(
            {
                "code": 500,
                "data": {"rider_id": rider_id},
                "message": "An error occurred assigning transaction to rider.",
            }
        ),
        500,
    )

@app.route("/rider/<string:rider_id>/unassign", methods=["PUT"])
def unassign_transaction(rider_id):
    # Check if rider exists
    existing = api_request("GET", f"riders/{rider_id}")
    if not existing:
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
    
    response = api_request("PUT", f"riders/{rider_id}/unassign")
    
    if response:
        return jsonify(
            {
                "code": 200,
                "data": response,
                "message": "Transaction unassigned from rider successfully."
            }
        )
    return (
        jsonify(
            {
                "code": 500,
                "data": {"rider_id": rider_id},
                "message": "An error occurred unassigning transaction from rider.",
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
    
    # If vehicle_type is provided, validate it
    if 'vehicle_type' in data:
        valid_vehicle_types = ['Bicycle', 'Motorcycle', 'Car']
        if data['vehicle_type'] not in valid_vehicle_types:
            return jsonify({
                "code": 400,
                "message": f"Invalid vehicle type. Must be one of: {', '.join(valid_vehicle_types)}"
            }), 400
    
    # Call the API to find the nearest rider
    response = api_request("POST", "riders/nearest", data=data)
    
    if response and "rider" in response:
        return jsonify({
            "code": 200,
            "data": response
        })
    return jsonify({"code": 404, "message": "No available riders found."}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5015, debug=True)