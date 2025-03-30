from pymongo import MongoClient

def get_db():
    CONNECTION_STRING = "YOUR_CONNECTION_STRING"
    client = MongoClient(CONNECTION_STRING)
    return client["DB_NAME"]  

# Function to get the movie collection
def get_movie_collection():
    db = get_db()
    return db["COLLECTION_NAME"]  

# Function to get the user collection (for caching Letterboxd users)
def get_user_collection():
    db = get_db()
    return db["USERS_COLLECTION"]  

#Function to get the movies collection (for Letterboxd scraper)
def get_scraped_movies_collection():
    db = get_db()
    return db["USERS_MOVIE_COLLECTION_NAME"]  