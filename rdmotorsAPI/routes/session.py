"""Session authentication routes."""
from __future__ import annotations

import logging
import secrets

from flask import Blueprint, current_app, jsonify, request

from rdmotorsAPI.auth import (
    create_firebase_session_cookie,
    revoke_firebase_sessions,
    verify_firebase_id_token,
    verify_firebase_session_cookie,
)

session_bp = Blueprint("session", __name__)


def _get_cookie_security_config():
    return {
        "secure": current_app.config.get("SESSION_COOKIE_SECURE", True),
        "samesite": current_app.config.get("SESSION_COOKIE_SAMESITE", "None"),
        "domain": current_app.config.get("SESSION_COOKIE_DOMAIN"),
        "path": "/",
    }


def _parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


@session_bp.route("/sessionLogin", methods=["POST"])
@session_bp.route("/api/sessionLogin", methods=["POST"])
@session_bp.route("/api/login", methods=["POST"])
def session_login():
    """Create Firebase-backed session cookie from ID token."""
    data = request.get_json(silent=True) or {}
    id_token = data.get("idToken")
    if not id_token:
        return jsonify({"error": "BadRequest", "message": "idToken is required"}), 400

    max_age = int(current_app.config.get("SESSION_COOKIE_EXPIRES_DAYS", 5) * 24 * 60 * 60)
    session_cookie_name = current_app.config.get("SESSION_COOKIE_NAME", "__session")
    csrf_cookie_name = current_app.config.get("CSRF_COOKIE_NAME", "csrfToken")
    cookie_security = _get_cookie_security_config()

    try:
        decoded_id_token = verify_firebase_id_token(id_token)
        session_cookie = create_firebase_session_cookie(id_token=id_token, expires_in_seconds=max_age)
    except RuntimeError as exc:
        logging.error("Session login unavailable: %s", str(exc))
        return jsonify({"error": "AuthUnavailable", "message": str(exc)}), 503
    except Exception as exc:
        logging.warning("Failed session login: %s", str(exc))
        return jsonify({"error": "Unauthorized", "message": "Invalid Firebase ID token"}), 401

    csrf_token = secrets.token_urlsafe(32)
    response = jsonify(
        {
            "status": "success",
            "uid": decoded_id_token.get("uid"),
            "email": decoded_id_token.get("email"),
        }
    )

    response.set_cookie(
        session_cookie_name,
        session_cookie,
        max_age=max_age,
        httponly=True,
        secure=cookie_security["secure"],
        samesite=cookie_security["samesite"],
        domain=cookie_security["domain"],
        path=cookie_security["path"],
    )
    response.set_cookie(
        csrf_cookie_name,
        csrf_token,
        max_age=max_age,
        httponly=False,
        secure=cookie_security["secure"],
        samesite=cookie_security["samesite"],
        domain=cookie_security["domain"],
        path=cookie_security["path"],
    )
    return response, 200


@session_bp.route("/sessionLogout", methods=["POST"])
@session_bp.route("/api/sessionLogout", methods=["POST"])
@session_bp.route("/api/logout", methods=["POST"])
def session_logout():
    """Clear session cookie and optionally revoke Firebase refresh tokens."""
    data = request.get_json(silent=True) or {}
    revoke = _parse_bool(data.get("revoke"), default=False)

    session_cookie_name = current_app.config.get("SESSION_COOKIE_NAME", "__session")
    csrf_cookie_name = current_app.config.get("CSRF_COOKIE_NAME", "csrfToken")
    cookie_security = _get_cookie_security_config()
    session_cookie = request.cookies.get(session_cookie_name)

    if revoke and session_cookie:
        try:
            decoded_claims = verify_firebase_session_cookie(session_cookie, check_revoked=False)
            uid = decoded_claims.get("uid")
            if uid:
                revoke_firebase_sessions(uid)
        except Exception as exc:
            logging.warning("Session revoke skipped: %s", str(exc))

    response = jsonify({"status": "success"})
    response.delete_cookie(
        session_cookie_name,
        domain=cookie_security["domain"],
        path=cookie_security["path"],
        secure=cookie_security["secure"],
        samesite=cookie_security["samesite"],
    )
    response.delete_cookie(
        csrf_cookie_name,
        domain=cookie_security["domain"],
        path=cookie_security["path"],
        secure=cookie_security["secure"],
        samesite=cookie_security["samesite"],
    )
    return response, 200
