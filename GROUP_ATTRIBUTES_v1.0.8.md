# Enhanced Group Attributes - v1.0.8 (REVIEW BEFORE PUSH)

## Improvements Made

### **Better Group Information Display** 🎯

Enhanced the group attributes to be more useful and user-friendly:

1. **Entity IDs instead of IP addresses** - Group members now show as entity IDs
2. **`is_master` boolean** - Clear indication if player is a master
3. **`is_slave` boolean** - Clear indication if player is a slave  
4. **Fixed master/slaves attributes** - Now show entity IDs or None/empty list
5. **Added `group_name`** - Shows the zone/group name from SyncStatus

## Before vs After

### Before (v1.0.7):

**Woonkamer (Master):**
```yaml
bluos_group: ["10.10.10.31", "10.10.10.23"]
master: null
slaves: ["10.10.10.23"]
```

**Flex (Slave):**
```yaml
bluos_group: ["10.10.10.31", "10.10.10.23"]
master: "10.10.10.31"
slaves: []
```

### After (v1.0.8):

**Woonkamer (Master):**
```yaml
bluos_group: ["media_player.woonkamer_stereo", "media_player.flex_speaker"]
master: null
slaves: ["media_player.flex_speaker"]
is_master: true
is_slave: false
group_name: "Woonkamer Stereo+FLEX Speaker"
```

**Flex (Slave):**
```yaml
bluos_group: ["media_player.woonkamer_stereo", "media_player.flex_speaker"]
master: "media_player.woonkamer_stereo"
slaves: []
is_master: false
is_slave: true
group_name: "Woonkamer Stereo+FLEX Speaker"
```

## Implementation Details

### IP to Entity ID Conversion

Added `_ip_to_entity_id()` helper method:

```python
def _ip_to_entity_id(self, ip: str | None) -> str | None:
    """Convert IP address to entity ID by finding the matching coordinator."""
    if not ip:
        return None
    
    # Get all BluOS coordinators from hass.data
    bluos_data = self.hass.data.get(DOMAIN, {})
    
    for entry_id, coordinator in bluos_data.items():
        # Check if this coordinator's host matches the IP
        if hasattr(coordinator, 'api') and coordinator.api.host == ip:
            # Found the coordinator, now find its media_player entity
            entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)
            
            # Find media_player entity for this config entry
            for entity in entity_registry.entities.values():
                if (entity.config_entry_id == entry_id and 
                    entity.domain == "media_player"):
                    return entity.entity_id
    
    return None
```

### Enhanced Attributes

Updated `extra_state_attributes()`:

```python
def extra_state_attributes(self) -> dict[str, Any]:
    """Return entity specific state attributes."""
    sync_status = self.coordinator.data.get("sync_status", {})
    
    # Determine if this player is a master
    is_master = bool(sync_status.get("slaves"))
    is_slave = bool(sync_status.get("master"))
    
    # Build group information with entity IDs
    group_members = []
    master_entity = None
    slave_entities = []
    
    if is_slave:
        # This player is a slave
        master_ip = sync_status.get("master")
        master_entity = self._ip_to_entity_id(master_ip)
        group_members.append(master_entity if master_entity else master_ip)
        group_members.append(self.entity_id)
    elif is_master:
        # This player is a master
        group_members.append(self.entity_id)
        for slave in sync_status.get("slaves", []):
            slave_ip = slave.get("ip")
            slave_entity = self._ip_to_entity_id(slave_ip)
            entity_or_ip = slave_entity if slave_entity else slave_ip
            slave_entities.append(entity_or_ip)
            group_members.append(entity_or_ip)
    
    return {
        ATTR_BLUEOS_GROUP: group_members,
        ATTR_MASTER: master_entity if is_slave else None,
        ATTR_SLAVES: slave_entities if is_master else [],
        "is_master": is_master,
        "is_slave": is_slave,
        "group_name": sync_status.get("zone", ""),
    }
```

## SyncStatus Information Used

From your Woonkamer SyncStatus:
```xml
<SyncStatus group="Woonkamer Stereo+FLEX Speaker" ...>
  <slave id="10.10.10.23" port="11000"/>
</SyncStatus>
```

**Extracted:**
- `group` attribute → `group_name`
- `<slave>` elements → converted to entity IDs
- Presence of slaves → `is_master = true`

## Use Cases

### Automations

**Check if player is master:**
```yaml
condition:
  - condition: state
    entity_id: media_player.woonkamer_stereo
    attribute: is_master
    state: true
```

**Get all group members:**
```yaml
variables:
  group_members: "{{ state_attr('media_player.woonkamer_stereo', 'bluos_group') }}"
```

**Loop through slaves:**
```yaml
repeat:
  for_each: "{{ state_attr('media_player.woonkamer_stereo', 'slaves') }}"
  sequence:
    - service: media_player.volume_set
      target:
        entity_id: "{{ repeat.item }}"
      data:
        volume_level: 0.5
```

### Templates

**Show group name:**
```yaml
{{ state_attr('media_player.woonkamer_stereo', 'group_name') }}
# Output: "Woonkamer Stereo+FLEX Speaker"
```

**Check if grouped:**
```yaml
{% if state_attr('media_player.flex_speaker', 'is_slave') %}
  Grouped with {{ state_attr('media_player.flex_speaker', 'master') }}
{% else %}
  Not grouped
{% endif %}
```

## Benefits

### 1. **Better Automation Support**
- Can reference entities directly without IP lookup
- Clear boolean flags for master/slave status
- Group name for display purposes

### 2. **More Robust**
- Entity IDs are stable (don't change with IP changes)
- Fallback to IP if entity not found
- Works across Home Assistant restarts

### 3. **Better UX**
- Attributes show meaningful entity names
- Easy to understand group structure
- Group name from BluOS shown

## Expected Attributes

### Ungrouped Player:
```yaml
bluos_group: []
master: null
slaves: []
is_master: false
is_slave: false
group_name: ""
```

### Master Player (Woonkamer):
```yaml
bluos_group:
  - media_player.woonkamer_stereo
  - media_player.flex_speaker
master: null
slaves:
  - media_player.flex_speaker
is_master: true
is_slave: false
group_name: "Woonkamer Stereo+FLEX Speaker"
```

### Slave Player (Flex):
```yaml
bluos_group:
  - media_player.woonkamer_stereo
  - media_player.flex_speaker
master: media_player.woonkamer_stereo
slaves: []
is_master: false
is_slave: true
group_name: "Woonkamer Stereo+FLEX Speaker"
```

## Files Modified

1. ✅ **Modified**: `custom_components/bluos/media_player.py`
   - Added `_ip_to_entity_id()` helper method
   - Enhanced `extra_state_attributes()` to use entity IDs
   - Added `is_master`, `is_slave`, and `group_name` attributes

## Testing

After updating:

1. **Check Ungrouped Player**:
   - All group attributes should be empty/false

2. **Group Players** (Woonkamer + Flex):
   - Woonkamer should show `is_master: true`
   - Flex should show `is_slave: true`
   - Both should show entity IDs in `bluos_group`
   - Woonkamer `slaves` should show `["media_player.flex_speaker"]`
   - Flex `master` should show `"media_player.woonkamer_stereo"`
   - Both should show `group_name: "Woonkamer Stereo+FLEX Speaker"`

3. **Ungroup Players**:
   - Both should show `is_master: false`, `is_slave: false`
   - All group attributes should be empty

## Ready to Push?

**Please review these changes!**

This makes group attributes much more useful:
- ✅ Entity IDs instead of IP addresses
- ✅ Clear boolean flags for master/slave
- ✅ Group name displayed
- ✅ Better automation support

Files to be committed:
- `custom_components/bluos/media_player.py` (modified)
