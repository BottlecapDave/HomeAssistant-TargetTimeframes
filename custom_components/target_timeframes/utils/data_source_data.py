from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel

class DataSourceItem(BaseModel):
  start: datetime
  end: datetime
  value: float
  metadata: Any

class ValidateDataSourceDataResult:

  def __init__(self, success: bool, data_source_id: str, data: list[DataSourceItem] = [], error_message: str | None = None):
    self.success = success
    self.data = data
    self.data_source_id = data_source_id
    self.error_message = error_message

def validate_data_source_data(items: list[dict], data_source_id: str):
  if items is None or len(items) < 1:
    return ValidateDataSourceDataResult(True, [])
  
  processed_data_source = []
  for index in range(len(items)):
    item = items[index]
    error = None

    start = None
    try:
      start = datetime.fromisoformat(item["start"])
    except:
      error = f"start was not a valid ISO datetime in string format at index {index}"
      break

    if start.tzinfo is None:
      error = f"start must include timezone at index {index}"
      break

    end = None
    try:
      end = datetime.fromisoformat(item["end"])
    except:
      error = f"end was not a valid ISO datetime in string format at index {index}"
      break

    if end.tzinfo is None:
      error = f"end must include timezone at index {index}"
      break

    if start >= end:
      error = f"start must be before end at index {index}"
      break

    if (end - start).seconds != 1800: # 30 minutes
      error = f"time period must be equal to 30 minutes at index {index}"
      break

    error = _validate_time(start, "start", index)
    if error is not None:
      break

    error = _validate_time(end, "end", index)
    if error is not None:
      break

    processed_data_source.append(DataSourceItem(start=start, end=end, value=item["value"], metadata=item["metadata"] if "metadata" in item else None))

  if error is not None:
    return ValidateDataSourceDataResult(False, data_source_id, [], error)

  return ValidateDataSourceDataResult(True, data_source_id, processed_data_source)

def _validate_time(value: datetime, key: str, index: int):
  if value.minute != 0 and value.minute != 30:
    return f"{key} minute must equal 0 or 30 at index {index}"
  
  if value.second != 0 or value.microsecond != 0:
    return f"{key} second and microsecond must equal 0 at index {index}"
  
  return None

def merge_data_source_data(current: datetime, new_data: list[DataSourceItem], current_data: list[DataSourceItem]):
  merged_data: list[DataSourceItem] = []
  merged_data.extend(new_data)
  earliest_item = current.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)

  if current_data is not None:
    for item in current_data:
      if item.end <= earliest_item:
        continue

      exists = False
      for merged_item in merged_data:
        if merged_item.start == item.start and merged_item.end == item.end:
          exists = True
          break

      if exists == False:
        merged_data.append(item)

  merged_data.sort(key=lambda x: x.start)
  return merged_data