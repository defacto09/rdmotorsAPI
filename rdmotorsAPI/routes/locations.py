"""Locations routes blueprint"""
from flask import Blueprint, jsonify
from rdmotorsAPI.models import Location
from rdmotorsAPI.auth import require_api_key

locations_bp = Blueprint('locations', __name__)


@locations_bp.route("/locations", methods=["GET"])
def get_locations():
    """Get all locations"""
    locations = Location.query.all()
    return jsonify([loc.to_dict() for loc in locations])


@locations_bp.route("/locations/id/<int:location_id>", methods=["GET"])
@require_api_key
def get_location_by_id(location_id):
    """Get location by ID"""
    location = Location.query.get(location_id)
    if location:
        return jsonify(location.to_dict())
    return jsonify({"error": "Location not found"}), 404
