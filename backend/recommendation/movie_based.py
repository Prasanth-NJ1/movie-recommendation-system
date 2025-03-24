import sys
import os

# Add backend folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_config import get_db  # Now it should work


def get_movie_recommendations(movie_title, page=1, limit=10):
    db = get_db()
    collection = db["imdb_movies"]
    
    # Fetch the movie details
    movie = collection.find_one({"title": {"$regex": f"^{movie_title.strip()}$", "$options": "i"}})

    if not movie:
        print(f"❌ Debug: Movie '{movie_title}' not found in database.")
        return {"error": "Your Movie is not found in our database."}

    # Extract genres (Fix the key name to match the DB)
    genres = movie.get("genre", [])  # Use "genre", NOT "genres"
    
    if not genres:
        print(f"❌ Debug: No genres found for movie '{movie_title}'")
        return {"error": "No genres found for this movie."}

    print(f"✅ Debug: Genres for '{movie_title}': {genres}")

    # Find movies with matching genres, exclude the input movie, and sort by IMDb rating
    recommendations = collection.find(
        {"genre": {"$in": genres}, "title": {"$ne": movie_title}},
        {"_id": 0, "title": 1, "year": 1, "genre": 1, "rating": 1}
    ).sort("rating", -1).skip((page - 1) * limit).limit(limit)

    recommended_movies = list(recommendations)
    
    if not recommended_movies:
        print(f"❌ Debug: No recommendations found for genres {genres}")
        return {"error": "No recommendations found."}

    print(f"✅ Debug: Found {len(recommended_movies)} recommendations.")

    formatted_results = [
        f"Title: {movie['title']}\nYear: {movie['year']}\nGenre: {', '.join(movie['genre'])}\niMDb rating: {movie['rating']}"
        for movie in recommended_movies
    ]

    return {
        "current_page": page,
        "next_page": page + 1,
        "previous_page": page - 1 if page > 1 else None,
        "results": formatted_results
    }

# Example usage
if __name__ == "__main__":
    movie_title = input("Enter a movie name: ")
    page = 1  # Default to page 1
    db = get_db()
    print(f"📡 Connected to Database: {db.name}")

    while True:
        response = get_movie_recommendations(movie_title, page)
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
