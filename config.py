import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file if running locally
load_dotenv()

class Config:
    # Session cookie settings
    SESSION_COOKIE_SAMESITE = 'None'  # Allows cookies to be sent cross-origin
    SESSION_COOKIE_SECURE = True  # Use this if you're using HTTPS

    # Use an environment variable for the secret key or generate one if not set
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)  

    # Database configuration from the Heroku environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('JAWSDB_URL') or os.environ.get('DATABASE_URI')  # Ensure this key matches Heroku's

    # Disable SQLAlchemy event system to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI API Key from environment variables
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
