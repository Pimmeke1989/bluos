# BluOS Integration - Quick Reference

## Services

### bluos.join
Join a player to a master player group.

**Parameters:**
- `entity_id` (required): The player to join to the group
- `master` (required): The master player entity ID

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
- `entity_id` (required): The player to remove from the group

**Example:**
```yaml
service: bluos.unjoin
target:
  entity_id: media_player.bedroom_speaker
```

## Standard Media Player Services

All standard Home Assistant media player services are supported:

- `media_player.turn_on` - Start playback
- `media_player.turn_off` - Stop playback
- `media_player.media_play` - Play
- `media_player.media_pause` - Pause
- `media_player.media_stop` - Stop
- `media_player.media_next_track` - Next track
- `media_player.media_previous_track` - Previous track
- `media_player.volume_set` - Set volume (0.0 to 1.0)
- `media_player.volume_up` - Increase volume
- `media_player.volume_down` - Decrease volume
- `media_player.volume_mute` - Mute/unmute
- `media_player.select_source` - Select input source/preset
- `media_player.shuffle_set` - Enable/disable shuffle
- `media_player.repeat_set` - Set repeat mode (off/all/one)

## Attributes

Each BluOS media player has these special attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `blueos_group` | list | IP addresses of all players in the current group |
| `master` | string | IP address of the master player (if this is a slave) |
| `slaves` | list | IP addresses of slave players (if this is a master) |

**Example:**
```yaml
# Check if a player is in a group
{{ state_attr('media_player.bedroom_speaker', 'blueos_group') | length > 0 }}

# Get the master player IP
{{ state_attr('media_player.bedroom_speaker', 'master') }}

# Count slaves
{{ state_attr('media_player.living_room_speaker', 'slaves') | length }}
```

## Common Patterns

### Group All Speakers
```yaml
script:
  group_all:
    sequence:
      - service: bluos.join
        target:
          entity_id: media_player.bedroom
        data:
          master: media_player.living_room
      - service: bluos.join
        target:
          entity_id: media_player.kitchen
        data:
          master: media_player.living_room
```

### Ungroup All Speakers
```yaml
script:
  ungroup_all:
    sequence:
      - service: bluos.unjoin
        target:
          entity_id:
            - media_player.bedroom
            - media_player.kitchen
            - media_player.living_room
```

### Check Group Status
```yaml
# Template to check if player is grouped
{% if state_attr('media_player.bedroom', 'blueos_group') | length > 1 %}
  Player is in a group
{% else %}
  Player is standalone
{% endif %}
```

### Conditional Grouping
```yaml
# Only group if not already grouped
- condition: template
  value_template: "{{ state_attr('media_player.bedroom', 'master') is none }}"
- service: bluos.join
  target:
    entity_id: media_player.bedroom
  data:
    master: media_player.living_room
```

## Lovelace Card Examples

### Simple Media Control
```yaml
type: media-control
entity: media_player.living_room_speaker
```

### Custom Card with Group Info
```yaml
type: entities
entities:
  - entity: media_player.living_room_speaker
  - type: attribute
    entity: media_player.living_room_speaker
    attribute: blueos_group
    name: Group Members
  - type: attribute
    entity: media_player.living_room_speaker
    attribute: slaves
    name: Slaves
```

### Group Control Buttons
```yaml
type: vertical-stack
cards:
  - type: media-control
    entity: media_player.living_room_speaker
  - type: horizontal-stack
    cards:
      - type: button
        name: Group All
        tap_action:
          action: call-service
          service: script.group_all
      - type: button
        name: Ungroup All
        tap_action:
          action: call-service
          service: script.ungroup_all
```

## API Endpoints

The integration uses these BluOS API endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/Status` | Get player status, playback info |
| `/SyncStatus` | Get group/sync information |
| `/Presets` | Get available sources/presets |
| `/Play` | Start playback |
| `/Pause` | Pause/stop playback |
| `/Volume` | Set volume or mute |
| `/Skip` | Next track |
| `/Back` | Previous track |
| `/AddSlave` | Add player to group |
| `/RemoveSlave` | Remove player from group |
| `/Shuffle` | Set shuffle mode |
| `/Repeat` | Set repeat mode |
| `/Preset` | Select preset/source |

## Port Information

- **Default Port**: 11000
- **Protocol**: HTTP
- **Response Format**: XML

## Tips

1. **Use Static IPs**: Assign static IP addresses to your BluOS devices for reliability
2. **Group Order**: Always join slaves to a master, not the other way around
3. **Refresh Rate**: Status updates every 5 seconds by default
4. **Network**: Ensure all devices are on the same network segment
5. **Firmware**: Keep BluOS firmware updated for best compatibility

## Troubleshooting Quick Checks

```yaml
# Check if device is responding
{{ states('media_player.living_room_speaker') }}

# Check last update time
{{ state_attr('media_player.living_room_speaker', 'last_changed') }}

# Check if grouped
{{ state_attr('media_player.living_room_speaker', 'blueos_group') }}

# Count group members
{{ state_attr('media_player.living_room_speaker', 'blueos_group') | length }}
```

## Support

- **Documentation**: [README.md](README.md)
- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Examples**: [EXAMPLES.md](EXAMPLES.md)
- **Issues**: https://github.com/Pimmeke1989/bluos/issues
