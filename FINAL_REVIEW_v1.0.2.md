# Complete Changes Summary - v1.0.2 (FINAL REVIEW)

## Issues Fixed

### 1. **Unjoin Not Working**
- Master IP parsed as dict instead of string
- RemoveSlave called on slave (wrong - must call on master!)

### 2. **Join Not Working**
- Couldn't find master coordinator (entity_id doesn't contain entry_id)

### 3. **Media Information Missing** ⭐ NEW
- Artist not showing (was looking for non-existent `artist` field)
- Title showing wrong data (was using `title1` instead of parsed `title`)
- Album art not displaying (image URLs not handled correctly)

## Detailed Changes

### File 1: `bluos_api.py` - `get_status()` method

#### Change 1.1: Parse artist and title from title2

**BluOS API Format:**
```xml
<title1>Radio 538</title1>              <!-- Station/Album name -->
<title2>CARDIGANS - MY FAVORITE GAME</title2>  <!-- Artist - Title -->
<title3>Jouw hits, jouw 538!</title3>   <!-- Description -->
```

**Before:**
```python
result = {
    "title1": status.get("title1", ""),
    "title2": status.get("title2", ""),
    "artist": status.get("artist", ""),  # ← Doesn't exist!
    "album": status.get("album", ""),    # ← Doesn't exist!
}
```

**After:**
```python
# Parse artist and title from title2
title2 = status.get("title2", "")
artist = ""
title = ""

if " - " in title2:
    parts = title2.split(" - ", 1)
    artist = parts[0].strip()  # "CARDIGANS"
    title = parts[1].strip()   # "MY FAVORITE GAME"
else:
    title = title2

result = {
    # Original BluOS fields
    "title1": status.get("title1", ""),  # "Radio 538"
    "title2": title2,                     # "CARDIGANS - MY FAVORITE GAME"
    "title3": status.get("title3", ""),  # "Jouw hits, jouw 538!"
    # Parsed fields for media player
    "title": title or status.get("title1", ""),  # "MY FAVORITE GAME"
    "artist": artist,                             # "CARDIGANS"
    "album": status.get("album", "") or status.get("title1", ""),  # "Radio 538"
}
```

#### Change 1.2: Handle image URLs correctly

**BluOS API Format:**
```xml
<image>http://cdn-profiles.tunein.com/s6712/images/logog.png</image>
```

**Before:**
```python
"image": status.get("image", ""),  # Returns full URL
```

**After:**
```python
# Get image URL - can be full URL or path
image = status.get("image", "") or status.get("stationImage", "")
result["image"] = image  # Preserve full URL
```

#### Change 1.3: Added additional useful fields

**New fields:**
```python
"service_name": status.get("serviceName", ""),     # "TuneIn"
"service_icon": status.get("serviceIcon", ""),     # "/Sources/images/TuneInIcon.png"
"stream_format": status.get("streamFormat", ""),   # "MP3 0 kb/s"
"can_seek": status.get("canSeek", "0") == "1",     # false for radio
"is_preset": status.get("is_preset", "false") == "true",
"preset_name": status.get("preset_name", ""),      # "Radio 538"
"quality": status.get("quality", "0"),
"db": status.get("db", "0"),                       # "-44"
```

#### Change 1.4: Fixed master IP extraction in `get_sync_status()`

**Before:**
```python
result["master"] = sync_status.get("master")  # Returns {'port': '11000', '_text': '10.10.10.31'}
```

**After:**
```python
master_data = sync_status.get("master")
if isinstance(master_data, dict):
    result["master"] = master_data.get("_text", "")  # Extract "10.10.10.31"
else:
    result["master"] = master_data
```

### File 2: `media_player.py`

#### Change 2.1: Use parsed title field

**Before:**
```python
def media_title(self) -> str | None:
    return self.coordinator.data["status"].get("title1", "")  # "Radio 538"
```

**After:**
```python
def media_title(self) -> str | None:
    # Use parsed title (from title2) or fall back to title1
    return self.coordinator.data["status"].get("title", "")  # "MY FAVORITE GAME"
```

#### Change 2.2: Handle full image URLs

**Before:**
```python
def media_image_url(self) -> str | None:
    image = self.coordinator.data["status"].get("image", "")
    if image:
        return f"http://{self._entry.data[CONF_HOST]}:11000{image}"  # ← Breaks full URLs!
```

**After:**
```python
def media_image_url(self) -> str | None:
    image = self.coordinator.data["status"].get("image", "")
    if image:
        # Image can be a full URL or a path
        if image.startswith("http://") or image.startswith("https://"):
            return image  # Return as-is
        else:
            return f"http://{self._entry.data[CONF_HOST]}:11000{image}"
```

#### Change 2.3: Fixed `async_join_player()` - Use entity registry

**Before:**
```python
# Try to find coordinator by checking if entry_id is in entity_id
for entry_id, coordinator in self.hass.data[DOMAIN].items():
    if entry_id in master:  # ← Doesn't work!
        master_coordinator = coordinator
```

**After:**
```python
# Method 1: Use entity registry
from homeassistant.helpers import entity_registry as er
entity_reg = er.async_get(self.hass)
master_entity_entry = entity_reg.async_get(master)

if master_entity_entry:
    if master_entity_entry.config_entry_id in self.hass.data[DOMAIN]:
        master_coordinator = self.hass.data[DOMAIN][master_entity_entry.config_entry_id]

# Method 2: Fallback - match by device name
if not master_coordinator:
    master_name = master_entity.attributes.get("friendly_name", "")
    for entry_id, coordinator in self.hass.data[DOMAIN].items():
        coordinator_name = coordinator.data.get("status", {}).get("name", "")
        if coordinator_name and coordinator_name in master_name:
            master_coordinator = coordinator
```

#### Change 2.4: Fixed `async_unjoin_player()` - Call on master

**Before:**
```python
if master_coordinator:
    # Call on master
else:
    # WRONG: Call on slave!
    result = await self.hass.async_add_executor_job(
        self.coordinator.api.remove_slave  # ← This is the slave!
    )
```

**After:**
```python
slave_ip = self._entry.data[CONF_HOST]

if master_coordinator:
    # Use master's coordinator
    result = await self.hass.async_add_executor_job(
        master_coordinator.api.remove_slave, slave_ip
    )
else:
    # Make direct API call to master
    from .bluos_api import BluOSApi
    master_api = BluOSApi(master_ip, self._entry.data.get("port", 11000))
    result = await self.hass.async_add_executor_job(
        master_api.remove_slave, slave_ip
    )
```

## Expected Results

### Media Information Display

**Before:**
- Title: "Radio 538" (wrong - showing station name)
- Artist: "" (empty)
- Album: "" (empty)
- Image: Not showing (URL broken)

**After:**
- Title: "MY FAVORITE GAME" ✅
- Artist: "CARDIGANS" ✅
- Album: "Radio 538" ✅ (station name as album)
- Image: Shows correctly ✅

### Join/Unjoin

**Join:**
```
Found master coordinator by entity registry: 01KF3GPW3W8C2H47M9CZNNHE9T (IP: 10.10.10.31)
Successfully joined 10.10.10.23 to 10.10.10.31
```

**Unjoin:**
```
Player is a slave. Removing from master 10.10.10.31
Found master coordinator for IP 10.10.10.31
RemoveSlave via coordinator result: True
```

## Files Modified

1. ✅ `custom_components/bluos/bluos_api.py`
   - Fixed `get_status()` - Parse artist/title from title2
   - Fixed `get_status()` - Handle image URLs
   - Fixed `get_status()` - Added additional fields
   - Fixed `get_sync_status()` - Extract master IP from dict

2. ✅ `custom_components/bluos/media_player.py`
   - Fixed `media_title` - Use parsed title
   - Fixed `media_image_url` - Handle full URLs
   - Fixed `async_join_player()` - Use entity registry
   - Fixed `async_unjoin_player()` - Call on master with direct API fallback

## Testing Checklist

After updating:

- [ ] Check media title shows song name, not station name
- [ ] Check artist shows correctly
- [ ] Check album art displays
- [ ] Test join - should find coordinator
- [ ] Test unjoin - should actually unjoin
- [ ] Check logs for any errors

## Ready to Push?

**All changes documented above. Please review before I push to GitHub.**
