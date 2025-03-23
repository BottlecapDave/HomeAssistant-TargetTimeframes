from typing import Any
from homeassistant.config_entries import (ConfigFlow, ConfigEntry, ConfigSubentryFlow, SubentryFlowResult)
from homeassistant.core import callback

from .config.target_time_period import validate_target_rate_config
from .config.rolling_target_time_period import validate_rolling_target_rate_config

from .const import (
  CONFIG_KIND,
  CONFIG_KIND_ROLLING_TARGET_RATE,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_DATA_SOURCE_NAME,
  CONFIG_TARGET_NAME,
  CONFIG_VERSION,
  DATA_SCHEMA_ROLLING_TARGET_TIME_PERIOD,
  DATA_SCHEMA_SOURCE,
  DATA_SCHEMA_TARGET_TIME_PERIOD,
  DOMAIN,
)

from .config.data_source import validate_source_config

class TargetTimePeriodsConfigFlow(ConfigFlow, domain=DOMAIN): 
  """Config flow."""

  VERSION = CONFIG_VERSION

  async def async_step_user(self, user_input):
    """Setup based on user config"""

    errors = {}
    if user_input is not None:
      errors = validate_source_config(user_input)

      # Setup our basic sensors
      if len(errors) < 1:
        return self.async_create_entry(
          title=f"{user_input[CONFIG_DATA_SOURCE_NAME]}", 
          data=user_input
        )

    return self.async_show_form(
      step_id="user",
      data_schema=DATA_SCHEMA_SOURCE,
      errors=errors
    )
  
  @classmethod
  @callback
  def async_get_supported_subentry_types(
      cls, config_entry: ConfigEntry
  ) -> dict[str, type[ConfigSubentryFlow]]:
      """Return subentries supported by this integration."""
      return {
        "target_time_period": TargetTimePeriodSubentryFlowHandler,
        "rolling_target_time_period": RollingTargetTimePeriodSubentryFlowHandler
      }
  
class TargetTimePeriodSubentryFlowHandler(ConfigSubentryFlow):

  async def async_step_user(
      self, user_input: dict[str, Any] | None = None
  ) -> SubentryFlowResult:
    config = dict(user_input) if user_input is not None else None
    errors = validate_target_rate_config(config) if config is not None else {}

    if len(errors) < 1 and user_input is not None:
      config[CONFIG_KIND] = CONFIG_KIND_TARGET_RATE
      # Setup our targets sensor
      return self.async_create_entry(
        title=f"{config[CONFIG_TARGET_NAME]} (target)", 
        data=config
      )

    return self.async_show_form(
      step_id="user",
      data_schema=self.add_suggested_values_to_schema(
        DATA_SCHEMA_TARGET_TIME_PERIOD,
        user_input if user_input is not None else {}
      ),
      errors=errors
    )

class RollingTargetTimePeriodSubentryFlowHandler(ConfigSubentryFlow):
  async def async_step_user(
      self, user_input: dict[str, Any] | None = None
  ) -> SubentryFlowResult:
    """Setup a target based on the provided user input"""
    config = dict(user_input) if user_input is not None else None
    errors = validate_rolling_target_rate_config(config) if config is not None else {}

    if len(errors) < 1 and user_input is not None:
      config[CONFIG_KIND] = CONFIG_KIND_ROLLING_TARGET_RATE
      # Setup our targets sensor
      return self.async_create_entry(
        title=f"{config[CONFIG_TARGET_NAME]} (rolling target)", 
        data=config
      )

    return self.async_show_form(
      step_id="user",
      data_schema=self.add_suggested_values_to_schema(
        DATA_SCHEMA_ROLLING_TARGET_TIME_PERIOD,
        user_input if user_input is not None else {}
      ),
      errors=errors
    )