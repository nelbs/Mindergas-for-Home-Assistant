# Mindergas for Home-Assistant (DEPRECATED)

This is repository is no longer supported as I dont use it myself. Please consider using https://github.com/Ernst79/degree-days instead. That repo does not rely on data of mindergas.nl but calculates the gas prognose and degree days.






This platform scrapes the gas consumption from the dutch website mindergas.nl. It creates the folowing sensors:

- sensor.mindergas_graaddag      : gas consumption per degree day
- sensor.mindergas_prognose      : forecasted total gas consumption current year
- sensor.mindergas_used          : gas consumption current year 

The sensors are updated daily since the data is based on daily gas consumption.

## Prerequisites
- You need a mindergas account
- You need to upload your daily gas consumption to the website mindergas frequently

## HACS Installation
1. Make sure you've installed [HACS](https://hacs.xyz/docs/installation/prerequisites)
2. In the integrations tab, search for Mindergas.
3. Install the Integration.
4. Add mindergas entry to configuration (see below)

## Manual installation

1. Open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called ziggonext.
4. Download all the files from the custom_components/mindergas/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Add mindergas entry to configuration (see below)
7. Restart Home Assistant

## Configuration
```yaml
sensor:
  - platform: mindergas
    username: !secret mindergas_username
    password: !secret mindergas_password
```
