# Services

There are a few services available within this integration, which are detailed here.

## Data Sources

### target_timeframes.update_target_timeframe_data_source

Updates the source data for a given target frame. This will update any existing data for the source, but keep any existing data that hasn't been provided. It will also remove any data that is older than 1 day previous to today. For example, if today is 2025-05-17, then all data before 2025-05-16 will be removed.

There are a collection of [blueprints](./blueprints.md#data-sources) available for loading popular data sources.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the [data source last updated](./setup/data_source.md#data-source-last-updated) sensor whose underlying data is to be updated.                                                   |
| `data.replace_all_existing_data` | `yes` | Determines if the provided data should replace all existing data. If not provided or false, then new data will be added to existing data and existing data will be replaced where start/end times match. |
| `data.data`      | `no`    | The collection of data to update the data source with. This will override any previous data. For the target rate sensors to work properly, you should target having data for the whole of yesterday, today and tomorrow (e.g. if today is 2025-01-04, you should aim to have data from 2025-01-03T00:00:00 to 2025-01-06T00:00:00).

The structure of the data should match the following

```
[
  {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-01T00:30:00Z",
    "value": 0.1,
    "metadata": {
      // Any additional metadata that might describe how the value was created
    }
  },
  {
    "start": "2025-01-01T00:30:00Z",
    "end": "2025-01-01T01:00:00Z",
    "value": 0.2,
    "metadata": {
      // Any additional metadata that might describe how the value was created
    }
  },
  ...
]
```

Each item within the data must be in thirty minute increments. The minute must be 00 or 30, the second should be zero.

#### Automations

Examples can be found in the [blueprints](./blueprints.md) section for configuring a variety of different data sources.

## Target Timeframes

The following services are available if you have set up at least one [target timeframe](./setup/target_timeframe.md).

### target_timeframes.update_target_timeframe_config

For updating a given [target timeframe's](./setup/target_timeframe.md) config. This allows you to change target timeframes sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

!!! warning

    This will cause the sensor to re-evaluate the target times, which may result in different times being picked.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated.                                                   |
| `data.target_hours`      | `yes`    | The optional number of hours the target timeframe sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_start_time` | `yes`    | The optional time the evaluation period should start. Must be in the format of `HH:MM`.                               |
| `data.target_end_time`   | `yes`    | The optional time the evaluation period should end. Must be in the format of `HH:MM`.                                 |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target timeframe when it starts. Must be in the format `(+/-)HH:MM:SS`.                |
| `data.target_minimum_value`     | `yes`    | The optional minimum timeframe the selected timeframes should not go below. |
| `data.target_maximum_value`     | `yes`    | The optional maximum timeframe the selected timeframes should not go above. |
| `data.target_weighting`     | `yes`    | The optional weighting that should be applied to the selected timeframes. |
| `data.persist_changes` | `yes` | Determines if the changes should be persisted to the original configuration or should be temporary and reset upon integration reload. If not supplied, then the changes are temporary |

#### Automation Example

This can be used via automations in the following way. Assuming we have the following inputs.

```yaml
input_number:
  target_timeframes_target_hours:
    name: Target Timeframes Target Hours
    min: 0
    max: 24

input_text:
  # From/to would ideally use input_datetime, but we need the time in a different format
  target_timeframes_target_from:
    name: Target Timeframes Target From
    initial: "00:00"
  target_timeframes_target_to:
    name: Target Timeframes Target To
    initial: "00:00"
  target_timeframes_target_offset:
    name: Target Timeframes Target Offset
    initial: "-00:00:00"
```

Then an automation might look like the following

```yaml
mode: single
alias: Update target timeframe config
triggers:
  - trigger: state
    entity_id:
      - input_number.target_timeframes_target_hours
      - input_text.target_timeframes_target_from
      - input_text.target_timeframes_target_to
      - input_text.target_timeframes_target_offset
conditions: []
actions:
  - action: target_timeframes.update_target_timeframe_config
    data:
      target_hours: >
        {{ states('input_number.target_timeframes_target_hours') }}
      target_start_time: >
        {{ states('input_text.target_timeframes_target_from') }}
      target_end_time: >
        {{ states('input_text.target_timeframes_target_to') }}
      target_offset: >
        {{ states('input_text.target_timeframes_target_offset') }}
    target:
      entity_id: binary_sensor.target_timeframes_target_example
```

## Rolling Target Timeframes

The following services are available if you have set up at least one [rolling target timeframe](./setup/rolling_target_timeframe.md).

### target_timeframes.update_rolling_target_timeframe_config

For updating a given [rolling target timeframe's](./setup/rolling_target_timeframe.md) config. This allows you to change rolling target timeframes sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

!!! warning

    This will cause the sensor to re-evaluate the target times, which may result in different times being picked.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated.                                                   |
| `data.target_hours`      | `yes`    | The optional number of hours the target timeframe sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_look_ahead_hours` | `yes`    | The optional number of hours worth of timeframes the sensor should look at for the evaluation period.                               |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target timeframe when it starts. Must be in the format `(+/-)HH:MM:SS`.                |
| `data.target_minimum_value`     | `yes`    | The optional minimum timeframe the selected timeframes should not go below. |
| `data.target_maximum_value`     | `yes`    | The optional maximum timeframe the selected timeframes should not go above. |
| `data.target_weighting`     | `yes`    | The optional weighting that should be applied to the selected timeframes. |
| `data.persist_changes` | `yes` | Determines if the changes should be persisted to the original configuration or should be temporary and reset upon integration reload. If not supplied, then the changes are temporary |

#### Automation Example

This can be used via automations in the following way. Assuming we have the following inputs.

```yaml
input_number:
  target_timeframes_rolling_target_hours:
    name: Target Timeframes Rolling Target Hours
    min: 0
    max: 24
  target_timeframes_rolling_target_look_ahead_hours:
    name: Target Timeframes Rolling Target Look Ahead Hours
    min: 0
    max: 24

input_text:
  target_timeframes_target_offset:
    name: Target Timeframes Target Offset
    initial: "-00:00:00"
```

Then an automation might look like the following

```yaml
mode: single
alias: Update target timeframe config
triggers:
  - trigger: state
    entity_id:
      - input_number.target_timeframes_rolling_target_hours
      - input_number.target_timeframes_rolling_target_look_ahead_hours
      - input_text.target_timeframes_target_offset
conditions: []
actions:
  - action: target_timeframes.update_target_timeframe_config
    data:
      target_hours: >
        {{ states('input_number.target_timeframes_target_hours') }}
      target_look_ahead_hours: >
        {{ states('input_number.target_timeframes_rolling_target_look_ahead_hours') }}
      target_offset: >
        {{ states('input_text.target_timeframes_target_offset') }}
    target:
      entity_id: binary_sensor.target_timeframes_rolling_target_example
```