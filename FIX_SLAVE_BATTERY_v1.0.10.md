# Fix Battery and Slave Issues - v1.0.10 (REVIEW BEFORE PUSH)

## Issues Fixed

### 1. **Slave IP Parsing** 🔧
**Problem**: Master's `slaves` attribute was empty

**Root Cause**: Slave XML uses `id` attribute:
```xml
<slave id="10.10.10.23" port="11000"/>
```

**Fix**: Changed from `slave.get("ip")` to `slave.get("id")`

### 2. **Battery Sensors Not Working When Grouped** 🔋
**Problem**: Battery sensors disappear when Flex speaker is grouped

**Root Cause**: When grouped, `/Status` endpoint doesn't include battery info!

**Discovery**: Battery info is ALWAYS in `/SyncStatus`, even when grouped

**Fix**: Parse battery from `/SyncStatus` instead of `/Status`

## Key Discovery

**When a device is grouped:**
- `/Status` - Battery info MISSING ❌
- `/SyncStatus` - Battery info ALWAYS present ✅

**Solution**: Use `/SyncStatus` as primary source for battery info

## Changes Made

### File 1: `bluos_api.py`

#### Change 1: Fixed slave IP extraction
```python
# Before (BROKEN):
"ip": slave.get("ip", "")  # Returns empty!

# After (FIXED):
"ip": slave.get("id", "")  # Correct attribute!
```

#### Change 2: Added battery to SyncStatus parsing
```python
result = {
    ...
    "mac": sync_status.get("mac", ""),
    # Battery info (always present in SyncStatus, even when grouped)
    "battery": self._parse_battery(sync_status.get("battery")),
}
```

### File 2: `sensor.py`

#### Updated all battery checks to use SyncStatus first:

**Setup:**
```python
# Check SyncStatus first (always has battery)
battery_info = coordinator.data.get("sync_status", {}).get("battery", {})
if not battery_info:
    # Fallback to Status
    battery_info = coordinator.data.get("status", {}).get("battery", {})
```

**Applied to:**
- `async_setup_entry()` - Battery sensor creation
- `BluOSBatterySensor.native_value` - Battery level
- `BluOSBatterySensor.extra_state_attributes` - Battery attributes
- `BluOSBatteryChargingSensor.native_value` - Charging status
- `BluOSBatteryChargingSensor.icon` - Icon selection
- `BluOSBatteryChargingSensor.extra_state_attributes` - Charging attributes

### File 3: `media_player.py`

Added debug logging to `_ip_to_entity_id()` (from previous change)

## Expected Behavior After Fix

### Slave Attributes (Master - Woonkamer):

**Before:**
```yaml
bluos_group: [media_player.woonkamer_stereo]  # Only master
slaves: []  # Empty!
```

**After:**
```yaml
bluos_group: [media_player.woonkamer_stereo, media_player.flex_speaker]  # Both!
slaves: [media_player.flex_speaker]  # Slave shown!
group_name: "Woonkamer Stereo+FLEX Speaker"
```

### Battery Sensors (Flex Speaker):

**Before:**
- Ungrouped: Battery sensors work ✅
- Grouped: Battery sensors disappear ❌

**After:**
- Ungrouped: Battery sensors work ✅
- Grouped: Battery sensors work ✅

**Entities:**
- `sensor.flex_speaker_battery` - Shows 0-100%
- `sensor.flex_speaker_battery_charging` - Shows "Charging" / "Not charging"

## Why This Works

### SyncStatus Always Has Battery

**Ungrouped Flex:**
```xml
<SyncStatus name="FLEX Speaker" ...>
  <battery level="100" charging="true" icon="..."/>
</SyncStatus>
```

**Grouped Flex (as slave):**
```xml
<SyncStatus name="FLEX Speaker" ...>
  <battery level="100" charging="true" icon="..."/>  ← Still present!
  <master>10.10.10.31</master>
</SyncStatus>
```

**Status endpoint when grouped:**
```xml
<status>
  <!-- No battery element! -->
</status>
```

## Files Modified

1. ✅ **Modified**: `custom_components/bluos/bluos_api.py`
   - Fixed slave IP extraction (use `id` not `ip`)
   - Added battery parsing to SyncStatus

2. ✅ **Modified**: `custom_components/bluos/sensor.py`
   - Check SyncStatus first for battery info
   - Fallback to Status for compatibility
   - Added debug logging

3. ✅ **Modified**: `custom_components/bluos/media_player.py`
   - Added debug logging to `_ip_to_entity_id()`

## Testing

After updating:

### Test 1: Slave Attributes
1. Group Woonkamer + Flex
2. Check Woonkamer attributes
3. Should show:
   - `slaves: [media_player.flex_speaker]`
   - `bluos_group: [media_player.woonkamer_stereo, media_player.flex_speaker]`

### Test 2: Battery Sensors (Ungrouped)
1. Ungroup Flex
2. Battery sensors should exist
3. Should show battery level and charging status

### Test 3: Battery Sensors (Grouped)
1. Group Flex with Woonkamer
2. Battery sensors should STILL work ✅
3. Should show battery level and charging status

### Test 4: Re-add Device
1. Remove Flex from integration
2. Re-add Flex
3. Battery sensors should be created automatically

## Ready to Push?

**YES - This fixes both issues!**

Files to be committed:
- `custom_components/bluos/bluos_api.py` (modified - slave IP + battery in SyncStatus)
- `custom_components/bluos/sensor.py` (modified - use SyncStatus for battery)
- `custom_components/bluos/media_player.py` (modified - debug logging)
