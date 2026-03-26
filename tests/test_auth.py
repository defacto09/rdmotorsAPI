"""Tests for authentication"""

from rdmotorsAPI.routes import session as session_routes


def test_require_api_key_missing(client):
    """Test that endpoint requires API key"""
    response = client.post('/services', json={})
    assert response.status_code == 401
    assert 'error' in response.get_json()
    assert response.get_json()['error'] == 'Unauthorized'


def test_require_api_key_invalid(client):
    """Test that invalid API key is rejected"""
    headers = {'Authorization': 'Bearer wrong_key'}
    response = client.post('/services', json={}, headers=headers)
    assert response.status_code == 401


def test_require_api_key_valid(client, auth_headers):
    """Test that valid API key is accepted"""
    response = client.post('/services', json={}, headers=auth_headers)
    assert response.status_code != 401


def test_session_login_sets_cookie_domain(client, app, monkeypatch):
    """Test that session login can set a shared cookie domain."""
    app.config["SESSION_COOKIE_DOMAIN"] = ".rdmotors.com.ua"

    monkeypatch.setattr(
        session_routes,
        "verify_firebase_id_token",
        lambda id_token: {"uid": "test-uid", "email": "test@example.com"},
    )
    monkeypatch.setattr(
        session_routes,
        "create_firebase_session_cookie",
        lambda id_token, expires_in_seconds: "test-session-cookie",
    )

    response = client.post('/api/login', json={"idToken": "test-id-token"})

    assert response.status_code == 200
    set_cookie_headers = response.headers.getlist("Set-Cookie")
    assert any(
        "__session=test-session-cookie" in header and "Domain=rdmotors.com.ua" in header
        for header in set_cookie_headers
    )
    assert any(
        "csrfToken=" in header and "Domain=rdmotors.com.ua" in header
        for header in set_cookie_headers
    )
