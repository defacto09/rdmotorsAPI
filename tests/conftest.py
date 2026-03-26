"""Pytest configuration and fixtures"""
import os
import shutil
import pytest
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
    SQLALCHEMY_ENGINE_OPTIONS = {}
    API_KEY = 'test_api_key_for_testing'
    WTF_CSRF_ENABLED = False
    ENABLE_API_DOCS = False
    PHOTOS_AUTO_DIR = os.path.join(
        os.path.dirname(__file__),
        ".tmp",
        "photos",
        "autousa",
    )
    STATIC_DIR = os.path.join(
        os.path.dirname(__file__),
        ".tmp",
        "static",
    )
    STATIC_FOLDER = STATIC_DIR


@pytest.fixture
def app():
    """Create application for testing"""
    shutil.rmtree(TestConfig.STATIC_DIR, ignore_errors=True)
    shutil.rmtree(TestConfig.PHOTOS_AUTO_DIR, ignore_errors=True)

    app = create_app(TestConfig)
    os.makedirs(TestConfig.STATIC_DIR, exist_ok=True)
    with open(os.path.join(TestConfig.STATIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write("<!doctype html><html><body>RD Motors Test SPA</body></html>")
    
    with app.app_context():
        db.session.remove()
        db.session.configure(expire_on_commit=False)
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    shutil.rmtree(TestConfig.STATIC_DIR, ignore_errors=True)
    shutil.rmtree(TestConfig.PHOTOS_AUTO_DIR, ignore_errors=True)


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
def browser_headers():
    """Headers that mimic direct browser navigation to an HTML page."""
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
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
        _ = auto.loc_now
        _ = auto.loc_next
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
