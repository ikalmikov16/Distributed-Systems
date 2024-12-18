from kafka import KafkaConsumer
import json

# Kafka configuration
KAFKA_CONFIG = {
    "bootstrap_servers": "kafka-3568f565-kafka-cluster.k.aivencloud.com:28805",  # Replace with your Aiven Kafka bootstrap server
    "security_protocol": "SSL",
    "ssl_cafile": "certs/ca.pem",          # Path to CA certificate
    "ssl_certfile": "certs/service.cert", # Path to Service certificate
    "ssl_keyfile": "certs/service.key",   # Path to Service key
}

TOPIC_NAME = "trending-topics"

# Initialize Kafka consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    **KAFKA_CONFIG,
    group_id="trending-consumer-group",
    auto_offset_reset="earliest",  # Read messages from the beginning if no offset is set
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))  # Deserialize JSON data
)

def consume_messages():
    print("Listening for messages...")

    for message in consumer:
        print(f"Received message: {message.value}")

if __name__ == "__main__":
    consume_messages()
