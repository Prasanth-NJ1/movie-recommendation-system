import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app


from backend.app import app

if __name__ == "__main__":
    app.run()
