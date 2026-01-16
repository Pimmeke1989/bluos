# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.5] - 2026-01-16

### Fixed - CRITICAL HOTFIX
- **Integration Loading**: Fixed unsafe `coordinator.data` access in `__init__`
  - Integration now loads successfully
  - Players are discovered correctly
  - Prevents KeyError during initialization
- **Progress Bar Crash**: Fixed `media_position_updated_at` attribute name
  - Changed from `last_update_success_time` to `last_update_success`
  - Fixes AttributeError that occurred every update cycle
  - Progress bar now works without crashes

### Changed
- **Manufacturer**: Changed from "BluOS" to "Bluesound" (official brand name)
- **Icon**: Removed custom icon.png (uses default media player icon)

### Notes
- This is a critical hotfix for v1.0.4 which had breaking bugs
- If you're on v1.0.4, update immediately to v1.0.5

## [1.0.4] - 2026-01-16

### Fixed
- **Spotify and Local Music Playback**: Major fix for media information display
  - Now correctly parses separate `artist` and `album` XML fields from Spotify/local music
  - Previously only parsed radio format with "ARTIST - TITLE" in title2
  - Track name, artist, and album now display correctly for Spotify and local files
  - Radio streams continue to work as before
- **Progress Bar**: Added `media_position_updated_at` property
  - Progress bar now works during playback
  - Shows current position in track
- **Volume Display**: Added fallback to `/Status` endpoint
  - Prevents volume showing as 0 if `/Volume` endpoint fails
  - More robust volume reporting
- **Image Display**: Added `currentImage` to image sources
  - Spotify album art now displays correctly

### Added
- **Device Configuration URL**: Link to BluOS web interface on device page
- Smart parsing logic that detects Spotify vs Radio format automatically

### Changed
- Media information parsing now checks for separate artist/album fields first
- Falls back to title2 parsing for radio streams
- More robust error handling for volume endpoint

## [1.0.3] - 2026-01-16

### Fixed
- **Volume Display for Grouped Players**: Major fix for volume reporting
  - Now uses `/Volume` endpoint instead of `/Status` for volume information
  - Each player now shows its individual volume, even when grouped
  - Previously, grouped slaves showed the master's volume
  - Volume control continues to work correctly for all players

### Added
- **Integration Logo**: Added Bluesound logo (`icon.png`)
  - Shows in Settings → Devices & Services
  - Shows in HACS integration list
  - Professional branding throughout Home Assistant
- **Entity Picture**: Dynamic entity icons
  - Shows media artwork when playing
  - Shows default speaker icon when idle/paused
  - Fixes broken image icon in entity picker
- **Volume API Method**: New `get_volume()` method in API client
  - Fetches individual player volume from `/Volume` endpoint
  - Returns accurate volume even for grouped players

### Changed
- Volume data now fetched from `/Volume` endpoint on every update
- Entity picture dynamically updates based on playback state

## [1.0.2] - 2026-01-16

### Fixed
- **Media Information Display**: Fixed parsing of artist, title, and album from BluOS API
  - Artist now correctly parsed from `title2` field (e.g., "CARDIGANS - MY FAVORITE GAME")
  - Title now shows actual song/track name instead of station name
  - Album shows station name or actual album
  - Album art URLs now handled correctly (both full URLs and paths)
- **Join Functionality**: Fixed coordinator lookup using entity registry
  - Now properly finds master player coordinator
  - Added fallback to match by device name
- **Unjoin Functionality**: Fixed RemoveSlave API call
  - Now correctly calls RemoveSlave on master player (not slave)
  - Added direct API call fallback if master coordinator not found
  - Fixed master IP extraction from XML (was dict, now string)

### Added
- Additional status fields: `service_name`, `stream_format`, `preset_name`, `quality`, `db`
- Better error logging for join/unjoin operations
- Comprehensive debug logging for troubleshooting

## [1.0.1] - 2026-01-16

### Changed
- Made `group_name` parameter optional in `bluos.join` service
- Removed unnecessary `channelMode` parameter from AddSlave API call
- Group name now defaults to BluOS automatic naming if not specified

### Fixed
- Improved join/unjoin functionality with proper BluOS API parameters
- Enhanced error handling and logging for grouping operations
- Better entity lookup logic for finding master players

### Added
- Optional `group_name` field in join service for custom group naming
- Comprehensive debug logging for troubleshooting grouping issues
- Troubleshooting guide for join/unjoin operations

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

[1.0.5]: https://github.com/Pimmeke1989/bluos/releases/tag/v1.0.5
[1.0.4]: https://github.com/Pimmeke1989/bluos/releases/tag/v1.0.4
[1.0.3]: https://github.com/Pimmeke1989/bluos/releases/tag/v1.0.3
[1.0.2]: https://github.com/Pimmeke1989/bluos/releases/tag/v1.0.2
[1.0.1]: https://github.com/Pimmeke1989/bluos/releases/tag/v1.0.1
[1.0.0]: https://github.com/Pimmeke1989/bluos/releases/tag/v1.0.0
