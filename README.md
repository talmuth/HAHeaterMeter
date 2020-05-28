# HeaterMeter smoker controller
HeaterMeter smoker controller custom sensor for home assistant

### Getting started

* Add sensor.py, __init__.py, services.yaml and manifest.json to the Home Assistant config\custom_components\heaterheter directory

#### Home Assistant Example

```
configuration.yaml

heaterheter:
  host: <Hostname of HeaterMeter>
  port: 80
  username: PORTAL_LOGIN
  password: PORTAL_PASSWORD

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
  - service: heaterheter.set_temperature
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
          - heaterheter.setpoint
          - heaterheter.lid
          - heaterheter.fan
          - heaterheter.probe0_temperature
          - heaterheter.probe1_temperature
          - heaterheter.probe2_temperature
      - type: history-graph
        hours_to_show: 12
        refresh_interval: 10
        entities:
          - heaterheter.setpoint
          - heaterheter.probe0_temperature
          - heaterheter.probe1_temperature
          - heaterheter.probe2_temperature

```

### References
Support for reading HeaterMeter data. See https://store.heatermeter.com/
