#!/usr/bin/env python3

import pika
import os
import json

amqp_host = os.getenv('RABBITMQ_HOST', 'localhost')  
amqp_port = 5672
exchange_name = "notification_exchange"
exchange_type = "topic"

def create_exchange(hostname, port, exchange_name, exchange_type):
    print(f"Connecting to AMQP broker {hostname}:{port}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname,
            port=port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected")

    channel = connection.channel()

    # Declare exchange as durable
    print(f"Declare exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True
    )

    return channel

def create_queue(channel, exchange_name, queue_name, routing_key):
    print(f"Bind to queue: {queue_name}")
    # Declare the queue as durable
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
    print(f"Queue {queue_name} bound with routing_key {routing_key}")

# Create exchange and queues for notifications
channel = create_exchange(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name=exchange_name,
    exchange_type=exchange_type,
)

# Create queues for notification messages with specific routing keys
create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="Notification_Success",
    routing_key="notification.success"
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="Notification_Error",
    routing_key="notification.error"
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="Notification_Generic",
    routing_key="notification.*"
)
