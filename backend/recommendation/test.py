''''Used for testing purposes only, no need to change anything here'''

import sys
import os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_config import get_scraped_movies_collection

def check_user_movies(username):
    db = get_scraped_movies_collection()
    user_movies = list(db.find({"username": username}))

    if not user_movies:
        print(f"No movie data found for user '{username}'.")
        all_users = list(db.distinct("username")) 
        print("👥 Users in database:", all_users)
    else:
        print(f"{len(user_movies)} movies found for '{username}':")
        for movie in user_movies[:5]: 
            print(movie)

if __name__ == "__main__":
    check_user_movies("")
