from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Qndr1%40n4@localhost/rdmotorsdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Clients
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

class Service(db.Model):
    __tablename__ = "services"
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    descr = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)

    def to_dict(self):
        return {
            "service_id": self.service_id,
            "name": self.name,
            "descr": self.descr,
            "price": float(self.price),
            "currency": self.currency
        }

# Imported USA cars
class AutoUsa(db.Model):
    __tablename__ = "autousa"
    vin = db.Column(db.String(17), primary_key=True)
    container_number = db.Column(db.String(30))
    mark = db.Column(db.String(30), nullable=False)
    model = db.Column(db.String(40), nullable=False)
    loc_now = db.Column(db.String(120))
    loc_next = db.Column(db.String(120))

    def to_dict(self):
        return {
            "vin": self.vin,
            "container_number": self.container_number,
            "mark": self.mark,
            "model": self.model,
            "loc_now": self.loc_now,
            "loc_next": self.loc_next
        }

# Inventory cars
class Car(db.Model):
    __tablename__ = "cars"
    car_id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.String(30), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    addi = db.Column(db.String(200))

    def to_dict(self):
        return {
            "car_id": self.car_id,
            "mark": self.mark,
            "model": self.model,
            "year": self.year,
            "addi": self.addi
        }

# Home
@app.route("/")
def home():
    return "RD Motors API is running!"

# Routes Auto/Cars
@app.route("/autousa", methods=["GET"])
def get_autousa():
    cars = AutoUsa.query.all()
    return jsonify([car.to_dict() for car in cars])

@app.route("/autousa/<vin>", methods=["GET"])
def get_autousa_by_vin(vin):
    car = AutoUsa.query.get(vin)
    if car:
        return jsonify(car.to_dict())
    return jsonify({"error": "Auto not found"}), 404

@app.route("/autousa", methods=["POST"])
def add_autousa():
    data = request.json
    if AutoUsa.query.get(data["vin"]):
        return jsonify({"error": "VIN already exists"}), 400
    new_car = AutoUsa(
        vin=data["vin"],
        container_number=data.get("container_number"),
        mark=data["mark"],
        model=data["model"],
        loc_now=data.get("loc_now"),
        loc_next=data.get("loc_next")
    )
    db.session.add(new_car)
    db.session.commit()
    return jsonify(new_car.to_dict()), 201

@app.route("/autousa/<vin>", methods=["PUT"])
def update_autousa(vin):
    car = AutoUsa.query.get(vin)
    if not car:
        return jsonify({"error": "Auto not found"}), 404
    data = request.json
    car.container_number = data.get("container_number", car.container_number)
    car.mark = data.get("mark", car.mark)
    car.model = data.get("model", car.model)
    car.loc_now = data.get("loc_now", car.loc_now)
    car.loc_next = data.get("loc_next", car.loc_next)
    db.session.commit()
    return jsonify(car.to_dict())

@app.route("/autousa/<vin>", methods=["DELETE"])
def delete_autousa(vin):
    car = AutoUsa.query.get(vin)
    if not car:
        return jsonify({"error": "Auto not found"}), 404
    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Auto deleted successfully"})

@app.route("/cars", methods=["GET"])
def get_cars():
    cars = Car.query.all()
    return jsonify([car.to_dict() for car in cars])

@app.route("/cars/<int:car_id>", methods=["GET"])
def get_car_by_id(car_id):
    car = Car.query.get(car_id)
    if car:
        return jsonify(car.to_dict())
    return jsonify({"error": "Car not found"}), 404

@app.route("/cars", methods=["POST"])
def add_car():
    data = request.json
    new_car = Car(
        mark=data["mark"],
        model=data["model"],
        year=data["year"],
        addi=data.get("addi")
    )
    db.session.add(new_car)
    db.session.commit()
    return jsonify(new_car.to_dict()), 201

@app.route("/cars/<int:car_id>", methods=["PUT"])
def update_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    data = request.json
    car.mark = data.get("mark", car.mark)
    car.model = data.get("model", car.model)
    car.year = data.get("year", car.year)
    car.addi = data.get("addi", car.addi)
    db.session.commit()
    return jsonify(car.to_dict())

@app.route("/cars/<int:car_id>", methods=["DELETE"])
def delete_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Car deleted successfully"})

# Routes clients

@app.route("/clients", methods=["GET"])
def get_clientsa():
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

@app.route("/clients/<int:client_id>", methods = ["GET"])
def get_clientss(client_id):
    client = Client.query.get(client_id)
    if client:
        return jsonify(client.to_dict())
    return jsonify({"error": "Client not found"}), 404

@app.route("/clients", methods=["POST"])
def add_client():
    data = request.json
    required_fields = ["login", "email", "number", "status"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    if Client.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400
    new_client = Client(
        login=data["login"],
        email=data["email"],
        number=data["number"],
        status=data["status"]
    )

    db.session.add(new_client)
    db.session.commit()
    return jsonify(new_client.to_dict()), 201

# Update an existing client
@app.route("/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    data = request.json
    client.login = data.get("login", client.login)
    client.email = data.get("email", client.email)
    client.number = data.get("number", client.number)
    client.status = data.get("status", client.status)
    db.session.commit()
    return jsonify(client.to_dict())

# Delete a client
@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Client deleted sucessfully"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
