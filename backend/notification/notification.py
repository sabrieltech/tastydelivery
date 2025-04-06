from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime
import pika
import json
import threading
import time

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:root@localhost:8889/fooddelivery1"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Notification(db.Model):
    __tablename__ = "notification"

    notification_id = db.Column(db.String(32), primary_key=True)
    customer_id = db.Column(db.String(32), nullable=False)
    message_type = db.Column(db.Enum('Payment_Success', 'Refund_Processed', 'Loyalty_Updated', 'Order_Delivered'), nullable=False)
    transaction_id = db.Column(db.String(32), nullable=True)
    voucher_id = db.Column(db.String(32), nullable=True)
    loyalty_points = db.Column(db.Integer, nullable=True)
    loyalty_status = db.Column(db.Enum('Bronze', 'Silver', 'Gold'), nullable=True)
    status = db.Column(db.Enum('Unread', 'Read'), nullable=False, default='Unread')
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)

    def __init__(self, notification_id, customer_id, message_type, transaction_id=None, 
                voucher_id=None, loyalty_points=None, loyalty_status=None, status='Unread'):
        self.notification_id = notification_id
        self.customer_id = customer_id
        self.message_type = message_type
        self.transaction_id = transaction_id
        self.voucher_id = voucher_id
        self.loyalty_points = loyalty_points
        self.loyalty_status = loyalty_status
        self.status = status

    def json(self):
        return {
            "notification_id": self.notification_id,
            "customer_id": self.customer_id,
            "message_type": self.message_type,
            "transaction_id": self.transaction_id,
            "voucher_id": self.voucher_id,
            "loyalty_points": self.loyalty_points,
            "loyalty_status": self.loyalty_status,
            "status": self.status,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# RabbitMQ Consumer Logic
def callback(ch, method, properties, body):
    notification_data = json.loads(body)
    print(f"Received Notification: {notification_data}")

    # Create and store notification in the database
    notification = Notification(
        notification_id=notification_data['notification_id'],
        customer_id=notification_data['customer_id'],
        message_type=notification_data['message_type'],
        transaction_id=notification_data.get('transaction_id'),
        voucher_id=notification_data.get('voucher_id'),
        loyalty_points=notification_data.get('loyalty_points'),
        loyalty_status=notification_data.get('loyalty_status'),
        status=notification_data.get('status', 'Unread')
    )

    try:
        db.session.add(notification)
        db.session.commit()
        print("Notification saved!")
    except Exception as e:
        print(f"Error saving notification: {str(e)}")

# Function to listen to RabbitMQ queues
def listen_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('guest', 'guest')))
            channel = connection.channel()

            # Declare the queues we're listening to
            channel.queue_declare(queue='Notification_Success', durable=True)
            channel.queue_declare(queue='Notification_Error', durable=True)

            # Bind to both queues
            channel.basic_consume(queue='Notification_Success', on_message_callback=callback, auto_ack=True)
            channel.basic_consume(queue='Notification_Error', on_message_callback=callback, auto_ack=True)

            print('Waiting for messages in Notification queues...')
            channel.start_consuming()
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {e}")
            time.sleep(5)  # Retry after 5 seconds if there's an error

# Start the RabbitMQ listener in the background
rabbitmq_thread = threading.Thread(target=listen_to_rabbitmq)
rabbitmq_thread.daemon = True  # Ensures the thread will exit when the main program exits
rabbitmq_thread.start()

@app.route("/notification")
def get_all():
    notifications = db.session.scalars(db.select(Notification)).all()

    if len(notifications):
        return jsonify(
            {
                "code": 200,
                "data": {"notifications": [notification.json() for notification in notifications]},
            }
        )
    return jsonify({"code": 404, "message": "There are no notifications."}), 404

@app.route("/notification/<string:notification_id>")
def find_by_notification_id(notification_id):
    notification = db.session.scalar(db.select(Notification).filter_by(notification_id=notification_id))

    if notification:
        return jsonify({"code": 200, "data": notification.json()})
    return jsonify({"code": 404, "message": "Notification not found."}), 404

@app.route("/notification/customer/<string:customer_id>")
def find_by_customer_id(customer_id):
    notifications = db.session.scalars(db.select(Notification).filter_by(customer_id=customer_id)).all()

    if len(notifications):
        return jsonify({
            "code": 200,
            "data": {"notifications": [notification.json() for notification in notifications]}
        })
    return jsonify({"code": 404, "message": "No notifications found for this customer."}), 404

@app.route("/notification/unread/customer/<string:customer_id>")
def find_unread_by_customer_id(customer_id):
    notifications = db.session.scalars(
        db.select(Notification).filter_by(customer_id=customer_id, status='Unread')
    ).all()

    if len(notifications):
        return jsonify({
            "code": 200,
            "data": {"notifications": [notification.json() for notification in notifications]}
        })
    return jsonify({"code": 404, "message": "No unread notifications found for this customer."}), 404

@app.route("/notification/<string:notification_id>", methods=["POST"])
def create_notification(notification_id):
    if db.session.scalar(db.select(Notification).filter_by(notification_id=notification_id)):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"notification_id": notification_id},
                    "message": "Notification already exists.",
                }
            ),
            400,
        )

    data = request.get_json()
    
    # Check for required fields
    required_fields = ["customer_id", "message_type"]
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "message": f"Field '{field}' is required."}), 400
    
    # Validate message_type
    valid_message_types = ['Payment_Success', 'Refund_Processed', 'Loyalty_Updated', 'Order_Delivered']
    if data['message_type'] not in valid_message_types:
        return jsonify({
            "code": 400,
            "message": f"Invalid message_type. Must be one of: {', '.join(valid_message_types)}"
        }), 400
    
    # Create new notification
    notification = Notification(
        notification_id=notification_id,
        customer_id=data["customer_id"],
        message_type=data["message_type"],
        transaction_id=data.get("transaction_id"),
        voucher_id=data.get("voucher_id"),
        loyalty_points=data.get("loyalty_points"),
        loyalty_status=data.get("loyalty_status"),
        status=data.get("status", "Unread")
    )

    try:
        db.session.add(notification)
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"notification_id": notification_id},
                    "message": "An error occurred creating the notification: " + str(e),
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": notification.json()}), 201

@app.route("/notification/<string:notification_id>/read", methods=["PUT"])
def mark_as_read(notification_id):
    notification = db.session.scalar(db.select(Notification).filter_by(notification_id=notification_id))
    
    if not notification:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"notification_id": notification_id},
                    "message": "Notification not found.",
                }
            ),
            404,
        )

    try:
        notification.status = 'Read'
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": notification.json(),
                "message": "Notification marked as read."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"notification_id": notification_id},
                    "message": "An error occurred updating the notification: " + str(e),
                }
            ),
            500,
        )


@app.route("/notification/mark_all_read/customer/<string:customer_id>", methods=["PUT"])
def mark_all_as_read(customer_id):
    notifications = db.session.scalars(
        db.select(Notification).filter_by(customer_id=customer_id, status='Unread')
    ).all()
    
    if not notifications:
        return jsonify({"code": 404, "message": "No unread notifications found for this customer."}), 404

    try:
        update_count = 0
        for notification in notifications:
            notification.status = 'Read'
            update_count += 1
            
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": f"Marked {update_count} notifications as read."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "message": "An error occurred updating the notifications: " + str(e),
                }
            ),
            500,
        )


@app.route("/notification/<string:notification_id>", methods=["DELETE"])
def delete_notification(notification_id):
    notification = db.session.scalar(db.select(Notification).filter_by(notification_id=notification_id))
    
    if not notification:
        return (
            jsonify(
                {
                    "code": 404,
                    "data": {"notification_id": notification_id},
                    "message": "Notification not found.",
                }
            ),
            404,
        )

    try:
        db.session.delete(notification)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Notification deleted successfully."
            }
        )
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"notification_id": notification_id},
                    "message": "An error occurred deleting the notification: " + str(e),
                }
            ),
            500,
        )

# This will ensure the database tables match our models
with app.app_context():
    db.create_all()
    print("Database tables created/updated.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=True)
