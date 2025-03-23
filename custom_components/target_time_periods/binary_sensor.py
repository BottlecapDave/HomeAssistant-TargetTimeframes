import logging

import voluptuous as vol

from homeassistant.helpers import config_validation as cv, entity_platform

from .const import (
  CONFIG_KIND,
  CONFIG_KIND_ROLLING_TARGET_RATE,
  CONFIG_KIND_TARGET_RATE
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if entry.data[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE or entry.data[CONFIG_KIND] == CONFIG_KIND_ROLLING_TARGET_RATE:
    await async_setup_target_sensors(hass, entry, async_add_entities)

    platform = entity_platform.async_get_current_platform()

    if entry.data[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
      platform.async_register_entity_service(
        "update_target_config",
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
        "update_rolling_target_config",
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

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  # now = utcnow()
  # is_export = False
  # for point in account_info["electricity_meter_points"]:
  #   tariff_code = get_active_tariff(now, point["agreements"])
  #   if tariff_code is not None:
  #     # For backwards compatibility, pick the first applicable meter
  #     if point["mpan"] == mpan or mpan is None:
  #       for meter in point["meters"]:
  #         is_export = meter["is_export"]
  #         serial_number = meter["serial_number"]
  #         coordinator = hass.data[DOMAIN][account_id][DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)]
  #         free_electricity_coordinator = hass.data[DOMAIN][account_id][DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR]
  #         entities = []

  #         if config[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
  #           entities.append(TargetTimePeriodsTargetRate(hass, account_id, entry, config, is_export, coordinator, free_electricity_coordinator))
  #         else:
  #           entities.append(TargetTimePeriodsRollingTargetRate(hass, account_id, entry, config, is_export, coordinator, free_electricity_coordinator))

  #         async_add_entities(entities)
  #         return
