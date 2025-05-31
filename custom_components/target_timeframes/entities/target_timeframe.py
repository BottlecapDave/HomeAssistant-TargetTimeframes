import logging
from datetime import timedelta
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
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST,
  CONFIG_TARGET_HOURS_MODE,
  CONFIG_TARGET_MAX_VALUE,
  CONFIG_TARGET_MIN_VALUE,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_ROLLING_TARGET,
  CONFIG_TARGET_LATEST_VALUES,
  CONFIG_TARGET_FIND_HIGHEST_VALUES,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_TYPE_CONTINUOUS,
  CONFIG_TARGET_TYPE_INTERMITTENT,
  CONFIG_TARGET_WEIGHTING,
  DOMAIN,
  EVENT_DATA_SOURCE,
)

from . import (
  calculate_continuous_times,
  calculate_intermittent_times,
  compare_config,
  create_weighting,
  extract_config,
  get_fixed_applicable_time_periods,
  get_start_and_end_times,
  get_target_time_period_info,
  is_target_timeframe_complete_in_period,
  should_evaluate_target_timeframes
)

from ..config.target_timeframe import validate_target_timeframe_config
from .repairs import check_for_errors
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class TargetTimeframesTargetRate(BinarySensorEntity, RestoreEntity):
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
    
    is_rolling_target = True
    if CONFIG_TARGET_ROLLING_TARGET in self._config:
      is_rolling_target = self._config[CONFIG_TARGET_ROLLING_TARGET]
    self._attributes[CONFIG_TARGET_ROLLING_TARGET] = is_rolling_target

    find_last_rates = False
    if CONFIG_TARGET_LATEST_VALUES in self._config:
      find_last_rates = self._config[CONFIG_TARGET_LATEST_VALUES]
    self._attributes[CONFIG_TARGET_LATEST_VALUES] = find_last_rates

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

    evaluation_mode = self._config[CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE] if CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE in self._config else CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST
    should_evaluate = should_evaluate_target_timeframes(current_date, self._target_timeframes, evaluation_mode)
    if should_evaluate:
      _LOGGER.debug(f'{len(self._data_source_data) if self._data_source_data is not None else None} time periods found')

      if len(self._data_source_data) > 0:
        start_time = None
        if CONFIG_TARGET_START_TIME in self._config:
          start_time = self._config[CONFIG_TARGET_START_TIME]

        end_time = None
        if CONFIG_TARGET_END_TIME in self._config:
          end_time = self._config[CONFIG_TARGET_END_TIME]

        # True by default for backwards compatibility
        is_rolling_target = True
        if CONFIG_TARGET_ROLLING_TARGET in self._config:
          is_rolling_target = self._config[CONFIG_TARGET_ROLLING_TARGET]

        find_last_rates = False
        if CONFIG_TARGET_LATEST_VALUES in self._config:
          find_last_rates = self._config[CONFIG_TARGET_LATEST_VALUES]     

        target_hours = float(self._config[CONFIG_TARGET_HOURS])

        find_highest_values = False
        if (CONFIG_TARGET_FIND_HIGHEST_VALUES in self._config):
          find_highest_values = self._config[CONFIG_TARGET_FIND_HIGHEST_VALUES]

        min_rate = None
        if CONFIG_TARGET_MIN_VALUE in self._config:
          min_rate = self._config[CONFIG_TARGET_MIN_VALUE]

        max_rate = None
        if CONFIG_TARGET_MAX_VALUE in self._config:
          max_rate = self._config[CONFIG_TARGET_MAX_VALUE]

        target_start, target_end = get_start_and_end_times(current_local_date, start_time, end_time, True)
        applicable_time_periods = get_fixed_applicable_time_periods(
          target_start,
          target_end,
          self._data_source_data
        )

        # Make sure we haven't already completed for the current target timeframe
        applicable_target_start, applicable_target_end = get_start_and_end_times(current_local_date, start_time, end_time, False)
        is_target_timeframe_complete = is_rolling_target == False and is_target_timeframe_complete_in_period(current_local_date, applicable_target_start, applicable_target_end, self._target_timeframes)

        if applicable_time_periods is not None and is_target_timeframe_complete == False:
          number_of_slots = math.ceil(target_hours * 2)
          weighting = create_weighting(self._config[CONFIG_TARGET_WEIGHTING] if CONFIG_TARGET_WEIGHTING in self._config else None, number_of_slots)

          proposed_target_timeframes = None
          if (self._config[CONFIG_TARGET_TYPE] == CONFIG_TARGET_TYPE_CONTINUOUS):
            proposed_target_timeframes = calculate_continuous_times(
              applicable_time_periods,
              target_hours,
              find_highest_values,
              find_last_rates,
              min_rate,
              max_rate,
              weighting,
              hours_mode = self._config[CONFIG_TARGET_HOURS_MODE]
            )
          elif (self._config[CONFIG_TARGET_TYPE] == CONFIG_TARGET_TYPE_INTERMITTENT):
            proposed_target_timeframes = calculate_intermittent_times(
              applicable_time_periods,
              target_hours,
              find_highest_values,
              find_last_rates,
              min_rate,
              max_rate,
              hours_mode = self._config[CONFIG_TARGET_HOURS_MODE]
            )
          else:
            _LOGGER.error(f"Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

          self._target_timeframes = proposed_target_timeframes
          self._attributes["target_times"] = self._target_timeframes
          self._attributes["target_times_last_evaluated"] = current_date
          _LOGGER.debug(f"calculated rates: {self._target_timeframes}")
        
        self._attributes["time_periods_incomplete"] = applicable_time_periods is None

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
    
    self._state = active_result["is_active"]

    _LOGGER.debug(f"calculated: {self._state}")
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
        []
      )

      self._target_timeframes = self._attributes["target_times"] if "target_times" in self._attributes else []

      # Reset everything if our settings have changed
      if compare_config(self._config, self._attributes) == False:
        self._state = False
        self._attributes = self._config.copy()
        self._target_timeframes = None
    
      _LOGGER.debug(f'Restored TargetTimeframesTargetRate state: {self._state}')

    self.async_on_remove(
      self._hass.bus.async_listen(EVENT_DATA_SOURCE, self._async_handle_event)
    )

  @callback
  async def async_update_target_timeframe_config(self, target_start_time=None, target_end_time=None, target_hours=None, target_offset=None, target_minimum_value=None, target_maximum_value=None, target_weighting=None, persist_changes=False):
    """Update sensors config"""

    config = dict(self._config)
    if target_hours is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_TARGET_HOURS: target_hours if isinstance(target_hours, str) == False else (target_hours.strip('\"') if target_hours != "" else None)
      })

    if target_start_time is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_TARGET_START_TIME: target_start_time if isinstance(target_start_time, str) == False else (target_start_time.strip('\"') if target_start_time != "" else None)
      })

    if target_end_time is not None:
      # Inputs from automations can include quotes, so remove these
      config.update({
        CONFIG_TARGET_END_TIME: target_end_time if isinstance(target_end_time, str) == False else (target_end_time.strip('\"') if target_end_time != "" else None)
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

    errors = validate_target_timeframe_config(config)
    keys = list(errors.keys())
    if (len(keys)) > 0:
      translations = await translation.async_get_translations(self._hass, self._hass.config.language, "config_subentries", {DOMAIN})
      raise vol.Invalid(translations[f'component.{DOMAIN}.config_subentries.target_time_period.error.{errors[keys[0]]}'])

    self._config = config
    self._attributes = self._config.copy()
    self._target_timeframes = []
    self.async_write_ha_state()

    if persist_changes:
      updatable_keys = [CONFIG_TARGET_HOURS, CONFIG_TARGET_START_TIME, CONFIG_TARGET_END_TIME, CONFIG_TARGET_OFFSET, CONFIG_TARGET_MIN_VALUE, CONFIG_TARGET_MAX_VALUE, CONFIG_TARGET_WEIGHTING]
      new_config_data = { **self._config_subentry.data }
      new_config_data.update(extract_config(config, updatable_keys))

      self._hass.config_entries.async_update_subentry(
        self._config_entry,
        self._config_subentry,
        data = new_config_data
      )