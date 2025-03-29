import logging
from datetime import timedelta

from .const import (
  CONFIG_VERSION,
  DOMAIN
)

PLATFORMS = ["binary_sensor", "sensor"]

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_remove_config_entry_device(
  hass, config_entry, device_entry
) -> bool:
  """Remove a config entry from a device."""
  return True

async def async_migrate_entry(hass, config_entry):
  """Migrate old entry."""
  if (config_entry.version < CONFIG_VERSION):
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    new_data = None
    new_options = None
    title = config_entry.title
    
    hass.config_entries.async_update_entry(config_entry, title=title, data=new_data, options=new_options, version=CONFIG_VERSION)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

  return True

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

  return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok