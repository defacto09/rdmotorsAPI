"""Configuration module for the API"""
import os
from typing import Dict, List, Optional
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


def _get_database_env() -> Dict[str, Optional[str]]:
    """Collect database-related environment variables."""
    return {
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_NAME": os.getenv("DB_NAME"),
    }


def get_missing_database_env_vars() -> List[str]:
    """Return missing database env vars for default MySQL configuration."""
    return [key for key, value in _get_database_env().items() if not value]


def _build_sqlalchemy_database_uri() -> Optional[str]:
    """Build SQLAlchemy database URI from environment configuration."""
    explicit_uri = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
    if explicit_uri:
        return explicit_uri

    db_env = _get_database_env()
    missing_vars = [key for key, value in db_env.items() if not value]
    if missing_vars:
        return None

    db_password_escaped = quote_plus(db_env["DB_PASSWORD"] or "")
    return (
        f"mysql+pymysql://{db_env['DB_USER']}:{db_password_escaped}"
        f"@{db_env['DB_HOST']}:{db_env['DB_PORT']}/{db_env['DB_NAME']}?charset=utf8mb4"
    )

API_KEY = os.getenv("API_KEY")
SQLALCHEMY_DATABASE_URI = _build_sqlalchemy_database_uri()

# CORS configuration
CORS_ORIGINS = _parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:3000"))

# Base URL for generating photo URLs
BASE_URL = os.getenv("BASE_URL", "https://rdmotors.com.ua")
STATIC_FOLDER = os.getenv("STATIC_FOLDER") or os.getenv("FRONTEND_STATIC_FOLDER")

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
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
SESSION_COOKIE_SECURE = _str_to_bool(os.getenv("SESSION_COOKIE_SECURE"), default=True)
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "None")
SESSION_COOKIE_EXPIRES_DAYS = int(os.getenv("SESSION_COOKIE_EXPIRES_DAYS", "5"))

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(BASE_DIR, "static", "photos", "services")
PHOTOS_AUTO_DIR = os.getenv("PHOTOS_AUTO_DIR", "/var/www/rdmotorsAPI/static/photos/autousa")

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
    BASE_URL = BASE_URL
    STATIC_FOLDER = STATIC_FOLDER
    PHOTOS_DIR = PHOTOS_DIR
    PHOTOS_AUTO_DIR = PHOTOS_AUTO_DIR
    
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
    SESSION_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
    SESSION_COOKIE_SECURE = SESSION_COOKIE_SECURE
    SESSION_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE
    SESSION_COOKIE_EXPIRES_DAYS = SESSION_COOKIE_EXPIRES_DAYS
