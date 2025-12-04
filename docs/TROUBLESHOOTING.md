# Local Feather - Troubleshooting Guide

Common problems and solutions for Local Feather.

## Quick Diagnostics

Run these commands first to gather information:

**Raspberry Pi**:
```bash
# Check if service is running
sudo systemctl status localfeather

# View recent logs
sudo journalctl -u localfeather --no-pager | tail -50

# Check database connection
mysql -u localfeather -p -e "SELECT 1"

# Test web server
curl http://localhost:5000/api/health
```

**Docker**:
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs --tail=50

# Test web server
curl http://localhost:5000/api/health
```

---

## Installation Issues

### Problem: Install script fails with "Permission denied"

**Solution**:
```bash
# Download script first
wget https://raw.githubusercontent.com/YOUR_REPO/localfeather/main/install.sh

# Make executable
chmod +x install.sh

# Run with bash
./install.sh
```

### Problem: "Python 3.9+ not found"

**Solution** (Raspberry Pi OS / Debian):
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

### Problem: MariaDB installation fails

**Solution**:
```bash
# Remove partial installation
sudo apt remove --purge mariadb-server mariadb-client

# Clean up
sudo apt autoremove
sudo apt autoclean

# Reinstall
sudo apt update
sudo apt install mariadb-server
```

---

## Server / Web Interface Issues

### Problem: Can't access web interface

**Symptoms**: Browser shows "This site can't be reached" or connection timeout.

**Diagnosis**:
```bash
# Is service running?
sudo systemctl status localfeather  # Should show "active (running)"

# Is port 5000 listening?
sudo netstat -tlnp | grep 5000

# Can you access locally?
curl http://localhost:5000
```

**Solutions**:

**1. Service not running**:
```bash
sudo systemctl start localfeather
sudo systemctl status localfeather
# Check logs for errors
sudo journalctl -u localfeather -n 50
```

**2. Wrong IP address**:
```bash
# Find Raspberry Pi IP
hostname -I

# Access using IP instead of raspberrypi.local
# Example: http://192.168.1.100:5000
```

**3. Firewall blocking**:
```bash
# Temporarily disable firewall to test
sudo ufw disable

# If that fixes it, add rule:
sudo ufw allow from 192.168.1.0/24 to any port 5000
sudo ufw enable
```

**4. mDNS not working** (raspberrypi.local doesn't resolve):
```bash
# Install Avahi (should be installed by default)
sudo apt install avahi-daemon
sudo systemctl start avahi-daemon

# Or just use IP address instead
```

###Problem: Web interface loads but shows errors

**Symptoms**: Page loads but shows "Database error" or500 errors.

**Solution**:
```bash
# Check database is running
sudo systemctl status mariadb

# Test database connection
mysql -u localfeather -p localfeather -e "SHOW TABLES;"

# Check DATABASE_URL in .env is correct
cat /opt/localfeather/.env | grep DATABASE_URL

# Restart service
sudo systemctl restart localfeather
```

### Problem: Login page appears but login fails

**Solution**:
```bash
# Reset admin password
cd /opt/localfeather
source venv/bin/activate
flask reset-password admin

# Or create new admin
flask create-admin
```

---

## ESP32 / Device Issues

### Problem: ESP32 won't enter setup mode

**Symptoms**: LED doesn't blink, no "LocalFeather-Setup" WiFi appears.

**Solutions**:

**1. Force factory reset**:
- Hold BOOT button
- Press and release RESET button
- Release BOOT button after 3 seconds

**2. Re-flash firmware**:
- Connect via USB
- Open Arduino IDE
- Upload firmware again
- Monitor serial output: Tools → Serial Monitor

**3. Check serial monitor**:
```
Expected output:
Starting WiFiManager...
AP Name: LocalFeather-Setup
AP IP: 192.168.4.1
```

If you see errors, note them and search GitHub issues.

### Problem: ESP32 can't connect to WiFi

**Symptoms**: Setup completes but device doesn't connect to home WiFi.

**Diagnosis** (Serial Monitor):
```
Connecting to WiFi: MyNetwork
.........................
Failed to connect
```

**Solutions**:

**1. Wrong password**:
- Re-enter WiFi setup mode (hold BOOT for 10 seconds)
- Double-check password (case-sensitive!)

**2. 5GHz WiFi network**:
- ESP32 only supports 2.4GHz
- Check router settings: enable 2.4GHz band
- Use separate SSID for 2.4GHz if possible

**3. Special characters in SSID**:
- Avoid spaces, quotes, or special characters in network name
- Or use quotes in WiFiManager: `"My Network"`

**4. Hidden SSID**:
- Unhide network temporarily
- Or manually add in code (see firmware README)

**5. MAC address filtering**:
- Check ESP32 MAC address in serial monitor
- Add to router's allowed devices list

### Problem: "No API key found" or "401 Invalid API key" errors

**Symptoms**: Serial monitor shows:
```
No API key found - registering with server...
Response code: 401
❌ Invalid API key - device may need re-registration
```

**Diagnosis**:

First, find your device ID in the serial output:
```
📟 Device ID: esp32-3323b0
```

Then SSH into your server and check the device registration:
```bash
ssh user@192.168.1.234
mysql -u localfeather -p localfeather_db \
  -e "SELECT device_id, api_key, approved, last_seen FROM devices WHERE device_id='esp32-3323b0';"
```

**Solutions by scenario**:

**1. Device not in database** (query returns no rows):
- Server may be refusing registration requests
- Check server logs: `journalctl -u localfeather -n 50` or `docker logs localfeather-web-1`
- Ensure `/api/readings` endpoint is accessible
- Test manually: `curl http://192.168.1.234:5000/api/health`

**2. Device registered but `approved=0`**:
- New devices require manual approval for security
- Approve via web UI: Dashboard → Devices → esp32-3323b0 → Approve
- Or approve via database:
  ```bash
  mysql -u localfeather -p localfeather_db \
    -e "UPDATE devices SET approved=1 WHERE device_id='esp32-3323b0';"
  ```

**3. Device approved but API key mismatch**:
- The API key in the database doesn't match what's stored on the ESP32
- **Option A**: Regenerate and manually set on ESP32 (see below)
- **Option B**: Reset device and let it re-register

**Manually setting API key on ESP32**:
- Generate new API key in web UI: Devices → esp32-3323b0 → Regenerate Key
- Copy the displayed key (e.g., `abc123xyz456`)
- The ESP32 firmware currently doesn't support manual key entry, so you need to either:
  - Use the web UI to trigger key sync (future feature), OR
  - Erase ESP32 NVS and let it re-register:
    ```bash
    pio run --target erase
    pio run --target upload
    ```

### Problem: Device registers but shows "offline"

**Symptoms**: Device appears in web UI but status is always offline.

**Solutions**:

**1. Check device can reach server**:

In serial monitor, look for:
```
Server: http://192.168.1.100:5000
Posting readings...
HTTP Response: 200
```

If you see `HTTP Response: -1` or connection errors:
- Check server IP is correct
- Ping server from another device
- Ensure server and ESP32 are on same network/subnet

**2. API key invalid**:
```bash
# Check device in database
mysql -u localfeather -p localfeather \
  -e "SELECT device_id, api_key, status FROM devices WHERE device_id='esp32-sensor-01';"

# Regenerate API key in web UI:
# Devices → [device name] → Regenerate API Key
```

**3. Approve device in web UI**:
- New devices need approval
- Dashboard → Notifications → "Approve Device"

### Problem: Readings not appearing in dashboard

**Symptoms**: Device shows "online" but no sensor data.

**Diagnosis**:
```bash
# Check if readings are being received
mysql -u localfeather -p localfeather \
  -e "SELECT * FROM readings WHERE device_id=1 ORDER BY timestamp DESC LIMIT 5;"
```

**Solutions**:

**1. Sensor not connected**:
- Check wiring (VCC, GND, SDA, SCL)
- Test sensor with example sketch first

**2. Sensor type mismatch**:
- Serial monitor should show: `Sensor: BME280 detected`
- If "Sensor not found", check I2C address (0x76 or 0x77)

**3. Data not sent**:

Serial monitor should show:
```
Temperature: 23.5 C
Humidity: 65.2 %
Posting to server...
Response: 200 OK
```

If "Response: 401" → API key problem
If "Response: 429" → Rate limited (sending too fast)

### Problem: OTA update fails

**Symptoms**: Update starts but device reboots to old version.

**Solutions**:

**1. Check firmware file**:
- File must be .bin format
- File size should be <1MB
- Upload via web UI: Menu → Firmware → Upload

**2. Not enough flash space**:
- ESP32 needs 2x firmware size free
- Use "Minimal SPIFFS" partition scheme in Arduino

IDE

**3. Network interruption during download**:
- Keep ESP32 powered during update
- Use stable WiFi connection
- Place ESP32 closer to router during update

**Serial monitor during OTA**:
```
Checking for updates...
Update available: v1.1.0
Downloading...
[====================] 100%
Update successful, rebooting...
```

---

## Database Issues

### Problem: "Database connection failed"

**Solution**:
```bash
# Is MariaDB running?
sudo systemctl status mariadb

# Start if stopped
sudo systemctl start mariadb

# Test connection
mysql -u localfeather -p

# Check password in .env matches database
cat /opt/localfeather/.env | grep DATABASE_URL
```

### Problem: Slow dashboard / queries timeout

**Symptoms**: Dashboard takes >5 seconds to load, charts don't render.

**Solutions**:

**1. Too much data**:
```sql
-- Check table sizes
SELECT COUNT(*) FROM readings;

-- If >1 million rows, clean up old data
DELETE FROM readings WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Optimize tables
OPTIMIZE TABLE readings;
```

**2. Missing indexes**:
```sql
-- Add indexes if missing
CREATE INDEX idx_timestamp ON readings(timestamp);
CREATE INDEX idx_device_sensor ON readings(device_id, sensor_type);
```

**3. Raspberry Pi overloaded**:
```bash
# Check CPU/RAM usage
htop

# Check disk I/O
iostat -x 1

# If high, consider upgrading to Raspberry Pi 4 or dedicated server
```

### Problem: "Disk full" errors

**Solution**:
```bash
# Check disk space
df -h

# Find large files
du -sh /var/lib/mysql/*
du -sh /opt/localfeather/*

# Clean up old backups
rm /var/backups/localfeather/db-202*.sql.gz

# Clean up old data in database
mysql -u localfeather -p localfeather \
  -e "DELETE FROM readings WHERE timestamp < DATE_SUB(NOW(), INTERVAL 180 DAY);"
```

---

## Network Issues

### Problem: "Device not found" on local network

**Symptoms**: Can't access raspberrypi.local or ESP32 won't connect.

**Solutions**:

**1. Find IP addresses**:
```bash
# Raspberry Pi: Find own IP
hostname -I

# Router admin panel: Check DHCP client list
# Look for "raspberrypi" or ESP32's MAC address
```

**2. Reserve IPs in router**:
- Router settings → DHCP → Reserved IPs
- Assign static IP to Raspberry Pi (e.g., 192.168.1.100)
- Assign static IPs to ESP32 devices

**3. Use IP instead of hostname**:
- Instead of `http://raspberrypi.local:5000`
- Use `http://192.168.1.100:5000`

### Problem: Devices on different subnets

**Symptoms**: Raspberry Pi has IP 192.168.1.x, ESP32 has 192.168.0.x

**Solution**:
- Both must be on same subnet to communicate
- Check router configuration
- Guest network usually can't access main network
- Move all devices to main network

---

## Docker-Specific Issues

### Problem: "docker-compose: command not found"

**Solution**:
```bash
# Install Docker Compose
sudo apt install docker-compose

# Or use Docker Compose V2 (built into Docker)
docker compose up -d  # Note: no hyphen
```

### Problem: Containers won't start

**Diagnosis**:
```bash
docker-compose ps      # Check status
docker-compose logs    # View error messages
```

**Common issues**:

**1. Port 5000 already in use**:
```bash
# Find process using port
sudo lsof -i :5000

# Kill process or change port in docker-compose.yml
ports:
  - "5001:5000"  # Use port 5001 instead
```

**2. Database initialization failed**:
```bash
# Remove volumes and start fresh
docker-compose down -v
docker-compose up -d
```

**3. Permission errors**:
```bash
# Fix ownership of data directories
sudo chown -R $USER:$USER ./data ./backups
```

---

## Performance Issues

### Problem: Raspberry Pi running hot / slow

**Symptoms**: Temperature >70°C, dashboard sluggish.

**Solutions**:

**1. Add heatsink or fan**:
- Passive heatsink: <$5
- Active cooling case: $10-15
- Target: <60°C under load

**2. Reduce worker processes**:

Edit systemd service:
```ini
ExecStart=/opt/localfeather/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app
```
(Use 2 workers instead of 4 on Raspberry Pi 3)

**3. Optimize database**:
See "Slow dashboard" above.

###Problem: High memory usage

**Diagnosis**:
```bash
free -h
```

**Solution**:
```bash
# Add swap (if not already added)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Backup & Recovery

### Problem: Lost admin password

**Solution**:
```bash
# Raspberry Pi
cd /opt/localfeather
source venv/bin/activate
flask reset-password admin

# Docker
docker-compose exec flask flask reset-password admin
```

### Problem: Corrupted database

**Symptoms**: "Table doesn't exist" errors, random crashes.

**Solution**:
```bash
# Stop service
sudo systemctl stop localfeather

# Try to repair
mysqlcheck -u localfeather -p --auto-repair localfeather

# If that fails, restore from backup
mysql -u localfeather -p localfeather < /var/backups/localfeather/db-20241129.sql

# Restart service
sudo systemctl start localfeather
```

### Problem: SD card corrupted (Raspberry Pi)

**Symptoms**: Raspberry Pi won't boot, filesystem errors.

**Solution**:
1. Buy new SD card (quality brand: Samsung, SanDisk)
2. Re-image with Raspberry Pi OS
3. Reinstall Local Feather (see SETUP.md)
4. Restore database from backup (if you have one)

**Prevention**:
- Use quality SD cards
- Enable regular backups to USB drive or network storage
- Safely shutdown before unplugging: `sudo shutdown now`

---

## Still Stuck?

### Gather Debug Information

Create a debug report:

```bash
#!/bin/bash
echo "=== System Info ===" > debug.txt
uname -a >> debug.txt
free -h >> debug.txt
df -h >> debug.txt

echo -e "\n=== Service Status ===" >> debug.txt
systemctl status localfeather >> debug.txt 2>&1

echo -e "\n=== Recent Logs ===" >> debug.txt
journalctl -u localfeather --no-pager | tail -100 >> debug.txt

echo -e "\n=== Network ===" >> debug.txt
hostname -I >> debug.txt
ip route >> debug.txt

echo -e "\n=== Database ===" >> debug.txt
mysql -u localfeather -p -e "SHOW TABLES;" localfeather >> debug.txt 2>&1

echo "Debug report saved to debug.txt"
```

### Get Help

1. **Search existing issues**: [GitHub Issues](https://github.com/YOUR_REPO/issues)
2. **Ask in discussions**: [GitHub Discussions](https://github.com/YOUR_REPO/discussions)
3. **Create new issue** with:
   - Description of problem
   - Steps to reproduce
   - Debug report (debug.txt)
   - Hardware (Raspberry Pi model, ESP32 type)
   - Installation method (install script, Docker, manual)

### Community Support

- **Discord/Slack**: [Community chat link]
- **Forum**: [Forum link]
- **Reddit**: r/localfeather (if exists)

---

## FAQ

**Q: How do I erase the ESP32's stored configuration and start fresh?**
A: To completely wipe the ESP32's NVS (non-volatile storage) including saved WiFi credentials, API keys, and server settings:

```bash
cd firmware
pio run --target erase
pio run --target upload
```

**If you get "port is busy" or "Access is denied" errors:**

The serial port is being used by your serial monitor or another program. Try these solutions in order:

1. **Close your serial monitor** - The most common cause. Close any terminal/window showing ESP32 serial output.

2. **Kill PlatformIO monitor processes:**
   ```powershell
   # Windows PowerShell
   taskkill /F /IM "pio.exe" /T

   # Or kill Python processes
   taskkill /F /IM python.exe /T
   ```

3. **Close VS Code entirely** - If using PlatformIO extension in VS Code, it may hold the port.

4. **Unplug and replug the USB cable** - This forces the port to release. Note: Windows might assign a different COM port number (check `pio device list`).

5. **Find and kill the specific process:**
   ```powershell
   # Windows PowerShell
   Get-Process | Where-Object {$_.MainWindowTitle -like "*COM9*"} | Stop-Process -Force
   ```

After erasing, the ESP32 will boot as if brand new and need to be reconfigured through the WiFiManager portal.

**Q: I see "Device registered successfully. Awaiting approval." - what do I do?**
A: This is normal for new devices. The device registered successfully and received an API key, but it needs admin approval before it can send data.

To approve the device:
```bash
# Via database
mysql -u localfeather -p localfeather_db \
  -e "UPDATE devices SET approved=1 WHERE device_id='esp32-XXXXXX';"

# Or via web UI (if available)
Dashboard → Devices → [your device] → Approve
```

After approval, the device will start sending readings successfully on the next POST request.

**Q: How do I find my ESP32's device ID?**
A: The device ID is printed in the serial monitor after setup completes. Look for:
```
✓ Setup complete - entering main loop
📟 Device ID: esp32-a1b2c3
🌐 Server: http://192.168.1.234:5000
```
The device ID format is `esp32-XXXXXX` where XXXXXX are the last 3 bytes of the MAC address. If you don't see it (using older firmware), press the RESET button on your ESP32 to reboot, or check the early boot "Configuration" section in the serial output.

**Q: I'm getting "Table 'localfeather.Devices' doesn't exist" errors**
A: Table names are **case-sensitive** on Linux/Mac but not on Windows. The correct table names are lowercase:
- `devices` (not `Devices`)
- `sensors` (not `Sensors`)
- `readings` (not `Readings`)
- `users` (not `Users`)

If you need to check your table names: `SHOW TABLES;`

**Q: Can I use PostgreSQL instead of MariaDB?**
A: Yes, change DATABASE_URL in .env to postgresql:// format. Same migrations work.

**Q: Can I run on Windows without Docker?**
A: Use WSL2 (Windows Subsystem for Linux) and follow Linux installation steps.

**Q: How many devices can one Raspberry Pi handle?**
A: Tested up to 20 devices on Raspberry Pi 4. Raspberry Pi 3 handles 10-15.

**Q: Can I access from internet (outside local network)?**
A: Not recommended (security risk). If needed:
  - Set up VPN (WireGuard, OpenVPN)
  - OR use Cloudflare Tunnel
  - OR reverse proxy with HTTPS + authentication

**Q: ESP32 keeps rebooting**
A: Check power supply (use 5V 2A+), check for short circuits in wiring, view serial monitor for crash logs.

**Q: Can I use different sensors?**
A: Yes! Modify firmware to support your sensor. See firmware/examples/ for templates.

**Q: How do I backup to external USB drive?**
A: Mount USB drive, update backup script to copy to /mnt/usb/backups/

**Q: Does it work offline?**
A: Yes! No internet required. Everything runs on local network.

---

**Last Updated**: 2024-11-29

**Didn't find your issue?** [Open a new issue](https://github.com/YOUR_REPO/issues/new) with details!
