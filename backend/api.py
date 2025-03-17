from flask import Flask, request,  jsonify
from db_config import get_db

app=Flask(__name__)
db=get_db()
users_collection = db["users"]

@app.route("/recommend", methods=["GET"])


def recommend_movies():
    username = request.args.get("username")
    user = users_collection.find_one({"username" : username})

    if not user or "movies" not in user:
        return jsonify({"error":"User not found or No Movies listed"}), 404
    
    movies = user["movies"]
    return jsonify({"recommended_movies" : movies})

if __name__ == "__main__":
    app.run(debug=True)