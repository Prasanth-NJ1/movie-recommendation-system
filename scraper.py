import requests
import xml.etree.ElementTree as ET
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_config import get_scraped_movies_collection
from omdb_tmdb import get_movie_genres  # Function to fetch genres

BASE_URL = "https://letterboxd.com"

def fetch_letterboxd_rss(username):
    """Fetch movies from Letterboxd RSS feed."""
    rss_url = f"{BASE_URL}/{username}/rss/"
    response = requests.get(rss_url)

    if response.status_code != 200:
        print(f"Error {response.status_code}: Unable to fetch RSS feed.")
        return []

    root = ET.fromstring(response.content)
    movies = []

    for item in root.findall(".//item"):
        title = item.find("title").text
        link = item.find("link").text

        # Exclude "Theatre" entries
        if "Theatre" in title:
            continue

        movies.append({"title": title, "url": link, "username": username})

    return movies

def store_movies_in_db(username, movies):
    """Store movies in MongoDB with genres."""
    collection = get_scraped_movies_collection()

    for movie in movies:
        genres = get_movie_genres(movie["title"])  # Fetch genres
        if not genres:
            continue  # Skip movies without genres

        movie_data = {
            "username": username,
            "title": movie["title"],
            "url": movie["url"],
            "genres": genres
        }

        collection.update_one(
            {"username": username, "title": movie["title"]},
            {"$set": movie_data},
            upsert=True
        )

        print(f"📌 Stored: {movie['title']} - Genres: {', '.join(genres)}")

def update_watched_movies(username):
    """Fetch movies via RSS, get genres, and update database."""
    movies = fetch_letterboxd_rss(username)
    if not movies:
        print("⚠️ No new movies found via RSS.")
        return []

    store_movies_in_db(username, movies)
    return movies

# 🔹 Usage Example
if __name__ == "__main__":
    username = input("Enter Letterboxd username: ").strip()
    update_watched_movies(username)
