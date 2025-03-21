from flask import Flask, request, jsonify
from db_config import get_db
from recommendation import get_genre_based_recommendations, get_movie_based_recommendations

app = Flask(__name__)
db = get_db()

@app.route("/recommend", methods=["GET"])
def recommend():
    """API for movie recommendations. Supports two modes:
       - /recommend?mode=genre&username=prasanth
       - /recommend?mode=movie&title=Inception
    """
    mode = request.args.get("mode")
    
    if mode == "genre":
        username = request.args.get("username")
        if not username:
            return jsonify({"error": "Username is required for genre-based recommendations"}), 400
        recommendations = get_genre_based_recommendations(username)
    
    elif mode == "movie":
        movie_title = request.args.get("title")
        if not movie_title:
            return jsonify({"error": "Movie title is required for movie-based recommendations"}), 400
        recommendations = get_movie_based_recommendations(movie_title)

    else:
        return jsonify({"error": "Invalid mode. Use 'genre' or 'movie'."}), 400
    
    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True)
