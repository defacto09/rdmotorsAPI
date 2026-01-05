"""AutoUSA routes blueprint"""
from flask import Blueprint, jsonify, request
from rdmotorsAPI.models import AutoUsa, AutoUsaHistory, db
from rdmotorsAPI.auth import require_api_key
from rdmotorsAPI.utils import get_pagination_params, validate_vin, parse_date, sanitize_string
from rdmotorsAPI.config import PHOTOS_AUTO_DIR, BASE_URL
from rdmotorsAPI import limiter  # noqa: E402
import os
import shutil
import pathlib
import logging
from zipfile import ZipFile
from werkzeug.utils import secure_filename

autousa_bp = Blueprint('autousa', __name__)


@autousa_bp.route("/autousa", methods=["GET"])
@limiter.limit("100 per hour")
@require_api_key
def get_autousa():
    """Get all autos with optional pagination"""
    page, per_page = get_pagination_params()
    pagination = AutoUsa.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "data": [car.to_dict() for car in pagination.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    })


@autousa_bp.route("/autousa/id/<int:car_id>", methods=["GET"])
@require_api_key
def get_autousa_by_id(car_id):
    """Get auto by ID"""
    car = AutoUsa.query.get(car_id)
    if car:
        return jsonify(car.to_dict())
    return jsonify({"error": "Auto not found"}), 404


@autousa_bp.route("/autousa/id/<int:car_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_autousa_by_id(car_id):
    """Update auto by ID"""
    car = AutoUsa.query.get(car_id)
    if not car:
        return jsonify({"error": "Auto not found"}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Validate VIN if being updated
    if "vin" in data and data["vin"]:
        if not validate_vin(data["vin"]):
            return jsonify({"error": "Invalid VIN format. VIN must be 17 alphanumeric characters"}), 400
        # Check if VIN already exists for another car
        existing = AutoUsa.query.filter_by(vin=data["vin"]).first()
        if existing and existing.id != car_id:
            return jsonify({"error": "VIN already exists"}), 400

    new_loc_now_id = data.get("loc_now_id")

    # Додаємо запис в історію лише якщо loc_now_id змінюється
    if new_loc_now_id is not None and new_loc_now_id != car.loc_now_id:
        if car.loc_now_id is not None:
            last_history = AutoUsaHistory(
                autousa_id=car.id,
                loc_id=car.loc_now_id,
                arrival_date=car.arrival_date,
                departure_date=car.departure_date
            )
            db.session.add(last_history)

        # Оновлюємо новий loc_now і дати
        car.loc_now_id = new_loc_now_id
        car.arrival_date = parse_date(data.get("arrival_date")) or car.arrival_date
        car.departure_date = parse_date(data.get("departure_date")) or car.departure_date

    # Оновлюємо loc_next_id, якщо є
    if "loc_next_id" in data:
        car.loc_next_id = data["loc_next_id"]

    # Інші поля
        # Sanitize string inputs
        for key in ["container_number", "mark", "model"]:
            if key in data and data[key] is not None:
                max_length = 40 if key == "model" else 30
                data[key] = sanitize_string(data[key], max_length=max_length)
                setattr(car, key, data[key])
        
        # VIN is validated separately, don't sanitize it
        if "vin" in data and data["vin"] is not None:
            setattr(car, "vin", data["vin"])

    try:
        db.session.commit()
        logging.info(f"Auto updated by ID: {car_id}")
        return jsonify(car.to_dict())
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating auto {car_id}: {str(e)}")
        return jsonify({"error": f"Commit failed: {str(e)}"}), 500


@autousa_bp.route("/autousa/id/<int:car_id>", methods=["DELETE"])
@require_api_key
def delete_autousa_by_id(car_id):
    """Delete auto by ID"""
    car = AutoUsa.query.get(car_id)
    if not car:
        return jsonify({"error": "Auto not found"}), 404
    
    vin = car.vin
    vin_folder = os.path.join(PHOTOS_AUTO_DIR, vin)
    if os.path.exists(vin_folder):
        try:
            shutil.rmtree(vin_folder)
            logging.info(f"Deleted photos for auto ID {car_id} (VIN: {vin})")
        except Exception as e:
            logging.error(f"Error deleting photos for auto ID {car_id}: {str(e)}")
    
    try:
        AutoUsaHistory.query.filter_by(autousa_id=car.id).delete()
        db.session.delete(car)
        db.session.commit()
        logging.info(f"Auto deleted by ID: {car_id}")
        return jsonify({"message": "Auto deleted successfully"})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting auto {car_id}: {str(e)}")
        return jsonify({"error": "Failed to delete auto", "message": str(e)}), 500


@autousa_bp.route("/autousa/vin/<string:vin>", methods=["GET"])
@require_api_key
def get_autousa_by_vin(vin):
    """Get auto by VIN"""
    if not validate_vin(vin):
        return jsonify({"error": "Invalid VIN format. VIN must be 17 alphanumeric characters"}), 400
    
    car = AutoUsa.query.filter_by(vin=vin).first()
    if not car:
        return jsonify({"error": "Auto not found"}), 404

    return jsonify(car.to_dict()), 200


@autousa_bp.route("/autousa/vin/<string:vin>", methods=["PUT", "PATCH"])
@require_api_key
def upsert_autousa_by_vin(vin):
    """Create or update auto by VIN"""
    if not validate_vin(vin):
        return jsonify({"error": "Invalid VIN format. VIN must be 17 alphanumeric characters"}), 400

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    car = AutoUsa.query.filter_by(vin=vin).first()

    if car:
        # 🔁 Якщо існує — оновлюємо
        new_loc_now_id = data.get("loc_now_id")

        # Історія переміщень, якщо loc_now_id змінюється
        if new_loc_now_id is not None and new_loc_now_id != car.loc_now_id:
            if car.loc_now_id is not None:
                db.session.add(AutoUsaHistory(
                    autousa_id=car.id,
                    loc_id=car.loc_now_id,
                    arrival_date=car.arrival_date,
                    departure_date=car.departure_date
                ))

            car.loc_now_id = new_loc_now_id
            car.arrival_date = parse_date(data.get("arrival_date")) or car.arrival_date
            car.departure_date = parse_date(data.get("departure_date")) or car.departure_date

        if "loc_next_id" in data:
            car.loc_next_id = data["loc_next_id"]

        for key in ["container_number", "mark", "model"]:
            if key in data and data[key] is not None:
                setattr(car, key, data[key])

        try:
            db.session.commit()
            logging.info(f"Auto updated by VIN: {vin}")
            return jsonify(car.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating auto by VIN {vin}: {str(e)}")
            return jsonify({"error": "Failed to update auto", "message": str(e)}), 500

    else:
        # 🆕 Якщо авто немає — створюємо новий запис
        car_data = {
            "vin": vin,
            "container_number": data.get("container_number"),
            "mark": data.get("mark"),
            "model": data.get("model"),
            "loc_now_id": data.get("loc_now_id"),
            "loc_next_id": data.get("loc_next_id"),
            "arrival_date": parse_date(data.get("arrival_date")),
            "departure_date": parse_date(data.get("departure_date"))
        }

        try:
            new_car = AutoUsa(**car_data)
            db.session.add(new_car)
            db.session.commit()
            logging.info(f"Auto created by VIN: {vin}")
            return jsonify(new_car.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating auto by VIN {vin}: {str(e)}")
            return jsonify({"error": "Failed to create auto", "message": str(e)}), 500


@autousa_bp.route("/autousa/vin/<string:vin>/history", methods=["GET"])
@require_api_key
def get_autousa_history_by_vin(vin):
    """Get auto history by VIN"""
    if not validate_vin(vin):
        return jsonify({"error": "Invalid VIN format. VIN must be 17 alphanumeric characters"}), 400
    
    car = AutoUsa.query.filter_by(vin=vin).first()
    if not car:
        return jsonify({"error": "Auto not found"}), 404

    history = []

    # Записи з історії
    for h in car.history:
        history.append({
            "loc_id": h.loc_id,
            "location_name": f"{h.location.country} - {h.location.description}" if h.location else "",
            "arrival_date": str(h.arrival_date) if h.arrival_date else "",
            "departure_date": str(h.departure_date) if h.departure_date else ""
        })

    # Поточна локація
    if car.loc_now_id:
        history.append({
            "loc_id": car.loc_now_id,
            "location_name": f"{car.loc_now.country} - {car.loc_now.description}" if car.loc_now else "",
            "arrival_date": str(car.arrival_date) if car.arrival_date else "",
            "departure_date": str(car.departure_date) if car.departure_date else None
        })

    # Сортування по arrival_date
    history.sort(key=lambda x: x["arrival_date"] or "9999-12-31")

    return jsonify(history)


@autousa_bp.route("/autousa/vin/<string:vin>", methods=["DELETE"])
@require_api_key
def delete_autousa_by_vin(vin):
    """Delete auto by VIN"""
    if not validate_vin(vin):
        return jsonify({"error": "Invalid VIN format. VIN must be 17 alphanumeric characters"}), 400
    
    car = AutoUsa.query.filter_by(vin=vin).first()
    if not car:
        return jsonify({"error": "Auto not found"}), 404

    vin_folder = os.path.join(PHOTOS_AUTO_DIR, vin)
    if os.path.exists(vin_folder):
        try:
            shutil.rmtree(vin_folder)
            logging.info(f"Deleted photos for VIN: {vin}")
        except Exception as e:
            logging.error(f"Error deleting photos for VIN {vin}: {str(e)}")
            return jsonify({"error": f"Failed to delete photos: {str(e)}"}), 500

    try:
        db.session.delete(car)
        db.session.commit()
        logging.info(f"Auto deleted by VIN: {vin}")
        return jsonify({"message": "Auto deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting auto by VIN {vin}: {str(e)}")
        return jsonify({"error": "Failed to delete auto", "message": str(e)}), 500


@autousa_bp.route("/autousa", methods=["POST"])
@require_api_key
def add_autousa():
    """Create a new auto"""
    data = request.get_json(force=True)
    if not data or "vin" not in data:
        return jsonify({"error": "Invalid JSON or missing VIN"}), 400

    vin = data["vin"]
    if not validate_vin(vin):
        return jsonify({"error": "Invalid VIN format. VIN must be 17 alphanumeric characters"}), 400

    if AutoUsa.query.filter_by(vin=vin).first():
        return jsonify({"error": "VIN already exists"}), 400

    try:
        car_data = {k: (v if v is not None else "") for k, v in data.items()}
        new_car = AutoUsa(**car_data)
        db.session.add(new_car)
        db.session.commit()
        logging.info(f"Auto created: {new_car.id} (VIN: {vin})")
        return jsonify(new_car.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating auto: {str(e)}")
        return jsonify({"error": "Failed to create auto", "message": str(e)}), 500


@autousa_bp.route("/autousa/<string:vin>/upload", methods=["POST"])
@limiter.limit("20 per hour")  # Lower limit for file uploads
@require_api_key
def upload_auto_photos(vin):
    """Upload photos for auto by VIN"""
    if not validate_vin(vin):
        return jsonify({"error": "Invalid VIN format. VIN must be 17 alphanumeric characters"}), 400
    
    car = AutoUsa.query.filter_by(vin=vin).first()
    if not car:
        return jsonify({"error": "Auto not found"}), 404

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if not file.filename.endswith('.zip'):
        return jsonify({"error": 'File must be a .zip'}), 400

    vin_folder = os.path.join(PHOTOS_AUTO_DIR, vin)
    os.makedirs(vin_folder, exist_ok=True)

    temp_path = os.path.join(vin_folder, 'temp.zip')
    file.save(temp_path)

    SKIP_NAMES = {"DS_Store"}
    allowed_ext = {'.jpg', '.jpeg', '.png'}

    try:
        with ZipFile(temp_path, 'r') as zip_ref:
            for zip_info in zip_ref.infolist():
                # Ігноруємо AppleDouble, __MACOSX і службові файли від macOS
                if ("__MACOSX" in zip_info.filename or
                    zip_info.filename.startswith("._")):
                    continue

                safe_name = secure_filename(pathlib.Path(zip_info.filename).name)
                if not safe_name or safe_name in SKIP_NAMES:
                    continue

                ext = pathlib.Path(safe_name).suffix.lower()
                if ext not in allowed_ext:
                    continue

                dest_path = os.path.join(vin_folder, safe_name)
                with zip_ref.open(zip_info) as source, open(dest_path, 'wb') as target:
                    shutil.copyfileobj(source, target)

    except Exception as e:
        logging.error(f"Error uploading photos for VIN {vin}: {str(e)}")
        return jsonify({"error": f'Failed to unzip: {str(e)}'}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    logging.info(f"Photos uploaded successfully for VIN: {vin}")
    return jsonify({'message': f"Photos uploaded successfully for VIN {vin}"}), 201


@autousa_bp.route("/autousa/<string:vin>/photos", methods=["GET"])
def get_auto_photos(vin):
    """Get photos for auto by VIN"""
    if not validate_vin(vin):
        return jsonify({"error": "Invalid VIN format. VIN must be 17 alphanumeric characters"}), 400
    
    vin_folder = os.path.join(PHOTOS_AUTO_DIR, vin)
    if not os.path.exists(vin_folder):
        return jsonify({"error": "No photos found for this VIN"}), 404

    files = []
    allowed_ext = {'.jpg', '.jpeg', '.png'}

    try:
        for f in sorted(os.listdir(vin_folder)):
            if f.startswith('.') or f == "DS_Store":
                continue

            ext = pathlib.Path(f).suffix.lower()
            if ext not in allowed_ext:
                continue

            files.append(f"{BASE_URL}/photos/autousa/{vin}/{f}")

        return jsonify({"vin": vin, "photos": files})
    except Exception as e:
        logging.error(f"Error reading photos for VIN {vin}: {str(e)}")
        return jsonify({"error": "Failed to read photos", "message": str(e)}), 500
