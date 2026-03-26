"""Tests for /api-prefixed route aliases."""


class TestApiRouteAliases:
    """Verify that explicit /api routes return JSON and preserve auth behavior."""

    def test_api_services_returns_json_for_browser_request(self, client, sample_service, browser_headers):
        response = client.get('/api/services', headers=browser_headers)

        assert response.status_code == 200
        assert response.is_json
        data = response.get_json()
        assert 'data' in data
        assert len(data['data']) >= 1

    def test_api_service_detail_returns_json_for_browser_request(
        self, client, sample_service, browser_headers
    ):
        response = client.get(f'/api/services/{sample_service.service_id}', headers=browser_headers)

        assert response.status_code == 200
        assert response.is_json
        assert response.get_json()['service_id'] == sample_service.service_id

    def test_api_cars_returns_json_for_browser_request(self, client, sample_car, browser_headers):
        response = client.get('/api/cars', headers=browser_headers)

        assert response.status_code == 200
        assert response.is_json
        data = response.get_json()
        assert 'data' in data
        assert len(data['data']) >= 1

    def test_api_car_detail_returns_json_for_browser_request(
        self, client, sample_car, browser_headers
    ):
        response = client.get(f'/api/cars/{sample_car.car_id}', headers=browser_headers)

        assert response.status_code == 200
        assert response.is_json
        assert response.get_json()['car_id'] == sample_car.car_id

    def test_api_clients_requires_auth(self, client):
        response = client.get('/api/clients')

        assert response.status_code == 401

    def test_api_clients_with_auth(self, client, auth_headers, sample_client):
        response = client.get('/api/clients', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert len(data['data']) >= 1

    def test_api_autousa_alias_with_auth(self, client, auth_headers, sample_autousa):
        response = client.get(f'/api/autousa/vin/{sample_autousa.vin}', headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json()['vin'] == sample_autousa.vin

    def test_api_locations_alias_is_public(self, client, sample_location):
        response = client.get('/api/locations')

        assert response.status_code == 200
        assert isinstance(response.get_json(), list)
        assert len(response.get_json()) >= 1
