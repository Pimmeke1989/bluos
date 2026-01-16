# BluOS Integration Setup Guide

This guide will walk you through setting up the BluOS integration for Home Assistant.

## Prerequisites

- Home Assistant installed and running (version 2023.1 or later recommended)
- BluOS-enabled device(s) on your network
- HACS installed (for easy installation) or ability to manually copy files

## Installation Methods

### Method 1: HACS (Recommended)

1. **Add Custom Repository**
   - Open HACS in your Home Assistant
   - Click on "Integrations"
   - Click the three dots (⋮) in the top right corner
   - Select "Custom repositories"
   - Add repository URL: `https://github.com/Pimmeke1989/bluos`
   - Select category: "Integration"
   - Click "Add"

2. **Install the Integration**
   - Search for "BluOS" in HACS
   - Click on the BluOS integration
   - Click "Download"
   - Restart Home Assistant

### Method 2: Manual Installation

1. **Download the Integration**
   - Download the latest release from GitHub
   - Extract the files

2. **Copy Files**
   - Copy the `custom_components/bluos` folder to your Home Assistant's `config/custom_components/` directory
   - Your structure should look like: `config/custom_components/bluos/`

3. **Restart Home Assistant**
   - Restart Home Assistant to load the new integration

## Configuration

### Finding Your BluOS Device IP Address

Before configuring, you need to know your BluOS device's IP address:

1. **Using the BluOS App**
   - Open the BluOS Controller app
   - Go to Settings → Player Information
   - Note the IP address shown

2. **Using Your Router**
   - Log into your router's admin panel
   - Look for connected devices
   - Find your BluOS device (usually named after the device model)

3. **Using Network Scanner**
   - Use a network scanning tool like Fing or Advanced IP Scanner
   - Look for devices on port 11000

### Adding the Integration

1. **Navigate to Integrations**
   - Go to Settings → Devices & Services
   - Click the "+ Add Integration" button

2. **Search for BluOS**
   - Type "BluOS" in the search box
   - Click on "BluOS" when it appears

3. **Enter Connection Details**
   - **IP Address**: Enter your BluOS device's IP address (e.g., `192.168.1.100`)
   - **Port**: Enter `11000` (this is the default BluOS API port)
   - Click "Submit"

4. **Verify Connection**
   - The integration will attempt to connect to your device
   - If successful, you'll see a success message
   - Your device will now appear in Home Assistant

### Adding Multiple Devices

To add multiple BluOS devices:
- Repeat the "Adding the Integration" steps for each device
- Each device will be added as a separate integration instance

## Verifying Installation

### Check Device Status

1. Go to Settings → Devices & Services → BluOS
2. You should see your device listed
3. Click on the device to see its entities

### Check Media Player Entity

1. Go to Developer Tools → States
2. Search for `media_player.` followed by your device name
3. You should see attributes like:
   - `blueos_group`: List of grouped players
   - `master`: Master player IP (if grouped)
   - `slaves`: Slave player IPs (if this is a master)

## Testing the Integration

### Test Basic Playback

1. Go to Overview or Media
2. Find your BluOS media player
3. Try playing content from a source
4. Test volume control, pause, skip, etc.

### Test Grouping

1. **Join Players**
   ```yaml
   service: bluos.join
   target:
     entity_id: media_player.bedroom_speaker
   data:
     master: media_player.living_room_speaker
   ```

2. **Unjoin Players**
   ```yaml
   service: bluos.unjoin
   target:
     entity_id: media_player.bedroom_speaker
   ```

3. **Check Group Status**
   - Look at the `blueos_group` attribute
   - It should list all players in the group

## Troubleshooting

### Cannot Find Integration

**Problem**: BluOS doesn't appear in the integration list

**Solutions**:
- Ensure you've restarted Home Assistant after installation
- Check that files are in the correct location: `config/custom_components/bluos/`
- Check Home Assistant logs for any errors

### Cannot Connect to Device

**Problem**: "Failed to connect" error during setup

**Solutions**:
- Verify the IP address is correct
- Ensure the device is powered on and connected to the network
- Check that port 11000 is not blocked by a firewall
- Try pinging the device from your Home Assistant server
- Ensure your Home Assistant and BluOS device are on the same network

### Device Shows as Unavailable

**Problem**: Device appears but shows as "unavailable"

**Solutions**:
- Check network connectivity
- Verify the device hasn't changed IP addresses
- Restart the BluOS device
- Restart Home Assistant
- Check Home Assistant logs for connection errors

### Grouping Not Working

**Problem**: Join/unjoin services don't work

**Solutions**:
- Ensure all devices are on the same network
- Verify all devices are running compatible firmware
- Check that both devices are properly configured in Home Assistant
- Try ungrouping via the BluOS app first, then try again
- Check Home Assistant logs for errors

### Missing Presets/Sources

**Problem**: Source list is empty or incomplete

**Solutions**:
- Ensure presets are configured in the BluOS app
- Restart the integration
- Check if the device is properly responding to API calls
- Verify the device firmware is up to date

## Advanced Configuration

### Static IP Address

For best results, assign a static IP address to your BluOS devices:

1. **Via Router DHCP Reservation**
   - Log into your router
   - Find your BluOS device's MAC address
   - Create a DHCP reservation for that MAC address

2. **Via BluOS Device** (if supported)
   - Some BluOS devices allow setting a static IP in their settings
   - Check your device's manual for instructions

### Firewall Configuration

If you have a firewall between Home Assistant and your BluOS devices:
- Allow TCP port 11000 (BluOS API)
- Allow the Home Assistant server IP to communicate with BluOS device IPs

## Next Steps

- Check out [EXAMPLES.md](EXAMPLES.md) for automation ideas
- Create automations to group/ungroup speakers based on time or events
- Set up scenes for different listening scenarios
- Explore the media player controls in your dashboard

## Getting Help

If you encounter issues:

1. **Check the Logs**
   - Go to Settings → System → Logs
   - Look for errors related to "bluos"

2. **Enable Debug Logging**
   Add to your `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.bluos: debug
   ```

3. **Report Issues**
   - Visit https://github.com/Pimmeke1989/bluos/issues
   - Provide details about your setup and the issue
   - Include relevant logs

## Updating the Integration

### Via HACS
1. HACS will notify you when updates are available
2. Click "Update" in HACS
3. Restart Home Assistant

### Manual Update
1. Download the latest release
2. Replace the files in `custom_components/bluos/`
3. Restart Home Assistant

---

**Congratulations!** Your BluOS integration is now set up and ready to use. Enjoy your multi-room audio experience!
