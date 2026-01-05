"""Pytest configuration and fixtures"""
import pytest
import os
from rdmotorsAPI import create_app, db
from rdmotorsAPI.config import Config
from rdmotorsAPI.models import Service, Location, AutoUsa, Client, Car, AutoUsaHistory


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URI',
        'sqlite:///:memory:'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = 'test_api_key_for_testing'
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config.from_object(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Get authentication headers for testing"""
    return {
        'Authorization': 'Bearer test_api_key_for_testing',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_service(app):
    """Create a sample service for testing"""
    with app.app_context():
        service = Service(
            name="Test Service",
            descr="Test Description",
            price=100.00,
            currency="USD",
            photo_filename="test.jpg"
        )
        db.session.add(service)
        db.session.commit()
        return service


@pytest.fixture
def sample_location(app):
    """Create a sample location for testing"""
    with app.app_context():
        location = Location(
            country="USA",
            description="Test Location"
        )
        db.session.add(location)
        db.session.commit()
        return location


@pytest.fixture
def sample_autousa(app, sample_location):
    """Create a sample AutoUSA for testing"""
    with app.app_context():
        auto = AutoUsa(
            vin="1HGBH41JXMN109186",
            container_number="TEST123",
            mark="Honda",
            model="Civic",
            loc_now_id=sample_location.location_id
        )
        db.session.add(auto)
        db.session.commit()
        return auto


@pytest.fixture
def sample_client(app):
    """Create a sample client for testing"""
    with app.app_context():
        client = Client(
            login="testuser",
            email="test@example.com",
            number="+1234567890",
            status="active"
        )
        db.session.add(client)
        db.session.commit()
        return client


@pytest.fixture
def sample_car(app):
    """Create a sample car for testing"""
    with app.app_context():
        car = Car(
            mark="Toyota",
            model="Camry",
            year=2020,
            addi="Test addition",
            transmission="Automatic",
            mileage=10000,
            fuel_type="Gasoline",
            price=25000,
            discount=0,
            quality=5,
            engine="2.5L",
            photo_url="https://example.com/car.jpg"
        )
        db.session.add(car)
        db.session.commit()
        return car
