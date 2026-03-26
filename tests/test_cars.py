"""Tests for cars endpoints"""


class TestGetCars:
    """Test GET /cars endpoint"""

    def test_get_cars_is_public(self, client, sample_car):
        """Test that cars listing is public"""
        response = client.get('/cars')
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'pagination' in data
        assert len(data['data']) >= 1

    def test_cars_browser_navigation_serves_spa(self, client, browser_headers):
        """Test that browser navigation receives SPA HTML instead of API JSON."""
        response = client.get('/cars', headers=browser_headers)
        assert response.status_code == 200
        assert 'text/html' in response.content_type
        assert b'RD Motors Test SPA' in response.data

    def test_get_car_by_id_is_public(self, client, sample_car):
        """Test that car details are public"""
        response = client.get(f'/cars/{sample_car.car_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['car_id'] == sample_car.car_id
        assert data['mark'] == sample_car.mark

    def test_car_page_browser_navigation_serves_spa(self, client, sample_car, browser_headers):
        """Test that browser navigation to car page receives SPA HTML."""
        response = client.get(f'/cars/{sample_car.car_id}', headers=browser_headers)
        assert response.status_code == 200
        assert 'text/html' in response.content_type
        assert b'RD Motors Test SPA' in response.data


class TestProtectedCarMutations:
    """Test that car mutations remain protected"""

    def test_create_car_requires_auth(self, client):
        """Test that creating a car still requires authentication"""
        response = client.post('/cars', json={})
        assert response.status_code == 401
