import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_config import get_scraped_movies_collection, get_movie_collection  

# TMDb API Key
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
    """Find the most-watched genre from the user's Letterboxd movie history."""
    genre_count = {}
    movie_collection = get_scraped_movies_collection()
    
    user_movies = list(movie_collection.find({"username": username}))

    if not user_movies:
        return None

    for movie in user_movies:
        genres = movie.get("genres", [])
        for genre in genres:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    return max(genre_count, key=genre_count.get, default=None)


def recommend_movies_from_db(genre, page=1, limit=10):
    """Recommend movies from 'imdb_movies' based on the most-watched genre."""
    movie_collection = get_movie_collection()
    skip = (page - 1) * limit  # Pagination offset

    matching_movies = list(movie_collection.find(
        {"genre": genre, "rating": {"$gte": 7}},
        {"_id": 0, "title": 1, "year": 1, "rating": 1}
    ).sort("rating", -1).skip(skip).limit(limit))

    if not matching_movies:
        return []

    return matching_movies


def recommend_movies_from_tmdb(genre_name, page=1, limit=10):
    """Fetch movies from TMDb if not enough are found in the database."""
    if not GENRE_MAP:
        get_tmdb_genre_map()

    genre_id = GENRE_MAP.get(genre_name)

    if not genre_id:
        return []

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&page={page}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    movies = response.json().get("results", [])[:limit]

    return [
        {
            "title": movie["title"],
            "year": movie.get("release_date", "N/A")[:4],
            "rating": movie.get("vote_average", "N/A")
        }
        for movie in movies
    ]


def get_letterboxd_recommendations(username, page=1, limit=10):
    """Get movie recommendations based on a user's most-watched genre."""
    if not username:
        return {"error": "Username is required."}

    genre = get_most_watched_genre(username)
    if not genre:
        return {"error": f"No genre data found for user '{username}'."}

    recommendations = recommend_movies_from_db(genre, page, limit)

    # If not enough recommendations, fetch from TMDb
    if not recommendations:
        recommendations = recommend_movies_from_tmdb(genre, page, limit)

    return {
        "current_page": page,
        "next_page": page + 1 if len(recommendations) == limit else None,
        "previous_page": page - 1 if page > 1 else None,
        "results": recommendations
    }


# 🔹 Example usage
if __name__ == "__main__":
    username = input("Enter your Letterboxd username: ").strip()
    page = 1

    while True:
        response = get_letterboxd_recommendations(username, page)

        if "error" in response:
            print(response["error"])
            break

        print("\n **Recommended Movies:**\n")
        for movie in response["results"]:
            print(f"{movie['title']} ({movie['year']}) | IMDb: {movie['rating']}")

        # Pagination control
        next_prev = input("Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ").strip().lower()
        if next_prev == 'n' and response["next_page"]:
            page = response["next_page"]
        elif next_prev == 'p' and response["previous_page"]:
            page = response["previous_page"]
        else:
            break
