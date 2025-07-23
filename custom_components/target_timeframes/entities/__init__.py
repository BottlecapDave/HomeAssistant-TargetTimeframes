from datetime import datetime, timedelta
from decimal import Decimal
import math
import re
import logging

from homeassistant.util.dt import (as_utc, parse_datetime)

from ..const import CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS, CONFIG_TARGET_HOURS_MODE_EXACT, CONFIG_TARGET_HOURS_MODE_MAXIMUM, CONFIG_TARGET_HOURS_MODE_MINIMUM, CONFIG_TARGET_KEYS, REGEX_OFFSET_PARTS, REGEX_WEIGHTING

_LOGGER = logging.getLogger(__name__)

def extract_config(config: dict, keys: list[str]):
  new_config = {}
  for key in config.keys():
    if key in keys:
      new_config[key] = config[key]

  return new_config

def apply_offset(date_time: datetime, offset: str, inverse = False):
  matches = re.search(REGEX_OFFSET_PARTS, offset)
  if matches == None:
    raise Exception(f'Unable to extract offset: {offset}')

  symbol = matches[1]
  hours = float(matches[2])
  minutes = float(matches[3])
  seconds = float(matches[4])

  if ((symbol == "-" and inverse == False) or (symbol != "-" and inverse == True)):
    return date_time - timedelta(hours=hours, minutes=minutes, seconds=seconds)
  
  return date_time + timedelta(hours=hours, minutes=minutes, seconds=seconds)

def is_target_timeframe_complete_in_period(current_date: datetime, start_time: datetime, end_time: datetime, target_timeframes: list | None, context: str = None):
  if target_timeframes is None or len(target_timeframes) < 1:
    return False
  
  return (
    start_time <= target_timeframes[0]["start"] and 
    end_time >= target_timeframes[-1]["end"] and
    target_timeframes[-1]["end"] <= current_date
  )

def get_start_and_end_times(current_date: datetime, target_start_time: str, target_end_time: str, start_time_not_in_past = True, context: str = None):
  if (target_start_time is not None):
    target_start = parse_datetime(current_date.strftime(f"%Y-%m-%dT{target_start_time}:00%z"))
  else:
    target_start = parse_datetime(current_date.strftime(f"%Y-%m-%dT00:00:00%z"))

  if (target_end_time is not None):
    target_end = parse_datetime(current_date.strftime(f"%Y-%m-%dT{target_end_time}:00%z"))
  else:
    target_end = parse_datetime(current_date.strftime(f"%Y-%m-%dT00:00:00%z")) + timedelta(days=1)

  target_start = as_utc(target_start)
  target_end = as_utc(target_end)

  if (target_start >= target_end):
    _LOGGER.debug(f'{context} - {target_start} is after {target_end}, so setting target end to tomorrow')
    if target_start > current_date:
      target_start = target_start - timedelta(days=1)
    else:
      target_end = target_end + timedelta(days=1)

  # If our start date has passed, reset it to current_date to avoid picking a slot in the past
  if (start_time_not_in_past == True and target_start < current_date and current_date < target_end):
    _LOGGER.debug(f'{context} - Rolling target and {target_start} is in the past. Setting start to {current_date}')
    target_start = current_date

  # If our start and end are both in the past, then look to the next day
  if (target_start < current_date and target_end < current_date):
    target_start = target_start + timedelta(days=1)
    target_end = target_end + timedelta(days=1)

  return (target_start, target_end)

def get_fixed_applicable_time_periods(target_start: datetime, target_end: datetime, time_period_values: list, calculate_with_incomplete_data = False, context: str = None):
  _LOGGER.debug(f'{context} - Finding rates between {target_start} and {target_end}')

  # Retrieve the rates that are applicable for our target rate
  applicable_rates = []
  if time_period_values is not None:
    for rate in time_period_values:
      if rate["start"] >= target_start and (target_end is None or rate["end"] <= target_end):
        new_rate = dict(rate)
        
        applicable_rates.append(new_rate)

  # Make sure that we have enough rates that meet our target period
  date_diff = target_end - target_start
  hours = (date_diff.days * 24) + (date_diff.seconds // 3600)
  periods = hours * 2
  if len(applicable_rates) < periods and calculate_with_incomplete_data == False:
    _LOGGER.debug(f'{context} - Incorrect number of periods discovered. Require {periods}, but only have {len(applicable_rates)}')
    return None

  return applicable_rates

def get_rolling_applicable_time_periods(current_date: datetime, time_period_values: list, target_hours: float, calculate_with_incomplete_data = False, context: str = None):
  # Retrieve the rates that are applicable for our target rate
  applicable_time_periods = []
  periods = target_hours * 2

  if time_period_values is not None:
    for rate in time_period_values:
      if rate["end"] >= current_date:
        new_rate = dict(rate)
        applicable_time_periods.append(new_rate)

        if len(applicable_time_periods) >= periods:
          break

  # Make sure that we have enough rates that meet our target period
  if len(applicable_time_periods) < periods and calculate_with_incomplete_data == False:
    _LOGGER.debug(f'{context} - Incorrect number of periods discovered. Require {periods}, but only have {len(applicable_time_periods)}')
    return None

  return applicable_time_periods

def __get_end(rate):
  return (rate["end"].timestamp(), rate["end"].fold)

def calculate_continuous_times(
    applicable_time_periods: list,
    target_hours: float,
    search_for_highest_value = False,
    find_latest_values = False,
    min_value = None,
    max_value = None,
    weighting: list = None,
    hours_mode = CONFIG_TARGET_HOURS_MODE_EXACT,
    context: str = None
  ):
  if (applicable_time_periods is None or target_hours <= 0):
    return []
  
  applicable_time_periods_count = len(applicable_time_periods)
  total_required_time_periods = math.ceil(target_hours * 2)

  if weighting is not None and len(weighting) != total_required_time_periods:
    raise ValueError(f"{context} - Weighting does not match target hours")

  best_continuous_time_periods = None
  best_continuous_time_periods_total = None

  _LOGGER.debug(f'{context} - {applicable_time_periods_count} applicable time periods found')

  # Loop through our rates and try and find the block of time that meets our desired
  # hours and has the lowest combined rates
  for index, time_period in enumerate(applicable_time_periods):
    if (min_value is not None and time_period["value"] < min_value):
      continue

    if (max_value is not None and time_period["value"] > max_value):
      continue

    continuous_time_periods = [time_period]
    value_weight = Decimal(time_period["weighting"]) if "weighting" in time_period else 1
    continuous_rates_total = Decimal(time_period["value"]) * value_weight * (weighting[0] if weighting is not None and len(weighting) > 0 else 1)
    
    for offset in range(1, total_required_time_periods if hours_mode != CONFIG_TARGET_HOURS_MODE_MINIMUM else applicable_time_periods_count):
      if (index + offset) < applicable_time_periods_count:
        offset_time_period = applicable_time_periods[(index + offset)]

        if (min_value is not None and offset_time_period["value"] < min_value):
          break

        if (max_value is not None and offset_time_period["value"] > max_value):
          break

        continuous_time_periods.append(offset_time_period)
        value_weight = Decimal(offset_time_period["weighting"]) if "weighting" in offset_time_period else 1
        continuous_rates_total += Decimal(offset_time_period["value"]) * value_weight * (weighting[offset] if weighting is not None else 1)
      else:
        break

    current_continuous_time_periods_length = len(continuous_time_periods)
    best_continuous_time_periods_length = len(best_continuous_time_periods) if best_continuous_time_periods is not None else 0

    is_best_continuous_rates = False
    if best_continuous_time_periods is not None:
      if search_for_highest_value:
        is_best_continuous_rates = (continuous_rates_total >= best_continuous_time_periods_total if find_latest_values else continuous_rates_total > best_continuous_time_periods_total)
      else:
        is_best_continuous_rates = (continuous_rates_total <= best_continuous_time_periods_total if find_latest_values else continuous_rates_total < best_continuous_time_periods_total)

    has_required_hours = False
    if hours_mode == CONFIG_TARGET_HOURS_MODE_EXACT:
      has_required_hours = current_continuous_time_periods_length == total_required_time_periods
    elif hours_mode == CONFIG_TARGET_HOURS_MODE_MINIMUM:
      has_required_hours = current_continuous_time_periods_length >= total_required_time_periods and current_continuous_time_periods_length >= best_continuous_time_periods_length
    elif hours_mode == CONFIG_TARGET_HOURS_MODE_MAXIMUM:
      has_required_hours = current_continuous_time_periods_length <= total_required_time_periods and current_continuous_time_periods_length >= best_continuous_time_periods_length
    
    if ((best_continuous_time_periods is None or is_best_continuous_rates) and has_required_hours):
      best_continuous_time_periods = continuous_time_periods
      best_continuous_time_periods_total = continuous_rates_total
      _LOGGER.debug(f'{context} - New best block discovered {continuous_rates_total} ({continuous_time_periods[0]["start"] if len(continuous_time_periods) > 0 else None} - {continuous_time_periods[-1]["end"] if len(continuous_time_periods) > 0 else None})')
    else:
      _LOGGER.debug(f'{context} - Total rates for current block {continuous_rates_total} ({continuous_time_periods[0]["start"] if len(continuous_time_periods) > 0 else None} - {continuous_time_periods[-1]["end"] if len(continuous_time_periods) > 0 else None}). Total rates for best block {best_continuous_time_periods_total}')

  if best_continuous_time_periods is not None:
    # Make sure our rates are in ascending order before returning
    best_continuous_time_periods.sort(key=__get_end)
    return best_continuous_time_periods
  return []

def highest_last_time_period(time_period):
  rate_weight = Decimal(time_period["weighting"]) if "weighting" in time_period else 1
  return (-(Decimal(time_period["value"]) * rate_weight), -time_period["end"].timestamp(), -time_period["end"].fold)

def lowest_last_time_period(time_period):
  rate_weight = Decimal(time_period["weighting"]) if "weighting" in time_period else 1
  return (Decimal(time_period["value"]) * rate_weight, -time_period["end"].timestamp(), -time_period["end"].fold)

def highest_first_time_period(time_period):
  rate_weight = Decimal(time_period["weighting"]) if "weighting" in time_period else 1
  return (-(Decimal(time_period["value"]) * rate_weight), time_period["end"], time_period["end"].fold)

def lowest_first_time_period(time_period):
  rate_weight = Decimal(time_period["weighting"]) if "weighting" in time_period else 1
  return (Decimal(time_period["value"]) * rate_weight, time_period["end"], time_period["end"].fold)

def calculate_intermittent_times(
    applicable_time_periods: list,
    target_hours: float,
    search_for_highest_value = False,
    find_latest_time_periods = False,
    min_value = None,
    max_value = None,
    hours_mode = CONFIG_TARGET_HOURS_MODE_EXACT,
    context: str = None
  ):
  if (applicable_time_periods is None):
    return []
  
  total_required_time_periods = math.ceil(target_hours * 2)

  if find_latest_time_periods:
    if search_for_highest_value:
      applicable_time_periods.sort(key=highest_last_time_period)
    else:
      applicable_time_periods.sort(key=lowest_last_time_period)
  else:
    if search_for_highest_value:
      applicable_time_periods.sort(key=highest_first_time_period)
    else:
      applicable_time_periods.sort(key=lowest_first_time_period)

  applicable_time_periods = list(filter(lambda rate: (min_value is None or rate["value"] >= min_value) and (max_value is None or rate["value"] <= max_value), applicable_time_periods))
  
  _LOGGER.debug(f'{context} - {len(applicable_time_periods)} applicable time periods found')

  if ((hours_mode == CONFIG_TARGET_HOURS_MODE_EXACT and len(applicable_time_periods) >= total_required_time_periods) or hours_mode == CONFIG_TARGET_HOURS_MODE_MAXIMUM):
    applicable_time_periods = applicable_time_periods[:total_required_time_periods]

    # Make sure our rates are in ascending order before returning
    applicable_time_periods.sort(key=__get_end)

    return applicable_time_periods
  elif len(applicable_time_periods) >= total_required_time_periods:
    # Make sure our rates are in ascending order before returning
    applicable_time_periods.sort(key=__get_end)

    return applicable_time_periods
  
  return []

def get_target_time_period_info(current_date: datetime, applicable_time_periods, offset: str = None, context: str = None):
  is_active = False
  next_time = None
  current_duration_in_hours = 0
  next_duration_in_hours = 0
  total_applicable_time_periods = len(applicable_time_periods) if applicable_time_periods is not None else 0

  overall_total_value = 0
  overall_min_value = None
  overall_max_value = None

  current_average_value = None
  current_min_value = None
  current_max_value = None

  next_average_value = None
  next_min_value = None
  next_max_value = None

  if (total_applicable_time_periods > 0):

    # Find the applicable rates that when combine become a continuous block. This is more for
    # intermittent rates.
    applicable_time_periods.sort(key=__get_end)
    applicable_rate_blocks = list()
    block_valid_from = applicable_time_periods[0]["start"]

    total_value = 0
    min_value = None
    max_value = None

    for index, rate in enumerate(applicable_time_periods):
      if (index > 0 and applicable_time_periods[index - 1]["end"] != rate["start"]):
        diff = applicable_time_periods[index - 1]["end"] - block_valid_from
        minutes = diff.total_seconds() / 60
        periods = minutes / 30
        if periods < 1:
          _LOGGER.error(f"{context} - Less than 1 period discovered. Defaulting to 1 period. Rate start: {rate["start"]}; Applicable rates: {applicable_time_periods}")
          periods = 1

        applicable_rate_blocks.append({
          "start": block_valid_from,
          "end": applicable_time_periods[index - 1]["end"],
          "duration_in_hours": minutes / 60,
          "average_value": total_value / periods,
          "min_value": min_value,
          "max_value": max_value
        })

        block_valid_from = rate["start"]
        total_value = 0
        min_value = None
        max_value = None

      total_value += rate["value"]
      if min_value is None or min_value > rate["value"]:
        min_value = rate["value"]

      if max_value is None or max_value < rate["value"]:
        max_value = rate["value"]

      overall_total_value += rate["value"]
      if overall_min_value is None or overall_min_value > rate["value"]:
        overall_min_value = rate["value"]

      if overall_max_value is None or overall_max_value < rate["value"]:
        overall_max_value = rate["value"]

    # Make sure our final block is added
    diff = applicable_time_periods[-1]["end"] - block_valid_from
    minutes = diff.total_seconds() / 60
    applicable_rate_blocks.append({
      "start": block_valid_from,
      "end": applicable_time_periods[-1]["end"],
      "duration_in_hours": minutes / 60,
      "average_value": total_value / (minutes / 30),
      "min_value": min_value,
      "max_value": max_value
    })

    # Find out if we're within an active block, or find the next block
    for index, rate in enumerate(applicable_rate_blocks):
      if (offset is not None):
        valid_from = apply_offset(rate["start"], offset)
        valid_to = apply_offset(rate["end"], offset)
      else:
        valid_from = rate["start"]
        valid_to = rate["end"]
      
      if current_date >= valid_from and current_date < valid_to:
        current_duration_in_hours = rate["duration_in_hours"]
        current_average_value = rate["average_value"]
        current_min_value = rate["min_value"]
        current_max_value = rate["max_value"]
        is_active = True
      elif current_date < valid_from:
        next_time = valid_from
        next_duration_in_hours = rate["duration_in_hours"]
        next_average_value = rate["average_value"]
        next_min_value = rate["min_value"]
        next_max_value = rate["max_value"]
        break

  return {
    "is_active": is_active,
    "overall_average_value": round(overall_total_value / total_applicable_time_periods, 5) if total_applicable_time_periods > 0  else 0,
    "overall_min_value": overall_min_value,
    "overall_max_value": overall_max_value,
    "current_duration_in_hours": current_duration_in_hours,
    "current_average_value": current_average_value,
    "current_min_value": current_min_value,
    "current_max_value": current_max_value,
    "next_time": next_time,
    "next_duration_in_hours": next_duration_in_hours,
    "next_average_value": next_average_value,
    "next_min_value": next_min_value,
    "next_max_value": next_max_value,
  }

def create_weighting(config: str, number_of_slots: int):
  if config is None or config == "" or config.isspace():
    return None

  matches = re.search(REGEX_WEIGHTING, config)
  if matches is None:
    raise ValueError("Invalid config")
  
  parts = config.split(',')
  parts_length = len(parts)
  weighting = []
  for index in range(parts_length):
    if (parts[index] == "*"):
      # +1 to account for the current part
      target_number_of_slots = number_of_slots - parts_length + 1
      for index in range(target_number_of_slots):
          weighting.append(Decimal(1))

      continue

    weighting.append(Decimal(parts[index]))

  return weighting

def compare_config(current_config: dict, existing_config: dict):
  if current_config is None or existing_config is None:
    return False

  for key in CONFIG_TARGET_KEYS:
    if ((key not in existing_config and key in current_config) or 
        (key in existing_config and key not in current_config) or
        (key in existing_config and key in current_config and current_config[key] != existing_config[key])):
      return False
    
  return True

def should_evaluate_target_timeframes(current_date: datetime, target_timeframes: list, evaluation_mode: str) -> bool:
  if target_timeframes is None or len(target_timeframes) < 1:
    return True
  
  all_rates_in_past = True
  one_rate_in_past = False
  for rate in target_timeframes:
    if rate["end"] > current_date:
      all_rates_in_past = False
    
    if rate["start"] <= current_date:
      one_rate_in_past = True
  
  return ((evaluation_mode == CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST and all_rates_in_past) or
          (evaluation_mode == CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST and (one_rate_in_past == False or all_rates_in_past)) or
          (evaluation_mode == CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS))