from kafka import KafkaProducer
from bs4 import BeautifulSoup
import requests
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

# Initialize Kafka producer
producer = KafkaProducer(
    **KAFKA_CONFIG,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize data to JSON
)


def scrape_trending_topics():
    twitter_trends_url = "https://trends24.in/united-states/"
    response = requests.get(twitter_trends_url)

    if response.status_code != 200:
        print(f"Failed to fetch the website. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the sections with trends
    list_containers = soup.select("div.list-container")

    if not list_containers:
        print("No list containers found. Check the structure of the page.")
        return []

    trends = []

    for container in list_containers:
        # Get timestamp
        title_element = container.select_one("h3.title")
        if title_element:
            timestamp = title_element.get_text(strip=True)
        else:
            print("No timestamp found for this container. Skipping...")
            timestamp = None

        # Extract all trend items in this section
        trend_items = container.select("ol.trend-card__list li")
        for item in trend_items:
            trend_name_element = item.select_one(".trend-name a")
            tweet_count_element = item.select_one(".tweet-count")

            # Debugging: Check trend name and count
            if not trend_name_element:
                print("No trend name found for this item. Skipping...")
                continue

            trend_name = trend_name_element.get_text(strip=True)
            tweet_count = tweet_count_element["data-count"] if tweet_count_element and "data-count" in tweet_count_element.attrs else None

            # Format data and append to list
            trends.append({
                "trend_name": trend_name,
                "tweet_count": tweet_count,
                "timestamp": timestamp
            })

    return trends


trends = scrape_trending_topics()
if not trends:
    print("No trends found!")

for trend in trends:
    message = {"trend": trend}
    producer.send(TOPIC_NAME, value=message)
    print(f"Sent message: {message}")

producer.flush()
print("All messages sent!")
producer.close()
