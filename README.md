# BluOS Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A custom Home Assistant integration for BluOS/Bluesound devices.

## Features

- **Media Player Control**: Full control of BluOS devices including play, pause, stop, next, previous
- **Volume Control**: Set volume level and mute/unmute
- **Source Selection**: Switch between different input sources and presets
- **Shuffle & Repeat**: Control shuffle and repeat modes
- **Multi-room Audio**: Group and ungroup BluOS players
- **Group Information**: Each player shows its group membership via the `blueos_group` attribute

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/pimlo/bluos`
6. Select category: "Integration"
7. Click "Add"
8. Search for "BluOS" in HACS
9. Click "Install"
10. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/bluos` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "BluOS"
4. Enter the IP address of your BluOS device
5. Enter the port (default: 11000)
6. Click "Submit"

## Services

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

## Attributes

Each BluOS media player entity has the following special attributes:

- `blueos_group`: List of IP addresses of all players in the current group
- `master`: IP address of the master player (if this player is a slave)
- `slaves`: List of IP addresses of slave players (if this player is a master)

## Supported Devices

This integration should work with all BluOS-enabled devices, including:
- Bluesound speakers and players
- NAD amplifiers with BluOS
- Other BluOS-compatible devices

## API Documentation

This integration is based on the BluOS Custom Integration API v1.7. The API uses HTTP GET requests on port 11000 and returns XML responses.

## Troubleshooting

### Cannot connect to device

- Verify the IP address is correct
- Ensure the device is powered on and connected to your network
- Check that port 11000 is accessible
- Verify there's no firewall blocking the connection

### Grouping not working

- Ensure all players are on the same network
- Check that all players are running compatible BluOS firmware versions
- Try ungrouping and regrouping the players

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Credits

Created by @pimlo

Based on the BluOS Custom Integration API v1.7 documentation.
