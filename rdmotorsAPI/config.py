"""Configuration module for the API"""
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
API_KEY = os.getenv("API_KEY")

# Validate required environment variables
required_env_vars = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "API_KEY": API_KEY
}

missing_vars = [key for key, value in required_env_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Flask configuration
DB_PASSWORD_ESCAPED = quote_plus(DB_PASSWORD)
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ESCAPED}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Base URL for generating photo URLs
BASE_URL = os.getenv("BASE_URL", "https://rdmotors.com.ua")

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(BASE_DIR, "static", "photos", "services")
PHOTOS_AUTO_DIR = os.getenv("PHOTOS_AUTO_DIR", "/var/www/rdmotorsAPI/static/photos/autousa")
os.makedirs(PHOTOS_AUTO_DIR, exist_ok=True)

# App configuration
class Config:
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB
    PREFERRED_URL_SCHEME = os.getenv("URL_SCHEME", "https")  # Default to https for production
    
    # Rate limiting configuration
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"