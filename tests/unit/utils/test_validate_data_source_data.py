from datetime import datetime, timedelta, timezone
import pytest

from custom_components.target_timeframes.utils.data_source_data import validate_data_source_data, DataSourceItem

@pytest.mark.asyncio
async def test_when_none_items_are_provided_then_success_with_empty_data_is_returned():
    # Arrange
    items = None
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == True
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message is None

@pytest.mark.asyncio
async def test_when_empty_list_is_provided_then_success_with_empty_data_is_returned():
    # Arrange
    items = []
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == True
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message is None

@pytest.mark.asyncio
async def test_when_valid_data_with_datetime_objects_is_provided_then_success_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=30)
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5,
            "metadata": {"test": "data"}
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == True
    assert len(result.data) == 1
    assert result.data[0].start == start
    assert result.data[0].end == end
    assert result.data[0].value == 10.5
    assert result.data[0].metadata == {"test": "data"}
    assert result.data_source_id == data_source_id
    assert result.error_message is None

@pytest.mark.asyncio
async def test_when_valid_data_with_iso_string_format_is_provided_then_success_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=30)
    items = [
        {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "value": 10.5,
            "metadata": {"test": "data"}
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == True
    assert len(result.data) == 1
    assert result.data[0].start == start
    assert result.data[0].end == end
    assert result.data[0].value == 10.5
    assert result.data[0].metadata == {"test": "data"}
    assert result.data_source_id == data_source_id
    assert result.error_message is None

@pytest.mark.asyncio
async def test_when_valid_data_without_metadata_is_provided_then_success_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=30)
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == True
    assert len(result.data) == 1
    assert result.data[0].start == start
    assert result.data[0].end == end
    assert result.data[0].value == 10.5
    assert result.data[0].metadata is None
    assert result.data_source_id == data_source_id
    assert result.error_message is None

@pytest.mark.asyncio
async def test_when_multiple_valid_items_are_provided_then_success_is_returned():
    # Arrange
    start1 = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end1 = start1 + timedelta(minutes=30)
    start2 = datetime(2024, 1, 1, 12, 30, 0, 0, tzinfo=timezone.utc)
    end2 = start2 + timedelta(minutes=30)
    items = [
        {
            "start": start1,
            "end": end1,
            "value": 10.5,
            "metadata": {"test": "data1"}
        },
        {
            "start": start2,
            "end": end2,
            "value": 20.5,
            "metadata": {"test": "data2"}
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == True
    assert len(result.data) == 2
    assert result.data[0].start == start1
    assert result.data[1].start == start2
    assert result.data_source_id == data_source_id
    assert result.error_message is None

@pytest.mark.asyncio
async def test_when_start_is_missing_then_error_is_returned():
    # Arrange
    end = datetime(2024, 1, 1, 12, 30, 0, 0, tzinfo=timezone.utc)
    items = [
        {
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start is missing at index 0"

@pytest.mark.asyncio
async def test_when_end_is_missing_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    items = [
        {
            "start": start,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "end is missing at index 0"

@pytest.mark.asyncio
async def test_when_start_is_invalid_iso_format_then_error_is_returned():
    # Arrange
    end = datetime(2024, 1, 1, 12, 30, 0, 0, tzinfo=timezone.utc)
    items = [
        {
            "start": "invalid-date",
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start was not a valid ISO datetime in string format at index 0"

@pytest.mark.asyncio
async def test_when_end_is_invalid_iso_format_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    items = [
        {
            "start": start,
            "end": "invalid-date",
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "end was not a valid ISO datetime in string format at index 0"

@pytest.mark.asyncio
async def test_when_start_has_no_timezone_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0)  # No timezone
    end = datetime(2024, 1, 1, 12, 30, 0, 0, tzinfo=timezone.utc)
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start must include timezone at index 0"

@pytest.mark.asyncio
async def test_when_end_has_no_timezone_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 1, 1, 12, 30, 0, 0)  # No timezone
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "end must include timezone at index 0"

@pytest.mark.asyncio
async def test_when_start_equals_end_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = start
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start must be before end at index 0"

@pytest.mark.asyncio
async def test_when_start_is_after_end_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 30, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start must be before end at index 0"

@pytest.mark.asyncio
async def test_when_time_period_is_not_30_minutes_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=60)  # 60 minutes instead of 30
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "time period must be equal to 30 minutes at index 0"

@pytest.mark.asyncio
async def test_when_start_minute_is_not_0_or_30_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 15, 0, 0, tzinfo=timezone.utc)  # 15 minutes
    end = start + timedelta(minutes=30)
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start minute must equal 0 or 30 at index 0"

@pytest.mark.asyncio
async def test_when_start_second_is_not_0_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 5, 0, tzinfo=timezone.utc)  # 5 seconds
    end = start + timedelta(minutes=30)
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start second and microsecond must equal 0 at index 0"

@pytest.mark.asyncio
async def test_when_start_microsecond_is_not_0_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 1000, tzinfo=timezone.utc)  # 1000 microseconds
    end = start + timedelta(minutes=30)
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start second and microsecond must equal 0 at index 0"

@pytest.mark.asyncio
async def test_when_end_second_is_not_0_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 5, 0, tzinfo=timezone.utc)
    end = datetime(2024, 1, 1, 12, 30, 5, 0, tzinfo=timezone.utc)  # 5 seconds
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start second and microsecond must equal 0 at index 0"

@pytest.mark.asyncio
async def test_when_end_microsecond_is_not_0_then_error_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 1, 1, 12, 30, 0, 1000, tzinfo=timezone.utc)  # 1000 microseconds
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "end second and microsecond must equal 0 at index 0"

@pytest.mark.asyncio
async def test_when_error_occurs_at_second_item_then_correct_index_is_reported():
    # Arrange
    start1 = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    end1 = start1 + timedelta(minutes=30)
    start2 = datetime(2024, 1, 1, 12, 15, 0, 0, tzinfo=timezone.utc)  # Invalid minute: 15
    end2 = start2 + timedelta(minutes=30)
    items = [
        {
            "start": start1,
            "end": end1,
            "value": 10.5
        },
        {
            "start": start2,
            "end": end2,
            "value": 20.5
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == False
    assert result.data == []
    assert result.data_source_id == data_source_id
    assert result.error_message == "start minute must equal 0 or 30 at index 1"

@pytest.mark.asyncio
async def test_when_valid_data_with_30_minute_start_is_provided_then_success_is_returned():
    # Arrange
    start = datetime(2024, 1, 1, 12, 30, 0, 0, tzinfo=timezone.utc)  # 30 minutes
    end = datetime(2024, 1, 1, 13, 0, 0, 0, tzinfo=timezone.utc)  # 0 minutes
    items = [
        {
            "start": start,
            "end": end,
            "value": 10.5,
            "metadata": {"test": "data"}
        }
    ]
    data_source_id = "test_source"

    # Act
    result = validate_data_source_data(items, data_source_id)

    # Assert
    assert result.success == True
    assert len(result.data) == 1
    assert result.data[0].start == start
    assert result.data[0].end == end
    assert result.data_source_id == data_source_id
    assert result.error_message is None
