from datetime import datetime, timedelta
from decimal import Decimal
from custom_components.target_timeframes.const import CONFIG_TARGET_HOURS_MODE_MAXIMUM, CONFIG_TARGET_HOURS_MODE_MINIMUM
import pytest

from unit import (create_data_source_data, default_time_periods)
from custom_components.target_timeframes.entities import calculate_intermittent_times, get_fixed_applicable_time_periods, get_start_and_end_times

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target,find_last_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),

  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),

  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),

  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
])
async def test_when_intermittent_times_present_then_next_intermittent_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target, find_last_rates):
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_values = [0.1, 0.2, 0.3]

  values = create_data_source_data(
    period_from,
    period_to,
    expected_values
  )
  
  # Restrict our time block
  target_hours = 1

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, is_rolling_target)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    target_hours,
    False,
    find_last_rates
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == expected_first_valid_from
  assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value"] == 0.1

  assert result[1]["start"] == expected_first_valid_from + timedelta(hours=1, minutes=30)
  assert result[1]["end"] == expected_first_valid_from + timedelta(hours=2)
  assert result[1]["value"] == 0.1

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target,find_last_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
])
async def test_when_intermittent_times_present_and_highest_prices_are_true_then_next_intermittent_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target, find_last_rates):
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_values = [0.1, 0.2, 0.3]

  values = create_data_source_data(
    period_from,
    period_to,
    expected_values
  )
  
  # Restrict our time block
  target_hours = 1

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, is_rolling_target)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    target_hours,
    True,
    find_last_rates
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == expected_first_valid_from
  assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value"] == 0.3

  assert result[1]["start"] == expected_first_valid_from + timedelta(hours=1, minutes=30)
  assert result[1]["end"] == expected_first_valid_from + timedelta(hours=2)
  assert result[1]["value"] == 0.3

@pytest.mark.asyncio
async def test_when_current_time_has_not_enough_time_left_then_no_intermittent_times_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_values = [0.1, 0.2, 0.3]

  values = create_data_source_data(
    period_from,
    period_to,
    expected_values
  )
  
  # Restrict our time block
  current_date = datetime.strptime("2022-02-09T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "18:00"
  target_hours = 1

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, True)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    target_hours
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_using_agile_times_then_lowest_rates_are_picked():
  # Arrange
  current_date = datetime.strptime("2022-10-21T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 3

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, False)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    default_time_periods
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    target_hours
  )

  # Assert
  assert result is not None
  assert len(result) == 6

  assert result[0]["start"] == datetime.strptime("2022-10-21T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["end"] == datetime.strptime("2022-10-22T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["value"] == 14.123

  assert result[1]["start"] == datetime.strptime("2022-10-22T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["end"] == datetime.strptime("2022-10-22T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["value"] == 14.123

  assert result[2]["start"] == datetime.strptime("2022-10-22T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[2]["end"] == datetime.strptime("2022-10-22T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[2]["value"] == 17.9025

  assert result[3]["start"] == datetime.strptime("2022-10-22T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[3]["end"] == datetime.strptime("2022-10-22T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[3]["value"] == 17.136

  assert result[4]["start"] == datetime.strptime("2022-10-22T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[4]["end"] == datetime.strptime("2022-10-22T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[4]["value"] == 17.136

  assert result[5]["start"] == datetime.strptime("2022-10-22T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[5]["end"] == datetime.strptime("2022-10-22T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[5]["value"] == 18.081

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_then_no_times_are_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 3

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, False)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    default_time_periods
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    target_hours
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("target_hours,expected_valid_froms,expected_values",[
  (0.5, [datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")], [19.1]),
  (1, [datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2022-10-22T19:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")], [19.1, 19.1]),
])
async def test_when_min_value_is_provided_then_result_does_not_include_any_rate_below_min_value(target_hours: float, expected_valid_froms: datetime, expected_values: list):
  # Arrange
  current_date = datetime.strptime("2022-10-22T16:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  min_value = 19

  values = create_data_source_data(
    datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.5, 17.9, 16.5, 20.1]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, False)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    target_hours,
    min_value=min_value
  )

  # Assert
  assert result is not None
  assert len(result) == len(expected_values)

  for index in range(0, len(expected_values)):
    assert result[index]["start"] == expected_valid_froms[index]
    assert result[index]["end"] == expected_valid_froms[index] + timedelta(minutes=30)
    assert result[index]["value"] == expected_values[index]

@pytest.mark.asyncio
@pytest.mark.parametrize("target_hours,expected_valid_froms,expected_values",[
  (0.5, [datetime.strptime("2022-10-22T17:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")], [19.5]),
  (1, [datetime.strptime("2022-10-22T17:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2022-10-22T20:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")], [19.5, 19.5]),
])
async def test_when_max_value_is_provided_then_result_does_not_include_any_rate_below_max_value(target_hours: float, expected_valid_froms: datetime, expected_values: list):
  # Arrange
  current_date = datetime.strptime("2022-10-22T16:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  max_value = 20.0

  values = create_data_source_data(
    datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.5, 17.9, 16.5, 20.1]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, False)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    target_hours,
    True,
    max_value=max_value
  )

  # Assert
  assert result is not None
  assert len(result) == len(expected_values)

  for index in range(0, len(expected_values)):
    assert result[index]["start"] == expected_valid_froms[index]
    assert result[index]["end"] == expected_valid_froms[index] + timedelta(minutes=30)
    assert result[index]["value"] == expected_values[index]

@pytest.mark.asyncio
async def test_when_hour_mode_is_maximum_and_not_enough_hours_available_then_reduced_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T16:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "12:00"
  target_end_time = "16:00"
  max_value = 19

  values = create_data_source_data(
    datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.5, 18.9, 20.1, 18.9]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, False)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    3,
    True,
    max_value=max_value,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MAXIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 4

  expected_valid_from = datetime.strptime("2022-10-23T12:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 4):
    assert result[index]["start"] == expected_valid_from
    assert result[index]["end"] == expected_valid_from + timedelta(minutes=30)
    expected_valid_from = expected_valid_from + timedelta(minutes=60)
    assert result[index]["value"] == 18.9

@pytest.mark.asyncio
async def test_when_hour_mode_is_maximum_and_more_than_enough_hours_available_then_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T16:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"

  values = create_data_source_data(
    datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.5, 18.9, 20.1, 18.9]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, False)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    3,
    False,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MAXIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 6

  expected_valid_from = datetime.strptime("2022-10-22T16:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 6):
    assert result[index]["start"] == expected_valid_from
    assert result[index]["end"] == expected_valid_from + timedelta(minutes=30)
    expected_valid_from = expected_valid_from + timedelta(minutes=60)
    assert result[index]["value"] == 18.9

@pytest.mark.asyncio
async def test_when_hour_mode_is_minimum_and_not_enough_hours_available_then_no_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T16:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "12:00"
  target_end_time = "16:00"
  max_value = 19

  values = create_data_source_data(
    datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.5, 18.9, 20.1, 18.9]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, False)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    3,
    False,
    max_value=max_value,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MINIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_hour_mode_is_minimum_and_more_than_enough_hours_available_then_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T16:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  max_value = 19

  values = create_data_source_data(
    datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.5, 18.9, 20.1, 18.9]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, False)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    3,
    False,
    max_value=max_value,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MINIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 24

  expected_valid_from = datetime.strptime("2022-10-22T16:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 24):
    assert result[index]["start"] == expected_valid_from
    assert result[index]["end"] == expected_valid_from + timedelta(minutes=30)
    expected_valid_from = expected_valid_from + timedelta(minutes=60)
    assert result[index]["value"] == 18.9

@pytest.mark.asyncio
async def test_when_clocks_go_back_then_correct_rates_are_selected():
  # Arrange
  max_value = 20
  applicable_time_periods = [
    {
      "value_exc_vat": 13.14,
      "value": 13.797,
      "start": datetime.strptime("2024-10-27T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 23.94,
      "value": 25.137,
      "start": datetime.strptime("2024-10-27T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.96,
      "value": 16.758,
      "start": datetime.strptime("2024-10-27T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 25.2,
      "value": 26.46,
      "start": datetime.strptime("2024-10-27T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 17.68,
      "value": 18.564,
      "start": datetime.strptime("2024-10-27T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 23.18,
      "value": 24.339,
      "start": datetime.strptime("2024-10-27T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 18.82,
      "value": 19.761,
      "start": datetime.strptime("2024-10-27T19:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 19.02,
      "value": 19.971,
      "start": datetime.strptime("2024-10-27T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T19:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 32.22,
      "value": 33.831,
      "start": datetime.strptime("2024-10-27T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 37.54,
      "value": 39.417,
      "start": datetime.strptime("2024-10-27T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 34.85,
      "value": 36.5925,
      "start": datetime.strptime("2024-10-27T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 37.2,
      "value": 39.06,
      "start": datetime.strptime("2024-10-27T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 35.1,
      "value": 36.855,
      "start": datetime.strptime("2024-10-27T16:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 30.16,
      "value": 31.668,
      "start": datetime.strptime("2024-10-27T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T16:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 20.71,
      "value": 21.7455,
      "start": datetime.strptime("2024-10-27T15:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.54,
      "value": 16.317,
      "start": datetime.strptime("2024-10-27T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T15:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 17.43,
      "value": 18.3015,
      "start": datetime.strptime("2024-10-27T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.75,
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 16.67,
      "value": 17.5035,
      "start": datetime.strptime("2024-10-27T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 17.85,
      "value": 18.7425,
      "start": datetime.strptime("2024-10-27T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.69,
      "value": 16.4745,
      "start": datetime.strptime("2024-10-27T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.75,
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 16.28,
      "value": 17.094,
      "start": datetime.strptime("2024-10-27T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.75,
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.75,
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 16.77,
      "value": 17.6085,
      "start": datetime.strptime("2024-10-27T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 18.72,
      "value": 19.656,
      "start": datetime.strptime("2024-10-27T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 19.53,
      "value": 20.5065,
      "start": datetime.strptime("2024-10-27T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 19.24,
      "value": 22002,
      "start": datetime.strptime("2024-10-27T08:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 19.22,
      "value": 20.181,
      "start": datetime.strptime("2024-10-27T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T08:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 18.65,
      "value": 19.5825,
      "start": datetime.strptime("2024-10-27T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 18.9,
      "value": 19.845,
      "start": datetime.strptime("2024-10-27T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 22.26,
      "value": 23.373,
      "start": datetime.strptime("2024-10-27T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 17.85,
      "value": 18.7425,
      "start": datetime.strptime("2024-10-27T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 19.82,
      "value": 20.811,
      "start": datetime.strptime("2024-10-27T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.75,
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 18.06,
      "value": 18.963,
      "start": datetime.strptime("2024-10-27T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 18.45,
      "value": 19.3725,
      "start": datetime.strptime("2024-10-27T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.96,
      "value": 16.758,
      "start": datetime.strptime("2024-10-27T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.59,
      "value": 16.3695,
      "start": datetime.strptime("2024-10-27T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 14.7,
      "value": 15.435,
      "start": datetime.strptime("2024-10-27T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 15.12,
      "value": 15.876,
      "start": datetime.strptime("2024-10-27T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 16.05,
      "value": 16.8525,
      "start": datetime.strptime("2024-10-27T01:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 22.85,
      "value": 23.9925,
      "start": datetime.strptime("2024-10-27T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T01:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 21,
      "value": 22.05,
      "start": datetime.strptime("2024-10-27T00:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 14.7,
      "value": 15.435,
      "start": datetime.strptime("2024-10-27T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T00:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 18.32,
      "value": 19.236,
      "start": datetime.strptime("2024-10-26T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value_exc_vat": 20.16,
      "value": 21.168,
      "start": datetime.strptime("2024-10-26T23:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-26T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
    },
  ]
  
  applicable_time_periods.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    12,
    False,
    max_value=max_value,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MAXIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 24

@pytest.mark.parametrize("search_for_highest_rate,find_last_rates,expected_start",[
  (True, True, datetime.strptime("2024-11-27T23:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")),
  (True, False, datetime.strptime("2024-11-27T20:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")),
  (False, True, datetime.strptime("2024-11-27T22:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")),
  (False, False, datetime.strptime("2024-11-27T21:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")),
])
def test_when_weighting_present_in_rates_then_weighted_rate_is_picked(search_for_highest_rate: bool, find_last_rates: bool, expected_start: datetime):
  applicable_time_periods = create_data_source_data(datetime.strptime("2024-11-27T20:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
                                      datetime.strptime("2024-11-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
                                      [20])
  
  applicable_time_periods[2]["weighting"] = Decimal(0.5)
  applicable_time_periods[2]["value"] = 0.3
  
  applicable_time_periods[3]["weighting"] = Decimal(0.5)
  applicable_time_periods[3]["value"] = 0.3

  applicable_time_periods[4]["weighting"] = Decimal(0.5)
  applicable_time_periods[4]["value"] = 0.3
  
  applicable_time_periods[5]["weighting"] = Decimal(0.5)
  applicable_time_periods[5]["value"] = 0.3

  # Act
  result = calculate_intermittent_times(
    applicable_time_periods,
    1,
    search_for_highest_rate,
    find_last_rates,
  )

  # Assert
  print(result)
  assert result is not None
  assert len(result) == 2

  current_start = expected_start
  for rate in result:
    assert rate["start"] == current_start
    current_start = current_start + timedelta(minutes=30)
    assert rate["end"] == current_start