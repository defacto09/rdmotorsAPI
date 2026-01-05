# ✅ Server Deployment Checklist

## Before Uploading to Server

### 1. Code Fixes ✅
- [x] Fixed debug mode (now uses FLASK_DEBUG env var)
- [x] Fixed log file path (now uses LOG_DIR env var)
- [x] Fixed URL_SCHEME (defaults to https)
- [x] Created wsgi.py for production
- [x] Verified .env is in .gitignore

### 2. Environment Variables
Create `.env` file on server with:
```env
# Database
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=your_db_name

# API Security
API_KEY=your_strong_secret_key_here

# URLs
BASE_URL=https://rdmotors.com.ua
URL_SCHEME=https

# CORS (comma-separated, no spaces)
CORS_ORIGINS=https://rdmotors.com.ua,https://www.rdmotors.com.ua

# File Storage
PHOTOS_AUTO_DIR=/var/www/rdmotorsAPI/static/photos/autousa
LOG_DIR=/var/log/rdmotors

# Flask Settings
FLASK_DEBUG=false
ENABLE_API_DOCS=false

# Rate Limiting
RATELIMIT_ENABLED=true
RATELIMIT_STORAGE_URL=memory://
```

### 3. Server Setup Commands

```bash
# 1. Create directories
sudo mkdir -p /var/www/rdmotorsAPI/static/photos/autousa
sudo mkdir -p /var/www/rdmotorsAPI/static/photos/services
sudo mkdir -p /var/log/rdmotors
sudo chown -R www-data:www-data /var/www/rdmotorsAPI
sudo chown -R www-data:www-data /var/log/rdmotors

# 2. Create virtual environment
cd /var/www/rdmotorsAPI
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r rdmotorsAPI/requirements.txt

# 4. Create .env file
nano .env
# Paste environment variables above

# 5. Test import
python3 -c "from rdmotorsAPI import create_app; print('OK')"

# 6. Run with Gunicorn
gunicorn wsgi:application -w 4 -b 0.0.0.0:5000 \
  --access-logfile /var/log/rdmotors/access.log \
  --error-logfile /var/log/rdmotors/error.log
```

### 4. Systemd Service (Optional but Recommended)

Create `/etc/systemd/system/rdmotors.service`:
```ini
[Unit]
Description=RD Motors API
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/rdmotorsAPI
Environment="PATH=/var/www/rdmotorsAPI/venv/bin"
ExecStart=/var/www/rdmotorsAPI/venv/bin/gunicorn \
    wsgi:application \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --access-logfile /var/log/rdmotors/access.log \
    --error-logfile /var/log/rdmotors/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rdmotors
sudo systemctl start rdmotors
sudo systemctl status rdmotors
```

### 5. Nginx Configuration (If using reverse proxy)

```nginx
server {
    listen 80;
    server_name rdmotors.com.ua;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name rdmotors.com.ua;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /var/www/rdmotorsAPI/static/;
        expires 30d;
    }
}
```

## Post-Deployment Verification

- [ ] Health check: `curl https://rdmotors.com.ua/health`
- [ ] Test API endpoint: `curl -H "Authorization: Bearer YOUR_KEY" https://rdmotors.com.ua/services`
- [ ] Check logs: `tail -f /var/log/rdmotors/error.log`
- [ ] Verify database connection
- [ ] Test file upload functionality
- [ ] Check rate limiting works
- [ ] Verify CORS headers

## Rollback Plan

If something goes wrong:
```bash
# Stop service
sudo systemctl stop rdmotors

# Restore previous version
cd /var/www/rdmotorsAPI
git checkout previous-commit-hash

# Restart
sudo systemctl start rdmotors
```

## Monitoring

- Check logs regularly: `/var/log/rdmotors/`
- Monitor disk space for photo uploads
- Set up database backups
- Monitor API response times
