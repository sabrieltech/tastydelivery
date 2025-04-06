from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# URLs for the microservices
transaction_URL = os.environ.get('transaction_URL') or "http://localhost:5009/transaction"
transaction_item_URL = os.environ.get('transaction_item_URL') or "http://localhost:5010/transaction_item"
notification_URL = os.environ.get('notification_URL') or "http://localhost:5011/notification"
customer_URL = os.environ.get('customer_URL') or "http://localhost:5006/customer"
voucher_URL = os.environ.get('voucher_URL') or "http://localhost:5012/voucher"
stripe_service_URL = os.environ.get('stripe_service_URL') or "http://localhost:5021/payment/refund"
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


@app.route('/process_refund', methods=['POST'])
def process_refund():
    """
    Process a refund for a food delivery order
    This is a composite service that orchestrates multiple atomic services
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["transaction_id", "customer_id", "refund_amount", "refund_reason"]
        for field in required_fields:
            if field not in data:
                return jsonify({"code": 400, "message": f"Missing required field: {field}"}), 400
        
        # Extract data
        transaction_id = data["transaction_id"]
        customer_id = data["customer_id"]
        refund_amount = float(data["refund_amount"])
        refund_reason = data["refund_reason"]
        
        # Step 1: Get transaction details to verify it exists and is valid for refund
        transaction_result = invoke_http(f"{transaction_URL}/{transaction_id}", method='GET')
        
        if transaction_result["code"] not in range(200, 300):
            return jsonify({
                "code": transaction_result["code"],
                "message": "Failed to retrieve transaction details"
            }), transaction_result["code"]
        
        transaction_data = transaction_result["data"]
        
        # Verify the transaction belongs to the customer
        if transaction_data["customer_id"] != customer_id:
            return jsonify({
                "code": 403,
                "message": "Transaction does not belong to this customer"
            }), 403
        
        # Verify the transaction is in a valid state for refund (Paid)
        if transaction_data["status"] != "Paid":
            return jsonify({
                "code": 400,
                "message": f"Transaction cannot be refunded (current status: {transaction_data['status']})"
            }), 400
        
        # Verify the refund amount is valid (not more than the original amount)
        if refund_amount > transaction_data["total_price_after_discount"]:
            return jsonify({
                "code": 400,
                "message": f"Refund amount (${refund_amount}) cannot exceed the original transaction amount (${transaction_data['total_price_after_discount']})"
            }), 400
        
        # Step 2: Process the refund through Stripe
        # Get the stripe_session_id from the transaction if available, otherwise use transaction_id
        stripe_session_id = transaction_data.get("stripe_session_id", transaction_id)
        
        stripe_refund_data = {
            "session_id": stripe_session_id,
            "amount": refund_amount
        }
        
        stripe_result = invoke_http(
            stripe_service_URL,
            method='POST',
            json=stripe_refund_data
        )
        
        if "error" in stripe_result:
            return jsonify({
                "code": 500,
                "message": f"Failed to process refund with payment provider: {stripe_result['error']}"
            }), 500
        
        # Step 3: Update transaction status to Refunded
        update_transaction = invoke_http(
            f"{transaction_URL}/{transaction_id}/status",
            method='PUT',
            json={"status": "Refunded"}
        )
        
        if update_transaction["code"] not in range(200, 300):
            print(f"Warning: Failed to update transaction status: {update_transaction}")
            # Continue processing even if this fails
        
        # Step 4: Update customer loyalty points (if applicable)
        # Calculate loyalty points to deduct (from the original earned points)
        loyalty_points_to_deduct = int(refund_amount)
        
        # Only update if points need to be deducted
        if loyalty_points_to_deduct > 0:
            # Get current customer info
            customer_result = invoke_http(f"{customer_URL}/{customer_id}", method='GET')
            
            if customer_result["code"] in range(200, 300):
                customer_data = customer_result["data"]
                current_points = customer_data["loyalty_points"]
                
                # Calculate new points (don't go below 0)
                new_points = max(0, current_points - loyalty_points_to_deduct)
                
                # Update customer loyalty points
                loyalty_update = invoke_http(
                    f"{customer_URL}/{customer_id}/loyalty",
                    method='PUT',
                    json={"loyalty_points": new_points}
                )
                
                if loyalty_update["code"] not in range(200, 300):
                    print(f"Warning: Failed to update customer loyalty points: {loyalty_update}")
        
        # Step 5: Create a notification for the customer
        notification_id = f"NOTIF{uuid.uuid4().hex[:8].upper()}"
        notification_data = {
            "notification_id": notification_id,
            "customer_id": customer_id,
            "message_type": "Refund_Processed",
            "transaction_id": transaction_id,
            "status": "Unread"
        }
        
        notification_result = invoke_http(
            f"{notification_URL}/{notification_id}",
            method='POST',
            json=notification_data
        )
        
        if notification_result["code"] not in range(200, 300):
            print(f"Warning: Failed to create notification: {notification_result}")
        
        # Step 6: Create a refund record (in a real system, you might have a separate refund table)
        refund_id = f"REFUND{uuid.uuid4().hex[:8].upper()}"
        
        # Return success response
        return jsonify({
            "code": 200,
            "data": {
                "refund_id": refund_id,
                "transaction_id": transaction_id,
                "refund_amount": refund_amount,
                "refund_status": "Processed",
                "stripe_refund_id": stripe_result.get("refund_id"),
                "loyalty_points_deducted": loyalty_points_to_deduct
            },
            "message": "Refund processed successfully"
        }), 200
        
    except Exception as e:
        print(f"Error processing refund: {str(e)}")
        
        return jsonify({
            "code": 500,
            "message": "An unexpected error occurred while processing the refund",
            "error": str(e)
        }), 500


@app.route('/eligible_refunds/<string:customer_id>', methods=['GET'])
def get_eligible_refunds(customer_id):
    """
    Get transactions eligible for refund for a specific customer
    """
    try:
        # Get all transactions for the customer
        transactions_result = invoke_http(f"{transaction_URL}/customer/{customer_id}", method='GET')
        
        if transactions_result["code"] not in range(200, 300):
            return jsonify({
                "code": transactions_result["code"],
                "message": "Failed to retrieve customer transactions"
            }), transactions_result["code"]
        
        # Filter transactions to only include those eligible for refund (Paid status and within 7 days)
        eligible_transactions = []
        current_time = datetime.now()
        
        for transaction in transactions_result["data"]["transactions"]:
            # Parse transaction timestamp
            transaction_time = datetime.strptime(transaction["created_at"], '%Y-%m-%d %H:%M:%S')
            
            # Calculate time difference in days
            time_diff = (current_time - transaction_time).total_seconds() / (60 * 60 * 24)
            
            # Check if transaction is eligible (Paid status and within 7 days)
            if transaction["status"] == "Paid" and time_diff <= 7:
                # Get transaction items for more details
                items_result = invoke_http(
                    f"{transaction_item_URL}/transaction/{transaction['transaction_id']}", 
                    method='GET'
                )
                
                if items_result["code"] == 200 and "transaction_items" in items_result["data"]:
                    transaction["items"] = items_result["data"]["transaction_items"]
                else:
                    transaction["items"] = []
                
                eligible_transactions.append(transaction)
        
        return jsonify({
            "code": 200,
            "data": {
                "eligible_transactions": eligible_transactions
            }
        }), 200
        
    except Exception as e:
        print(f"Error retrieving eligible refunds: {str(e)}")
        
        return jsonify({
            "code": 500,
            "message": "An unexpected error occurred while retrieving eligible refunds",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5022, debug=True)