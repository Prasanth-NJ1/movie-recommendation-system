import requests

TMDB_API_KEY = "a9cca56ed16bad2ba4d7ff57c2f9c89e"


GENRE_MAP = {}

def get_tmdb_genre_map():
    """Fetch and store TMDb genre ID to name mapping."""
    global GENRE_MAP
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url).json()
    if "genres" in response:
        GENRE_MAP = {genre["id"]: genre["name"] for genre in response["genres"]}

def fetch_from_tmdb(title, year=None):
    """Fetch movie genres from TMDb API with improved accuracy."""
    if not GENRE_MAP:
        get_tmdb_genre_map()  

    search_url = f"https://api.themoviedb.org/3/search/movie?query={title}&api_key={TMDB_API_KEY}"
    if year:
        search_url += f"&year={year}"  

    search_response = requests.get(search_url).json()

    if not search_response.get("results"):
        return []

    movie = search_response["results"][0]  # First result is assumed best match
    movie_id = movie["id"]

    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    details_response = requests.get(details_url).json()

    # Convert genre IDs to names using the pre-fetched map
    return [GENRE_MAP.get(genre["id"], "Unknown") for genre in details_response.get("genres", [])]

def get_movie_genres(title):
    """Fetch genres for a given movie title from TMDb."""
    return fetch_from_tmdb(title)  