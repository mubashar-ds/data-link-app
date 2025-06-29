import json
import random
from faker import Faker
from tqdm import tqdm
from datetime import datetime

fake = Faker()

with open("1000000_user_profiles.json") as f:
    user_profiles = json.load(f)
    user_ids = [user["user_id"] for user in user_profiles]

with open("500000_user_posts.json") as f:
    user_posts = json.load(f)
    post_ids = [post["post_id"] for post in user_posts]

actions = ["Like", "Comment", "Connect"]
weights = [0.6, 0.25, 0.15]

interactions = []

N = 2000000

print("Generating user interactions...")

for i in tqdm(range(N)):
    action_type = random.choices(actions, weights=weights)[0]
    user_id = random.choice(user_ids)
    interaction = {
        "interaction_id": f"INT{str(i + 1).zfill(8)}",
        "user_id": user_id,
        "action_type": action_type,
        "timestamp": fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S"),
        "post_id": None,
        "content": None
    }

    if action_type in ["Like", "Comment"]:
        interaction["post_id"] = random.choice(post_ids)
        if action_type == "Comment":
            interaction["content"] = fake.sentence(nb_words=random.randint(4, 10))
    elif action_type == "Connect":
        other_user = random.choice(user_ids)
        while other_user == user_id:
            other_user = random.choice(user_ids)
        interaction["post_id"] = f"{user_id} ↔ {other_user}"

    interactions.append(interaction)

with open("2000000_user_interactions.json", "w") as f:
    json.dump(interactions, f, indent=4)

print(f"Generated {len(interactions)} user interactions...")
