import logging

import voluptuous as vol

from homeassistant.helpers import config_validation as cv, entity_platform

from .const import (
  CONFIG_DATA_SOURCE_ID,
  CONFIG_KIND,
  CONFIG_KIND_ROLLING_TARGET_RATE,
  CONFIG_KIND_TARGET_RATE
)
from .entities.rolling_target_timeframe import TargetTimeframesRollingTargetRate
from .entities.target_timeframe import TargetTimeframesTargetRate
from .storage.data_source_data import async_load_cached_data_source_data

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  parent_config = dict(entry.data)

  if entry.options:
    parent_config.update(entry.options)

  data_source_id = parent_config[CONFIG_DATA_SOURCE_ID]

  data = await async_load_cached_data_source_data(hass, data_source_id)
  data_dict = None
  if data is not None:
    data_dict = list(map(lambda x: x.dict(), data))

  if entry.subentries:
    for sub_entry in entry.subentries.values():
      config = dict(sub_entry.data)

      if config[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE or config[CONFIG_KIND] == CONFIG_KIND_ROLLING_TARGET_RATE:
        await async_setup_target_sensors(hass, entry, config, data_source_id, async_add_entities, data_dict)

        platform = entity_platform.async_get_current_platform()

        if config[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
          platform.async_register_entity_service(
            "update_target_timeframe_config",
            vol.All(
              cv.make_entity_service_schema(
                {
                  vol.Optional("target_hours"): str,
                  vol.Optional("target_start_time"): str,
                  vol.Optional("target_end_time"): str,
                  vol.Optional("target_offset"): str,
                  vol.Optional("target_minimum_value"): str,
                  vol.Optional("target_maximum_value"): str,
                  vol.Optional("target_weighting"): str,
                  vol.Optional("persist_changes"): bool,
                },
                extra=vol.ALLOW_EXTRA,
              ),
              cv.has_at_least_one_key(
                "target_hours", "target_start_time", "target_end_time", "target_offset", "target_minimum_value", "target_maximum_value"
              ),
            ),
            "async_update_target_rate_config",
          )
        else:
          platform.async_register_entity_service(
            "update_rolling_target_timeframe_config",
            vol.All(
              cv.make_entity_service_schema(
                {
                  vol.Optional("target_hours"): str,
                  vol.Optional("target_look_ahead_hours"): str,
                  vol.Optional("target_offset"): str,
                  vol.Optional("target_minimum_value"): str,
                  vol.Optional("target_maximum_value"): str,
                  vol.Optional("target_weighting"): str,
                  vol.Optional("persist_changes"): bool,
                },
                extra=vol.ALLOW_EXTRA,
              ),
              cv.has_at_least_one_key(
                "target_hours", "target_look_ahead_hours", "target_offset", "target_minimum_value", "target_maximum_value"
              ),
            ),
            "async_update_rolling_target_rate_config",
          )

  return True

async def async_setup_target_sensors(hass, entry, config, data_source_id, async_add_entities, initial_data):
  entities = []

  if config[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
    entities.append(TargetTimeframesTargetRate(hass, data_source_id, entry, config, initial_data))
  else:
    entities.append(TargetTimeframesRollingTargetRate(hass, data_source_id, entry, config, initial_data))

  async_add_entities(entities)
  return
