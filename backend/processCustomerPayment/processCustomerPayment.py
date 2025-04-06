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
transaction_item_URL = os.environ.get('transaction_item_URL') or "http://localhost:5010/transaction_item"
notification_URL = os.environ.get('notification_URL') or "http://localhost:5011/notification"
customer_URL = os.environ.get('customer_URL') or "http://localhost:5006/customer"
voucher_URL = os.environ.get('voucher_URL') or "http://localhost:5012/voucher"
stripe_service_URL = os.environ.get('stripe_service_URL') or "http://localhost:5021/payment/stripe"
restaurant_inventory_URL = os.environ.get('restaurant_inventory_URL') or "http://localhost:5008/restaurant_inventory"


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
        
        # Get loyalty points used (if any)
        loyalty_points_used = data.get("loyalty_points_used", 0)
        
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
        
        # Calculate loyalty points discount (each point is worth $0.10)
        loyalty_points_discount = loyalty_points_used * 0.1
        
        # Include loyalty points discount in total discount calculation
        total_discount = loyalty_discount_amount + voucher_discount + loyalty_points_discount
        total_price = total_without_discount - total_discount
        
        # Round to 2 decimal places for currency
        total_price = round(total_price, 2)
        
        # Generate order ID for the payment
        order_id = f"ORDER{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate loyalty points to use (if any)
        loyalty_points_used = data.get("loyalty_points_used", 0)

        # Calculate loyalty points to add (1 point per dollar spent)
        loyalty_points_added = int(total_price)
        
        # NEW: Create a transaction record
        transaction_id = f"TRANS{uuid.uuid4().hex[:8].upper()}"
        transaction_data = {
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "food_cost": float(food_cost),
            "delivery_cost": float(delivery_fee),
            "loyalty_discount_percentage": float(loyalty_discount_percentage),
            "total_price_after_discount": float(total_price),
            "loyalty_points_added": loyalty_points_added,
            "current_loyalty_points": loyalty_points + loyalty_points_added - loyalty_points_used,
            "current_loyalty_status": loyalty_status,
            "status": "Pending",
            "voucher_id": voucher_id if voucher_id else None,
            "rider_id": rider_id
        }
        
        # Create the transaction
        transaction_result = invoke_http(
            f"{transaction_URL}", 
            method='POST',
            json=transaction_data
        )
        
        # Check if transaction creation was successful
        if transaction_result["code"] not in range(200, 300):
            return jsonify({
                "code": transaction_result["code"],
                "message": "Failed to create transaction"
            }), transaction_result["code"]
        
        print("Transaction created:", transaction_result)
        
        # NEW: Create transaction items
        # Prepare items for batch creation
        batch_items = []
        for item in cart_items:
            transaction_item = {
                "transaction_id": transaction_id,
                "restaurant_id": item["restaurant_id"],
                "item_id": item["item_id"],
                "quantity": item["quantity"],
                "price_per_item": float(item["price"]),
                "total_price": float(item["price"] * item["quantity"])
            }
            batch_items.append(transaction_item)
        
        # Call the batch endpoint to create all items at once
        transaction_items_result = invoke_http(
            f"{transaction_item_URL}/batch",
            method='POST',
            json={"items": batch_items}
        )
        
        # Check if transaction items creation was successful
        if transaction_items_result["code"] not in range(200, 300):
            # Attempt to rollback the transaction since items failed
            try:
                invoke_http(f"{transaction_URL}/{transaction_id}", method='DELETE')
            except:
                pass  # Ignore rollback errors
                
            return jsonify({
                "code": transaction_items_result["code"],
                "message": "Failed to create transaction items"
            }), transaction_items_result["code"]
        
        print("Transaction items created:", transaction_items_result)
        
        # Prepare data for stripe service
        stripe_data = {
            "order_id": order_id,
            "transaction_id": transaction_id,  # Add transaction_id for reference
            "customer_id": customer_id,  # Add customer_id for reference
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
            # Attempt to rollback the transaction and items
            try:
                invoke_http(f"{transaction_URL}/{transaction_id}", method='DELETE')
            except:
                pass  # Ignore rollback errors
                
            return jsonify({
                "code": 500,
                "message": "Failed to create Stripe checkout session"
            }), 500
        
        # Extract session_id from the stripe response
        session_id = stripe_result.get("id")
        
        # Update transaction record with session_id if available
        if session_id:
            update_transaction = invoke_http(
                f"{transaction_URL}/{transaction_id}",
                method='PUT',
                json={"stripe_session_id": session_id}
            )
            
            if update_transaction["code"] not in range(200, 300):
                print(f"Warning: Failed to update transaction with Stripe session ID: {update_transaction}")
        
        # Prepare the order summary for the client
        order_summary = {
            "food_cost": float(food_cost),
            "delivery_fee": float(delivery_fee),
            "loyalty_discount": float(loyalty_discount_amount),
            "voucher_discount": float(voucher_discount),
            "total_price": float(total_price)
        }
        
        # Return the checkout URL, order ID, transaction ID, and order summary
        return jsonify({
            "code": 200,
            "data": {
                "checkout_url": stripe_result["url"],
                "order_id": order_id,
                "transaction_id": transaction_id,
                "order_summary": order_summary
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
        
        # Extract data
        session_id = data.get("session_id")
        order_id = data.get("order_id")
        transaction_id = data.get("transaction_id")
        customer_id = data.get("customer_id")
        
        # Validate required fields
        if not (session_id and customer_id):
            return jsonify({
                "code": 400,
                "message": "Missing required fields: session_id and customer_id are required"
            }), 400
        
        # If transaction_id is not provided, try to retrieve it from the Stripe session metadata
        if not transaction_id:
            # In a real implementation, you would call Stripe API to retrieve session details
            # For now, we'll return an error
            return jsonify({
                "code": 400,
                "message": "transaction_id is required"
            }), 400
        
        # Step 1: Update transaction status to 'Paid'
        transaction_status_update = invoke_http(
            f"{transaction_URL}/{transaction_id}/status",
            method='PUT',
            json={"status": "Paid"}
        )
        
        if transaction_status_update["code"] not in range(200, 300):
            print(f"Failed to update transaction status: {transaction_status_update}")
            # Continue processing even if this fails
        
        # Get transaction details to get the cart items and other information
        transaction_details = invoke_http(f"{transaction_URL}/{transaction_id}", method='GET')
        
        if transaction_details["code"] not in range(200, 300):
            return jsonify({
                "code": transaction_details["code"],
                "message": "Failed to retrieve transaction details"
            }), transaction_details["code"]
        
        transaction_data = transaction_details["data"]
        
        # Get transaction items
        transaction_items = invoke_http(
            f"{transaction_item_URL}/transaction/{transaction_id}", 
            method='GET'
        )
        
        if transaction_items["code"] not in range(200, 300):
            print(f"Failed to retrieve transaction items: {transaction_items}")
            # Continue processing even if this fails
        
        # Step 2: Update inventory for each item
        if transaction_items["code"] == 200 and "transaction_items" in transaction_items["data"]:
            for item in transaction_items["data"]["transaction_items"]:
                item_id = item["item_id"]
                quantity = item["quantity"]
                
                # Get current inventory level
                inventory_response = invoke_http(
                    f"{restaurant_inventory_URL}/{item_id}",
                    method='GET'
                )
                
                if inventory_response["code"] == 200:
                    current_stock = inventory_response["data"]["stock_quantity"]
                    new_stock = max(0, current_stock - quantity)
                    
                    # Update inventory
                    stock_update = invoke_http(
                        f"{restaurant_inventory_URL}/update_stock/{item_id}",
                        method='PUT',
                        json={"stock_quantity": new_stock}
                    )
                    
                    if stock_update["code"] not in range(200, 300):
                        print(f"Failed to update stock for item {item_id}: {stock_update}")
        
        # Step 3: Update customer loyalty
        # Calculate new loyalty points (already in the transaction data)
        loyalty_points_added = transaction_data["loyalty_points_added"]
        current_loyalty_points = transaction_data["current_loyalty_points"]
        
        # Update customer loyalty points
        loyalty_update = invoke_http(
            f"{customer_URL}/{customer_id}/loyalty",
            method='PUT',
            json={"loyalty_points": current_loyalty_points}
        )
        
        if loyalty_update["code"] not in range(200, 300):
            print(f"Failed to update customer loyalty: {loyalty_update}")
        
        # Step 4: Create success notification
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
        
        if notification_result["code"] not in range(200, 300):
            print(f"Failed to create notification: {notification_result}")
        
        # Prepare the response
        return jsonify({
            "code": 200,
            "data": {
                "transaction_id": transaction_id,
                "order_id": order_id,
                "payment_status": "success",
                "loyalty": {
                    "points_earned": loyalty_points_added,
                    "points_used": transaction_data.get("loyalty_points_used", 0),
                    "new_total_points": current_loyalty_points,
                    "status": transaction_data["current_loyalty_status"]
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
        
        if (event_type == 'checkout.session.completed'):
            session = event_data['data']['object']
            
            # Extract order details from metadata
            order_id = session.get('metadata', {}).get('order_id')
            transaction_id = session.get('metadata', {}).get('transaction_id')
            customer_id = session.get('metadata', {}).get('customer_id')
            
            # Process the successful payment
            if transaction_id and customer_id:
                # Call the payment_success function with the retrieved data
                payment_data = {
                    "session_id": session.id,
                    "order_id": order_id,
                    "transaction_id": transaction_id,
                    "customer_id": customer_id
                }
                
                # Create a new request to the payment_success endpoint
                success_response = requests.post(
                    f"http://localhost:5020/payment_success",
                    json=payment_data
                )
                
                if success_response.status_code == 200:
                    return jsonify({"received": True, "success": True}), 200
                else:
                    return jsonify({"received": True, "success": False}), 200
            
        return jsonify({"received": True}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=True)