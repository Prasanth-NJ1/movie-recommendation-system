# Movie Recommendation System  
A movie recommendation system that fetches data from Letterboxd and stores it in MongoDB to suggest personalized movies.

## Setup Instructions  
1. Clone the repository  
2. Install dependencies: `pip install -r requirements.txt`  
3. Run the scraper: `python backend/scraper.py`  
4. Start API: `python backend/api.py`  
5. Test: `curl http://127.0.0.1:5000/recommend?username=<your_username>`
