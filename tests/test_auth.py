"""Tests for authentication"""
import pytest
from rdmotorsAPI.auth import require_api_key


def test_require_api_key_missing(client):
    """Test that endpoint requires API key"""
    response = client.get('/services')
    assert response.status_code == 401
    assert 'error' in response.get_json()
    assert response.get_json()['error'] == 'Unauthorized'


def test_require_api_key_invalid(client):
    """Test that invalid API key is rejected"""
    headers = {'Authorization': 'Bearer wrong_key'}
    response = client.get('/services', headers=headers)
    assert response.status_code == 401


def test_require_api_key_valid(client, auth_headers):
    """Test that valid API key is accepted"""
    # This will fail if service endpoint doesn't exist, but auth should pass
    response = client.get('/services', headers=auth_headers)
    # Should not be 401 (might be 200 or 404 depending on data)
    assert response.status_code != 401
