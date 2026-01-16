# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-16

### Added
- Initial release of BluOS integration
- Media player platform with full playback control
- Volume control (set level, mute/unmute)
- Source/preset selection
- Shuffle and repeat mode control
- Multi-room audio grouping support
- `bluos.join` service to add players to groups
- `bluos.unjoin` service to remove players from groups
- `blueos_group` attribute showing all players in the current group
- Config flow for easy setup via UI
- HACS support for easy installation
- Support for all standard media player features
- Automatic status polling every 5 seconds
- Album art display
- Media information (title, artist, album)
- Playback position tracking

### Features
- Local polling integration (no cloud required)
- XML API parsing for BluOS devices
- Support for multiple BluOS devices
- Group master/slave relationship tracking
- Preset/source management

[1.0.0]: https://github.com/pimlo/bluos/releases/tag/v1.0.0
