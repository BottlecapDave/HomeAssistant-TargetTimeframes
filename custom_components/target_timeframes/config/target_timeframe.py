import re
from datetime import timedelta

from homeassistant.util.dt import (parse_datetime)

from ..const import (
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_HOURS_MODE,
  CONFIG_TARGET_HOURS_MODE_EXACT,
  CONFIG_TARGET_HOURS_MODE_MINIMUM,
  CONFIG_TARGET_MAX_VALUE,
  CONFIG_TARGET_MIN_VALUE,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_TYPE_CONTINUOUS,
  CONFIG_TARGET_WEIGHTING,
  REGEX_ENTITY_NAME,
  REGEX_HOURS,
  REGEX_OFFSET_PARTS,
  REGEX_VALUE,
  REGEX_TIME,
  REGEX_WEIGHTING
)

from ..entities import create_weighting

async def async_migrate_target_timeframe_config(version: int, data: {}, get_entries):
  new_data = {**data}

  return new_data

def merge_target_timeframe_config(data: dict, updated_config: dict = None):
  config = dict(data)

  if updated_config is not None:
    config.update(updated_config)

    if CONFIG_TARGET_START_TIME not in updated_config and CONFIG_TARGET_START_TIME in config:
      config[CONFIG_TARGET_START_TIME] = None

    if CONFIG_TARGET_END_TIME not in updated_config and CONFIG_TARGET_END_TIME in config:
      config[CONFIG_TARGET_END_TIME] = None

    if CONFIG_TARGET_OFFSET not in updated_config and CONFIG_TARGET_OFFSET in config:
      config[CONFIG_TARGET_OFFSET] = None

    if CONFIG_TARGET_MIN_VALUE not in updated_config and CONFIG_TARGET_MIN_VALUE in config:
      config[CONFIG_TARGET_MIN_VALUE] = None

    if CONFIG_TARGET_MAX_VALUE not in updated_config and CONFIG_TARGET_MAX_VALUE in config:
      config[CONFIG_TARGET_MAX_VALUE] = None

    if CONFIG_TARGET_WEIGHTING not in updated_config and CONFIG_TARGET_WEIGHTING in config:
      config[CONFIG_TARGET_WEIGHTING] = None

  return config

def is_time_frame_long_enough(hours, start_time, end_time):
  start_time = parse_datetime(f"2023-08-01T{start_time}:00Z")
  end_time = parse_datetime(f"2023-08-01T{end_time}:00Z")
  if end_time <= start_time:
    end_time = end_time + timedelta(days=1)

  time_diff = end_time - start_time
  available_minutes = time_diff.total_seconds() / 60
  target_minutes = (hours / 0.5) * 30

  return available_minutes >= target_minutes

def validate_target_timeframe_config(data):
  errors = {}

  matches = re.search(REGEX_ENTITY_NAME, data[CONFIG_TARGET_NAME])
  if matches is None:
    errors[CONFIG_TARGET_NAME] = "invalid_target_name"

  # For some reason float type isn't working properly - reporting user input malformed
  if isinstance(data[CONFIG_TARGET_HOURS], float) == False:
    matches = re.search(REGEX_HOURS, data[CONFIG_TARGET_HOURS])
    if matches is None:
      errors[CONFIG_TARGET_HOURS] = "invalid_target_hours"
    else:
      data[CONFIG_TARGET_HOURS] = float(data[CONFIG_TARGET_HOURS])
  
  if CONFIG_TARGET_HOURS not in errors:
    if data[CONFIG_TARGET_HOURS] % 0.5 != 0:
      errors[CONFIG_TARGET_HOURS] = "invalid_target_hours"

  if CONFIG_TARGET_START_TIME in data and data[CONFIG_TARGET_START_TIME] is not None:
    matches = re.search(REGEX_TIME, data[CONFIG_TARGET_START_TIME])
    if matches is None:
      errors[CONFIG_TARGET_START_TIME] = "invalid_target_time"

  if CONFIG_TARGET_END_TIME in data and data[CONFIG_TARGET_END_TIME] is not None:
    matches = re.search(REGEX_TIME, data[CONFIG_TARGET_END_TIME])
    if matches is None:
      errors[CONFIG_TARGET_END_TIME] = "invalid_target_time"

  if CONFIG_TARGET_OFFSET in data and data[CONFIG_TARGET_OFFSET] is not None:
    matches = re.search(REGEX_OFFSET_PARTS, data[CONFIG_TARGET_OFFSET])
    if matches is None:
      errors[CONFIG_TARGET_OFFSET] = "invalid_offset"

  minimum_value: float | None = None
  if CONFIG_TARGET_MIN_VALUE in data and data[CONFIG_TARGET_MIN_VALUE] is not None:
    if isinstance(data[CONFIG_TARGET_MIN_VALUE], float) == False:
      matches = re.search(REGEX_VALUE, data[CONFIG_TARGET_MIN_VALUE])
      if matches is None:
        errors[CONFIG_TARGET_MIN_VALUE] = "invalid_value"
      else:
        minimum_value = float(data[CONFIG_TARGET_MIN_VALUE])
        data[CONFIG_TARGET_MIN_VALUE] = minimum_value
    else:
      minimum_value = data[CONFIG_TARGET_MIN_VALUE]

  maximum_value: float | None = None
  if CONFIG_TARGET_MAX_VALUE in data and data[CONFIG_TARGET_MAX_VALUE] is not None:
    if isinstance(data[CONFIG_TARGET_MAX_VALUE], float) == False:
      matches = re.search(REGEX_VALUE, data[CONFIG_TARGET_MAX_VALUE])
      if matches is None:
        errors[CONFIG_TARGET_MAX_VALUE] = "invalid_value"
      else:
        maximum_value = float(data[CONFIG_TARGET_MAX_VALUE])
        data[CONFIG_TARGET_MAX_VALUE] = maximum_value
    else:
      maximum_value = data[CONFIG_TARGET_MAX_VALUE]

  if minimum_value is not None and maximum_value is not None and minimum_value > maximum_value:
    errors[CONFIG_TARGET_MIN_VALUE] = "minimum_value_not_less_than_maximum_value"

  if CONFIG_TARGET_WEIGHTING in data and data[CONFIG_TARGET_WEIGHTING] is not None:
    matches = re.search(REGEX_WEIGHTING, data[CONFIG_TARGET_WEIGHTING])
    if matches is None:
      errors[CONFIG_TARGET_WEIGHTING] = "invalid_weighting"
    
    if CONFIG_TARGET_WEIGHTING not in errors:
      number_of_slots = int(data[CONFIG_TARGET_HOURS] * 2)
      weighting = create_weighting(data[CONFIG_TARGET_WEIGHTING], number_of_slots)

      if (len(weighting) != number_of_slots):
        errors[CONFIG_TARGET_WEIGHTING] = "invalid_weighting_slots"

    if data[CONFIG_TARGET_TYPE] != CONFIG_TARGET_TYPE_CONTINUOUS:
      errors[CONFIG_TARGET_WEIGHTING] = "weighting_not_supported_for_type"
    
    if CONFIG_TARGET_HOURS_MODE in data and data[CONFIG_TARGET_HOURS_MODE] != CONFIG_TARGET_HOURS_MODE_EXACT:
      errors[CONFIG_TARGET_WEIGHTING] = "weighting_not_supported_for_hour_mode"

  if CONFIG_TARGET_HOURS_MODE in data and data[CONFIG_TARGET_HOURS_MODE] == CONFIG_TARGET_HOURS_MODE_MINIMUM:
    if (CONFIG_TARGET_MIN_VALUE not in data or data[CONFIG_TARGET_MIN_VALUE] is None) and (CONFIG_TARGET_MAX_VALUE not in data or data[CONFIG_TARGET_MAX_VALUE] is None):
      errors[CONFIG_TARGET_HOURS_MODE] = "minimum_or_maximum_value_not_specified"

  start_time = data[CONFIG_TARGET_START_TIME] if CONFIG_TARGET_START_TIME in data and data[CONFIG_TARGET_START_TIME] is not None else "00:00"
  end_time = data[CONFIG_TARGET_END_TIME] if CONFIG_TARGET_END_TIME in data and data[CONFIG_TARGET_END_TIME] is not None else "00:00"

  is_time_valid = CONFIG_TARGET_START_TIME not in errors and CONFIG_TARGET_END_TIME not in errors

  if CONFIG_TARGET_HOURS not in errors and is_time_valid:
    if is_time_frame_long_enough(data[CONFIG_TARGET_HOURS], start_time, end_time) == False:
      errors[CONFIG_TARGET_HOURS] = "invalid_hours_time_frame"

  return errors