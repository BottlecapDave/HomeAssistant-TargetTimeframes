import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util.dt import (utcnow)

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
)
from homeassistant.helpers.entity import generate_entity_id

from ..utils.attributes import dict_to_typed_dict
from ..const import DOMAIN, EVENT_DATA_SOURCE
from ..storage.data_source_data import async_save_cached_data_source_data
from ..utils.data_source_data import validate_data_source_data

_LOGGER = logging.getLogger(__name__)

class TargetTimePeriodDataSource(RestoreSensor):
  """Sensor for displaying a target time period data source"""

  _unrecorded_attributes = frozenset({ "data" })

  def __init__(self, hass: HomeAssistant, source_id: str):
    """Init sensor."""
    self._hass = hass
    self._state = None
    self._source_id = source_id
    self._attributes = {
      "data_source_id": source_id
    }

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"target_timeframes_{self._source_id}_data_source_last_updated"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Data source last updated ({self._source_id})"
  
  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:clock"
  
  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.TIMESTAMP

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored state: {self._state}')

  @callback
  async def async_update_target_time_period_data_source(self, data):
    """Update target time period data source"""
    result = validate_data_source_data(data, self._source_id)
    if result.success == False:
      raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="invalid_data_source_data",
        translation_placeholders={ 
          "error": result.error_message,
        },
      )
    
    await async_save_cached_data_source_data(self._hass, self._source_id, result.data)
    
    data_dict = list(map(lambda x: x.dict(), result.data))
    self._attributes["data"] = data_dict
    self._state = utcnow()
    self.async_write_ha_state()

    self._hass.data.setdefault(DOMAIN, {})
    self._hass.data[DOMAIN].setdefault(self._source_id, {})
    self._hass.data[DOMAIN][self._source_id] = data_dict

    self._hass.bus.async_fire(EVENT_DATA_SOURCE, {
      "data_source_id": self._source_id
    })