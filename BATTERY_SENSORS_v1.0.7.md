# Battery Sensors + Device Info - v1.0.7 (REVIEW BEFORE PUSH)

## Features Added

### 1. **Battery Sensors for Battery-Powered Devices** 🔋

Added automatic battery monitoring for battery-powered BluOS devices (like the Flex speaker).

**Two sensors automatically created:**
1. **Battery Level** - Shows battery percentage (0-100%)
2. **Battery Charging** - Shows charging status ("Charging" / "Not charging")

### 2. **Enhanced Device Information** 📱

Devices now show proper names and model information from SyncStatus.

**Improvements:**
- Device name from SyncStatus (e.g., "FLEX Speaker" instead of generic "BluOS Player")
- Model name shown (e.g., "PULSE FLEX 2i" instead of "BluOS Player")
- Brand from SyncStatus (e.g., "Bluesound")
- Manufacturer changed to "Pimmeke1989" as default

## SyncStatus Information

The `/SyncStatus` endpoint provides detailed device information:

```xml
<SyncStatus etag="306" syncStat="306" version="4.12.11" id="10.10.10.23:11000" 
            db="-38.4" volume="14" name="FLEX Speaker" model="P125" 
            modelName="PULSE FLEX 2i" class="speaker" 
            icon="/images/players/P125_nt.png" brand="Bluesound" 
            schemaVersion="34" initialized="true" mac="90:56:82:61:D5:7A">
```

**Parsed fields:**
- `name`: "FLEX Speaker" → Used as device name
- `model`: "P125" → Used if modelName not available
- `modelName`: "PULSE FLEX 2i" → Preferred model name
- `brand`: "Bluesound" → Used as manufacturer
- `icon`: Device icon path
- `mac`: MAC address

## Device Information Display

### Before:
```
Name: BluOS Player
Manufacturer: Bluesound
Model: BluOS Player
```

### After:
```
Name: FLEX Speaker
Manufacturer: Bluesound (or Pimmeke1989 if not in SyncStatus)
Model: PULSE FLEX 2i
```

## Battery Sensors

### Battery Level Sensor
- **Entity ID**: `sensor.flex_speaker_battery`
- **Device Class**: Battery
- **Unit**: Percentage (%)
- **State**: Battery level (0-100)
- **Attributes**:
  - `charging`: true/false
  - `icon_path`: BluOS battery icon path

### Battery Charging Sensor
- **Entity ID**: `sensor.flex_speaker_battery_charging`
- **State**: "Charging" or "Not charging"
- **Icon**: 
  - `mdi:battery-charging` when charging
  - `mdi:battery` when not charging
- **Attributes**:
  - `battery_level`: Current battery percentage
  - `charging`: true/false

## Implementation Details

### File 1: `bluos_api.py`

#### Added battery parsing:
```python
def _parse_battery(self, battery_data: dict | None) -> dict[str, Any]:
    """Parse battery information."""
    if not battery_data:
        return {}
    
    return {
        "level": int(battery_data.get("level", 0)),
        "charging": battery_data.get("charging", "false") == "true",
        "icon": battery_data.get("icon", ""),
    }
```

#### Enhanced SyncStatus parsing:
```python
def get_sync_status(self) -> dict[str, Any] | None:
    """Get sync/group status and device information."""
    result = {
        ...
        # Device information from SyncStatus
        "device_name": sync_status.get("name", ""),
        "model": sync_status.get("model", ""),
        "model_name": sync_status.get("modelName", ""),
        "brand": sync_status.get("brand", ""),
        "icon": sync_status.get("icon", ""),
        "mac": sync_status.get("mac", ""),
    }
```

### File 2: `sensor.py` (NEW)

Created two battery sensor classes:
- `BluOSBatterySensor` - Battery level
- `BluOSBatteryChargingSensor` - Charging status

Automatic detection - sensors only created if device has battery.

### File 3: `media_player.py`

Updated device_info to use SyncStatus:
```python
# Get device information from SyncStatus (more detailed than Status)
sync_status = coordinator.data.get("sync_status", {})

device_name = sync_status.get("device_name", "")  # "FLEX Speaker"
model_name = sync_status.get("model_name", "")     # "PULSE FLEX 2i"
brand = sync_status.get("brand", "Pimmeke1989")    # "Bluesound" or default

self._attr_device_info = {
    "name": device_name,
    "manufacturer": brand,
    "model": model_name if model_name else model,
}
```

### File 4: `__init__.py`

Added sensor platform:
```python
PLATFORMS = [Platform.MEDIA_PLAYER, Platform.SENSOR]
```

## Expected Results

### Flex Speaker (has battery):
**Device Info:**
- Name: "FLEX Speaker" (from SyncStatus)
- Manufacturer: "Bluesound"
- Model: "PULSE FLEX 2i"

**Entities:**
- `media_player.flex_speaker`
- `sensor.flex_speaker_battery` (100%)
- `sensor.flex_speaker_battery_charging` ("Charging")

### Woonkamer NAD (no battery):
**Device Info:**
- Name: "Woonkamer NAD" (from SyncStatus)
- Manufacturer: "Bluesound" or "Pimmeke1989"
- Model: From SyncStatus

**Entities:**
- `media_player.woonkamer_nad`
- No battery sensors

## Use Cases

### Low Battery Alert:
```yaml
automation:
  - alias: "Flex Speaker Low Battery"
    trigger:
      - platform: numeric_state
        entity_id: sensor.flex_speaker_battery
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Flex speaker battery low ({{ states('sensor.flex_speaker_battery') }}%)"
```

### Fully Charged Notification:
```yaml
automation:
  - alias: "Flex Speaker Fully Charged"
    trigger:
      - platform: numeric_state
        entity_id: sensor.flex_speaker_battery
        above: 99
    action:
      - service: notify.mobile_app
        data:
          message: "Flex speaker fully charged!"
```

## Files Modified/Created

1. ✅ **Modified**: `custom_components/bluos/bluos_api.py`
   - Added `_parse_battery()` method
   - Enhanced `get_sync_status()` to include device info
   - Updated `get_status()` to include battery info

2. ✅ **Created**: `custom_components/bluos/sensor.py`
   - `BluOSBatterySensor` - Battery level sensor
   - `BluOSBatteryChargingSensor` - Charging status sensor
   - Automatic detection based on battery presence

3. ✅ **Modified**: `custom_components/bluos/media_player.py`
   - Use SyncStatus for device name
   - Use SyncStatus for model and brand
   - Manufacturer defaults to "Pimmeke1989"

4. ✅ **Modified**: `custom_components/bluos/__init__.py`
   - Added `Platform.SENSOR` to PLATFORMS list

## Testing

After updating:

1. **Restart Home Assistant**

2. **Check Device Names**:
   - Flex Speaker should show as "FLEX Speaker"
   - Model should show as "PULSE FLEX 2i"
   - Manufacturer should show as "Bluesound"

3. **Check Battery Sensors** (Flex only):
   - Battery sensor should show current percentage
   - Charging sensor should show status
   - Unplug/plug to test charging status changes

4. **Check Other Devices**:
   - Should show proper names from SyncStatus
   - No battery sensors (if no battery)

## Ready to Push?

**Please review these changes!**

This adds:
- ✅ Battery monitoring for Flex speaker
- ✅ Proper device names from SyncStatus
- ✅ Model information (PULSE FLEX 2i, etc.)
- ✅ Manufacturer changed to Pimmeke1989

Files to be committed:
- `custom_components/bluos/bluos_api.py` (modified)
- `custom_components/bluos/sensor.py` (new)
- `custom_components/bluos/media_player.py` (modified)
- `custom_components/bluos/__init__.py` (modified)
