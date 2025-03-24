
import requests
import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  
from db_config import get_scraped_movies_collection, get_movie_collection  

# API Key
TMDB_API_KEY = "a9cca56ed16bad2ba4d7ff57c2f9c89e"


GENRE_MAP = {}

def get_tmdb_genre_map():
    """Fetch and store TMDb genre ID to name mapping."""
    global GENRE_MAP
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
    response = requests.get(url).json()

    if "genres" in response:
        GENRE_MAP = {genre["name"]: genre["id"] for genre in response["genres"]}

def get_most_watched_genre(username):
    """Find the most-watched genre from the stored movie database."""
    genre_count = {}
    movie_collection = get_scraped_movies_collection()
    
    user_movies = list(movie_collection.find({"username": username}))

    if not user_movies:
        print(f"No movie data found for user '{username}'.")
        return None

    for movie in user_movies:
        genres = movie.get("genres", [])

        print(f"Movie: {movie['title']} | Genres: {genres}")  # Debugging line

        for genre in genres:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    most_watched = max(genre_count, key=genre_count.get, default=None)
    
    print(f"Genre count: {genre_count}")  # Debugging line
    return most_watched

def recommend_movies_from_db(genre, limit=10):
    """Recommend movies from 'imdb_movies' based on the most-watched genre."""
    movie_collection = get_movie_collection()

    # Find movies where the genre matches and IMDb rating is available
    matching_movies = list(movie_collection.find(
        {"genre": genre, "rating": {"$gte": 7}},  # Ensure IMDb rating is 7+
        {"_id": 0, "title": 1, "year": 1, "rating": 1}  # Fetch only required fields
    ).sort("rating", -1).limit(limit))

    if not matching_movies:
        print(f"No movies found in the database for genre '{genre}'.")
        return []

    # Format output like genre-based recommendations
    formatted_movies = [
        f"Title: {movie['title']}\nYear: {movie['year']}\niMDb rating: {movie['rating']}"
        for movie in matching_movies
    ]

    return formatted_movies

def recommend_movies_from_tmdb(genre_name, limit=10):
    """Fetch movies from TMDb if not enough are found in the database."""
    if not GENRE_MAP:
        get_tmdb_genre_map()  # Fetch genre mappings

    genre_id = GENRE_MAP.get(genre_name)

    if not genre_id:
        print(f"No TMDb genre ID found for '{genre_name}'.")
        return []

    print(f"🔍 Searching for movies in the {genre_name} genre (ID: {genre_id})...")

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching recommendations from TMDb.")
        return []

    movies = response.json().get("results", [])[:limit]  # Get top 'limit' movies

    if not movies:
        print("No recommendations found.")
        return []

    formatted_movies = [
        f"Title: {movie['title']}\nYear: {movie.get('release_date', 'N/A')[:4]}\niMDb rating: {movie.get('vote_average', 'N/A')}"
        for movie in movies
    ]

    return formatted_movies

def main():
    username = input("Enter your Letterboxd username: ").strip()
    
    if not username:
        print("Username is required.")
        return
    
    genre = get_most_watched_genre(username)

    if not genre:
        print(f"No genre data found for user '{username}'.")
        return

    print(f"🔍 Most watched genre for {username}: {genre}")

    # First, try to recommend from the database
    recommendations = recommend_movies_from_db(genre)

    # If not enough movies are found, fetch from TMDb
    if not recommendations:
        recommendations = recommend_movies_from_tmdb(genre)

    if recommendations:
        print("\n **Recommended Movies:**\n")
        for movie in recommendations:
            print(movie + "\n")
    else:
        print("No movie recommendations found.")

if __name__ == "__main__":
    main()
