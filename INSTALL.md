# Installation Guide - Input Remapper MQTT

## Quick Start (Debian/Ubuntu/Raspberry Pi OS)

### Prerequisites
- Debian 11+, Ubuntu 22.04+, or Raspberry Pi OS (current)
- Python 3.9 or later
- Active MQTT broker (e.g., Mosquitto on Home Assistant)

### Installation Steps

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y \
    python3-setuptools \
    python3-dev \
    python3-evdev \
    gir1.2-gtk-3.0 \
    gir1.2-gtksource-4 \
    python3-gi \
    python3-pydbus \
    python3-psutil \
    python3-pydantic \
    python3-paho-mqtt \
    gettext

# 2. Clone this repository
git clone https://github.com/Qutaiba-Khader/input-remapper-mqtt.git
cd input-remapper-mqtt

# 3. Build and install
./scripts/build.sh
sudo apt install -f ./dist/input-remapper-mqtt-*.deb

# OR install directly without building .deb:
# sudo python3 setup.py install

# 4. Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable input-remapper-mqtt
sudo systemctl start input-remapper-mqtt

# 5. Create MQTT configuration
cp mqtt_config.json.example ~/mqtt_config.json
nano ~/mqtt_config.json
# Edit with your MQTT broker details
```

### Post-Installation

1. **Launch the GUI**:
   ```bash
   input-remapper-mqtt-gtk
   ```

2. **Configure MQTT Settings** (in GUI):
   - Settings → MQTT & HA Settings
   - Enter your broker IP, port, username, password
   - Enter your Home Assistant URL
   - Click "Test MQTT" to verify connection
   - Click "Save"

3. **Create Your First Mapping**:
   - Select your input device
   - Create a new preset
   - Record a button press
   - Enter an MQTT action string (e.g., "toggle_lights")
   - Apply the preset

4. **Test**:
   ```bash
   # In one terminal, subscribe to MQTT
   mosquitto_sub -h YOUR_BROKER_IP -p 1883 -u mqttuser -P mqttuser -t 'key_remap/events' -v

   # Press your mapped button and verify the message appears
   ```

## Coexistence with Original input-remapper

### Can I run both?

**YES!** This fork is designed to coexist peacefully with the original input-remapper.

### How it works:

| Component | Original | MQTT Fork |
|-----------|----------|-----------|
| Package name | `input-remapper` | `input-remapper-mqtt` |
| Binaries | `input-remapper-gtk` | `input-remapper-mqtt-gtk` |
| Service | `input-remapper.service` | `input-remapper-mqtt.service` |
| D-Bus name | `inputremapper.Control` | `inputremapper.mqtt.Control` |
| Config dir | `~/.config/input-remapper-2/` | `~/.config/input-remapper-2/` (shared) |
| Desktop entry | Input Remapper | Input Remapper MQTT |

### Shared vs Separate:

**Shared** (both use the same):
- Configuration directory `~/.config/input-remapper-2/`
- Preset files
- udev rules
- polkit policies

**Separate** (no conflicts):
- Binary names (`-mqtt` suffix)
- Systemd services (different names)
- D-Bus services (different names)
- Desktop launchers (different names)

### Installation Scenarios:

**Scenario 1: I want ONLY the MQTT version**
```bash
# If original is installed, you can keep it or remove it
sudo apt remove input-remapper  # Optional

# Install MQTT version
sudo python3 setup.py install
sudo systemctl enable input-remapper-mqtt
```

**Scenario 2: I want BOTH versions**
```bash
# Keep original installed
# Install MQTT version alongside
sudo python3 setup.py install

# Both services can run simultaneously:
sudo systemctl enable input-remapper
sudo systemctl enable input-remapper-mqtt

# Use different presets for each
```

**Scenario 3: I want to switch between them**
```bash
# Use only one service at a time
sudo systemctl stop input-remapper
sudo systemctl disable input-remapper
sudo systemctl enable input-remapper-mqtt
sudo systemctl start input-remapper-mqtt
```

### Important Notes:

- ⚠️ **Presets are shared**: Both versions read from `~/.config/input-remapper-2/presets/`
- ✅ **No file conflicts**: Different binary names prevent overwrites
- ✅ **No service conflicts**: Different service names allow both to run
- ⚠️ **Device access**: Only one service should handle a device at a time

## Verifying Installation

```bash
# Check if binaries are installed
which input-remapper-mqtt-gtk
which input-remapper-mqtt-service

# Check if service is installed
systemctl status input-remapper-mqtt

# Check if dependencies are satisfied
python3 -c "import evdev, paho.mqtt.client, pydbus, gi, pydantic; print('✓ All dependencies OK')"

# Check MQTT connection (requires ~/mqtt_config.json)
input-remapper-mqtt-gtk  # Use Settings → Test MQTT
```

## Logs

```bash
# Service logs
sudo journalctl -u input-remapper-mqtt -f

# Application logs
tail -f ~/.local/share/input-remapper-mqtt/logs/app.log

# Enable debug mode
input-remapper-mqtt-gtk --debug
```

## Uninstallation

```bash
# Stop and disable service
sudo systemctl stop input-remapper-mqtt
sudo systemctl disable input-remapper-mqtt

# Remove package
sudo apt remove input-remapper-mqtt

# Clean up config (optional)
rm -rf ~/.config/input-remapper-2/
rm -rf ~/.local/share/input-remapper-mqtt/
rm ~/mqtt_config.json
```

## Troubleshooting

### "MQTT client not initialized"
- Create `~/mqtt_config.json` with your broker settings
- Use Settings dialog to configure and save

### "Failed to connect to MQTT broker"
- Verify broker IP and port
- Check username/password
- Test with: `mosquitto_pub -h IP -p 1883 -u user -P pass -t test -m test`

### "ImportError: No module named paho.mqtt"
```bash
sudo apt install python3-paho-mqtt
sudo systemctl restart input-remapper-mqtt
```

### Permission errors accessing /dev/input/*
```bash
# Restart udev and re-plug device
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Next Steps

1. Configure your MQTT broker details
2. Set up a test mapping
3. Create Home Assistant automations (see README.md)
4. Enjoy your MQTT-powered input devices!
