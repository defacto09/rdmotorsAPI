"""Authentication and authorization middleware"""
from functools import wraps
from flask import request, jsonify
import logging
from rdmotorsAPI.config import API_KEY


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("Authorization")
        if not key or key != f"Bearer {API_KEY}":
            logging.warning(f"Unauthorized access attempt to {request.path} from {request.remote_addr}")
            return jsonify({"error": "Unauthorized", "message": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated
