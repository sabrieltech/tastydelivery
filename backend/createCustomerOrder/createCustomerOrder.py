from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# URLs for the atomic microservices
transaction_URL = os.environ.get('transaction_URL') or "http://localhost:5009/transaction"
transaction_item_URL = os.environ.get('transaction_item_URL') or "http://localhost:5010/transaction_item"
restaurant_URL = os.environ.get('restaurant_URL') or "http://localhost:5007/restaurant"
restaurant_inventory_URL = os.environ.get('restaurant_inventory_URL') or "http://localhost:5008/restaurant_inventory"
customer_URL = os.environ.get('customer_URL') or "http://localhost:5006/customer"
rider_URL = os.environ.get('https://personal-g86bdbq5.outsystemscloud.com/Rider/rest/v1/riders/')
voucher_URL = os.environ.get('voucher_URL') or "http://localhost:5012/voucher"


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


@app.route("/order/<string:transaction_id>", methods=['GET'])
def get_order_details(transaction_id):
    """
    Get detailed order information for a specific transaction
    This is a composite service that orchestrates multiple atomic services
    """
    try:
        # Create the result dictionary
        result = {
            "code": 200,
            "data": {}
        }

        # 1. Get transaction details
        transaction_result = get_transaction_info(transaction_id)
        if transaction_result["code"] not in range(200, 300):
            return jsonify({
                "code": transaction_result["code"],
                "message": "Failed to retrieve transaction information"
            }), transaction_result["code"]
        
        # Extract base transaction details
        transaction_data = transaction_result["data"]
        
        # 2. Get customer data
        customer_result = get_customer_info(transaction_data["customer_id"])
        if customer_result["code"] not in range(200, 300):
            print(f"Warning: Failed to retrieve customer data: {customer_result}")
            customer_data = None
        else:
            customer_data = customer_result["data"]
        
        # 3. Get transaction items
        transaction_items_result = get_transaction_items(transaction_id)
        if transaction_items_result["code"] not in range(200, 300):
            return jsonify({
                "code": transaction_items_result["code"],
                "message": "Failed to retrieve transaction items"
            }), transaction_items_result["code"]
        
        # 4. Enrich items with product details
        enriched_items = []
        restaurant_info = None
        restaurant_id = None
        
        if transaction_items_result["code"] == 200:
            items = transaction_items_result["data"]["transaction_items"]
            if items and len(items) > 0:
                # Get restaurant information from the first item
                first_item = items[0]
                restaurant_id = first_item["restaurant_id"]
                restaurant_info = get_restaurant_info(restaurant_id)
                
                # Enrich each item with details from restaurant inventory
                for item in items:
                    enriched_item = enrich_item_with_details(item)
                    if enriched_item:
                        enriched_items.append(enriched_item)
        
        # 5. Get rider information if available
        rider_info = None
        if transaction_data.get("rider_id"):
            rider_result = get_rider_info(transaction_data["rider_id"])
            if rider_result["code"] == 200:
                rider_info = rider_result["data"]
        
        # 6. Get voucher information if available
        voucher_info = None
        if transaction_data.get("voucher_id"):
            voucher_result = get_voucher_info(transaction_data["voucher_id"])
            if voucher_result["code"] == 200:
                voucher_info = voucher_result["data"]
        
        # 7. Calculate delivery details (could add more data from dynamic pricing if available)
        delivery_details = {
            "address": customer_data["address"] if customer_data and "address" in customer_data else "123 Customer Address St, Singapore",
            "rider_name": rider_info["name"] if rider_info else "Assigned Rider",
            "rider_phone": rider_info["phone_number"] if rider_info else "Not available",
            "rider_vehicle": rider_info["vehicle_type"] if rider_info else "Not available",
            "estimated_time": "30-45 minutes",  # Placeholder, could be calculated from dynamic pricing
            "status": transaction_data["status"],
            "rider_status": rider_info["availability_status"] if rider_info else "Unknown"
        }
        
        # Calculate discount amounts
        food_cost = float(transaction_data["food_cost"])
        delivery_cost = float(transaction_data["delivery_cost"])
        total_after_discount = float(transaction_data["total_price_after_discount"])
        
        # Calculate discount - handle negative values that might occur due to loyalty discounts
        calculated_discount = (food_cost + delivery_cost) - total_after_discount
        discount_amount = max(0, calculated_discount)
        
        # Calculate voucher discount
        voucher_discount = 0
        if voucher_info:
            # Simple approximation - in production, you'd use the exact value from when the voucher was applied
            voucher_discount = min(
                (food_cost + delivery_cost) * (float(voucher_info["discount_percentage"]) / 100),
                float(voucher_info["max_discount_amount"])
            )
        
        # Calculate loyalty discount
        loyalty_discount_percentage = float(transaction_data["loyalty_discount_percentage"])
        loyalty_discount = (food_cost + delivery_cost) * (loyalty_discount_percentage / 100)
        
        # Build the complete order object
        order_details = {
            "transaction_id": transaction_id,
            "customer_id": transaction_data["customer_id"],
            "customer_name": customer_data["name"] if customer_data else "Customer",
            "customer_phone": customer_data["phone_number"] if customer_data else "Not available",
            "status": transaction_data["status"],
            "transaction_date": transaction_data["created_at"],
            "items": enriched_items,
            "subtotal": food_cost,
            "delivery_fee": delivery_cost,
            "voucher_discount": voucher_discount,
            "loyalty_discount": loyalty_discount,
            "discount_amount": discount_amount,
            "total_price": total_after_discount,
            "loyalty_points_earned": transaction_data["loyalty_points_added"],
            "loyalty_points_used": transaction_data.get("loyalty_points_used", 0),
            "loyalty_status": transaction_data["current_loyalty_status"],
            "delivery_details": delivery_details,
            "payment_method": "Credit Card"  # Placeholder, could be expanded with actual payment data
        }
        
        # Add restaurant information if available
        if restaurant_info and "data" in restaurant_info:
            order_details["restaurant_id"] = restaurant_info["data"]["restaurant_id"]
            order_details["restaurant_name"] = restaurant_info["data"]["name"]
            order_details["restaurant_image"] = restaurant_info["data"]["image_url"]
            order_details["restaurant_address"] = f"123 {restaurant_info['data']['name']} St, Singapore"  # Placeholder
            order_details["restaurant_phone"] = restaurant_info["data"]["contact_number"]
        
        # Add voucher information if available
        if voucher_info:
            order_details["voucher_code"] = voucher_info["code"]
            order_details["voucher_discount_percentage"] = voucher_info["discount_percentage"]
            order_details["voucher_max_discount"] = voucher_info["max_discount_amount"]
        
        result["data"] = order_details
        return jsonify(result), result["code"]

    except Exception as e:
        # Unexpected error
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "createCustomerOrder.py internal error: " + ex_str
        }), 500


def get_transaction_info(transaction_id):
    """Get transaction information"""
    print(f'\n-----Invoking transaction microservice for transaction {transaction_id}-----')
    transaction_result = invoke_http(f"{transaction_URL}/{transaction_id}", method='GET')
    print('transaction_result:', transaction_result)
    
    return transaction_result


def get_customer_info(customer_id):
    """Get customer information"""
    print(f'\n-----Invoking customer microservice for customer {customer_id}-----')
    customer_result = invoke_http(f"{customer_URL}/{customer_id}", method='GET')
    print('customer_result:', customer_result)
    
    return customer_result


def get_transaction_items(transaction_id):
    """Get items for a specific transaction"""
    print(f'\n-----Invoking transaction_item microservice for transaction {transaction_id}-----')
    items_result = invoke_http(f"{transaction_item_URL}/transaction/{transaction_id}", method='GET')
    print('items_result:', items_result)
    
    return items_result


def get_restaurant_info(restaurant_id):
    """Get restaurant information"""
    try:
        print(f'\n-----Invoking restaurant microservice for restaurant {restaurant_id}-----')
        restaurant_result = invoke_http(f"{restaurant_URL}/{restaurant_id}", method='GET')
        print('restaurant_result:', restaurant_result)
        
        return restaurant_result
    except Exception as e:
        print(f"Error getting restaurant info: {str(e)}")
        return None

def get_rider_info(rider_id):
    """Get rider information"""
    try:
        print(f'\n-----Invoking rider microservice for rider {rider_id}-----')
        # Check rider service health first
            
        # Get all riders and find the one with matching phone_number
        all_riders_result = invoke_http(f"https://personal-g86bdbq5.outsystemscloud.com/Rider/rest/v1/riders/", method='GET')
        print('all_riders_result:', all_riders_result)
        
        if "Riders" in all_riders_result["Result"]:
            for rider in all_riders_result["Result"]["Riders"]:
                if rider["phone_number"] == rider_id:
                    return {"code": 200, "data": rider}
            
            # If no rider found with that phone number
            return {"code": 404, "message": f"No rider found with phone number {rider_id}"}
        else:
            return {"code": 500, "message": "Invalid response format from rider service"}
            
    except Exception as e:
        print(f"Error getting rider info: {str(e)}")
        return {"code": 500, "message": f"Error getting rider info: {str(e)}"}



def get_voucher_info(voucher_id):
    """Get voucher information"""
    try:
        print(f'\n-----Invoking voucher microservice for voucher {voucher_id}-----')
        voucher_result = invoke_http(f"{voucher_URL}/{voucher_id}", method='GET')
        print('voucher_result:', voucher_result)
        
        return voucher_result
    except Exception as e:
        print(f"Error getting voucher info: {str(e)}")
        return None


def get_item_details(item_id):
    """Get details for a specific inventory item"""
    try:
        print(f'\n-----Invoking restaurant_inventory microservice for item {item_id}-----')
        item_result = invoke_http(f"{restaurant_inventory_URL}/{item_id}", method='GET')
        print('item_result:', item_result)
        
        return item_result
    except Exception as e:
        print(f"Error getting item details: {str(e)}")
        return None


def enrich_item_with_details(item):
    """Enrich a transaction item with details from the restaurant inventory"""
    item_id = item["item_id"]
    item_details = get_item_details(item_id)
    
    if item_details and item_details["code"] == 200:
        details = item_details["data"]
        return {
            "item_id": item["item_id"],
            "restaurant_id": item["restaurant_id"],
            "item_name": details.get("item_name", "Unknown Item"),
            "description": details.get("description", ""),
            "image_url": details.get("image_url", ""),
            "quantity": item["quantity"],
            "price": float(item["price_per_item"]),
            "total_price": float(item["total_price"]),
            "category": details.get("category", ""),
            "options": []  # Add empty options array for potential future use
        }
    else:
        # Return basic information if details not available
        return {
            "item_id": item["item_id"],
            "restaurant_id": item["restaurant_id"],
            "item_name": f"Item #{item_id}",
            "quantity": item["quantity"],
            "price": float(item["price_per_item"]),
            "total_price": float(item["total_price"]),
            "options": []  # Add empty options array for potential future use
        }


# Add a health check endpoint for OutSystems monitoring
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "order-service",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }), 200


@app.route("/order/assign/<string:transaction_id>/<string:rider_id>", methods=['PUT'])
def assign_rider_to_order(transaction_id, rider_phone):
    """
    Assign a rider to a specific order/transaction
    This is a composite service that orchestrates multiple atomic services
    """
    try:
        # 1. Check if the rider exists and is available
        rider_result = get_rider_info(rider_phone)
        if rider_result["code"] not in range(200, 300):
            return jsonify({
                "code": rider_result["code"],
                "message": "Failed to get rider information"
            }), rider_result["code"]
        
        rider_data = rider_result["data"]
        if rider_data["availability_status"] != "Available":
            return jsonify({
                "code": 400,
                "message": f"Rider is not available. Current status: {rider_data['availability_status']}"
            }), 400
        
        # 2. Check if the transaction exists
        transaction_result = get_transaction_info(transaction_id)
        if transaction_result["code"] not in range(200, 300):
            return jsonify({
                "code": transaction_result["code"],
                "message": "Failed to get transaction information"
            }), transaction_result["code"]
        
        # 3. Assign the rider to the transaction
        assign_data = {
            "transaction_id": transaction_id
        }
        
        print(f'\n-----Assigning rider {rider_phone} to transaction {transaction_id}-----')
        assignment_result = invoke_http(f"{rider_URL}/riders/{rider_phone}/assign", method='PUT', json=assign_data)
        print('assignment_result:', assignment_result)
        
        if assignment_result["code"] not in range(200, 300):
            return jsonify({
                "code": assignment_result["code"],
                "message": "Failed to assign rider to transaction"
            }), assignment_result["code"]
        
        # 4. Update the transaction with the rider phone
        transaction_update = {
            "rider_id": rider_phone,  # Using phone as the rider_id
            "status": "In Progress"  # Update status to show that delivery is in progress
        }
        
        print(f'\n-----Updating transaction {transaction_id} with rider {rider_phone}-----')
        transaction_update_result = invoke_http(f"{transaction_URL}/{transaction_id}", method='PUT', json=transaction_update)
        print('transaction_update_result:', transaction_update_result)
        
        # Return the updated order details
        return get_order_details(transaction_id)
        
    except Exception as e:
        # Unexpected error
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "createCustomerOrder.py internal error: " + ex_str
        }), 500


@app.route("/order/complete/<string:transaction_id>", methods=['PUT'])
def complete_order(transaction_id):
    """
    Mark an order as completed and unassign the rider
    This is a composite service that orchestrates multiple atomic services
    """
    try:
        # 1. Get the transaction details to find the rider
        transaction_result = get_transaction_info(transaction_id)
        if transaction_result["code"] not in range(200, 300):
            return jsonify({
                "code": transaction_result["code"],
                "message": "Failed to get transaction information"
            }), transaction_result["code"]
        
        transaction_data = transaction_result["data"]
        rider_phone = transaction_data.get("rider_id")  # Now contains phone number
        
        if not rider_phone:
            return jsonify({
                "code": 400,
                "message": "No rider assigned to this transaction"
            }), 400
        
        # 2. Update the transaction status
        transaction_update = {
            "status": "Completed"
        }
        
        print(f'\n-----Updating transaction {transaction_id} to Completed-----')
        transaction_update_result = invoke_http(f"{transaction_URL}/{transaction_id}", method='PUT', json=transaction_update)
        print('transaction_update_result:', transaction_update_result)
        
        # 3. Unassign the rider from the transaction
        print(f'\n-----Unassigning rider {rider_phone} from transaction {transaction_id}-----')
        unassign_result = invoke_http(f"{rider_URL}/riders/{rider_phone}/unassign", method='PUT')
        print('unassign_result:', unassign_result)
        
        # Return the updated order details
        return get_order_details(transaction_id)
        
    except Exception as e:
        # Unexpected error
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "createCustomerOrder.py internal error: " + ex_str
        }), 500

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for retrieving order details...")
    app.run(host="0.0.0.0", port=5014, debug=True)
