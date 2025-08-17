from datetime import datetime, timedelta
from decimal import Decimal
from custom_components.target_timeframes.const import CONFIG_TARGET_HOURS_MODE_MAXIMUM, CONFIG_TARGET_HOURS_MODE_MINIMUM
import pytest

from unit import (create_data_source_data, default_time_periods, values_to_thirty_minute_increments)
from custom_components.target_timeframes.entities import calculate_continuous_times, get_fixed_applicable_time_periods, get_start_and_end_times

default_minimum_slot_minutes = 30

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,minimum_slot_minutes,find_last_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
])
async def test_when_continuous_times_present_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, minimum_slot_minutes, find_last_rates):
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_values = [0.1, 0.2, 0.3, 0.2, 0.2, 0.1]

  values = create_data_source_data(
    period_from,
    period_to,
    expected_values
  )
  
  # Restrict our time block
  target_hours = 1

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
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

  assert result[1]["start"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["end"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value"] == 0.1

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,minimum_slot_minutes,find_last_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  # # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, True),
])
async def test_when_continuous_times_present_and_highest_price_required_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, minimum_slot_minutes, find_last_rates):
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

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
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
  assert result[0]["value"] == 0.2

  assert result[1]["start"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["end"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value"] == 0.3

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,minimum_slot_minutes",[
  (datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None),
  (datetime.strptime("2023-01-01T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None),
  (datetime.strptime("2023-01-01T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30),
  (datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, None, 30),

  (datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None),
  (datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None),
  (datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30),
  (datetime.strptime("2023-01-01T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30),
  (datetime.strptime("2023-01-01T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", None, 30),

  (datetime.strptime("2023-01-01T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None),
  (datetime.strptime("2023-01-02T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None),
  (datetime.strptime("2023-01-02T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-02T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30),
  (datetime.strptime("2023-01-02T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", None, 30),
])
async def test_readme_examples(current_date, target_start_time, target_end_time, expected_first_valid_from, minimum_slot_minutes):
  # Arrange
  values = values_to_thirty_minute_increments(
    [
      {
        "value": 6,
        "start": "2023-01-01T00:00:00Z",
        "end": "2023-01-01T00:30:00Z"
      },
      {
        "value": 12,
        "start": "2023-01-01T00:30:00Z",
        "end": "2023-01-01T05:00:00Z"
      },
      {
        "value": 7,
        "start": "2023-01-01T05:00:00Z",
        "end": "2023-01-01T05:30:00Z"
      },
      {
        "value": 20,
        "start": "2023-01-01T05:30:00Z",
        "end": "2023-01-01T18:00:00Z"
      },
      {
        "value": 34,
        "start": "2023-01-01T18:00:00Z",
        "end": "2023-01-01T23:30:00Z"
      },
      {
        "value": 5,
        "start": "2023-01-01T23:30:00Z",
        "end": "2023-01-02T00:30:00Z"
      },
      {
        "value": 12,
        "start": "2023-01-02T00:30:00Z",
        "end": "2023-01-02T05:00:00Z"
      },
      {
        "value": 7,
        "start": "2023-01-02T05:00:00Z",
        "end": "2023-01-02T05:30:00Z"
      },
      {
        "value": 20,
        "start": "2023-01-02T05:30:00Z",
        "end": "2023-01-02T18:00:00Z"
      },
      {
        "value": 34,
        "start": "2023-01-02T18:00:00Z",
        "end": "2023-01-02T23:30:00Z"
      },
      {
        "value": 6,
        "start": "2023-01-02T23:30:00Z",
        "end": "2023-01-03T00:00:00Z"
      },
    ],
    datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  
  # Restrict our time block
  target_hours = 1

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    target_hours,
  )

  # Assert
  assert result is not None

  if (expected_first_valid_from is None):
    assert len(result) == 0
  else:
    assert len(result) == 2
    assert result[0]["start"] == expected_first_valid_from
    assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
    assert result[1]["start"] == expected_first_valid_from + timedelta(minutes=30)
    assert result[1]["end"] == expected_first_valid_from + timedelta(minutes=60)

@pytest.mark.asyncio
async def test_when_applicable_time_periods_is_none_then_no_continuous_times_returned():
  # Arrange
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    None,
    target_hours
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_last_rate_is_currently_active_and_target_is_rolling_then_rates_are_not_reevaluated():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"

  expected_first_valid_from = datetime.strptime("2022-10-22T12:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 0.5

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    default_time_periods
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    target_hours,
    False,
    True
  )

  # Assert
  assert result is not None
  assert len(result) == 1
  assert result[0]["start"] == expected_first_valid_from
  assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value"] == 18.081

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_then_no_times_are_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 3

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, None)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    default_time_periods
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    target_hours
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("target_hours,expected_first_valid_from,expected_values",[
  (0.5, datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [19.1]),
  (1, datetime.strptime("2022-10-22T09:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [20, 19.1]),
])
async def test_when_min_value_is_provided_then_result_does_not_include_any_rate_below_min_value(target_hours: float, expected_first_valid_from: datetime, expected_values: list):
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  min_value = 19

  values = create_data_source_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.1, 20]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    target_hours,
    False,
    False,
    min_value
  )

  # Assert
  assert result is not None
  assert len(result) == len(expected_values)

  expected_from = expected_first_valid_from
  for index in range(0, len(expected_values)):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value"] == expected_values[index]

@pytest.mark.asyncio
@pytest.mark.parametrize("target_hours,expected_first_valid_from,expected_values",[
  (0.5, datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [19.1]),
  (1, datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [19.1, 18.9]),
])
async def test_when_max_value_is_provided_then_result_does_not_include_any_rate_above_max_value(target_hours: float, expected_first_valid_from: datetime, expected_values: list):
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  max_value = 19.9

  values = create_data_source_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.1, 20]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    target_hours,
    True,
    False,
    None,
    max_value
  )

  # Assert
  assert result is not None
  assert len(result) == len(expected_values)

  expected_from = expected_first_valid_from
  for index in range(0, len(expected_values)):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value"] == expected_values[index]

@pytest.mark.asyncio
@pytest.mark.parametrize("weighting,possible_values,expected_first_valid_from,expected_values",[
  ([1, 2, 1], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T11:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [19.1, 15.1, 20]),
  ([1, 2, 2], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [18.9, 19.1, 15.1]),
  ([1, 0, 0], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T11:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [15.1, 20, 19.1]),
  
  ([Decimal('1.1'), Decimal('2.2'), Decimal('1.1')], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T11:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [19.1, 15.1, 20]),
  ([Decimal('1.1'), Decimal('2.2'), Decimal('2.2')], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [18.9, 19.1, 15.1]),
  ([Decimal('1.1'), Decimal('0.0'), Decimal('0.0')], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T11:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [15.1, 20, 19.1]),

  # Examples defined in https://github.com/BottlecapDave/homeassistant-targettimeframes/issues/807
  (None, [14, 14, 10, 7, 15, 21], datetime.strptime("2022-10-22T09:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [14, 10, 7]),
  ([1, 1, 2], [14, 14, 10, 7, 15, 21], datetime.strptime("2022-10-22T09:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [14, 10, 7]),
  ([5, 1, 1], [14, 14, 10, 7, 15, 21], datetime.strptime("2022-10-22T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [7, 15, 21]),

  ([Decimal('1.1'), Decimal('1.1'), Decimal('2.2')], [14, 14, 10, 7, 15, 21], datetime.strptime("2022-10-22T09:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [14, 10, 7]),
  ([Decimal('5.5'), Decimal('1.1'), Decimal('1.1')], [14, 14, 10, 7, 15, 21], datetime.strptime("2022-10-22T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [7, 15, 21]),
])
async def test_when_weighting_specified_then_result_is_adjusted(weighting: list, possible_values: list, expected_first_valid_from: datetime, expected_values: list):
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"

  values = create_data_source_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_values
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    1.5,
    False,
    False,
    None,
    weighting=weighting
  )

  # Assert
  assert result is not None
  assert len(result) == len(expected_values)

  expected_from = expected_first_valid_from
  for index in range(0, len(expected_values)):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value"] == expected_values[index]

@pytest.mark.asyncio
@pytest.mark.parametrize("weighting",[
  (None),
  ([]),
])
async def test_when_target_hours_zero_then_result_is_adjusted(weighting):
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"

  values = create_data_source_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.1, 15.1, 20]
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    0,
    False,
    False,
    None,
    weighting=weighting
  )

  # Assert
  assert result is not None
  assert len(result) == 0

def test_when_hour_mode_is_maximum_and_not_enough_hours_available_then_reduced_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  possible_values = [19.1, 18.9, 21.1, 15.1, 20]
  expected_values = [19.1, 18.9]

  values = create_data_source_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_values
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    1.5,
    False,
    False,
    max_value=19.9,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MAXIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 2

  expected_from = datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 2):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value"] == expected_values[index]

def test_when_hour_mode_is_maximum_and_more_than_enough_hours_available_then_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  possible_values = [19.1, 18.9, 19.1, 15.1, 20]
  expected_values = [18.9, 19.1, 15.1]

  values = create_data_source_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_values
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    1.5,
    False,
    False,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MAXIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 3

  expected_from = datetime.strptime("2022-10-22T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 3):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value"] == expected_values[index]

def test_when_hour_mode_is_minimum_and_not_enough_hours_available_then_no_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  possible_values = [19.1, 18.9, 21.1, 15.1, 20]

  values = create_data_source_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_values
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    1.5,
    False,
    False,
    max_value=0.199,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MINIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 0

def test_when_hour_mode_is_minimum_and_more_than_enough_hours_available_then_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  possible_values = [19.1, 18.9, 19.1, 15.1, 20]
  expected_values = [19.1, 18.9, 19.1, 15.1]

  values = create_data_source_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_values
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  applicable_time_periods = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values
  )

  # Act
  result = calculate_continuous_times(
    applicable_time_periods,
    1.5,
    False,
    False,
    max_value=19.9,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MINIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 4

  expected_from = datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 3):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value"] == expected_values[index]

def test_when_multiple_blocks_have_same_value_then_earliest_is_picked():
  applicable_time_periods = [
    {
        "value": 23.9295,
        "start": datetime.strptime("2024-09-04T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 24.36,
        "start": datetime.strptime("2024-09-04T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 37.464,
        "start": datetime.strptime("2024-09-04T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 37.2435,
        "start": datetime.strptime("2024-09-04T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 39.333,
        "start": datetime.strptime("2024-09-04T16:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 36.687,
        "start": datetime.strptime("2024-09-04T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T16:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 34.1565,
        "start": datetime.strptime("2024-09-04T15:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 32.949,
        "start": datetime.strptime("2024-09-04T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T15:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 18.837,
        "start": datetime.strptime("2024-09-04T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 18.186,
        "start": datetime.strptime("2024-09-04T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 17.3355,
        "start": datetime.strptime("2024-09-04T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8,
        "start": datetime.strptime("2024-09-04T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 17.283,
        "start": datetime.strptime("2024-09-04T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 17.115,
        "start": datetime.strptime("2024-09-04T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 18.417,
        "start": datetime.strptime("2024-09-04T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 21.168,
        "start": datetime.strptime("2024-09-04T08:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 22.05,
        "start": datetime.strptime("2024-09-04T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T08:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 23.373,
        "start": datetime.strptime("2024-09-04T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 22.974,
        "start": datetime.strptime("2024-09-04T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 25.3995,
        "start": datetime.strptime("2024-09-04T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 22.932,
        "start": datetime.strptime("2024-09-04T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 23.31,
        "start": datetime.strptime("2024-09-04T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 20.727,
        "start": datetime.strptime("2024-09-04T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 18.3015,
        "start": datetime.strptime("2024-09-04T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 18.543,
        "start": datetime.strptime("2024-09-04T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 15.6765,
        "start": datetime.strptime("2024-09-04T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 15.876,
        "start": datetime.strptime("2024-09-04T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T01:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T01:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-04T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 16.8945,
        "start": datetime.strptime("2024-09-03T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-04T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 17.535,
        "start": datetime.strptime("2024-09-03T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 19.6245,
        "start": datetime.strptime("2024-09-03T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 19.6245,
        "start": datetime.strptime("2024-09-03T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 18.438,
        "start": datetime.strptime("2024-09-03T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 21.2205,
        "start": datetime.strptime("2024-09-03T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 22.2285,
        "start": datetime.strptime("2024-09-03T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 25.032,
        "start": datetime.strptime("2024-09-03T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 25.578,
        "start": datetime.strptime("2024-09-03T19:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value": 27.1215,
        "start": datetime.strptime("2024-09-03T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2024-09-03T19:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    }
  ]
  
  applicable_time_periods.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))
  
  result = calculate_continuous_times(
    applicable_time_periods,
    3,
    False,
    False
  )

  assert result is not None
  assert len(result) == 6

  current_start = datetime.strptime("2024-09-04T01:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  for rate in result:
    assert rate["start"] == current_start
    current_start = current_start + timedelta(minutes=30)
    assert rate["end"] == current_start


def test_when_weighting_present_with_find_latest_rate_then_latest_time_is_picked():
  applicable_time_periods = create_data_source_data(datetime.strptime("2024-10-10T20:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
                                      datetime.strptime("2024-10-10T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
                                      [2067159])
  applicable_time_periods.extend(create_data_source_data(datetime.strptime("2024-10-10T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
                                           datetime.strptime("2024-10-11T05:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
                                           [70003]))
  applicable_time_periods.extend(create_data_source_data(datetime.strptime("2024-10-11T05:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
                                           datetime.strptime("2024-10-11T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
                                           [2067159]))
  
  applicable_time_periods.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))
  
  result = calculate_continuous_times(
    applicable_time_periods,
    7.5,
    False,
    True,
    weighting=[2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
  )

  assert result is not None
  assert len(result) == 15

  current_start = datetime.strptime("2024-10-10T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  for rate in result:
    assert rate["start"] == current_start
    current_start = current_start + timedelta(minutes=30)
    assert rate["end"] == current_start


def test_when_weighting_present_in_rates_then_weighted_rate_is_picked():
  applicable_time_periods = create_data_source_data(datetime.strptime("2024-10-10T20:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
                                      datetime.strptime("2024-10-10T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
                                      [20])
  
  applicable_time_periods[2]["weighting"] = Decimal(0.5)
  applicable_time_periods[2]["value"] = 0.3
  
  applicable_time_periods[3]["weighting"] = Decimal(0.5)
  applicable_time_periods[3]["value"] = 0.3

  applicable_time_periods[4]["weighting"] = Decimal(0.5)
  applicable_time_periods[4]["value"] = 0.3
  
  applicable_time_periods[5]["weighting"] = Decimal(0.5)
  applicable_time_periods[5]["value"] = 0.3
  
  result = calculate_continuous_times(
    applicable_time_periods,
    1,
    False,
    False
  )

  assert result is not None
  assert len(result) == 2

  current_start = datetime.strptime("2024-10-10T21:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  for rate in result:
    assert rate["start"] == current_start
    current_start = current_start + timedelta(minutes=30)
    assert rate["end"] == current_start