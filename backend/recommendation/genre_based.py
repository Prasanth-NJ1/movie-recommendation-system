import sys
import os

# Add backend folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_config import get_movie_collection  

def get_movies_by_genre(genre, limit=10, page=1):
    collection = get_movie_collection()  #  Get correct collection
    skip = (page - 1) * limit  # Pagination offset
    
    query = {"genre": genre, "rating": {"$gte": 7}}
    projection = {"_id": 0, "title": 1, "year": 1, "genre": 1, "rating": 1}

    movies = list(collection.find(query, projection).sort("rating", -1).skip(skip).limit(limit))  

    if not movies:
        return {"error": "No movies found for the given genre."}

    formatted_movies = [
        f"Title: {movie['title']}\nYear: {movie['year']}\nGenre: {', '.join(movie['genre'])}\niMDb rating: {movie['rating']}"
        for movie in movies
    ]

    return {
        "current_page": page,
        "next_page": page + 1 if len(movies) == limit else None,
        "previous_page": page - 1 if page > 1 else None,
        "results": formatted_movies
    }

# 🔹 Example usage
if __name__ == "__main__":
    genre = input("Enter genre: ").strip()
    page = 1  

    while True:
        response = get_movies_by_genre(genre, page=page)
        if "error" in response:
            print(response["error"])
            break

        for movie in response["results"]:
            print(movie + "\n")

        # Pagination control
        next_prev = input("Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ").strip().lower()
        if next_prev == 'n':
            page = response["next_page"]
        elif next_prev == 'p' and response["previous_page"]:
            page = response["previous_page"]
        else:
            break
