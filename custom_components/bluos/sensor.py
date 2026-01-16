"""BluOS sensor platform."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BluOSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BluOS sensor entities."""
    coordinator: BluOSDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Check if device has battery
    battery_info = coordinator.data.get("status", {}).get("battery", {})
    
    entities = []
    
    if battery_info:
        # Device has battery, add battery sensors
        _LOGGER.info("Device %s has battery, adding battery sensors", entry.data.get("host"))
        entities.append(BluOSBatterySensor(coordinator, entry))
        entities.append(BluOSBatteryChargingSensor(coordinator, entry))
    
    if entities:
        async_add_entities(entities)


class BluOSBatterySensor(CoordinatorEntity, SensorEntity):
    """Battery level sensor for BluOS devices."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BluOSDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_battery"
        self._attr_name = "Battery"
        
        # Get device information from SyncStatus (same as media_player)
        sync_status = coordinator.data.get("sync_status", {}) if coordinator.data else {}
        
        device_name = sync_status.get("device_name", "")
        if not device_name and coordinator.data and "status" in coordinator.data:
            device_name = coordinator.data["status"].get("name", "BluOS Player")
        if not device_name:
            device_name = "BluOS Player"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
        }

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        if not self.coordinator.data:
            return None
        
        battery_info = self.coordinator.data.get("status", {}).get("battery", {})
        return battery_info.get("level")

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
        
        battery_info = self.coordinator.data.get("status", {}).get("battery", {})
        
        return {
            "charging": battery_info.get("charging", False),
            "icon_path": battery_info.get("icon", ""),
        }


class BluOSBatteryChargingSensor(CoordinatorEntity, SensorEntity):
    """Battery charging status sensor for BluOS devices."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BluOSDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the battery charging sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_battery_charging"
        self._attr_name = "Battery charging"
        
        # Get device information from SyncStatus (same as media_player)
        sync_status = coordinator.data.get("sync_status", {}) if coordinator.data else {}
        
        device_name = sync_status.get("device_name", "")
        if not device_name and coordinator.data and "status" in coordinator.data:
            device_name = coordinator.data["status"].get("name", "BluOS Player")
        if not device_name:
            device_name = "BluOS Player"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
        }

    @property
    def native_value(self) -> str | None:
        """Return the charging status."""
        if not self.coordinator.data:
            return None
        
        battery_info = self.coordinator.data.get("status", {}).get("battery", {})
        charging = battery_info.get("charging", False)
        
        return "Charging" if charging else "Not charging"

    @property
    def icon(self) -> str:
        """Return the icon."""
        if not self.coordinator.data:
            return "mdi:battery"
        
        battery_info = self.coordinator.data.get("status", {}).get("battery", {})
        charging = battery_info.get("charging", False)
        
        return "mdi:battery-charging" if charging else "mdi:battery"

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
        
        battery_info = self.coordinator.data.get("status", {}).get("battery", {})
        
        return {
            "battery_level": battery_info.get("level"),
            "charging": battery_info.get("charging", False),
        }
