"""Cars routes blueprint"""
from flask import Blueprint, jsonify, request
from rdmotorsAPI.models import Car, db
from rdmotorsAPI.auth import require_api_key
from rdmotorsAPI.utils import get_pagination_params
import logging

cars_bp = Blueprint('cars', __name__)


@cars_bp.route("/cars", methods=["GET"])
@require_api_key
def get_cars():
    """Get all cars with optional pagination"""
    page, per_page = get_pagination_params()
    pagination = Car.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "data": [car.to_dict() for car in pagination.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    })


@cars_bp.route("/cars/<int:car_id>", methods=["GET"])
@require_api_key
def get_car_by_id(car_id):
    """Get car by ID"""
    car = Car.query.get(car_id)
    if car:
        return jsonify(car.to_dict())
    return jsonify({"error": "Car not found"}), 404


@cars_bp.route("/cars", methods=["POST"])
@require_api_key
def add_car():
    """Create a new car"""
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        new_car = Car(**data)
        db.session.add(new_car)
        db.session.commit()
        logging.info(f"Car created: {new_car.car_id}")
        return jsonify(new_car.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating car: {str(e)}")
        return jsonify({"error": "Failed to create car", "message": str(e)}), 500


@cars_bp.route("/cars/<int:car_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_car(car_id):
    """Update a car by ID"""
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        for key, value in data.items():
            if hasattr(car, key) and value is not None:
                setattr(car, key, value)

        db.session.commit()
        logging.info(f"Car updated: {car_id}")
        return jsonify(car.to_dict())
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating car {car_id}: {str(e)}")
        return jsonify({"error": "Failed to update car", "message": str(e)}), 500


@cars_bp.route("/cars/<int:car_id>", methods=["DELETE"])
@require_api_key
def delete_car(car_id):
    """Delete a car by ID"""
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    try:
        db.session.delete(car)
        db.session.commit()
        logging.info(f"Car deleted: {car_id}")
        return jsonify({"message": "Car deleted successfully"})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting car {car_id}: {str(e)}")
        return jsonify({"error": "Failed to delete car", "message": str(e)}), 500
