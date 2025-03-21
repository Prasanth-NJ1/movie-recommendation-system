from pymongo import MongoClient

def get_db():
    CONNECTION_STRING ="mongodb+srv://prasanthnj72:Prasanth%4072@moviecluster.qd8li.mongodb.net/?retryWrites=true&w=majority&appName=MovieCluster"

    client = MongoClient(CONNECTION_STRING)  # Change this if using a cloud database
    return client["movie_recommendation"]

    # prasanthnj72:Prasanth%4072
