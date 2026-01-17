# Remove Group Name Parameter - v1.0.11 (REVIEW BEFORE PUSH)

## Change Made

### **Removed `group_name` parameter from `bluos.join` service**

The `group_name` parameter was not working correctly with the BluOS API, so it has been removed.

BluOS will now automatically generate group names (e.g., "Woonkamer Stereo+FLEX Speaker").

## Reason for Removal

The `group_name` parameter was intended to allow users to set custom names for groups, but:
- The BluOS API doesn't properly support custom group names via the `AddSlave` endpoint
- BluOS automatically generates group names based on the devices in the group
- The parameter was not functional and caused confusion

## Changes Made

### File 1: `bluos_api.py`
**Removed `group_name` parameter from `add_slave()` method:**
```python
# Before:
def add_slave(self, slave_ip: str, group_name: str | None = None) -> bool:
    params = {"slave": slave_ip, "port": str(self.port)}
    if group_name:
        params["group"] = group_name

# After:
def add_slave(self, slave_ip: str) -> bool:
    params = {"slave": slave_ip, "port": str(self.port)}
```

### File 2: `media_player.py`
**Removed `group_name` parameter from `async_join_player()` method:**
```python
# Before:
async def async_join_player(self, master: str, group_name: str | None = None) -> None:
    result = await self.hass.async_add_executor_job(
        master_coordinator.api.add_slave, slave_ip, group_name
    )

# After:
async def async_join_player(self, master: str) -> None:
    result = await self.hass.async_add_executor_job(
        master_coordinator.api.add_slave, slave_ip
    )
```

**Removed from service registration:**
```python
# Before:
platform.async_register_entity_service(
    SERVICE_JOIN,
    {
        vol.Required("master"): cv.entity_id,
        vol.Optional("group_name"): cv.string,  # ← Removed
    },
    "async_join_player",
)

# After:
platform.async_register_entity_service(
    SERVICE_JOIN,
    {
        vol.Required("master"): cv.entity_id,
    },
    "async_join_player",
)
```

### File 3: `services.yaml`
**Removed `group_name` field:**
```yaml
# Before:
join:
  fields:
    master:
      name: Master Player
      ...
    group_name:  # ← Removed
      name: Group Name
      ...

# After:
join:
  fields:
    master:
      name: Master Player
      ...
```

### File 4: `strings.json`
**Removed `group_name` field:**
```json
// Before:
"join": {
    "fields": {
        "master": {...},
        "group_name": {...}  // ← Removed
    }
}

// After:
"join": {
    "fields": {
        "master": {...}
    }
}
```

## Service Usage

### Before (v1.0.10):
```yaml
service: bluos.join
target:
  entity_id: media_player.flex_speaker
data:
  master: media_player.woonkamer_stereo
  group_name: "My Custom Group"  # ← This didn't work
```

### After (v1.0.11):
```yaml
service: bluos.join
target:
  entity_id: media_player.flex_speaker
data:
  master: media_player.woonkamer_stereo
  # group_name parameter removed
```

## Group Naming

BluOS will automatically generate group names based on the devices:
- Example: "Woonkamer Stereo+FLEX Speaker"
- Format: "{Master Name}+{Slave Name}"

This is visible in the `group_name` attribute after joining.

## Files Modified

1. ✅ **Modified**: `custom_components/bluos/bluos_api.py`
   - Removed `group_name` parameter from `add_slave()`
   - Simplified logging

2. ✅ **Modified**: `custom_components/bluos/media_player.py`
   - Removed `group_name` parameter from `async_join_player()`
   - Removed from service registration

3. ✅ **Modified**: `custom_components/bluos/services.yaml`
   - Removed `group_name` field definition

4. ✅ **Modified**: `custom_components/bluos/strings.json`
   - Removed `group_name` field translation

## Backward Compatibility

**Breaking Change**: If users were calling the service with `group_name`, they will need to remove that parameter.

However, since the parameter wasn't working anyway, this shouldn't affect functionality.

## Testing

After updating:

1. **Call join service:**
   ```yaml
   service: bluos.join
   target:
     entity_id: media_player.flex_speaker
   data:
     master: media_player.woonkamer_stereo
   ```

2. **Check group_name attribute:**
   - Should show BluOS-generated name
   - Example: "Woonkamer Stereo+FLEX Speaker"

3. **Verify no errors:**
   - Service should work without `group_name` parameter
   - Group should form correctly

## Ready to Push?

**YES - This removes the non-functional group_name parameter**

Files to be committed:
- `custom_components/bluos/bluos_api.py` (modified)
- `custom_components/bluos/media_player.py` (modified)
- `custom_components/bluos/services.yaml` (modified)
- `custom_components/bluos/strings.json` (modified)
