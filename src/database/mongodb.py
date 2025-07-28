from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_mongodb_client():
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise ValueError("MONGODB_URI environment variable not set")
    return MongoClient(mongodb_uri)

def get_user_credentials(user_id):
    client = get_mongodb_client()
    db = client["sql_assistant_db"]
    collection = db["user_credentials"]
    return collection.find_one({"user_id": user_id})

def save_user_credentials(user_id, credentials):
    client = get_mongodb_client()
    db = client["sql_assistant_db"]
    collection = db["user_credentials"]
    collection.update_one(
        {"user_id": user_id},
        {"$set": credentials},
        upsert=True
    )

def delete_user_credentials(user_id):
    client = get_mongodb_client()
    db = client["sql_assistant_db"]
    collection = db["user_credentials"]
    collection.delete_one({"user_id": user_id})
