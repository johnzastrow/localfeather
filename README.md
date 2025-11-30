# Local Feather

**Get data from ESP32 sensor devices straight into your own database — no cloud required.**

Local Feather is a self-hosted environmental monitoring system designed for home hobbyists and small offices. Deploy sensors around your space, collect temperature, humidity, pressure, and more — all stored locally on your network.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ESP32](https://img.shields.io/badge/ESP32-Supported-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)]()

---

## ✨ Features

- 🌡️ **Multiple Sensors Supported** - BME280, AHT20, DHT22, DS18B20, analog sensors, and more
- 📡 **Easy WiFi Setup** - Captive portal configuration (no code changes needed)
- 🔄 **Over-the-Air Updates** - Update firmware wirelessly from the web interface
- 📊 **Real-Time Visualization** - Charts and graphs of your sensor data
- 🏠 **100% Local** - All data stays on your network, no cloud dependencies
- 🔒 **Secure** - API key authentication, optional HTTPS, user access control
- 🚀 **Simple Installation** - One-command setup on Raspberry Pi
- 📱 **Web Dashboard** - Monitor all devices from any browser

---

## 🎯 Project Status

| Component | Status | Version |
|-----------|--------|---------|
| **ESP32 Firmware** | ✅ Complete | v1.0.0 |
| **Flask Server** | ⏳ Planned | - |
| **Web UI** | ⏳ Planned | - |
| **Database** | ⏳ Planned | - |
| **Deployment** | ⏳ Planned | - |

**Current Progress:** Firmware complete with full OTA support. Server implementation coming next.

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and [TODO.md](TODO.md) for planned features.

---

## 🚀 Quick Start

### Hardware You'll Need

- **Server:** Raspberry Pi 3/4 (or any Linux machine)
- **Sensors:** One or more ESP32 boards with sensors
  - [ESP32 Dev Module](https://www.adafruit.com/category/288) (~$10)
  - [BME280 Sensor](https://www.adafruit.com/product/2652) (~$20) or [AHT20 Sensor](https://www.adafruit.com/product/4566) (~$5)

### Installation (Server - Coming Soon)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/localfeather.git
cd localfeather

# Run installation script (Raspberry Pi / Ubuntu)
sudo ./install.sh

# Or use Docker Compose
docker-compose up -d
```

**Note:** Server implementation is not yet complete. For now, you can flash the ESP32 firmware and prepare your hardware.

### ESP32 Firmware Setup (Available Now)

See the complete guide: **[firmware/README.md](firmware/README.md)**

**Quick version:**

```bash
# Install PlatformIO
pip install platformio

# Flash firmware
cd firmware
pio run --target upload

# Monitor output
pio device monitor
```

Then connect to the `LocalFeather-XXXXXX` WiFi network and configure via captive portal.

---

## 📚 Documentation

### Getting Started
- **[Setup Guide](docs/SETUP.md)** - Complete step-by-step installation for non-technical users
- **[Firmware README](firmware/README.md)** - ESP32 firmware installation and configuration
- **[OTA Update Guide](firmware/docs/OTA_GUIDE.md)** - How to update devices wirelessly

### Reference
- **[Requirements](docs/REQUIREMENTS.md)** - Project requirements and user stories
- **[Design Document](docs/DESIGN.md)** - Architecture and technology stack
- **[API Documentation](docs/API.md)** - Complete API specification
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common problems and solutions

### Development
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[TODO.md](TODO.md)** - Planned features and roadmap
- **[CLAUDE.md](CLAUDE.md)** - Development guide for AI assistants
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - How to contribute (coming soon)

---

## 🏗️ Architecture

Local Feather uses a simple three-component architecture:

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   ESP32 Device  │  HTTPS  │  Flask Server   │   SQL   │    MariaDB      │
│   (Firmware)    │────────>│  (Python 3.9+)  │<───────>│   (Database)    │
│                 │  POST   │                 │         │                 │
│ - WiFiManager   │         │ - API Endpoints │         │ - Readings      │
│ - Sensors       │         │ - Web UI        │         │ - Devices       │
│ - OTA Updates   │         │ - Auth          │         │ - Users         │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

**Technology Stack:**
- **Firmware:** ESP32 + Arduino framework + PlatformIO
- **Backend:** Flask 3.x + Gunicorn
- **Frontend:** Jinja2 templates + HTMX + Tailwind CSS
- **Database:** MariaDB 10.5+ (SQLite for development)
- **Visualization:** Chart.js
- **Deployment:** Docker Compose or systemd

See [DESIGN.md](docs/DESIGN.md) for complete architecture details.

---

## 🔌 Supported Sensors

### Out of the Box
- **BME280** - Temperature, humidity, pressure (I2C)
- **AHT20** - Temperature, humidity (I2C) - [Adafruit #4566](https://www.adafruit.com/product/4566)

### Easy to Add (Examples Included)
- **DHT22** - Temperature, humidity (GPIO)
- **DS18B20** - Waterproof temperature (OneWire)
- **Analog Sensors** - Soil moisture, light (LDR), voltage
- **Multiple Sensors** - Combine several sensors on one ESP32

See [firmware/examples/](firmware/examples/) for complete code examples.

---

## 💡 Use Cases

- **Home Environmental Monitoring** - Track temperature and humidity in different rooms
- **Greenhouse/Garden** - Monitor soil moisture, temperature, and light levels
- **Aquarium/Terrarium** - Water temperature and room conditions
- **Server Room** - Temperature monitoring with email alerts
- **Weather Station** - Outdoor temperature, humidity, and pressure
- **HVAC Optimization** - Track heating/cooling efficiency
- **Research/Education** - Data logging for science projects

---

## 🛠️ Development

### Prerequisites

```bash
# For Firmware Development
- PlatformIO (VS Code extension recommended)
- ESP32 board with USB cable

# For Server Development (Coming Soon)
- Python 3.9+
- MariaDB 10.5+ or SQLite
- Node.js (for Tailwind CSS build)
```

### Project Structure

```
localfeather/
├── firmware/              # ESP32 firmware (PlatformIO)
│   ├── src/              # Main firmware code
│   ├── examples/         # Sensor examples
│   └── docs/             # Firmware-specific docs
├── server/               # Flask server (Coming Soon)
│   ├── app/              # Application code
│   ├── templates/        # Jinja2 templates
│   └── static/           # CSS, JS assets
├── docs/                 # Documentation
├── docker/               # Docker configuration
└── scripts/              # Installation scripts
```

### Running Tests (Coming Soon)

```bash
# Server tests
pytest

# Firmware tests
pio test
```

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) (coming soon).

**Ways to help:**
- 🐛 Report bugs or issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🧪 Test on different hardware
- 🌍 Translate documentation

---

## 📋 Roadmap

### v1.0 (Current)
- [x] ESP32 firmware with WiFiManager
- [x] BME280 and AHT20 sensor support
- [x] Full OTA update implementation
- [x] Sensor examples (DHT22, DS18B20, analog)
- [x] Complete documentation
- [ ] Flask server implementation
- [ ] MariaDB schema
- [ ] Web UI with HTMX
- [ ] Docker deployment

### v2.0 (Future)
- [ ] Alert system (email/webhook)
- [ ] Deep sleep for battery operation
- [ ] Multi-user support with roles
- [ ] Advanced analytics
- [ ] Mobile app

### v3.0 (Ideas)
- [ ] Cloud backup (optional)
- [ ] Machine learning anomaly detection
- [ ] Plugin system for custom sensors

See [TODO.md](TODO.md) for complete feature list.

---

## 📊 Example Screenshots

*Coming soon once the web UI is implemented!*

---

## ❓ FAQ

**Q: Do I need programming experience?**
A: No! The setup guide is designed for non-technical users. Just follow the step-by-step instructions.

**Q: Does this require an internet connection?**
A: Only for initial setup and OTA updates. All data storage and monitoring is 100% local.

**Q: How many devices can I connect?**
A: Designed for 5-20 devices, but can scale higher with proper database configuration.

**Q: What if I don't have a Raspberry Pi?**
A: Any Linux machine works. We also provide Docker images for easy deployment.

**Q: Can I use different sensors?**
A: Yes! We provide examples for common sensors, and it's easy to add your own.

**Q: Is this secure?**
A: Yes. API key authentication, optional HTTPS, and all data stays on your local network.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with these excellent open-source projects:
- [Arduino ESP32](https://github.com/espressif/arduino-esp32)
- [WiFiManager](https://github.com/tzapu/WiFiManager) by tzapu
- [ArduinoJson](https://arduinojson.org/) by Benoit Blanchon
- [Adafruit Sensor Libraries](https://github.com/adafruit)
- [Flask](https://flask.palletsprojects.com/)
- [HTMX](https://htmx.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Chart.js](https://www.chartjs.org/)

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/localfeather/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/localfeather/discussions)
- **Documentation:** [docs/](docs/)

---

**Made with ❤️ for the open-source hardware community**

*Last updated: 2025-11-30*
