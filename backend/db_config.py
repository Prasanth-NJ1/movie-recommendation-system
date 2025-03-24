from pymongo import MongoClient

def get_db():
    CONNECTION_STRING = "mongodb+srv://prasanthnj72:Prasanth%4072@moviecluster.qd8li.mongodb.net/?retryWrites=true&w=majority&appName=MovieCluster"
    client = MongoClient(CONNECTION_STRING)
    return client["movies_database"]  

# Function to get the movie collection
def get_movie_collection():
    db = get_db()
    return db["imdb_movies"]  

# Function to get the user collection (for caching Letterboxd users)
def get_user_collection():
    db = get_db()
    return db["users"]  

#Function to get the movies collection (for Letterboxd scraper)
def get_scraped_movies_collection():
    db = get_db()
    return db["movies"]  