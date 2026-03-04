# RD Motors API

A comprehensive REST API for managing RD Motors services, inventory, clients, and AutoUSA operations.

## 🚀 Features

- **RESTful API** with comprehensive CRUD operations
- **Authentication** via API key
- **Rate Limiting** to prevent abuse
- **Input Sanitization** for security
- **Pagination** on all list endpoints
- **Comprehensive Testing** with pytest
- **API Documentation** via Swagger/OpenAPI
- **Database Connection Pooling** for performance
- **Security Headers** for protection

## 📋 Requirements

- Python 3.8+
- MySQL 5.7+ or MariaDB 10.3+
- pip

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rdmotorsAPi
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r rdmotorsAPI/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure database**
   - Create MySQL database
   - Update `.env` with database credentials

6. **Run migrations** (if needed)
   ```bash
   python rdmotorsAPI/server.py
   # Database tables will be created automatically
   ```

## 🏃 Running the Application

### Development Mode
```bash
python rdmotorsAPI/server.py
```

### Production Mode (using Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 rdmotorsAPI.server:app
```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:5000/docs/`
- **ReDoc**: `http://localhost:5000/docs/` (alternative view)

## 🔐 Authentication

Protected CRUD endpoints now use Firebase session cookies (`httpOnly`) via backend session login.

- `POST /sessionLogin` (alias: `POST /api/login`) accepts Firebase `idToken` and sets:
  - `__session` cookie (`httpOnly`, default 5 days)
  - `csrfToken` cookie
- `POST /sessionLogout` (alias: `POST /api/logout`) clears cookies and can optionally revoke Firebase refresh tokens (`{"revoke": true}`)

Legacy API key authentication is still supported as a fallback for backward compatibility.

## 📡 API Endpoints

### Services
- `GET /services` - List all services (paginated)
- `GET /services/<id>` - Get service by ID
- `POST /services` - Create new service
- `PUT/PATCH /services/<id>` - Update service
- `DELETE /services/<id>` - Delete service

### AutoUSA
- `GET /autousa` - List all autos (paginated)
- `GET /autousa/id/<id>` - Get auto by ID
- `GET /autousa/vin/<vin>` - Get auto by VIN
- `POST /autousa` - Create new auto
- `PUT/PATCH /autousa/id/<id>` - Update auto by ID
- `PUT/PATCH /autousa/vin/<vin>` - Update or create auto by VIN
- `DELETE /autousa/id/<id>` - Delete auto by ID
- `DELETE /autousa/vin/<vin>` - Delete auto by VIN
- `GET /autousa/vin/<vin>/history` - Get auto history
- `POST /autousa/<vin>/upload` - Upload photos (ZIP file)
- `GET /autousa/<vin>/photos` - Get auto photos

### Cars
- `GET /cars` - List all cars (paginated)
- `GET /cars/<id>` - Get car by ID
- `POST /cars` - Create new car
- `PUT/PATCH /cars/<id>` - Update car
- `DELETE /cars/<id>` - Delete car

### Clients
- `GET /clients` - List all clients (paginated)
- `GET /clients/<id>` - Get client by ID
- `POST /clients` - Create new client
- `PUT/PATCH /clients/<id>` - Update client
- `DELETE /clients/<id>` - Delete client

### Locations
- `GET /locations` - List all locations
- `GET /locations/id/<id>` - Get location by ID

### Health Check
- `GET /health` - Check API health status

### Session Auth
- `POST /sessionLogin` - Exchange Firebase ID token for session cookie
- `POST /sessionLogout` - Clear session cookies (optional token revocation)

## 🧪 Testing

Run tests with pytest:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rdmotorsAPI --cov-report=html

# Run specific test file
pytest tests/test_services.py

# Run with verbose output
pytest -v
```

Test coverage report will be generated in `htmlcov/index.html`

## 🔒 Security Features

- **Rate Limiting**: Prevents API abuse
  - GET endpoints: 100 requests/hour
  - POST/PUT/DELETE: 50 requests/hour
  - File uploads: 20 requests/hour

- **Input Sanitization**: All string inputs are sanitized to prevent XSS attacks

- **Security Headers**: 
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security
  - Content-Security-Policy

- **API Key Authentication**: Required for all protected endpoints

## 📊 Rate Limits

| Endpoint Type | Limit |
|--------------|-------|
| GET requests | 100/hour |
| POST/PUT/PATCH | 50/hour |
| DELETE | 50/hour |
| File uploads | 20/hour |

## 🗂️ Project Structure

```
rdmotorsAPI/
├── __init__.py          # App factory
├── server.py            # Main entry point
├── config.py            # Configuration
├── models.py            # Database models
├── utils.py             # Utility functions
├── auth.py              # Authentication
├── api_docs.py          # API documentation
├── routes/              # Route blueprints
│   ├── services.py
│   ├── autousa.py
│   ├── cars.py
│   ├── clients.py
│   └── locations.py
└── requirements.txt

tests/
├── conftest.py          # Test fixtures
├── test_models.py
├── test_services.py
├── test_autousa.py
├── test_auth.py
└── test_utils.py
```

## 🔧 Configuration

Key configuration options in `.env`:

```env
# Database
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=rdmotors

# API
API_KEY=your_secret_key
BASE_URL=https://rdmotors.com.ua

# CORS
CORS_ORIGINS=https://your-frontend-domain.com
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=None

# Firebase Admin
FIREBASE_SERVICE_ACCOUNT_PATH=/absolute/path/to/firebase-service-account.json
# or
# FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
# or (separate fields)
# FIREBASE_PROJECT_ID=...
# FIREBASE_PRIVATE_KEY_ID=...
# FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
# FIREBASE_CLIENT_EMAIL=...
# FIREBASE_CLIENT_ID=...

# File Storage
PHOTOS_AUTO_DIR=/var/www/rdmotorsAPI/static/photos/autousa

# Rate Limiting
RATELIMIT_ENABLED=true
```

## 📝 Example Requests

### Create a Service
```bash
curl -X POST http://localhost:5000/services \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Oil Change",
    "descr": "Full synthetic oil change",
    "price": 49.99,
    "currency": "USD",
    "photo_filename": "oil_change.jpg"
  }'
```

### Get Services with Pagination
```bash
curl -X GET "http://localhost:5000/services?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Create AutoUSA
```bash
curl -X POST http://localhost:5000/autousa \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "1HGBH41JXMN109186",
    "mark": "Honda",
    "model": "Civic",
    "container_number": "CONT123"
  }'
```

## 🐛 Troubleshooting

### Database Connection Issues
- Verify database credentials in `.env`
- Ensure MySQL server is running
- Check network connectivity

### Rate Limit Errors
- Check rate limit headers in response
- Wait for rate limit window to reset
- Consider increasing limits in production

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r rdmotorsAPI/requirements.txt`
- Check Python version (3.8+)

## 📈 Performance

- **Connection Pooling**: Configured for optimal database performance
- **Pagination**: All list endpoints support pagination
- **Indexing**: Database indexes on frequently queried fields

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

[Your License Here]

## 👥 Authors

[Your Name/Team]

## 🙏 Acknowledgments

- Flask framework
- SQLAlchemy ORM
- Flask-RESTX for API documentation
- All contributors

---

For more information, see the [API Documentation](http://localhost:5000/docs/) when the server is running.
