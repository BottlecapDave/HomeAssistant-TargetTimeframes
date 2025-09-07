## [1.3.1](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.3.0...v1.3.1) (2025-09-07)


### Bug Fixes

* fixed ability to set zero for min/max values (30 minutes dev time) ([e542f71](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/e542f71593738496568898bb783951c605786c6d))
* fixed target timeframes to support reloading entity upon updating configuration (15 minutes dev time) ([c4a2f84](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/c4a2f844a5e959583a798a91d3393280b7f7ed6c))

# [1.3.0](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.2.1...v1.3.0) (2025-08-17)


### Bug Fixes

* fixed minimum/maximum targets to support negative values (45 minutes dev time) ([8d27582](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/8d27582d7b037e23bb2d285d6b4aca2e5586f02a))


### Features

* Added configuration for standard and rolling target timeframes to determine minimum minutes for a slot to be evaluated (3.5 hours dev time) ([3d4ba9d](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/3d4ba9dfc24005cd77b5961553faacb765dcf593))
* added support to evaluate with incomplete data (1 hour dev time) ([a61edfa](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/a61edfa71c23f5c88a7017ac0606f70f73b2b659))

## [1.2.1](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.2.0...v1.2.1) (2025-06-14)


### Bug Fixes

* added additional logging for debugging purposes ([99d0bb6](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/99d0bb60cb6da0df69fd8b82c8752a072a571794))

# [1.2.0](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.1.1...v1.2.0) (2025-06-11)


### Features

* Added data source attribute to sensors ([4ff880e](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/4ff880ebda435371c3e55cc86e4440f8e29a7f89))
* Updated update config service to re-evaluate straight away (5 minutes dev time) ([54f68ca](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/54f68ca6fa2c5f4d65ed0c899aea87fc5afc1aa9))

## [1.1.1](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.1.0...v1.1.1) (2025-05-31)


### Bug Fixes

* Fixed issue where started target timeframes are calculated and it starts in the past (2 hours dev time) ([fe54ba0](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/fe54ba036c10af23cd2d4a2ee495b6b6123ee025))

# [1.1.0](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.0.4...v1.1.0) (2025-05-23)


### Bug Fixes

* Fixed issue where target times could be recalculated within the same target time frame once complete, causing the sensor to come on more than it should (1 hour dev time) ([6627bb8](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/6627bb88a02704b845cd425745193fe8a1e5017a))


### Features

* Updated update_data_source service to now append data instead of replace data by default as this caused issues with certain data sources when it was replacing. Replacing is now available as an optional toggle (40 minute dev time) ([4e657f8](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/4e657f83436beca8261a47f48cf730520cfd8185))

## [1.0.3](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.0.2...v1.0.3) (2025-05-09)


### Bug Fixes

* Fixed issue where target timeframes can't be reconfigured on 2025.4 onwards (30 minutes dev time) ([b778dda](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/b778ddae183358f706f3840bfd17d3720553d867))
* Fixed the ability to reconfigure data sources (1 hour dev time) ([a2472d4](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/a2472d4cd9a279325485e6a6aaab011f12761605))

## [1.0.2](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.0.1...v1.0.2) (2025-04-01)


### Bug Fixes

* Fixed integration not appearing in integrations ([51820ff](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/51820fff765b63bad931d54b9a89c44346003d91))

## [1.0.1](https://github.com/BottlecapDave/homeassistant-targettimeframes/compare/v1.0.0...v1.0.1) (2025-03-29)


### Bug Fixes

* Fixed documentation references ([c09d012](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/c09d01291b1f65d43589ce81f3098c658e4ba676))
* Fixed missing repair translation and associated doc page ([e71a958](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/e71a958e7c69f5b9e6ff9ba316593eca6598ced9))
* Fixed updating configuration when only some values are updated ([d146fb4](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/d146fb4c0f2db46da56e5076a6ffd90947d22066))

# 1.0.0 (2025-03-29)


### Features

* Added initial integration ([247db85](https://github.com/BottlecapDave/homeassistant-targettimeframes/commit/247db859e3d3f417ab2170e00515ad7328b9e320))
