from datetime import datetime, timedelta
import pytest

from custom_components.target_timeframes.entities import get_fixed_applicable_time_periods, get_start_and_end_times
from unit import create_data_source_data, default_time_periods, values_to_thirty_minute_increments

default_minimum_slot_minutes = 30

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,minimum_slot_minutes,expected_number_of_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 16),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 12),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 16),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 16),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 16),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 16),
  
  # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 36),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 12),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 36),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 36),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 36),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 36),
  
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 28),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 24),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 28),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 28),
  
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 48),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 30, 24),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 48),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, 48),
])
async def test_when_continuous_times_present_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, minimum_slot_minutes, expected_number_of_rates):
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_values = [0.1, 20, 0.3, 20, 20, 0.1]
  calculate_with_incomplete_data = False

  values = create_data_source_data(
    period_from,
    period_to,
    expected_values
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, minimum_slot_minutes)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values,
    calculate_with_incomplete_data
  )

  assert result is not None

  assert len(result) == expected_number_of_rates
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "20:00"
  target_end_time = "09:00"
  calculate_with_incomplete_data = False

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, None)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    default_time_periods,
    calculate_with_incomplete_data
  )

  # Assert
  assert result is not None
  assert len(result) == 26

  expected_first_valid_from = current_date.replace(hour=20, minute=0)
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T17:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  calculate_with_incomplete_data = False

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, None)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    default_time_periods,
    calculate_with_incomplete_data
  )

  # Assert
  assert result is not None
  expected_first_valid_from = current_date.replace(hour=16, minute=0)
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_and_rolling_target_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "22:00"
  target_end_time = "01:00"
  calculate_with_incomplete_data = False

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

  values = values_to_thirty_minute_increments(
    [
      {
        "value": 15.1,
        "start": "2022-10-21T00:00:00Z",
        "end": "2022-10-21T22:00:00Z"
      },
      {
        "value": 16.1,
        "start": "2022-10-21T22:00:00Z",
        "end": "2022-10-22T02:00:00Z"
      },
      {
        "value": 15.1,
        "start": "2022-10-22T02:00:00Z",
        "end": "2022-10-22T05:00:00Z"
      },
    ],
    datetime.strptime("2022-10-21T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values,
    calculate_with_incomplete_data
  )

  # Assert
  assert result is not None
  assert len(result) == 3
  expected_first_valid_from = current_date.replace(hour=23, minute=30)
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_and_rolling_target_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  calculate_with_incomplete_data = False

  expected_first_valid_from = datetime.strptime("2022-10-22T02:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

  values = values_to_thirty_minute_increments(
    [
      {
        "value": 15.1,
        "start": "2022-10-21T00:00:00Z",
        "end": "2022-10-21T22:00:00Z"
      },
      {
        "value": 16.1,
        "start": "2022-10-21T22:00:00Z",
        "end": "2022-10-22T02:00:00Z"
      },
      {
        "value": 15.1,
        "start": "2022-10-22T02:00:00Z",
        "end": "2022-10-22T05:00:00Z"
      },
      {
        "value": 16.1,
        "start": "2022-10-22T05:00:00Z",
        "end": "2022-10-23T00:00:00Z"
      },
    ],
    datetime.strptime("2022-10-21T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, default_minimum_slot_minutes)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values,
    calculate_with_incomplete_data
  )

  # Assert
  assert result is not None
  assert len(result) == 33
  
  expected_first_valid_from = current_date.replace(hour=23, minute=30)
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_then_no_times_are_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  calculate_with_incomplete_data = False

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, None)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    default_time_periods,
    calculate_with_incomplete_data
  )

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_and_incomplete_data_is_true_then_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  calculate_with_incomplete_data = True

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, None)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    default_time_periods,
    calculate_with_incomplete_data
  )

  # Assert
  assert result is not None
  assert len(result) == 14
  expected_first_valid_from = datetime.strptime("2022-10-22T16:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_times_are_in_bst_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2024-04-06T17:10:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "21:00"
  calculate_with_incomplete_data = False

  period_from = datetime.strptime("2024-04-06T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2024-04-07T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_values = [0.1, 20, 0.3, 20, 20, 0.1]

  values = create_data_source_data(
    period_from,
    period_to,
    expected_values
  )

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, None)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values,
    calculate_with_incomplete_data
  )

  # Assert
  assert result is not None
  assert len(result) == 10
  expected_first_valid_from = datetime.strptime("2024-04-06T15:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

  assert expected_first_valid_from == datetime.strptime("2024-04-06T20:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_clocks_go_back_then_correct_times_are_selected():
  # Arrange
  current_date = datetime.strptime("2024-10-27T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "23:00"
  target_end_time = "23:00"
  calculate_with_incomplete_data = False

  values = [
    {
      "value": 13.797,
      "start": datetime.strptime("2024-10-27T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 25.137,
      "start": datetime.strptime("2024-10-27T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.758,
      "start": datetime.strptime("2024-10-27T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 26.46,
      "start": datetime.strptime("2024-10-27T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 18.564,
      "start": datetime.strptime("2024-10-27T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 24.339,
      "start": datetime.strptime("2024-10-27T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 19.761,
      "start": datetime.strptime("2024-10-27T19:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 19.971,
      "start": datetime.strptime("2024-10-27T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T19:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 33.831,
      "start": datetime.strptime("2024-10-27T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 39.417,
      "start": datetime.strptime("2024-10-27T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 36.5925,
      "start": datetime.strptime("2024-10-27T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 39.06,
      "start": datetime.strptime("2024-10-27T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 36.855,
      "start": datetime.strptime("2024-10-27T16:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 31.668,
      "start": datetime.strptime("2024-10-27T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T16:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 21.7455,
      "start": datetime.strptime("2024-10-27T15:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.317,
      "start": datetime.strptime("2024-10-27T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T15:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 18.3015,
      "start": datetime.strptime("2024-10-27T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 17.5035,
      "start": datetime.strptime("2024-10-27T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 18.7425,
      "start": datetime.strptime("2024-10-27T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.4745,
      "start": datetime.strptime("2024-10-27T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 17.094,
      "start": datetime.strptime("2024-10-27T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 17.6085,
      "start": datetime.strptime("2024-10-27T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 19.656,
      "start": datetime.strptime("2024-10-27T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 20.5065,
      "start": datetime.strptime("2024-10-27T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 22002,
      "start": datetime.strptime("2024-10-27T08:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 20.181,
      "start": datetime.strptime("2024-10-27T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T08:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 19.5825,
      "start": datetime.strptime("2024-10-27T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 19.845,
      "start": datetime.strptime("2024-10-27T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 23.373,
      "start": datetime.strptime("2024-10-27T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 18.7425,
      "start": datetime.strptime("2024-10-27T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 20.811,
      "start": datetime.strptime("2024-10-27T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.5375,
      "start": datetime.strptime("2024-10-27T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 18.963,
      "start": datetime.strptime("2024-10-27T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 19.3725,
      "start": datetime.strptime("2024-10-27T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.758,
      "start": datetime.strptime("2024-10-27T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.3695,
      "start": datetime.strptime("2024-10-27T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 15.435,
      "start": datetime.strptime("2024-10-27T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 15.876,
      "start": datetime.strptime("2024-10-27T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 16.8525,
      "start": datetime.strptime("2024-10-27T01:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 23.9925,
      "start": datetime.strptime("2024-10-27T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T01:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 22.05,
      "start": datetime.strptime("2024-10-27T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 15.435,
      "start": datetime.strptime("2024-10-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 19.236,
      "start": datetime.strptime("2024-10-26T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 21.168,
      "start": datetime.strptime("2024-10-26T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
      "end": datetime.strptime("2024-10-26T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 28.665,
      "start": datetime.strptime("2024-10-26T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2024-10-26T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "value": 19.383,
      "start": datetime.strptime("2024-10-26T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2024-10-26T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
  ]
  
  values.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))

  (target_start_datetime, target_end_datetime) = get_start_and_end_times(current_date, target_start_time, target_end_time, None)

  # Act
  result = get_fixed_applicable_time_periods(
    target_start_datetime,
    target_end_datetime,
    values,
    calculate_with_incomplete_data
  )

  # Assert
  assert result is not None
  assert len(result) == 48

  current_start = datetime.strptime("2024-10-26T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  for rate in result:
    assert rate["start"] == current_start
    current_start += timedelta(minutes=30)
    assert rate["end"] == current_start