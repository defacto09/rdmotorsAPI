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

    def test_get_car_by_id_is_public(self, client, sample_car):
        """Test that car details are public"""
        response = client.get(f'/cars/{sample_car.car_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['car_id'] == sample_car.car_id
        assert data['mark'] == sample_car.mark


class TestProtectedCarMutations:
    """Test that car mutations remain protected"""

    def test_create_car_requires_auth(self, client):
        """Test that creating a car still requires authentication"""
        response = client.post('/cars', json={})
        assert response.status_code == 401
