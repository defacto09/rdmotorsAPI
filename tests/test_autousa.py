"""Tests for AutoUSA endpoints"""
import pytest


class TestAutoUSAValidation:
    """Test AutoUSA validation"""
    
    def test_get_autousa_by_vin_invalid(self, client, auth_headers):
        """Test getting auto with invalid VIN"""
        response = client.get('/autousa/vin/INVALID', headers=auth_headers)
        assert response.status_code == 400
    
    def test_get_autousa_by_vin_not_found(self, client, auth_headers):
        """Test getting non-existent auto"""
        response = client.get('/autousa/vin/1HGBH41JXMN109186', headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_autousa_by_vin_success(self, client, auth_headers, sample_autousa):
        """Test getting auto by VIN successfully"""
        response = client.get(f'/autousa/vin/{sample_autousa.vin}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['vin'] == sample_autousa.vin


class TestCreateAutoUSA:
    """Test creating AutoUSA"""
    
    def test_create_autousa_invalid_vin(self, client, auth_headers):
        """Test creating auto with invalid VIN"""
        data = {
            'vin': 'INVALID',
            'mark': 'Honda',
            'model': 'Civic'
        }
        response = client.post('/autousa', json=data, headers=auth_headers)
        assert response.status_code == 400
    
    def test_create_autousa_success(self, client, auth_headers, app):
        """Test creating auto successfully"""
        data = {
            'vin': '1HGBH41JXMN109187',
            'mark': 'Toyota',
            'model': 'Camry',
            'container_number': 'CONT123'
        }
        response = client.post('/autousa', json=data, headers=auth_headers)
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['vin'] == '1HGBH41JXMN109187'
        assert response_data['mark'] == 'Toyota'


class TestAutoUSAHistory:
    """Test AutoUSA history endpoint"""
    
    def test_get_history_invalid_vin(self, client, auth_headers):
        """Test getting history with invalid VIN"""
        response = client.get('/autousa/vin/INVALID/history', headers=auth_headers)
        assert response.status_code == 400
    
    def test_get_history_not_found(self, client, auth_headers):
        """Test getting history for non-existent auto"""
        response = client.get('/autousa/vin/1HGBH41JXMN109186/history', headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_history_success(self, client, auth_headers, sample_autousa):
        """Test getting history successfully"""
        response = client.get(f'/autousa/vin/{sample_autousa.vin}/history', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
