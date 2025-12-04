# Web UI Deployment Guide

The LocalFeather web UI is now ready for deployment. Follow these steps to deploy and test.

## What Was Built

### Features
- **Dashboard**: Overview of all devices with online/offline status
- **Device List**: Manage devices, approve pending devices
- **Device Detail**: View individual device with sensor reading charts (7-day history)
- **Authentication**: Flask-Login with admin/viewer roles
- **Device Management**: Approve, rename, delete devices, regenerate API keys
- **Auto-refresh**: Dashboard updates device list every 10 seconds via HTMX
- **Responsive UI**: Built with Tailwind CSS

### Tech Stack
- Flask 3.1.2 with Flask-Login 0.6.3
- Jinja2 templates (server-side rendering)
- HTMX 1.9.10 for dynamic updates
- Tailwind CSS via CDN
- Chart.js 4.4.1 for sensor graphs

## Files Created/Modified

### New Files
```
server/app/web/
├── __init__.py           # Web blueprint
├── auth.py               # Login/logout routes
├── dashboard.py          # Dashboard routes
└── devices.py            # Device management routes

server/app/templates/
├── base.html             # Base template with nav
├── login.html            # Login page
├── dashboard.html        # Main dashboard
├── devices.html          # Device list
└── device_detail.html    # Device detail with charts

server/create_user.py     # CLI script to create users
```

### Modified Files
```
server/requirements.txt   # Added flask-login, flask-bcrypt
server/app/__init__.py    # Integrated Flask-Login and web blueprint
server/app/models.py      # Added Flask-Login methods to User model
```

## Deployment Steps

### 1. Copy Files to Server

You need to copy the new/modified files to the server at `192.168.1.234:/home/jcz/localfeather/`

**Option A: Manual copy via SSH/SFTP**
Copy these directories and files:
- `app/web/` (entire directory)
- `app/templates/` (entire directory)
- `app/__init__.py`
- `app/models.py`
- `requirements.txt`
- `create_user.py`

**Option B: Use the deploy script** (if you have SSH access)
```bash
cd /home/jcz/Github/localfeather/server
./deploy.sh
```

### 2. Install New Dependencies

SSH into the server:
```bash
ssh jcz@192.168.1.234
cd ~/localfeather
source .venv/bin/activate
pip install -r requirements.txt
```

Expected new packages:
- flask-login==0.6.3
- flask-bcrypt==1.0.1

### 3. Create Admin User

Run the create_user script:
```bash
cd ~/localfeather
source .venv/bin/activate
python create_user.py
```

Example:
```
Username: admin
Email: admin@localfeather.local
Password: [your secure password]
Confirm password: [your secure password]
Role (admin/viewer) [admin]: admin
```

### 4. Restart the Flask Server

```bash
sudo systemctl restart localfeather
sudo systemctl status localfeather
```

Check logs for any errors:
```bash
sudo journalctl -u localfeather -f
```

### 5. Test the Web UI

Open your browser and visit:
```
http://192.168.1.234:5000/
```

You should be redirected to the login page. Log in with the credentials you created.

## Post-Deployment Testing

### Test Checklist

- [ ] Login page loads at `http://192.168.1.234:5000/login`
- [ ] Can log in with created admin user
- [ ] Dashboard loads and shows device statistics
- [ ] Dashboard shows your ESP32 device (esp32-3323b0)
- [ ] Device shows "Online" status (green badge)
- [ ] Device is marked as "Approved"
- [ ] Click "View" on device to see detail page
- [ ] Device detail shows status, network info, and charts
- [ ] Temperature and humidity charts display with real data
- [ ] Can navigate between Dashboard and Devices pages
- [ ] Can log out successfully

### Troubleshooting

**Issue: Login page shows but can't log in**
- Check that user was created: `mysql -ujcz -pyub.miha -h192.168.1.234 localfeather -e "SELECT * FROM users;"`
- Check Flask logs: `sudo journalctl -u localfeather -n 50`

**Issue: 500 Internal Server Error**
- Check Flask logs: `sudo journalctl -u localfeather -f`
- Check if flask-login is installed: `pip list | grep flask-login`

**Issue: Charts don't show**
- Open browser developer console (F12)
- Check for JavaScript errors
- Verify Chart.js loaded from CDN

**Issue: Devices list is empty**
- Verify device is in database: `mysql -ujcz -pyub.miha -h192.168.1.234 localfeather -e "SELECT * FROM devices;"`
- Check that device is approved: `approved` column should be 1

**Issue: Can't approve devices**
- Verify user has admin role: `SELECT username, role FROM users;`
- Only admin users can approve/delete devices

## Database Schema Changes

No database schema changes are required. The web UI uses the existing `users` table from the models.

If the `users` table doesn't exist, you'll need to run migrations or create it manually:

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'viewer') NOT NULL DEFAULT 'viewer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

## Security Considerations

### Current Implementation
- Passwords are hashed using Werkzeug's `pbkdf2:sha256`
- Flask-Login handles session management
- Session cookie is HTTPOnly (default)
- SECRET_KEY is set in Flask config (currently using dev key)

### Production Recommendations
1. **Change SECRET_KEY**: Set environment variable on server
   ```bash
   export SECRET_KEY="your-random-secret-key-here"
   ```

2. **Use HTTPS**: Configure nginx reverse proxy with SSL/TLS certificate

3. **Secure Database**: The web UI currently uses the same database credentials as the API

## Features Available

### Admin Users Can:
- View dashboard with all devices
- Approve pending devices
- Delete devices
- Regenerate device API keys
- View device details and sensor charts
- Rename devices
- Update device location and notes

### Viewer Users Can:
- View dashboard
- View device list
- View device details and charts
- Cannot modify devices

## Next Steps / Future Enhancements

### Potential Improvements:
1. **Data Export**: Add CSV export for readings
2. **Alerts**: Configure threshold alerts per device
3. **User Management**: Web UI to create/manage users
4. **API Key Management**: View/regenerate device API keys from UI
5. **Advanced Charts**: More chart options (hourly aggregation, custom date ranges)
6. **Device Notes**: Add notes field visible on device detail page
7. **Firmware Management**: Upload and manage OTA firmware updates

## Support

If you encounter issues during deployment:
1. Check Flask logs: `sudo journalctl -u localfeather -f`
2. Check database connection: `mysql -ujcz -pyub.miha -h192.168.1.234 localfeather`
3. Verify all files were copied correctly
4. Ensure dependencies are installed in venv

## Summary

The web UI replaces the need for MySQL commands to manage devices. You can now:
- ✅ Approve devices with one click instead of SQL commands
- ✅ View all devices and their status at a glance
- ✅ See sensor readings as interactive charts
- ✅ Manage devices from any browser on your network
- ✅ Auto-refreshing dashboard shows real-time status

Access the web UI at: **http://192.168.1.234:5000/**
