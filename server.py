from functools import wraps
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Завантаження секретів
load_dotenv()

app = Flask(__name__)
CORS(app)

# Параметри бази даних
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
API_KEY = os.getenv("API_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Декоратор для перевірки API ключа
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("Authorization")
        if key != f"Bearer " + API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# Models
class Client(db.Model):
    __tablename__ = "clients"
    client_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {"client_id": self.client_id, "login": self.login, "email": self.email, "number": self.number, "status": self.status}

class Service(db.Model):
    __tablename__ = "services"
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    descr = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)

    def to_dict(self):
        return {"service_id": self.service_id, "name": self.name, "descr": self.descr, "price": float(self.price), "currency": self.currency}

class AutoUsa(db.Model):
    __tablename__ = "autousa"
    vin = db.Column(db.String(17), primary_key=True)
    container_number = db.Column(db.String(30))
    mark = db.Column(db.String(30), nullable=False)
    model = db.Column(db.String(40), nullable=False)
    loc_now = db.Column(db.String(120))
    loc_next = db.Column(db.String(120))

    def to_dict(self):
        return {"vin": self.vin, "container_number": self.container_number, "mark": self.mark, "model": self.model, "loc_now": self.loc_now, "loc_next": self.loc_next}

class Car(db.Model):
    __tablename__ = "cars"
    car_id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.String(30), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    addi = db.Column(db.String(200))

    def to_dict(self):
        return {"car_id": self.car_id, "mark": self.mark, "model": self.model, "year": self.year, "addi": self.addi}

# Routes
@app.route("/")
@require_api_key
def home():
    return "RD Motors API is running!"

@app.route("/autousa", methods=["GET"])
@require_api_key
def get_autousa():
    cars = AutoUsa.query.all()
    return jsonify([car.to_dict() for car in cars])

@app.route("/autousa/<vin>", methods=["GET"])
@require_api_key
def get_autousa_by_vin(vin):
    car = AutoUsa.query.get(vin)
    if car:
        return jsonify(car.to_dict())
    return jsonify({"error": "Auto not found"}), 404

@app.route("/autousa", methods=["POST"])
@require_api_key
def add_autousa():
    data = request.json
    if AutoUsa.query.get(data["vin"]):
        return jsonify({"error": "VIN already exists"}), 400
    new_car = AutoUsa(**data)
    db.session.add(new_car)
    db.session.commit()
    return jsonify(new_car.to_dict()), 201

@app.route("/autousa/<vin>", methods=["PUT"])
@require_api_key
def update_autousa(vin):
    car = AutoUsa.query.get(vin)
    if not car:
        return jsonify({"error": "Auto not found"}), 404
    data = request.json
    for key, value in data.items():
        setattr(car, key, value)
    db.session.commit()
    return jsonify(car.to_dict())

@app.route("/autousa/<vin>", methods=["DELETE"])
@require_api_key
def delete_autousa(vin):
    car = AutoUsa.query.get(vin)
    if not car:
        return jsonify({"error": "Auto not found"}), 404
    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Auto deleted successfully"})

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
    data = request.json
    new_car = Car(**data)
    db.session.add(new_car)
    db.session.commit()
    return jsonify(new_car.to_dict()), 201

@app.route("/cars/<int:car_id>", methods=["PUT"])
@require_api_key
def update_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    data = request.json
    for key, value in data.items():
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
    data = request.json
    if Client.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400
    new_client = Client(**data)
    db.session.add(new_client)
    db.session.commit()
    return jsonify(new_client.to_dict()), 201

@app.route("/clients/<int:client_id>", methods=["PUT"])
@require_api_key
def update_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    data = request.json
    for key, value in data.items():
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
