# Fix Slave IP Parsing - v1.0.10 (REVIEW BEFORE PUSH)

## Issue Fixed

### **Slaves Not Showing in Group Attributes** 🔧

**Problem**: Master player's `slaves` attribute was empty

**Root Cause**: Slave XML uses `id` attribute, not `ip`:
```xml
<slave id="10.10.10.23" port="11000"/>
```

But code was looking for:
```python
slave.get("ip", "")  # ← Wrong! Returns empty string
```

**Fix**: Use `id` attribute:
```python
slave.get("id", "")  # ← Correct!
```

## Changes Made

### File: `bluos_api.py` - Fixed slave IP extraction

**Before (BROKEN):**
```python
result["slaves"] = [
    {
        "ip": slave.get("ip", "") if isinstance(slave.get("ip"), str) else slave.get("ip", {}).get("_text", ""),
        "name": slave.get("name", ""),
        "zone": slave.get("zone", ""),
    }
    for slave in slaves
]
```

**After (FIXED):**
```python
result["slaves"] = [
    {
        # Slave XML: <slave id="10.10.10.23" port="11000"/>
        "ip": slave.get("id", ""),
        "name": slave.get("name", ""),
        "zone": slave.get("zone", ""),
    }
    for slave in slaves
]
```

## Expected Behavior After Fix

### Before (v1.0.9):

**Master (Woonkamer):**
```yaml
bluos_group: [media_player.woonkamer_stereo]  # ← Only master!
slaves: []  # ← Empty!
is_master: true
```

### After (v1.0.10):

**Master (Woonkamer):**
```yaml
bluos_group: [media_player.woonkamer_stereo, media_player.flex_speaker]  # ← Both!
slaves: [media_player.flex_speaker]  # ← Slave shown!
is_master: true
group_name: "Woonkamer Stereo+FLEX Speaker"
```

**Slave (Flex):**
```yaml
bluos_group: [media_player.woonkamer_stereo, media_player.flex_speaker]
master: media_player.woonkamer_stereo
slaves: []
is_slave: true
group_name: "Woonkamer Stereo+FLEX Speaker"
```

## SyncStatus XML Format

Your SyncStatus shows:
```xml
<SyncStatus group="Woonkamer Stereo+FLEX Speaker" ...>
  <slave id="10.10.10.23" port="11000"/>
</SyncStatus>
```

**Key point**: The slave IP is in the `id` attribute, NOT an `ip` attribute!

## Files Modified

1. ✅ **Modified**: `custom_components/bluos/bluos_api.py`
   - Fixed slave IP extraction to use `id` attribute
   - Simplified logic (removed complex isinstance check)

2. ✅ **Modified**: `custom_components/bluos/media_player.py`
   - Added debug logging (from previous change)

## Remaining Issues

### Battery Entities Not Working

This is a separate issue. The error message mentions:
```
ERROR [homeassistant.components.bluesound.coordinator]
```

**This is the OFFICIAL Bluesound integration, not our custom BluOS!**

**Questions:**
1. Do you have both integrations installed?
2. Are the battery sensors under the BluOS integration or Bluesound integration?

## Testing

After updating:

1. **Group Players**:
   - Woonkamer + Flex
   - Check Woonkamer attributes
   - Should show Flex in `slaves` and `bluos_group`

2. **Check Debug Logs** (if enabled):
   - Should see: `_ip_to_entity_id: Converting IP 10.10.10.23`
   - Should see: `_ip_to_entity_id: Found entity media_player.flex_speaker`

3. **Ungroup Players**:
   - Both should show empty group attributes

## Ready to Push?

**YES - This fixes the slave IP parsing issue!**

But battery entities issue needs separate investigation (might be related to official Bluesound integration conflict).

Files to be committed:
- `custom_components/bluos/bluos_api.py` (modified - slave IP fix)
- `custom_components/bluos/media_player.py` (modified - debug logging)
