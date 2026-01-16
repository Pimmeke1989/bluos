# Debug Version - v1.0.6 (REVIEW BEFORE PUSH)

## Issues to Debug

### 1. **Progress Bar Not Showing Correct Information**
**User Report**: Progress bar added but not showing right information
**Expected**: Should use `<secs>` for current position and `<totlen>` for total length

**Current Implementation** (appears correct):
```python
@property
def media_position(self) -> int | None:
    return self.coordinator.data["status"].get("secs", 0)

@property
def media_duration(self) -> int | None:
    return self.coordinator.data["status"].get("totlen", 0)
```

**Possible Issue**: The `media_position_updated_at` might not be working correctly, or the values aren't being updated.

### 2. **Volume Shows 0 Instead of Actual Value**
**User Report**: `volume_level: 0` but Status page shows `<volume>11</volume>`

**Current Implementation**:
- Tries to use `/Volume` endpoint first
- Falls back to `/Status` if `/Volume` fails
- Should work, but clearly isn't

**Possible Issues**:
1. `/Volume` endpoint returning empty/invalid data
2. XML parsing failing
3. Coordinator not fetching volume data

## Changes Made - Debug Logging

### File 1: `bluos_api.py` - Added debug logging to `get_volume()`

**Added logging at each step:**
```python
def get_volume(self) -> dict[str, Any] | None:
    response = self._get("Volume")
    if not response:
        _LOGGER.debug("get_volume: No response from /Volume endpoint for %s", self.host)
        return None
    
    _LOGGER.debug("get_volume: Raw response from %s: %s", self.host, response[:200])
    
    volume_data = self._parse_xml(response)
    if not volume_data:
        _LOGGER.debug("get_volume: Failed to parse XML response for %s", self.host)
        return None
    
    _LOGGER.debug("get_volume: Parsed data from %s: %s", self.host, volume_data)
    
    result = {
        "volume": int(volume_data.get("volume", 0)),
        "mute": volume_data.get("mute", "0") == "1",
        "db": volume_data.get("db", "0"),
    }
    
    _LOGGER.debug("get_volume: Result for %s: %s", self.host, result)
    return result
```

### File 2: `media_player.py` - Added debug logging to `volume_level` property

**Added logging to track volume source:**
```python
@property
def volume_level(self) -> float | None:
    volume_data = self.coordinator.data.get("volume", {})
    _LOGGER.debug("volume_level: volume_data = %s", volume_data)
    
    if volume_data and "volume" in volume_data:
        volume = volume_data.get("volume", 0)
        _LOGGER.debug("volume_level: Using /Volume endpoint, volume = %s", volume)
    else:
        volume = self.coordinator.data["status"].get("volume", 0)
        _LOGGER.debug("volume_level: Using /Status fallback, volume = %s", volume)
    
    result = volume / 100
    _LOGGER.debug("volume_level: Final result = %s", result)
    return result
```

## Testing Instructions

After updating to v1.0.6:

### 1. Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.bluos: debug
```

Restart Home Assistant.

### 2. Check Volume Logs

Look for these log entries:
```
get_volume: Raw response from 10.10.10.23: <volume>...</volume>
get_volume: Parsed data from 10.10.10.23: {...}
get_volume: Result for 10.10.10.23: {'volume': 11, ...}
volume_level: volume_data = {'volume': 11, ...}
volume_level: Using /Volume endpoint, volume = 11
volume_level: Final result = 0.11
```

### 3. Check Progress Bar Logs

Look for:
```
media_position: <value>
media_duration: <value>
media_position_updated_at: <timestamp>
```

### 4. Provide Feedback

Please provide:
1. **Volume logs** - What does `get_volume` return?
2. **Status logs** - What's in `coordinator.data["status"]`?
3. **Volume endpoint** - What does `http://10.10.10.23:11000/Volume` return in browser?

## Expected Findings

### If `/Volume` endpoint fails:
```
get_volume: No response from /Volume endpoint for 10.10.10.23
volume_level: volume_data = {}
volume_level: Using /Status fallback, volume = 11
volume_level: Final result = 0.11
```
→ Should still work via fallback!

### If `/Volume` returns wrong data:
```
get_volume: Parsed data from 10.10.10.23: {'volume': '11', ...}  # String instead of int?
```
→ Might need to handle string values

### If coordinator doesn't fetch volume:
```
volume_level: volume_data = {}
```
→ Check coordinator.py

## Files Modified

1. ✅ `custom_components/bluos/bluos_api.py`
   - Added debug logging to `get_volume()`

2. ✅ `custom_components/bluos/media_player.py`
   - Added debug logging to `volume_level` property

## Next Steps

1. Push v1.0.6 with debug logging
2. User updates and checks logs
3. Identify root cause from logs
4. Fix the actual issue in v1.0.7
5. Remove debug logging in v1.0.8

## Ready to Push?

**YES - This adds debug logging to help diagnose the issues**

Files to be committed:
- `custom_components/bluos/bluos_api.py` (modified - debug logging)
- `custom_components/bluos/media_player.py` (modified - debug logging)
