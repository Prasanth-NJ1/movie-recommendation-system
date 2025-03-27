import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_config import get_db


TMDB_API_KEY = "a9cca56ed16bad2ba4d7ff57c2f9c89e"

def fetch_similar_movies_from_tmdb(movie_title, page=1, limit=10):
    """Fetch similar movies from TMDb using the movie ID with pagination."""
    
    # Step 1: Get movie ID from TMDb search
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(movie_title)}"
    search_response = requests.get(search_url)

    if search_response.status_code != 200 or not search_response.json().get("results"):
        return {"error": "Movie not found on TMDb."}  

    # Get the first matching movie ID
    movie_id = search_response.json()["results"][0]["id"]

    # Step 2: Fetch similar movies using the movie ID
    similar_url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={TMDB_API_KEY}&page={page}"
    similar_response = requests.get(similar_url)

    if similar_response.status_code != 200:
        return {"error": "Failed to fetch similar movies from TMDb."}  

    # Extract data
    similar_data = similar_response.json()
    movies = similar_data.get("results", [])[:limit]  # Limit results
    total_pages = similar_data.get("total_pages", 1)   # Total pages from API

    formatted_movies = [
        {
            "title": movie["title"],
            "year": movie.get("release_date", "N/A")[:4],
            "genre": [],  # Fetch genres separately if needed
            "rating": movie.get("vote_average", "N/A")
        }
        for movie in formatted_movies
        if movie["title"].strip().lower() != movie_title.strip().lower()  # Exclude the searched movie
    ]

    return {
        "current_page": page,
        "total_pages": total_pages,
        "next_page": page + 1 if page < total_pages else None,
        "previous_page": page - 1 if page > 1 else None,
        "results": formatted_movies
    }
def get_movie_recommendations(movie_title, page=1, limit=10):
    db = get_db()
    collection = db["imdb_movies"]

    # Find the movie in the database
    movie = collection.find_one({"title": {"$regex": f"^{movie_title.strip()}$", "$options": "i"}})

    if not movie:
        return {
            "current_page": page,
            "next_page": None,
            "previous_page": page - 1 if page > 1 else None,
            "results": [],
            "error": "Movie not found in the database."
        }

    genres = movie.get("genre", [])

    if not genres:
        return {
            "current_page": page,
            "next_page": None,
            "previous_page": page - 1 if page > 1 else None,
            "results": [],
            "error": "No genres found for this movie."
        }

    # Find movies with at least 2 matching genres, excluding the input movie
    recommendations = list(collection.find(
        {"genre": {"$in": genres}, "title": {"$ne": movie_title}},
        {"_id": 0, "title": 1, "year": 1, "genre": 1, "rating": 1}
    ))

    # Sort movies: First by matching genre count, then by IMDb rating
    recommendations = sorted(
        recommendations,
        key=lambda x: (-len(set(x.get("genre", [])) & set(genres)), -float(x["rating"]) if x["rating"] else 0)
    )

    # Paginate results
    start_index = (page - 1) * limit
    end_index = start_index + limit
    recommended_movies = recommendations[start_index:end_index]

    return {
        "current_page": page,
        "next_page": page + 1 if end_index < len(recommendations) else None,
        "previous_page": page - 1 if page > 1 else None,
        "results": [
            {
                "title": movie["title"],
                "year": movie["year"],
                "genre": movie["genre"],
                "rating": movie["rating"]
            }
            for movie in recommended_movies
        ]
    }


# 🔹 Example usage
if __name__ == "__main__":
    movie_title = input("Enter a movie name: ")
    page = 1
    db = get_db()
    print(f"Connected to Database: {db.name}")

    while True:
        response = get_movie_recommendations(movie_title, page)
        
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
