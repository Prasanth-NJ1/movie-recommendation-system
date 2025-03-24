import requests
import csv
import time

TMDB_API_KEY = "4920a5b79e57b1ac32a0a8cde05c520e"  # Replace with your TMDb API key
TMDB_URL = "https://api.themoviedb.org/3/movie/top_rated"

MOVIE_LIMIT = 8000  # Target count
CSV_FILENAME = "tmdb_movies.csv"

# TMDb Endpoints
ENDPOINTS = [
    "https://api.themoviedb.org/3/movie/top_rated",
    "https://api.themoviedb.org/3/movie/popular",
    "https://api.themoviedb.org/3/movie/now_playing",
    "https://api.themoviedb.org/3/discover/movie"
]

def fetch_movies():
    movies = set()  # Use set to avoid duplicates

    for endpoint in ENDPOINTS:
        for page in range(1, 500):  # Adjust pages if needed
            params = {
                "api_key": TMDB_API_KEY,
                "page": page,
                "vote_average.gte": 7.0  # Only movies with IMDb rating >= 7
            }
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for movie in data.get("results", []):
                    title = movie["title"]
                    year = movie["release_date"].split("-")[0]
                    movies.add((title, year))  # Add as tuple to avoid duplicates
                
                print(f"Fetched {len(movies)} movies so far...")
                if len(movies) >= MOVIE_LIMIT:
                    return list(movies)  
            else:
                print(f"API Error: {response.status_code}")
            time.sleep(1)  # Avoid rate limiting
    
    return list(movies)

# Save movies to CSV
def save_to_csv(movies):
    with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Year"])  # CSV Header
        writer.writerows(movies)
    
    print(f"CSV Created: {len(movies)} movies saved in '{CSV_FILENAME}'")

movies_data = fetch_movies()
save_to_csv(movies_data)
