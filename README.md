# BluOS Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/Pimmeke1989/bluos.svg)](https://github.com/Pimmeke1989/bluos/releases)
[![License](https://img.shields.io/github/license/Pimmeke1989/bluos.svg)](LICENSE)

A custom Home Assistant integration for BluOS/Bluesound devices with full media control, battery monitoring, and advanced group management.

## ✨ Features

### 🎵 Media Player Control
- **Playback Control**: Play, pause, stop, next, previous track
- **Volume Control**: Set volume level and mute/unmute
- **Source Selection**: Switch between different input sources and presets
- **Shuffle & Repeat**: Control shuffle and repeat modes (off/all/one)
- **Media Information**: Track title, artist, album, album art
- **Progress Tracking**: Real-time progress bar with 2-second updates
- **Fast Updates**: Media information refreshes every 2 seconds for responsive control

### 🔋 Battery Sensors
- **Battery Level**: Shows battery percentage (0-100%) for battery-powered devices
- **Charging Status**: Indicates "Charging" or "Not charging"
- **Auto-Detection**: Automatically creates sensors for devices with batteries (e.g., PULSE FLEX)
- **Works When Grouped**: Battery sensors continue to work even when device is in a group

### 👥 Multi-Room Audio & Group Management
- **Join/Unjoin Services**: Group and ungroup BluOS players
- **Entity IDs in Attributes**: Group members shown as entity IDs (not IP addresses)
- **Master/Slave Status**: Boolean flags (`is_master`, `is_slave`) for easy automation
- **Auto-Generated Group Names**: BluOS automatically creates group names (e.g., "Living Room+Bedroom")
- **Group Member List**: See all players in the group via `blueos_group` attribute

### 📱 Device Information
- **Device Name**: Actual device name from BluOS (e.g., "PULSE FLEX Speaker")
- **Model Information**: Full model name (e.g., "PULSE FLEX 2i")
- **Brand/Manufacturer**: Device manufacturer
- **MAC Address**: Network MAC address
- **Configuration URL**: Direct link to device configuration

## 📦 Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/Pimmeke1989/bluos`
6. Select category: "Integration"
7. Click "Add"
8. Search for "BluOS" in HACS
9. Click "Install"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/Pimmeke1989/bluos/releases)
2. Copy the `custom_components/bluos` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## ⚙️ Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "BluOS"
4. Enter the IP address of your BluOS device
5. Enter the port (default: 11000)
6. Click "Submit"

Repeat for each BluOS device you want to add.

## 🔧 Services

### bluos.join

Join a player to a master player to create a multi-room group.

**Parameters:**
- `entity_id`: The entity ID of the player to join to the group
- `master`: The entity ID of the master player

**Example:**
```yaml
service: bluos.join
target:
  entity_id: media_player.bedroom_speaker
data:
  master: media_player.living_room_speaker
```

### bluos.unjoin

Remove a player from its group.

**Parameters:**
- `entity_id`: The entity ID of the player to remove from the group

**Example:**
```yaml
service: bluos.unjoin
target:
  entity_id: media_player.bedroom_speaker
```

## 📊 Attributes

### Media Player Attributes

Each BluOS media player entity has the following attributes:

- `blueos_group`: List of entity IDs of all players in the current group
- `master`: Entity ID of the master player (if this player is a slave), or `null`
- `slaves`: List of entity IDs of slave players (if this player is a master)
- `is_master`: Boolean - `true` if this player is a group master
- `is_slave`: Boolean - `true` if this player is a slave in a group
- `group_name`: Auto-generated group name (e.g., "Living Room+Bedroom")
- `source_list`: Available input sources and presets
- `volume_level`: Current volume (0.0-1.0)
- `is_volume_muted`: Mute status
- `media_*`: Media metadata (title, artist, album, duration, position, etc.)

### Battery Sensor Attributes

For battery-powered devices:

- `battery_level`: Battery percentage
- `charging`: Boolean - `true` if charging
- `icon_path`: BluOS battery icon path

## 💡 Example Automations

### Low Battery Alert

```yaml
automation:
  - alias: "Flex Speaker Low Battery"
    trigger:
      - platform: numeric_state
        entity_id: sensor.flex_speaker_battery
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Flex speaker battery is low ({{ states('sensor.flex_speaker_battery') }}%)"
```

### Group Speakers at Sunset

```yaml
automation:
  - alias: "Group Speakers at Sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: bluos.join
        target:
          entity_id: media_player.bedroom_speaker
        data:
          master: media_player.living_room_speaker
```

### Ungroup When Master Stops Playing

```yaml
automation:
  - alias: "Ungroup When Master Stops"
    trigger:
      - platform: state
        entity_id: media_player.living_room_speaker
        to: "idle"
        for: "00:05:00"
    condition:
      - condition: state
        entity_id: media_player.living_room_speaker
        attribute: is_master
        state: true
    action:
      - service: bluos.unjoin
        target:
          entity_id: "{{ state_attr('media_player.living_room_speaker', 'slaves') }}"
```

## 🎯 Supported Devices

This integration works with all BluOS-enabled devices, including:

- **Bluesound**: PULSE, PULSE FLEX, PULSE MINI, NODE, POWERNODE, VAULT, etc.
- **NAD**: M10, M33, C 658, C 700, T 778, etc.
- **DALI**: BluOS-enabled speakers
- **And more**: Any device running BluOS firmware

## 📖 Documentation

- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Examples**: [EXAMPLES.md](EXAMPLES.md)
- **Troubleshooting**: [TROUBLESHOOTING_JOIN_UNJOIN.md](TROUBLESHOOTING_JOIN_UNJOIN.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🐛 Troubleshooting

### Cannot connect to device

- Verify the IP address is correct
- Ensure the device is powered on and connected to your network
- Check that port 11000 is accessible
- Verify there's no firewall blocking the connection

### Grouping not working

- Ensure all players are on the same network
- Check that all players are running compatible BluOS firmware versions
- Try ungrouping and regrouping the players
- Check the logs for any error messages

### Battery sensors not appearing

- Battery sensors only appear for battery-powered devices (e.g., PULSE FLEX)
- Remove and re-add the integration if sensors don't appear
- Check that the device is reporting battery information in `/SyncStatus`

## 🔄 Updates

The integration checks for updates every **2 seconds**, providing:
- Fast media information updates
- Smooth progress bar tracking
- Responsive volume and state changes
- Real-time group status

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Created by**: [@Pimmeke1989](https://github.com/Pimmeke1989)
- **Based on**: BluOS Custom Integration API v1.7
- **API Documentation**: Included in repository

## ⭐ Support

If you find this integration useful:
- ⭐ Star this repository
- 🐛 Report issues at [GitHub Issues](https://github.com/Pimmeke1989/bluos/issues)
- 💬 Share your feedback
- 📖 Contribute improvements

---

**Enjoy your BluOS devices in Home Assistant! 🎵**
