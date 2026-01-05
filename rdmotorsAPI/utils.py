"""Utility functions for the API"""
from flask import request
from datetime import datetime
import bleach
from rdmotorsAPI.config import BASE_URL


def get_photo_url(filename):
    """Get photo URL for services"""
    return f"{BASE_URL}/photos/services/{filename}"


def get_car_photo_url(filename):
    """Get photo URL for cars"""
    return f"{BASE_URL}/photos/cars/{filename}"


def get_service_photo_url(filename):
    """Get service photo URL"""
    if not filename:
        return None
    return f"{BASE_URL}/static/photos/services/{filename}"


def parse_date(date_str):
    """Parse date string to date object"""
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def normalize_int(value):
    """Normalize integer value, handling None and empty strings"""
    if value in [None, "", " "]:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def validate_vin(vin):
    """Validate VIN format (17 characters, alphanumeric)"""
    if not vin or len(vin) != 17:
        return False
    return vin.isalnum()


def get_pagination_params():
    """Extract pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    # Limit per_page to prevent excessive queries
    per_page = min(per_page, 100)
    return page, per_page


def sanitize_string(value, max_length=None, allow_html=False):
    """
    Sanitize string input to prevent XSS attacks
    
    Args:
        value: String to sanitize
        max_length: Maximum length of the string
        allow_html: Whether to allow HTML tags (default: False)
    
    Returns:
        Sanitized string or None if value is None/empty
    """
    if not value:
        return None
    
    # Convert to string
    value = str(value).strip()
    
    if not value:
        return None
    
    # Sanitize HTML/script tags
    if not allow_html:
        value = bleach.clean(value, tags=[], strip=True)
    
    # Enforce max length
    if max_length:
        value = value[:max_length]
    
    return value


def sanitize_email(email):
    """
    Sanitize and validate email address
    
    Args:
        email: Email string to sanitize
    
    Returns:
        Sanitized email or None if invalid
    """
    if not email:
        return None
    
    email = sanitize_string(email, max_length=255)
    if not email:
        return None
    
    # Basic email validation
    if '@' not in email or '.' not in email.split('@')[-1]:
        return None
    
    return email.lower()
