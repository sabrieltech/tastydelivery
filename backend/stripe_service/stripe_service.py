import stripe
from flask import Flask, request, jsonify, render_template
from flask_cors import cross_origin

app = Flask(__name__)

stripe_keys = {
    "secret_key": 'sk_test_51RABcdQOf6nNEYS6EtcT2rpS2rhh2C8OS27gNG9JQDFF6NZk90wiveaJabUHnF2OoCq8qyF54xCLBprVCByTMyUQ00jvBngMEk',
    "publishable_key": 'pk_test_51RABcdQOf6nNEYS6gkG9lNJJbOojM2bXxkZfgwDNfutZH6AAkiStVVqO7Z49kvRzSs2eAvggP6l5IveRoQBjZybR00I0oI8Kim'
}

stripe.api_key = stripe_keys['secret_key']

@app.route('/payment/success', methods=["GET"])
def payment_success():
    # Retrieve the session ID from the query string
    session_id = request.args.get('session_id')

    if not session_id:
        return "Session ID is missing", 400

    try:
        # Retrieve the checkout session to get the payment_intent
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        payment_intent_id = checkout_session.payment_intent

        # Retrieve the payment intent to get details like amount and currency
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        amount_paid = payment_intent.amount_received / 100  # Convert from cents to dollars
        
        # Calculate loyalty points - $1 = 1 point
        loyalty_points_earned = round(amount_paid)
        
        # Get the delivery fee, order details, and loyalty points from metadata
        order_id = checkout_session.metadata.get('order_id', '')
        transaction_id = checkout_session.metadata.get('transaction_id', '')
        customer_id = checkout_session.metadata.get('customer_id', '')
        restaurant_name = checkout_session.metadata.get('restaurant_name', '')
        delivery_fee = checkout_session.metadata.get('delivery_fee', '0')
        subtotal = checkout_session.metadata.get('subtotal', '0')
        loyalty_points_used = checkout_session.metadata.get('loyalty_points_used', '0')
        
        # Render success.html with dynamic payment details
        return render_template(
            "success.html", 
            payment_intent_id=payment_intent_id, 
            amount_paid=amount_paid, 
            currency=payment_intent.currency.upper(),
            order_id=order_id,
            transaction_id=transaction_id,
            customer_id=customer_id,
            restaurant_name=restaurant_name,
            delivery_fee=delivery_fee,
            subtotal=subtotal,
            loyalty_points_earned=loyalty_points_earned,
            loyalty_points_used=loyalty_points_used
        )
    except stripe.error.StripeError as e:
        # Handle Stripe errors (e.g., session not found)
        return jsonify(error=str(e)), 403
    except Exception as e:
        # Handle other exceptions
        return jsonify(error=str(e)), 500

@app.route('/payment/stripe', methods=["POST"])
@cross_origin()
def process_stripe_payment():
    # Extract data from request
    data = request.json
    
    # Required fields from the checkout process
    order_id = data.get('order_id', '')
    transaction_id = data.get('transaction_id', '')
    customer_id = data.get('customer_id', '')
    restaurant_name = data.get('restaurant_name', '')
    subtotal = data.get('subtotal', 0)
    delivery_fee = data.get('delivery_fee', 0)
    discount_amount = data.get('discount_amount', 0)
    loyalty_points_used = data.get('loyalty_points_used', 0)
    
    # Calculate loyalty discount (each point is worth $0.10)
    loyalty_discount = loyalty_points_used * 0.1
    
    # Calculate total amount in cents (Stripe requires amounts in smallest currency unit)
    # Accounting for both voucher discount and loyalty points discount
    total_amount = int((subtotal + delivery_fee - discount_amount - loyalty_discount) * 100)
    
    # Create product description
    product_description = f"Food order from {restaurant_name}"
    
    try:
        checkout_url, session_id = create_stripe_checkout_session(
            product_description, 
            total_amount, 
            order_id,
            transaction_id,
            customer_id,
            restaurant_name,
            subtotal,
            delivery_fee,
            loyalty_points_used
        )
        return jsonify({"url": checkout_url, "id": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_stripe_checkout_session(
    product_description, 
    total_amount, 
    order_id,
    transaction_id,
    customer_id,
    restaurant_name,
    subtotal,
    delivery_fee,
    loyalty_points_used,
    currency='sgd'
):
    stripe.api_key = stripe_keys["secret_key"]
    try:
        # Create a checkout session using the current Stripe API format
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': 'Food Delivery Order',
                            'description': product_description,
                        },
                        'unit_amount': total_amount,
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url="http://localhost:8080/app/order-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:8080/app/cart",
            metadata={
                "order_id": order_id,
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "restaurant_name": restaurant_name,
                "subtotal": str(subtotal),
                "delivery_fee": str(delivery_fee),
                "loyalty_points_used": str(loyalty_points_used)
            }
        )
        return checkout_session.url, checkout_session.id
    except Exception as e:
        raise Exception(f"Stripe Checkout Session creation failed: {str(e)}")

@app.route('/payment/refund', methods=["POST"])
@cross_origin()
def process_refund():
    data = request.json
    session_id = data.get('session_id')  # Changed to session_id
    amount = data.get('amount')  # Amount to refund in dollars

    try:
        # Retrieve checkout session
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        payment_intent_id = checkout_session.payment_intent

        refund = create_stripe_refund(payment_intent_id, amount)
        return jsonify({"refund_id": refund.id, "status": refund.status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_stripe_refund(payment_intent_id, amount, currency='sgd'):
    stripe.api_key = stripe_keys["secret_key"]
    try:
        # Stripe requires amount in cents
        amount_in_cents = int(amount * 100)
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=amount_in_cents,
            currency=currency
        )
        return refund
    except Exception as e:
        raise Exception(f"Stripe Refund creation failed: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5021, debug=True)