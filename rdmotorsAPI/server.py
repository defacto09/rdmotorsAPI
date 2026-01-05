"""Main server file - entry point for the API"""
from flask import Flask, jsonify, request, make_response, send_from_directory
from werkzeug.exceptions import HTTPException
from datetime import datetime
import os
import logging
from rdmotorsAPI import create_app, db
from rdmotorsAPI.config import PHOTOS_DIR

# Configure logging
log_dir = os.getenv("LOG_DIR", os.path.dirname(os.path.abspath(__file__)))
log_file = os.path.join(log_dir, "autousa_photos.log")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Create Flask app
app = create_app()

# Register error handlers
def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "The requested resource was not found"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": "Invalid request data"}), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({"error": e.name, "description": e.description, "code": e.code}), e.code

        logging.error(
            f"Exception occurred at {request.method} {request.path}",
            exc_info=True
        )
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

# Register error handlers
register_error_handlers(app)

# Register middleware
def register_middleware(app):
    """Register middleware functions"""
    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            resp = make_response('', 204)  # Відповідь 204 No Content
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            return resp

    @app.before_request
    def validate_json():
        # Skip validation for file upload endpoints
        if request.endpoint in ['upload_auto_photos', 'serve_photo', 'serve_spa', 'get_auto_photos']:
            return
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json and request.content_type != 'application/json':
                return jsonify({"error": "Content-Type must be application/json"}), 400

    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

# Register middleware
register_middleware(app)

# Static file serving
@app.route('/photos/services/<path:filename>')
def serve_photo(filename):
    """Serve service photos"""
    resp = make_response(send_from_directory(PHOTOS_DIR, filename))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def serve_spa(path):
    """Serve SPA frontend"""
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text("SELECT 1"))
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # Use environment variable for debug mode (default: False for production)
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
