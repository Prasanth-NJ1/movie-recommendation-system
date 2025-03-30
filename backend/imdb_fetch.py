import requests
import csv
from pymongo import MongoClient
import time
import pandas as pd
import os
from dotenv import load_dotenv

def configure():
    load_dotenv()

client = MongoClient(os.getenv('DB_STRING'))
db = client["movies_database"]
collection = db["imdb_movies"]

OMDB_API_KEY = os.getenv('OMDB_API')  # Replace with your API key
OMDB_URL = "http://www.omdbapi.com"

df = pd.read_csv("tmdb_movies.csv")  
movies = df["Title"].tolist()  

def fetch_movie_details(title):
    params = {"t": title, "apikey": OMDB_API_KEY}
    response = requests.get(OMDB_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return {
                "title": data.get("Title"),
                "year": int(data.get("Year", "0").replace("–", "-").split("-")[0]),  # Extract only start year
                "genre": data.get("Genre", "").split(", ") if data.get("Genre") else [],  
                "rating": float(data.get("imdbRating", 0)) if data.get("imdbRating") != "N/A" else None
            }
    return None


count = 0
for movie in movies:
    # Check if movie already exists
    if collection.count_documents({"title": movie}) == 0:
        movie_data = fetch_movie_details(movie)
        if movie_data:
            collection.insert_one(movie_data)
            count += 1
            print(f"Inserted: {movie_data['title']} ({movie_data['year']}) - {movie_data['genre']} - {movie_data['rating']}")
        else:
            print(f"Skipped: {movie}")
        
        time.sleep(1)  # Rate-limiting to prevent API blocks

    if count >= 8000:
        break

print(f"Done! {count} movies stored in MongoDB.")