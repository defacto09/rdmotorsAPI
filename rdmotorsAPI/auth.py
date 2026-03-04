"""Authentication and authorization middleware."""
from __future__ import annotations

import json
import logging
from datetime import timedelta
from functools import wraps
from typing import Any, Dict, Optional

from flask import current_app, g, jsonify, request

from rdmotorsAPI.config import API_KEY


def _get_api_key() -> Optional[str]:
    """Get configured API key (app config overrides env default)."""
    return current_app.config.get("API_KEY", API_KEY)


def _is_valid_api_key_request() -> bool:
    """Check whether current request has valid API key Authorization header."""
    configured_api_key = _get_api_key()
    if not configured_api_key:
        return False
    key = request.headers.get("Authorization")
    return key == f"Bearer {configured_api_key}"


def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _is_valid_api_key_request():
            logging.warning("Unauthorized API key attempt to %s from %s", request.path, request.remote_addr)
            return jsonify({"error": "Unauthorized", "message": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated


def _get_firebase_auth():
    """
    Initialize Firebase Admin SDK lazily and return firebase_admin.auth module.

    We initialize only when first needed to avoid hard failure at import time.
    """
    try:
        import firebase_admin
        from firebase_admin import auth as firebase_auth
        from firebase_admin import credentials
    except Exception as exc:
        raise RuntimeError(
            "Firebase Admin SDK is not available. Install firebase-admin and configure credentials."
        ) from exc

    if not firebase_admin._apps:
        service_account_path = current_app.config.get("FIREBASE_SERVICE_ACCOUNT_PATH")
        service_account_json = current_app.config.get("FIREBASE_SERVICE_ACCOUNT_JSON")
        project_id = current_app.config.get("FIREBASE_PROJECT_ID")
        private_key_id = current_app.config.get("FIREBASE_PRIVATE_KEY_ID")
        private_key = current_app.config.get("FIREBASE_PRIVATE_KEY")
        client_email = current_app.config.get("FIREBASE_CLIENT_EMAIL")
        client_id = current_app.config.get("FIREBASE_CLIENT_ID")

        if service_account_json:
            try:
                cred_info = json.loads(service_account_json)
            except json.JSONDecodeError as exc:
                raise RuntimeError("Invalid FIREBASE_SERVICE_ACCOUNT_JSON format") from exc
            cred = credentials.Certificate(cred_info)
        elif service_account_path:
            cred = credentials.Certificate(service_account_path)
        elif project_id and private_key and client_email:
            normalized_private_key = private_key.strip().strip('"').replace("\\n", "\n")
            cred_info = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": private_key_id,
                "private_key": normalized_private_key,
                "client_email": client_email,
                "client_id": client_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
            cred = credentials.Certificate(cred_info)
        else:
            cred = credentials.ApplicationDefault()

        options: Dict[str, Any] = {}
        if project_id:
            options["projectId"] = project_id

        firebase_admin.initialize_app(cred, options=options or None)

    return firebase_auth


def verify_firebase_id_token(id_token: str) -> Dict[str, Any]:
    """Verify Firebase ID token."""
    firebase_auth = _get_firebase_auth()
    return firebase_auth.verify_id_token(id_token)


def create_firebase_session_cookie(id_token: str, expires_in_seconds: int) -> str:
    """Create Firebase session cookie from ID token."""
    firebase_auth = _get_firebase_auth()
    return firebase_auth.create_session_cookie(
        id_token,
        expires_in=timedelta(seconds=expires_in_seconds),
    )


def verify_firebase_session_cookie(session_cookie: str, check_revoked: bool = True) -> Dict[str, Any]:
    """Verify Firebase session cookie."""
    firebase_auth = _get_firebase_auth()
    return firebase_auth.verify_session_cookie(session_cookie, check_revoked=check_revoked)


def revoke_firebase_sessions(uid: str) -> None:
    """Revoke all refresh tokens for Firebase user."""
    firebase_auth = _get_firebase_auth()
    firebase_auth.revoke_refresh_tokens(uid)


def require_firebase_auth(f):
    """
    Require Firebase session cookie auth.

    Legacy API-key auth is still accepted as fallback for backward compatibility.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        session_cookie_name = current_app.config.get("SESSION_COOKIE_NAME", "__session")
        session_cookie = request.cookies.get(session_cookie_name)
        if not session_cookie:
            logging.warning("Missing Firebase session cookie for %s from %s", request.path, request.remote_addr)
            return jsonify({"error": "Unauthorized", "message": "Missing session cookie"}), 401

        try:
            decoded_claims = verify_firebase_session_cookie(session_cookie, check_revoked=True)
            g.auth_mode = "firebase"
            g.firebase_user = decoded_claims
            g.user_uid = decoded_claims.get("uid")
            return f(*args, **kwargs)
        except RuntimeError as exc:
            logging.error("Firebase auth unavailable on %s: %s", request.path, str(exc))
            return jsonify({"error": "AuthUnavailable", "message": str(exc)}), 503
        except Exception as exc:
            logging.warning("Invalid Firebase session on %s: %s", request.path, str(exc))
            return jsonify({"error": "Unauthorized", "message": "Invalid or expired session"}), 401

    return decorated
