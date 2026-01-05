"""Clients routes blueprint"""
from flask import Blueprint, jsonify, request
from rdmotorsAPI.models import Client, db
from rdmotorsAPI.auth import require_api_key
from rdmotorsAPI.utils import get_pagination_params, sanitize_string, sanitize_email
from rdmotorsAPI import limiter  # noqa: E402
import logging

clients_bp = Blueprint('clients', __name__)


@clients_bp.route("/clients", methods=["GET"])
@limiter.limit("100 per hour")
@require_api_key
def get_clients():
    """Get all clients with optional pagination"""
    page, per_page = get_pagination_params()
    pagination = Client.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "data": [client.to_dict() for client in pagination.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    })


@clients_bp.route("/clients/<int:client_id>", methods=["GET"])
@require_api_key
def get_client(client_id):
    """Get client by ID"""
    client = Client.query.get(client_id)
    if client:
        return jsonify(client.to_dict())
    return jsonify({"error": "Client not found"}), 404


@clients_bp.route("/clients", methods=["POST"])
@limiter.limit("50 per hour")
@require_api_key
def add_client():
    """Create a new client"""
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Sanitize inputs
    if 'email' in data:
        data['email'] = sanitize_email(data['email'])
        if not data['email']:
            return jsonify({"error": "Invalid email format"}), 400
    
    if 'login' in data:
        data['login'] = sanitize_string(data['login'], max_length=20)
    if 'number' in data:
        data['number'] = sanitize_string(data['number'], max_length=20)
    if 'status' in data:
        data['status'] = sanitize_string(data['status'], max_length=20)

    if Client.query.filter_by(email=data.get("email")).first():
        return jsonify({"error": "Email already exists"}), 400

    try:
        new_client = Client(**data)
        db.session.add(new_client)
        db.session.commit()
        logging.info(f"Client created: {new_client.client_id}")
        return jsonify(new_client.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating client: {str(e)}")
        return jsonify({"error": "Failed to create client", "message": str(e)}), 500


@clients_bp.route("/clients/<int:client_id>", methods=["PUT", "PATCH"])
@limiter.limit("100 per hour")
@require_api_key
def update_client(client_id):
    """Update a client by ID"""
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Sanitize inputs
    if "email" in data:
        data["email"] = sanitize_email(data["email"])
        if not data["email"]:
            return jsonify({"error": "Invalid email format"}), 400
        if data["email"] != client.email:
            if Client.query.filter_by(email=data["email"]).first():
                return jsonify({"error": "Email already exists"}), 400
    
    if "login" in data:
        data["login"] = sanitize_string(data["login"], max_length=20)
    if "number" in data:
        data["number"] = sanitize_string(data["number"], max_length=20)
    if "status" in data:
        data["status"] = sanitize_string(data["status"], max_length=20)

    try:
        for key, value in data.items():
            if hasattr(client, key) and value is not None:
                setattr(client, key, value)

        db.session.commit()
        logging.info(f"Client updated: {client_id}")
        return jsonify(client.to_dict())
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating client {client_id}: {str(e)}")
        return jsonify({"error": "Failed to update client", "message": str(e)}), 500


@clients_bp.route("/clients/<int:client_id>", methods=["DELETE"])
@limiter.limit("50 per hour")
@require_api_key
def delete_client(client_id):
    """Delete a client by ID"""
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    try:
        db.session.delete(client)
        db.session.commit()
        logging.info(f"Client deleted: {client_id}")
        return jsonify({"message": "Client deleted successfully"})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting client {client_id}: {str(e)}")
        return jsonify({"error": "Failed to delete client", "message": str(e)}), 500
