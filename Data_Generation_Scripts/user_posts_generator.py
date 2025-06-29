import random
import json
import uuid
from faker import Faker
from datetime import datetime
from tqdm import tqdm

fake = Faker()

with open("1000000_user_profiles.json") as f:
    user_profiles = json.load(f)
    user_ids = [user["user_id"] for user in user_profiles]

random.shuffle(user_ids)

very_active_users = user_ids[:50000]        
occasional_users = user_ids[50000:200000]   

post_types = ["text", "image"]

text_templates = [
    "Excited to start a new role in {}!",
    "Just completed a course on {}.",
    "Sharing thoughts about {} today.",
    "Looking back on my journey in {}.",
    "Just hit a milestone in {}!"
]

topics = ["AI", "Big Data", "Cloud", "DevOps", "ML", "System Design"]

image_urls = [
    f"https://datalink-post-media.s3.ap-south-1.amazonaws.com/post_media/post_{str(i).zfill(3)}.jpg"
    for i in range(1, 241)
]

posts = []
MAX_POSTS = 500000

print("Generating realistic posts for active users...")

for user_id in tqdm(very_active_users):
    for _ in range(random.randint(3, 7)):
        if len(posts) >= MAX_POSTS:
            break
        post_type = random.choices(post_types, weights=[75, 25])[0]
        topic = random.choice(topics)
        post = {
            "post_id": str(uuid.uuid4()),
            "user_id": user_id,
            "post_type": post_type,
            "content": random.choice(text_templates).format(topic),
            "image_url": random.choice(image_urls) if post_type == "image" else None,
            "timestamp": fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S"),
            "likes_count": random.randint(10, 1000),
            "shares_count": random.randint(0, 300)
        }
        posts.append(post)

for user_id in tqdm(occasional_users):
    for _ in range(random.randint(1, 2)):
        if len(posts) >= MAX_POSTS:
            break
        post_type = random.choices(post_types, weights=[80, 20])[0]
        topic = random.choice(topics)
        post = {
            "post_id": str(uuid.uuid4()),
            "user_id": user_id,
            "post_type": post_type,
            "content": random.choice(text_templates).format(topic),
            "image_url": random.choice(image_urls) if post_type == "image" else None,
            "timestamp": fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S"),
            "likes_count": random.randint(0, 500),
            "shares_count": random.randint(0, 150)
        }
        posts.append(post)

with open("500000_user_posts.json", "w") as f:
    json.dump(posts, f, indent=4)

print(f"Generated {len(posts)} realistic posts with behavioral pattern...")
