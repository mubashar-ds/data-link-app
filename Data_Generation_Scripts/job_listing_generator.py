from faker import Faker
import random
import json

fake = Faker()

job_titles = [
    "Software Engineer", "Data Scientist", "Machine Learning Engineer",
    "DevOps Engineer", "Cloud Architect", "Backend Developer", "Frontend Developer"
]

companies = ["Google", "Amazon", "Microsoft", "Meta", "Netflix", "IBM", "Apple"]

locations = ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Toronto, Canada"]

job_types = ["Full-time", "Part-time", "Contract"]

remote_options = ["Remote", "Hybrid", "On-site"]

skills = ["Python", "Java", "C++", "SQL", "Docker", "Kubernetes", "TensorFlow", "PyTorch", "AWS"]

jobs = []

for _ in range(10001):
    title = f"{random.choice(job_titles)} - {random.choice(['AI', 'Cloud', 'Backend', 'ML', 'DevOps'])}"
    company = random.choice(companies)
    job = {
        "title": title,
        "company": company,
        "location": random.choice(locations),
        "posted": f"{random.randint(1, 7)} days ago",
        "applicants": f"{random.randint(10, 200)} applicants",
        "description": fake.paragraph(),
        "requirements": random.sample(skills, random.randint(3, 6)),
        "salary": f"${random.randint(90000, 160000)} - ${random.randint(170000, 250000)}",
        "job_type": random.choice(job_types),
        "remote": random.choice(remote_options),
        "company_info": {
            "size": random.choice(["51-200", "201-500", "5000+", "10,001+ employees"]),
            "industry": "Technology",
            "founded": random.randint(1980, 2020),
            "description": fake.text(max_nb_chars=150)
        }
    }
    jobs.append(job)

with open("10000_job_listings.json", "w") as f:
    json.dump(jobs, f, indent=4)

print("Generated 10000 job listings...")