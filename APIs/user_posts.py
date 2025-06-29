import json
import uuid
from cassandra.cluster import Cluster
from cassandra.query import PreparedStatement
from datetime import datetime

# Path to your JSON file...

json_path = r"E:\Bigdata_project\Datasets\500000_user_posts.json"

# 1 - Connect to Cassandra...

cluster = Cluster(['127.0.0.1'])  
session = cluster.connect('datalink')  

# 2 - Prepare the insert statement...

insert_query = session.prepare("""
    INSERT INTO user_posts (
        post_id, user_id, post_type, content,
        image_url, timestamp, likes_count, shares_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""")

# 3 - Load and upload data...

with open(json_path, 'r', encoding='utf-8') as f:
    posts = json.load(f)

for idx, post in enumerate(posts):
    try:
        session.execute(
            insert_query,
            (
                uuid.UUID(post["post_id"]),
                post["user_id"],
                post["post_type"],
                post.get("content", ""),
                post.get("image_url"),
                datetime.strptime(post["timestamp"], "%Y-%m-%d %H:%M:%S"),
                int(post.get("likes_count", 0)),
                int(post.get("shares_count", 0))
            )
        )
        if idx % 1000 == 0:
            print(f"Uploaded {idx} posts...")
    except Exception as e:
        print(f"Failed to insert post_id {post['post_id']}: {e}")