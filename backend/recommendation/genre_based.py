import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_config import get_movie_collection  


TMDB_API_KEY = "a9cca56ed16bad2ba4d7ff57c2f9c89e"

GENRE_MAP = {}


def get_tmdb_genre_map():
    """Fetch and store TMDb genre ID to name mapping."""
    global GENRE_MAP
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
    response = requests.get(url).json()

    if "genres" in response:
        GENRE_MAP = {genre["name"]: genre["name"] for genre in response["genres"]}

def fetch_similar_movies_from_tmdb(movie_title, page=1, limit=10):
    """Fetch similar movies from TMDb using the movie ID."""
    
    # Step 1: Get movie ID from TMDb search
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(movie_title)}"
    search_response = requests.get(search_url)

    if search_response.status_code != 200 or not search_response.json().get("results"):
        return []  # Return empty list if search fails or no results

    # Get the first matching movie ID
    movie_id = search_response.json()["results"][0]["id"]

    # Step 2: Fetch similar movies using the movie ID
    similar_url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={TMDB_API_KEY}&page={page}"
    similar_response = requests.get(similar_url)

    if similar_response.status_code != 200:
        return []  # Return empty if fetching similar movies fails

    movies = similar_response.json().get("results", [])[:limit]

    return [
        {
            "title": movie["title"],
            "year": movie.get("release_date", "N/A")[:4],
            "genre": [],  # Genres are not fetched here, but we can enhance this if needed
            "rating": movie.get("vote_average", "N/A")
        }
        for movie in movies
        if movie["title"].strip().lower() != movie_title.strip().lower()  # Exclude the searched movie
    ]

def get_movies_by_genre(genre, limit=10, page=1):
    collection = get_movie_collection()  # Get the correct collection
    skip = (page - 1) * limit  # Pagination offset

    query = {"genre": {"$regex": f"^{genre}$", "$options": "i"}, "rating": {"$gte": 7}}
    projection = {"_id": 0, "title": 1, "year": 1, "genre": 1, "rating": 1}

    # Get total movie count for the genre
    total_movies = collection.count_documents(query)
    total_pages = (total_movies + limit - 1) // limit  # Round up division

    movies = list(collection.find(query, projection).sort("rating", -1).skip(skip).limit(limit))

    if not movies:
        return {
            "current_page": page,
            "total_pages": total_pages,
            "next_page": None,
            "previous_page": page - 1 if page > 1 else None,
            "results": [],
            "error": "No movies found for the given genre."
        }

    formatted_movies = [
        {
            "title": movie['title'],
            "year": movie['year'],
            "genre": movie['genre'],
            "rating": movie['rating']
        }
        for movie in movies
    ]

    return {
        "current_page": page,
        "total_pages": total_pages, 
        "next_page": page + 1 if page < total_pages else None,
        "previous_page": page - 1 if page > 1 else None,
        "results": formatted_movies
    }


# 🔹 Example usage
if __name__ == "__main__":
    genre = input("Enter genre: ").strip()
    page = 1  

    while True:
        response = get_movies_by_genre(genre, page=page)
        if "error" in response and not response["results"]:
            print(response["error"])
            break

        for movie in response["results"]:
            print(f"{movie['title']} ({movie['year']}) - {', '.join(movie['genre'])} | IMDb: {movie['rating']}")

        # Pagination control
        next_prev = input("Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ").strip().lower()
        if next_prev == 'n' and response["next_page"]:
            page = response["next_page"]
        elif next_prev == 'p' and response["previous_page"]:
            page = response["previous_page"]
        else:
            break
