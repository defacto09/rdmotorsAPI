"""Configuration module for the API"""
import os
from typing import List
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()


def _str_to_bool(value: str, default: bool = False) -> bool:
    """Convert environment string value to boolean."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_cors_origins(value: str) -> List[str]:
    """Parse and normalize CORS origins from env string."""
    origins = [origin.strip() for origin in (value or "").split(",") if origin.strip()]
    if not origins:
        return ["http://localhost:3000"]
    return [origin for origin in origins if origin != "*"] or ["http://localhost:3000"]

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
    "DB_NAME": DB_NAME
}

missing_vars = [key for key, value in required_env_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Flask configuration
DB_PASSWORD_ESCAPED = quote_plus(DB_PASSWORD)
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ESCAPED}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# CORS configuration
CORS_ORIGINS = _parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:3000"))

# Base URL for generating photo URLs
BASE_URL = os.getenv("BASE_URL", "https://rdmotors.com.ua")

# Firebase / Session auth configuration
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY")
FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "__session")
CSRF_COOKIE_NAME = os.getenv("CSRF_COOKIE_NAME", "csrfToken")
SESSION_COOKIE_SECURE = _str_to_bool(os.getenv("SESSION_COOKIE_SECURE"), default=True)
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "None")
SESSION_COOKIE_EXPIRES_DAYS = int(os.getenv("SESSION_COOKIE_EXPIRES_DAYS", "5"))

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(BASE_DIR, "static", "photos", "services")
PHOTOS_AUTO_DIR = os.getenv("PHOTOS_AUTO_DIR", "/var/www/rdmotorsAPI/static/photos/autousa")
os.makedirs(PHOTOS_AUTO_DIR, exist_ok=True)

# App configuration
class Config:
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = API_KEY
    CORS_ORIGINS = CORS_ORIGINS
    CORS_SUPPORTS_CREDENTIALS = True
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

    # Firebase session auth
    FIREBASE_SERVICE_ACCOUNT_PATH = FIREBASE_SERVICE_ACCOUNT_PATH
    FIREBASE_SERVICE_ACCOUNT_JSON = FIREBASE_SERVICE_ACCOUNT_JSON
    FIREBASE_PROJECT_ID = FIREBASE_PROJECT_ID
    FIREBASE_PRIVATE_KEY_ID = FIREBASE_PRIVATE_KEY_ID
    FIREBASE_PRIVATE_KEY = FIREBASE_PRIVATE_KEY
    FIREBASE_CLIENT_EMAIL = FIREBASE_CLIENT_EMAIL
    FIREBASE_CLIENT_ID = FIREBASE_CLIENT_ID
    SESSION_COOKIE_NAME = SESSION_COOKIE_NAME
    CSRF_COOKIE_NAME = CSRF_COOKIE_NAME
    SESSION_COOKIE_SECURE = SESSION_COOKIE_SECURE
    SESSION_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE
    SESSION_COOKIE_EXPIRES_DAYS = SESSION_COOKIE_EXPIRES_DAYS
