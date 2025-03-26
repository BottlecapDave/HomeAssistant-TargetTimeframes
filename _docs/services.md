# Services

There are a few services available within this integration, which are detailed here.

## Target Rates

The following services are available if you have set up at least one [target rate](./setup/target_rate.md).

### target_timeframes.update_target_config

For updating a given [target rate's](./setup/target_rate.md) config. This allows you to change target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated.                                                   |
| `data.target_hours`      | `yes`    | The optional number of hours the target rate sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_start_time` | `yes`    | The optional time the evaluation period should start. Must be in the format of `HH:MM`.                               |
| `data.target_end_time`   | `yes`    | The optional time the evaluation period should end. Must be in the format of `HH:MM`.                                 |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target rate when it starts. Must be in the format `(+/-)HH:MM:SS`.                |
| `data.target_minimum_value`     | `yes`    | The optional minimum rate the selected rates should not go below. |
| `data.target_maximum_value`     | `yes`    | The optional maximum rate the selected rates should not go above. |
| `data.target_weighting`     | `yes`    | The optional weighting that should be applied to the selected rates. |
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
alias: Update target rate config
triggers:
  - trigger: state
    entity_id:
      - input_number.target_timeframes_target_hours
      - input_text.target_timeframes_target_from
      - input_text.target_timeframes_target_to
      - input_text.target_timeframes_target_offset
conditions: []
actions:
  - action: target_timeframes.update_target_config
    data:
      target_hours: >
        "{{ states('input_number.target_timeframes_target_hours') | string }}"
      target_start_time: >
        {{ states('input_text.target_timeframes_target_from') }}
      target_end_time: >
        {{ states('input_text.target_timeframes_target_to') }}
      target_offset: >
        {{ states('input_text.target_timeframes_target_offset') }}
    target:
      entity_id: binary_sensor.target_timeframes_target_example
```

## Rolling Target Rates

The following services are available if you have set up at least one [rolling target rate](./setup/rolling_target_rate.md).

### target_timeframes.update_rolling_target_config

For updating a given [rolling target rate's](./setup/rolling_target_rate.md) config. This allows you to change rolling target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated.                                                   |
| `data.target_hours`      | `yes`    | The optional number of hours the target rate sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_look_ahead_hours` | `yes`    | The optional number of hours worth of rates the sensor should look at for the evaluation period.                               |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target rate when it starts. Must be in the format `(+/-)HH:MM:SS`.                |
| `data.target_minimum_value`     | `yes`    | The optional minimum rate the selected rates should not go below. |
| `data.target_maximum_value`     | `yes`    | The optional maximum rate the selected rates should not go above. |
| `data.target_weighting`     | `yes`    | The optional weighting that should be applied to the selected rates. |
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
alias: Update target rate config
triggers:
  - trigger: state
    entity_id:
      - input_number.target_timeframes_rolling_target_hours
      - input_number.target_timeframes_rolling_target_look_ahead_hours
      - input_text.target_timeframes_target_offset
conditions: []
actions:
  - action: target_timeframes.update_target_config
    data:
      target_hours: >
        "{{ states('input_number.target_timeframes_target_hours') | string }}"
      target_look_ahead_hours: >
        "{{ states('input_number.target_timeframes_rolling_target_look_ahead_hours') | string }}"
      target_offset: >
        {{ states('input_text.target_timeframes_target_offset') }}
    target:
      entity_id: binary_sensor.target_timeframes_rolling_target_example
```
