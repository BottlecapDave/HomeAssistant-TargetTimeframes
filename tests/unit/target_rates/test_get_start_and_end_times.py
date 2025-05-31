from datetime import datetime
import pytest
import logging

from custom_components.target_timeframes.entities import get_start_and_end_times

_LOGGER = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_when_target_times_are_none_and_start_time_not_in_past_is_false_then_returns_full_day():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = None
  target_end_time = None
  start_time_not_in_past = False

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_target_times_are_none_and_start_time_not_in_past_is_true_then_returns_half_day():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = None
  target_end_time = None
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_start_time_provided_and_start_time_not_in_past_is_true_then_returns_specified_times():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = None
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_start_time_provided_and_start_time_not_in_past_is_false_then_returns_specified_times():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = None
  start_time_not_in_past = False

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_end_time_provided_and_start_time_not_in_past_is_true_then_returns_specified_times():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = None
  target_end_time = "18:00"
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-16T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_end_time_provided_and_start_time_not_in_past_is_false_then_returns_specified_times():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = None
  target_end_time = "18:00"
  start_time_not_in_past = False

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-16T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_target_times_provided_and_start_time_not_in_past_is_false_then_returns_specified_times():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "15:00"
  start_time_not_in_past = False

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-16T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_target_times_provided_and_start_time_not_in_past_is_true_then_returns_specified_times():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "15:00"
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-16T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_start_time_after_end_time_and_start_after_current_and_start_time_not_in_past_is_true_then_start_moves_to_previous_day():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "22:00"
  target_end_time = "04:00"
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-17T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_start_time_after_end_time_and_start_before_current_and_start_time_not_in_past_is_false_then_end_moves_to_next_day():
  # Arrange
  current_date = datetime.strptime("2023-11-16T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "22:00"
  target_end_time = "04:00"
  start_time_not_in_past = False

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-17T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_start_time_after_end_time_and_start_before_current_and_start_time_not_in_past_is_true_then_end_moves_to_next_day():
  # Arrange
  current_date = datetime.strptime("2023-11-16T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "22:00"
  target_end_time = "04:00"
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-17T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_rolling_target_and_start_time_in_past_and_end_time_in_future_then_start_becomes_current_time():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "15:00"
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = current_date
  expected_end = datetime.strptime("2023-11-16T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_non_rolling_target_and_start_time_in_past_and_end_time_in_future_then_start_stays_in_past():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "15:00"
  start_time_not_in_past = False

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-16T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_both_start_and_end_times_in_past_then_moves_to_next_day():
  # Arrange
  current_date = datetime.strptime("2023-11-16T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "15:00"
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-17T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-17T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_times_are_same_day_with_current_between_them_and_non_rolling_target():
  # Arrange
  current_date = datetime.strptime("2023-11-16T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "15:00"
  start_time_not_in_past = False

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-16T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end

@pytest.mark.asyncio
async def test_when_current_is_before_both_start_and_end_times_same_day():
  # Arrange
  current_date = datetime.strptime("2023-11-16T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "15:00"
  start_time_not_in_past = True

  # Act
  target_start, target_end = get_start_and_end_times(current_date, target_start_time, target_end_time, start_time_not_in_past)

  # Assert
  expected_start = datetime.strptime("2023-11-16T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = datetime.strptime("2023-11-16T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  assert target_start == expected_start
  assert target_end == expected_end