"""RD Motors API package initialization"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from rdmotorsAPI.config import Config

# Initialize extensions
db = SQLAlchemy()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)

# Import models after db is created (models import db from here)
from rdmotorsAPI import models  # noqa: E402, F401


def create_app():
    """Application factory pattern"""
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    cors.init_app(
        app,
        methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
        resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", [])}},
        allow_headers=['Authorization', 'Content-Type', 'X-CSRF-Token'],
    )
    limiter.init_app(app)
    
    # Register blueprints
    from rdmotorsAPI.routes import services, autousa, cars, clients, locations, session
    app.register_blueprint(services.services_bp)
    app.register_blueprint(autousa.autousa_bp)
    app.register_blueprint(cars.cars_bp)
    app.register_blueprint(clients.clients_bp)
    app.register_blueprint(locations.locations_bp)
    app.register_blueprint(session.session_bp)
    
    # Register API documentation (optional - can be disabled in production)
    if app.config.get('ENABLE_API_DOCS', True):
        from rdmotorsAPI.api_docs import api
        api.init_app(app)
    
    return app
