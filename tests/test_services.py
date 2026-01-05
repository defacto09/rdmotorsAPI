"""Tests for services endpoints"""
import pytest
import json


class TestGetServices:
    """Test GET /services endpoint"""
    
    def test_get_services_requires_auth(self, client):
        """Test that authentication is required"""
        response = client.get('/services')
        assert response.status_code == 401
    
    def test_get_services_with_auth(self, client, auth_headers, sample_service):
        """Test getting services with authentication"""
        response = client.get('/services', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'pagination' in data
        assert len(data['data']) >= 1
    
    def test_get_services_pagination(self, client, auth_headers, app, sample_service):
        """Test pagination"""
        with app.app_context():
            # Create more services
            for i in range(5):
                service = Service(
                    name=f"Service {i}",
                    descr="Test",
                    price=100.00,
                    currency="USD",
                    photo_filename="test.jpg"
                )
                from rdmotorsAPI import db
                db.session.add(service)
            from rdmotorsAPI import db
            db.session.commit()
        
        response = client.get('/services?page=1&per_page=2', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 2
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 2


class TestGetServiceById:
    """Test GET /services/<id> endpoint"""
    
    def test_get_service_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent service"""
        response = client.get('/services/99999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_service_by_id_success(self, client, auth_headers, sample_service):
        """Test getting service by ID"""
        response = client.get(f'/services/{sample_service.service_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['service_id'] == sample_service.service_id
        assert data['name'] == sample_service.name


class TestCreateService:
    """Test POST /services endpoint"""
    
    def test_create_service_requires_auth(self, client):
        """Test that authentication is required"""
        response = client.post('/services', json={})
        assert response.status_code == 401
    
    def test_create_service_missing_fields(self, client, auth_headers):
        """Test creating service with missing fields"""
        response = client.post('/services', 
                             json={'name': 'Test'}, 
                             headers=auth_headers)
        assert response.status_code == 400
    
    def test_create_service_success(self, client, auth_headers, app):
        """Test creating a service successfully"""
        data = {
            'name': 'New Service',
            'descr': 'Description',
            'price': 150.00,
            'currency': 'USD',
            'photo_filename': 'new.jpg'
        }
        response = client.post('/services', 
                             json=data, 
                             headers=auth_headers)
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['name'] == 'New Service'
        assert response_data['price'] == 150.00


class TestUpdateService:
    """Test PUT/PATCH /services/<id> endpoint"""
    
    def test_update_service_not_found(self, client, auth_headers):
        """Test updating non-existent service"""
        response = client.patch('/services/99999', 
                              json={'name': 'Updated'}, 
                              headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_service_success(self, client, auth_headers, sample_service):
        """Test updating service successfully"""
        response = client.patch(f'/services/{sample_service.service_id}', 
                              json={'name': 'Updated Name'}, 
                              headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Name'


class TestDeleteService:
    """Test DELETE /services/<id> endpoint"""
    
    def test_delete_service_not_found(self, client, auth_headers):
        """Test deleting non-existent service"""
        response = client.delete('/services/99999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_service_success(self, client, auth_headers, app):
        """Test deleting service successfully"""
        with app.app_context():
            from rdmotorsAPI.models import Service
            from rdmotorsAPI import db
            service = Service(
                name="To Delete",
                descr="Test",
                price=100.00,
                currency="USD",
                photo_filename="test.jpg"
            )
            db.session.add(service)
            db.session.commit()
            service_id = service.service_id
        
        response = client.delete(f'/services/{service_id}', headers=auth_headers)
        assert response.status_code == 200
        
        # Verify it's deleted
        response = client.get(f'/services/{service_id}', headers=auth_headers)
        assert response.status_code == 404
