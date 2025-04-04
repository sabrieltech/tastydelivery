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
customer_URL = os.environ.get('customer_URL') or "http://localhost:5006/customer"
restaurant_URL = os.environ.get('restaurant_URL') or "http://localhost:5007/restaurant"
restaurant_inventory_URL = os.environ.get('restaurant_inventory_URL') or "http://localhost:5008/restaurant_inventory"
transaction_URL = os.environ.get('transaction_URL') or "http://localhost:5009/transaction"
transaction_item_URL = os.environ.get('transaction_item_URL') or "http://localhost:5010/transaction_item"
notification_URL = os.environ.get('notification_URL') or "http://localhost:5011/notification"
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


@app.route("/personalized_homepage/<string:customer_id>", methods=['GET'])
def get_personalized_homepage(customer_id):
    """
    Get personalized homepage data for a specific customer
    This is a composite service that orchestrates multiple atomic services
    """
    try:
        # Create the result dictionary
        result = {
            "code": 200,
            "data": {}
        }

        # 1. Get customer info (profile and loyalty)
        customer_result = get_customer_info(customer_id)
        if customer_result["code"] not in range(200, 300):
            return jsonify(customer_result), customer_result["code"]
        
        result["data"]["customerInfo"] = customer_result["data"]

        # 2. Get recent transactions (orders)
        transactions_result = get_recent_transactions(customer_id)
        if transactions_result["code"] == 200:
            result["data"]["recentOrders"] = transactions_result["data"]["transactions"]
        else:
            result["data"]["recentOrders"] = []

        # 3. Get transaction items and enrich transaction data
        result["data"]["recentOrders"] = enrich_transactions_with_items(result["data"]["recentOrders"])

        # 4. Get active vouchers
        vouchers_result = get_active_vouchers(customer_id)
        if vouchers_result["code"] == 200:
            result["data"]["vouchers"] = vouchers_result["data"]["vouchers"]
            result["data"]["activeVoucherCount"] = len(vouchers_result["data"]["vouchers"])
        else:
            result["data"]["vouchers"] = []
            result["data"]["activeVoucherCount"] = 0

        # 5. Get unread notifications
        notifications_result = get_unread_notifications(customer_id)
        if notifications_result["code"] == 200:
            result["data"]["notifications"] = notifications_result["data"]["notifications"]
        else:
            result["data"]["notifications"] = []

        # 6. Get recommended restaurants
        recommended_restaurants = get_recommended_restaurants(customer_id, result["data"]["recentOrders"])
        result["data"]["recommendedRestaurants"] = recommended_restaurants

        return jsonify(result), result["code"]

    except Exception as e:
        # Unexpected error
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "displayPersonalizedHomepage.py internal error: " + ex_str
        }), 500


def get_customer_info(customer_id):
    """Get customer information including loyalty status"""
    print('\n-----Invoking customer microservice-----')
    customer_result = invoke_http(f"{customer_URL}/{customer_id}", method='GET')
    print('customer_result:', customer_result)
    
    return customer_result


def get_recent_transactions(customer_id):
    """Get recent transactions for a customer"""
    print('\n-----Invoking transaction microservice-----')
    transactions_result = invoke_http(f"{transaction_URL}/customer/{customer_id}", method='GET')
    print('transactions_result:', transactions_result)
    
    # If successful, limit to most recent transactions
    if transactions_result["code"] == 200:
        # Sort by created_at in descending order
        transactions = transactions_result["data"]["transactions"]
        sorted_transactions = sorted(
            transactions, 
            key=lambda x: datetime.strptime(x["created_at"], '%Y-%m-%d %H:%M:%S'),
            reverse=True
        )
        
        # Limit to specified number of transactions
        transactions_result["data"]["transactions"] = sorted_transactions
    
    return transactions_result


def enrich_transactions_with_items(transactions):
    """Add item details to each transaction"""
    enriched_transactions = []
    
    for transaction in transactions:
        transaction_id = transaction["transaction_id"]
        
        # Get transaction items
        print(f'\n-----Invoking transaction_item microservice for transaction {transaction_id}-----')
        items_result = invoke_http(f"{transaction_item_URL}/transaction/{transaction_id}", method='GET')
        print('items_result:', items_result)
        
        # Create a simplified transaction object
        enriched_transaction = {
            "id": transaction_id,
            "date": transaction["created_at"].split()[0],  # Just the date part
            "totalPrice": transaction["total_price_after_discount"],
            "status": transaction["status"],
            "restaurant_ids": set(),  # Track unique restaurant IDs
            "items": []
        }
        
        # Process transaction items if found
        if items_result["code"] == 200:
            items = items_result["data"]["transaction_items"]
            
            # Add restaurant IDs and process items
            for item in items:
                enriched_transaction["restaurant_ids"].add(item["restaurant_id"])
                
                # Get restaurant inventory item details
                inventory_item = get_inventory_item(item["restaurant_id"], item["item_id"])
                
                # Add item to the transaction
                if inventory_item:
                    enriched_transaction["items"].append({
                        "name": inventory_item["item_name"],
                        "quantity": item["quantity"],
                        "price": item["price_per_item"]
                    })
        
        # Convert restaurant_ids to list
        enriched_transaction["restaurant_ids"] = list(enriched_transaction["restaurant_ids"])
        
        # Get restaurant names
        enriched_transaction["restaurants"] = []
        for restaurant_id in enriched_transaction["restaurant_ids"]:
            restaurant_info = get_restaurant_info(restaurant_id)
            if restaurant_info:
                enriched_transaction["restaurants"].append({
                    "id": restaurant_id,
                    "name": restaurant_info["name"]
                })
        
        # Set the primary restaurant name for display (use the first one)
        if enriched_transaction["restaurants"]:
            enriched_transaction["restaurantName"] = enriched_transaction["restaurants"][0]["name"]
        else:
            enriched_transaction["restaurantName"] = "Unknown Restaurant"
        
        # Format items for display
        item_texts = [f"{item['name']} (x{item['quantity']})" for item in enriched_transaction["items"]]
        if item_texts:
            enriched_transaction["items_text"] = ", ".join(item_texts)
        else:
            enriched_transaction["items_text"] = "No items"
        
        enriched_transactions.append(enriched_transaction)
    
    return enriched_transactions


def get_inventory_item(restaurant_id, item_id):
    """Get details of a specific inventory item"""
    try:
        print(f'\n-----Invoking restaurant_inventory microservice for item {item_id}-----')
        item_result = invoke_http(f"{restaurant_inventory_URL}/{item_id}", method='GET')
        print('item_result:', item_result)
        
        if item_result["code"] == 200:
            return item_result["data"]
        
        return None
    except Exception as e:
        print(f"Error getting inventory item: {str(e)}")
        return None


def get_restaurant_info(restaurant_id):
    """Get restaurant information"""
    try:
        print(f'\n-----Invoking restaurant microservice for restaurant {restaurant_id}-----')
        restaurant_result = invoke_http(f"{restaurant_URL}/{restaurant_id}", method='GET')
        print('restaurant_result:', restaurant_result)
        
        if restaurant_result["code"] == 200:
            return restaurant_result["data"]
        
        return None
    except Exception as e:
        print(f"Error getting restaurant info: {str(e)}")
        return None


def get_active_vouchers(customer_id):
    """Get active vouchers for a customer"""
    print('\n-----Invoking voucher microservice-----')
    vouchers_result = invoke_http(f"{voucher_URL}/active/customer/{customer_id}", method='GET')
    print('vouchers_result:', vouchers_result)
    
    return vouchers_result


def get_unread_notifications(customer_id):
    """Get unread notifications for a customer"""
    print('\n-----Invoking notification microservice-----')
    notifications_result = invoke_http(f"{notification_URL}/unread/customer/{customer_id}", method='GET')
    print('notifications_result:', notifications_result)
    
    # Process notifications if found
    if notifications_result["code"] == 200:
        for notification in notifications_result["data"]["notifications"]:
            # Map notification types to frontend types
            if notification["message_type"] == "Payment_Success":
                notification["type"] = "payment"
                notification["title"] = "Payment Successful"
                # Remove the message field
                if "message" in notification:
                    del notification["message"]
            elif notification["message_type"] == "Refund_Processed":
                notification["type"] = "refund"
                notification["title"] = "Refund Processed"
                # Remove the message field
                if "message" in notification:
                    del notification["message"]
            elif notification["message_type"] == "Loyalty_Updated":
                notification["type"] = "loyalty"
                notification["title"] = "Loyalty Status Updated"
                # Remove the message field
                if "message" in notification:
                    del notification["message"]
            
            # Format time
            created_at = datetime.strptime(notification["created_at"], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            delta = now - created_at
            
            if delta.days > 0:
                notification["time"] = f"{delta.days} days ago"
            elif delta.seconds // 3600 > 0:
                notification["time"] = f"{delta.seconds // 3600} hours ago"
            else:
                notification["time"] = f"{delta.seconds // 60} minutes ago"
    
    return notifications_result
    """Get unread notifications for a customer"""
    print('\n-----Invoking notification microservice-----')
    notifications_result = invoke_http(f"{notification_URL}/unread/customer/{customer_id}", method='GET')
    print('notifications_result:', notifications_result)
    
    # Process notifications if found
    if notifications_result["code"] == 200:
        for notification in notifications_result["data"]["notifications"]:
            # Map notification types to frontend types
            if notification["message_type"] == "Payment_Success":
                notification["type"] = "payment"
                notification["title"] = "Payment Successful"
                notification["message"] = f"Your payment of ${notification.get('total_amount', '0.00')} was successful"
            elif notification["message_type"] == "Refund_Processed":
                notification["type"] = "refund"
                notification["title"] = "Refund Processed"
                notification["message"] = "Your refund has been processed successfully"
            elif notification["message_type"] == "Loyalty_Updated":
                notification["type"] = "loyalty"
                notification["title"] = "Loyalty Status Updated"
                notification["message"] = f"You now have {notification.get('loyalty_points', '0')} points and are {notification.get('loyalty_status', 'Bronze')} status"
            
            # Format time
            created_at = datetime.strptime(notification["created_at"], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            delta = now - created_at
            
            if delta.days > 0:
                notification["time"] = f"{delta.days} days ago"
            elif delta.seconds // 3600 > 0:
                notification["time"] = f"{delta.seconds // 3600} hours ago"
            else:
                notification["time"] = f"{delta.seconds // 60} minutes ago"
    
    return notifications_result

def get_recommended_restaurants(customer_id, recent_orders):
    """Get recommended restaurants sorted by highest rating"""
    try:
        # 1. Get list of all restaurants
        print('\n-----Invoking restaurant microservice for all restaurants-----')
        restaurants_result = invoke_http(f"{restaurant_URL}", method='GET')
        print('restaurants_result (truncated):', {k: v for k, v in restaurants_result.items() if k != 'data'})
        
        if restaurants_result["code"] != 200:
            # Return empty list if cannot get restaurants
            return []
        
        all_restaurants = restaurants_result["data"]["restaurants"]
        
        # 2. Sort restaurants by rating (highest first)
        sorted_restaurants = sorted(all_restaurants, key=lambda x: float(x["rating"]), reverse=True)
        
        # 3. Take top restaurants up to the limit
        top_restaurants = sorted_restaurants
        
        # 4. Format for frontend
        processed_restaurants = []
        for r in top_restaurants:
            processed_restaurants.append({
                "id": r["restaurant_id"],
                "name": r["name"],
                "cuisine": r["cuisine_type"],
                "rating": float(r["rating"]),
                "deliveryTime": "30-45 min",  # Placeholder - could calculate based on distance
                "image_url": r["image_url"]
            })
        
        return processed_restaurants
    
    except Exception as e:
        print(f"Error getting recommended restaurants: {str(e)}")
        # Return an empty list on error
        return []

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for displaying personalized homepage data...")
    app.run(host="0.0.0.0", port=5013, debug=True)