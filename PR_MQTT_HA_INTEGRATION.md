# PR: MQTT & Home Assistant Integration

## Overview

This PR transforms input-remapper into an MQTT-based Home Assistant integration tool. Instead of remapping keys to other keys, this version publishes MQTT messages that trigger Home Assistant automations.

**Core functionality:** Button Press → String Action → MQTT Message → Home Assistant Automation

---

## ✅ What's Implemented

### 1. Core MQTT Functionality
- **MQTT Client** (`inputremapper/mqtt_client.py`)
  - Auto-reconnect capability
  - QoS support (0, 1, 2)
  - Configurable retain
  - Thread-safe operations
  - API compatibility (paho-mqtt 1.x and 2.x)

- **MQTT Handler** (`inputremapper/injection/mapping_handlers/mqtt_handler.py`)
  - Replaces KeyHandler
  - Publishes JSON: `{"device_name": "...", "pressed_key": "..."}`
  - Only publishes on press (not release)

### 2. Configuration
- **Config File:** `~/mqtt_config.json`
- **Fields:**
  - `broker` (required): MQTT broker IP/hostname
  - `port` (required): MQTT broker port
  - `username` (required): MQTT username
  - `password` (required): MQTT password
  - `topic` (optional): MQTT topic (default: `key_remap/events`)
  - `qos` (optional): Quality of Service 0-2 (default: 1)
  - `retain` (optional): Retain messages (default: false)
  - `default_device_name` (optional): Override device name
  - `ha_url` (optional): Home Assistant URL for UI buttons

- **Example:** `mqtt_config.json.example` provided

### 3. GUI Integration
- **Settings Dialog** (`inputremapper/gui/components/mqtt_settings_dialog.py`)
  - Edit all MQTT settings
  - Test connection button
  - Save button (writes to `~/mqtt_config.json` and reconnects)

- **Header Bar Buttons** (`inputremapper/gui/user_interface.py`)
  - ⚙️ Settings gear icon: Opens MQTT/HA config dialog
  - 🌐 Network icon: Opens Home Assistant in browser

- **Per-Mapping Automation Buttons** (`inputremapper/gui/components/editor.py`)
  - 🌐 Icon next to each mapping
  - Opens HA automation page for that mapping

### 4. Logging
- **File Logging** (`inputremapper/logging/logger.py`)
  - Location: `~/.local/share/input-remapper-mqtt/logs/app.log`
  - Rotating file handler (10MB max, 5 backups)
  - Logs MQTT events, connections, errors

- **Also supports:** `journalctl -u input-remapper-mqtt -f`

### 5. Coexistence Design
This fork is designed to run **alongside** the original input-remapper without conflicts.

| Component | MQTT Version | Original Version |
|-----------|--------------|------------------|
| **Binaries** | `input-remapper-mqtt-*` | `input-remapper-*` |
| **Service** | `input-remapper-mqtt.service` | `input-remapper.service` |
| **D-Bus** | `inputremapper.mqtt.Control` | `inputremapper.Control` |
| **MQTT Config** | `~/mqtt_config.json` | N/A |
| **Logs** | `~/.local/share/input-remapper-mqtt/logs/` | `~/.local/share/input-remapper/logs/` |
| **Presets** | `~/.config/input-remapper-2/` | `~/.config/input-remapper-2/` (shared) |

---

## 🧪 Tests Run

### Unit Tests: ✅ 12/12 PASSING
```bash
$ python3 -m unittest tests.unit.test_mqtt_client
Ran 12 tests in 0.010s
OK
```

**Coverage:**
- MQTTConfig initialization, loading, saving, validation
- MQTTClient initialization, API compatibility, error handling
- Publishing with auto-connect
- Connection testing

### Static Analysis: ✅ ALL MODULES COMPILE
```bash
$ python3 -m py_compile inputremapper/mqtt_client.py \
                      inputremapper/gui/components/mqtt_settings_dialog.py \
                      inputremapper/gui/user_interface.py \
                      inputremapper/injection/mapping_handlers/mqtt_handler.py
✓ All modules compile successfully
```

---

## 📦 Installation

### Prerequisites (Debian/Ubuntu/Raspberry Pi OS)
```bash
sudo apt update && sudo apt install -y \
    python3-evdev \
    python3-gi \
    python3-paho-mqtt \
    python3-pydbus \
    python3-psutil \
    python3-pydantic \
    python3-setuptools \
    gettext
```

**⚠️ CRITICAL:** Use `apt` to install `python3-paho-mqtt`, **NOT pip**

### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/Qutaiba-Khader/input-remapper-mqtt.git
cd input-remapper-mqtt

# 2. Checkout this PR branch
git checkout mqtt-ha-integration

# 3. Install
sudo python3 setup.py install

# 4. Enable service
sudo systemctl daemon-reload
sudo systemctl enable --now input-remapper-mqtt

# 5. Verify service is running
sudo systemctl status input-remapper-mqtt

# 6. Configure MQTT
cp mqtt_config.json.example ~/mqtt_config.json
nano ~/mqtt_config.json
# Edit: broker, port, username, password, ha_url

# 7. Launch GUI
input-remapper-mqtt-gtk
```

### Installation Scenarios

**Scenario 1: Fresh Install (no original input-remapper)**
- Follow steps above
- Only `input-remapper-mqtt` will be installed

**Scenario 2: Alongside Original input-remapper**
- Follow steps above
- Both services can run simultaneously
- Use original for key remapping, MQTT version for Home Assistant
- Both share preset directory (intentional)

**Scenario 3: Replacing Original input-remapper**
- Disable original first: `sudo systemctl disable --now input-remapper`
- Then follow installation steps above

---

## 🏠 Home Assistant Integration

### Example Automation

```yaml
automation:
  - alias: "Living Room Remote - Toggle Lights"
    trigger:
      - platform: mqtt
        topic: "key_remap/events"
    condition:
      - condition: template
        value_template: >
          {{ trigger.payload_json.device_name == "living_room_remote" and
             trigger.payload_json.pressed_key == "toggle_lights" }}
    action:
      - service: light.toggle
        target:
          entity_id: light.living_room
```

### Testing MQTT Messages

**Monitor with mosquitto_sub:**
```bash
mosquitto_sub -h YOUR_BROKER -p 1883 -u USER -P PASS -t 'key_remap/events' -v
```

**Expected output when button pressed:**
```json
key_remap/events {"device_name": "my_device", "pressed_key": "toggle_lights"}
```

---

## 🐛 Debugging

### View Logs

**Application log file:**
```bash
tail -f ~/.local/share/input-remapper-mqtt/logs/app.log
```

**systemd service logs:**
```bash
sudo journalctl -u input-remapper-mqtt -f
```

### Common Issues

**MQTT not connecting:**
- Check logs: `tail -f ~/.local/share/input-remapper-mqtt/logs/app.log`
- Verify broker reachable: `ping YOUR_BROKER`
- Test credentials: `mosquitto_pub -h BROKER -u USER -P PASS -t test -m "test"`

**No messages published:**
- Verify device mapped in GUI
- Check service status: `sudo systemctl status input-remapper-mqtt`
- Look for errors in logs

**Home Assistant not receiving:**
- Verify topic matches in HA automation
- Check MQTT integration in HA (Settings → Devices & Services → MQTT)
- Use MQTT Explorer or mosquitto_sub to verify messages

---

## 📋 Files Changed

### Core Implementation
```
inputremapper/mqtt_client.py                              # MQTT client & config
inputremapper/injection/mapping_handlers/mqtt_handler.py  # MQTT publishing
inputremapper/gui/components/mqtt_settings_dialog.py      # Settings UI
inputremapper/gui/user_interface.py                       # UI integration
inputremapper/gui/components/editor.py                    # Automation buttons
inputremapper/logging/logger.py                           # File logging
inputremapper/daemon.py                                   # D-Bus name update
```

### Configuration
```
mqtt_config.json.example                                  # Example config
data/input-remapper-mqtt.service                          # systemd service
data/inputremapper.mqtt.Control.conf                      # D-Bus policy
```

### Documentation
```
README.md                                                 # Complete docs
INSTALL.md                                                # Installation guide
DEPENDENCIES.md                                           # Dependency list
```

### Tests
```
tests/unit/test_mqtt_client.py                            # 12 unit tests
```

---

## ✅ Validation Checklist

- [x] Unit tests passing (12/12)
- [x] All modules compile without errors
- [x] Configuration files consistent
- [x] D-Bus name unique (`inputremapper.mqtt.Control`)
- [x] Service name unique (`input-remapper-mqtt.service`)
- [x] Binaries renamed (`input-remapper-mqtt-*`)
- [x] Documentation complete (README, INSTALL, DEPENDENCIES)
- [x] Coexistence design verified
- [x] Log paths separated (`~/.local/share/input-remapper-mqtt/`)
- [ ] **Hardware testing pending** (requires real MQTT broker, devices, HA)

---

## ⚠️ What Requires Hardware Testing

Cannot be tested in development environment:
1. MQTT broker connectivity over network
2. GTK UI rendering and button clicks
3. Physical input device event handling
4. systemd service operation
5. End-to-end: button press → MQTT message → HA automation

**Recommendation:** Test on Debian/Ubuntu/Raspberry Pi OS with:
- MQTT broker running (Mosquitto, etc.)
- Home Assistant with MQTT integration
- Physical input device (keyboard, remote, gamepad)

---

## 📄 Design Decisions

### Why Coexist Instead of Replace?
Users may want both versions:
- Original for key remapping (e.g., remap CapsLock to Ctrl)
- MQTT version for Home Assistant (e.g., remote buttons → smart home)

### Why Share Preset Directory?
Allows using same device mappings in both versions. MQTT-specific settings (broker, HA URL) stored separately in `~/mqtt_config.json`.

### Why QoS 1 Default?
Ensures messages delivered at least once. Higher QoS (2) adds overhead without benefit for button press events.

### Why Only Publish on Press?
Reduces MQTT traffic by 50%. Most HA automations respond to single events, not press+release pairs.

---

## 🔗 Related Documentation

- **Installation Guide:** [INSTALL.md](INSTALL.md)
- **Dependencies:** [DEPENDENCIES.md](DEPENDENCIES.md)
- **Implementation Status:** [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

---

**This PR is ready for review and hardware testing.**

All code is implemented, tested, and documented. The only remaining validation requires real hardware and network setup.
