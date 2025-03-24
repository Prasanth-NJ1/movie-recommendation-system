import requests
import xml.etree.ElementTree as ET
import time
import sys
import os
import re  

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_config import get_scraped_movies_collection
from omdb_tmdb import get_movie_genres  

BASE_URL = "https://letterboxd.com"

def clean_movie_title(title):
    title = re.sub(r"- ★+½?", "", title)  
    title = re.sub(r", \d{4}", "", title)  
    title = title.strip().replace("  ", " ")  
    title = re.sub(r"^\((\d+)\)", r"\1", title)  
    return title

def fetch_letterboxd_rss(username):
    """Fetch movies from Letterboxd RSS feed."""
    rss_url = f"{BASE_URL}/{username}/rss/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(rss_url, headers=headers)

    if response.status_code != 200:
        print(f"Error {response.status_code}: Unable to fetch RSS feed.")
        return []

    root = ET.fromstring(response.content)
    movies = []

    for item in root.findall(".//item"):
        raw_title = item.find("title").text
        link = item.find("link").text

        if "Theatre" in raw_title:
            continue

        cleaned_title = clean_movie_title(raw_title)

        movies.append({"title": cleaned_title, "url": link, "username": username})

    return movies

def store_movies_in_db(username, movies):
    """Store movies in MongoDB with genres."""
    collection = get_scraped_movies_collection()

    for movie in movies:
        genres = get_movie_genres(movie["title"]) or []  # Ensure it's a list
        if not genres:
            continue  

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

        print(f"Stored: {movie['title']} - Genres: {', '.join(genres)}")

def update_watched_movies(username):
    """Fetch movies via RSS, get genres, and update database."""
    movies = fetch_letterboxd_rss(username)
    if not movies:
        print("No new movies found via RSS.")
        return {"error": "No movies found for this user."}  # Return error dict

    store_movies_in_db(username, movies)
    return movies

if len(sys.argv) > 1:
    username = sys.argv[1].strip().replace('"', '')  # Remove extra quotes
else:
    print("No username provided.")
    sys.exit(1)  

update_watched_movies(username)
