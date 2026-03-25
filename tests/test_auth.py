"""Tests for authentication"""


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
