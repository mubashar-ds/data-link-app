from cassandra.cluster import Cluster
import pandas as pd
import matplotlib.pyplot as plt

### Cassandra Driver Setup.....

# Connect to Cassandra keyspace...

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('datalink')

# Fetch interaction actions..

rows = session.execute("SELECT action FROM activity_logs")

# Count actions..

action_counts = {}
for row in rows:
    action = row.action
    action_counts[action] = action_counts.get(action, 0) + 1

# Convert to DataFrame...

df = pd.DataFrame(list(action_counts.items()), columns=["Action", "Count"])

# Plot bar chart...

df.plot(kind='bar', x='Action', y='Count', legend=False, title="User Interactions Count")
plt.xlabel("Interaction Type")
plt.ylabel("Frequency")
plt.tight_layout()
plt.show()


### Insert Data from json....


### Insert User Interaction.....

import psycopg2
import json

# Database connection..

def get_db_connection():
    return psycopg2.connect(
        dbname="datalink_db",
        user="datalink",
        password="1234",
        host="localhost",
        port="5432"
    )

# Function to insert user connections...

def insert_user_connections(json_file):
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(json_file, "r") as file:
        data = json.load(file)

    insert_query = """
        INSERT INTO user_connections (connection_id, user_id_1, user_id_2, connected_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (connection_id) DO NOTHING
    """

    for conn_record in data:
        cursor.execute(insert_query, (
            conn_record["connection_id"],
            conn_record["user_id_1"],
            conn_record["user_id_2"],
            conn_record["connected_at"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("User connections inserted successfully.")

# Run...

if __name__ == "__main__":
    insert_user_connections(r"E:\Bigdata_project\Datasets\3000000_user_connections.json")


import psycopg2
import json

# Database connection setup..

def get_db_connection():
    return psycopg2.connect(
        dbname="datalink_db",  
        user="datalink",      
        password="1234",      
        host="localhost",     
        port="5432"           
    )

# Function to insert data into PostgreSQL..

def insert_data_from_json(json_file):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Read the JSON file..

    with open(json_file, 'r') as file:
        data = json.load(file)

    # SQL query for inserting data..

    insert_query = """
        INSERT INTO system_metadata (parameter_name, parameter_value, last_updated)
        VALUES (%s, %s, %s)
    """

    # Loop through the data and insert each record...

    for record in data:
        parameter_name = record['parameter_name']
        parameter_value = record['parameter_value']
        last_updated = record['last_updated']
        
        cursor.execute(insert_query, (parameter_name, parameter_value, last_updated))

    # Commit and close the connection...

    conn.commit()
    cursor.close()
    conn.close()

    print("Data inserted successfully!")

# Call the function with the path to your JSON file..

insert_data_from_json(r'E:\Bigdata_project\Datasets\system_metadata.json')  


### Kafka Consumer..

from kafka import KafkaConsumer
import json
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime

# Connect to Kafka...

consumer = KafkaConsumer(
    'user_interactions',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='interaction-group'
)

# Connect to Cassandra...

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('datalink')  

insert_query = SimpleStatement("""
    INSERT INTO activity_logs (user_id, timestamp, action)
    VALUES (%s, %s, %s)
""")

print("Listening to Kafka topic 'user_interactions'...")

for message in consumer:
    data = message.value
    try:
        user_id = data['user_id']
        timestamp = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
        action = data['action_type']
        session.execute(insert_query, (user_id, timestamp, action))
        print(f"Inserted interaction: {user_id} - {action}")
    except Exception as e:
        print("Error processing message:", e)


### Kafka Producer...

from kafka import KafkaProducer
import json
import time

# Setup Kafka producer...

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Load the user interaction data..

with open('E:/Bigdata_project/Datasets/5000000_user_interactions.json', 'r') as file:
    data = json.load(file)

print(f"Total interactions to send: {len(data)}")

# Send interactions to Kafka topic 'user_interactions'...

for i, interaction in enumerate(data):
    try:
        producer.send('user_interactions', value=interaction)
        
        # Optional: simulate real-time stream
        # time.sleep(0.005)
        
        # Log progress every 10,000 messages
        if i % 10000 == 0:
            print(f"Sent {i} interactions...")

    except Exception as e:
        print(f"Error sending interaction {i}: {e}")

# Finalize
producer.flush()
producer.close()

print("All messages sent successfully.")


### Kafka to Cassandra...

from confluent_kafka import Consumer
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import json
from uuid import uuid4
from datetime import datetime

# Kafka consumer config..

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'interaction-consumer-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(kafka_config)
consumer.subscribe(['user_interactions'])

# Cassandra config...

cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('datalink')

# Prepare insert query..

insert_query = session.prepare("""
    INSERT INTO user_interactions (user_id, timestamp, interaction_id, action, target_id)
    VALUES (?, ?, ?, ?, ?)
""")

print("Kafka → Cassandra consumer is now listening...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Kafka error: {msg.error()}")
            continue

        try:
            record = json.loads(msg.value().decode('utf-8'))

            # DEBUG - print incoming record...

            print("Received record:", record)

            # Validate required fields (note: changed 'action' to 'action_type')
            required_fields = ['user_id', 'timestamp', 'action_type']
            if not all(field in record for field in required_fields):
                print(f"Skipped malformed record: {record}")
                continue

            # Parse timestamp..

            try:
                ts = datetime.fromisoformat(record['timestamp'])
            except Exception:
                print(f"Invalid timestamp format: {record['timestamp']}")
                continue

            # Insert into Cassandra (note: changed 'action' to 'action_type')
            session.execute(insert_query, (
                record['user_id'],
                ts,
                uuid4(),
                record['action_type'],
                record.get('target_id', '')
            ))

            print(f"Inserted: {record['user_id']} | {record['action_type']}")

        except Exception as e:
            print(f"Insert failed: {e}")

except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()
    cluster.shutdown()
    print("Kafka consumer closed and Cassandra connection shut down.")


### time based analytics...
from cassandra.cluster import Cluster
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import pandas as pd

# Connect to Cassandra...

cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('datalink')

print("📆 Fetching user interactions for time-based analysis...")

# Fetch timestamp and action fields...

rows = session.execute("SELECT timestamp, action FROM user_interactions")

# Count interactions per day and action...

daily_counts = defaultdict(int)
daily_actions = defaultdict(lambda: Counter())

for row in rows:
    if row.timestamp:
        date_str = row.timestamp.date().isoformat()
        daily_counts[date_str] += 1
        daily_actions[date_str][row.action] += 1

# Convert to DataFrames...

date_series = pd.Series(daily_counts).sort_index()
action_df = pd.DataFrame(daily_actions).T.fillna(0).astype(int).sort_index()

# Plot: Total Interactions Per Day...

plt.figure(figsize=(10, 5))
date_series.plot(kind='line', marker='o', color='blue')
plt.title("Total Interactions Per Day")
plt.xlabel("Date")
plt.ylabel("Interaction Count")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig("interactions_per_day.png")
print("Saved: interactions_per_day.png")

# Plot: Action Type Breakdown Per Day (Stacked Bar)..

action_df.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='Set2')
plt.title("Action Type Breakdown Per Day")
plt.xlabel("Date")
plt.ylabel("Interaction Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("interaction_types_per_day.png")
print("Saved: interaction_types_per_day.png")

# Clean up
cluster.shutdown()
print("Cassandra connection closed.")


### user interaction analytics...

from cassandra.cluster import Cluster
from collections import defaultdict

# Cassandra connection setup..

cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('datalink')

print("Fetching user interactions from Cassandra...")

# Query to get all user_id (partition key)..

rows = session.execute("SELECT user_id FROM user_interactions")

# Count interactions per user_id..

counter = defaultdict(int)
for row in rows:
    counter[row.user_id] += 1

# Sort and display top 10 users..

top_users = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:20]

print("\n Top 10 Most Active Users:")
for rank, (user_id, count) in enumerate(top_users, start=1):
    print(f"{rank}. {user_id}: {count} interactions")

# Clean up...

cluster.shutdown()
print("Cassandra connection closed.")

### Main Function....

from fastapi import FastAPI, Request
from kafka_producer import publish_event
from db.mongo import insert_user_profile
from db.cassandra import insert_interaction
from db.redis import cache_feed

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Backend API is running"}

@app.post("/profile")
async def update_profile(payload: dict):
    insert_user_profile(payload)          # MongoDB
    await publish_event("profile_update", payload)  # Kafka
    return {"status": "profile updated"}

@app.post("/interaction")
async def record_interaction(payload: dict):
    insert_interaction(payload)           # Cassandra
    await publish_event("interaction", payload)  # Kafka
    return {"status": "interaction recorded"}

@app.post("/cache_feed")
def cache_user_feed(payload: dict):
    user_id = payload["user_id"]
    posts = payload["posts"]
    cache_feed(user_id, posts)            # Redis
    return {"status": "feed cached"}