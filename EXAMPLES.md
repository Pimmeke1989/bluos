# Example Automations for BluOS Integration

This file contains example automations to help you get started with the BluOS integration.

## Group Speakers When Playing

Automatically group bedroom speaker with living room when living room starts playing:

```yaml
automation:
  - alias: "Group Bedroom with Living Room on Play"
    trigger:
      - platform: state
        entity_id: media_player.living_room_speaker
        to: "playing"
    condition:
      - condition: state
        entity_id: media_player.bedroom_speaker
        state: "idle"
    action:
      - service: bluos.join
        target:
          entity_id: media_player.bedroom_speaker
        data:
          master: media_player.living_room_speaker
```

## Ungroup Speakers at Night

Automatically ungroup all speakers at bedtime:

```yaml
automation:
  - alias: "Ungroup Speakers at Bedtime"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: bluos.unjoin
        target:
          entity_id:
            - media_player.bedroom_speaker
            - media_player.kitchen_speaker
            - media_player.bathroom_speaker
```

## Volume Control Based on Time

Set different volume levels based on time of day:

```yaml
automation:
  - alias: "Morning Volume"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: media_player.volume_set
        target:
          entity_id: media_player.living_room_speaker
        data:
          volume_level: 0.3

  - alias: "Evening Volume"
    trigger:
      - platform: time
        at: "18:00:00"
    action:
      - service: media_player.volume_set
        target:
          entity_id: media_player.living_room_speaker
        data:
          volume_level: 0.5
```

## Play Preset on Button Press

Play a specific preset when a button is pressed:

```yaml
automation:
  - alias: "Play Radio on Button"
    trigger:
      - platform: state
        entity_id: binary_sensor.kitchen_button
        to: "on"
    action:
      - service: media_player.select_source
        target:
          entity_id: media_player.kitchen_speaker
        data:
          source: "Radio Paradise"
      - service: media_player.media_play
        target:
          entity_id: media_player.kitchen_speaker
```

## Sync Volume Across Group

Keep volume synchronized across grouped speakers:

```yaml
automation:
  - alias: "Sync Volume in Group"
    trigger:
      - platform: state
        entity_id: media_player.living_room_speaker
        attribute: volume_level
    condition:
      - condition: template
        value_template: "{{ state_attr('media_player.living_room_speaker', 'slaves') | length > 0 }}"
    action:
      - service: media_player.volume_set
        target:
          entity_id: media_player.bedroom_speaker
        data:
          volume_level: "{{ state_attr('media_player.living_room_speaker', 'volume_level') }}"
```

## Notification When Group Changes

Send a notification when speakers are grouped or ungrouped:

```yaml
automation:
  - alias: "Notify on Group Change"
    trigger:
      - platform: state
        entity_id: media_player.living_room_speaker
        attribute: blueos_group
    action:
      - service: notify.mobile_app
        data:
          title: "Speaker Group Changed"
          message: >
            Living room speaker group now has {{ state_attr('media_player.living_room_speaker', 'blueos_group') | length }} members
```

## Create Whole House Audio Scene

Create a scene that groups all speakers and starts playing:

```yaml
scene:
  - name: "Whole House Audio"
    entities:
      media_player.living_room_speaker:
        state: "playing"
        volume_level: 0.4
      media_player.bedroom_speaker:
        state: "playing"
        volume_level: 0.3
      media_player.kitchen_speaker:
        state: "playing"
        volume_level: 0.4

automation:
  - alias: "Activate Whole House Audio"
    trigger:
      - platform: state
        entity_id: input_boolean.party_mode
        to: "on"
    action:
      # First group all speakers
      - service: bluos.join
        target:
          entity_id: media_player.bedroom_speaker
        data:
          master: media_player.living_room_speaker
      - service: bluos.join
        target:
          entity_id: media_player.kitchen_speaker
        data:
          master: media_player.living_room_speaker
      # Then activate the scene
      - service: scene.turn_on
        target:
          entity_id: scene.whole_house_audio
```

## Scripts

### Group All Speakers

```yaml
script:
  group_all_speakers:
    alias: "Group All Speakers"
    sequence:
      - service: bluos.join
        target:
          entity_id: media_player.bedroom_speaker
        data:
          master: media_player.living_room_speaker
      - service: bluos.join
        target:
          entity_id: media_player.kitchen_speaker
        data:
          master: media_player.living_room_speaker
      - service: bluos.join
        target:
          entity_id: media_player.bathroom_speaker
        data:
          master: media_player.living_room_speaker
```

### Ungroup All Speakers

```yaml
script:
  ungroup_all_speakers:
    alias: "Ungroup All Speakers"
    sequence:
      - service: bluos.unjoin
        target:
          entity_id:
            - media_player.bedroom_speaker
            - media_player.kitchen_speaker
            - media_player.bathroom_speaker
            - media_player.living_room_speaker
```
