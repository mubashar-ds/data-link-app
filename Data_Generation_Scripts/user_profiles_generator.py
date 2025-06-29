from faker import Faker
import random
import json
from tqdm import tqdm

fake = Faker()

skills_pool = [
    "Python", "Java", "C++", "AWS", "Azure", "Machine Learning",
    "System Design", "Docker", "Kubernetes", "SQL", "NoSQL"
]

degrees = ["B.S. Computer Science", "M.S. Computer Science", "B.S. Software Engineering", "M.S. Data Science"]

schools = ["Stanford University", "MIT", "ITU", "UC Berkeley", "University of Washington", "Harvard", "Oxford"]

companies = ["Google", "Microsoft", "Amazon", "Meta", "Netflix", "Salesforce", "IBM", "Oracle"]

locations = ["San Francisco, CA", "Seattle, WA", "New York, NY", "Toronto, Canada", "London, UK"]

def generate_experience():
    job = {
        "title": fake.job(),
        "company": random.choice(companies),
        "duration": f"{random.randint(2015, 2022)} - Present",
        "description": fake.sentence(nb_words=10)
    }
    past = {
        "title": fake.job(),
        "company": random.choice(companies),
        "duration": f"{random.randint(2010, 2015)} - {random.randint(2015, 2020)}",
        "description": fake.sentence(nb_words=10)
    }
    return [job, past]

def generate_education():
    edu1 = {
        "school": random.choice(schools),
        "degree": random.choice(degrees),
        "duration": "2016 - 2018"
    }
    edu2 = {
        "school": random.choice(schools),
        "degree": "High School Diploma",
        "duration": "2012 - 2016"
    }
    return [edu1, edu2]

def generate_profile(i):
    user_id = f"U{str(i+1).zfill(6)}"
    skills = random.sample(skills_pool, random.randint(4, 7))

    media_folder_id = f"U{str(random.randint(1, 130)).zfill(6)}"

    profile_picture_url = f"https://datalink-user-media.s3.ap-south-1.amazonaws.com/user_media/{media_folder_id}/profile.jpg"
    resume_url = f"https://datalink-user-media.s3.ap-south-1.amazonaws.com/user_media/{media_folder_id}/resume.pdf"

    return {
        "user_id": user_id,
        "email": fake.email(),
        "password": fake.password(length=10),
        "name": fake.name(),
        "role": fake.job(),
        "company": random.choice(companies),
        "location": random.choice(locations),
        "connections": random.randint(100, 1000),
        "profile_views": random.randint(100, 5000),
        "about": fake.paragraph(nb_sentences=2),
        "experience": generate_experience(),
        "education": generate_education(),
        "skills": skills,
        "endorsements": {skill: random.randint(10, 50) for skill in skills},
        "profile_picture_url": profile_picture_url,
        "resume_url": resume_url
    }

N = 1000000

profiles = []

print("Generating user profiles...")

for i in tqdm(range(N)):
    profiles.append(generate_profile(i))

with open("1000000_user_profiles.json", "w") as f:
    json.dump(profiles, f, indent=4)

print("Generated 1000000 detailed user_profiles...")
