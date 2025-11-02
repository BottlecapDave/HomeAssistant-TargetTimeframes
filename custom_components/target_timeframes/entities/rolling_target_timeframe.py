import logging
import math

import voluptuous as vol

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (utcnow, now)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.helpers import translation

from ..const import (
  CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD,
  CONFIG_TARGET_CALCULATE_WITH_INCOMPLETE_DATA,
  CONFIG_TARGET_DANGEROUS_SETTINGS,
  CONFIG_TARGET_DEFAULT_MINIMUM_REQUIRED_MINUTES_IN_SLOT,
  CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE,
  CONFIG_TARGET_HOURS_MODE,
  CONFIG_TARGET_MAX_VALUE,
  CONFIG_TARGET_MIN_VALUE,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_ROLLING_TARGET,
  CONFIG_TARGET_LATEST_VALUES,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_TYPE_CONTINUOUS,
  CONFIG_TARGET_TYPE_INTERMITTENT,
  CONFIG_TARGET_WEIGHTING,
  CONFIG_TARGET_FIND_HIGHEST_VALUES,
  DOMAIN,
  EVENT_DATA_SOURCE,
)

from . import (
  calculate_continuous_times,
  calculate_intermittent_times,
  compare_config_to_attributes,
  create_weighting,
  extract_config,
  get_rolling_applicable_time_periods,
  get_target_time_period_info,
  should_evaluate_target_timeframes
)

from ..utils.attributes import dict_to_typed_dict
from .repairs import check_for_errors
from ..config.rolling_target_timeframe import validate_rolling_target_timeframe_config

_LOGGER = logging.getLogger(__name__)

class TargetTimeframesRollingTargetRate(BinarySensorEntity, RestoreEntity):
  """Sensor for calculating when a target should be turned on or off."""
  
  def __init__(self, hass: HomeAssistant, data_source_id: str, config_entry, config_subentry, config, initial_data):
    """Init sensor."""

    self._state = None
    self._config_entry = config_entry
    self._config_subentry = config_subentry
    self._config = config
    self._attributes = self._config.copy()
    self._last_evaluated = None
    self._data_source_id = data_source_id
    self._attributes["data_source_id"] = self._data_source_id
    self.update_default_attributes()

    self._data_source_data = initial_data if initial_data is not None else []
    self._target_timeframes = []
    
    self._hass = hass
    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"target_timeframes_{self._data_source_id}_{self._config[CONFIG_TARGET_NAME]}"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"{self._config[CONFIG_TARGET_NAME]} ({self._data_source_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:camera-timer"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def is_on(self):
    return self._state
  
  async def async_update(self):
    """Determines if the target rate sensor is active."""
    if not self.enabled:
      return

    if CONFIG_TARGET_OFFSET in self._config:
      offset = self._config[CONFIG_TARGET_OFFSET]
    else:
      offset = None

    current_local_date = now()
    check_for_errors(self._hass, self._config)

    # Find the current rate. Rates change a maximum of once every 30 minutes.
    current_date = utcnow()

    should_evaluate = should_evaluate_target_timeframes(current_date, self._target_timeframes, self._config[CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE])
    if should_evaluate:
      _LOGGER.debug(f'{self._config[CONFIG_TARGET_NAME]} - {len(self._data_source_data) if self._data_source_data is not None else None} time periods found')

      if len(self._data_source_data) > 0:
        # True by default for backwards compatibility
        find_last_time_periods = False
        if CONFIG_TARGET_LATEST_VALUES in self._config:
          find_last_time_periods = self._config[CONFIG_TARGET_LATEST_VALUES]     

        target_hours = float(self._config[CONFIG_TARGET_HOURS])

        find_highest_values = False
        if (CONFIG_TARGET_FIND_HIGHEST_VALUES in self._config):
          find_highest_values = self._config[CONFIG_TARGET_FIND_HIGHEST_VALUES]

        min_value = None
        if CONFIG_TARGET_MIN_VALUE in self._config:
          min_value = self._config[CONFIG_TARGET_MIN_VALUE]

        max_value = None
        if CONFIG_TARGET_MAX_VALUE in self._config:
          max_value = self._config[CONFIG_TARGET_MAX_VALUE]

        calculate_with_incomplete_data = False
        if CONFIG_TARGET_DANGEROUS_SETTINGS in self._config and CONFIG_TARGET_CALCULATE_WITH_INCOMPLETE_DATA in self._config[CONFIG_TARGET_DANGEROUS_SETTINGS]:
          calculate_with_incomplete_data = self._config[CONFIG_TARGET_DANGEROUS_SETTINGS][CONFIG_TARGET_CALCULATE_WITH_INCOMPLETE_DATA]

        minimum_slot_minutes = CONFIG_TARGET_DEFAULT_MINIMUM_REQUIRED_MINUTES_IN_SLOT
        if CONFIG_TARGET_DANGEROUS_SETTINGS in self._config and CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT in self._config[CONFIG_TARGET_DANGEROUS_SETTINGS]:
          minimum_slot_minutes = self._config[CONFIG_TARGET_DANGEROUS_SETTINGS][CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT]

        applicable_time_periods = get_rolling_applicable_time_periods(
          current_local_date,
          self._data_source_data,
          self._config[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD],
          minimum_slot_minutes,
          calculate_with_incomplete_data,
          self._config[CONFIG_TARGET_NAME]
        )

        if applicable_time_periods is not None:
          number_of_slots = math.ceil(target_hours * 2)
          weighting = create_weighting(self._config[CONFIG_TARGET_WEIGHTING] if CONFIG_TARGET_WEIGHTING in self._config else None, number_of_slots)

          if (self._config[CONFIG_TARGET_TYPE] == CONFIG_TARGET_TYPE_CONTINUOUS):
            self._target_timeframes = calculate_continuous_times(
              applicable_time_periods,
              target_hours,
              find_highest_values,
              find_last_time_periods,
              min_value,
              max_value,
              weighting,
              self._config[CONFIG_TARGET_HOURS_MODE],
              self._config[CONFIG_TARGET_NAME]
            )
          elif (self._config[CONFIG_TARGET_TYPE] == CONFIG_TARGET_TYPE_INTERMITTENT):
            self._target_timeframes = calculate_intermittent_times(
              applicable_time_periods,
              target_hours,
              find_highest_values,
              find_last_time_periods,
              min_value,
              max_value,
              self._config[CONFIG_TARGET_HOURS_MODE],
              self._config[CONFIG_TARGET_NAME]
            )
          else:
            _LOGGER.error(f"{self._config[CONFIG_TARGET_NAME]} - Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

          self._attributes["target_times"] = self._target_timeframes
          self._attributes["target_times_last_evaluated"] = current_date
          _LOGGER.debug(f"{self._config[CONFIG_TARGET_NAME]} - calculated rates: {self._target_timeframes}")
        
        self._attributes["time_periods_incomplete"] = applicable_time_periods is None or len(applicable_time_periods) < (target_hours * 2)

    active_result = get_target_time_period_info(current_date, self._target_timeframes, offset)

    self._attributes["overall_average_value"] = active_result["overall_average_value"]
    self._attributes["overall_min_value"] = active_result["overall_min_value"]
    self._attributes["overall_max_value"] = active_result["overall_max_value"]

    self._attributes["current_duration_in_hours"] = active_result["current_duration_in_hours"]
    self._attributes["current_average_value"] = active_result["current_average_value"]
    self._attributes["current_min_value"] = active_result["current_min_value"]
    self._attributes["current_max_value"] = active_result["current_max_value"]

    self._attributes["next_time"] = active_result["next_time"]
    self._attributes["next_duration_in_hours"] = active_result["next_duration_in_hours"]
    self._attributes["next_average_value"] = active_result["next_average_value"]
    self._attributes["next_min_value"] = active_result["next_min_value"]
    self._attributes["next_max_value"] = active_result["next_max_value"]
    self._attributes["data_source_id"] = self._data_source_id
    
    self._state = active_result["is_active"]

    _LOGGER.debug(f"{self._config[CONFIG_TARGET_NAME]} - calculated: {self._state}")
    self._attributes = dict_to_typed_dict(self._attributes)

  @callback
  def _async_handle_event(self, event) -> None:
    if (event.data is not None and 
        "data_source_id" in event.data and 
        event.data["data_source_id"] == self._data_source_id):
      self._data_source_data = self._hass.data[DOMAIN][self._data_source_id]
  
  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'
      self._attributes = dict_to_typed_dict(
        state.attributes,
        [CONFIG_TARGET_ROLLING_TARGET] # This was incorrectly included
      )
      self.update_default_attributes()

      self._target_timeframes = self._attributes["target_times"] if "target_times" in self._attributes else []

      # Reset everything if our settings have changed
      if compare_config_to_attributes(self.expand_config_attributes(self._config), self._attributes) == False:
        _LOGGER.debug(f'Not restoring target times for {self._config[CONFIG_TARGET_NAME]} as attributes have changed')
        self._state = False
        self._attributes = self._config.copy()
        self.update_default_attributes()
        self._target_timeframes = None
    
      _LOGGER.debug(f'{self._config[CONFIG_TARGET_NAME]} - Restored state: {self._state}')

    self.async_on_remove(
      self._hass.bus.async_listen(EVENT_DATA_SOURCE, self._async_handle_event)
    )

  @callback
  async def async_update_rolling_target_timeframe_config(self, target_hours=None, target_look_ahead_hours=None, target_offset=None, target_minimum_value=None, target_maximum_value=None, target_weighting=None, persist_changes=False):
    """Update sensors config"""
    _LOGGER.debug(f"{self._config[CONFIG_TARGET_NAME]} - async_update_rolling_target_timeframe_config called: {self._config}")

    config = dict(self._config)
    if target_hours is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_TARGET_HOURS: target_hours if isinstance(target_hours, str) == False else (target_hours.strip('\"') if target_hours != "" else None)
      })

    if target_look_ahead_hours is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: target_look_ahead_hours if isinstance(target_look_ahead_hours, str) == False else (target_look_ahead_hours.strip('\"') if target_look_ahead_hours != "" else None)
      })

    if target_offset is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_TARGET_OFFSET: target_offset if isinstance(target_offset, str) == False else (target_offset.strip('\"') if target_offset != "" else None)
      })

    if target_minimum_value is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_TARGET_MIN_VALUE: target_minimum_value if isinstance(target_minimum_value, str) == False else (target_minimum_value.strip('\"') if target_minimum_value != "" else None)
      })

    if target_maximum_value is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_TARGET_MAX_VALUE: target_maximum_value if isinstance(target_maximum_value, str) == False else (target_maximum_value.strip('\"') if target_maximum_value != "" else None)
      })

    if target_weighting is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_TARGET_WEIGHTING: target_weighting if isinstance(target_weighting, str) == False else (target_weighting.strip('\"') if target_weighting != "" else None)
      })

    errors = validate_rolling_target_timeframe_config(config)
    keys = list(errors.keys())
    if (len(keys)) > 0:
      translations = await translation.async_get_translations(self._hass, self._hass.config.language, "config_subentries", {DOMAIN})
      raise vol.Invalid(translations[f'component.{DOMAIN}.config_subentries.rolling_target_time_period.error.{errors[keys[0]]}'])

    self._config = config
    self._attributes = self._config.copy()
    self.update_default_attributes()
    self._target_timeframes = []
    await self.async_update()
    self.async_write_ha_state()

    if persist_changes:
      updatable_keys = [CONFIG_TARGET_HOURS, CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD, CONFIG_TARGET_OFFSET, CONFIG_TARGET_MIN_VALUE, CONFIG_TARGET_MAX_VALUE, CONFIG_TARGET_WEIGHTING]
      new_config_data = { **self._config_subentry.data }
      new_config_data.update(extract_config(config, updatable_keys))

      self._hass.config_entries.async_update_subentry(
        self._config_entry,
        self._config_subentry,
        data = new_config_data
      )

  def expand_config_attributes(self, attributes: dict):
    new_attributes = attributes.copy()

    find_last_rates = False
    if CONFIG_TARGET_LATEST_VALUES in new_attributes:
      find_last_rates = new_attributes[CONFIG_TARGET_LATEST_VALUES]
    new_attributes[CONFIG_TARGET_LATEST_VALUES] = find_last_rates

    if CONFIG_TARGET_CALCULATE_WITH_INCOMPLETE_DATA not in new_attributes:
      calculate_with_incomplete_data = False
      if CONFIG_TARGET_DANGEROUS_SETTINGS in new_attributes and CONFIG_TARGET_CALCULATE_WITH_INCOMPLETE_DATA in new_attributes[CONFIG_TARGET_DANGEROUS_SETTINGS]:
        calculate_with_incomplete_data = new_attributes[CONFIG_TARGET_DANGEROUS_SETTINGS][CONFIG_TARGET_CALCULATE_WITH_INCOMPLETE_DATA]
      new_attributes[CONFIG_TARGET_CALCULATE_WITH_INCOMPLETE_DATA] = calculate_with_incomplete_data

    if CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT not in new_attributes:
      minimum_required_minutes_in_slot = CONFIG_TARGET_DEFAULT_MINIMUM_REQUIRED_MINUTES_IN_SLOT
      if CONFIG_TARGET_DANGEROUS_SETTINGS in new_attributes and CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT in new_attributes[CONFIG_TARGET_DANGEROUS_SETTINGS]:
        minimum_required_minutes_in_slot = new_attributes[CONFIG_TARGET_DANGEROUS_SETTINGS][CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT]
      new_attributes[CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT] = minimum_required_minutes_in_slot

    if CONFIG_TARGET_DANGEROUS_SETTINGS in new_attributes:
      del new_attributes[CONFIG_TARGET_DANGEROUS_SETTINGS]

    return new_attributes

  def update_default_attributes(self):
    """Update the default attributes."""
    self._attributes["data_source_id"] = self._data_source_id
    self._attributes = self.expand_config_attributes(self._attributes)