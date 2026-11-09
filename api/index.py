import os
import sys

# Add the project root directory to sys.path so app and its templates/static are properly located
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Vercel Serverless Function entry point
# Vercel automatically exposes the WSGI 'app' object
if __name__ == "__main__":
    app.run()
