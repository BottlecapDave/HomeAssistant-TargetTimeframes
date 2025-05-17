from datetime import datetime, timedelta, timezone
import pytest

from custom_components.target_timeframes.utils.data_source_data import merge_data_source_data, DataSourceItem

@pytest.mark.asyncio
async def test_when_empty_lists_are_provided_then_empty_list_is_returned():
    # Arrange
    current = datetime.now(timezone.utc)
    new_data = []
    current_data = []

    # Act
    result = merge_data_source_data(current, new_data, current_data)

    # Assert
    assert result == []

@pytest.mark.asyncio
async def test_when_only_new_data_is_provided_then_only_new_data_is_returned():
    # Arrange
    current = datetime.now(timezone.utc)
    
    start1 = current.replace(minute=0, second=0, microsecond=0)
    end1 = start1 + timedelta(minutes=30)
    item1 = DataSourceItem(start=start1, end=end1, value=1.0, metadata=None)
    
    start2 = end1
    end2 = start2 + timedelta(minutes=30)
    item2 = DataSourceItem(start=start2, end=end2, value=2.0, metadata=None)
    
    new_data = [item1, item2]
    current_data = []

    # Act
    result = merge_data_source_data(current, new_data, current_data)

    # Assert
    assert len(result) == 2
    assert result[0] == item1
    assert result[1] == item2

@pytest.mark.asyncio
async def test_when_only_current_data_is_provided_then_only_current_data_is_returned():
    # Arrange
    current = datetime.now(timezone.utc)
    
    start1 = current.replace(minute=0, second=0, microsecond=0)
    end1 = start1 + timedelta(minutes=30)
    item1 = DataSourceItem(start=start1, end=end1, value=1.0, metadata=None)
    
    start2 = end1
    end2 = start2 + timedelta(minutes=30)
    item2 = DataSourceItem(start=start2, end=end2, value=2.0, metadata=None)
    
    new_data = []
    current_data = [item1, item2]

    # Act
    result = merge_data_source_data(current, new_data, current_data)

    # Assert
    assert len(result) == 2
    assert result[0] == item1
    assert result[1] == item2

@pytest.mark.asyncio
async def test_when_data_older_than_one_day_is_provided_then_it_is_filtered_out():
    # Arrange
    current = datetime.now(timezone.utc)
    earliest_item = current.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    
    # Recent item (should be included)
    start1 = current - timedelta(hours=2)
    start1 = start1.replace(minute=0, second=0, microsecond=0)
    end1 = start1 + timedelta(minutes=30)
    item1 = DataSourceItem(start=start1, end=end1, value=1.0, metadata=None)
    
    # Old item (should be filtered out)
    start_old = earliest_item - timedelta(hours=2)
    end_old = start_old + timedelta(minutes=30)
    item_old = DataSourceItem(start=start_old, end=end_old, value=3.0, metadata=None)
    
    new_data = []
    current_data = [item1, item_old]

    # Act
    result = merge_data_source_data(current, new_data, current_data)

    # Assert
    assert len(result) == 1
    assert result[0] == item1

@pytest.mark.asyncio
async def test_when_duplicate_items_exist_then_only_one_is_included():
    # Arrange
    current = datetime.now(timezone.utc)
    
    start1 = current.replace(minute=0, second=0, microsecond=0)
    end1 = start1 + timedelta(minutes=30)
    item1 = DataSourceItem(start=start1, end=end1, value=1.0, metadata=None)
    
    # Same time period but from current_data
    duplicate_item = DataSourceItem(start=start1, end=end1, value=3.0, metadata=None)
    
    start2 = end1
    end2 = start2 + timedelta(minutes=30)
    item2 = DataSourceItem(start=start2, end=end2, value=2.0, metadata=None)
    
    new_data = [item1, item2]
    current_data = [duplicate_item]

    # Act
    result = merge_data_source_data(current, new_data, current_data)

    # Assert
    assert len(result) == 2
    assert result[0] == item1  # The duplicate from new_data takes precedence
    assert result[1] == item2

@pytest.mark.asyncio
async def test_when_mixed_data_is_provided_then_result_is_sorted_by_start_time():
    # Arrange
    current = datetime.now(timezone.utc)
    
    # Item from new_data
    start1 = current + timedelta(hours=2)
    start1 = start1.replace(minute=0, second=0, microsecond=0)
    end1 = start1 + timedelta(minutes=30)
    item1 = DataSourceItem(start=start1, end=end1, value=1.0, metadata=None)
    
    # Earlier item from current_data
    start2 = current - timedelta(hours=1)
    start2 = start2.replace(minute=0, second=0, microsecond=0)
    end2 = start2 + timedelta(minutes=30)
    item2 = DataSourceItem(start=start2, end=end2, value=2.0, metadata=None)
    
    new_data = [item1]
    current_data = [item2]

    # Act
    result = merge_data_source_data(current, new_data, current_data)

    # Assert
    assert len(result) == 2
    assert result[0] == item2  # Earlier item should be first
    assert result[1] == item1

@pytest.mark.asyncio
async def test_when_current_data_is_none_then_only_new_data_is_returned():
    # Arrange
    current = datetime.now(timezone.utc)
    
    start1 = current.replace(minute=0, second=0, microsecond=0)
    end1 = start1 + timedelta(minutes=30)
    item1 = DataSourceItem(start=start1, end=end1, value=1.0, metadata=None)
    
    new_data = [item1]
    current_data = None

    # Act
    result = merge_data_source_data(current, new_data, current_data)

    # Assert
    assert len(result) == 1
    assert result[0] == item1