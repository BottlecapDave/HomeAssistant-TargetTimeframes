from datetime import datetime, timedelta
import pytest

from custom_components.target_timeframes.entities import is_target_timeframe_complete_in_period

@pytest.mark.asyncio
async def test_when_both_lists_are_none_then_false_is_returned():
  # Arrange
  current_date = datetime.now()
  start_time = None
  end_time = None
  target_timeframes = None

  # Act
  result = is_target_timeframe_complete_in_period(current_date, start_time, end_time, target_timeframes)

  # Assert
  assert result is False

@pytest.mark.asyncio
async def test_when_target_timeframes_is_empty_then_false_is_returned():
  # Arrange
  current_date = datetime.now()
  start_time = datetime.now()
  end_time =  datetime.now() + timedelta(hours=1)
  target_timeframes = []

  # Act
  result = is_target_timeframe_complete_in_period(current_date, start_time, end_time, target_timeframes)

  # Assert
  assert result is False

@pytest.mark.asyncio
async def test_when_target_timeframe_is_within_applicable_periods_and_complete_then_true_is_returned():
  # Arrange
  current_date = datetime.now()
  start_time = current_date - timedelta(hours=2, minutes=30)
  end_time = current_date
  
  target_timeframes = [
    {"start": start_time, "end": start_time + timedelta(minutes=30)},
    {"start": start_time + timedelta(minutes=30), "end": end_time}
  ]

  # Act
  result = is_target_timeframe_complete_in_period(current_date, start_time, end_time, target_timeframes)

  # Assert
  assert result is True

@pytest.mark.asyncio
async def test_when_target_timeframe_start_before_applicable_periods_then_false_is_returned():
  # Arrange
  current_date = datetime.now()
  start_time = current_date - timedelta(hours=2)
  end_time = current_date - timedelta(minutes=30)
  
  target_timeframes = [
    {"start": start_time - timedelta(minutes=30), "end": start_time + timedelta(minutes=30)},
    {"start": start_time + timedelta(minutes=30), "end": end_time}
  ]

  # Act
  result = is_target_timeframe_complete_in_period(current_date, start_time, end_time, target_timeframes)

  # Assert
  assert result is False

@pytest.mark.asyncio
async def test_when_target_timeframe_end_after_applicable_periods_then_false_is_returned():
  # Arrange
  current_date = datetime.now()
  start_time = current_date - timedelta(hours=2)
  end_time = current_date - timedelta(minutes=30)

  target_timeframes = [
    {"start": start_time, "end": start_time + timedelta(minutes=30)},
    {"start": start_time + timedelta(minutes=30), "end": end_time + timedelta(minutes=30)}
  ]

  # Act
  result = is_target_timeframe_complete_in_period(current_date, start_time, end_time, target_timeframes)

  # Assert
  assert result is False

@pytest.mark.asyncio
async def test_when_target_timeframe_end_not_in_past_then_false_is_returned():
  # Arrange
  current_date = datetime.now()
  start_time = current_date - timedelta(hours=2, minutes=30)
  end_time = current_date + timedelta(hours=1)

  target_timeframes = [
    {"start": start_time, "end": start_time + timedelta(minutes=30)},
    {"start": start_time + timedelta(minutes=30), "end": end_time}
  ]

  # Act
  result = is_target_timeframe_complete_in_period(current_date, start_time, end_time, target_timeframes)

  # Assert
  assert result is False

@pytest.mark.asyncio
async def test_when_target_timeframe_is_exactly_equal_to_applicable_periods_and_complete_then_true_is_returned():
  # Arrange
  current_date = datetime.now()
  start_time = current_date - timedelta(hours=2)
  end_time = current_date - timedelta(minutes=30)
  
  target_timeframes = [
    {"start": start_time, "end": start_time + timedelta(minutes=30)},
    {"start": start_time + timedelta(minutes=30), "end": end_time}
  ]

  # Act
  result = is_target_timeframe_complete_in_period(current_date, start_time, end_time, target_timeframes)

  # Assert
  assert result is True