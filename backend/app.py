from flask import Flask, request, jsonify
from flask_cors import CORS
from .recommendation.genre_based import get_movies_by_genre,fetch_movies_from_tmdb
from .recommendation.movie_based import get_movie_recommendations,fetch_similar_movies_from_tmdb
from .recommendation.letterboxd_based import get_scraped_movies_collection, get_most_watched_genre, recommend_movies_from_db, recommend_movies_from_tmdb  
import requests
import subprocess
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


app = Flask(__name__)
CORS(app) # Allow frontend requests

# Function to paginate results
def paginate_list(items, page, per_page=5):
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], len(items)

@app.route('/recommend/genre', methods=['GET'])
def recommend_by_genre():
    genre = request.args.get('genre')
    page = int(request.args.get('page', 1))
    if not genre:
        return jsonify({"error": "Genre is required"}), 400
    recommendations = get_movies_by_genre(genre, page=page)

    # If no results from DB, fetch from TMDb
    if not recommendations["results"]:
        recommendations["results"] = fetch_movies_from_tmdb(genre, page=page)
        recommendations["source"] = "tmdb"

    return jsonify(recommendations)

@app.route('/recommend/movie', methods=['GET'])
def recommend_by_movie():
    title = request.args.get('title')
    page = int(request.args.get('page', 1))
    if not title:
        return jsonify({"error": "Movie title is required"}), 400
    recommendations = get_movie_recommendations(title, page=page)

    # If no results from DB, fetch from TMDb
    if not recommendations["results"]:
        recommendations["results"] = fetch_similar_movies_from_tmdb(title, page=page)
        recommendations["source"] = "tmdb"

    return jsonify(recommendations)


@app.route("/recommend/letterboxd", methods=["GET"])
def recommend_by_letterboxd():
    username = request.args.get("username")
    page=int(request.args.get("page",1))
    
    
    if not username:
        return jsonify({"error": "Username is required"}), 400

    movie_collection = get_scraped_movies_collection()
    user_movies = list(movie_collection.find({"username": username}))

    if not user_movies:  # If no data exists, run scraper
        print(f"Running scraper for new user: {username}")
        try:
            subprocess.run(["python", "scraper.py", username], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Scraper failed: {str(e)}"}), 500

        #Re-fetch after scraping
        user_movies = list(movie_collection.find({"username": username}))
        if not user_movies:
            return jsonify({"error": "No data found after scraping. Please check username."}), 404

    
    most_watched_genre = get_most_watched_genre(username)

    if not most_watched_genre:
        return jsonify({"error": "No genre data found"}), 404

    genre_response = get_movies_by_genre(most_watched_genre, page=page)

    return jsonify({
        "username": username,
        "genre": most_watched_genre,
        "recommendations": genre_response["results"],
        "current_page": genre_response["current_page"],
        "total_pages": genre_response["total_pages"],
        "previous_page": genre_response["previous_page"],
        "next_page": genre_response["next_page"]
    })
@app.route("/")
def home():
    return "Flask server is running!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8090)

