# Fix for Unjoin Issue - v1.0.2

## Problem Identified

When trying to unjoin a slave player, the operation was failing because:

1. **XML Parsing Issue**: The master IP was being returned as a dictionary `{'port': '11000', '_text': '10.10.10.31'}` instead of just the IP string `'10.10.10.31'`

2. **Coordinator Lookup Failure**: Because the IP was a dict, the code couldn't find the master's coordinator (it was comparing a dict to a string)

3. **Wrong Fallback**: When the coordinator wasn't found, it tried calling `RemoveSlave` on the **slave** itself, which doesn't work. According to BluOS API, you must call `RemoveSlave` on the **master** with the slave's IP as a parameter.

## Log Evidence

From your log:
```
Current sync status: {'master': {'port': '11000', '_text': '10.10.10.31'}, ...}
Player is a slave. Removing from master {'port': '11000', '_text': '10.10.10.31'}
Could not find master coordinator for IP {'port': '11000', '_text': '10.10.10.31'}, trying direct unjoin
Ungrouping player 10.10.10.23  # ← Wrong! Should call on master, not slave
```

The response still showed `<master port="11000">10.10.10.31</master>`, confirming the unjoin didn't work.

## Fixes Applied

### 1. Fixed `get_sync_status()` in `bluos_api.py`

**Before:**
```python
if sync_status.get("master"):
    result["master"] = sync_status.get("master")  # Returns dict
```

**After:**
```python
if sync_status.get("master"):
    master_data = sync_status.get("master")
    # Master can be a string (IP) or a dict with _text containing the IP
    if isinstance(master_data, dict):
        result["master"] = master_data.get("_text", "")  # Extract IP
    else:
        result["master"] = master_data
```

### 2. Improved `async_unjoin_player()` in `media_player.py`

**Before:**
```python
if master_coordinator:
    # Call on master coordinator
else:
    # WRONG: Call RemoveSlave on the slave itself
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

### 3. Also Fixed Slave IP Parsing

Applied the same fix for slave IPs in case they're also returned as dicts:
```python
"ip": slave.get("ip", "") if isinstance(slave.get("ip"), str) else slave.get("ip", {}).get("_text", "")
```

## Expected Behavior After Fix

When you call unjoin on the Flex Speaker:

1. **Correct IP extraction**: `master_ip = "10.10.10.31"` (string, not dict)
2. **Find coordinator**: Should find the Woonkamer NAD coordinator
3. **Call RemoveSlave**: On master (10.10.10.31) with slave IP (10.10.10.23)
4. **Fallback**: If coordinator not found, makes direct HTTP call to master

## Testing

After updating, try unjoining again and you should see:

```
Attempting to unjoin player media_player.bluos_flex
Current sync status: {'master': '10.10.10.31', ...}  # ← Now a string!
Player is a slave. Removing from master 10.10.10.31
Found master coordinator for IP 10.10.10.31  # ← Should find it now
RemoveSlave via coordinator result: True
```

Or if the master isn't added to HA:
```
Could not find master coordinator for IP 10.10.10.31, making direct API call
RemoveSlave via direct API result: True
```

## Files Modified

- `custom_components/bluos/bluos_api.py` - Fixed master/slave IP extraction
- `custom_components/bluos/media_player.py` - Fixed unjoin logic with direct API fallback

## API Call

The correct API call should be:
```
http://10.10.10.31:11000/RemoveSlave?slave=10.10.10.23
```

NOT:
```
http://10.10.10.23:11000/RemoveSlave  # ← This doesn't work!
```
