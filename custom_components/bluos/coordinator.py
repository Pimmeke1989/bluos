"""Data update coordinator for BluOS."""
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .bluos_api import BluOSApi
from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class BluOSDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching BluOS data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.api = BluOSApi(
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
        )
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=f"BluOS {entry.data[CONF_HOST]}",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            status = await self.hass.async_add_executor_job(self.api.get_status)
            sync_status = await self.hass.async_add_executor_job(
                self.api.get_sync_status
            )
            presets = await self.hass.async_add_executor_job(self.api.get_presets)

            if status is None:
                raise UpdateFailed("Failed to fetch player status")

            return {
                "status": status,
                "sync_status": sync_status or {},
                "presets": presets,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
