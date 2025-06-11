# Home Assistant Target Timeframes

Target timeframes was a feature that has been extracted out of the [Octopus Energy integration](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy). The idea is you can configure binary sensors that will find and turn on during the most optimal time periods based on external data sources, targeting either the lowest or highest values. What these values represent can be anything. In the original integration, the values represented cost of energy, and so the cheapest periods were discovered. But it could represent other things like 

* Energy prices to turn on devices when cost is the cheapest
* Carbon emissions to turn on devices when renewables on the grid are at their highest
* Solar generation to turn on devices when the most energy is being generated.

How the sensors behave is configurable in a number of ways and explained further in the docs.

## How to install

There are multiple ways of installing the integration. Once you've installed the integration, you'll need to [setup your account](#how-to-setup) before you can use the integration.

### HACS

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This integration can be installed directly via HACS. To install:

* [Add the repository](https://my.home-assistant.io/redirect/hacs_repository/?owner=BottlecapDave&repository=homeassistant-targettimeframes&category=integration) to your HACS installation
* Click `Download`

### Manual

You should take the latest [published release](https://github.com/BottlecapDave/homeassistant-targettimeframes/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

## How to setup

It is recommended to consult the [getting started](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/setup/getting_started) guide.

## Events

This integration raises several events, which can be used for various tasks like automations. For more information, please see the [events docs](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/events).

## Services

This integration includes several services. Please review them in the [services doc](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/services).

## Blueprints

A selection of [blueprints](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/blueprints) are available to help get you up and running quickly with the integration.

## FAQ

Before raising anything, please read through the [faq](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/faq). If you have questions, then you can raise a [discussion](https://github.com/BottlecapDave/homeassistant-targettimeframes/discussions). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/homeassistant-targettimeframes/issues) using the appropriate report template.

## Sponsorship

Please see the [sponsorship](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/sponsorship) page for more information.