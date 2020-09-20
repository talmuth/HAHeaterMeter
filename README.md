# HeaterMeter smoker controller component for Home Assistant
HeaterMeter smoker controller integration for HA.

Changes from fancygaphtrn version:
- Changed "heatmeter" name to heatermeter.
- Changed and normalized F' to C'
- Supports new API for HeaterMeter V14

### Getting started

* Add sensor.py, __init__.py, services.yaml and manifest.json to the Home Assistant config\custom_components\heatermeter directory

#### Home Assistant Example

```
configuration.yaml

heatermeter:
  host: <Hostname of HeaterMeter>
  port: 80
  username: PORTAL_LOGIN
  password: PORTAL_PASSWORD
  scan_interval: time in sec (Not implemented yet)
  api_key: api key from HeaterMeter API

input_number:
  setpoint:
    name: Setpoint
    min: 1
    max: 350
    step: 1   
    mode: box    
    unit_of_measurement: "C"
    icon: mdi:thermometer
```
```
automation.yaml

- alias: Update HeaterMeter setpoint
  trigger:
  - entity_id: input_number.setpoint
    platform: state
  action:
  - service: heatermeter.set_temperature
    data_template:
      temperature: '{{ states.input_number.setpoint.state|int }}'
```
```
ui-lovelace.yaml

  - title: Smoker
    cards:
      - type: entities
        title: Smoker
        show_header_toggle: false
        entities:
          - input_number.setpoint
          - heatermeter.setpoint
          - heatermeter.lid
          - heatermeter.fan
          - heatermeter.probe0_temperature
          - heatermeter.probe1_temperature
          - heatermeter.probe2_temperature
          - heatermeter.probe3_temperature
      - type: history-graph
        hours_to_show: 12
        refresh_interval: 10
        entities:
          - heatermeter.setpoint
          - heatermeter.probe0_temperature
          - heatermeter.probe1_temperature
          - heatermeter.probe2_temperature
          - heatermeter.probe3_temperature

```

### References
Support for reading HeaterMeter data. See https://store.heatermeter.com/
