"""API Documentation using Flask-RESTX"""
from flask_restx import Api, Resource, fields, Namespace
from rdmotorsAPI import limiter

# Create API documentation
api = Api(
    title='RD Motors API',
    version='1.0',
    description='API for managing RD Motors services, cars, clients, and AutoUSA inventory',
    doc='/docs/',
    prefix='/api/v1'
)

# Define namespaces
services_ns = Namespace('services', description='Service operations')
autousa_ns = Namespace('autousa', description='AutoUSA operations')
cars_ns = Namespace('cars', description='Car operations')
clients_ns = Namespace('clients', description='Client operations')
locations_ns = Namespace('locations', description='Location operations')

# Service models
service_model = api.model('Service', {
    'service_id': fields.Integer(readonly=True, description='Service ID'),
    'name': fields.String(required=True, description='Service name', max_length=100),
    'descr': fields.String(required=True, description='Service description', max_length=500),
    'price': fields.Float(required=True, description='Service price'),
    'currency': fields.String(required=True, description='Currency code', max_length=3),
    'photo_filename': fields.String(required=True, description='Photo filename', max_length=255),
    'url': fields.String(readonly=True, description='Photo URL')
})

service_pagination = api.model('ServicePagination', {
    'data': fields.List(fields.Nested(service_model)),
    'pagination': fields.Nested(api.model('Pagination', {
        'page': fields.Integer,
        'per_page': fields.Integer,
        'total': fields.Integer,
        'pages': fields.Integer
    }))
})

# AutoUSA models
autousa_model = api.model('AutoUSA', {
    'id': fields.Integer(readonly=True, description='Auto ID'),
    'vin': fields.String(required=True, description='Vehicle Identification Number', max_length=17),
    'container_number': fields.String(description='Container number', max_length=30),
    'mark': fields.String(description='Car make', max_length=30),
    'model': fields.String(description='Car model', max_length=40),
    'loc_now': fields.String(readonly=True, description='Current location'),
    'loc_next': fields.String(readonly=True, description='Next location'),
    'arrival_date': fields.String(description='Arrival date (YYYY-MM-DD)'),
    'departure_date': fields.String(description='Departure date (YYYY-MM-DD)')
})

# Client models
client_model = api.model('Client', {
    'client_id': fields.Integer(readonly=True, description='Client ID'),
    'login': fields.String(required=True, description='Client login', max_length=20),
    'email': fields.String(required=True, description='Client email', max_length=50),
    'number': fields.String(required=True, description='Phone number', max_length=20),
    'status': fields.String(required=True, description='Client status', max_length=20)
})

# Car models
car_model = api.model('Car', {
    'car_id': fields.Integer(readonly=True, description='Car ID'),
    'mark': fields.String(required=True, description='Car make', max_length=30),
    'model': fields.String(required=True, description='Car model', max_length=50),
    'year': fields.Integer(required=True, description='Manufacturing year'),
    'addi': fields.String(required=True, description='Additional info', max_length=200),
    'transmission': fields.String(required=True, description='Transmission type', max_length=30),
    'mileage': fields.Integer(required=True, description='Mileage'),
    'fuel_type': fields.String(required=True, description='Fuel type', max_length=30),
    'price': fields.Float(required=True, description='Price'),
    'discount': fields.Float(required=True, description='Discount'),
    'quality': fields.Integer(required=True, description='Quality rating'),
    'engine': fields.String(required=True, description='Engine info'),
    'photo_url': fields.String(required=True, description='Photo URL', max_length=255)
})

# Location models
location_model = api.model('Location', {
    'location_id': fields.Integer(readonly=True, description='Location ID'),
    'country': fields.String(description='Country', max_length=50),
    'description': fields.String(description='Location description', max_length=255)
})

# Error models
error_model = api.model('Error', {
    'error': fields.String(description='Error type'),
    'message': fields.String(description='Error message')
})

# Register namespaces
api.add_namespace(services_ns)
api.add_namespace(autousa_ns)
api.add_namespace(cars_ns)
api.add_namespace(clients_ns)
api.add_namespace(locations_ns)
