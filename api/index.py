import os
import sys

# Add the current directory to sys.path so we can import app
sys.path.append(os.path.dirname(__file__))

from app import app
