from pymongo import MongoClient
from collections import Counter

# Connect to MongoDB
client = MongoClient("mongodb+srv://prasanthnj72:Prasanth%4072@moviecluster.qd8li.mongodb.net/?retryWrites=true&w=majority&appName=MovieCluster")
db = client.movie_recommendation
users_collection = db.users
movies_collection = db.movies

def get_most_watched_genre(user_id):
    """Find the most-watched genre for a given user."""
    user_movies = movies_collection.find({"user_id": user_id})  # Get user's watched movies
    
    genre_count = Counter()
    for movie in user_movies:
        genre_count.update(movie.get("genres", []))  # Count genre occurrences

    if genre_count:
        return genre_count.most_common(1)[0][0]  # Return the most common genre
    return None  # No genre found

def get_recommendations_by_genre(genre, exclude_user_id):
    """Get movie recommendations based on genre, excluding user's watched movies."""
    watched_movie_titles = {movie["title"] for movie in movies_collection.find({"user_id": exclude_user_id})}
    recommendations = movies_collection.find({"genres": genre, "title": {"$nin": list(watched_movie_titles)}})
    
    return [{"title": movie["title"], "genre": genre} for movie in recommendations]

def cleanup_user_data(user_id):
    """Remove old user data before inserting new recommendations."""
    users_collection.delete_one({"_id": user_id})
    movies_collection.delete_many({"user_id": user_id})

def store_user_recommendations(user_id, recommended_movies):
    """Store recommended movies for a user."""
    cleanup_user_data(user_id)  # Clean old data
    if recommended_movies:
        for movie in recommended_movies:
            movie["user_id"] = user_id  # Attach user_id to each movie
        movies_collection.insert_many(recommended_movies)  # Insert recommendations

def letterboxd_recommendation(user_id):
    """Main function to recommend movies based on the most-watched genre."""
    most_watched_genre = get_most_watched_genre(user_id)
    
    if not most_watched_genre:
        print(f"No genre data found for user {user_id}")
        return
    
    recommendations = get_recommendations_by_genre(most_watched_genre, user_id)
    
    if recommendations:
        print(f"Recommended movies for user {user_id}: {recommendations}")
        store_user_recommendations(user_id, recommendations)
    else:
        print(f"No new recommendations available for user {user_id}")

# Example usage
user_id = "udit_k"  # Replace with actual user ID
user_movies = list(movies_collection.find({"user_id": "udit_k"}))
print(user_movies)  # Should print the list of movies

letterboxd_recommendation(user_id)
