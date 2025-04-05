from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# URLs for the microservices
dynamic_pricing_URL = os.environ.get('dynamic_pricing_URL') or "http://localhost:5016/calculate_delivery_fee"
transaction_URL = os.environ.get('transaction_URL') or "http://localhost:5009/transaction"
notification_URL = os.environ.get('notification_URL') or "http://localhost:5011/notification"
customer_URL = os.environ.get('customer_URL') or "http://localhost:5006/customer"
voucher_URL = os.environ.get('voucher_URL') or "http://localhost:5012/voucher"
stripe_service_URL = os.environ.get('stripe_service_URL') or "http://localhost:5004/payment/stripe"

# Helper function for HTTP requests to other microservices
def invoke_http(url, method='GET', json=None, **kwargs):
    """
    A simple wrapper for requests methods.
    """
    code = 200
    result = {}
    
    try:
        if method.upper() == 'GET':
            r = requests.get(url, **kwargs)
        elif method.upper() == 'POST':
            r = requests.post(url, json=json, **kwargs)
        elif method.upper() == 'PUT':
            r = requests.put(url, json=json, **kwargs)
        elif method.upper() == 'DELETE':
            r = requests.delete(url, **kwargs)
        else:
            raise Exception(f"HTTP method '{method}' is not supported.")
        
        code = r.status_code
        
        try:
            result = r.json() if r.text else {}
        except Exception as e:
            result = {"code": code, "message": r.text}
            
    except Exception as e:
        code = 500
        result = {
            "code": code,
            "message": f"Error in invoking HTTP request: {str(e)}"
        }
    
    return result


@app.route('/process_payment', methods=['POST'])
def process_payment():
    """
    Process a payment for a food delivery order
    This is a composite service that orchestrates multiple atomic services
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["customer_id", "cart_items"]
        for field in required_fields:
            if field not in data:
                return jsonify({"code": 400, "message": f"Missing required field: {field}"}), 400
        
        # Extract data
        customer_id = data["customer_id"]
        cart_items = data["cart_items"]
        voucher_id = data.get("voucher_id")
        voucher_code = data.get("voucher_code")
        
        # Get customer info (for loyalty status)
        customer_result = invoke_http(f"{customer_URL}/{customer_id}", method='GET')
        
        if customer_result["code"] not in range(200, 300):
            return jsonify({
                "code": customer_result["code"],
                "message": "Failed to get customer information"
            }), customer_result["code"]
        
        customer_data = customer_result["data"]
        loyalty_status = customer_data["loyalty_status"]
        loyalty_points = customer_data["loyalty_points"]
        
        # Calculate food cost from cart items
        food_cost = sum(item["price"] * item["quantity"] for item in cart_items)
        
        # Get restaurant IDs from cart items
        restaurant_ids = set(item["restaurant_id"] for item in cart_items if "restaurant_id" in item)
        restaurant_names = set(item.get("restaurant_name", "Unknown") for item in cart_items)
        
        if not restaurant_ids:
            return jsonify({"code": 400, "message": "No valid restaurant IDs found in cart items"}), 400
        
        restaurant_id = list(restaurant_ids)[0]
        restaurant_name = list(restaurant_names)[0]
        
        rider_id = "RIDER001"  # Placeholder; should be assigned dynamically
        
        # Calculate delivery fee using dynamic pricing service
        pricing_result = invoke_http(f"{dynamic_pricing_URL}/{restaurant_id}/{rider_id}", method='GET')
        
        if pricing_result["code"] not in range(200, 300):
            return jsonify({
                "code": pricing_result["code"],
                "message": "Failed to calculate delivery fee"
            }), pricing_result["code"]
        
        delivery_fee = pricing_result["data"]["delivery_fee"]
        
        # Calculate loyalty discount
        loyalty_discount_percentage = 0
        if loyalty_status == "Silver":
            loyalty_discount_percentage = 5  # 5% discount
        elif loyalty_status == "Gold":
            loyalty_discount_percentage = 10  # 10% discount
        
        # Calculate voucher discount
        voucher_discount = 0
        voucher_data = None
        
        if voucher_id or voucher_code:
            # Validate and retrieve voucher details
            if voucher_id:
                voucher_result = invoke_http(f"{voucher_URL}/{voucher_id}", method='GET')
            else:
                voucher_result = invoke_http(f"{voucher_URL}/code/{voucher_code}", method='GET')
            
            
            if voucher_result["code"] == 200 and voucher_result["data"]:
                voucher_data = voucher_result["data"]
                
                # Check if voucher is active and for this customer
                if voucher_data["status"] == "Active" and (voucher_data["customer_id"] is None or voucher_data["customer_id"] == customer_id):
                    # Calculate voucher discount
                    discount_percentage = voucher_data["discount_percentage"]
                    max_discount = voucher_data["max_discount_amount"]
                    
                    calculated_discount = (food_cost + delivery_fee) * (discount_percentage / 100)
                    voucher_discount = min(calculated_discount, max_discount)
        
        # Calculate total before and after discounts
        subtotal = food_cost
        total_without_discount = food_cost + delivery_fee
        loyalty_discount_amount = total_without_discount * (loyalty_discount_percentage / 100)
        total_discount = loyalty_discount_amount + voucher_discount
        total_price = total_without_discount - total_discount
        
        # Round to 2 decimal places for currency
        total_price = round(total_price, 2)
        
        # Generate order ID for the payment
        order_id = f"ORDER{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate loyalty points to use (if any)
        loyalty_points_used = data.get("loyalty_points_used", 0)
        
        # Prepare data for stripe service
        stripe_data = {
            "order_id": order_id,
            "restaurant_name": restaurant_name,
            "subtotal": float(food_cost),
            "delivery_fee": float(delivery_fee),
            "discount_amount": float(total_discount),
            "loyalty_points_used": loyalty_points_used
        }
        
        # Call stripe service to create checkout session
        stripe_result = invoke_http(
            stripe_service_URL,
            method='POST',
            json=stripe_data
        )
        
        if "url" not in stripe_result:
            return jsonify({
                "code": 500,
                "message": "Failed to create Stripe checkout session"
            }), 500
        
        # Store payment details in session/database for later use
        # In a real application, you'd save this information to process once payment is completed
        payment_data = {
            "order_id": order_id,
            "customer_id": customer_id,
            "restaurant_id": restaurant_id,
            "rider_id": rider_id,
            "food_cost": float(food_cost),
            "delivery_fee": float(delivery_fee),
            "loyalty_discount_percentage": float(loyalty_discount_percentage),
            "loyalty_discount_amount": float(loyalty_discount_amount),
            "voucher_discount": float(voucher_discount),
            "total_price": float(total_price),
            "voucher_id": voucher_id if voucher_id else None,
            "loyalty_points_used": loyalty_points_used,
            "cart_items": cart_items
        }
        
        # When implementing a full solution, store payment_data to a database
        # or session store to be retrieved when webhook is received
        
        # Return the checkout URL
        return jsonify({
            "code": 200,
            "data": {
                "checkout_url": stripe_result["url"],
                "order_id": order_id,
                "order_summary": {
                    "food_cost": float(food_cost),
                    "delivery_fee": float(delivery_fee),
                    "loyalty_discount": float(loyalty_discount_amount),
                    "voucher_discount": float(voucher_discount),
                    "total_price": float(total_price)
                }
            }
        }), 200
            
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        
        return jsonify({
            "code": 500,
            "message": "An unexpected error occurred while processing payment",
            "error": str(e)
        }), 500


@app.route('/payment_success', methods=['POST'])
def payment_success():
    """
    Handle successful payment from Stripe webhook or redirect
    """
    try:
        data = request.get_json()
        
        # In a real implementation, you'd validate the webhook signature
        # and retrieve the order details from your database
        
        # Extract data
        session_id = data.get("session_id")
        order_id = data.get("order_id")
        customer_id = data.get("customer_id")
        
        # Retrieve the payment details saved earlier
        # In a real app, you'd fetch this from a database
        # payment_data = get_payment_data_from_db(order_id)
        
        # For this example, we'll just mock it
        payment_data = {
            "customer_id": customer_id,
            "food_cost": 50.0,
            "delivery_fee": 5.0,
            "loyalty_discount_percentage": 5,
            "total_price_after_discount": 52.25,
            "loyalty_points_added": 52,
            "rider_id": "RIDER001",
            "voucher_id": None
        }
        
        # Get customer info for loyalty update
        customer_result = invoke_http(f"{customer_URL}/{customer_id}", method='GET')
        if customer_result["code"] not in range(200, 300):
            return jsonify({
                "code": customer_result["code"],
                "message": "Failed to get customer information"
            }), customer_result["code"]
        
        customer_data = customer_result["data"]
        loyalty_points = customer_data["loyalty_points"]
        loyalty_status = customer_data["loyalty_status"]
        
        # Calculate loyalty points earned (1 point per $1 spent)
        loyalty_points_added = int(payment_data["total_price_after_discount"])
        new_loyalty_points = loyalty_points + loyalty_points_added
        
        # Update loyalty status if needed
        new_loyalty_status = loyalty_status
        if new_loyalty_points >= 300 and loyalty_status != "Gold":
            new_loyalty_status = "Gold"
        elif new_loyalty_points >= 100 and loyalty_status == "Bronze":
            new_loyalty_status = "Silver"
        
        # Generate a unique transaction ID
        transaction_id = f"TRANS{uuid.uuid4().hex[:8].upper()}"
        
        # Save transaction to database
        transaction_data = {
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "food_cost": payment_data["food_cost"],
            "delivery_cost": payment_data["delivery_fee"],
            "loyalty_discount_percentage": payment_data["loyalty_discount_percentage"],
            "total_price_after_discount": payment_data["total_price_after_discount"],
            "loyalty_points_added": loyalty_points_added,
            "current_loyalty_points": new_loyalty_points,
            "current_loyalty_status": new_loyalty_status,
            "status": "Paid",
            "voucher_id": payment_data["voucher_id"],
            "rider_id": payment_data["rider_id"]
        }
        
        transaction_result = invoke_http(
            f"{transaction_URL}", 
            method='POST',
            json=transaction_data
        )
        
        # Create a payment success notification
        notification_id = f"NOTIF{uuid.uuid4().hex[:8].upper()}"
        notification_data = {
            "notification_id": notification_id,
            "customer_id": customer_id,
            "message_type": "Payment_Success",
            "transaction_id": transaction_id,
            "status": "Unread"
        }
        
        notification_result = invoke_http(
            f"{notification_URL}/{notification_id}",
            method='POST',
            json=notification_data
        )
        
        # Create loyalty update notification if status changed
        if new_loyalty_status != loyalty_status:
            loyalty_notification_id = f"NOTIF{uuid.uuid4().hex[:8].upper()}"
            loyalty_notification_data = {
                "notification_id": loyalty_notification_id,
                "customer_id": customer_id,
                "message_type": "Loyalty_Updated",
                "loyalty_points": new_loyalty_points,
                "loyalty_status": new_loyalty_status,
                "status": "Unread"
            }
            
            loyalty_notification_result = invoke_http(
                f"{notification_URL}/{loyalty_notification_id}",
                method='POST',
                json=loyalty_notification_data
            )
        
        # Update customer's loyalty points and status
        customer_update_data = {
            "loyalty_points": new_loyalty_points,
            "loyalty_status": new_loyalty_status
        }
        
        customer_update_result = invoke_http(
            f"{customer_URL}/{customer_id}",
            method='PUT',
            json=customer_update_data
        )
        
        return jsonify({
            "code": 200,
            "data": {
                "transaction_id": transaction_id,
                "order_id": order_id,
                "payment_status": "success",
                "loyalty": {
                    "points_earned": loyalty_points_added,
                    "new_total_points": new_loyalty_points,
                    "status": new_loyalty_status
                }
            }
        }), 200
        
    except Exception as e:
        print(f"Error processing successful payment: {str(e)}")
        
        return jsonify({
            "code": 500,
            "message": "An unexpected error occurred while processing successful payment",
            "error": str(e)
        }), 500


# Webhook endpoint for Stripe
@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    
    # In a real implementation, you would verify the webhook signature
    # and handle different event types
    
    try:
        event_data = request.get_json()
        event_type = event_data.get('type')
        
        if event_type == 'checkout.session.completed':
            session = event_data['data']['object']
            
            # Extract order details from metadata
            order_id = session.get('metadata', {}).get('order_id')
            customer_id = session.get('metadata', {}).get('customer_id')
            
            # Process the successful payment
            # This would call your payment_success function or similar
            # For now, we'll just return a success response
            
            return jsonify({"received": True, "success": True}), 200
        
        return jsonify({"received": True}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=True)