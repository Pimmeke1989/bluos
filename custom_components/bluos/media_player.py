"""BluOS Media Player platform."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_BLUEOS_GROUP,
    ATTR_MASTER,
    ATTR_SLAVES,
    DOMAIN,
    SERVICE_JOIN,
    SERVICE_UNJOIN,
)
from .coordinator import BluOSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SUPPORT_BLUOS = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.SHUFFLE_SET
    | MediaPlayerEntityFeature.REPEAT_SET
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BluOS media player based on a config entry."""
    coordinator: BluOSDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([BluOSMediaPlayer(coordinator, entry)], True)

    # Register services
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_JOIN,
        {
            vol.Required("master"): cv.entity_id,
            vol.Optional("group_name"): cv.string,
        },
        "async_join_player",
    )

    platform.async_register_entity_service(
        SERVICE_UNJOIN,
        {},
        "async_unjoin_player",
    )


class BluOSMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Representation of a BluOS media player."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: BluOSDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the media player."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_media_player"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": coordinator.data["status"].get("name", "BluOS Player"),
            "manufacturer": "BluOS",
            "model": "BluOS Player",
        }
        self._attr_supported_features = SUPPORT_BLUOS

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        if not self.coordinator.data:
            return MediaPlayerState.OFF
        
        state = self.coordinator.data["status"].get("state", "idle")
        
        state_map = {
            "playing": MediaPlayerState.PLAYING,
            "paused": MediaPlayerState.PAUSED,
            "idle": MediaPlayerState.IDLE,
        }
        
        return state_map.get(state, MediaPlayerState.IDLE)

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        if not self.coordinator.data:
            return None
        
        volume = self.coordinator.data["status"].get("volume", 0)
        return volume / 100

    @property
    def is_volume_muted(self) -> bool | None:
        """Boolean if volume is currently muted."""
        if not self.coordinator.data:
            return None
        
        return self.coordinator.data["status"].get("mute", False)

    @property
    def media_content_type(self) -> str | None:
        """Content type of current playing media."""
        return MediaType.MUSIC

    @property
    def media_title(self) -> str | None:
        """Title of current playing media."""
        if not self.coordinator.data:
            return None
        
        return self.coordinator.data["status"].get("title1", "")

    @property
    def media_artist(self) -> str | None:
        """Artist of current playing media."""
        if not self.coordinator.data:
            return None
        
        return self.coordinator.data["status"].get("artist", "")

    @property
    def media_album_name(self) -> str | None:
        """Album name of current playing media."""
        if not self.coordinator.data:
            return None
        
        return self.coordinator.data["status"].get("album", "")

    @property
    def media_image_url(self) -> str | None:
        """Image url of current playing media."""
        if not self.coordinator.data:
            return None
        
        image = self.coordinator.data["status"].get("image", "")
        if image:
            return f"http://{self._entry.data[CONF_HOST]}:{self._entry.data.get('port', 11000)}{image}"
        return None

    @property
    def media_duration(self) -> int | None:
        """Duration of current playing media in seconds."""
        if not self.coordinator.data:
            return None
        
        return self.coordinator.data["status"].get("totlen", 0)

    @property
    def media_position(self) -> int | None:
        """Position of current playing media in seconds."""
        if not self.coordinator.data:
            return None
        
        return self.coordinator.data["status"].get("secs", 0)

    @property
    def source(self) -> str | None:
        """Name of the current input source."""
        if not self.coordinator.data:
            return None
        
        return self.coordinator.data["status"].get("service", "")

    @property
    def source_list(self) -> list[str] | None:
        """List of available input sources."""
        if not self.coordinator.data:
            return None
        
        presets = self.coordinator.data.get("presets", [])
        return [preset["name"] for preset in presets]

    @property
    def shuffle(self) -> bool | None:
        """Boolean if shuffle is enabled."""
        if not self.coordinator.data:
            return None
        
        return self.coordinator.data["status"].get("shuffle", False)

    @property
    def repeat(self) -> str | None:
        """Return current repeat mode."""
        if not self.coordinator.data:
            return None
        
        repeat_mode = self.coordinator.data["status"].get("repeat", "0")
        
        repeat_map = {
            "0": "off",
            "1": "all",
            "2": "one",
        }
        
        return repeat_map.get(str(repeat_mode), "off")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return {}
        
        sync_status = self.coordinator.data.get("sync_status", {})
        
        # Build group information
        group_info = {
            "master": sync_status.get("master"),
            "slaves": [slave["ip"] for slave in sync_status.get("slaves", [])],
        }
        
        # Create list of all players in group
        group_members = []
        if sync_status.get("master"):
            # This player is a slave
            group_members.append(sync_status["master"])
            group_members.append(self._entry.data[CONF_HOST])
        elif sync_status.get("slaves"):
            # This player is a master
            group_members.append(self._entry.data[CONF_HOST])
            group_members.extend([slave["ip"] for slave in sync_status["slaves"]])
        
        return {
            ATTR_BLUEOS_GROUP: group_members,
            ATTR_MASTER: group_info["master"],
            ATTR_SLAVES: group_info["slaves"],
        }

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self.async_media_play()

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        await self.async_media_stop()

    async def async_media_play(self) -> None:
        """Send play command."""
        await self.hass.async_add_executor_job(self.coordinator.api.play)
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self.hass.async_add_executor_job(self.coordinator.api.pause)
        await self.coordinator.async_request_refresh()

    async def async_media_stop(self) -> None:
        """Send stop command."""
        await self.hass.async_add_executor_job(self.coordinator.api.stop)
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.hass.async_add_executor_job(self.coordinator.api.next_track)
        await self.coordinator.async_request_refresh()

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self.hass.async_add_executor_job(self.coordinator.api.previous_track)
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_volume, int(volume * 100)
        )
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        await self.hass.async_add_executor_job(self.coordinator.api.mute, mute)
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        presets = self.coordinator.data.get("presets", [])
        for preset in presets:
            if preset["name"] == source:
                await self.hass.async_add_executor_job(
                    self.coordinator.api.select_preset, preset["id"]
                )
                await self.coordinator.async_request_refresh()
                return

    async def async_set_shuffle(self, shuffle: bool) -> None:
        """Enable/disable shuffle mode."""
        await self.hass.async_add_executor_job(self.coordinator.api.shuffle, shuffle)
        await self.coordinator.async_request_refresh()

    async def async_set_repeat(self, repeat: str) -> None:
        """Set repeat mode."""
        repeat_map = {
            "off": 0,
            "all": 1,
            "one": 2,
        }
        
        repeat_mode = repeat_map.get(repeat, 0)
        await self.hass.async_add_executor_job(self.coordinator.api.repeat, repeat_mode)
        await self.coordinator.async_request_refresh()

    async def async_join_player(self, master: str, group_name: str | None = None) -> None:
        """Join this player to a master player."""
        _LOGGER.info("Attempting to join %s to master %s (group_name: %s)", self.entity_id, master, group_name)
        
        # Get the master player's entity state
        master_entity = self.hass.states.get(master)
        if not master_entity:
            _LOGGER.error("Master player entity %s not found in Home Assistant", master)
            return
        
        _LOGGER.debug("Master entity found: %s", master_entity)
        
        # Find the master player's coordinator by matching entry_id from entity_id
        # Entity ID format: media_player.{device_name}_{entry_id}
        master_coordinator = None
        master_ip = None
        
        # Try to find coordinator by checking all BluOS integrations
        for entry_id, coordinator in self.hass.data[DOMAIN].items():
            # Check if this coordinator's entity matches the master entity_id
            # We can match by checking if the entry_id is in the master entity_id
            if entry_id in master:
                master_coordinator = coordinator
                master_ip = coordinator.entry.data[CONF_HOST]
                _LOGGER.debug("Found master coordinator by entry_id: %s (IP: %s)", entry_id, master_ip)
                break
        
        # If not found by entry_id, try matching by IP from attributes
        if not master_coordinator:
            for entry_id, coordinator in self.hass.data[DOMAIN].items():
                coordinator_ip = coordinator.entry.data[CONF_HOST]
                # Check if IPs match (from blueos_group attribute or other means)
                if master_entity.attributes.get(ATTR_BLUEOS_GROUP):
                    if coordinator_ip in master_entity.attributes.get(ATTR_BLUEOS_GROUP, []):
                        master_coordinator = coordinator
                        master_ip = coordinator_ip
                        _LOGGER.debug("Found master coordinator by IP match: %s", master_ip)
                        break
        
        if not master_coordinator or not master_ip:
            _LOGGER.error("Could not find coordinator for master player %s. Available coordinators: %s", 
                         master, list(self.hass.data[DOMAIN].keys()))
            return
        
        slave_ip = self._entry.data[CONF_HOST]
        _LOGGER.info("Calling AddSlave on master %s to add slave %s", master_ip, slave_ip)
        
        # Call AddSlave on the master
        try:
            result = await self.hass.async_add_executor_job(
                master_coordinator.api.add_slave, slave_ip, group_name
            )
            _LOGGER.debug("AddSlave result: %s", result)
            
            if not result:
                _LOGGER.error("AddSlave command failed")
                return
            
            # Refresh both players
            await master_coordinator.async_request_refresh()
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Successfully joined %s to %s", slave_ip, master_ip)
        except Exception as err:
            _LOGGER.error("Error joining player: %s", err, exc_info=True)

    async def async_unjoin_player(self) -> None:
        """Unjoin this player from its group."""
        _LOGGER.info("Attempting to unjoin player %s", self.entity_id)
        
        sync_status = self.coordinator.data.get("sync_status", {})
        _LOGGER.debug("Current sync status: %s", sync_status)
        
        try:
            if sync_status.get("master"):
                # This player is a slave, remove it from the master
                master_ip = sync_status["master"]
                _LOGGER.info("Player is a slave. Removing from master %s", master_ip)
                
                # Find the master's coordinator
                master_coordinator = None
                for entry_id, coordinator in self.hass.data[DOMAIN].items():
                    if coordinator.entry.data[CONF_HOST] == master_ip:
                        master_coordinator = coordinator
                        _LOGGER.debug("Found master coordinator for IP %s", master_ip)
                        break
                
                if master_coordinator:
                    slave_ip = self._entry.data[CONF_HOST]
                    result = await self.hass.async_add_executor_job(
                        master_coordinator.api.remove_slave, slave_ip
                    )
                    _LOGGER.debug("RemoveSlave result: %s", result)
                    await master_coordinator.async_request_refresh()
                else:
                    _LOGGER.warning("Could not find master coordinator for IP %s, trying direct unjoin", master_ip)
                    # Try to unjoin directly from this player
                    result = await self.hass.async_add_executor_job(
                        self.coordinator.api.remove_slave
                    )
                    _LOGGER.debug("Direct unjoin result: %s", result)
            else:
                # This player is a master or standalone, remove all slaves
                _LOGGER.info("Player is master or standalone. Ungrouping all slaves")
                result = await self.hass.async_add_executor_job(
                    self.coordinator.api.remove_slave
                )
                _LOGGER.debug("Ungroup all result: %s", result)
            
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Successfully unjoined player %s", self.entity_id)
        except Exception as err:
            _LOGGER.error("Error unjoining player: %s", err, exc_info=True)
