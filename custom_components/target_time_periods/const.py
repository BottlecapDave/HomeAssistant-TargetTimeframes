import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector

DOMAIN = "target_time_periods"
INTEGRATION_VERSION = "1.0.0"

CONFIG_VERSION = 1

CONFIG_DATA_SOURCE_NAME = "source_name"
CONFIG_DATA_SOURCE_ID = "source_id"

CONFIG_KIND = "kind"
CONFIG_KIND_TARGET_RATE = "target_rate"
CONFIG_KIND_ROLLING_TARGET_RATE = "rolling_target_rate"

CONFIG_TARGET_NAME = "name"
CONFIG_TARGET_HOURS = "hours"
CONFIG_TARGET_HOURS_MODE = "hours_mode"
CONFIG_TARGET_HOURS_MODE_EXACT = "exact_hours"
CONFIG_TARGET_HOURS_MODE_MINIMUM = "minimum_hours"
CONFIG_TARGET_HOURS_MODE_MAXIMUM = "maximum_hours"
CONFIG_TARGET_TYPE = "type"
CONFIG_TARGET_TYPE_CONTINUOUS = "Continuous"
CONFIG_TARGET_TYPE_INTERMITTENT = "Intermittent"
CONFIG_TARGET_START_TIME = "start_time"
CONFIG_TARGET_END_TIME = "end_time"
CONFIG_TARGET_OFFSET = "offset"
CONFIG_TARGET_ROLLING_TARGET = "rolling_target"
CONFIG_TARGET_LATEST_VALUES = "latest_values"
CONFIG_TARGET_INVERT_TARGET_VALUES = "target_invert_target_values"
CONFIG_TARGET_MIN_VALUE = "minimum_value"
CONFIG_TARGET_MAX_VALUE = "maximum_value"
CONFIG_TARGET_WEIGHTING = "weighting"
CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING = "free_electricity_weighting"
CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE = "target_times_evaluation_mode"
CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST = "all_target_times_in_past"
CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST = "all_target_times_in_future_or_past"
CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS = "always"

CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD = "look_ahead_hours"

CONFIG_TARGET_KEYS = [
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_ROLLING_TARGET,
  CONFIG_TARGET_LATEST_VALUES,
  CONFIG_TARGET_INVERT_TARGET_VALUES,
  CONFIG_TARGET_MIN_VALUE,
  CONFIG_TARGET_MAX_VALUE,
  CONFIG_TARGET_WEIGHTING,
  CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING,
  CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE
]

REGEX_HOURS = "^[0-9]+(\\.[0-9]+)*$"
REGEX_TIME = "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
REGEX_ENTITY_NAME = "^[a-z0-9_]+$"
REGEX_OFFSET_PARTS = "^(-)?([0-1]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$"
REGEX_DATE = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
REGEX_VALUE = "^(-)?[0-9]+(\\.[0-9]+)*$"

REGEX_WEIGHTING_NUMBERS = "([0-9]+\\.?[0-9]*(,[0-9]+\\.?[0-9]*+)*)"
REGEX_WEIGHTING_START = "(\\*(,[0-9]+\\.?[0-9]*+)+)"
REGEX_WEIGHTING_MIDDLE = "([0-9]+\\.?[0-9]*(,[0-9]+\\.?[0-9]*+)*(,\\*)(,[0-9]+\\.?[0-9]*+)+)"
REGEX_WEIGHTING_END = "([0-9]+\\.?[0-9]*(,[0-9]+\\.?[0-9]*+)*(,\\*))"
REGEX_WEIGHTING = f"^({REGEX_WEIGHTING_NUMBERS}|{REGEX_WEIGHTING_START}|{REGEX_WEIGHTING_MIDDLE}|{REGEX_WEIGHTING_END})$"

DATA_SCHEMA_SOURCE = vol.Schema({
  vol.Required(CONFIG_DATA_SOURCE_NAME): str,
  vol.Required(CONFIG_DATA_SOURCE_ID): str,
})

DATA_SCHEMA_TARGET_TIME_PERIOD = vol.Schema({
  vol.Required(CONFIG_TARGET_NAME): str,
  vol.Required(CONFIG_TARGET_HOURS): str,
  vol.Required(CONFIG_TARGET_HOURS_MODE, default=CONFIG_TARGET_HOURS_MODE_EXACT): selector.SelectSelector(
      selector.SelectSelectorConfig(
          options=[
            selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_EXACT, label="Exact"),
            selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MINIMUM, label="Minimum"),
            selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MAXIMUM, label="Maximum"),
          ],
          mode=selector.SelectSelectorMode.DROPDOWN,
      )
  ),
  vol.Required(CONFIG_TARGET_TYPE, default=CONFIG_TARGET_TYPE_CONTINUOUS): selector.SelectSelector(
      selector.SelectSelectorConfig(
          options=[
            selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_CONTINUOUS, label="Continuous"),
            selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_INTERMITTENT, label="Intermittent"),
          ],
          mode=selector.SelectSelectorMode.DROPDOWN,
      )
  ),
  vol.Optional(CONFIG_TARGET_START_TIME): str,
  vol.Optional(CONFIG_TARGET_END_TIME): str,
  vol.Optional(CONFIG_TARGET_OFFSET): str,
  vol.Required(CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE, default=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST): selector.SelectSelector(
      selector.SelectSelectorConfig(
          options=[
            selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, label="All existing target rates are in the past"),
            selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, label="Existing target rates haven't started or finished"),
          ],
          mode=selector.SelectSelectorMode.DROPDOWN,
      )
  ),
  vol.Optional(CONFIG_TARGET_ROLLING_TARGET, default=False): bool,
  vol.Optional(CONFIG_TARGET_LATEST_VALUES, default=False): bool,
  vol.Optional(CONFIG_TARGET_INVERT_TARGET_VALUES, default=False): bool,
  vol.Optional(CONFIG_TARGET_MIN_VALUE): str,
  vol.Optional(CONFIG_TARGET_MAX_VALUE): str,
  vol.Optional(CONFIG_TARGET_WEIGHTING): str,
})

DATA_SCHEMA_ROLLING_TARGET_TIME_PERIOD = vol.Schema({
  vol.Required(CONFIG_TARGET_NAME): str,
  vol.Required(CONFIG_TARGET_HOURS): str,
  vol.Required(CONFIG_TARGET_HOURS_MODE, default=CONFIG_TARGET_HOURS_MODE_EXACT): selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[
          selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_EXACT, label="Exact"),
          selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MINIMUM, label="Minimum"),
          selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MAXIMUM, label="Maximum"),
        ],
        mode=selector.SelectSelectorMode.DROPDOWN,
    )
  ),
  vol.Required(CONFIG_TARGET_TYPE, default=CONFIG_TARGET_TYPE_CONTINUOUS): selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[
          selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_CONTINUOUS, label="Continuous"),
          selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_INTERMITTENT, label="Intermittent"),
        ],
        mode=selector.SelectSelectorMode.DROPDOWN,
    )
  ),
  vol.Required(CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD): str,
  vol.Optional(CONFIG_TARGET_OFFSET): str,
  vol.Required(CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE, default=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST): selector.SelectSelector(
      selector.SelectSelectorConfig(
          options=[
            selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, label="All existing target rates are in the past"),
            selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, label="Existing target rates haven't started or finished"),
            selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS, label="Always"),
          ],
          mode=selector.SelectSelectorMode.DROPDOWN,
      )
  ),
  vol.Optional(CONFIG_TARGET_LATEST_VALUES): bool,
  vol.Optional(CONFIG_TARGET_INVERT_TARGET_VALUES): bool,
  vol.Optional(CONFIG_TARGET_MIN_VALUE): str,
  vol.Optional(CONFIG_TARGET_MAX_VALUE): str,
  vol.Optional(CONFIG_TARGET_WEIGHTING): str,
})