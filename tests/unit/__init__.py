from datetime import datetime, timedelta
import logging

logging.getLogger().setLevel(logging.DEBUG)

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