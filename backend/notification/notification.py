from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime
import pika
import json
import uuid
import threading
import time

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/fooddelivery1"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# AMQP Configuration
RABBITMQ_HOST = environ.get('RABBITMQ_HOST') or 'localhost'
RABBITMQ_PORT = int(environ.get('RABBITMQ_PORT') or 5672)
RABBITMQ_USER = environ.get('RABBITMQ_USER') or 'guest'
RABBITMQ_PASSWORD = environ.get('RABBITMQ_PASSWORD') or 'guest'
NOTIFICATION_QUEUE = 'notification_queue'

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

# AMQP Helper Class
class AMQPClient:
    def __init__(self, host=RABBITMQ_HOST, port=RABBITMQ_PORT, 
                 user=RABBITMQ_USER, password=RABBITMQ_PASSWORD):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.channel = None
        self.connect()
        
    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=30,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare a durable queue
            self.channel.queue_declare(
                queue=NOTIFICATION_QUEUE,
                durable=True
            )
            print("Connected to RabbitMQ successfully")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {str(e)}")
            # Retry connection after a delay
            time.sleep(5)
            self.connect()
    
    def publish_message(self, message, routing_key=NOTIFICATION_QUEUE):
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
                
            self.channel.basic_publish(
                exchange='',
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Makes message persistent
                    content_type='application/json'
                )
            )
            return True
        except Exception as e:
            print(f"Failed to publish message: {str(e)}")
            # Try to reconnect
            try:
                self.connect()
                return False
            except:
                return False
    
    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

# Initialize AMQP client
amqp_client = AMQPClient()

# AMQP Consumer Thread
def consume_messages():
    consumer_client = AMQPClient()
    
    def callback(ch, method, properties, body):
        try:
            notification_data = json.loads(body)
            
            # Process the notification message
            with app.app_context():
                existing_notification = db.session.scalar(
                    db.select(Notification).filter_by(notification_id=notification_data['notification_id'])
                )
                
                if existing_notification:
                    print(f"Notification {notification_data['notification_id']} already exists, skipping.")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                
                # Create new notification
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
                    print(f"Successfully processed notification {notification_data['notification_id']}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"Error processing notification: {str(e)}")
                    db.session.rollback()
                    # Negative acknowledgment to requeue the message
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            print(f"Error in consumer callback: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    # Set prefetch count to 1 to ensure messages are distributed evenly
    consumer_client.channel.basic_qos(prefetch_count=1)
    
    # Start consuming with manual acknowledgment
    consumer_client.channel.basic_consume(
        queue=NOTIFICATION_QUEUE,
        on_message_callback=callback,
        auto_ack=False
    )
    
    print('Started consuming messages from queue')
    consumer_client.channel.start_consuming()

# Start the consumer thread
consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()

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
    # Check if notification already exists
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
    
    # Prepare notification data
    notification_data = {
        "notification_id": notification_id,
        "customer_id": data["customer_id"],
        "message_type": data["message_type"],
        "transaction_id": data.get("transaction_id"),
        "voucher_id": data.get("voucher_id"),
        "loyalty_points": data.get("loyalty_points"),
        "loyalty_status": data.get("loyalty_status"),
        "status": data.get("status", "Unread")
    }
    
    # Publish to queue for durable processing
    publish_success = amqp_client.publish_message(notification_data)
    
    if publish_success:
        return jsonify({
            "code": 202,  # Accepted
            "data": {"notification_id": notification_id},
            "message": "Notification request accepted and queued for processing."
        }), 202
    else:
        # Fallback to direct database write if queue is unavailable
        try:
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
            
            db.session.add(notification)
            db.session.commit()
            
            return jsonify({
                "code": 201,
                "data": notification.json(),
                "message": "Notification created directly (queue unavailable)."
            }), 201
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

# Graceful shutdown handler
def close_amqp_connection():
    print("Closing AMQP connection")
    amqp_client.close()

# Register shutdown handler
import atexit
atexit.register(close_amqp_connection)

# This will ensure the database tables match our models
with app.app_context():
    db.create_all()
    print("Database tables created/updated.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=True)