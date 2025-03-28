from datetime import datetime, timedelta
import logging

from homeassistant.util.dt import (as_utc, parse_datetime)

logging.getLogger().setLevel(logging.DEBUG)

_LOGGER = logging.getLogger(__name__)

def create_data_source_data(period_from: datetime, period_to: datetime, expected_values: list):
  rates = []
  current_valid_from = period_from
  current_valid_to = None

  rate_index = 0
  while current_valid_to is None or current_valid_to < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)

    rates.append({
      "start": current_valid_from,
      "end": current_valid_to,
      "value": expected_values[rate_index],
    })

    current_valid_from = current_valid_to
    rate_index = rate_index + 1

    if (rate_index > (len(expected_values) - 1)):
      rate_index = 0

  return rates

def get_start(rate):
  return rate["start"]

def values_to_thirty_minute_increments(items: list, period_from: datetime, period_to: datetime):
  """Process the collection of rates to ensure they're in 30 minute periods"""
  starting_period_from = period_from
  results = []
    
  items.sort(key=get_start)

  # We need to normalise our data into 30 minute increments so that all of our rates across all tariffs are the same and it's 
  # easier to calculate our target rate sensors
  for item in items:
    value = float(item["value"])

    if "start" in item and item["start"] is not None:
      start = as_utc(parse_datetime(item["start"]))

      if (start < starting_period_from):
        start = starting_period_from
    else:
      start = starting_period_from

    # Some rates don't have end dates, so we should treat this as our period to target
    if "end" in item and item["end"] is not None:
      target_date = as_utc(parse_datetime(item["end"]))

      # Cap our target date to our end period
      if (target_date > period_to):
        target_date = period_to
    else:
      target_date = period_to
    
    while start < target_date:
      end = start + timedelta(minutes=30)
      results.append({
        "value": value,
        "start": start,
        "end": end,
      })

      start = end
      starting_period_from = end

  _LOGGER.info(results)
    
  return results

default_time_periods = values_to_thirty_minute_increments(
  [
    {
      "value": 16.0965,
      "start": "2022-10-22T22:30:00Z",
      "end": "2022-10-22T23:00:00Z"
    },
    {
      "value": 14.994,
      "start": "2022-10-22T22:00:00Z",
      "end": "2022-10-22T22:30:00Z"
    },
    {
      "value": 23.1315,
      "start": "2022-10-22T21:30:00Z",
      "end": "2022-10-22T22:00:00Z"
    },
    {
      "value": 25.641,
      "start": "2022-10-22T21:00:00Z",
      "end": "2022-10-22T21:30:00Z"
    },
    {
      "value": 24.255,
      "start": "2022-10-22T20:30:00Z",
      "end": "2022-10-22T21:00:00Z"
    },
    {
      "value": 29.2845,
      "start": "2022-10-22T20:00:00Z",
      "end": "2022-10-22T20:30:00Z"
    },
    {
      "value": 25.578,
      "start": "2022-10-22T19:30:00Z",
      "end": "2022-10-22T20:00:00Z"
    },
    {
      "value": 33.159,
      "start": "2022-10-22T19:00:00Z",
      "end": "2022-10-22T19:30:00Z"
    },
    {
      "value": 30.6915,
      "start": "2022-10-22T18:30:00Z",
      "end": "2022-10-22T19:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-22T18:00:00Z",
      "end": "2022-10-22T18:30:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-22T17:30:00Z",
      "end": "2022-10-22T18:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-22T17:00:00Z",
      "end": "2022-10-22T17:30:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-22T16:30:00Z",
      "end": "2022-10-22T17:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-22T16:00:00Z",
      "end": "2022-10-22T16:30:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-22T15:30:00Z",
      "end": "2022-10-22T16:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-22T15:00:00Z",
      "end": "2022-10-22T15:30:00Z"
    },
    {
      "value": 22.05,
      "start": "2022-10-22T14:30:00Z",
      "end": "2022-10-22T15:00:00Z"
    },
    {
      "value": 21.3885,
      "start": "2022-10-22T14:00:00Z",
      "end": "2022-10-22T14:30:00Z"
    },
    {
      "value": 18.921,
      "start": "2022-10-22T13:30:00Z",
      "end": "2022-10-22T14:00:00Z"
    },
    {
      "value": 19.1835,
      "start": "2022-10-22T13:00:00Z",
      "end": "2022-10-22T13:30:00Z"
    },
    {
      "value": 18.081,
      "start": "2022-10-22T12:30:00Z",
      "end": "2022-10-22T13:00:00Z"
    },
    {
      "value": 18.522,
      "start": "2022-10-22T12:00:00Z",
      "end": "2022-10-22T12:30:00Z"
    },
    {
      "value": 19.9815,
      "start": "2022-10-22T11:30:00Z",
      "end": "2022-10-22T12:00:00Z"
    },
    {
      "value": 21.3465,
      "start": "2022-10-22T11:00:00Z",
      "end": "2022-10-22T11:30:00Z"
    },
    {
      "value": 20.727,
      "start": "2022-10-22T10:30:00Z",
      "end": "2022-10-22T11:00:00Z"
    },
    {
      "value": 20.727,
      "start": "2022-10-22T10:00:00Z",
      "end": "2022-10-22T10:30:00Z"
    },
    {
      "value": 21.168,
      "start": "2022-10-22T09:30:00Z",
      "end": "2022-10-22T10:00:00Z"
    },
    {
      "value": 22.2705,
      "start": "2022-10-22T09:00:00Z",
      "end": "2022-10-22T09:30:00Z"
    },
    {
      "value": 22.6695,
      "start": "2022-10-22T08:30:00Z",
      "end": "2022-10-22T09:00:00Z"
    },
    {
      "value": 24.57,
      "start": "2022-10-22T08:00:00Z",
      "end": "2022-10-22T08:30:00Z"
    },
    {
      "value": 29.988,
      "start": "2022-10-22T07:30:00Z",
      "end": "2022-10-22T08:00:00Z"
    },
    {
      "value": 24.339,
      "start": "2022-10-22T07:00:00Z",
      "end": "2022-10-22T07:30:00Z"
    },
    {
      "value": 21.7875,
      "start": "2022-10-22T06:30:00Z",
      "end": "2022-10-22T07:00:00Z"
    },
    {
      "value": 17.136,
      "start": "2022-10-22T06:00:00Z",
      "end": "2022-10-22T06:30:00Z"
    },
    {
      "value": 17.136,
      "start": "2022-10-22T05:30:00Z",
      "end": "2022-10-22T06:00:00Z"
    },
    {
      "value": 19.845,
      "start": "2022-10-22T05:00:00Z",
      "end": "2022-10-22T05:30:00Z"
    },
    {
      "value": 17.9025,
      "start": "2022-10-22T04:30:00Z",
      "end": "2022-10-22T05:00:00Z"
    },
    {
      "value": 19.845,
      "start": "2022-10-22T04:00:00Z",
      "end": "2022-10-22T04:30:00Z"
    },
    {
      "value": 18.501,
      "start": "2022-10-22T03:30:00Z",
      "end": "2022-10-22T04:00:00Z"
    },
    {
      "value": 18.7005,
      "start": "2022-10-22T03:00:00Z",
      "end": "2022-10-22T03:30:00Z"
    },
    {
      "value": 18.3435,
      "start": "2022-10-22T02:30:00Z",
      "end": "2022-10-22T03:00:00Z"
    },
    {
      "value": 18.3435,
      "start": "2022-10-22T02:00:00Z",
      "end": "2022-10-22T02:30:00Z"
    },
    {
      "value": 19.341,
      "start": "2022-10-22T01:30:00Z",
      "end": "2022-10-22T02:00:00Z"
    },
    {
      "value": 19.6245,
      "start": "2022-10-22T01:00:00Z",
      "end": "2022-10-22T01:30:00Z"
    },
    {
      "value": 21.231,
      "start": "2022-10-22T00:30:00Z",
      "end": "2022-10-22T01:00:00Z"
    },
    {
      "value": 14.123,
      "start": "2022-10-22T00:00:00Z",
      "end": "2022-10-22T00:30:00Z"
    },
    {
      "value": 14.123,
      "start": "2022-10-21T23:30:00Z",
      "end": "2022-10-22T00:00:00Z"
    },
    {
      "value": 21.609,
      "start": "2022-10-21T23:00:00Z",
      "end": "2022-10-21T23:30:00Z"
    },
    {
      "value": 19.845,
      "start": "2022-10-21T22:30:00Z",
      "end": "2022-10-21T23:00:00Z"
    },
    {
      "value": 19.6875,
      "start": "2022-10-21T22:00:00Z",
      "end": "2022-10-21T22:30:00Z"
    },
    {
      "value": 20.727,
      "start": "2022-10-21T21:30:00Z",
      "end": "2022-10-21T22:00:00Z"
    },
    {
      "value": 23.1525,
      "start": "2022-10-21T21:00:00Z",
      "end": "2022-10-21T21:30:00Z"
    },
    {
      "value": 20.727,
      "start": "2022-10-21T20:30:00Z",
      "end": "2022-10-21T21:00:00Z"
    },
    {
      "value": 23.5095,
      "start": "2022-10-21T20:00:00Z",
      "end": "2022-10-21T20:30:00Z"
    },
    {
      "value": 21.651,
      "start": "2022-10-21T19:30:00Z",
      "end": "2022-10-21T20:00:00Z"
    },
    {
      "value": 26.019,
      "start": "2022-10-21T19:00:00Z",
      "end": "2022-10-21T19:30:00Z"
    },
    {
      "value": 21.9135,
      "start": "2022-10-21T18:30:00Z",
      "end": "2022-10-21T19:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T18:00:00Z",
      "end": "2022-10-21T18:30:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T17:30:00Z",
      "end": "2022-10-21T18:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T17:00:00Z",
      "end": "2022-10-21T17:30:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T16:30:00Z",
      "end": "2022-10-21T17:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T16:00:00Z",
      "end": "2022-10-21T16:30:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T15:30:00Z",
      "end": "2022-10-21T16:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T15:00:00Z",
      "end": "2022-10-21T15:30:00Z"
    },
    {
      "value": 22.05,
      "start": "2022-10-21T14:30:00Z",
      "end": "2022-10-21T15:00:00Z"
    },
    {
      "value": 20.727,
      "start": "2022-10-21T14:00:00Z",
      "end": "2022-10-21T14:30:00Z"
    },
    {
      "value": 21.21,
      "start": "2022-10-21T13:30:00Z",
      "end": "2022-10-21T14:00:00Z"
    },
    {
      "value": 21.21,
      "start": "2022-10-21T13:00:00Z",
      "end": "2022-10-21T13:30:00Z"
    },
    {
      "value": 21.3675,
      "start": "2022-10-21T12:30:00Z",
      "end": "2022-10-21T13:00:00Z"
    },
    {
      "value": 27.342,
      "start": "2022-10-21T12:00:00Z",
      "end": "2022-10-21T12:30:00Z"
    },
    {
      "value": 22.008,
      "start": "2022-10-21T11:30:00Z",
      "end": "2022-10-21T12:00:00Z"
    },
    {
      "value": 30.87,
      "start": "2022-10-21T11:00:00Z",
      "end": "2022-10-21T11:30:00Z"
    },
    {
      "value": 28.4445,
      "start": "2022-10-21T10:30:00Z",
      "end": "2022-10-21T11:00:00Z"
    },
    {
      "value": 26.46,
      "start": "2022-10-21T10:00:00Z",
      "end": "2022-10-21T10:30:00Z"
    },
    {
      "value": 26.901,
      "start": "2022-10-21T09:30:00Z",
      "end": "2022-10-21T10:00:00Z"
    },
    {
      "value": 33.075,
      "start": "2022-10-21T09:00:00Z",
      "end": "2022-10-21T09:30:00Z"
    },
    {
      "value": 32.109,
      "start": "2022-10-21T08:30:00Z",
      "end": "2022-10-21T09:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T08:00:00Z",
      "end": "2022-10-21T08:30:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T07:30:00Z",
      "end": "2022-10-21T08:00:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T07:00:00Z",
      "end": "2022-10-21T07:30:00Z"
    },
    {
      "value": 33.4761,
      "start": "2022-10-21T06:30:00Z",
      "end": "2022-10-21T07:00:00Z"
    },
    {
      "value": 27.363,
      "start": "2022-10-21T06:00:00Z",
      "end": "2022-10-21T06:30:00Z"
    },
    {
      "value": 21.8925,
      "start": "2022-10-21T05:30:00Z",
      "end": "2022-10-21T06:00:00Z"
    },
    {
      "value": 22.449,
      "start": "2022-10-21T05:00:00Z",
      "end": "2022-10-21T05:30:00Z"
    },
    {
      "value": 26.838,
      "start": "2022-10-21T04:30:00Z",
      "end": "2022-10-21T05:00:00Z"
    },
    {
      "value": 21.21,
      "start": "2022-10-21T04:00:00Z",
      "end": "2022-10-21T04:30:00Z"
    },
    {
      "value": 21.21,
      "start": "2022-10-21T03:30:00Z",
      "end": "2022-10-21T04:00:00Z"
    },
    {
      "value": 21.651,
      "start": "2022-10-21T03:00:00Z",
      "end": "2022-10-21T03:30:00Z"
    },
    {
      "value": 21.4305,
      "start": "2022-10-21T02:30:00Z",
      "end": "2022-10-21T03:00:00Z"
    },
    {
      "value": 21.651,
      "start": "2022-10-21T02:00:00Z",
      "end": "2022-10-21T02:30:00Z"
    },
    {
      "value": 20.727,
      "start": "2022-10-21T01:30:00Z",
      "end": "2022-10-21T02:00:00Z"
    },
    {
      "value": 21.651,
      "start": "2022-10-21T01:00:00Z",
      "end": "2022-10-21T01:30:00Z"
    },
    {
      "value": 21.651,
      "start": "2022-10-21T00:30:00Z",
      "end": "2022-10-21T01:00:00Z"
    },
    {
      "value": 21.21,
      "start": "2022-10-21T00:00:00Z",
      "end": "2022-10-21T00:30:00Z"
    },
    {
      "value": 21.651,
      "start": "2022-10-20T23:30:00Z",
      "end": "2022-10-21T00:00:00Z"
    },
    {
      "value": 24.696,
      "start": "2022-10-20T23:00:00Z",
      "end": "2022-10-20T23:30:00Z"
    }
  ],
  datetime.strptime("2022-10-21T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
  datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
)