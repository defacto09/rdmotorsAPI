from functools import wraps
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask import url_for
from urllib.parse import quote_plus
from flask import Flask, send_from_directory
from datetime import datetime
import pathlib
import logging

# Завантаження секретів
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], resources={r"/*": {"origins": "*"}})


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(BASE_DIR, "static", "photos", "services")
PHOTOS_AUTO_DIR = "/var/www/rdmotorsAPI/static/photos/autousa"
os.makedirs(PHOTOS_AUTO_DIR, exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("autousa_photos.log"),
        logging.StreamHandler()
    ]
)

@app.route('/photos/services/<path:filename>')
def serve_photo(filename):
    resp = make_response(send_from_directory(PHOTOS_DIR, filename))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def serve_spa(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        from flask import make_response
        resp = make_response('', 204)  # Відповідь 204 No Content
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return resp

def get_photo_url(filename):
    return f"https://rdmotors.com.ua/photos/services/{filename}"

# Параметри бази даних
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
API_KEY = os.getenv("API_KEY")

db_password_escaped = quote_plus(db_password)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password_escaped}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB
app.config['PREFERRED_URL_SCHEME'] = 'https'


db = SQLAlchemy(app)

from werkzeug.exceptions import HTTPException
import traceback

def get_service_photo_url(filename):
    if not filename:
        return None
    return f"https://rdmotors.com.ua/static/photos/services/{filename}"

def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None

def normalize_int(value):
    if value in [None, "", " "]:
        return None
    try:
        return int(value)
    except ValueError:
        return None

# -------------------
# 🌍 Global error handler
# -------------------
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.name, "description": e.description, "code": e.code}), e.code

    logging.error(
        f"Exception occurred at {request.method} {request.path}",
        exc_info=e
    )
    return jsonify({"error": "Internal Server Error"}), 500

# -------------------
# 🔑 API KEY middleware
# -------------------
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("Authorization")
        if not key or key != f"Bearer {API_KEY}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.before_request
def validate_json():
    if request.endpoint == 'upload_auto_photos':
        return
    if request.method in ['POST', 'PUT', 'PATCH']:
        if not request.is_json and request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 400

# -------------------
# 📦 Models
# -------------------
class Service(db.Model):
    __tablename__ = "services"
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    descr = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    photo_filename = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "service_id": self.service_id,
            "name": self.name,
            "descr": self.descr,
            "price": float(self.price),
            "currency": self.currency,
            "url": get_photo_url(self.photo_filename) if self.photo_filename else None
        }
@app.route("/services", methods=["GET"])
@require_api_key
def get_services():
    services = Service.query.all()
    return jsonify([service.to_dict() for service in services])

@app.route("/services/<int:service_id>", methods=["GET"])
@require_api_key
def get_service_by_id(service_id):
    service = Service.query.get(service_id)
    if service:
        return jsonify(service.to_dict())
    return jsonify({"error": "Service not found"}), 404

@app.route("/services", methods=["POST"])
@require_api_key
def add_service():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    new_service = Service(**data)
    db.session.add(new_service)
    db.session.commit()
    return jsonify(new_service.to_dict()), 201

@app.route("/services/<int:service_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_service(service_id):
    service = Service.query.get(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    for key, value in data.items():
        if hasattr(service, key) and value is not None:
            setattr(service, key, value)

    db.session.commit()
    return jsonify(service.to_dict())

@app.route("/services/<int:service_id>", methods=["DELETE"])
@require_api_key
def delete_service(service_id):
    service = Service.query.get(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": "Service deleted successfully"})

#
# AUTO USA
#

class AutoUsa(db.Model):
    __tablename__ = "autousa"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    container_number = db.Column(db.String(30), nullable=True)
    mark = db.Column(db.String(30), nullable=True)
    model = db.Column(db.String(40), nullable=True)

    loc_now_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=True)
    loc_next_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=True)
    arrival_date = db.Column(db.Date, nullable=True)
    departure_date = db.Column(db.Date, nullable=True)

    loc_now = db.relationship("Location", foreign_keys=[loc_now_id])
    loc_next = db.relationship("Location", foreign_keys=[loc_next_id])

    history = db.relationship(
        "AutoUsaHistory",
        cascade="all, delete-orphan",
        back_populates="autousa"  # замість backref
    )

    def to_dict(self):
        return {
            "id": self.id,
            "vin": self.vin,
            "container_number": self.container_number or "",
            "mark": self.mark,
            "model": self.model,
            "loc_now": f"{self.loc_now.country} - {self.loc_now.description}" if self.loc_now else "",
            "loc_next": f"{self.loc_next.country} - {self.loc_next.description}" if self.loc_next else "",
            "arrival_date": str(self.arrival_date) if self.arrival_date else "",
            "departure_date": str(self.departure_date) if self.departure_date else ""
        }

class Location(db.Model):
    __tablename__ = "locations"
    location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(50))
    description = db.Column(db.String(255))

    def to_dict(self):
        return {
            "location_id": self.location_id,
            "country": self.country,
            "description": self.description
        }
@app.route("/locations", methods=["GET"])
def get_locations():
    locations = Location.query.all()
    return jsonify([loc.to_dict() for loc in locations])

@app.route("/locations/id/<int:location_id>", methods=["GET"])
@require_api_key
def get_location_by_id(location_id):
    location = Location.query.get(location_id)
    if location:
        return jsonify(location.to_dict())
    return jsonify({"error": "Location not found"}), 404


class AutoUsaHistory(db.Model):
    __tablename__ = "autousa_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    autousa_id = db.Column(db.Integer, db.ForeignKey("autousa.id", ondelete="CASCADE"), nullable=False)
    loc_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)
    arrival_date = db.Column(db.Date, nullable=True)
    departure_date = db.Column(db.Date, nullable=True)

    autousa = db.relationship("AutoUsa", back_populates="history")
    location = db.relationship("Location", foreign_keys=[loc_id])


@app.route("/autousa/id/<int:car_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_autousa_by_id(car_id):
    car = AutoUsa.query.get(car_id)
    if not car:
        return jsonify({"error": "Auto not found"}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

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
    for key in ["vin", "container_number", "mark", "model"]:
        if key in data and data[key] is not None:
            setattr(car, key, data[key])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Commit failed: {str(e)}"}), 500

    return jsonify(car.to_dict())

@app.route("/autousa/vin/<string:vin>", methods=["GET"])
@require_api_key
def get_autousa_by_vin(vin):
    car = AutoUsa.query.filter_by(vin=vin).first()
    if not car:
        return jsonify({"error": "Auto not found"}), 404

    return jsonify(car.to_dict()), 200

@app.route("/autousa/vin/<string:vin>", methods=["PUT", "PATCH"])
@require_api_key
def upsert_autousa_by_vin(vin):

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

        db.session.commit()
        return jsonify(car.to_dict()), 200

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

        new_car = AutoUsa(**car_data)
        db.session.add(new_car)
        db.session.commit()
        return jsonify(new_car.to_dict()), 201


@app.route("/autousa/vin/<string:vin>/history", methods=["GET"])
@require_api_key
def get_autousa_history_by_vin(vin):
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

@app.route("/autousa/vin/<string:vin>", methods=["DELETE"])
@require_api_key
def delete_autousa_by_vin(vin):
    """
    Видалити авто по VIN.
    """
    car = AutoUsa.query.filter_by(vin=vin).first()
    if not car:
        return jsonify({"error": "Auto not found"}), 404

    vin_folder = os.path.join(PHOTOS_AUTO_DIR, vin)
    if os.path.exists(vin_folder):
        try:
            shutil.rmtree(vin_folder)
            print(f"✅ Deleted photos for {vin}")
        except Exception as e:
            return jsonify({"error": f"Failed to delete photos: {str(e)}"}), 500

    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Auto deleted successfully"}), 200

@app.route("/autousa", methods=["GET"])
@require_api_key
def get_autousa():
    cars = AutoUsa.query.all()
    return jsonify([car.to_dict() for car in cars])

@app.route("/autousa/id/<int:car_id>", methods=["GET"])
@require_api_key
def get_autousa_by_id(car_id):
    car = AutoUsa.query.get(car_id)
    if car:
        return jsonify(car.to_dict())
    return jsonify({"error": "Auto not found"}), 404

@app.route("/autousa/id/<int:car_id>", methods=["DELETE"])
@require_api_key
def delete_autousa_by_id(car_id):
    car = AutoUsa.query.get(car_id)
    if not car:
        return jsonify({"error": "Auto not found"}), 404
    AutoUsaHistory.query.filter_by(autousa_id=car.id).delete()
    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Auto deleted successfully"})

@app.route("/autousa", methods=["POST"])
@require_api_key
def add_autousa():
    data = request.get_json(force=True)
    if not data or "vin" not in data:
        return jsonify({"error": "Invalid JSON or missing VIN"}), 400

    if AutoUsa.query.filter_by(vin=data["vin"]).first():
        return jsonify({"error": "VIN already exists"}), 400

    car_data = {k: (v if v is not None else "") for k, v in data.items()}
    new_car = AutoUsa(**car_data)
    db.session.add(new_car)
    db.session.commit()
    return jsonify(new_car.to_dict()), 201

#
# CLIENT
#

class Client(db.Model):
    __tablename__ = "clients"
    client_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "login": self.login,
            "email": self.email,
            "number": self.number,
            "status": self.status
        }

class Car(db.Model):
    __tablename__ = "cars"
    car_id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.String(30), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    addi = db.Column(db.String(200), nullable=False)
    transmission = db.Column(db.String(30), nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    fuel_type = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    engine = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "car_id": self.car_id,
            "mark": self.mark,
            "model": self.model,
            "year": self.year,
            "addi": self.addi,
            "transmission": self.transmission,
            "mileage": self.mileage,
            "fuel_type": self.fuel_type,
            "price": float(self.price),
            "discount": float(self.discount),
            "engine": self.engine,
            "quality": self.quality
        }

# -------------------
# 🔹 CARS
# -------------------
@app.route("/cars", methods=["GET"])
@require_api_key
def get_cars():
    cars = Car.query.all()
    return jsonify([car.to_dict() for car in cars])

@app.route("/cars/<int:car_id>", methods=["GET"])
@require_api_key
def get_car_by_id(car_id):
    car = Car.query.get(car_id)
    if car:
        return jsonify(car.to_dict())
    return jsonify({"error": "Car not found"}), 404

@app.route("/cars", methods=["POST"])
@require_api_key
def add_car():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    new_car = Car(**data)
    db.session.add(new_car)
    db.session.commit()
    return jsonify(new_car.to_dict()), 201

@app.route("/cars/<int:car_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    for key, value in data.items():
        if hasattr(car, key) and value is not None:
            setattr(car, key, value)

    db.session.commit()
    return jsonify(car.to_dict())

@app.route("/cars/<int:car_id>", methods=["DELETE"])
@require_api_key
def delete_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Car deleted successfully"})

# -------------------
# 🔹 CLIENTS
# -------------------
@app.route("/clients", methods=["GET"])
@require_api_key
def get_clients():
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

@app.route("/clients/<int:client_id>", methods=["GET"])
@require_api_key
def get_client(client_id):
    client = Client.query.get(client_id)
    if client:
        return jsonify(client.to_dict())
    return jsonify({"error": "Client not found"}), 404

@app.route("/clients", methods=["POST"])
@require_api_key
def add_client():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    if Client.query.filter_by(email=data.get("email")).first():
        return jsonify({"error": "Email already exists"}), 400

    new_client = Client(**data)
    db.session.add(new_client)
    db.session.commit()
    return jsonify(new_client.to_dict()), 201

@app.route("/clients/<int:client_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    for key, value in data.items():
        if hasattr(client, key) and value is not None:
            setattr(client, key, value)

    db.session.commit()
    return jsonify(client.to_dict())

@app.route("/clients/<int:client_id>", methods=["DELETE"])
@require_api_key
def delete_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Client deleted successfully"})

#
# UPLOAD ZIP
#

from zipfile import ZipFile
import shutil
from werkzeug.utils import secure_filename
import os
import pathlib
from flask import request, jsonify

@app.route("/autousa/<string:vin>/upload", methods=["POST"])
@require_api_key
def upload_auto_photos(vin):
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
        return jsonify({"error": f'Failed to unzip: {str(e)}'}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify({'message': f"Photos uploaded successfully for VIN {vin}"}), 201

@app.route("/autousa/<string:vin>/photos", methods=["GET"])
def get_auto_photos(vin):
    vin_folder = os.path.join(PHOTOS_AUTO_DIR, vin)
    if not os.path.exists(vin_folder):
        return jsonify({"error": "No photos found for this VIN"}), 404

    files = []
    for f in sorted(os.listdir(vin_folder)):
        if f.startswith(".") or f == "DS_Store":
            continue
        files.append(f"https://rdmotors.com.ua/photos/autousa/{vin}/{f}")

    return jsonify({"vin": vin, "photos": files})
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)