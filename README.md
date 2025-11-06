<p align="center"><img src="data/input-remapper.svg" width=100/></p>

<h1 align="center">Input Remapper MQTT</h1>

<p align="center">
  <strong>🏠 MQTT-based Home Assistant Integration</strong><br/>
  Transform any input device into a Home Assistant controller via MQTT.<br/>
  Map buttons, keys, and inputs to string actions that trigger automations in Home Assistant.
</p>

<p align="center">
  <strong>⚠️ This is a fork of the original input-remapper project.</strong><br/>
  Instead of remapping keys to other keys, this version publishes MQTT messages to Home Assistant.<br/>
  <strong>Both versions can coexist on the same system!</strong>
</p>

<p align="center">
  <a href="INSTALL.md">📥 Installation</a> |
  <a href="DEPENDENCIES.md">📦 Dependencies</a> |
  <a href="#-home-assistant-integration">🏠 Home Assistant Setup</a> |
  <a href="#-debugging-and-logs">🐛 Debugging</a>
</p>

<br/>

## 🚀 Quick Start

```bash
# 1. Install dependencies (Debian/Ubuntu)
sudo apt install -y python3-evdev python3-gi python3-paho-mqtt python3-pydbus python3-psutil python3-pydantic

# 2. Clone and install
git clone https://github.com/Qutaiba-Khader/input-remapper-mqtt.git
cd input-remapper-mqtt
sudo python3 setup.py install

# 3. Enable service
sudo systemctl daemon-reload
sudo systemctl enable --now input-remapper-mqtt

# 4. Configure MQTT
cp mqtt_config.json.example ~/mqtt_config.json
nano ~/mqtt_config.json  # Edit with your broker details

# 5. Launch GUI
input-remapper-mqtt-gtk
```

📖 **[Full Installation Guide →](INSTALL.md)**

<br/>

## ✨ Key Features

- 🔘 **Button → String → MQTT**: Map any input to a custom string action
- 🏠 **Home Assistant Ready**: JSON payloads designed for HA automations
- 🔄 **Auto-Reconnect**: Robust MQTT connection handling
- 🎛️ **UI Configuration**: Edit all settings from the GUI
- 📊 **File Logging**: Rotating logs for easy debugging
- 🤝 **Coexists Peacefully**: Run alongside original input-remapper
- 🔐 **No Sudo Needed**: Systemd service handles permissions

<br/>

## 🏠 Home Assistant Integration

This version of input-remapper is **specifically designed** to integrate with Home Assistant via MQTT. When you press a button on your input device (keyboard, remote, game controller, etc.), it publishes an MQTT message to your Home Assistant broker with a custom string action that you define.

### How It Works

1. **Map buttons to strings**: Instead of remapping Button A to Button B, you map Button A to a string like `"toggle_living_room_lights"`
2. **MQTT publishing**: When you press the button, an MQTT JSON message is published to your Home Assistant broker
3. **Home Assistant automation**: Create automations in Home Assistant that trigger on these MQTT messages

### Example Use Cases

- 🎮 Use a wireless numpad as a Home Assistant scene controller
- 📺 Turn an old TV remote into a smart home controller
- 🕹️ Map gamepad buttons to control lights, media, or any Home Assistant entity
- ♿ Create custom input devices for accessibility needs

<br/>

## 📡 MQTT Configuration

### Creating the Configuration File

Create a file at `~/mqtt_config.json` with your MQTT broker settings:

```bash
cp mqtt_config.json.example ~/mqtt_config.json
nano ~/mqtt_config.json
```

**Example configuration:**

```json
{
  "broker": "192.168.1.160",
  "port": 1883,
  "username": "mqttuser",
  "password": "mqttuser",
  "topic": "key_remap/events",
  "qos": 1,
  "retain": false,
  "default_device_name": "living_room_remote",
  "ha_url": "http://192.168.1.160:8123"
}
```

### Configuration Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `broker` | **Yes** | - | IP address or hostname of your MQTT broker |
| `port` | **Yes** | - | MQTT broker port (usually 1883) |
| `username` | **Yes** | - | MQTT username |
| `password` | **Yes** | - | MQTT password |
| `topic` | No | `key_remap/events` | MQTT topic to publish to |
| `qos` | No | `1` | MQTT Quality of Service (0, 1, or 2) |
| `retain` | No | `false` | Whether messages should be retained |
| `default_device_name` | No | - | Override auto-detected device name |
| `ha_url` | No | - | Home Assistant URL (e.g., `http://192.168.1.160:8123`) |

### Editing Configuration

You can edit the configuration in **two ways**:

**Option 1: GUI Settings Dialog** (Recommended)
1. Launch `input-remapper-mqtt-gtk`
2. Click the **gear icon** (⚙️) in the header bar
3. Edit all fields in the Settings dialog:
   - MQTT broker, port, username, password
   - Topic, QoS, retain settings
   - Default device name
   - Home Assistant URL
4. Click **"Test MQTT"** to verify connection
5. Click **"Save"** to apply changes (saves to `~/mqtt_config.json` and reconnects MQTT client)

**Option 2: Manual File Editing**
```bash
nano ~/mqtt_config.json
```

After manual edits, restart the service:
```bash
sudo systemctl restart input-remapper-mqtt
```

### MQTT Payload Format

Every button press publishes a JSON message to the configured topic:

```json
{
  "device_name": "living_room_remote",
  "pressed_key": "toggle_govee_m1_small"
}
```

- `device_name`: The name of your input device (auto-detected or from config)
- `pressed_key`: The string action you configured in the UI

<br/>

## 🤖 Home Assistant Setup

### 1. Ensure MQTT Integration is Configured

In Home Assistant, go to **Settings → Devices & Services → MQTT** and ensure your MQTT broker is configured.

### 2. Create an Automation

Create an automation that triggers on MQTT messages. Here's an example:

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

  - alias: "Living Room Remote - Play/Pause"
    trigger:
      - platform: mqtt
        topic: "key_remap/events"
    condition:
      - condition: template
        value_template: >
          {{ trigger.payload_json.device_name == "living_room_remote" and
             trigger.payload_json.pressed_key == "play_pause" }}
    action:
      - service: media_player.media_play_pause
        target:
          entity_id: media_player.living_room_tv
```

### 3. Tips for Automation Design

- **Use descriptive action strings**: Instead of `"btn1"`, use `"toggle_living_room_lights"`
- **Group by device**: Filter by `device_name` to handle multiple remotes
- **Use snake_case**: e.g., `"volume_up"`, `"scene_movie_time"`
- **Test with MQTT Explorer**: Use [MQTT Explorer](http://mqtt-explorer.com/) to verify messages are being published

<br/>

## 🔧 Installation

### Installation Overview

This MQTT version is designed to **coexist** with the original input-remapper. You can have both installed on the same system without conflicts.

**What's different:**
- Binaries: `input-remapper-mqtt-gtk`, `input-remapper-mqtt-service` (vs `input-remapper-gtk`, `input-remapper-service`)
- Systemd service: `input-remapper-mqtt.service` (vs `input-remapper.service`)
- D-Bus name: `inputremapper.mqtt.Control` (vs `inputremapper.Control`)
- Config directory: **Shared** - Both use `~/.config/input-remapper-2/`

**Installation scenarios:**

1. **Fresh install (no original input-remapper)**: Follow the Quick Install steps below
2. **Alongside original input-remapper**: Both can run simultaneously - use original for key remapping, MQTT version for Home Assistant
3. **Replacing original**: Disable the original service first: `sudo systemctl disable --now input-remapper`

### Quick Install (Debian/Ubuntu/Raspberry Pi OS)

**Step 1: Install Dependencies**

⚠️ **CRITICAL**: Use `apt` to install `python3-paho-mqtt`, **NOT pip**. System-level MQTT library is required for proper permissions.

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

**Step 2: Clone and Install**

```bash
git clone https://github.com/Qutaiba-Khader/input-remapper-mqtt.git
cd input-remapper-mqtt
sudo python3 setup.py install
```

**Step 3: Enable Service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now input-remapper-mqtt
```

**Step 4: Configure MQTT**

```bash
cp mqtt_config.json.example ~/mqtt_config.json
nano ~/mqtt_config.json  # Edit with your broker details
```

**Step 5: Launch GUI**

```bash
input-remapper-mqtt-gtk
```

📖 **[Detailed Installation Guide with Troubleshooting →](INSTALL.md)**

<br/>

## 📝 Usage Notes

### UI Changes

The MQTT version includes several UI enhancements:

**Header Bar Buttons:**
- **⚙️ Settings** (gear icon): Open MQTT & Home Assistant configuration dialog
- **🌐 Open HA** (network icon): Open Home Assistant in your browser (uses `ha_url` from config)

**Mapping Editor:**
- The "Output Key" field now accepts any string (your MQTT action)
- Instead of selecting a key from a dropdown, type your action string
- Examples: `toggle_lights`, `play_pause`, `scene_movie_night`
- The string you enter will be sent as the `pressed_key` in the MQTT payload

**Per-Mapping Automation Buttons:**
- When a mapping is selected, a **🌐 network icon** appears next to the edit button
- Click it to quickly open the Home Assistant automation page for creating automations for that mapping

### MQTT Action String Guidelines

- Use lowercase with underscores (snake_case): `toggle_bedroom_lights`
- Be descriptive: `play_pause` is better than `pp`
- Group by function: `light_`, `media_`, `scene_`
- Keep them short but meaningful

### Device Names

The `device_name` in MQTT payloads comes from:
1. The actual device name (auto-detected from the input device)
2. Or the `default_device_name` from your MQTT config

This allows you to have multiple devices publishing to the same topic and distinguish them in Home Assistant automations.

<br/>

## 🐛 Debugging and Logs

### Log File Location

Input Remapper MQTT automatically logs to a **rotating log file** at:

```
~/.local/share/input-remapper-mqtt/logs/app.log
```

**Log rotation settings:**
- Maximum file size: 10 MB
- Backup files: 5 (app.log.1, app.log.2, etc.)
- Oldest logs are automatically deleted when limit is reached

### Viewing Logs

**View the main log file:**
```bash
tail -f ~/.local/share/input-remapper-mqtt/logs/app.log
```

**View systemd service logs:**
```bash
# Follow service logs in real-time
sudo journalctl -u input-remapper-mqtt -f

# View last 100 lines
sudo journalctl -u input-remapper-mqtt -n 100

# View logs since last boot
sudo journalctl -u input-remapper-mqtt -b
```

### What Gets Logged

The log file captures:
- ✅ MQTT connection/disconnection events
- ✅ Device names and pressed keys (MQTT payloads)
- ✅ Configuration loading/saving
- ✅ Errors and warnings
- ✅ Button press events and mapping activations

### Enabling Debug Logging

For more verbose output, edit the logger configuration in your installation:

```bash
# Edit logger configuration
sudo nano /usr/lib/python3/dist-packages/inputremapper/logging/logger.py
```

Look for the logging level and change it to `DEBUG`:
```python
logger.setLevel(logging.DEBUG)
```

Then restart the service:
```bash
sudo systemctl restart input-remapper-mqtt
```

### Testing MQTT Messages

**Method 1: MQTT Explorer** (GUI)
- Download [MQTT Explorer](http://mqtt-explorer.com/)
- Connect to your broker
- Watch for messages on `key_remap/events` topic

**Method 2: mosquitto_sub** (CLI)
```bash
# Subscribe to all events
mosquitto_sub -h 192.168.1.160 -p 1883 \
  -u mqttuser -P mqttpassword \
  -t 'key_remap/events' -v
```

Press buttons on your mapped device and you should see:
```
key_remap/events {"device_name": "my_keyboard", "pressed_key": "toggle_lights"}
```

### Common Issues

**Issue: MQTT not connecting**
- Check logs: `tail -f ~/.local/share/input-remapper-mqtt/logs/app.log`
- Verify broker is reachable: `ping 192.168.1.160`
- Test credentials: `mosquitto_pub -h 192.168.1.160 -u mqttuser -P mqttpassword -t test -m "test"`

**Issue: No messages published**
- Verify device is mapped: Check GUI for active mappings
- Check service status: `sudo systemctl status input-remapper-mqtt`
- Look for errors in logs

**Issue: Home Assistant not receiving**
- Verify topic in HA automation matches config
- Check MQTT integration in HA: Settings → Devices & Services → MQTT
- Use MQTT Explorer to verify messages are actually being published

<br/>

## 🔐 Permissions & systemd Service

### How Permissions Work

Input Remapper MQTT uses a systemd service to handle privileged operations:

- **GUI (`input-remapper-mqtt-gtk`)**: Runs as your user, no sudo needed
- **Service (`input-remapper-mqtt.service`)**: Runs with elevated privileges, handles:
  - Reading from `/dev/input/*` devices
  - Publishing MQTT messages
  - Loading configurations

### Service Management

```bash
# Start/stop service
sudo systemctl start input-remapper-mqtt
sudo systemctl stop input-remapper-mqtt

# Enable/disable autostart
sudo systemctl enable input-remapper-mqtt
sudo systemctl disable input-remapper-mqtt

# Check status
sudo systemctl status input-remapper-mqtt

# View logs
sudo journalctl -u input-remapper-mqtt -f
```

### udev Rules

The included udev rules (`99-input-remapper.rules`) allow the service to access input devices without running as root. These are automatically installed to `/usr/lib/udev/rules.d/`.

## 🆚 Comparison: Original vs MQTT Fork

| Feature | Original input-remapper | input-remapper-mqtt |
|---------|------------------------|---------------------|
| **Purpose** | Remap keys to other keys | Trigger Home Assistant automations |
| **Output** | Injected key events | MQTT JSON messages |
| **Use Case** | Keyboard/gamepad remapping | Smart home control |
| **Config** | GUI + presets | GUI + presets + MQTT config |
| **Dependencies** | evdev, GTK, pydbus | + paho-mqtt |
| **Installation** | Can coexist | Yes, different binaries |
| **Service Name** | `input-remapper.service` | `input-remapper-mqtt.service` |

## 📚 Additional Documentation

- [**INSTALL.md**](INSTALL.md) - Detailed installation guide with coexistence scenarios
- [**DEPENDENCIES.md**](DEPENDENCIES.md) - Complete dependency list and installation notes
- [**IMPLEMENTATION_STATUS.md**](IMPLEMENTATION_STATUS.md) - Current implementation status

## 🤝 Contributing

This is a fork specifically designed for MQTT/Home Assistant integration. For the original project, see [sezanzeb/input-remapper](https://github.com/sezanzeb/input-remapper).

## 📜 License

GPL-3.0 - Same as the original input-remapper project.

Original project by [sezanzeb](https://github.com/sezanzeb/input-remapper).
MQTT fork by [Qutaiba-Khader](https://github.com/Qutaiba-Khader/input-remapper-mqtt).

---

**Ready to get started?** → [Installation Guide](INSTALL.md)
