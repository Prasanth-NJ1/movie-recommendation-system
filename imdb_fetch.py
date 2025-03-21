import requests
import csv
from pymongo import MongoClient
import time
import pandas as pd

# MongoDB Atlas Connection (Replace with your credentials)
client = MongoClient("mongodb+srv://prasanthnj72:Prasanth%4072@moviecluster.qd8li.mongodb.net/?retryWrites=true&w=majority&appName=MovieCluster")
db = client["movies_database"]
collection = db["imdb_movies"]

# OMDb API Key
OMDB_API_KEY = "9d170725"  # Replace with your API key
OMDB_URL = "http://www.omdbapi.com"

df = pd.read_csv("tmdb_movies.csv")  # Ensure this file contains at least 8000 movies
movies = df["Title"].tolist()  # Extract movie titles

# Function to fetch movie details
def fetch_movie_details(title):
    params = {"t": title, "apikey": OMDB_API_KEY}
    response = requests.get(OMDB_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return {
                "title": data.get("Title"),
                "year": int(data.get("Year", "0").replace("–", "-").split("-")[0]),  # Normalize dash  # Extract only start year
                "genre": data.get("Genre"),
                "rating": float(data.get("imdbRating", 0)) if data.get("imdbRating") != "N/A" else None
            }
    return None

# Insert movies into MongoDB
count = 0
for movie in movies:
    # Check if movie already exists
    if collection.count_documents({"title": movie}) == 0:
        movie_data = fetch_movie_details(movie)
        if movie_data:
            collection.insert_one(movie_data)
            count += 1
            print(f"Inserted: {movie_data['title']} ({movie_data['year']}) - {movie_data['rating']}")
        else:
            print(f"Skipped: {movie}")
        
        time.sleep(1)  # Rate-limiting to prevent API blocks

    if count >= 8000:
        break

print(f"🎬 Done! {count} movies stored in MongoDB.")

# 4920a5b79e57b1ac32a0a8cde05c520e tmdb
# 5555307a omdb
# 9d170725 omdb 1