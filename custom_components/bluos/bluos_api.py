"""BluOS API client."""
import logging
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import quote

import requests

_LOGGER = logging.getLogger(__name__)


class BluOSApi:
    """BluOS API client."""

    def __init__(self, host: str, port: int = 11000) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = 10

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> str | None:
        """Make a GET request to the BluOS API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as err:
            _LOGGER.error("Error making request to %s: %s", url, err)
            return None

    def _parse_xml(self, xml_string: str) -> dict[str, Any] | None:
        """Parse XML response."""
        if not xml_string:
            return None
        
        try:
            root = ET.fromstring(xml_string)
            return self._element_to_dict(root)
        except ET.ParseError as err:
            _LOGGER.error("Error parsing XML: %s", err)
            return None

    def _element_to_dict(self, element: ET.Element) -> dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Add text content
        if element.text and element.text.strip():
            if len(element.attrib) == 0 and len(list(element)) == 0:
                return element.text.strip()
            result["_text"] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._element_to_dict(child)
            if child.tag in result:
                # Handle multiple children with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result

    def get_status(self) -> dict[str, Any] | None:
        """Get player status."""
        response = self._get("Status")
        if not response:
            return None
        
        status = self._parse_xml(response)
        if not status:
            return None
        
        # Parse artist and title
        # Spotify and local music provide separate artist/album fields
        # Radio streams combine them in title2 as "ARTIST - TITLE"
        
        # Check if we have separate artist/album fields (Spotify, local music)
        has_artist_field = bool(status.get("artist", ""))
        has_album_field = bool(status.get("album", ""))
        
        if has_artist_field:
            # Spotify/local music format
            artist = status.get("artist", "")
            title = status.get("title1", "")  # Spotify puts track name in title1
            album = status.get("album", "")
        else:
            # Radio stream format - parse from title2
            title2 = status.get("title2", "")
            if " - " in title2:
                # Split on first " - " to separate artist and title
                parts = title2.split(" - ", 1)
                artist = parts[0].strip()
                title = parts[1].strip()
            else:
                artist = ""
                title = title2 or status.get("title1", "")
            album = status.get("title1", "")  # Station name as album for radio
        
        # Get image URL - can be full URL or path
        image = status.get("image", "") or status.get("currentImage", "") or status.get("stationImage", "")
        
        # Extract relevant information
        result = {
            "name": status.get("name", "BluOS Player"),
            "state": self._parse_state(status.get("state")),
            "volume": int(status.get("volume", 0)),
            "mute": status.get("mute", "0") == "1",
            "shuffle": status.get("shuffle", "0") == "1",
            "repeat": status.get("repeat", "0"),
            "service": status.get("service", ""),
            "service_name": status.get("serviceName", ""),
            "service_icon": status.get("serviceIcon", ""),
            # Title fields from BluOS
            "title1": status.get("title1", ""),
            "title2": status.get("title2", ""),
            "title3": status.get("title3", ""),
            # Parsed fields for media player
            "title": title,
            "artist": artist,
            "album": album,
            # Image
            "image": image,
            # Playback info
            "totlen": int(status.get("totlen", 0)),
            "secs": int(status.get("secs", 0)),
            "can_seek": status.get("canSeek", "0") == "1",
            # Stream info
            "stream_format": status.get("streamFormat", ""),
            "stream_url": status.get("streamUrl", ""),
            # Preset info
            "is_preset": status.get("is_preset", "false") == "true",
            "preset_id": status.get("preset_id", ""),
            "preset_name": status.get("preset_name", ""),
            # Quality
            "quality": status.get("quality", "0"),
            "db": status.get("db", "0"),
            # Group (for compatibility)
            "group": status.get("group", {}),
        }
        
        return result

    def _parse_state(self, state: str | None) -> str:
        """Parse player state."""
        if not state:
            return "idle"
        
        state_map = {
            "play": "playing",
            "pause": "paused",
            "stop": "idle",
            "stream": "playing",
        }
        
        return state_map.get(state.lower(), "idle")

    def get_sync_status(self) -> dict[str, Any] | None:
        """Get sync/group status."""
        response = self._get("SyncStatus")
        if not response:
            return None
        
        sync_status = self._parse_xml(response)
        if not sync_status:
            return None
        
        # Parse group information
        result = {
            "master": None,
            "slaves": [],
            "zone": sync_status.get("zone"),
            "master_id": sync_status.get("master"),
        }
        
        # Check if this player is a slave
        if sync_status.get("master"):
            master_data = sync_status.get("master")
            # Master can be a string (IP) or a dict with _text containing the IP
            if isinstance(master_data, dict):
                result["master"] = master_data.get("_text", "")
            else:
                result["master"] = master_data
        
        # Get list of slaves if this is a master
        if "slave" in sync_status:
            slaves = sync_status["slave"]
            if not isinstance(slaves, list):
                slaves = [slaves]
            result["slaves"] = [
                {
                    "ip": slave.get("ip", "") if isinstance(slave.get("ip"), str) else slave.get("ip", {}).get("_text", ""),
                    "name": slave.get("name", ""),
                    "zone": slave.get("zone", ""),
                }
                for slave in slaves
            ]
        
        return result

    def get_presets(self) -> list[dict[str, Any]]:
        """Get available presets/sources."""
        response = self._get("Presets")
        if not response:
            return []
        
        presets_data = self._parse_xml(response)
        if not presets_data or "preset" not in presets_data:
            return []
        
        presets = presets_data["preset"]
        if not isinstance(presets, list):
            presets = [presets]
        
        return [
            {
                "id": preset.get("id", ""),
                "name": preset.get("name", ""),
                "url": preset.get("url", ""),
            }
            for preset in presets
        ]

    def get_volume(self) -> dict[str, Any] | None:
        """Get volume information from /Volume endpoint.
        
        This endpoint returns the individual player's volume,
        even when grouped (unlike /Status which returns master's volume).
        """
        response = self._get("Volume")
        if not response:
            return None
        
        volume_data = self._parse_xml(response)
        if not volume_data:
            return None
        
        # Parse volume information
        result = {
            "volume": int(volume_data.get("volume", 0)),
            "mute": volume_data.get("mute", "0") == "1",
            "db": volume_data.get("db", "0"),
        }
        
        return result

    def play(self) -> bool:
        """Start playback."""
        response = self._get("Play")
        return response is not None

    def pause(self) -> bool:
        """Pause playback."""
        response = self._get("Pause")
        return response is not None

    def stop(self) -> bool:
        """Stop playback."""
        response = self._get("Pause")  # BluOS uses Pause for stop
        return response is not None

    def play_pause(self) -> bool:
        """Toggle play/pause."""
        response = self._get("Pause", {"toggle": "1"})
        return response is not None

    def next_track(self) -> bool:
        """Skip to next track."""
        response = self._get("Skip")
        return response is not None

    def previous_track(self) -> bool:
        """Skip to previous track."""
        response = self._get("Back")
        return response is not None

    def set_volume(self, volume: int) -> bool:
        """Set volume level (0-100)."""
        response = self._get("Volume", {"level": volume})
        return response is not None

    def volume_up(self) -> bool:
        """Increase volume."""
        response = self._get("Volume", {"level": "+3"})
        return response is not None

    def volume_down(self) -> bool:
        """Decrease volume."""
        response = self._get("Volume", {"level": "-3"})
        return response is not None

    def mute(self, mute: bool) -> bool:
        """Mute or unmute."""
        response = self._get("Volume", {"mute": "1" if mute else "0"})
        return response is not None

    def select_preset(self, preset_id: str) -> bool:
        """Select a preset/source."""
        response = self._get("Preset", {"id": preset_id})
        return response is not None

    def shuffle(self, shuffle: bool) -> bool:
        """Enable or disable shuffle."""
        response = self._get("Shuffle", {"state": "1" if shuffle else "0"})
        return response is not None

    def repeat(self, repeat: int) -> bool:
        """Set repeat mode (0=off, 1=all, 2=one)."""
        response = self._get("Repeat", {"state": repeat})
        return response is not None

    def add_slave(self, slave_ip: str, group_name: str | None = None) -> bool:
        """Add a slave player to this master."""
        # BluOS AddSlave parameters
        # slave: IP address of the secondary player (required)
        # port: Port number of the secondary player (required)
        # group: OPTIONAL, name of the group. If not provided, BluOS will give a default group name
        params = {
            "slave": slave_ip,
            "port": str(self.port),
        }
        
        # Only add group parameter if provided
        if group_name:
            params["group"] = group_name
        
        _LOGGER.debug("Adding slave %s to master %s with params: %s", slave_ip, self.host, params)
        response = self._get("AddSlave", params)
        _LOGGER.debug("AddSlave response: %s", response)
        return response is not None

    def remove_slave(self, slave_ip: str | None = None) -> bool:
        """Remove a slave player or unjoin this player from group."""
        if slave_ip:
            # Remove specific slave
            params = {"slave": slave_ip}
            _LOGGER.debug("Removing slave %s from master %s", slave_ip, self.host)
        else:
            # Unjoin this player from its group
            params = {}
            _LOGGER.debug("Ungrouping player %s", self.host)
        
        response = self._get("RemoveSlave", params)
        _LOGGER.debug("RemoveSlave response: %s", response)
        return response is not None
