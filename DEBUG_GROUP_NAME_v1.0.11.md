# Debug Group Name Issue - v1.0.11

## Issue

**Group name not being set correctly when using `bluos.join` service**

The join function works, but the group name is not applied correctly.

## Investigation

### Current Implementation

The code flow is:
1. User calls `bluos.join` service with `group_name` parameter
2. `async_join_player()` receives `group_name`
3. Calls `master_coordinator.api.add_slave(slave_ip, group_name)`
4. `add_slave()` adds `group` parameter to API call
5. Calls `/AddSlave?slave=X&port=11000&group=NAME`

### Code Looks Correct

The implementation appears correct:
```python
# In add_slave():
params = {
    "slave": slave_ip,
    "port": str(self.port),
}

if group_name:
    params["group"] = group_name  # ← This should work

response = self._get("AddSlave", params)
```

### Possible Issues

1. **URL Encoding**: Group name might need special encoding
2. **BluOS API**: The API might not accept the `group` parameter as we think
3. **Timing**: Group name might be set but then overwritten
4. **Parameter Name**: Maybe it's not `group` but something else?

## Changes Made - Debug Logging

Added extensive logging to diagnose the issue:

### File: `bluos_api.py`

**In `add_slave()`:**
```python
if group_name:
    params["group"] = group_name
    _LOGGER.info("Adding slave %s with group name: '%s'", slave_ip, group_name)
else:
    _LOGGER.info("Adding slave %s without group name (BluOS will use default)", slave_ip)

_LOGGER.debug("AddSlave params: %s", params)
response = self._get("AddSlave", params)

if response:
    _LOGGER.debug("AddSlave response: %s", response[:200])
else:
    _LOGGER.error("AddSlave returned no response")
```

**In `_get()`:**
```python
response = requests.get(url, params=params, timeout=self.timeout)
# Log the actual URL that was called (with params)
_LOGGER.debug("BluOS API call: %s", response.url)
```

## Testing Instructions

### Step 1: Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.bluos: debug
```

Restart Home Assistant.

### Step 2: Call Join Service

Use the `bluos.join` service:
```yaml
service: bluos.join
target:
  entity_id: media_player.flex_speaker
data:
  master: media_player.woonkamer_stereo
  group_name: "My Test Group"
```

### Step 3: Check Logs

Look for these log entries:

1. **Group name being passed:**
   ```
   Adding slave 10.10.10.23 with group name: 'My Test Group'
   ```

2. **Parameters:**
   ```
   AddSlave params: {'slave': '10.10.10.23', 'port': '11000', 'group': 'My Test Group'}
   ```

3. **Actual URL called:**
   ```
   BluOS API call: http://10.10.10.31:11000/AddSlave?slave=10.10.10.23&port=11000&group=My+Test+Group
   ```

4. **Response:**
   ```
   AddSlave response: <status>...</status>
   ```

### Step 4: Check SyncStatus

After joining, check:
```
http://10.10.10.31:11000/SyncStatus
```

Look for the `group` attribute:
```xml
<SyncStatus group="???" ...>
```

**Questions:**
- What does it show?
- Is it "My Test Group" or something else?

## Possible Solutions

### Solution 1: Different Parameter Name

Maybe BluOS uses a different parameter name. Try:
- `name` instead of `group`
- `groupName` instead of `group`
- `zone` instead of `group`

### Solution 2: URL Encoding Issue

Maybe spaces or special characters need different encoding.

### Solution 3: BluOS Limitation

Maybe BluOS doesn't actually support custom group names via API, and always generates its own (like "Woonkamer Stereo+FLEX Speaker").

### Solution 4: Separate API Call

Maybe the group name needs to be set with a separate API call after joining.

## Next Steps

1. **Enable debug logging**
2. **Call join service with group name**
3. **Check logs** - What URL is actually called?
4. **Check SyncStatus** - What group name appears?
5. **Try manual API call** - Test directly in browser:
   ```
   http://10.10.10.31:11000/AddSlave?slave=10.10.10.23&port=11000&group=TestName
   ```

## Questions for User

1. What group name are you trying to set?
2. What group name actually appears after joining?
3. Can you share the debug logs after calling the join service?
4. Can you try the manual API call in your browser and see what happens?

## Files Modified

1. ✅ **Modified**: `custom_components/bluos/bluos_api.py`
   - Added debug logging to `add_slave()`
   - Added URL logging to `_get()`

## Ready to Push?

**NOT YET - Need to investigate with debug logs first**

This adds logging to help diagnose why the group name isn't being set correctly.
