import logging
import voluptuous as vol

from homeassistant.helpers import config_validation as cv, entity_platform

from .entities.data_source import TargetTimePeriodDataSource
from .const import (
  CONFIG_DATA_SOURCE_ID
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  platform = entity_platform.async_get_current_platform()
  platform.async_register_entity_service(
    "update_target_time_period_data_source",
    vol.All(
      cv.make_entity_service_schema(
        {
          vol.Required("data"): vol.All(
            cv.ensure_list,
            [
              {
                vol.Required("start"): str,
                vol.Required("end"): str,
                vol.Required("value"): float,
                vol.Optional("metadata"): vol.Schema({}).extend({}, extra=vol.ALLOW_EXTRA)
              }
            ],
          ),
        },
        extra=vol.ALLOW_EXTRA,
      ),
    ),
    "async_update_target_time_period_data_source",
  )

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  entities = [TargetTimePeriodDataSource(hass, config[CONFIG_DATA_SOURCE_ID])]

  if len(entities) > 0:
    async_add_entities(entities)

  return True
