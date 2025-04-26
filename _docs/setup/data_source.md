# Data source

Data sources help group target timeframe sensors together to be fed from a central data source. These data sources take a specific shape, but can represent anything. To start configuring target timeframe sensors, you'll need to create an initial data source. This can be done via the [integration UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=target_timeframe).

Once the data source has been created, you'll have the following entities created. You'll then need to use the [available service](../services.md#target_timeframesupdate_target_timeframe_data_source) to configure the underlying data. There are also a collection of [blueprints](../blueprints.md#data-sources) available for loading popular data sources.

## Entities

### Data Source Last Updated

`sensor.target_timeframes_{{DATA_SOURCE_ID}}_data_source_last_updated`

This entity represents when the data source data was last updated via the [associated service](../services.md#target_timeframesupdate_target_timeframe_data_source).

| Attribute | Type | Description |
|-----------|------|-------------|
| `data_source_id` | `string` | The id of the underlying data source. |
| `data` | `list` | The current collection of data associated with the data source. |

For each item within `data`, you get the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start datetime of the period the value is applicable for. |
| `end` | `datetime` | The end datetime of the period the value is applicable for. |
| `value` | `float` | The value associated with the time period. This is what drives the target timeframe sensors. |
| `metadata` | `object` | The optional metadata associated with the timeframe. This can be used to show how the value was calculated. This is up to the datasource to determine the shape and will vary. |