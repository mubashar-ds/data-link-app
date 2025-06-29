from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, EmailStr
from pymongo import MongoClient
from typing import List, Optional
import time
from cassandra.query import dict_factory

app = FastAPI(title="LinkedIn Clone API")
MONGO_URI = "mongodb://localhost:27017/"

# MongoDB Setup... 

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["DB_01"]
mongo_profiles = mongo_db["user_profiles"]

# Data Model...

class UserProfile(BaseModel):
    user_id: str
    full_name: str
    email: EmailStr
    password: str
    location: str
    headline: str
    industry: str
    skills: List[str]
    experience: str
    profile_picture_url: Optional[HttpUrl] = None
    resume_url: Optional[HttpUrl] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    about: Optional[str] = None
    connections: Optional[int] = None
    profile_views: Optional[int] = None
    experience: Optional[List[dict]] = None
    education: Optional[List[dict]] = None
    skills: Optional[List[str]] = None


# Create Profile...

@app.post("/api/user_profiles/")
def create_user_profile(profile: UserProfile):
    if mongo_profiles.find_one({"user_id": profile.user_id}):
        raise HTTPException(status_code=400, detail="User already exists")

    mongo_profiles.insert_one(profile.dict())
    return {"message": "User profile saved successfully"}

# Get Profile by ID..

@app.get("/api/user_profiles/{user_id}")
def get_user_profile(user_id: str):
    user = mongo_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

# Update Profile...

@app.put("/api/user_profiles/{user_id}")
def update_user_profile(user_id: str, updated: UserProfileUpdate):
    result = mongo_profiles.update_one(
        {"user_id": user_id},
        {"$set": {k: v for k, v in updated.dict().items() if v is not None}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User profile updated successfully"}


# Signup/Login Models..

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ExperienceEntry(BaseModel):
    title: str
    company: str
    duration: str
    description: str

class EducationEntry(BaseModel):
    school: str
    degree: str
    duration: str

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    company: str
    location: str
    about: str
    experience: List[ExperienceEntry]
    education: List[EducationEntry]
    skills: List[str]

# Signup API...

@app.post("/api/auth/signup")
def signup_user(user: SignupRequest):
    if mongo_profiles.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    user_id = "U" + str(mongo_profiles.estimated_document_count() + 1).zfill(6)

    profile = {
        "user_id": user_id,
        "full_name": user.full_name,
        "email": user.email,
        "password": user.password,
        "role": user.role,
        "company": user.company,
        "location": user.location,
        "about": user.about,
        "experience": [e.dict() for e in user.experience],
        "education": [e.dict() for e in user.education],
        "skills": user.skills,
        "connections": 0,
        "profile_views": 0
    }

    mongo_profiles.insert_one(profile)
    return {"message": "Signup successful", "user_id": user_id}

# Login API...

@app.post("/api/auth/login")
def login_user(credentials: LoginRequest):
    user = mongo_profiles.find_one({"email": credentials.email})
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "user_id": user["user_id"],
        "name": user["full_name"],
        'role': user["role"],
        'location': user["location"],
        'company': user["company"],
        'about': user["about"],
        'experience': user["experience"],
        'education': user["education"],
        'skills': user["skills"],
        'connections': user["connections"],
        'profile_views': user["profile_views"],
        'profile_picture_url': user.get("profile_picture_url"),
        'resume_url': user.get("resume_url")
    }


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from uuid import uuid4
from cassandra.cluster import Cluster
from datetime import datetime
from uuid import uuid4, UUID
# Cassandra Setup
cluster = Cluster(['127.0.0.1'])  
session = cluster.connect('datalink')  

# Prepare the insert query to match the new schema..

insert_query = session.prepare("""
    INSERT INTO user_posts (
        post_id, user_id, post_type, content, image_url, timestamp, likes_count, shares_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""")

# Pydantic Post Schema (updated with the correct fields)...

class Post(BaseModel):
    user_id: str
    post_type: str
    content: str
    image_url: Optional[HttpUrl] = None
    timestamp: str  # format: "YYYY-MM-DD HH:MM:SS"

# Endpoint to create a post..

@app.post("/api/posts")
def create_post(post: Post):
    try:
        post_id = uuid4()  
        post_time = datetime.strptime(post.timestamp, "%Y-%m-%d %H:%M:%S")  

        # Execute insert query...
        session.execute(insert_query, (
            post_id,
            post.user_id,
            post.post_type,
            post.content,
            str(post.image_url) if post.image_url else None,
            post_time,
            0,  # Likes count (initially set to 0)
            0   # Shares count (initially set to 0)
        ))

        # Return response with the post ID...

        return {"message": "Post saved to Cassandra", "post_id": str(post_id)}

    except Exception as e:
        print("Exception:", e)
        raise HTTPException(status_code=500, detail=str(e))

class Interaction(BaseModel):
    user_id: str
    action_type: str         
    post_id: UUID
    content: str = None      
    timestamp: str

@app.post("/api/interactions")
def create_interaction(interaction: Interaction):
    interaction_id = f"INT{int(time.time() * 1000)}"

    stmt = session.prepare("""
        INSERT INTO user_interactions (
            interaction_id, user_id, action_type, post_id,
            content, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?)
    """)

    session.execute(stmt, (
        interaction_id,
        interaction.user_id,
        interaction.action_type,
        interaction.post_id,
        interaction.content,
        datetime.strptime(interaction.timestamp, "%Y-%m-%d %H:%M:%S")
    ))

    return {"message": "Interaction recorded", "interaction_id": interaction_id}


# Fetch Likes and Comments for a post...

@app.get("/api/posts/{post_id}/interactions")
def get_post_interactions(post_id: UUID):
    try:
        # Query to get likes and comments for specific post id..

        query = "SELECT * FROM user_interactions WHERE post_id = %s ALLOW FILTERING"
        rows = session.execute(query, (post_id,))
        
        likes = []
        comments = []

        # Separate likes and comments...

        for row in rows:
            if row["action_type"] == "Like":
                likes.append(row)
            elif row["action_type"] == "Comment":
                comments.append(row)

        return {
            "likes_count": len(likes),
            "comments": comments
        }
    
    except Exception as e:
        print("Error fetching interactions:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch interactions")

session.row_factory = dict_factory

@app.get("/api/posts/feed")
def get_user_feed():
    try:
        # Fetch latest 20 posts from Cassandra..

        rows = session.execute("SELECT * FROM user_posts LIMIT 20")

        # Convert rows to list of dictionaries...

        posts = []
        for post in rows:
            # Enrich the post with user data from MongoDB..
            user = mongo_db["user_profiles"].find_one({"user_id": post["user_id"]})
            if user:
                post_dict = post  
                post_dict["name"] = user.get("full_name", "Unknown")
                post_dict["role"] = user.get("role", "Unknown")
                post_dict["profile_pic"] = user.get("profile_picture_url", "")
                posts.append(post_dict)

        return {"posts": posts}

    except Exception as e:
        print(f"Feed fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch posts")