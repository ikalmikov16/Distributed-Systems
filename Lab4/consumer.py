from kafka import KafkaConsumer
import json

# Kafka configuration
KAFKA_CONFIG = {
    "bootstrap_servers": "kafka-3568f565-kafka-cluster.k.aivencloud.com:28805",
    "security_protocol": "SSL",
    "ssl_cafile": "certs/ca.pem",
    "ssl_certfile": "certs/service.cert", 
    "ssl_keyfile": "certs/service.key",  
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


print("Listening for messages...")
for message in consumer:
    print(f"Received message: {message.value}")

