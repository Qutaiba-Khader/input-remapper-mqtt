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
  "default_device_name": "living_room_remote"
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
2. Go to **Settings → MQTT & HA Settings**
3. Edit all fields in the form
4. Click **"Test MQTT"** to verify connection
5. Click **"Save"** to apply changes

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

### Quick Install (Debian/Ubuntu/Raspberry Pi OS)

```bash
# Install dependencies
sudo apt update && sudo apt install -y \
    python3-evdev python3-gi python3-paho-mqtt \
    python3-pydbus python3-psutil python3-pydantic \
    python3-setuptools gettext

# Clone and install
git clone https://github.com/Qutaiba-Khader/input-remapper-mqtt.git
cd input-remapper-mqtt
sudo python3 setup.py install

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable --now input-remapper-mqtt
```

📖 **[Detailed Installation Instructions →](INSTALL.md)**

### Coexistence with Original Input-Remapper

**Good news**: This MQTT version can run **alongside** the original input-remapper!

- ✅ Different binaries: `input-remapper-mqtt-gtk` vs `input-remapper-gtk`
- ✅ Different services: `input-remapper-mqtt.service` vs `input-remapper.service`
- ✅ Different D-Bus names: No conflicts
- ⚠️ Shared config directory: Both use `~/.config/input-remapper-2/`

You can have both installed and use them for different purposes:
- **Original** for key remapping
- **MQTT version** for Home Assistant integration

📖 **[Coexistence Guide →](INSTALL.md#coexistence-with-original-input-remapper)**

<br/>

```bash
# Subscribe to all events
mosquitto_sub -h 192.168.1.160 -p 1883 -u mqttuser -P mqttuser -t 'key_remap/events' -v
```

Press buttons on your mapped device and you should see messages like:

```
key_remap/events {"device_name": "my_keyboard", "pressed_key": "toggle_lights"}
```

<br/>

## 📝 Usage Notes

### UI Changes

In the mapping editor:
- The "Output Key" field now accepts any string (your MQTT action)
- Instead of selecting a key from a dropdown, type your action string
- Examples: `toggle_lights`, `play_pause`, `scene_movie_night`
- The string you enter will be sent as the `pressed_key` in the MQTT payload

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
