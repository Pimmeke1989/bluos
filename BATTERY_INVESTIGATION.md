# Battery Issue Investigation

## Error Message Analysis

The error you're seeing:
```
ERROR (MainThread) [homeassistant.components.bluesound.coordinator] 
Error requesting Woonkamer Stereo data: 'ConfigEntry' object has no attribute 'runtime_data'
```

### Key Observations:

1. **Wrong Component**: `homeassistant.components.bluesound` (official) vs `custom_components.bluos` (ours)
2. **runtime_data**: This is a newer Home Assistant feature used by the official integration
3. **Appears for both devices**: Woonkamer Stereo AND FLEX Speaker

## Possible Scenarios

### Scenario 1: Both Integrations Installed (Most Likely)

You have BOTH:
- **Official "Bluesound" integration** (built into Home Assistant)
- **Custom "BluOS" integration** (our custom component)

**How to check:**
1. Go to Settings → Devices & Services
2. Look for BOTH "Bluesound" and "BluOS"
3. Check which devices are under which integration

**Solution:**
- Remove one of the integrations
- Keep only the one you want to use

### Scenario 2: Wrong Integration Loading

Home Assistant might be loading the official Bluesound integration instead of our custom BluOS.

**How to check:**
1. Check entity IDs:
   - Custom BluOS: `media_player.flex_speaker`, `sensor.flex_speaker_battery`
   - Official Bluesound: Different naming pattern

### Scenario 3: Cached Error

The error might be from a previous installation of the official integration.

**Solution:**
- Restart Home Assistant
- Clear browser cache

## Investigation Steps

### Step 1: Check Installed Integrations

Go to Settings → Devices & Services and answer:

1. **Do you see "Bluesound"?** (official integration)
2. **Do you see "BluOS"?** (our custom integration)
3. **How many devices under each?**

### Step 2: Check Entity IDs

Look at your Flex speaker entities:

**Media Player:**
- What's the entity ID? (e.g., `media_player.flex_speaker`)
- What integration does it belong to?

**Battery Sensors:**
- Do they exist at all?
- What are their entity IDs?
- What integration do they belong to?

### Step 3: Check Logs with Domain Filter

Enable debug logging for BOTH:

```yaml
logger:
  default: info
  logs:
    custom_components.bluos: debug
    homeassistant.components.bluesound: debug
```

Restart and check which integration is actually running.

### Step 4: Check Battery Data

Go to: `http://10.10.10.23:11000/Status`

Look for the battery element:
```xml
<battery level="100" charging="true" icon="..."/>
```

**Questions:**
- Is the battery element present?
- What are the values?

## Expected Behavior

### If Using Custom BluOS Integration:

**Entities should be:**
- `media_player.flex_speaker` (or similar)
- `sensor.flex_speaker_battery`
- `sensor.flex_speaker_battery_charging`

**Logs should show:**
- `custom_components.bluos` messages
- NO `homeassistant.components.bluesound` messages

**Battery sensors should:**
- Show battery level (0-100%)
- Show charging status
- Update every 5 seconds

### If Using Official Bluesound Integration:

**Entities would be:**
- Different naming pattern
- NO battery sensors (official integration doesn't support battery)

**Logs would show:**
- `homeassistant.components.bluesound` messages
- The `runtime_data` error

## Diagnostic Commands

### Check Integration Files

```bash
# Check if custom integration exists
ls custom_components/bluos/

# Check if official integration is being used
# (Official integration is built into HA, no files to check)
```

### Check Entity Registry

In Developer Tools → States:
- Filter by "flex"
- Look at all entities
- Check which integration they belong to

## Most Likely Solution

Based on the error message, I believe you have the **official Bluesound integration** installed alongside our custom BluOS integration.

**Recommended Action:**

1. **Remove Official Bluesound Integration:**
   - Settings → Devices & Services
   - Find "Bluesound"
   - Click the 3 dots → Delete

2. **Keep Only Custom BluOS Integration:**
   - Ensure "BluOS" is still there
   - Restart Home Assistant

3. **Verify:**
   - Battery sensors should appear
   - No more `bluesound.coordinator` errors

## Questions to Answer

Please provide:

1. **Screenshot of Settings → Devices & Services** showing all integrations
2. **Entity IDs** for Flex speaker (media_player and sensors)
3. **Status XML** from `http://10.10.10.23:11000/Status` (just the battery line)
4. **Logs** after enabling debug logging

This will help us determine exactly what's happening!
