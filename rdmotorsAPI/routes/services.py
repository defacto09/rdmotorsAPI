"""Services routes blueprint"""
from flask import Blueprint, jsonify, request
from rdmotorsAPI.models import Service, db
from rdmotorsAPI.auth import require_api_key
from rdmotorsAPI.utils import get_pagination_params, sanitize_string
from rdmotorsAPI import limiter  # noqa: E402
import logging

services_bp = Blueprint('services', __name__)


@services_bp.route("/services", methods=["GET"])
@limiter.limit("100 per hour")
@require_api_key
def get_services():
    """Get all services with optional pagination"""
    page, per_page = get_pagination_params()
    pagination = Service.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "data": [service.to_dict() for service in pagination.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    })


@services_bp.route("/services/<int:service_id>", methods=["GET"])
@require_api_key
def get_service_by_id(service_id):
    """Get service by ID"""
    service = Service.query.get(service_id)
    if service:
        return jsonify(service.to_dict())
    return jsonify({"error": "Service not found"}), 404


@services_bp.route("/services", methods=["POST"])
@limiter.limit("50 per hour")
@require_api_key
def add_service():
    """Create a new service"""
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Validate required fields
    required_fields = ["name", "descr", "price", "currency", "photo_filename"]
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Sanitize string inputs
    if 'name' in data:
        data['name'] = sanitize_string(data['name'], max_length=100)
    if 'descr' in data:
        data['descr'] = sanitize_string(data['descr'], max_length=500)
    if 'photo_filename' in data:
        data['photo_filename'] = sanitize_string(data['photo_filename'], max_length=255)

    try:
        new_service = Service(**data)
        db.session.add(new_service)
        db.session.commit()
        logging.info(f"Service created: {new_service.service_id}")
        return jsonify(new_service.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating service: {str(e)}")
        return jsonify({"error": "Failed to create service", "message": str(e)}), 500


@services_bp.route("/services/<int:service_id>", methods=["PUT", "PATCH"])
@limiter.limit("100 per hour")
@require_api_key
def update_service(service_id):
    """Update a service by ID"""
    service = Service.query.get(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        for key, value in data.items():
            if hasattr(service, key) and value is not None:
                setattr(service, key, value)

        db.session.commit()
        logging.info(f"Service updated: {service_id}")
        return jsonify(service.to_dict())
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating service {service_id}: {str(e)}")
        return jsonify({"error": "Failed to update service", "message": str(e)}), 500


@services_bp.route("/services/<int:service_id>", methods=["DELETE"])
@limiter.limit("50 per hour")
@require_api_key
def delete_service(service_id):
    """Delete a service by ID"""
    service = Service.query.get(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    try:
        db.session.delete(service)
        db.session.commit()
        logging.info(f"Service deleted: {service_id}")
        return jsonify({"message": "Service deleted successfully"})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting service {service_id}: {str(e)}")
        return jsonify({"error": "Failed to delete service", "message": str(e)}), 500
