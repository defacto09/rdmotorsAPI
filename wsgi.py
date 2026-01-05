"""WSGI entry point for production server"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from rdmotorsAPI.server import app

# This is the application object that WSGI servers will use
application = app

if __name__ == "__main__":
    app.run()
