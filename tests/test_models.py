"""Tests for database models"""
import pytest
from rdmotorsAPI.models import Service, Location, AutoUsa, Client, Car


class TestServiceModel:
    """Test Service model"""
    
    def test_service_to_dict(self, sample_service):
        """Test service serialization"""
        data = sample_service.to_dict()
        assert 'service_id' in data
        assert 'name' in data
        assert 'price' in data
        assert data['name'] == sample_service.name


class TestLocationModel:
    """Test Location model"""
    
    def test_location_to_dict(self, sample_location):
        """Test location serialization"""
        data = sample_location.to_dict()
        assert 'location_id' in data
        assert 'country' in data
        assert data['country'] == sample_location.country


class TestAutoUsaModel:
    """Test AutoUsa model"""
    
    def test_autousa_to_dict(self, sample_autousa):
        """Test AutoUsa serialization"""
        data = sample_autousa.to_dict()
        assert 'id' in data
        assert 'vin' in data
        assert 'mark' in data
        assert data['vin'] == sample_autousa.vin
    
    def test_autousa_unique_vin(self, app, sample_autousa):
        """Test that VIN must be unique"""
        with app.app_context():
            from rdmotorsAPI import db
            duplicate = AutoUsa(
                vin=sample_autousa.vin,  # Same VIN
                mark="Different",
                model="Different"
            )
            db.session.add(duplicate)
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()
            db.session.rollback()


class TestClientModel:
    """Test Client model"""
    
    def test_client_to_dict(self, sample_client):
        """Test client serialization"""
        data = sample_client.to_dict()
        assert 'client_id' in data
        assert 'email' in data
        assert data['email'] == sample_client.email
    
    def test_client_unique_email(self, app, sample_client):
        """Test that email must be unique"""
        with app.app_context():
            from rdmotorsAPI import db
            duplicate = Client(
                login="different",
                email=sample_client.email,  # Same email
                number="+9876543210",
                status="active"
            )
            db.session.add(duplicate)
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()
            db.session.rollback()


class TestCarModel:
    """Test Car model"""
    
    def test_car_to_dict(self, sample_car):
        """Test car serialization"""
        data = sample_car.to_dict()
        assert 'car_id' in data
        assert 'mark' in data
        assert 'price' in data
        assert data['mark'] == sample_car.mark
