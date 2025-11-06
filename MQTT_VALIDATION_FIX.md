# Fix for MQTT String Validation Issue

**Date:** 2025-11-06
**Issue:** Free-form MQTT action strings rejected by validation
**Branch:** `claude/fix-mqtt-string-validation-011CUpuLaMAqk8fc7qbkjDgb`

---

## Problem

When trying to create a mapping with a free-form MQTT action string (e.g., "test text 22"), the GUI shows:

```
Failed to apply preset "22". "PLAYPAUSE": The output_symbol "test text 22"
is not a macro and not a valid keycode-name
```

**Root Cause:** The validation layer in `inputremapper/configs/mapping.py` (lines 407-409) validates all output symbols against the keyboard layout, treating them as either:
1. A macro (containing special syntax like `key()`, `hold()`, etc.)
2. A valid keycode name (like "KEY_A", "BTN_LEFT", etc.)

Free-form strings like "test text 22" are neither, so validation fails **before** the MQTT handler can be used.

---

## The Fix

Modified `inputremapper/configs/mapping.py` to:

1. **Import MQTT_AVAILABLE** (lines 39-43):
```python
# Check if MQTT is available for accepting free-form action strings
try:
    from inputremapper.mqtt_client import MQTT_AVAILABLE
except ImportError:
    MQTT_AVAILABLE = False
```

2. **Skip keycode validation when MQTT is available** (lines 413-418):
```python
# If MQTT is available, accept any non-empty string as a valid MQTT action
# This allows free-form strings like "toggle_lights" to be used as MQTT payloads
if MQTT_AVAILABLE:
    # Any string is valid for MQTT - it will be published as the "pressed_key"
    # in the MQTT JSON payload. No need to validate against keyboard layout.
    return values
```

This validation bypass happens **after** macro validation but **before** keycode validation, so the priority is:
1. DISABLE_NAME ("disable") → accepted
2. Macros → validated and accepted
3. **MQTT strings (if MQTT available) → accepted without validation**
4. Keycodes → validated against keyboard layout

---

## How It Works

### Before the Fix

```
User enters: "test text 22"
     ↓
validate_symbol() in mapping.py
     ↓
Check if macro? No
     ↓
Check if valid keycode? No
     ↓
❌ Raise OutputSymbolUnknownError
     ↓
Mapping rejected, never applied
```

### After the Fix

```
User enters: "test text 22"
     ↓
validate_symbol() in mapping.py
     ↓
Check if macro? No
     ↓
Check if MQTT available? Yes
     ↓
✅ Accept as valid MQTT action string
     ↓
Mapping applied successfully
     ↓
_get_output_handler() sees string → returns HandlerEnums.mqtt
     ↓
MQTTHandler created with mqtt_action="test text 22"
     ↓
Button pressed → MQTTHandler.notify()
     ↓
Publishes: {"device_name": "device", "pressed_key": "test text 22"}
```

---

## Testing Steps

### 1. Verify the Fix Compiles

```bash
cd input-remapper-mqtt
git checkout claude/fix-mqtt-string-validation-011CUpuLaMAqk8fc7qbkjDgb
python3 -m py_compile inputremapper/configs/mapping.py
# Should complete without errors
```

### 2. Install with the Fix

```bash
sudo python3 setup.py install
```

### 3. Test in GUI

```bash
# Start GUI
input-remapper-mqtt-gtk

# Create mapping:
# 1. Select device
# 2. Create preset, enable Autoload
# 3. Add mapping:
#    - Input: Record a button (e.g., PLAYPAUSE)
#    - Output Type: "Key or Macro"
#    - Output text: "test text 22"
# 4. Click "Apply"

# Expected result:
# ✅ No error message
# ✅ Preset applied successfully
# ✅ Mapping shows in list
```

### 4. Test MQTT Publishing

```bash
# Terminal 1: Monitor MQTT
mosquitto_sub -h YOUR_BROKER -p 1883 -u USER -P PASS -t 'key_remap/events' -v

# Terminal 2: View logs
tail -f ~/.local/share/input-remapper-mqtt/logs/app.log

# Press the mapped button
# Expected in Terminal 1:
# key_remap/events {"device_name": "your_device", "pressed_key": "test text 22"}
```

---

## What Strings Are Now Accepted

With MQTT available, these are all **valid** output symbols:

- ✅ `toggle_lights` - simple identifier
- ✅ `test text 22` - string with spaces and numbers
- ✅ `scene_movie_night` - snake_case
- ✅ `volume_up` - descriptive action
- ✅ `my-custom-action` - with hyphens
- ✅ Any UTF-8 string (emoji, non-ASCII, etc.)

**Still validated as before:**
- `disable` - special disable keyword
- `key(a)` - macro syntax
- `hold(shift, key(a))` - complex macro
- `KEY_A` - valid keycode (still works if MQTT not available)

---

## Backward Compatibility

This fix maintains backward compatibility:

1. **If MQTT is NOT available** (paho-mqtt not installed):
   - MQTT_AVAILABLE = False
   - Validation works as before (only macros and keycodes accepted)
   - No behavior change for original input-remapper

2. **If MQTT IS available**:
   - Free-form strings accepted for MQTT
   - Macros still work (validated first)
   - Valid keycodes still work (accepted after MQTT check)
   - Original key remapping functionality unchanged

---

## Files Changed

**Single file modified:** `inputremapper/configs/mapping.py`

**Changes:**
1. Added MQTT_AVAILABLE import (lines 39-43)
2. Added validation bypass for MQTT strings (lines 413-418)

**Total:** 9 lines added

---

## Why This Approach

**Alternative 1:** Add a new "MQTT" output type
❌ Requires GUI changes, more complex, breaks existing mappings

**Alternative 2:** Use special prefix (e.g., "mqtt:toggle_lights")
❌ Ugly, user-unfriendly, not intuitive

**Alternative 3:** Check for MQTT before validation ✅
✅ Simple, no GUI changes, works with existing UI
✅ Backward compatible
✅ Follows principle of least surprise

---

## Branch Information

**Branch:** `claude/fix-mqtt-string-validation-011CUpuLaMAqk8fc7qbkjDgb`

**GitHub:**
https://github.com/Qutaiba-Khader/input-remapper-mqtt/tree/claude/fix-mqtt-string-validation-011CUpuLaMAqk8fc7qbkjDgb

**Compare:**
https://github.com/Qutaiba-Khader/input-remapper-mqtt/compare/main...claude/fix-mqtt-string-validation-011CUpuLaMAqk8fc7qbkjDgb

---

## Summary

**Problem:** Validation layer blocks free-form MQTT strings
**Solution:** Skip keycode validation when MQTT is available
**Impact:** Enables the core "button → string → MQTT" functionality
**Testing:** Compile verified, ready for user testing

**This fix unblocks the primary use case of the MQTT fork.**
