import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.target_timeframes.config.target_timeframe import validate_target_timeframe_config
from custom_components.target_timeframes.const import CONFIG_TARGET_END_TIME, CONFIG_TARGET_HOURS, CONFIG_TARGET_HOURS_MODE, CONFIG_TARGET_HOURS_MODE_EXACT, CONFIG_TARGET_HOURS_MODE_MAXIMUM, CONFIG_TARGET_HOURS_MODE_MINIMUM, CONFIG_TARGET_MAX_VALUE, CONFIG_TARGET_MIN_VALUE, CONFIG_TARGET_NAME, CONFIG_TARGET_OFFSET, CONFIG_TARGET_START_TIME, CONFIG_TARGET_TYPE, CONFIG_TARGET_TYPE_CONTINUOUS, CONFIG_TARGET_TYPE_INTERMITTENT, CONFIG_TARGET_WEIGHTING

now = as_utc(parse_datetime("2023-08-20T10:00:00Z"))

@pytest.mark.asyncio
async def test_when_config_is_valid_no_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "00:00",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_VALUE: "0",
    CONFIG_TARGET_MAX_VALUE: "10",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
async def test_when_optional_config_is_valid_no_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: None,
    CONFIG_TARGET_END_TIME: None,
    CONFIG_TARGET_OFFSET: None,
    CONFIG_TARGET_MIN_VALUE: None,
    CONFIG_TARGET_MAX_VALUE: None,
    CONFIG_TARGET_WEIGHTING: None,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

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
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_NAME in errors
  assert errors[CONFIG_TARGET_NAME] == "invalid_target_name"
  
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
async def test_when_config_has_valid_hours_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "0",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

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
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_HOURS in errors
  assert errors[CONFIG_TARGET_HOURS] == "invalid_target_hours"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time",[
  (""),
  ("s"),
  ("24:00"),
  ("-0:01"),
  ("00:000"),
  ("00:60"),
  ("00:00:00"),
])
async def test_when_config_has_invalid_start_time_then_errors_returned(start_time):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: start_time,
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_START_TIME in errors
  assert errors[CONFIG_TARGET_START_TIME] == "invalid_target_time"
  
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("end_time",[
  (""),
  ("s"),
  ("24:00"),
  ("-0:01"),
  ("00:000"),
  ("00:60"),
  ("00:00:00"),
])
async def test_when_config_has_invalid_end_time_then_errors_returned(end_time):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: end_time,
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_END_TIME in errors
  assert errors[CONFIG_TARGET_END_TIME] == "invalid_target_time"
  
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

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
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: offset,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_OFFSET in errors
  assert errors[CONFIG_TARGET_OFFSET] == "invalid_offset"
  
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time,end_time",[
  ("01:00","02:00"),
  ("23:00","00:00"),
])
async def test_when_hours_exceed_selected_time_frame_then_errors_returned(start_time, end_time):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: start_time,
    CONFIG_TARGET_END_TIME: end_time,
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_HOURS in errors
  assert errors[CONFIG_TARGET_HOURS] == "invalid_hours_time_frame"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time,end_time,offset",[
  ("00:00","00:00","00:00:00"),
  (None, None, None),
])
async def test_when_config_is_valid_and_not_agile_then_no_errors_returned(start_time, end_time, offset):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  if start_time is not None:
    data[CONFIG_TARGET_START_TIME] = start_time

  if end_time is not None:
    data[CONFIG_TARGET_END_TIME] = end_time
  
  if offset is not None:
    data[CONFIG_TARGET_OFFSET] = offset

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time,end_time,offset",[
  ("00:00","23:00","00:00:00"),
  ("00:00","16:00","00:00:00"),
  ("23:00","16:00","00:00:00"),
  ("16:00","16:00","00:00:00"),
  ("16:00","00:00","00:00:00"),
  (None, "23:00", None),
  ("16:00", None, None),
  ("10:00","23:00","00:00:00"),
  ("16:30","23:30","00:00:00"),
  ("17:00","14:00","00:00:00"),
])
async def test_when_config_is_valid_and_agile_then_no_errors_returned(start_time, end_time, offset):
  # Arrange
  data = {
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  if start_time is not None:
    data[CONFIG_TARGET_START_TIME] = start_time

  if end_time is not None:
    data[CONFIG_TARGET_END_TIME] = end_time
  
  if offset is not None:
    data[CONFIG_TARGET_OFFSET] = offset


  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

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
    CONFIG_TARGET_WEIGHTING: weighting,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == expected_error

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

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
    CONFIG_TARGET_WEIGHTING: "1,2,3",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == "weighting_not_supported_for_type"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("min_value,max_value",[
  (None,"1.5"),
  ("1.5",None),
  ("1.5","2.0"),
])
async def test_when_hour_mode_is_minimum_and_minimum_or_maximum_value_is_specified_then_no_error_returned(min_value: float, max_value: float):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "00:00",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_VALUE: min_value,
    CONFIG_TARGET_MAX_VALUE: max_value,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_MINIMUM
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

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
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "00:00",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_MIN_VALUE: "0.18",
    CONFIG_TARGET_HOURS_MODE: hour_mode
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == "weighting_not_supported_for_hour_mode"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
async def test_when_hour_mode_is_minimum_and_minimum_and_maximum_value_is_not_specified_then_error_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "00:00",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_MINIMUM
  }

  # Act
  errors = validate_target_timeframe_config(data)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_VALUE not in errors
  assert CONFIG_TARGET_MAX_VALUE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE in errors
  assert errors[CONFIG_TARGET_HOURS_MODE] == "minimum_or_maximum_value_not_specified"