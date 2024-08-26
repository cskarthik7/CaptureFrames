from flask_pymongo import PyMongo
from flask import Flask

def init_db(app: Flask, mongo_db_uri: str):
    """Initialize the database connection."""
    app.config["MONGO_URI"] = mongo_db_uri  # Update with your MongoDB URI
    mongo = PyMongo(app)
    return mongo