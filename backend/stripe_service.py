import stripe
from flask import request, jsonify, render_template
from flask_cors import cross_origin
from flask import Flask

app = Flask(__name__)

stripe_keys = {
    "secret_key": 'sk_test_51OrbjMC8yRcQdEl0w13nANLCRoKyTFoKWDmZWiZvUXtQKlmjvLBb46tpDSCHY0PHJzf58no91ZJs8ODKcjbf8DNg00mBFVAaJQ',
    "publishable_key": 'pk_test_51OrbjMC8yRcQdEl0iyEcmAtTVmPb7U7YVUPrtYyLd0fIAZvm4mtj5EwoQftTKCLcfryyiYTP1ioU4tcpTrhGjk21008zPpEqso'
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
        amount_paid = payment_intent.amount_received
        points = round(amount_paid)

        # Convert amount to a more readable format (e.g., from cents to dollars)
        amount_paid = amount_paid/100  # Adjust based on the smallest currency unit
        currency = payment_intent.currency
        points_used = checkout_session.metadata.get('points_used', '0')

        # Render success.html with dynamic payment details
        return render_template("success.html", payment_intent_id=payment_intent_id, amount_paid=amount_paid, currency=currency.upper(), deets=payment_intent, points=points, points_used=points_used)
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
    product_description = data.get('product_description', 'Flight Ticket')
    unit_amount = data.get('unit_amount', 0)
    points_used = data.get('points_used', 0)
    currency = data.get('currency', 'sgd')
    
    try:
        checkout_url = create_stripe_checkout_session(product_description, unit_amount, points_used, currency)
        return jsonify({"url": checkout_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_stripe_checkout_session(product_description, unit_amount, points_used, currency='sgd'):
    stripe.api_key = stripe_keys["secret_key"]
    try:
        product = stripe.Product.create(name='ticket', description=product_description)
        price = stripe.Price.create(product=product.id, unit_amount=unit_amount, currency=currency)
        # domain_url = "http://localhost:5004"

        checkout_session = stripe.checkout.Session.create(
            # success_url=f"{domain_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            # cancel_url=f"{domain_url}/payment/cancelled",
            #implement checkout id
            success_url="http://localhost:3000/payment?status=success",
            cancel_url="http://localhost:3000/payment?status=canceled",
            mode="payment",
            custom_text={
                "submit": {"message":"Points used: " + str(points_used)}
            },
            line_items=[{'price': price.id, 'quantity': 1}],
            metadata={"points_used": str(points_used)},  # Store points used here
        )
        return checkout_session["url"]
    # 
    except Exception as e:
        raise Exception(f"Stripe Checkout Session creation failed: {str(e)}")
#return stripe.redirectToCheckout({sessionId: data.sessionId}) --> redirects to stripe checkout page, shld be implemented on front end

# function 2 to flight inventory

def create_email_template(type, details):
    if type == "confirmation":
        subject = "Flight Booking Confirmed!"

        if "accommodation" in details:
            accommodation = details["accommodation"]
            message = f"Dear Sir/Madam, \n\nThanks for flying with Hotwings. \
            \n\n We're sorry to hear about your delayed flights and have arranged a new flight and accommodation for you. Your confirmed itinerary details are shown below: \
            \n\n Place of Origin: {details['origin']}\n Place of Destination: {details['destination']} \n Seat Numbers: {','.join([seat for seat in details['seat_num']])}\n \
            \n\nYou have successfully secured an accomodation at {accommodation['hotel_name']} located at {accommodation['location_near']} \
            \n\nWe hope you have a pleasant trip ahead! \
             \n\n~~~~~~~~~~Hotwings provide you the wings to fly to any destinations possible!~~~~~~~~~~"
        else: 
            message = f"Dear Sir/Madam, \n\nThanks for flying with Hotwings. \
            \n\nWe're excited to inform you of your flight details for your upcoming trip. Your confirmed itinerary details are shown below: \
            \n\n Place of Origin: {details['origin']}\n Place of Destination: {details['destination']} \n Seat Numbers: {','.join([seat for seat in details['seat_num']])} \
            \n\nWe hope you have a pleasant trip ahead!\
            \n\n~~~~~~~~~~Hotwings provide you the wings to fly to any destinations possible!~~~~~~~~~~"

    elif type == "points": 
        subject = "Accumulated Loyalty Points"
        message = f"Dear Sir/Madam, \n\nThanks for flying with Hotwings.\
        \n\nYour total loyalty point as of today is: {details}. \
        \n\nHope to see you onboard of our flight soon!\
        \n\n~~~~~~~~~~Hotwings provide you the wings to fly to any destinations possible!~~~~~~~~~~"

    elif type == "delay":
        subject = f"Notification: Delayed Flight {details['flight_id']}"
        message = f"Dear Sir/Madam,\
        \n\nWe regret to inform you there has been a delay to your scheduledn flight {details['flight_id']} from {details['origin']} to {details['destination']}.\
        \n\nWe sincerely apologize for any inconvenince this delay may cause you.Our team is working diligently to resolve the issue and get you on your way as soon as possible. Please rest assured that we will keep you updated with any further developments regarding your flight.\
        \n\nThank you for choosing to fly with us. We appreciate your understanding and look forward to welcoming you onboard soon. \
        \n\n~~~~~~~~~~Hotwings provide you the wings to fly to any destinations possible!~~~~~~~~~~"

    return {"subject": subject, "message": message}