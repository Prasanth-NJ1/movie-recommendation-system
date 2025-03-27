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
        GENRE_MAP = {genre["id"]: genre["name"] for genre in response["genres"]}

def fetch_similar_movies_from_tmdb(movie_title, page=1, limit=10):
    """Fetch similar movies from TMDb, including genres and proper pagination."""
    if not GENRE_MAP:  # Ensure genre map is loaded
        get_tmdb_genre_map()

    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(movie_title)}&page={page}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Failed to fetch data from TMDb", "results": []}

    movies = response.json()
    total_pages = movies.get("total_pages", 1)  # Total TMDb pages available
    total_results = movies.get("total_results", 0)

    filtered_movies = [
        movie for movie in movies.get("results", [])
        if movie["title"].strip().lower() != movie_title.strip().lower()
    ][:limit]  # Ensure we return only `limit` number of movies

    return {
        "current_page": page,
        "total_pages": total_pages,
        "next_page": page + 1 if page < total_pages else None,
        "previous_page": page - 1 if page > 1 else None,
        "total_results": total_results,
        "results": [
            {
                "title": movie["title"],
                "year": movie.get("release_date", "N/A")[:4],
                "genre": [GENRE_MAP.get(genre_id, "Unknown") for genre_id in movie.get("genre_ids", [])],
                "rating": movie.get("vote_average", "N/A")
            }
            for movie in filtered_movies
        ]
    }

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
