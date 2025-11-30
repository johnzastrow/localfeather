# Local Feather - Deployment Guide

This guide covers deploying Local Feather in various environments beyond the basic setup.

## Deployment Options

### Option 1: Raspberry Pi (Production)

**Best for**: Home/small office, 5-20 devices

See [SETUP.md](SETUP.md) for detailed step-by-step guide.

**Quick Summary**:
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/localfeather/main/install.sh | bash
```

**Components Installed**:
- Flask application (`/opt/localfeather`)
- MariaDB database
- Systemd service (`localfeather.service`)
- Automatic backups (daily cron job)

**Service Management**:
```bash
sudo systemctl start localfeather    # Start
sudo systemctl stop localfeather     # Stop
sudo systemctl restart localfeather  # Restart
sudo systemctl status localfeather   # Check status
```

---

### Option 2: Docker Compose (All Platforms)

**Best for**: Development, Windows/Mac, easy updates

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  mariadb:
    image: mariadb:10.11
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: localfeather
      MYSQL_USER: localfeather
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mariadb_data:/var/lib/mysql
    networks:
      - localfeather

  flask:
    build: ./server
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: mysql+pymysql://localfeather:${DB_PASSWORD}@mariadb/localfeather
      SECRET_KEY: ${SECRET_KEY}
      FLASK_ENV: production
    volumes:
      - ./data:/app/data
      - ./backups:/app/backups
    depends_on:
      - mariadb
    networks:
      - localfeather

volumes:
  mariadb_data:

networks:
  localfeather:
```

**.env.example**:
```env
DB_ROOT_PASSWORD=change-this-root-password
DB_PASSWORD=change-this-db-password
SECRET_KEY=change-this-secret-key-to-random-string
```

**Setup**:
```bash
# Copy and configure environment
cp .env.example .env
nano .env  # Edit with your passwords

# Start services
docker-compose up -d

# Create admin user
docker-compose exec flask flask create-admin

# View logs
docker-compose logs -f
```

**Updates**:
```bash
git pull
docker-compose build
docker-compose up -d
```

---

### Option 3: Manual Installation (Linux Server)

**Best for**: Ubuntu/Debian servers, custom configurations

**Requirements**:
- Ubuntu 20.04+ or Debian 11+
- Python 3.9+
- MariaDB 10.5+
- 2GB+ RAM

**Step 1: Install Dependencies**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv mariadb-server git
```

**Step 2: Configure MariaDB**
```bash
sudo mysql_secure_installation
# Follow prompts to secure installation

sudo mysql -u root -p
```

In MySQL prompt:
```sql
CREATE DATABASE localfeather CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'localfeather'@'localhost' IDENTIFIED BY 'your-password-here';
GRANT ALL PRIVILEGES ON localfeather.* TO 'localfeather'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Step 3: Install Local Feather**
```bash
sudo mkdir -p /opt/localfeather
sudo chown $USER:$USER /opt/localfeather
cd /opt/localfeather

git clone https://github.com/YOUR_REPO/localfeather.git .

python3 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
```

**Step 4: Configure Application**
```bash
cp .env.example .env
nano .env
```

Edit `.env`:
```env
DATABASE_URL=mysql+pymysql://localfeather:your-password@localhost/localfeather
SECRET_KEY=generate-random-string-here
FLASK_ENV=production
```

**Step 5: Initialize Database**
```bash
cd server
flask db upgrade
flask create-admin
```

**Step 6: Create Systemd Service**
```bash
sudo nano /etc/systemd/system/localfeather.service
```

```ini
[Unit]
Description=Local Feather Sensor Platform
After=network.target mariadb.service

[Service]
Type=simple
User=localfeather
WorkingDirectory=/opt/localfeather/server
Environment="PATH=/opt/localfeather/venv/bin"
ExecStart=/opt/localfeather/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Step 7: Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable localfeather
sudo systemctl start localfeather
```

---

## Production Considerations

### Security

**1. Use HTTPS (Optional for Local Network)**

Generate self-signed certificate:
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/localfeather.key \
  -out /etc/ssl/certs/localfeather.crt
```

Configure Flask to use HTTPS (or use reverse proxy like Nginx).

**2. Firewall Configuration**
```bash
# Allow only local network access
sudo ufw allow from 192.168.1.0/24 to any port 5000
sudo ufw enable
```

**3. Strong Passwords**
- Admin account: 12+ characters, mixed case, numbers, symbols
- Database: Generate random 32-character password
- SECRET_KEY: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`

**4. Regular Updates**
```bash
# Update system
sudo apt update && sudo apt upgrade

# Update Local Feather
cd /opt/localfeather
git pull
source venv/bin/activate
pip install --upgrade -r server/requirements.txt
flask db upgrade
sudo systemctl restart localfeather
```

### Backups

**Automated Backups** (cron job):
```bash
sudo nano /etc/cron.daily/localfeather-backup
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/localfeather"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u localfeather -p'your-password' localfeather | gzip > $BACKUP_DIR/db-$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db-*.sql.gz" -mtime +7 -delete
```

```bash
sudo chmod +x /etc/cron.daily/localfeather-backup
```

**Manual Backup**:
```bash
mysqldump -u localfeather -p localfeather > backup-$(date +%Y%m%d).sql
```

**Restore from Backup**:
```bash
mysql -u localfeather -p localfeather < backup-20241129.sql
```

### Monitoring

**System Health**:
```bash
# Check service status
systemctl status localfeather

# View logs
journalctl -u localfeather -f

# Check resource usage
htop
```

**Database Monitoring**:
```bash
# Connect to database
mysql -u localfeather -p

# Check table sizes
SELECT table_name,
       ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'localfeather';
```

**Disk Space Monitoring**:
```bash
df -h
du -sh /opt/localfeather/*
du -sh /var/lib/mysql/localfeather
```

### Performance Tuning

**MariaDB Configuration**:

Edit `/etc/mysql/mariadb.conf.d/50-server.cnf`:

```ini
[mysqld]
# InnoDB settings for Raspberry Pi
innodb_buffer_pool_size = 128M  # 25% of RAM (for 512MB Pi)
innodb_log_file_size = 64M
innodb_flush_method = O_DIRECT
innodb_flush_log_at_trx_commit = 2

# Query cache
query_cache_size = 32M
query_cache_limit = 2M

# Connections
max_connections = 50
```

Restart MariaDB:
```bash
sudo systemctl restart mariadb
```

**Flask/Gunicorn Tuning**:

For Raspberry Pi 4 (4GB RAM):
```bash
# 4 workers for 4 cores
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

For Raspberry Pi 3 (1GB RAM):
```bash
# 2 workers to conserve memory
gunicorn -w 2 -b 0.0.0.0:5000 --timeout 120 app:app
```

---

## High Availability (Advanced)

### Load Balancing with Nginx

**Install Nginx**:
```bash
sudo apt install nginx
```

**Configure** (`/etc/nginx/sites-available/localfeather`):
```nginx
upstream localfeather_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;  # Run second Flask instance
}

server {
    listen 80;
    server_name localfeather.local;

    location / {
        proxy_pass http://localfeather_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/localfeather /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### MariaDB Replication

**Master-Slave Setup** (for data redundancy):

See MariaDB documentation: https://mariadb.com/kb/en/setting-up-replication/

---

## Scaling Beyond 20 Devices

**Option 1: Upgrade Hardware**
- Raspberry Pi 4 (8GB RAM)
- Dedicated server (4+ CPU cores, 8GB+ RAM)

**Option 2: Optimize Database**
```sql
-- Add aggregated hourly data table
CREATE TABLE reading_hourly (
    device_id INT,
    sensor_type VARCHAR(50),
    hour DATETIME,
    min_value FLOAT,
    max_value FLOAT,
    avg_value FLOAT,
    count INT,
    INDEX (device_id, hour)
);

-- Aggregate old data
INSERT INTO reading_hourly
SELECT device_id, sensor_type,
       DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00'),
       MIN(value), MAX(value), AVG(value), COUNT(*)
FROM readings
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY device_id, sensor_type, DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00');

-- Delete old raw data
DELETE FROM readings WHERE timestamp < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

**Option 3: Migrate to PostgreSQL**
```bash
# Export from MariaDB
mysqldump localfeather > maria_export.sql

# Install PostgreSQL
sudo apt install postgresql

# Create database
sudo -u postgres createdb localfeather

# Migrate (manual schema adjustment needed)
# Or use DATABASE_URL with PostgreSQL and run:
flask db upgrade
```

---

## Troubleshooting Deployment

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common deployment issues.

**Quick Checks**:
```bash
# Is service running?
systemctl status localfeather

# Can you connect to database?
mysql -u localfeather -p localfeather

# Are ports accessible?
curl http://localhost:5000/api/health

# Check logs for errors
journalctl -u localfeather --no-pager | tail -50
```

---

## Uninstall

**Raspberry Pi (install script)**:
```bash
sudo systemctl stop localfeather
sudo systemctl disable localfeather
sudo rm /etc/systemd/system/localfeather.service
sudo rm -rf /opt/localfeather
sudo mysql -u root -p -e "DROP DATABASE localfeather; DROP USER 'localfeather'@'localhost';"
```

**Docker**:
```bash
docker-compose down -v  # -v removes volumes (deletes data!)
```

---

## Support

- Deployment issues: [GitHub Issues](https://github.com/YOUR_REPO/issues)
- Security concerns: [security@example.com]
- Community forum: [discussions](https://github.com/YOUR_REPO/discussions)

---

**Last Updated**: 2024-11-29
