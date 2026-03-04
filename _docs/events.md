# Events

The following events are either raised or received by the integration. These events power various entities and can also be used within automations.

## Update Data Source

`target_timeframe_update_data_source`

Data sources listen for this event and then update the data based on the provided data if the `data_source_id` matches the data source's id.

| Attribute | Type | Description |
|-----------|------|-------------|
| `data_source_id` | `string` | The id of the data source the data belongs to |
| `data` | `array` | The data to update the data source with |

For each item in `data`, the following attributes should be present

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start timestamp the value is effective from |
| `end` | `datetime` | The end timestamp the value is effective to |
| `value` | `float` | The value that is applicable for the timeframe. This could be something like an electricity rate |
| `metadata` | `object` | Additional metadata that might describe how the value was created |