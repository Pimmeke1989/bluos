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

    async def async_join_player(self, master: str) -> None:
        """Join this player to a master player."""
        # Get the master player's IP address from entity_id
        master_entity = self.hass.states.get(master)
        if not master_entity:
            _LOGGER.error("Master player %s not found", master)
            return
        
        # Find the master player's coordinator to get its IP
        for entry_id, coordinator in self.hass.data[DOMAIN].items():
            if coordinator.data["status"]["name"] == master_entity.attributes.get("friendly_name"):
                master_ip = coordinator.entry.data[CONF_HOST]
                
                # Call AddSlave on the master
                await self.hass.async_add_executor_job(
                    coordinator.api.add_slave, self._entry.data[CONF_HOST]
                )
                
                # Refresh both players
                await coordinator.async_request_refresh()
                await self.coordinator.async_request_refresh()
                return
        
        _LOGGER.error("Could not find master player coordinator for %s", master)

    async def async_unjoin_player(self) -> None:
        """Unjoin this player from its group."""
        sync_status = self.coordinator.data.get("sync_status", {})
        
        if sync_status.get("master"):
            # This player is a slave, remove it from the master
            # Find the master's coordinator
            for entry_id, coordinator in self.hass.data[DOMAIN].items():
                if coordinator.entry.data[CONF_HOST] == sync_status["master"]:
                    await self.hass.async_add_executor_job(
                        coordinator.api.remove_slave, self._entry.data[CONF_HOST]
                    )
                    await coordinator.async_request_refresh()
                    break
        else:
            # This player is a master or standalone, remove all slaves
            await self.hass.async_add_executor_job(self.coordinator.api.remove_slave)
        
        await self.coordinator.async_request_refresh()
