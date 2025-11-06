# Dependencies for Input Remapper MQTT

## Python Dependencies

### Required Python Packages
- `setuptools` - Build and installation
- `evdev` (>= 1.3.0) - Input device access
- `psutil` - Process utilities
- `pydbus` - D-Bus communication
- `pygobject` - GTK3 Python bindings
- `pydantic` - Configuration validation
- **`paho-mqtt` (>= 1.5.0)** - MQTT client library (NEW)

## System Dependencies (Debian/Ubuntu)

### Required APT Packages

```bash
# Core dependencies
sudo apt install python3-setuptools python3-dev

# Input device handling
sudo apt install python3-evdev

# GUI dependencies
sudo apt install gir1.2-gtk-3.0 gir1.2-gtksource-4 python3-gi

# D-Bus and process utilities
sudo apt install python3-pydbus python3-psutil

# Data validation
sudo apt install python3-pydantic

# MQTT client (CRITICAL - NEW REQUIREMENT)
sudo apt install python3-paho-mqtt

# Build tools
sudo apt install gettext
```

### Optional but Recommended
```bash
# For polkit authentication dialogs
sudo apt install policykit-1

# For udev rules
sudo apt install udev
```

## Important Notes

### About paho-mqtt Installation

**STRONGLY RECOMMENDED: Use system package**
```bash
sudo apt install python3-paho-mqtt
```

**NOT RECOMMENDED: pip installation**
```bash
# Only use if system package unavailable
sudo pip3 install paho-mqtt
```

⚠️ **Warning**: Mixing pip with system Python can cause:
- Conflicts with apt package manager
- Broken system tools
- Dependency resolution issues
- Problems after system updates

### Verifying Installation

Check if all dependencies are available:
```bash
python3 -c "import evdev, paho.mqtt.client, pydbus, gi, pydantic; print('All dependencies OK')"
```

## Dependency Changes from Original

This fork adds **one new dependency**:
- **paho-mqtt** - Required for MQTT publishing to Home Assistant

All other dependencies remain the same as the original input-remapper project.
