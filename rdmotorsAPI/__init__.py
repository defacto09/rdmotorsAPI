"""RD Motors API package initialization"""
import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from rdmotorsAPI.config import Config, get_missing_database_env_vars

# Initialize extensions
db = SQLAlchemy()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)

# Import models after db is created (models import db from here)
from rdmotorsAPI import models  # noqa: E402, F401


def _resolve_static_folder(config_object) -> str:
    """Resolve the static directory used to serve the SPA frontend."""
    configured_static = getattr(config_object, "STATIC_FOLDER", None)
    if configured_static:
        return str(configured_static)

    package_dir = Path(__file__).resolve().parent
    project_root = package_dir.parent
    candidates = [
        project_root / "static",
        package_dir / "static",
    ]

    for candidate in candidates:
        if (candidate / "index.html").exists():
            return str(candidate)

    return str(candidates[0])


def _prepare_app_config(app: Flask) -> None:
    """Validate and normalize app configuration before extension init."""
    database_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not database_uri:
        missing_vars = get_missing_database_env_vars()
        missing = ", ".join(missing_vars) if missing_vars else "SQLALCHEMY_DATABASE_URI"
        raise RuntimeError(
            "Database configuration is missing. Set SQLALCHEMY_DATABASE_URI "
            f"or provide DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME. Missing: {missing}"
        )

    if database_uri.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}

    photos_auto_dir = app.config.get("PHOTOS_AUTO_DIR")
    if photos_auto_dir:
        os.makedirs(photos_auto_dir, exist_ok=True)


def create_app(config_object=Config):
    """Application factory pattern"""
    app = Flask(__name__, static_folder=_resolve_static_folder(config_object))
    app.config.from_object(config_object)
    _prepare_app_config(app)
    
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
