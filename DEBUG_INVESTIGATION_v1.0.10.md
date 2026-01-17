# Debug and Investigation - v1.0.10

## Issues Reported

### 1. **Master Group Attributes Not Correct**
- `bluos_group` only shows master, not slaves
- `slaves` attribute is empty

### 2. **Battery Entities Not Working**
- Battery sensors not functioning

### 3. **Error in Logs**
```
ERROR (MainThread) [homeassistant.components.bluesound.coordinator] 
Error requesting Woonkamer Stereo data: 'ConfigEntry' object has no attribute 'runtime_data'
```

## Analysis

### Issue 1: Group Attributes

Looking at the screenshot, the master shows:
```yaml
bluos_group: media_player.woonkamer_stereo
master: null
slaves:  # Empty!
is_master: true
is_slave: false
group_name: null
```

**Expected:**
```yaml
bluos_group: ["media_player.woonkamer_stereo", "media_player.flex_speaker"]
slaves: ["media_player.flex_speaker"]
```

**Possible causes:**
1. `_ip_to_entity_id()` returning None for slave IP
2. Slave not in entity registry
3. Coordinator data not containing slave info

### Issue 2: Battery Entities

Battery sensors were working in v1.0.7 but stopped working.

**Possible causes:**
1. Sensor platform not loading
2. Battery data not being parsed
3. Related to the runtime_data error

### Issue 3: Error Message - CRITICAL!

The error mentions `homeassistant.components.bluesound.coordinator` - this is the **OFFICIAL Bluesound integration**, not our custom BluOS integration!

**This suggests:**
- You might have BOTH integrations installed
- Home Assistant is loading the official "bluesound" integration
- The official integration is trying to use `runtime_data` (newer HA feature)
- Our custom "bluos" integration might not be loading at all

## Changes Made - Debug Logging

Added extensive debug logging to `_ip_to_entity_id()`:

```python
def _ip_to_entity_id(self, ip: str | None) -> str | None:
    _LOGGER.debug("_ip_to_entity_id: Converting IP %s to entity ID", ip)
    
    bluos_data = self.hass.data.get(DOMAIN, {})
    _LOGGER.debug("_ip_to_entity_id: Found %d BluOS entries", len(bluos_data))
    
    for entry_id, coordinator in bluos_data.items():
        if hasattr(coordinator, 'api') and coordinator.api.host == ip:
            _LOGGER.debug("_ip_to_entity_id: Found matching coordinator for IP %s", ip)
            # ... find entity
            _LOGGER.debug("_ip_to_entity_id: Found entity %s for IP %s", entity.entity_id, ip)
            return entity.entity_id
    
    _LOGGER.warning("_ip_to_entity_id: Could not find entity for IP %s", ip)
    return None
```

## Investigation Steps

### Step 1: Check Which Integration is Running

**Question**: Do you have the official "Bluesound" integration installed?

Check in Home Assistant:
- Settings → Devices & Services
- Look for both "BluOS" (custom) and "Bluesound" (official)

### Step 2: Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.bluos: debug
```

Restart HA and check logs for:
- `_ip_to_entity_id: Converting IP ...`
- `_ip_to_entity_id: Found X BluOS entries`
- `_ip_to_entity_id: Found entity ... for IP ...`

### Step 3: Check SyncStatus Data

The logs should show what slave data is being received.

## Possible Solutions

### If Official Bluesound Integration is Installed:

**Option A**: Remove official integration, use only custom BluOS
**Option B**: Remove custom BluOS, use only official Bluesound
**Option C**: Keep both but ensure they use different devices

### If Only Custom BluOS is Installed:

The error message is confusing - might be a cached error. Need to:
1. Check debug logs
2. Verify slave IP addresses
3. Verify entity registry entries

## Files Modified

1. ✅ **Modified**: `custom_components/bluos/media_player.py`
   - Added debug logging to `_ip_to_entity_id()`
   - Added error handling

## Next Steps

1. **Check for duplicate integrations**
2. **Enable debug logging**
3. **Provide debug logs** showing:
   - What IPs are being converted
   - How many BluOS entries found
   - What entities are found
4. **Check SyncStatus** - does it contain slave info?

## Questions for User

1. Do you have the official "Bluesound" integration installed?
2. Can you enable debug logging and share the logs?
3. What does `/SyncStatus` show for the master when grouped?

## Ready to Push?

**NOT YET - Need more information**

This adds debug logging to help diagnose the issue, but we need to understand:
- Why slaves aren't showing
- Why battery entities stopped working
- Whether there's a conflict with official integration
