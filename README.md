# Movie Recommendation System  
A Flask-based movie recommendation system that suggests movies based on:
1. Letterboxd watch history
2. User-selected genres
3. User-entered movies

It fetches movie data from Letterboxd, OMDb, and TMDb and stores it in MongoDB for fast recommendations.

## Features
Letterboxd-Based Recommendations – Fetches user watch history and suggests movies based on most-watched genres.
Genre-Based Recommendations – Users enter a genre (e.g., "Drama"), and the system recommends highly-rated movies.
Movie-Based Recommendations – Users enter a movie title, and similar movies are suggested.

## Setup Instructions  
1. Clone the repository `https://github.com/Prasanth-NJ1/movie-recommendation-system.git`
2. Install dependencies: `pip install -r requirements.txt`  
3. Start the Flask Server `python app.py`  

## Example Usage
Run the following commands in your command prompt after the Flask started running 

`curl http://127.0.0.1:8090/recommend/letterboxd?username=your_username_here`

`curl http://127.0.0.1:8090/recommend/genre?genre=Action`

`curl http://127.0.0.1:8090/recommend/movie?title=Pusher`

