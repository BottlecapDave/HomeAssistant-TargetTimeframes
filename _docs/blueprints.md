# Blueprints

[Blueprints](https://www.home-assistant.io/docs/automation/using_blueprints/) are an excellent way to get you up and running with the integration quickly. They can also be used as a guide for setting up new automations which you can tailor to your needs.

## Data Sources

The following blueprints can help you use data from other integrations as the source of your target timeframes.

### Carbon Intensity

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fbottlecapdave.github.io%2FHomeAssistant-TargetTimeframes%2Fblueprints%2Ftarget_timeframes_carbon_intensity.yaml) | [Source](./blueprints/target_timeframes_carbon_intensity.yaml)

This blueprint will provide the data source for the UK Carbon Intensity as provided by the [Carbon Intensity](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity) integration.

!!! warning

    This automation will run when any of the underlying entities update. This make take a while initially. If you want the data available immediately, then you'll need to run the automation manually.

### Octopus Energy

[Install blueprint (No Free Electricity)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fbottlecapdave.github.io%2FHomeAssistant-TargetTimeframes%2Fblueprints%2Ftarget_timeframes_octopus_energy.yaml) | [Source](./blueprints/target_timeframes_octopus_energy.yaml)

[Install blueprint (Free Electricity Included)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fbottlecapdave.github.io%2FHomeAssistant-TargetTimeframes%2Fblueprints%2Ftarget_timeframes_octopus_energy_with_free_electricity.yaml) | [Source](./blueprints/target_timeframes_octopus_energy_with_free_electricity.yaml)

This blueprint will provide the data source for Octopus Energy rates as provided by the [Octopus Energy](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy) integration.

!!! warning

    This automation will run when any of the underlying entities update. This make take a while initially. If you want the data available immediately, then you'll need to run the automation manually.

### Octopus Energy and Carbon Intensity

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fbottlecapdave.github.io%2FHomeAssistant-TargetTimeframes%2Fblueprints%2Ftarget_timeframes_octopus_energy_carbon_intensity.yaml) | [Source](./blueprints/target_timeframes_octopus_energy_carbon_intensity.yaml)

This blueprint will provide the data source for Octopus Energy rates as provided by the [Octopus Energy](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy) integration and UK Carbon Intensity as provided by the [Carbon Intensity](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity) integration. It will multiply the OE rate by the carbon intensity, resulting in target timeframes favouring periods with low rates, and then falling back to carbon intensity where rates are the same.

!!! warning

    This automation will run when any of the underlying entities update. This make take a while initially. If you want the data available immediately, then you'll need to run the automation manually.