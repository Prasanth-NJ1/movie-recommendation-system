import requests
from bs4 import BeautifulSoup
from db_config import get_db  # Import from db_config.py

def get_letterboxd_movies(username):
    url = f"https://letterboxd.com/{username}/films/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch data.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    movies = [film.img["alt"] for film in soup.select(".poster-container") if film.img]

    return movies

def save_movies_to_db(username, movies):
    db = get_db()
    users_collection = db["users"]
    users_collection.update_one({"username": username}, {"$set": {"movies": movies}}, upsert=True)
    print(f"Saved {len(movies)} movies for {username}.")

if __name__ == "__main__":
    username = input("Enter Letterboxd username: ")
    movies = get_letterboxd_movies(username)

    if movies:
        print(f"Found {len(movies)} movies for {username}. Saving to database...")
        save_movies_to_db(username, movies)
    else:
        print("No movies found.")
