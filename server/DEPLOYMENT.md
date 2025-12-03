# Local Feather Server Deployment Guide

This guide will help you deploy the Local Feather Flask server to 192.168.1.234.

## Prerequisites

- SSH access to 192.168.1.234
- Python 3.8+ installed on the server
- MariaDB already running on 192.168.1.234:3306 (with localfeather database)

## Deployment Steps

### 1. Copy Files to Server

From your development machine, copy the server directory to 192.168.1.234:

```bash
# Option A: Using scp
scp -r server/ jcz@192.168.1.234:~/localfeather/

# Option B: Using rsync (recommended - excludes venv)
rsync -av --exclude='.venv' --exclude='__pycache__' server/ jcz@192.168.1.234:~/localfeather/
```

### 2. SSH into the Server

```bash
ssh jcz@192.168.1.234
cd ~/localfeather
```

### 3. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Verify Database Configuration

The database config should already be set in `database/config.ini`:

```ini
[database]
host = 192.168.1.234
port = 3306
database = localfeather
username = jcz
password = yub.miha
pool_size = 10
max_overflow = 20
pool_recycle = 3600
pool_pre_ping = true
```

### 5. Test the Server

```bash
# Run development server for testing
python run.py
```

You should see:
```
============================================================
Local Feather - Development Server
============================================================
Database: Connected
API Endpoints: /api
Health Check: /health
============================================================

 * Running on http://0.0.0.0:5000
```

Test from another machine on your network:
```bash
curl http://192.168.1.234:5000/health
```

### 6. Set Up Production Server with Gunicorn

For production, use Gunicorn instead of the Flask development server:

```bash
# Install gunicorn
pip install gunicorn

# Test gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

### 7. Create Systemd Service (Recommended)

Create `/etc/systemd/system/localfeather.service`:

```ini
[Unit]
Description=Local Feather API Server
After=network.target mariadb.service

[Service]
Type=notify
User=jcz
Group=jcz
WorkingDirectory=/home/jcz/localfeather
Environment="PATH=/home/jcz/localfeather/.venv/bin"
ExecStart=/home/jcz/localfeather/.venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile /home/jcz/localfeather/logs/access.log \
    --error-logfile /home/jcz/localfeather/logs/error.log \
    'app:create_app()'
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Create log directory:
```bash
mkdir -p ~/localfeather/logs
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable localfeather
sudo systemctl start localfeather
sudo systemctl status localfeather
```

### 8. Configure Firewall

Ensure port 5000 is open:

```bash
# If using ufw
sudo ufw allow 5000/tcp

# If using firewalld
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 9. Verify Deployment

From any device on your network:

```bash
# Health check
curl http://192.168.1.234:5000/health

# List endpoints
curl http://192.168.1.234:5000/

# List devices
curl http://192.168.1.234:5000/api/devices
```

## Updating the Server

To update the server after making changes:

```bash
# On your dev machine
rsync -av --exclude='.venv' --exclude='__pycache__' server/ jcz@192.168.1.234:~/localfeather/

# On the server
ssh jcz@192.168.1.234
cd ~/localfeather
sudo systemctl restart localfeather
```

## Troubleshooting

### Check logs
```bash
# Systemd logs
sudo journalctl -u localfeather -f

# Application logs
tail -f ~/localfeather/logs/error.log
tail -f ~/localfeather/logs/access.log
```

### Test database connection
```bash
cd ~/localfeather
source .venv/bin/activate
python -c "from app.database import init_db; db = init_db(); print('DB OK' if db.health_check() else 'DB FAILED')"
```

### Common Issues

**Port already in use:**
```bash
sudo lsof -i :5000
# Kill the process if needed
sudo kill -9 <PID>
```

**Database connection failed:**
- Verify MariaDB is running: `sudo systemctl status mariadb`
- Check database exists: `mysql -u jcz -p -e "SHOW DATABASES;"`
- Verify credentials in `database/config.ini`

**Permission denied:**
```bash
# Fix file ownership
sudo chown -R jcz:jcz ~/localfeather
```

## Security Notes

1. **Change the SECRET_KEY**: Edit `app/__init__.py` and set a strong secret key
2. **Use HTTPS**: Consider setting up nginx reverse proxy with SSL/TLS
3. **Database password**: Consider using environment variables instead of config.ini
4. **Firewall**: Only allow access from your local network

## Quick Reference

- **Start server**: `sudo systemctl start localfeather`
- **Stop server**: `sudo systemctl stop localfeather`
- **Restart server**: `sudo systemctl restart localfeather`
- **View status**: `sudo systemctl status localfeather`
- **View logs**: `sudo journalctl -u localfeather -f`
- **Test health**: `curl http://192.168.1.234:5000/health`
