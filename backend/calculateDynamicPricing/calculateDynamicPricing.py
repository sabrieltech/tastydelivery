from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from math import sin, cos, sqrt, asin  # Added import at the top level

app = Flask(__name__)
CORS(app)

# URLs for the atomic microservices
restaurant_URL = os.environ.get('restaurant_URL') or "http://localhost:5007/restaurant"
rider_URL = os.environ.get('https://personal-g86bdbq5.outsystemscloud.com/Rider/rest/v1/riders/')

# Helper function for HTTP requests to other microservices
def invoke_http(url, method='GET', json=None, **kwargs):
    """
    A simple wrapper for requests methods.
    
    Args:
        url (str): The URL to send the request to
        method (str): The HTTP method to use (GET, POST, PUT, DELETE)
        json (dict, optional): JSON data to send in the request body
        **kwargs: Additional arguments to pass to the requests call
        
    Returns:
        dict: The JSON response as a dictionary
    """
    code = 200
    result = {}
    
    try:
        if method.upper() == 'GET':
            # Handle GET requests
            r = requests.get(url, **kwargs)
        elif method.upper() == 'POST':
            # Handle POST requests with JSON body
            r = requests.post(url, json=json, **kwargs)
        elif method.upper() == 'PUT':
            # Handle PUT requests with JSON body
            r = requests.put(url, json=json, **kwargs)
        elif method.upper() == 'DELETE':
            # Handle DELETE requests
            r = requests.delete(url, **kwargs)
        else:
            # If invalid method specified, raise an error
            raise Exception(f"HTTP method '{method}' is not supported.")
        
        # Check if the response status code indicates success
        code = r.status_code
        
        # Get the response as a JSON object if possible, or raw text otherwise
        try:
            result = r.json() if r.text else {}
        except Exception as e:
            # If the response is not in JSON format, return the raw text
            result = {"code": code, "message": r.text}
            
    except Exception as e:
        # Handle any exceptions that occur during the request
        code = 500
        result = {
            "code": code,
            "message": f"Error in invoking HTTP request: {str(e)}"
        }
    
    return result


def calculate_travel_time(restaurant_coords, rider_coords):
    """
    Use the Google Maps Service to calculate travel time between two coordinates
    """
    try:
        # Prepare coordinates string for Google Maps API
        origin = f"{restaurant_coords[0]},{restaurant_coords[1]}"
        destination = f"{rider_coords[0]},{rider_coords[1]}"
        
        # Call the Node.js Google Maps Service via a subprocess
        node_command = f"node -e \"const {{ getDistanceMatrix }} = require('./googleMapsService.js'); getDistanceMatrix('{origin}', '{destination}').then(result => console.log(JSON.stringify(result))).catch(err => console.error(err));\""
        
        # Execute the Node.js command
        process = subprocess.Popen(node_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if stderr:
            print(f"Error from Google Maps Service: {stderr.decode()}")
            raise Exception(f"Error from Google Maps Service: {stderr.decode()}")
        
        # Parse the result
        result = json.loads(stdout.decode().strip())
        
        # Extract duration text (e.g., "15 mins") and convert to minutes
        duration_text = result['duration']
        minutes = 0
        
        # Parse duration text (assuming format like "X days Y hours Z mins", "X hours Y mins", or "1 min")
        if "days" in duration_text:
            # Format: "X days Y hours Z mins"
            days_part = duration_text.split("days")[0].strip()
            remaining = duration_text.split("days")[1].strip()
            hours_part = 0
            mins_part = 0
            if "hours" in remaining and "mins" in remaining:
                hours_part = remaining.split("hours")[0].strip()
                mins_part = remaining.split("hours")[1].split("mins")[0].strip()
            elif "hour" in remaining and "mins" in remaining:
                hours_part = remaining.split("hour")[0].strip()
                mins_part = remaining.split("hour")[1].split("mins")[0].strip()
            elif "hour" in remaining:
                hours_part = remaining.split("hour")[0].strip()
            elif "min" in remaining:
                mins_part = remaining.split("min")[0].strip()
            minutes = int(days_part) * 24 * 60 + int(hours_part) * 60 + int(mins_part)
        elif "day" in duration_text:
            # Format: "1 day Y hours Z mins"
            days_part = duration_text.split("day")[0].strip()
            remaining = duration_text.split("day")[1].strip()
            hours_part = 0
            mins_part = 0
            if "hours" in remaining and "mins" in remaining:
                hours_part = remaining.split("hours")[0].strip()
                mins_part = remaining.split("hours")[1].split("mins")[0].strip()
            elif "hour" in remaining and "mins" in remaining:
                hours_part = remaining.split("hour")[0].strip()
                mins_part = remaining.split("hour")[1].split("mins")[0].strip()
            elif "hour" in remaining:
                hours_part = remaining.split("hour")[0].strip()
            elif "min" in remaining:
                mins_part = remaining.split("min")[0].strip()
            minutes = int(days_part) * 24 * 60 + int(hours_part) * 60 + int(mins_part)
        elif "hours" in duration_text and "mins" in duration_text:
            # Format: "X hours Y mins"
            hours_part = duration_text.split("hours")[0].strip()
            mins_part = duration_text.split("hours")[1].split("mins")[0].strip()
            minutes = int(hours_part) * 60 + int(mins_part)
        elif "hour" in duration_text and "mins" in duration_text:
            # Format: "1 hour Y mins"
            hours_part = duration_text.split("hour")[0].strip()
            mins_part = duration_text.split("hour")[1].split("mins")[0].strip()
            minutes = int(hours_part) * 60 + int(mins_part)
        elif "hour" in duration_text:
            # Format: "1 hour" or "X hours"
            hours_part = duration_text.split("hour")[0].strip()
            minutes = int(hours_part) * 60
        elif "min" in duration_text:  # Handle both "1 min" and "X mins"
            mins_part = duration_text.split("min")[0].strip()
            minutes = int(mins_part)
        else:
            # Fallback for unrecognized formats
            print(f"Warning: Unrecognized duration format: {duration_text}")
            minutes = 0  # Default to 0 minutes if the format is unrecognized
        
        return {
            "duration_text": duration_text,
            "minutes": minutes,
            "distance": result['distance']
        }
        
    except Exception as e:
        print(f"Error calculating travel time: {str(e)}")
        raise e


def calculate_price(travel_time_data):
    """
    Calculate the dynamic price based on the travel time
    
    Pricing model:
    - Base fare: $2.50
    - Per minute rate: $0.30
    - Distance surcharge:
      - 0-3 km: $0
      - 3-10 km: $1.50
      - >10 km: $3.00
    - Peak hour multiplier: 1.5x during peak hours (not implemented yet)
    """
    # Base fare
    base_fare = Decimal('2.50')
    
    # Time component
    minutes = travel_time_data["minutes"]
    time_charge = Decimal(str(minutes)) * Decimal('0.30')
    
    # Distance component
    distance_text = travel_time_data["distance"]
    distance_km = 0
    
    # Parse distance text (e.g., "5.2 km" or "4,493 m")
    if "km" in distance_text:
        distance_km = float(distance_text.split("km")[0].strip().replace(",", ""))
    elif "m" in distance_text:  # For very short distances in meters
        distance_m = float(distance_text.split("m")[0].strip().replace(",", ""))
        distance_km = distance_m / 1000
    
    # Apply distance surcharge
    if distance_km <= 3:
        distance_surcharge = Decimal('0')
    elif distance_km <= 10:
        distance_surcharge = Decimal('1.50')
    else:
        distance_surcharge = Decimal('3.00')
    
    # Calculate total price
    total_price = base_fare + time_charge + distance_surcharge
    
    # Round to 2 decimal places using ROUND_HALF_UP
    total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return {
        "base_fare": float(base_fare),
        "time_charge": float(time_charge),
        "distance_km": distance_km,
        "distance_surcharge": float(distance_surcharge),
        "total_price": float(total_price)
    }


def getStaticMapImageUrl(restaurant_coords, rider_coords):
    """
    Generate a static map image URL using the Google Static Maps API.
    """
    try:
        # Define the base URL for the Google Static Maps API
        base_url = "https://maps.googleapis.com/maps/api/staticmap?"
        
        # Define the map parameters
        size = "600x300"  # Map size
        maptype = "roadmap"  # Map type
        markers = []
        
        # Add restaurant marker
        restaurant_marker = f"color:blue%7Clabel:R%7C{restaurant_coords[0]},{restaurant_coords[1]}"
        markers.append(restaurant_marker)
        
        # Add rider marker
        rider_marker = f"color:red%7Clabel:D%7C{rider_coords[0]},{rider_coords[1]}"
        markers.append(rider_marker)
        
        # Encode the markers
        markers_str = "&markers=".join(markers)
        
        # Construct the URL
        url = f"{base_url}size={size}&maptype={maptype}&markers={markers_str}&key=AIzaSyB1cfjM0hDHbd0tP3aYDZOd6C9tlRfyu6s"
        
        return url
    
    except Exception as e:
        print(f"Error generating static map image URL: {str(e)}")
        return None


# Helper function to calculate Haversine distance between two points
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points
    specified by their latitude and longitude in degrees.
    Returns distance in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lat1 = float(lat1) * (3.14159 / 180.0)
    lon1 = float(lon1) * (3.14159 / 180.0)
    lat2 = float(lat2) * (3.14159 / 180.0)
    lon2 = float(lon2) * (3.14159 / 180.0)
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = pow(sin(dlat/2), 2) + cos(lat1) * cos(lat2) * pow(sin(dlon/2), 2)
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r


@app.route("/calculate_delivery_fee/<string:restaurant_id>/<string:phone_number>", methods=['GET'])
def get_dynamic_price(restaurant_id, phone_number):
    """
    Calculate the dynamic delivery fee based on distance between restaurant and rider
    This is a composite service that orchestrates multiple atomic services
    Uses the rider's phone number as the primary key to identify the rider
    If phone_number is "auto", selects the closest available rider automatically
    """
    try:
        # Create the result dictionary
        result = {
            "code": 200,
            "data": {}
        }

        # 1. Get restaurant coordinates
        print('\n-----Invoking restaurant microservice-----')
        restaurant_result = invoke_http(f"{restaurant_URL}/{restaurant_id}", method='GET')
        print('restaurant_result:', restaurant_result)
        
        if restaurant_result["code"] not in range(200, 300):
            return jsonify({
                "code": restaurant_result["code"],
                "message": "Failed to get restaurant information"
            }), restaurant_result["code"]
        
        restaurant_data = restaurant_result["data"]
        restaurant_coords = [restaurant_data["latitude"], restaurant_data["longitude"]]
        
        # Add restaurant info to result
        result["data"]["restaurant"] = {
            "id": restaurant_id,
            "name": restaurant_data["name"],
            "coordinates": restaurant_coords
        }

        # 2. Get rider coordinates
        print('\n-----Invoking rider microservice-----')
        rider_result = invoke_http(f"https://personal-g86bdbq5.outsystemscloud.com/Rider/rest/v1/riders/", method='GET')
        print('rider_result:', rider_result)
        
        if "Result" not in rider_result or not rider_result["Result"]["Success"]:
            health_result = invoke_http(f"https://personal-g86bdbq5.outsystemscloud.com/Rider/rest/v1/riders/", method='GET')
            
            if "Result" not in health_result or not health_result["Result"]["Success"]:
                return jsonify({
                    "code": 503,
                    "message": "Rider service is unavailable"
                }), 503
            
            return jsonify({
                "code": 400,
                "message": "Failed to get rider information"
            }), 400
        
        # Get all available riders
        available_riders = [rider for rider in rider_result["Riders"] if rider["availability_status"] == "Available"]
        
        if not available_riders:
            return jsonify({
                "code": 404,
                "message": "No available riders found"
            }), 404
        
        # Check if we need to find a specific rider by phone number or the closest rider
        if phone_number != "auto":
            # Try to find the rider with the specified phone number
            matched_riders = [rider for rider in rider_result["Riders"] if rider["phone_number"] == phone_number]
            
            if matched_riders:
                selected_rider = matched_riders[0]
                # Check if the rider is available
                if selected_rider["availability_status"] != "Available":
                    return jsonify({
                        "code": 400,
                        "message": f"Rider with phone number {phone_number} is not available (current status: {selected_rider['availability_status']})"
                    }), 400
            else:
                # If specified rider not found, find the closest available rider
                # Calculate distance from restaurant to each available rider
                for rider in available_riders:
                    rider["distance_to_restaurant"] = calculate_distance(
                        restaurant_coords[0], restaurant_coords[1],
                        rider["latitude"], rider["longitude"]
                    )
                
                # Sort riders by distance
                available_riders.sort(key=lambda x: x["distance_to_restaurant"])
                
                # Select the closest available rider
                selected_rider = available_riders[0]
                
                # Inform that we're using the closest rider instead
                print(f"Rider with phone number {phone_number} not found or not available. Using closest available rider instead.")
        else:
            # Auto mode - find the closest available rider
            # Calculate distance from restaurant to each available rider
            for rider in available_riders:
                rider["distance_to_restaurant"] = calculate_distance(
                    restaurant_coords[0], restaurant_coords[1],
                    rider["latitude"], rider["longitude"]
                )
            
            # Sort riders by distance
            available_riders.sort(key=lambda x: x["distance_to_restaurant"])
            
            # Select the closest available rider
            selected_rider = available_riders[0]
        
        rider_data = {
            "id": str(selected_rider["rider_id"]),
            "name": selected_rider["name"],
            "phone_number": selected_rider["phone_number"],
            "latitude": selected_rider["latitude"],
            "longitude": selected_rider["longitude"],
            "availability_status": selected_rider["availability_status"],
            "vehicle_type": selected_rider["vehicle_type"],
            "distance_to_restaurant_km": selected_rider.get("distance_to_restaurant", "Not calculated")
        }
        
        rider_coords = [rider_data["latitude"], rider_data["longitude"]]
        
        # Add rider info to result - IMPORTANT: Use phone_number as the id value
        result["data"]["rider"] = {
            "id": rider_data["phone_number"],  # Use phone number as the rider id
            "name": rider_data["name"],
            "phone_number": rider_data["phone_number"],
            "vehicle_type": rider_data["vehicle_type"],
            "availability_status": rider_data["availability_status"],
            "coordinates": rider_coords,
            "distance_to_restaurant_km": rider_data["distance_to_restaurant_km"]
        }

        # 3. Calculate travel time using Google Maps Service
        print('\n-----Invoking Google Maps Service-----')
        travel_time_data = calculate_travel_time(restaurant_coords, rider_coords)
        print('travel_time_data:', travel_time_data)
        
        # Add travel info to result
        result["data"]["travel_info"] = {
            "duration": travel_time_data["duration_text"],
            "distance": travel_time_data["distance"]
        }

        # 4. Calculate dynamic price based on travel time
        print('\n-----Calculating dynamic price-----')
        price_data = calculate_price(travel_time_data)
        print('price_data:', price_data)
        
        # Add price info to result
        result["data"]["price_info"] = price_data
        result["data"]["delivery_fee"] = price_data["total_price"]
        
        # 5. Generate static map image URL
        print('\n-----Generating static map image URL-----')
        static_map_url = getStaticMapImageUrl(restaurant_coords, rider_coords)
        print('static_map_url:', static_map_url)
        
        # Add static map image URL to result
        result["data"]["static_map_url"] = static_map_url

        return jsonify(result), result["code"]

    except Exception as e:
        # Unexpected error
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "calculateDynamicPricing.py internal error: " + ex_str
        }), 500


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for calculating dynamic delivery pricing...")
    app.run(host="0.0.0.0", port=5016, debug=True)