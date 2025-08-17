import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.target_timeframes.config.rolling_target_timeframe import validate_rolling_target_timeframe_config
from custom_components.target_timeframes.const import CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD, CONFIG_TARGET_DANGEROUS_SETTINGS, CONFIG_TARGET_HOURS, CONFIG_TARGET_HOURS_MODE, CONFIG_TARGET_HOURS_MODE_EXACT, CONFIG_TARGET_HOURS_MODE_MAXIMUM, CONFIG_TARGET_HOURS_MODE_MINIMUM, CONFIG_TARGET_MAX_VALUE, CONFIG_TARGET_MIN_VALUE, CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT, CONFIG_TARGET_NAME, CONFIG_TARGET_OFFSET, CONFIG_TARGET_TYPE, CONFIG_TARGET_TYPE_CONTINUOUS, CONFIG_TARGET_TYPE_INTERMITTENT, CONFIG_TARGET_WEIGHTING, DATA_SCHEMA_ROLLING_TARGET_TIME_PERIOD
from ..config import assert_errors_not_present, get_schema_keys

now = as_utc(parse_datetime("2023-08-20T10:00:00Z"))

default_keys = get_schema_keys(DATA_SCHEMA_ROLLING_TARGET_TIME_PERIOD.schema)

@pytest.mark.asyncio
async def test_when_config_is_valid_no_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_VALUE: "0",
    CONFIG_TARGET_MAX_VALUE: "10",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert_errors_not_present(errors, default_keys)

@pytest.mark.asyncio
async def test_when_optional_config_is_valid_no_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: None,
    CONFIG_TARGET_MIN_VALUE: None,
    CONFIG_TARGET_MAX_VALUE: None,
    CONFIG_TARGET_WEIGHTING: None,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert_errors_not_present(errors, default_keys)

@pytest.mark.asyncio
@pytest.mark.parametrize("name",[
  (""),
  ("Test"),
  ("test@"),
])
async def test_when_config_has_invalid_name_then_errors_returned(name):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: name,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_NAME in errors
  assert errors[CONFIG_TARGET_NAME] == "invalid_target_name"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_NAME)

@pytest.mark.asyncio
async def test_when_config_has_valid_hours_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "0",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert_errors_not_present(errors, default_keys)

@pytest.mark.asyncio
@pytest.mark.parametrize("hours",[
  (""),
  ("-1.0"),
  ("s"),
  ("1.01"),
  ("1.49"),
  ("1.51"),
  ("1.99"),
])
async def test_when_config_has_invalid_hours_then_errors_returned(hours):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: hours,
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_HOURS in errors
  assert errors[CONFIG_TARGET_HOURS] == "invalid_target_hours"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_HOURS)

@pytest.mark.asyncio
@pytest.mark.parametrize("look_ahead",[
  (""),
  ("s"),
  ("-0"),
  ("-0.01"),
])
async def test_when_config_has_invalid_look_ahead_hours_then_errors_returned(look_ahead):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: look_ahead,
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD in errors
  assert errors[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD] == "invalid_target_hours"
  assert_errors_not_present(errors, default_keys, CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD)

@pytest.mark.asyncio
@pytest.mark.parametrize("offset",[
  (""),
  ("s"),
  ("00"),
  ("-00"),
  ("00:00"),
  ("-00:00"),
  ("24:00:00"),
  ("-24:00:00"),
  ("00:60:00"),
  ("-00:60:00"),
  ("00:00:60"),
  ("-00:00:60"),
])
async def test_when_config_has_invalid_offset_then_errors_returned(offset):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: offset,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_OFFSET in errors
  assert errors[CONFIG_TARGET_OFFSET] == "invalid_offset"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_OFFSET)

@pytest.mark.asyncio
async def test_when_hours_exceed_selected_look_ahead_hours_then_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "1.49",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD in errors
  assert errors[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD] == "invalid_target_hours"
  assert_errors_not_present(errors, default_keys, CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD)

@pytest.mark.asyncio
@pytest.mark.parametrize("weighting,expected_error",[
  ("*", "invalid_weighting"),
  ("*,*", "invalid_weighting"),
  ("1,*,1,*", "invalid_weighting"),
  ("a,*", "invalid_weighting"),
  ("1,2", "invalid_weighting_slots"),
  ("1,2,3,4", "invalid_weighting_slots"),
])
async def test_when_weighting_is_invalid_then_weighting_error_returned(weighting, expected_error):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_WEIGHTING: weighting,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == expected_error
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_WEIGHTING)

@pytest.mark.asyncio
@pytest.mark.parametrize("type",[
  (CONFIG_TARGET_TYPE_INTERMITTENT),
])
async def test_when_weighting_set_and_type_invalid_then_weighting_error_returned(type):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: type,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_WEIGHTING: "1,2,3",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == "weighting_not_supported_for_type"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_WEIGHTING)

@pytest.mark.asyncio
@pytest.mark.parametrize("min_value,max_value",[
  (None,"1.5"),
  (None,1.5),
  (None,"-1.5"),
  (None,-1.5),
  ("1.5",None),
  (1.5,None),
  ("-1.5",None),
  (-1.5,None),
  ("1.5","2.0"),
  (1.5,2.0),
  ("-2.0","-1.5"),
  (-2.0,-1.5),
])
async def test_when_hour_mode_is_minimum_and_minimum_or_maximum_value_is_specified_then_no_error_returned(min_value: float, max_value: float):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_VALUE: min_value,
    CONFIG_TARGET_MAX_VALUE: max_value,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_MINIMUM
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert_errors_not_present(errors, default_keys)

@pytest.mark.asyncio
@pytest.mark.parametrize("min_value,max_value",[
  ("1.5","1.49"),
  (1.5,1.49),
  ("-1.49","-1.5"),
  (-1.49,-1.5),
])
async def test_when_minimum_value_greater_to_maximum_value_is_specified_then_error_returned(min_value: float, max_value: float):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_VALUE: min_value,
    CONFIG_TARGET_MAX_VALUE: max_value,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_MINIMUM
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_MIN_VALUE in errors
  assert errors[CONFIG_TARGET_MIN_VALUE] == "minimum_value_not_less_than_maximum_value"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_MIN_VALUE)

@pytest.mark.asyncio
@pytest.mark.parametrize("hour_mode",[
  (CONFIG_TARGET_HOURS_MODE_MINIMUM),
  (CONFIG_TARGET_HOURS_MODE_MAXIMUM),
])
async def test_when_hour_mode_is_not_exact_and_weighting_specified_then_error_returned(hour_mode: str):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_MIN_VALUE: "0.18",
    CONFIG_TARGET_HOURS_MODE: hour_mode
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == "weighting_not_supported_for_hour_mode"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_WEIGHTING)

@pytest.mark.asyncio
async def test_when_hour_mode_is_minimum_and_minimum_and_maximum_value_is_not_specified_then_error_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_MINIMUM
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_HOURS_MODE in errors
  assert errors[CONFIG_TARGET_HOURS_MODE] == "minimum_or_maximum_value_not_specified"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_HOURS_MODE)

@pytest.mark.asyncio
@pytest.mark.parametrize("minimum_required_minutes",[
  ("30"),
  (30),
  ("1"),
  (1),
])
async def test_when_minimum_required_minutes_set_to_valid_integer_then_no_error_returned(minimum_required_minutes):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_VALUE: "0",
    CONFIG_TARGET_MAX_VALUE: "10",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
    CONFIG_TARGET_DANGEROUS_SETTINGS: {
      CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT: minimum_required_minutes
    }
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert_errors_not_present(errors, default_keys)

@pytest.mark.asyncio
@pytest.mark.parametrize("minimum_required_minutes",[
  ("30.1"),
  (30.1),
  ("a"),
])
async def test_when_minimum_required_minutes_set_to_invalid_integer_then_error_returned(minimum_required_minutes):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_VALUE: "0",
    CONFIG_TARGET_MAX_VALUE: "10",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
    CONFIG_TARGET_DANGEROUS_SETTINGS: {
      CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT: minimum_required_minutes
    }
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_DANGEROUS_SETTINGS in errors
  assert errors[CONFIG_TARGET_DANGEROUS_SETTINGS] == "invalid_integer"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_DANGEROUS_SETTINGS)

@pytest.mark.asyncio
@pytest.mark.parametrize("minimum_required_minutes",[
  ("0"),
  (0),
  ("31"),
  (31),
])
async def test_when_minimum_required_minutes_set_to_invalid_value_then_error_returned(minimum_required_minutes):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: "2",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_VALUE: "0",
    CONFIG_TARGET_MAX_VALUE: "10",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
    CONFIG_TARGET_DANGEROUS_SETTINGS: {
      CONFIG_TARGET_MINIMUM_REQUIRED_MINUTES_IN_SLOT: minimum_required_minutes
    }
  }

  # Act
  errors = validate_rolling_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_DANGEROUS_SETTINGS in errors
  assert errors[CONFIG_TARGET_DANGEROUS_SETTINGS] == "invalid_minimum_required_minutes_in_slot"
  assert_errors_not_present(errors, default_keys, CONFIG_TARGET_DANGEROUS_SETTINGS)