import requests
from bs4 import BeautifulSoup
from db_config import get_db
import sys

db = get_db()
users_collection = db["users"]

def get_movies_with_genres(username):
    url = f"https://letterboxd.com/{username}/films/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {username}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    movies = []
    for movie_tag in soup.select('.poster'):
        title = movie_tag['alt']
        movie_url = "https://letterboxd.com" + movie_tag['href']
        
        # Scraping genre
        movie_page = requests.get(movie_url)
        movie_soup = BeautifulSoup(movie_page.text, "html.parser")
        genre_tags = movie_soup.select('.text-sluglist a')
        genres = [tag.text for tag in genre_tags]

        movies.append({"title": title, "genres": genres})

    return movies

def save_movies_to_db(username, movies):
    if not movies:
        print("No movies found to save.")
        return
    
    users_collection.update_one(
        {"username": username},
        {"$set": {"movies": movies}},
        upsert=True
    )
    print(f"Movies successfully saved for {username}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    movies = get_movies_with_genres(username)
    save_movies_to_db(username, movies)
