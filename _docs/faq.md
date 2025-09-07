# FAQ

## I've updated the configuration of one of my target timeframe sensors but it's not updating. Is there something wrong?

This was an issue before Home Assistant 2025.09. If you update to 2025.09 or later, this should no longer be an issue.

If you are on a version before Home Assistant 2025.09, then you'll need to reload the parent entry to get the configuration to take effect.

## I've setup a target timeframe with the default time period (00:00-00:00) or a rolling target timeframe looking ahead for 24 hours but it's not updating. Is something broken?

By default, the target timeframe sensors require the supporting data for the specified time periods to be available in order to be calculate. For example if it was `00:00` on `1/12/2025`, then the standard target timeframe would require data for _at least_ between `2025-12-01T00:00` and `2025-12-01T00:00`. If this is not the case, then the sensor will not be evaluated. This is made clearer by the `values_incomplete` attributes of the [target timeframe](./setup/target_timeframe.md#attributes) and [rolling target timeframe](./setup/rolling_target_timeframe.md#attributes).

For some data sources, this might cause issues due to the data available (e.g. When you're on the Agile tariff of [Octopus Energy UK](./blueprints.md#octopus-energy) where data is available in advanced up to `23:00`).

In this scenario, you have two options.

1. The recommended approach would be to adjust the time period that the target timeframe looks at. See below for example suggestions 

| Data Source | Standard Target Timeframe Recommendation | Rolling Target Timeframe Recommendation |
|-|-|-|
| Agile tariff for [Octopus Energy UK](./blueprints.md#octopus-energy) | Have an end time before or equal to `23:00` (e.g. `23:00-23:00` if you want to look at a full 24 hours) | Because data refreshes around `16:00` and will go up to `23:00`, then your look ahead hours should be no more than `7` to ensure it's working `99%` of the time |

2. Set the configuration option to [calculate with incomplete data](./setup/target_timeframe.md#calculate-with-incomplete-data). This _could_ have undesired consequences in the calculations (e.g. picking times that look odd retrospectively because the full data wasn't available at the time of picking), so use with caution.

## How do I increase the logs for the integration?

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issue. This can be done by following the [instructions](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging) outlined by Home Assistant.

You should run these logs for about a day and then include the contents in the issue. Please be sure to remove any personal identifiable information from the logs before including them.