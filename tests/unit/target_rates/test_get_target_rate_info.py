from datetime import datetime, timedelta
from custom_components.target_timeframes.const import CONFIG_TARGET_HOURS_MODE_MAXIMUM
import pytest

from unit import (create_data_source_data)
from custom_components.target_timeframes.entities import calculate_intermittent_times, get_target_time_period_info
import zoneinfo
from zoneinfo import ZoneInfo

@pytest.mark.asyncio
async def test_when_called_before_rates_then_not_active_returned():
  # Arrange
  values = [
    {
      "start": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 10
    },
    {
      "start": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 5
    },
    {
      "start": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 15
    }
  ]

  current_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  result = get_target_time_period_info(
    current_date,
    values
  )

  # Assert
  assert result is not None
  assert result["is_active"] == False

  assert result["overall_average_value"] == 10
  assert result["overall_min_value"] == 5
  assert result["overall_max_value"] == 15
  
  assert result["current_duration_in_hours"] == 0
  assert result["current_average_value"] == None
  assert result["current_min_value"] == None
  assert result["current_max_value"] == None

  assert result["next_time"] == values[0]["start"]
  assert result["next_duration_in_hours"] == 1
  assert result["next_average_value"] == 7.5
  assert result["next_min_value"] == 5
  assert result["next_max_value"] == 10

@pytest.mark.asyncio
@pytest.mark.parametrize("test",[
    ({
      "current_date": datetime.strptime("2022-02-09T10:15:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_current_duration_in_hours": 1.5,
      "expected_current_average_value": 13.333333333333334,
      "expected_current_min_value": 10,
      "expected_current_max_value": 15,
      "expected_next_duration_in_hours": 1,
      "expected_next_average_value": 12.5,
      "expected_next_min_value": 5,
      "expected_next_max_value": 20,
    }),
    ({
      "current_date": datetime.strptime("2022-02-09T12:35:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": datetime.strptime("2022-02-09T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_current_duration_in_hours": 1,
      "expected_current_average_value": 12.5,
      "expected_current_min_value": 5,
      "expected_current_max_value": 20,
      "expected_next_duration_in_hours": 0.5,
      "expected_next_average_value": 10,
      "expected_next_min_value": 10,
      "expected_next_max_value": 10,
    }),
    ({
      "current_date": datetime.strptime("2022-02-09T14:05:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": None,
      "expected_current_duration_in_hours": 0.5,
      "expected_current_average_value": 10,
      "expected_current_min_value": 10,
      "expected_current_max_value": 10,
      "expected_next_duration_in_hours": 0,
      "expected_next_average_value": None,
      "expected_next_min_value": None,
      "expected_next_max_value": None,
    })
  ])
async def test_when_called_during_rates_then_active_returned(test):
  # Arrange
  values = [
    {
      "start": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 10,
    },
    {
      "start": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 15,
    },
    {
      "start": datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 15,
    },
    {
      "start": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 5,
    },
    {
      "start": datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 20,
    },
    {
      "start": datetime.strptime("2022-02-09T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 10,
    }
  ]

  result = get_target_time_period_info(
    test["current_date"],
    values
  )

  # Assert
  assert result != None
  assert result["is_active"] == True

  assert result["overall_average_value"] == 12.5
  assert result["overall_min_value"] == 5
  assert result["overall_max_value"] == 20
  
  assert result["current_duration_in_hours"] == test["expected_current_duration_in_hours"]
  assert result["current_average_value"] == test["expected_current_average_value"]
  assert result["current_min_value"] == test["expected_current_min_value"]
  assert result["current_max_value"] == test["expected_current_max_value"]

  assert result["next_time"] == test["expected_next_time"]
  assert result["next_duration_in_hours"] == test["expected_next_duration_in_hours"]
  assert result["next_average_value"] == test["expected_next_average_value"]
  assert result["next_min_value"] == test["expected_next_min_value"]
  assert result["next_max_value"] == test["expected_next_max_value"]

@pytest.mark.asyncio
async def test_when_called_after_rates_then_not_active_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_values = [0.1, 0.2]

  values = create_data_source_data(
    period_from,
    period_to,
    expected_values
  )

  current_date = period_to + timedelta(minutes=15)

  # Act
  result = get_target_time_period_info(
    current_date,
    values
  )

  # Assert
  assert result is not None
  assert result["is_active"] == False
  assert result["next_time"] is None

  assert result["overall_average_value"] == 0.15
  assert result["overall_min_value"] == 0.1
  assert result["overall_max_value"] == 0.2

  assert result["current_average_value"] == None
  assert result["current_min_value"] == None
  assert result["current_max_value"] == None

  assert result["next_average_value"] == None
  assert result["next_min_value"] == None
  assert result["next_max_value"] == None

@pytest.mark.asyncio
async def test_when_offset_set_then_active_at_correct_current_time():
  # Arrange
  offset = "-01:00:00"

  values = [
    {
      "start": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 10,
    },
    {
      "start": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 15,
    },
    {
      "start": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value": 5,
    }
  ]

  # Check where we're before the offset
  current_date = datetime.strptime("2022-02-09T08:59:00Z", "%Y-%m-%dT%H:%M:%S%z")

  result = get_target_time_period_info(
    current_date,
    values,
    offset
  )

  assert result is not None
  assert result["is_active"] == False
  assert result["next_time"] == datetime.strptime("2022-02-09T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert result["overall_average_value"] == 10
  assert result["overall_min_value"] == 5
  assert result["overall_max_value"] == 15

  assert result["current_average_value"] == None
  assert result["current_min_value"] == None
  assert result["current_max_value"] == None

  assert result["next_average_value"] == 12.5
  assert result["next_min_value"] == 10
  assert result["next_max_value"] == 15

  # Check where's within our values and our offset
  for minutes_to_add in range(60):
    current_date = values[0]["start"] - timedelta(hours=1) + timedelta(minutes=minutes_to_add)

    result = get_target_time_period_info(
      current_date,
      values,
      offset
    )

    assert result is not None
    assert result["is_active"] == True
    assert result["next_time"] is not None

    assert result["overall_average_value"] == 10
    assert result["overall_min_value"] == 5
    assert result["overall_max_value"] == 15

    assert result["current_average_value"] == 12.5
    assert result["current_min_value"] == 10
    assert result["current_max_value"] == 15

    assert result["next_average_value"] == 5
    assert result["next_min_value"] == 5
    assert result["next_max_value"] == 5

  # Check when within rate but after offset
  current_date = values[0]["start"] + timedelta(minutes=1)

  result = get_target_time_period_info(
    current_date,
    values,
    offset
  )

  assert result is not None
  assert result["is_active"] == False
  assert result["next_time"] == datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert result["overall_average_value"] == 10
  assert result["overall_min_value"] == 5
  assert result["overall_max_value"] == 15

  assert result["current_average_value"] == None
  assert result["current_min_value"] == None
  assert result["current_max_value"] == None

  assert result["next_average_value"] == 5
  assert result["next_min_value"] == 5
  assert result["next_max_value"] == 5

@pytest.mark.asyncio
async def test_when_current_date_is_equal_to_last_end_date_then_not_active():
  # Arrange
  period_from = datetime.strptime("2022-10-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_values = [0.16511, 0.16512, 0.16999]
  values = create_data_source_data(
    period_from,
    period_to,
    expected_values
  )

  current_date = datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  result = get_target_time_period_info(
    current_date,
    values,
    None
  )

  assert result is not None
  assert result["is_active"] == False
  assert result["next_time"] == None

  assert result["overall_average_value"] == 0.16633
  assert result["overall_min_value"] == 0.16511
  assert result["overall_max_value"] == 0.16999

  assert result["current_average_value"] == None
  assert result["current_min_value"] == None
  assert result["current_max_value"] == None

  assert result["next_average_value"] == None
  assert result["next_min_value"] == None
  assert result["next_max_value"] == None

@pytest.mark.asyncio
async def test_when_clocks_go_back_then_correct_result_returned():
  # Arrange
  max_value = 20
  applicable_time_periods = [{'start': datetime(2024, 10, 27, 0, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 0, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 201168}, {'start': datetime(2024, 10, 27, 0, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 1, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.19236}, {'start': datetime(2024, 10, 27, 1, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 1, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.15435}, {'start': datetime(2024, 10, 27, 1, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 1, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 20205}, {'start': datetime(2024, 10, 27, 1, 0, fold=1, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 1, 30, fold=1, tzinfo=ZoneInfo(key='Europe/London')), 'value': 2039925}, {'start': datetime(2024, 10, 27, 1, 30, fold=1, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 2, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.168525}, {'start': datetime(2024, 10, 27, 2, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 2, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.15876}, {'start': datetime(2024, 10, 27, 2, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 3, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.15435}, {'start': datetime(2024, 10, 27, 3, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 3, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.163695}, {'start': datetime(2024, 10, 27, 3, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 4, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.16758}, {'start': datetime(2024, 10, 27, 4, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 4, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.193725}, {'start': datetime(2024, 10, 27, 4, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 5, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 18.963}, {'start': datetime(2024, 10, 27, 5, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 5, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.165375}, {'start': datetime(2024, 10, 27, 5, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 6, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 200811}, {'start': datetime(2024, 10, 27, 6, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 6, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.187425}, {'start': datetime(2024, 10, 27, 6, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 7, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 203373}, {'start': datetime(2024, 10, 27, 7, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 7, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13041, 'is_intelligent_adjusted': True}, {'start': datetime(2024, 10, 27, 7, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 8, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13041, 'is_intelligent_adjusted': True}, {'start': datetime(2024, 10, 27, 8, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 8, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 200181}, {'start': datetime(2024, 10, 27, 8, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 9, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 200202}, {'start': datetime(2024, 10, 27, 9, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 9, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 2005065}, {'start': datetime(2024, 10, 27, 9, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 10, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.19656}, {'start': datetime(2024, 10, 27, 10, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 10, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13041, 'is_intelligent_adjusted': True}, {'start': datetime(2024, 10, 27, 10, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 11, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.165375}, {'start': datetime(2024, 10, 27, 11, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 11, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.165375}, {'start': datetime(2024, 10, 27, 11, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 12, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.17094}, {'start': datetime(2024, 10, 27, 12, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 12, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13041, 'is_intelligent_adjusted': True}, {'start': datetime(2024, 10, 27, 12, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 13, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13041, 'is_intelligent_adjusted': True}, {'start': datetime(2024, 10, 27, 13, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 13, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.187425}, {'start': datetime(2024, 10, 27, 13, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 14, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.175035}, {'start': datetime(2024, 10, 27, 14, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 14, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.165375}, {'start': datetime(2024, 10, 27, 14, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 15, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.183015}, {'start': datetime(2024, 10, 27, 15, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 15, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.16317}, {'start': datetime(2024, 10, 27, 15, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 16, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 2017455}, {'start': datetime(2024, 10, 27, 16, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 16, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.31668}, {'start': datetime(2024, 10, 27, 16, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 17, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.36855}, {'start': datetime(2024, 10, 27, 17, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 17, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.3906}, {'start': datetime(2024, 10, 27, 17, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 18, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.365925}, {'start': datetime(2024, 10, 27, 18, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 18, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13041, 'is_intelligent_adjusted': True}, {'start': datetime(2024, 10, 27, 18, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 19, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.33831}, {'start': datetime(2024, 10, 27, 19, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 19, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13041, 'is_intelligent_adjusted': True}, {'start': datetime(2024, 10, 27, 19, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 20, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13041, 'is_intelligent_adjusted': True}, {'start': datetime(2024, 10, 27, 20, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 20, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 204339}, {'start': datetime(2024, 10, 27, 20, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 21, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.18564}, {'start': datetime(2024, 10, 27, 21, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 21, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 20646}, {'start': datetime(2024, 10, 27, 21, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 22, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.16758}, {'start': datetime(2024, 10, 27, 22, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 22, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 205137}, {'start': datetime(2024, 10, 27, 22, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 23, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.13797}, {'start': datetime(2024, 10, 27, 23, 0, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 27, 23, 30, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.1764}, {'start': datetime(2024, 10, 27, 23, 30, tzinfo=ZoneInfo(key='Europe/London')), 'end': datetime(2024, 10, 28, 0, 0, tzinfo=ZoneInfo(key='Europe/London')), 'value': 0.165375}]
  
  applicable_time_periods.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))

  # Act
  values = calculate_intermittent_times(
    applicable_time_periods,
    12,
    False,
    max_value=max_value,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MAXIMUM
  )

  current_date = datetime(2024, 10, 27, 12, 39, tzinfo=ZoneInfo(key='Europe/London'))

  # Act
  result = get_target_time_period_info(
    current_date,
    values
  )

  # Assert
  assert result is not None
  assert result["is_active"] == True