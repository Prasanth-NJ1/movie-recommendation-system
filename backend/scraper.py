import requests
from bs4 import BeautifulSoup
import time
from db_config import get_db

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE_URL = "https://letterboxd.com"

def get_movies_with_genres(username):
    url = f"{BASE_URL}/{username}/films/"
    session = requests.Session()

    print(f"\nFetching movies for: {username} ({url})")
    response = session.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: Unable to fetch data.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    
    movie_tags = soup.find_all("div", class_="film-poster")
    if not movie_tags:
        print("No movies found.")
        return []

    movies = []
    db=get_db()
    movies_collection=db["movies"]
    
    for movie_tag in movie_tags:
        title = movie_tag.img["alt"].strip() if movie_tag.img else "Unknown"
        movie_slug = movie_tag["data-film-slug"]
        movie_url = f"{BASE_URL}/film/{movie_slug}/"
        genre_url = movie_url + "genres/"

        genres = get_movie_genres(session, genre_url)
        
        movie_data = {
            "title": title,
            "url": movie_url,
            "genres": genres
        }

        movies_collection.update_one(
            {"title": title},  
            {"$set": movie_data},  
            upsert=True
        )
        movies.append(movie_data)

        print(f"Stored: {title} - Genres: {', '.join(genres) if genres else 'None'}")
        time.sleep(1)

    return movies

def get_movie_genres(session, genre_url):
    """ Fetches genres from the genre page of a movie """
    try:
        response = session.get(genre_url, headers=HEADERS)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        genre_links = soup.select('a[href*="/films/genre/"]')
        genres = [link.text.strip() for link in genre_links]

        return genres
    except Exception as e:
        print(f"Error fetching genres: {e}")
        return []

# 🔹 Take username as input
username = input("Enter Letterboxd username: ").strip()
movies = get_movies_with_genres(username)

if movies:
    print("\n=== Movies Fetched & Stored in MongoDB ===")
    for movie in movies:
        print(f"{movie['title']} | Genres: {', '.join(movie['genres']) if movie['genres'] else 'None'} | {movie['url']}")
else:
    print("No movies found.")
