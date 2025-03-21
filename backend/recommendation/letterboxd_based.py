import time
import sys
import os

# Add backend folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_config import get_scraped_movies_collection, get_movie_collection, get_user_collection
from scraper import get_movies_with_genres  # Import the Letterboxd scraper

#  Connect to the required MongoDB collections
movies_collection = get_scraped_movies_collection()  # Movies watched by Letterboxd user
imdb_collection = get_movie_collection()  # IMDb database for recommendations
users_collection = get_user_collection()  # Store user data & last_updated timestamps

def get_most_watched_genre(username):
    """
    Fetch the most watched genre of a user from stored Letterboxd movies.
    """
    user_entry = users_collection.find_one({"username": username})
    current_time = time.time()

    # If user exists and last update was within 24 hours, use stored movies
    if user_entry and (current_time - user_entry.get("last_updated", 0) < 86400):
        print(f"⏳ Using cached data for {username} (last updated < 24 hours ago).")
    else:
        print(f"⚠️ No recent data found for {username}. Running scraper...")
        get_movies_with_genres(username)  # Fetch movies from Letterboxd
        users_collection.update_one(
            {"username": username},
            {"$set": {"last_updated": current_time}},
            upsert=True
        )

    user_movies = list(movies_collection.find())

    if not user_movies:
        print(f"❌ No movies found for user {username}")
        return None

    genre_counts = {}
    for movie in user_movies:
        for genre in movie.get("genres", []):  # ✅ Ensure genres are stored as lists
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    if not genre_counts:
        print(f"❌ No genre data found for user {username}")
        return None

    most_watched_genre = max(genre_counts, key=genre_counts.get)
    print(f"🎭 Most Watched Genre for {username}: {most_watched_genre}")
    return most_watched_genre

def recommend_movies_by_genre(genre, page=1, limit=10):
    """
    Fetch recommended movies from the `imdb_movies` collection based on the given genre.
    """
    skip = (page - 1) * limit  # Pagination offset
    recommended_movies = list(imdb_collection.find(
        {"genre": genre, "rating": {"$gte": 7}},  # ✅ Query correctly formatted
        {"_id": 0, "title": 1, "year": 1, "genre": 1, "rating": 1}
    ).sort("rating", -1).skip(skip).limit(limit))

    if not recommended_movies:
        print(f"❌ No recommendations found for genre: {genre}")
        return {"error": f"No recommendations for {genre}."}

    formatted_movies = [
        f"Title: {movie['title']}\nYear: {movie['year']}\nGenre: {', '.join(movie['genre'])}\niMDb rating: {movie['rating']}"
        for movie in recommended_movies
    ]

    return {
        "current_page": page,
        "next_page": page + 1 if len(recommended_movies) == limit else None,
        "previous_page": page - 1 if page > 1 else None,
        "results": formatted_movies
    }

def letterboxd_recommendation(username):
    """
    Full pipeline: Fetch user movies, get most-watched genre, and recommend movies.
    """
    most_watched_genre = get_most_watched_genre(username)
    
    if not most_watched_genre:
        return {"error": "No valid genre found."}

    return recommend_movies_by_genre(most_watched_genre)

# 🔹 Example usage
if __name__ == "__main__":
    username = input("Enter Letterboxd username: ").strip()
    page = 1  

    while True:
        response = letterboxd_recommendation(username)

        if "error" in response:
            print(response["error"])
            break

        for movie in response["results"]:
            print(movie + "\n")

        # Pagination control
        next_prev = input("Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ").strip().lower()
        if next_prev == 'n' and response["next_page"]:
            page = response["next_page"]
        elif next_prev == 'p' and response["previous_page"]:
            page = response["previous_page"]
        else:
            break
