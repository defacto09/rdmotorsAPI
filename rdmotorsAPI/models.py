"""Database models for the API"""
# db is imported from __init__.py after it's created
# This avoids circular imports - models are imported after db initialization
from rdmotorsAPI.utils import get_photo_url

# Import will work because __init__.py imports models after creating db
from rdmotorsAPI import db  # noqa: E402


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
        back_populates="autousa"
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


class AutoUsaHistory(db.Model):
    __tablename__ = "autousa_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    autousa_id = db.Column(db.Integer, db.ForeignKey("autousa.id", ondelete="CASCADE"), nullable=False)
    loc_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)
    arrival_date = db.Column(db.Date, nullable=True)
    departure_date = db.Column(db.Date, nullable=True)

    autousa = db.relationship("AutoUsa", back_populates="history")
    location = db.relationship("Location", foreign_keys=[loc_id])


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
    photo_url = db.Column(db.String(255), nullable=False)

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
            "quality": self.quality,
            "photo_url": self.photo_url
        }
