# Local Feather - Setup Guide

**For Non-Technical Users**

This guide will walk you through setting up Local Feather step-by-step. No prior programming experience required!

## What You'll Need

### Hardware

**For the Server** (choose one):
- ✅ **Recommended**: Raspberry Pi 4 (2GB or 4GB model) with power supply and microSD card (32GB+)
- OR a spare laptop/desktop running Linux
- OR a Windows 10/11 computer (we'll use WSL2)

**For Sensors**:
- ESP32 development board (like Adafruit ESP32 Feather)
- Temperature/humidity sensor (like DHT22 or BME280)
- USB cable to connect ESP32 to your computer
- Power supply for ESP32 (USB power adapter or battery)

**Network**:
- WiFi router (2.4GHz - the ESP32 needs this)
- Ethernet cable for Raspberry Pi (optional but recommended)

### Software You'll Download

Don't worry about downloading these yet - we'll guide you through each step!

---

## Part 1: Set Up the Server

### Option A: Raspberry Pi (Recommended)

#### Step 1: Prepare Your Raspberry Pi

**1.1 Install Raspberry Pi OS**

If your Raspberry Pi doesn't have an operating system yet:

1. Download **Raspberry Pi Imager** from [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Insert your microSD card into your computer
3. Open Raspberry Pi Imager
4. Click "Choose OS" → "Raspberry Pi OS (64-bit)" (the first option)
5. Click "Choose Storage" → select your microSD card
6. Click the gear icon ⚙️ for advanced options:
   - ✅ Enable SSH
   - ✅ Set username and password (remember these!)
   - ✅ Configure WiFi (enter your network name and password)
   - ✅ Set locale settings
7. Click "Write" and wait (takes 5-10 minutes)
8. Remove microSD card and insert into Raspberry Pi
9. Connect power cable - Raspberry Pi will boot up (takes 1-2 minutes)

**1.2 Connect to Your Raspberry Pi**

On your computer:

**Windows**:
- Download PuTTY from [putty.org](https://www.putty.org/)
- Open PuTTY
- Enter hostname: `raspberrypi.local` (or the IP address if you know it)
- Click "Open"
- Login with the username and password you set earlier

**Mac/Linux**:
- Open Terminal
- Type: `ssh username@raspberrypi.local` (replace `username` with your username)
- Enter your password when prompted

You should now see a command prompt like: `username@raspberrypi:~ $`

#### Step 2: Install Local Feather (Automated)

**2.1 Download and Run Installation Script**

Copy and paste this command into your Raspberry Pi terminal:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/localfeather/main/install.sh | bash
```

**What this does**:
- Installs Python and required packages
- Installs and configures MariaDB database
- Downloads Local Feather code
- Creates database tables
- Sets up automatic startup on boot
- Creates your first admin user

**This takes 15-20 minutes. Go grab a coffee!** ☕

**2.2 Create Your Admin Account**

When the script asks, create your admin account:
- Username: (choose a username, like "admin")
- Password: (choose a strong password - write it down!)
- Email: (your email address)

**2.3 Check Installation**

After the script finishes, you should see:

```
✅ Local Feather installed successfully!
✅ Service is running
✅ Access your dashboard at: http://raspberrypi.local:5000
```

#### Step 3: Access the Web Interface

1. On any computer/phone on the same WiFi network
2. Open a web browser
3. Go to: `http://raspberrypi.local:5000`
   - If that doesn't work, use `http://192.168.1.XXX:5000` (replace XXX with your Raspberry Pi's IP address)
4. You should see the Local Feather login page!
5. Log in with the username and password you created

**Troubleshooting**:
- Can't access the page? See [Troubleshooting Guide](TROUBLESHOOTING.md#cant-access-web-interface)
- Page loads slowly? This is normal on Raspberry Pi 3, faster on Raspberry Pi 4

---

### Option B: Docker (Windows/Mac/Linux)

If you prefer using Docker, or want to run on Windows/Mac:

#### Step 1: Install Docker

**Windows**:
1. Download Docker Desktop from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Run installer and follow prompts
3. Restart computer when asked
4. Open Docker Desktop - it may take a few minutes to start

**Mac**:
1. Download Docker Desktop from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Drag Docker to Applications folder
3. Open Docker from Applications
4. Follow setup prompts

**Linux**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

#### Step 2: Download Local Feather

**Windows/Mac**:
1. Download the code from GitHub (click green "Code" button → "Download ZIP")
2. Extract the ZIP file to a folder (like Documents/localfeather)
3. Open that folder

**Linux**:
```bash
cd ~
git clone https://github.com/YOUR_REPO/localfeather.git
cd localfeather
```

#### Step 3: Start Local Feather

**Windows**:
1. Open PowerShell (right-click Start → Windows PowerShell)
2. Navigate to your localfeather folder:
   ```powershell
   cd Documents\localfeather
   ```
3. Start the services:
   ```powershell
   docker-compose up -d
   ```

**Mac/Linux**:
1. Open Terminal
2. Navigate to localfeather folder:
   ```bash
   cd ~/localfeather
   ```
3. Start the services:
   ```bash
   docker-compose up -d
   ```

**Wait 2-3 minutes** for everything to start.

#### Step 4: Create Admin User

Run this command to create your admin account:

```bash
docker-compose exec flask flask create-admin
```

Follow the prompts to set username and password.

#### Step 5: Access Web Interface

Open browser and go to: `http://localhost:5000`

---

## Part 2: Set Up Your First ESP32 Sensor

### Step 1: Install Arduino IDE

1. Download Arduino IDE 2.0 from [arduino.cc/en/software](https://www.arduino.cc/en/software)
2. Install and open Arduino IDE

### Step 2: Add ESP32 Support

1. In Arduino IDE, go to: **File → Preferences**
2. Find "Additional Board Manager URLs"
3. Paste this URL:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Click OK
5. Go to: **Tools → Board → Boards Manager**
6. Search for "esp32"
7. Install "esp32 by Espressif Systems"
8. Wait for installation (takes 5-10 minutes)

### Step 3: Download Local Feather Firmware

1. Download the firmware from GitHub (in the `firmware/` folder)
2. In Arduino IDE: **File → Open**
3. Navigate to and open `localfeather-firmware.ino`

### Step 4: Configure for Your Network

In the firmware code, you'll see:

```cpp
// No configuration needed!
// WiFi setup happens through captive portal on first boot
```

Good news: The firmware uses WiFiManager - it creates its own WiFi network for setup!

### Step 5: Flash Firmware to ESP32

**5.1 Connect ESP32**
1. Connect ESP32 to your computer via USB cable
2. Wait for driver installation (Windows may take a minute)

**5.2 Select Board**
1. **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
2. **Tools → Port → COM3** (Windows) or **/dev/ttyUSB0** (Linux) or **/dev/cu.usbserial** (Mac)
   - The port with your ESP32 will say something like "USB Serial"

**5.3 Upload**
1. Click the Upload button (→ arrow icon)
2. Wait for "Connecting..." message
3. If stuck on "Connecting...", hold the BOOT button on ESP32
4. Wait for upload (takes 1-2 minutes)
5. When done, you'll see "Hard resetting via RTS pin..."

**Done!** Your ESP32 now has Local Feather firmware.

### Step 6: Connect ESP32 to WiFi

**6.1 Enter Setup Mode**

1. Unplug and replug USB cable (or press RESET button on ESP32)
2. ESP32's LED should blink rapidly (setup mode)
3. On your phone/computer, look for WiFi network named: **"LocalFeather-Setup"**
4. Connect to that network (no password)

**6.2 Configure WiFi**

1. Your phone/computer should automatically open a setup page
   - If not, open browser and go to: `http://192.168.4.1`
2. Click "Configure WiFi"
3. Select your home WiFi network from the list
4. Enter your WiFi password
5. Enter server address:
   - **If Raspberry Pi**: `http://raspberrypi.local:5000`
   - **If Docker on same computer**: `http://192.168.1.XXX:5000` (your computer's IP)
6. Click "Save"

**6.3 Register Device**

1. ESP32 will restart and connect to your WiFi
2. Go back to Local Feather web interface
3. You should see a notification: **"New device detected!"**
4. Click to approve the device
5. Give it a friendly name (like "Living Room Sensor")

**Congratulations!** Your first sensor is connected! 🎉

---

## Part 3: Connect a Sensor (Example: BME280)

### Step 1: Wire the Sensor

**BME280 Temperature/Humidity Sensor**:

Connect these pins from BME280 to ESP32:
- **VCC** → **3.3V** (red wire)
- **GND** → **GND** (black wire)
- **SCL** → **GPIO 22** (yellow wire)
- **SDA** → **GPIO 21** (green wire)

**Visual Check**:
- Wires firmly connected?
- Colors match the descriptions above?
- No loose connections?

### Step 2: Verify Sensor in Dashboard

1. Go to your Local Feather dashboard
2. Click on your device name
3. You should see sensor readings appear:
   - Temperature: XX.X °C
   - Humidity: XX.X %
   - Pressure: XXXX hPa (if BME280)

**Troubleshooting**:
- No readings? Check wiring carefully
- Weird values? Sensor may be faulty or not BME280
- See [Troubleshooting Guide](TROUBLESHOOTING.md#sensor-not-detected)

---

## Part 4: View Your Data

### Dashboard Tour

**Home Page**:
- Shows all your devices
- Green dot = online, Red dot = offline
- Latest reading from each sensor

**Device Page** (click device name):
- Live readings (updates every 10 seconds)
- Charts showing:
  - Last 24 hours
  - Last 7 days
  - Last 30 days
- Click the buttons to switch between timeframes

**Export Data**:
1. Go to: **Menu → Export Data**
2. Select device and date range
3. Choose format (CSV for Excel, JSON for programming)
4. Click "Download"
5. Open in Excel or save for analysis

---

## Part 5: Add More Devices

To add more ESP32 sensors:

1. Flash new ESP32 with same firmware (Part 2, Steps 4-5)
2. Connect to "LocalFeather-Setup" WiFi (Part 2, Step 6)
3. Configure with your WiFi and server address
4. Approve in web interface
5. Give it a unique name (Kitchen Sensor, Garage, etc.)

**Repeat for up to 20 devices!**

---

## Part 6: Keep Your System Running

### Auto-Start on Boot

**Raspberry Pi** (using install script):
- ✅ Already configured! Service starts automatically on boot
- Check status: `sudo systemctl status localfeather`

**Docker**:
- Docker Compose is configured to restart on boot
- To stop: `docker-compose down`
- To start: `docker-compose up -d`

### Backups

**Automatic Backups** (Raspberry Pi):
- Backups happen daily at 2 AM
- Stored in `/var/lib/localfeather/backups/`
- Keeps last 7 daily + 4 weekly backups
- To download: Menu → Settings → Download Backup

**Manual Backup**:
1. Web UI: **Menu → Settings → Create Backup Now**
2. Download the file to your computer
3. Store safely (external drive, cloud storage)

**Restore from Backup**:
1. Web UI: **Menu → Settings → Restore**
2. Upload your backup file
3. Confirm restoration
4. System will restart with restored data

### Updates

**Check for Updates**:
1. Web UI: **Menu → Settings → System**
2. Current version shown at bottom
3. Click "Check for Updates"

**Install Update**:
1. Download new release from GitHub
2. Raspberry Pi:
   ```bash
   cd /opt/localfeather
   sudo git pull
   sudo systemctl restart localfeather
   ```
3. Docker:
   ```bash
   cd ~/localfeather
   docker-compose pull
   docker-compose up -d
   ```

---

## Common Tasks

### Add a New User

**Admin users can add viewers** (read-only access):

1. Web UI: **Menu → Settings → Users**
2. Click "Add User"
3. Enter username and password
4. Select role: **Viewer** (can only view) or **Admin** (full access)
5. Click "Create"
6. Share username/password with family member, colleague, etc.

### Delete a Device

1. Web UI: **Devices** page
2. Click device name
3. Scroll to bottom
4. Click "Delete Device"
5. Confirm (⚠️ this deletes all historical data for this device)

### Change Device Reading Interval

**Default**: 60 seconds

To change:
1. Device page → "Settings" tab
2. Change "Reading Interval" (10-300 seconds)
3. Click "Save"
4. ESP32 will update on next check-in

### View Logs

**Web UI**:
- Menu → Settings → Logs
- Shows recent errors and events

**Raspberry Pi Terminal**:
```bash
sudo journalctl -u localfeather -f
```
(Press Ctrl+C to stop)

**Docker**:
```bash
docker-compose logs -f flask
```
(Press Ctrl+C to stop)

---

## Next Steps

### Learn More
- [API Documentation](API.md) - For developers who want to integrate with Local Feather
- [Deployment Guide](DEPLOYMENT.md) - Advanced deployment options
- [Troubleshooting](TROUBLESHOOTING.md) - Solutions to common problems

### Get Help
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) first
- GitHub Issues: Report bugs or request features
- Community Forum: Ask questions, share setups

### Customize
- Add custom sensor types (see firmware examples)
- Create custom dashboards (v2.0 feature)
- Set up alerts for temperature thresholds (v2.0 feature)

---

## Safety & Best Practices

### ESP32 Safety
- ✅ Use official USB power supplies (not cheap knockoffs)
- ✅ Don't cover ESP32 (it needs airflow to stay cool)
- ✅ Keep away from water (unless using waterproof enclosure)
- ❌ Don't exceed 3.3V on GPIO pins
- ❌ Don't connect/disconnect sensors while powered on

### Raspberry Pi Safety
- ✅ Use official Raspberry Pi power supply (5V 3A)
- ✅ Use quality microSD cards (Samsung, SanDisk)
- ✅ Ensure good airflow or add heatsink/fan
- ✅ Safely shut down before unplugging (`sudo shutdown now`)
- ❌ Don't unplug power while running (can corrupt SD card)

### Network Security
- ✅ Use strong passwords for admin account
- ✅ Keep Raspberry Pi updated: `sudo apt update && sudo apt upgrade`
- ✅ Only expose to local network (not internet) unless using HTTPS
- ✅ Change default passwords immediately
- ❌ Don't use "admin/admin" or similar weak credentials

### Data Privacy
- Your data **never leaves your local network**
- No cloud services involved
- You control all data retention
- Export and delete data anytime

---

## Quick Reference

### Important URLs
- **Dashboard**: `http://raspberrypi.local:5000` (or `http://localhost:5000` for Docker)
- **Device Setup**: Connect to `LocalFeather-Setup` WiFi → `http://192.168.4.1`

### Important Commands (Raspberry Pi)
```bash
# Check if service is running
sudo systemctl status localfeather

# Stop service
sudo systemctl stop localfeather

# Start service
sudo systemctl start localfeather

# Restart service
sudo systemctl restart localfeather

# View logs
sudo journalctl -u localfeather -f
```

### Important Commands (Docker)
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

### Default Login
- **Username**: (created during setup)
- **Password**: (created during setup)
- **Reset password**: `flask reset-password <username>` (Raspberry Pi) or `docker-compose exec flask flask reset-password <username>` (Docker)

---

**Need Help?** See the [Troubleshooting Guide](TROUBLESHOOTING.md) or open an issue on GitHub!

**Enjoying Local Feather?** Star the repository on GitHub and share with friends! ⭐
