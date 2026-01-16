# Summary of Changes - v1.0.2 (REVIEW BEFORE PUSH)

## Issues Fixed

### 1. **Unjoin Not Working**
**Problem**: When unjoining a slave from master, the operation failed because:
- Master IP was parsed as dict `{'port': '11000', '_text': '10.10.10.31'}` instead of string `'10.10.10.31'`
- Coordinator lookup failed (comparing dict to string)
- Fallback called `RemoveSlave` on slave itself (doesn't work - must call on master!)

### 2. **Join Not Working**  
**Problem**: Could not find master coordinator because:
- Entity ID `media_player.bluos_woonkamer` doesn't contain entry ID
- Entry IDs are long hashes like `01KF3GPW3W8C2H47M9CZNNHE9T`
- Previous lookup methods failed

## Changes Made

### File 1: `custom_components/bluos/bluos_api.py`

#### Change 1.1: Fixed `get_sync_status()` - Extract master IP from dict

**Before:**
```python
# Check if this player is a slave
if sync_status.get("master"):
    result["master"] = sync_status.get("master")  # Returns {'port': '11000', '_text': '10.10.10.31'}
```

**After:**
```python
# Check if this player is a slave
if sync_status.get("master"):
    master_data = sync_status.get("master")
    # Master can be a string (IP) or a dict with _text containing the IP
    if isinstance(master_data, dict):
        result["master"] = master_data.get("_text", "")  # Extract just the IP
    else:
        result["master"] = master_data
```

#### Change 1.2: Fixed slave IP extraction too

**Before:**
```python
"ip": slave.get("ip", ""),
```

**After:**
```python
"ip": slave.get("ip", "") if isinstance(slave.get("ip"), str) else slave.get("ip", {}).get("_text", ""),
```

### File 2: `custom_components/bluos/media_player.py`

#### Change 2.1: Fixed `async_unjoin_player()` - Call RemoveSlave on master, not slave

**Before:**
```python
if master_coordinator:
    slave_ip = self._entry.data[CONF_HOST]
    result = await self.hass.async_add_executor_job(
        master_coordinator.api.remove_slave, slave_ip
    )
else:
    # WRONG: Calls RemoveSlave on the slave itself!
    result = await self.hass.async_add_executor_job(
        self.coordinator.api.remove_slave  # ← This is the slave!
    )
```

**After:**
```python
slave_ip = self._entry.data[CONF_HOST]

if master_coordinator:
    # Use the master's coordinator
    result = await self.hass.async_add_executor_job(
        master_coordinator.api.remove_slave, slave_ip
    )
else:
    # Make direct API call to the master
    from .bluos_api import BluOSApi
    master_api = BluOSApi(master_ip, self._entry.data.get("port", 11000))
    result = await self.hass.async_add_executor_job(
        master_api.remove_slave, slave_ip
    )
```

#### Change 2.2: Fixed `async_join_player()` - Use entity registry to find coordinator

**Before:**
```python
# Try to find coordinator by checking if entry_id is in entity_id
for entry_id, coordinator in self.hass.data[DOMAIN].items():
    if entry_id in master:  # ← This doesn't work!
        master_coordinator = coordinator
        break
```

**After:**
```python
# Method 1: Use entity registry to get config_entry_id
from homeassistant.helpers import entity_registry as er
entity_reg = er.async_get(self.hass)
master_entity_entry = entity_reg.async_get(master)

if master_entity_entry:
    if master_entity_entry.config_entry_id in self.hass.data[DOMAIN]:
        master_coordinator = self.hass.data[DOMAIN][master_entity_entry.config_entry_id]
        master_ip = master_coordinator.entry.data[CONF_HOST]

# Method 2: Fallback - match by device name
if not master_coordinator:
    master_name = master_entity.attributes.get("friendly_name", "")
    for entry_id, coordinator in self.hass.data[DOMAIN].items():
        coordinator_name = coordinator.data.get("status", {}).get("name", "")
        if coordinator_name and coordinator_name in master_name:
            master_coordinator = coordinator
            master_ip = coordinator.entry.data[CONF_HOST]
            break
```

## Expected Behavior After Fix

### For Unjoin:
```
Attempting to unjoin player media_player.bluos_flex
Current sync status: {'master': '10.10.10.31', ...}  # ← Now a string!
Player is a slave. Removing from master 10.10.10.31
Found master coordinator for IP 10.10.10.31
RemoveSlave via coordinator result: True
Successfully unjoined player media_player.bluos_flex
```

### For Join:
```
Attempting to join media_player.bluos_flex to master media_player.bluos_woonkamer
Master entity entry found: config_entry_id=01KF3GPW3W8C2H47M9CZNNHE9T
Found master coordinator by entity registry: 01KF3GPW3W8C2H47M9CZNNHE9T (IP: 10.10.10.31)
Calling AddSlave on master 10.10.10.31 to add slave 10.10.10.23
Successfully joined 10.10.10.23 to 10.10.10.31
```

## Files Modified

1. ✅ `custom_components/bluos/bluos_api.py`
   - Fixed master IP extraction in `get_sync_status()`
   - Fixed slave IP extraction

2. ✅ `custom_components/bluos/media_player.py`
   - Fixed `async_unjoin_player()` to call RemoveSlave on master
   - Fixed `async_join_player()` to use entity registry
   - Added direct API fallback for unjoin

3. ✅ `FIX_UNJOIN_v1.0.2.md` - Documentation of fixes

## Testing Instructions

After updating:

1. **Test Join:**
   ```yaml
   service: bluos.join
   target:
     entity_id: media_player.bluos_flex
   data:
     master: media_player.bluos_woonkamer
   ```

2. **Test Unjoin:**
   ```yaml
   service: bluos.unjoin
   target:
     entity_id: media_player.bluos_flex
   ```

3. **Check logs** for successful messages

## Ready to Push?

Please review these changes. If they look good, I'll:
1. Commit the changes
2. Update version to 1.0.2
3. Update CHANGELOG.md
4. Push to GitHub
5. Create v1.0.2 tag

**Do these changes look correct to you?**
