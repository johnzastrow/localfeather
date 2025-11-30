# Local Feather - Database Setup

This directory contains database schema, migrations, and setup scripts for Local Feather.

## Quick Start

### 1. Configure Database Connection

```bash
# Copy example config
cp config.example.ini config.ini

# Edit with your MariaDB credentials
nano config.ini
```

Update these settings in `config.ini`:

```ini
[database]
host = localhost          # Your MariaDB server IP or hostname
port = 3306
database = localfeather
username = localfeather_user
password = YOUR_STRONG_PASSWORD_HERE
```

### 2. Create Database and User (MariaDB)

Connect to your MariaDB server and run:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS localfeather
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Create user (change password!)
CREATE USER IF NOT EXISTS 'localfeather_user'@'%'
    IDENTIFIED BY 'YOUR_STRONG_PASSWORD_HERE';

-- Grant permissions
GRANT ALL PRIVILEGES ON localfeather.* TO 'localfeather_user'@'%';
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user = 'localfeather_user';
```

### 3. Import Schema

```bash
# Import schema into MariaDB
mysql -h localhost -u localfeather_user -p localfeather < schema.sql

# Or using mariadb command
mariadb -h localhost -u localfeather_user -p localfeather < schema.sql
```

### 4. Seed Test Data (Optional)

```bash
# Install Python dependencies first
cd ..
pip install sqlalchemy pymysql werkzeug

# Run seed script
python database/seed_data.py
```

This creates:
- 2 test users (admin/viewer)
- 4 sample devices
- 144 sample sensor readings
- 2 firmware versions
- Sample device logs and alerts

**Default login credentials:**
- Admin: `admin` / `admin123`
- Viewer: `viewer` / `viewer123`

⚠️ **Change these passwords immediately in production!**

---

## Files in This Directory

### Configuration
- **`config.example.ini`** - Example configuration (copy to `config.ini`)
- **`config.ini`** - Your actual config (**DO NOT commit to git!**)

### Schema
- **`schema.sql`** - Complete MariaDB schema definition
  - Tables for users, devices, readings, firmware, etc.
  - Indexes for performance
  - Views for common queries
  - Stored procedures for maintenance

### Scripts
- **`seed_data.py`** - Populate database with test data
- **`README.md`** - This file

---

## Database Schema Overview

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | Web UI user accounts | username, password_hash, role |
| `devices` | ESP32 device registry | device_id, api_key, approved |
| `readings` | Sensor data points | device_id, sensor, value, timestamp |
| `firmware` | OTA firmware binaries | version, filename, file_hash |
| `device_updates` | OTA update history | device_id, firmware_id, status |
| `settings` | App configuration | setting_key, setting_value |
| `device_logs` | Device events/errors | device_id, log_level, message |
| `alerts` | Alert rules | sensor, condition, threshold |
| `api_keys` | API authentication | api_key, permissions |

### Views

- **`latest_readings`** - Most recent reading for each sensor on each device
- **`device_stats`** - Device statistics summary (sensor count, last seen, etc.)

### Stored Procedures

- **`cleanup_old_readings(days)`** - Delete readings older than N days
- **`update_device_stats()`** - Refresh device statistics

---

## Using with Flask

### Initialize Database Connection

```python
from app.database import init_db

# Initialize with MariaDB
db = init_db()

# Or use SQLite for development
db = init_db(use_dev=True)
```

### Query Examples

```python
from app.database import get_db
from app.models import Device, Reading, User

db = get_db()

# Get all approved devices
with db.session_scope() as session:
    devices = session.query(Device).filter_by(approved=True).all()

# Get recent readings for a device
with db.session_scope() as session:
    readings = session.query(Reading)\
        .filter_by(device_id=1)\
        .order_by(Reading.timestamp.desc())\
        .limit(100)\
        .all()

# Create a new user
from werkzeug.security import generate_password_hash

with db.session_scope() as session:
    user = User(
        username='newuser',
        email='newuser@example.com',
        password_hash=generate_password_hash('password'),
        role='viewer'
    )
    session.add(user)
    # Automatically committed at end of scope
```

---

## Development with SQLite

For development without MariaDB:

1. Edit `config.ini`:

```ini
[database_dev]
sqlite_path = ../data/localfeather_dev.db
```

2. Initialize with dev flag:

```python
from app.database import init_db

db = init_db(use_dev=True)
db.create_tables()
```

3. Seed data works the same:

```bash
# Modify seed_data.py to use use_dev=True
python database/seed_data.py
```

---

## Maintenance

### Backup Database

```bash
# Backup entire database
mysqldump -h localhost -u localfeather_user -p localfeather > backup_$(date +%Y%m%d).sql

# Backup with compression
mysqldump -h localhost -u localfeather_user -p localfeather | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore from Backup

```bash
# Restore
mysql -h localhost -u localfeather_user -p localfeather < backup_20251130.sql

# Restore from compressed
gunzip < backup_20251130.sql.gz | mysql -h localhost -u localfeather_user -p localfeather
```

### Clean Up Old Readings

```sql
-- Delete readings older than 365 days
CALL cleanup_old_readings(365);

-- Check result
SELECT ROW_COUNT() AS rows_deleted;
```

### Optimize Tables

```sql
-- Analyze tables for query optimization
ANALYZE TABLE devices, readings;

-- Optimize tables (reclaim space)
OPTIMIZE TABLE readings;
```

### Check Database Size

```sql
-- Table sizes
SELECT
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
    table_rows AS 'Rows'
FROM information_schema.TABLES
WHERE table_schema = 'localfeather'
ORDER BY (data_length + index_length) DESC;
```

---

## Performance Tuning

### Indexes

The schema includes optimized indexes for:
- Device lookups by `device_id` and `api_key`
- Reading queries by `device_id`, `sensor`, and `timestamp`
- User authentication by `username` and `email`

### Partitioning (Large Deployments)

For high-volume deployments (100,000+ readings), enable partitioning:

```sql
-- Partition readings table by month
ALTER TABLE readings PARTITION BY RANGE (UNIX_TIMESTAMP(timestamp)) (
    PARTITION p_2025_11 VALUES LESS THAN (UNIX_TIMESTAMP('2025-12-01')),
    PARTITION p_2025_12 VALUES LESS THAN (UNIX_TIMESTAMP('2026-01-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### Connection Pooling

Configured in `config.ini`:

```ini
[database]
pool_size = 10          # Base connections
max_overflow = 20       # Additional connections when busy
pool_recycle = 3600     # Recycle connections after 1 hour
pool_pre_ping = true    # Test connections before use
```

---

## Troubleshooting

### Cannot Connect to MariaDB

**Error:** `Can't connect to MySQL server on 'localhost'`

**Solutions:**
1. Check MariaDB is running: `systemctl status mariadb`
2. Verify host/port in `config.ini`
3. Check firewall allows port 3306
4. Ensure MariaDB allows remote connections (if not localhost)

### Authentication Failed

**Error:** `Access denied for user 'localfeather_user'@'host'`

**Solutions:**
1. Verify username/password in `config.ini`
2. Check user exists: `SELECT user, host FROM mysql.user;`
3. Ensure proper permissions: `SHOW GRANTS FOR 'localfeather_user'@'%';`
4. Try wildcard host `'%'` instead of `'localhost'`

### Table Doesn't Exist

**Error:** `Table 'localfeather.devices' doesn't exist`

**Solution:**
```bash
# Import schema
mysql -h localhost -u localfeather_user -p localfeather < schema.sql

# Or use Python
python -c "from app.database import init_db; db = init_db(); db.create_tables()"
```

### Foreign Key Constraint Fails

**Error:** `Cannot add or update a child row: a foreign key constraint fails`

**Solution:**
- Ensure parent records exist before creating child records
- For devices: Ensure device is in `devices` table before adding readings
- For firmware: Ensure user exists before setting `uploaded_by`

---

## Security Best Practices

### 1. Use Strong Passwords

```bash
# Generate secure password
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Limit Database User Permissions

```sql
-- Don't grant SUPER or FILE privileges
-- Only grant what's needed:
GRANT SELECT, INSERT, UPDATE, DELETE ON localfeather.* TO 'localfeather_user'@'%';
```

### 3. Use SSL/TLS for Remote Connections

In `config.ini`:

```ini
[database]
host = mariadb.example.com
port = 3306
# Add SSL parameters
ssl_ca = /path/to/ca.pem
ssl_cert = /path/to/client-cert.pem
ssl_key = /path/to/client-key.pem
```

### 4. Regular Backups

Set up automated backups:

```bash
# Add to crontab
0 2 * * * mysqldump -h localhost -u localfeather_user -p'PASSWORD' localfeather | gzip > /backup/lf_$(date +\%Y\%m\%d).sql.gz
```

### 5. Monitor for Suspicious Activity

```sql
-- Check for unusual device activity
SELECT device_id, COUNT(*) as reading_count
FROM readings
WHERE timestamp > NOW() - INTERVAL 1 HOUR
GROUP BY device_id
HAVING reading_count > 100;  -- More than 100 readings/hour

-- Check for failed login attempts (implement in app)
SELECT username, COUNT(*) as failed_attempts
FROM login_attempts
WHERE success = 0 AND timestamp > NOW() - INTERVAL 1 HOUR
GROUP BY username;
```

---

## Next Steps

After database setup:

1. **Configure Flask App** - Update Flask config with database settings
2. **Test Connection** - Run `python -c "from app.database import init_db; init_db().health_check()"`
3. **Seed Test Data** - Run `python database/seed_data.py`
4. **Start Server** - Begin Flask server implementation

See [TODO.md](../../TODO.md) for complete project roadmap.

---

**Last Updated:** 2025-11-30
