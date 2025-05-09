# Target Timeframe Sensor(s)

After you've configured your [data source](./data_source.md), you'll be able to configure target timeframe sensors. These are configured as sub configuration options associated with your data source. Select `Target timeframe` from the sub menu.

These sensors calculate the lowest continuous or intermittent values **within a 24 hour period** and turn on when these periods are active. If you are targeting an export meter, then the sensors will calculate the highest continuous or intermittent values **within a 24 hour period** and turn on when these periods are active. If you are wanting to evaluate on a rolling basis, you might be interested in the [rolling target value sensors](./rolling_target_timeframe.md)

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need target value sensors.

Each sensor will be in the form `binary_sensor.target_timeframes_{{DATA_SOURCE_ID}}_{{TARGET_TIMEFRAME_NAME}}`.

## Setup

### Target Timeframe

If you're wanting your devices to come on during a certain timeframe, for example while you're at work, you can set the minimum and/or maximum times for your target value sensor. These are specified in 24 hour clock format and will attempt to find the optimum discovered period during these times.

The `from/start` time can be set in the field `The minimum time to start the device` and the `to/end` time can be set in the field `The maximum time to stop the device`.

If not specified, these default from `00:00:00` to `00:00:00` the following day.

If for example you want to look at prices overnight you could set the minimum time to something like `20:00` and your maximum time to something like `05:00`. If the minimum time is "after" the maximum time, then it will treat the maximum time as the time for the following day.

!!! info

    The target value will not be evaluated until **all values** are available for the specified timeframe. Therefore if we're looking between `00:00` and `00:00`, full value information must exist between this time. Whereas if times are between `10:00` and `16:00`, then value information is only needed between these times before it can be calculated.

### Hours

The hours that you require for the sensor to find. This should be in decimal format and represent 30 minute increments. For example 30 minutes would be `0.5`, 1 hour would be `1` or `1.0`, 1 hour and 30 minutes would be `1.5`, etc.

### Hours Mode

There are three different modes that the target value sensor can be set to, which determines how the specified hours should be interpreted

#### Exact (default)

The target value sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will not come on at all. If there are more hours than required that meet the specified requirements (e.g. below a certain value), then it will come on for the lowest available times up to the specified hours.

For instance if the lowest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target value is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T01:30`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will not come on at all.

#### Minimum

The target value sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will not come on at all. If there are more hours than required that meet the specified requirements (e.g. below a certain value), then it will come on for all discovered times.

For instance if the lowest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target value is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T05:00`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will not come on at all.

#### Maximum

The target value sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will come on for all times that are discovered. If there are more hours than required that meet the specified requirements (e.g. below a certain value), then it will come on for the lowest available times up to the specified hours.

For instance if the lowest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target value is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T01:30`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will come on between  `2023-01-01T00:30` and `2023-01-01T01:00`.

### Evaluation mode

Because the time frame that is being evaluated could change at different frequencies depending on the source, you might want to set how/when the target times are evaluated in order to make the selected times more or less dynamic.

#### All existing target values are in the past

This is the default way of evaluating target times. This will only evaluate new target times if no target times have been calculated or all existing target times are in the past.

#### Existing target values haven't started or finished

This will only evaluate target times if no target times have been calculated or all existing target times are either in the future or all existing target times are in the past. 

For example, lets say we have a continuous target which looks between `00:00` and `08:00` has existing target times from `2023-01-02T01:00` to `2023-01-02T02:00`. 

* If the current time is `2023-01-02T00:59`, then the target times will be re-evaluated and might change if the target period (i.e. `2023-01-02T00:30` to `2023-01-02T08:30`) has better values than the existing target times (e.g. the external weightings have changed).
* If the current time is `2023-01-02T01:00`, the the target times will not be re-evaluated because we've entered our current target times, even if the evaluation period has cheaper times. 
* If the current time is `2023-01-02T02:01`, the the target times will be re-evaluated because our existing target times are in the past and will find the best times in the new rolling target period (i.e. `2023-01-02T02:00` to `2023-01-02T10:00`). 

### Offset

You may want your target value sensors to turn on a period of time before the optimum discovered period. For example, you may be turning on a robot vacuum cleaner for a 30 minute clean and want it to charge during the optimum period. For this, you'd use the `offset` field and set it to `-00:30:00`, which can be both positive and negative and go up to a maximum of 24 hours. This will shift when the sensor turns on relative to the optimum period. For example, if the optimum period is between `2023-01-18T10:00` and `2023-01-18T11:00` with an offset of `-00:30:00`, the sensor will turn on between `2023-01-18T09:30` and `2023-01-18T10:30`.

### Re-evaluate within time frame

Depending on how you're going to use the sensor, you might want the best period to be found throughout the day so it's always available. For example, you might be using the sensor to turn on a washing machine which you might want to come on at the best time regardless of when you use the washing machine. You can activate this behaviour by setting the `Re-evaluate multiple times a day` checkbox.

!!! warning

    Using this can result in the sensor coming on more than the target hours, and therefore should be used in conjunction with other sensors. Depending on how long your target timeframe is, upon each re-evaluation the picked times will get steadily worse.

However, you might also only want the target time to occur once during each timeframe so once the best time for that day has passed it won't turn on again until the next timeframe. For example, you might be using the sensor to turn on something that isn't time critical and could wait till the next timeframe like a charger. This is the default behaviour and is done by not setting the `Re-evaluate multiple times a day` checkbox.

!!! info

    The next set of target times will not be calculated until all target times are in the past. This will have an effect on the `next` set of attributes on the sensor.

### Latest Period

Depending on how you're going to use the sensor, you might want the best period at the latest possible time. For example, you might be using the sensor to turn on an immersion heater which you'll want to come on at the end of the lowest found period. 

For instance if you turn this on and the lowest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target value is for 1 hour, then it will come on between `2023-01-01T04:00` and `2023-01-01T05:00` instead of `2023-01-01T00:30` and `2023-01-01T01:30`.

This feature is toggled on by the `Find last applicable values` checkbox.

### Find highest value

If this is checked, then the highest values will be discovered, instead of the normal behaviour of the lowest values.

### Minimum/Maximum Values

There may be times that you want the target timeframe sensors to not take into account values that are above or below a certain value (e.g. you don't want the sensor to turn on when values go crazy or where it would be more beneficial to export).

!!! info

    If hours mode is set to **minimum**, then a minimum and/or maximum value must be specified in order for the target timeframe sensor to know what the cut off is for discovered times.

### Weighting

!!! info

    This is only available for **continuous** target value sensors in **exact** hours mode.

There may be times when the device you're wanting the target value sensor to turn on doesn't have a consistent power draw. You can specify a weighting which can be applied to each discovered 30 minute slot. This can be specified in a few different ways. Take the following example weighting for a required 2 hours.

* `1,1,2,1` - This applies a weighting of 1 to the first, second and forth slot and a weighting of 2 to the third slot. This will try and make the lowest slot fall on the third slot, as long as the surrounding slots are cheaper than other continuous slots.
* `*,2,1` - This applies a weighting of 1 to the first, second and forth slot and a weighting of 2 to the third slot. The `*` can be used as a placeholder for the standard weighting of 1 for all slots before the ones specified.
* `1,1,2,*` - This applies a weighting of 1 to the first, second and forth slot and a weighting of 2 to the third slot. The `*` can be used as a placeholder for the standard weighting of 1 for all slots after the ones specified.
* `2,*,2` - This applies a weighting of 2 to the first and forth slot and a weighting of 1 to all slots in between. The `*` can be used as a placeholder for the standard weighting of 1 for all slots in between the specified slots.

Each slot weighting must be a whole number or decimal number and be positive.

You can also use weightings to ignore slots. This can be done by assigning a value of 0 for the desired slot.

## Attributes

The following attributes are available on each sensor

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The name of the sensor. |
| `hours` | `string` | The total hours are being discovered.  |
| `type` | `string` | The type/mode for the target value sensor. This will be either `continuous` or `intermittent`. |
| `mpan` | `string` | The `mpan` of the meter being used to determine the values. |
| `target_times_evaluation_mode` | `string` | The mode that determines when/how target times are picked |
| `rolling_target` | `boolean` | Determines if `Re-evaluate multiple times a day` is turned on for the sensor. |
| `last_values` | `boolean` | Determines if `Find last applicable values` is turned off for the sensor. |
| `offset` | `string` | The offset configured for the sensor. |
| `start_time` | `string` | The start time configured for the sensor. |
| `end_time` | `string` | The end time configured for the sensor. |
| `values_incomplete` | `boolean` | True if value information is incomplete and therefore target times cannot be calculated; False otherwise. |
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
| `target_times_last_evaluated` | datetime | The datetime the target times collection was last evaluated. This will occur if all previous target times are in the past and all values are available for the requested future time period. For example, if you are targeting 16:00 (day 1) to 16:00 (day 2), and you only have values up to 23:00 (day 1), then the target values won't be calculated. |

## Services

There are services available associated with target value sensors. Please review them in the [services doc](../services.md#target-timeframes).

## Examples

Let's look at a few examples. Let's say we have the the following (unrealistic) set of values:

| start | end | value |
| ----- | --- | ----- |
| `2023-01-01T00:00` | `2023-01-01T00:30` | 6 |
| `2023-01-01T00:30` | `2023-01-01T05:00` | 12 |
| `2023-01-01T05:00` | `2023-01-01T05:30` | 7 |
| `2023-01-01T05:30` | `2023-01-01T18:00` | 20 |
| `2023-01-01T18:00` | `2023-01-01T23:30` | 34 |
| `2023-01-01T23:30` | `2023-01-02T00:30` | 5 |
| `2023-01-02T00:30` | `2023-01-02T05:00` | 12 |
| `2023-01-02T05:00` | `2023-01-02T05:30` | 7 |
| `2023-01-02T05:30` | `2023-01-02T18:00` | 20 |
| `2023-01-02T18:00` | `2023-01-02T23:00` | 34 |
| `2023-01-02T23:30` | `2023-01-03T00:00` | 6 |

### Continuous

If we look at a continuous sensor that we want on for 1 hour.

If we set no from/to times, then our 24 hour period being looked at ranges from `00:00:00` to `23:59:59`.

The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T00:00` - `2023-01-01T01:00` | `false`                            | While 5 is our lowest value within the current 24 hour period, it doesn't cover our whole 1 hour and is next to a high 34 value. A value of 6 is the next available value with a low following value. |
| `2023-01-01T01:00` | `2023-01-02T00:00` - `2023-01-02T01:00` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-01T01:00` | `2023-01-01T04:30` - `2023-01-01T05:30` | `true`                             | The value of 6 is in the past, so 7 is our next lowest value. 12 is smaller value than 20 so we start in the value period before to fill our desired hour. |
| `2023-01-01T23:30` | None | `true`                             | There is no longer enough time available in the current 24 hour period, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times for `05:00` to `19:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T05:00` - `2023-01-01T06:00` | `false`                            | The value of 12 is no longer available as it's outside of our `from` time. |
| `2023-01-01T06:30` | `2023-01-02T05:00` - `2023-01-02T06:00` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-01T06:30` | `2023-01-01T06:30` - `2023-01-01T07:30` | `true`                             | The value of 7 is in the past, so we must look for the next lowest combined value. |
| `2023-01-01T18:00` | `2023-01-01T18:00` - `2023-01-01T19:00` | `true`                             | The value of 20 is in the past, so we must look for the next lowest combined value which is 34. |
| `2023-01-01T18:30` | None | `true`                            | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times to look over two days, from `20:00` to `06:00`, we then limit the period that we look at to overnight. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30` - `2023-01-02T01:30` | `false`                            | Our lowest value of 5 now falls between our overnight time period so is available. |
| `2023-01-02T02:00` | `2023-01-01T23:30` - `2023-01-02T01:30` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-02T02:00` | `2023-01-02T04:30` - `2023-01-02T05:30` | `true`                             | The value of 5 is in the past, so we must look for the next lowest combined value, which includes our half hour value at 7. |
| `2023-01-02T05:30` | None | `true`                             | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set an offset of `-00:30:00`, then while the times might be the same, the target value sensor will turn on 30 minutes before the select value period starts. Any set time restrictions **will not** include the offset.

### Intermittent

If we look at an intermittent sensor that we want on for 1 hour total (but not necessarily together).

If we set no from/to times, then our 24 hour period being looked at ranges from `00:00:00` to `23:59:59`.

The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T00:00` - `2023-01-01T00:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `false`                            | Our sensor will go on for 30 minutes at the lowest value, then 30 minutes at the next lowest value. |
| `2023-01-01T01:00` | `2023-01-01T00:00` - `2023-01-01T00:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `false`                            | Our sensor will go on for 30 minutes at the lowest value, which will be in the past, then 30 minutes at the next lowest value. |
| `2023-01-01T01:00` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `true`                             | Our sensor will go on for 30 minutes at the second lowest value, then 30 minutes at the third lowest value. |
| `2023-01-01T23:30` | None | `true`                             | There is no longer enough time available in the current 24 hour period, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times for `05:00` to `19:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T05:30` - `2023-01-01T06:00` | `false`                            | Our lowest values are outside our target range, so we need to look at the next lowest. Luckily on our scenario the two lowest values are next to each other. |
| `2023-01-01T06:30` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T05:30` - `2023-01-01T06:00` | `false`                            | Both of our lowest values in the target range are in the past. |
| `2023-01-01T06:30` | `2023-01-01T06:30` - `2023-01-01T07:00`, `2023-01-01T07:00` - `2023-01-01T07:30` | `true`                             | Both of our lowest values in the target range are in the past, so we must look for the next lowest combined value. |
| `2023-01-01T18:30` | None | `true`                            | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times to look over two days, from `20:00` to `06:00`, we then limit the period that we look at to overnight. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30` - `2023-01-02T00:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `false`                            | Our lowest value of 5 now falls between our overnight time period so is available. |
| `2023-01-02T02:00` | `2023-01-01T23:30` - `2023-01-02T00:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `false`                            | Our lowest period is in the past, but we still have a value in the future so our sensor will only come on once. |
| `2023-01-02T02:00` | `2023-01-02T02:00` - `2023-01-02T02:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `true`                             | The value of 5 is in the past, so we must look for the next lowest combined value, which includes our half hour value at 7. |
| `2023-01-02T05:30` | None | `true`                             | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set an offset of `-00:30:00`, then while the times might be the same, the target value sensor will turn on 30 minutes before the select value period starts. Any set time restrictions **will not** include the offset.
