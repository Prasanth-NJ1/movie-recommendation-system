# # test.py
# from pymongo import MongoClient

# # MongoDB connection setup
# client = MongoClient("mongodb+srv://prasanthnj72:Prasanth%4072@moviecluster.qd8li.mongodb.net/?retryWrites=true&w=majority&appName=MovieCluster")
# db = client["movies_database"]  # Ensure this matches your DB name
# collection = db["imdb_movies"]  # Ensure this matches your collection name

# # sample_movie = collection.find_one({}, {"title": 1, "_id": 0})
# # print(f"📌 Sample Movie from DB: {sample_movie}")

# # titles = collection.distinct("title")
# # print(f"🎬 Movies in DB: {titles[:10]}")  # Show first 10 movies

# # print(collection.find_one())  # Check if data is stored correctly

# # from db_config import get_movie_collection


# movie = collection.find_one({"title": "Pusher"})
# print(movie)


# # titles = collection.distinct("title")
# # print("Available titles in DB:", titles)
import sys
import os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_config import get_scraped_movies_collection

def check_user_movies(username):
    db = get_scraped_movies_collection()
    user_movies = list(db.find({"username": username}))

    if not user_movies:
        print(f"⚠️ No movie data found for user '{username}'.")
        all_users = list(db.distinct("username"))  # Get all usernames
        print("👥 Users in database:", all_users)
    else:
        print(f"✅ {len(user_movies)} movies found for '{username}':")
        for movie in user_movies[:5]:  # Print first 5 movies
            print(movie)

if __name__ == "__main__":
    check_user_movies("udit_k")
