# Rolling Target Timeframe Sensor(s)

After you've configured your [data source](./data_source.md), you'll be able to configure rolling target timeframe sensors. These are configured as sub configuration options associated with your data source. Select `Rolling Target Timeframe` from the sub menu.

These sensors calculate the lowest continuous or intermittent values within the next available `x` hours, where `x` is configurable via the sensor, and turn on when these periods are active. If you are targeting an export meter, then the sensors will calculate the highest continuous or intermittent values within the next available `x` hours and turn on when these periods are active. If you are wanting to evaluate on a fixed basis (e.g. every 24 hours), you might be interested in the [standard target timeframe sensors](./target_timeframe.md)

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need rolling target timeframe sensors.

Each sensor will be in the form `binary_sensor.target_timeframes_{{DATA_SOURCE_ID}}_{{TARGET_TIMEFRAME_NAME}}`.

## Setup

### Hours

The hours that you require for the sensor to find. This should be in decimal format and represent 30 minute increments. For example 30 minutes would be `0.5`, 1 hour would be `1` or `1.0`, 1 hour and 30 minutes would be `1.5`, etc.

### Hours Mode

There are three different modes that the target timeframe sensor can be set to, which determines how the specified hours should be interpreted

#### Exact (default)

The target timeframe sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will not come on at all. If there are more hours than required that meet the specified requirements (e.g. below a certain value), then it will come on for the lowest available times up to the specified hours.

For instance if the lowest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target timeframe is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T01:30`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will not come on at all.

#### Minimum

The target timeframe sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will not come on at all. If there are more hours than required that meet the specified requirements (e.g. below a certain value), then it will come on for all discovered times.

For instance if the lowest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target timeframe is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T05:00`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will not come on at all.

#### Maximum

The target timeframe sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will come on for all times that are discovered. If there are more hours than required that meet the specified requirements (e.g. below a certain value), then it will come on for the lowest available times up to the specified hours.

For instance if the lowest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target timeframe is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T01:30`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will come on between  `2023-01-01T00:30` and `2023-01-01T01:00`.

### Look Ahead Hours

This is the number of hours to look ahead for the best time periods. This will include the current time period. For instance, if it's `2023-01-01T00:15` and you have your look ahead hours set to `8`, then it will look for the best times between `2023-01-01T00:00` and `2023-01-01T08:00`.

### Evaluation mode

Because the time frame that is being evaluated could change at different frequencies depending on the source, you might want to set how/when the target times are evaluated in order to make the selected times more or less dynamic.

#### All existing target timeframes are in the past

This is the default way of evaluating target times. This will only evaluate new target times if no target times have been calculated or all existing target times are in the past.

#### Existing target timeframes haven't started or finished

This will only evaluate target times if no target times have been calculated or all existing target times are either in the future or all existing target times are in the past. 

For example, lets say we have a continuous rolling target which looks ahead for `8` hours and has existing target times from `2023-01-02T01:00` to `2023-01-02T02:00`. 

* If the current time is `2023-01-02T00:59`, then the target times will be re-evaluated and might change if the new rolling target period (i.e. `2023-01-02T00:30` to `2023-01-02T08:30`) has better times than the existing target times.
* If the current time is `2023-01-02T01:00`, the the target times will not be re-evaluated because we've entered our current target times, even if the new rolling target period has cheaper times. 
* If the current time is `2023-01-02T02:01`, the the target times will be re-evaluated because our existing target times are in the past and will find the best times in the new rolling target period (i.e. `2023-01-02T02:00` to `2023-01-02T10:00`). 

#### Always

This will always evaluate the best target times for the rolling target period, even if the sensor is in the middle of an existing target time period.

For example, lets say we have a continuous rolling target which looks ahead for `8` hours and has existing target times from `2023-01-02T01:00` to `2023-01-02T02:00`. 

* If the current time is `2023-01-02T00:59`, then the target times will be re-evaluated and might change if the new rolling target period (i.e. `2023-01-02T00:30` to `2023-01-02T08:30`) has better times than the existing target times.
* If the current time is `2023-01-02T01:31`, then the target times will be re-evaluated and might change if the new rolling target period (i.e. `2023-01-02T01:30` to `2023-01-02T09:30`) has better times than the existing target times.
* If the current time is `2023-01-02T02:01`, the the target times will be re-evaluated because our existing target times are in the past and will find the best times in the new rolling target period (i.e. `2023-01-02T02:00` to `2023-01-02T10:00`). 

!!! warning

    This setting means that you could end up with the sensor not turning on for the fully requested hours as the target times might be moved ahead half way through the picked times. It also could mean that the sensor doesn't come on at all during the requested look ahead hours (e.g. 8) because the lowest period kept moving back. 

### Offset

You may want your target timeframe sensors to turn on a period of time before the optimum discovered period. For example, you may be turning on a robot vacuum cleaner for a 30 minute clean and want it to charge during the optimum period. For this, you'd use the `offset` field and set it to `-00:30:00`, which can be both positive and negative and go up to a maximum of 24 hours. This will shift when the sensor turns on relative to the optimum period. For example, if the optimum period is between `2023-01-18T10:00` and `2023-01-18T11:00` with an offset of `-00:30:00`, the sensor will turn on between `2023-01-18T09:30` and `2023-01-18T10:30`.

### Latest Period

Depending on how you're going to use the sensor, you might want the best period at the latest possible time. For example, you might be using the sensor to turn on an immersion heater which you'll want to come on at the end of the lowest found period. 

For instance if you turn this on and the lowest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target timeframe is for 1 hour, then it will come on between `2023-01-01T04:00` and `2023-01-01T05:00` instead of `2023-01-01T00:30` and `2023-01-01T01:30`.

This feature is toggled on by the `Find last applicable values` checkbox.

### Find highest value

If this is checked, then the highest values will be discovered, instead of the normal behaviour of the lowest values.

### Minimum/Maximum Values

There may be times that you want the target timeframe sensors to not take into account values that are above or below a certain value (e.g. you don't want the sensor to turn on when values go crazy or where it would be more beneficial to export).

!!! info

    If hours mode is set to **minimum**, then a minimum and/or maximum rate must be specified in order for the target timeframe sensor to know what the cut off is for discovered times.

### Weighting/Multipliers

!!! info

    This is only available for **continuous** target value sensors in **exact** hours mode.

There may be times when the device you're wanting the target value sensor to turn on doesn't have a consistent power draw. You can specify a weighting/multiplier which can be applied to the value of each discovered 30 minute slot. This can be specified in a few different ways. Take the following example weighting/multiplier for a required 2 hours.

* `1,1,2,1` - This applies a weighting/multiplier of 1 to the first, second and forth slot and a weighting/multiplier of 2 to the third slot. This will try and make the lowest slot fall on the third slot, as long as the surrounding slots are cheaper than other continuous slots.
* `*,2,1` - This applies a weighting/multiplier of 1 to the first, second and forth slot and a weighting/multiplier of 2 to the third slot. The `*` can be used as a placeholder for the standard weighting/multiplier of 1 for all slots before the ones specified.
* `1,1,2,*` - This applies a weighting/multiplier of 1 to the first, second and forth slot and a weighting/multiplier of 2 to the third slot. The `*` can be used as a placeholder for the standard weighting/multiplier of 1 for all slots after the ones specified.
* `2,*,2` - This applies a weighting/multiplier of 2 to the first and forth slot and a weighting/multiplier of 1 to all slots in between. The `*` can be used as a placeholder for the standard weighting/multiplier of 1 for all slots in between the specified slots.

Each slot weighting/multiplier must be a whole number or decimal number and be positive.

You can also use weightings/multipliers to ignore slots. This can be done by assigning a value of 0 for the desired slot.

## Attributes

The following attributes are available on each sensor

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The name of the sensor. |
| `hours` | `string` | The total hours are being discovered.  |
| `type` | `string` | The type/mode for the target timeframe sensor. This will be either `continuous` or `intermittent`. |
| `look_ahead_hours` | `float` | The number of hours the sensor should look ahead for the best time period |
| `target_times_evaluation_mode` | `string` | The mode that determines when/how target times are picked |
| `last_values` | `boolean` | Determines if `Find last applicable values` is turned off for the sensor. |
| `offset` | `string` | The offset configured for the sensor. |
| `values_incomplete` | `boolean` | True if rate information is incomplete and therefore target times cannot be calculated; False otherwise. |
| `target_times` | `array` | The discovered times and values the sensor will come on for. |
| `overall_average_value` | `float` | The average value of all discovered times during the current **24 hour period**. |
| `overall_min_value` | `float` | The minimum value of all discovered times during the current **24 hour period**. |
| `overall_max_value` | `float` | The maximum value of all discovered times during the current **24 hour period**. |
| `current_duration_in_hours` | `float` | The duration the sensor will be on for, for the current continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_average_value` | `float` | The average value for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_min_value` | `float` | The min value for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_max_value` | `float` | The max value for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `next_time` | `datetime` | The next date/time the sensor will come on. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `next_duration_in_hours` | `float` | The duration the sensor will be on for, for the next continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `next_average_value` | `float` | The average value for the next continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `next_min_value` | `float` | The average value for the next continuous discovered period. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `next_max_value` | `float` | The average value for the next continuous discovered period. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `target_times_last_evaluated` | datetime | The datetime the target times collection was last evaluated. This will occur if all previous target times are in the past and all values are available for the requested future time period. For example, if you are targeting 16:00 (day 1) to 16:00 (day 2), and you only have values up to 23:00 (day 1), then the target timeframes won't be calculated. |

## Services

There are services available associated with target timeframe sensors. Please review them in the [services doc](../services.md#rolling-target-timeframes).
