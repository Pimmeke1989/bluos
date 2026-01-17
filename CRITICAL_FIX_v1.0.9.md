# Critical Fix - v1.0.9 (HOTFIX)

## Issue Fixed

### **AttributeError: 'HomeAssistant' object has no attribute 'helpers'** 🚨

**Error:**
```
AttributeError: 'HomeAssistant' object has no attribute 'helpers'
File "/config/custom_components/bluos/media_player.py", line 374, in _ip_to_entity_id
    entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)
```

**Root Cause:**
Incorrect import and usage of entity_registry in v1.0.8.

**Fix:**
1. Added proper import: `from homeassistant.helpers import entity_registry as er`
2. Changed usage from `self.hass.helpers.entity_registry.async_get(self.hass)` to `er.async_get(self.hass)`

## Changes Made

### File: `media_player.py`

**Import Fix:**
```python
# Before (BROKEN):
from homeassistant.helpers import config_validation as cv, entity_platform

# After (FIXED):
from homeassistant.helpers import config_validation as cv, entity_platform, entity_registry as er
```

**Method Fix:**
```python
# Before (BROKEN):
entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)

# After (FIXED):
entity_registry = er.async_get(self.hass)
```

## Impact

**v1.0.8**: Completely broken - AttributeError on every update
**v1.0.9**: Fixed - Works correctly

## Files Modified

1. ✅ **Modified**: `custom_components/bluos/media_player.py`
   - Added `entity_registry as er` import
   - Fixed `_ip_to_entity_id()` to use `er.async_get()`

## Testing

After updating:
1. Restart Home Assistant
2. Check logs - no more AttributeError
3. Group players - should work correctly
4. Check attributes - should show entity IDs

## Ready to Push?

**YES - This is a critical hotfix for v1.0.8!**

Files to be committed:
- `custom_components/bluos/media_player.py` (modified - CRITICAL FIX)
