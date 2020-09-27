"""
Support for reading HeaterMeter data. See https://github.com/CapnBry/HeaterMeter/wiki/Accessing-Raw-Data-Remotely

configuration.yaml

heatermeter:
    api_key: api key from HeaterMeter API
    host: smoker.lan
    port: 80
    scan_interval: 2
"""
import logging
import requests
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (
        CONF_HOST, CONF_PORT, CONF_TEMPERATURE_UNIT, CONF_UNIT_SYSTEM, CONF_API_KEY, CONF_SCAN_INTERVAL
    )

DOMAIN = 'heatermeter'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_TEMPERATURE_UNIT, default="F"): cv.string,
        vol.Optional(CONF_PORT, default=80): cv.positive_int,
        vol.Optional(CONF_SCAN_INTERVAL, default=10): cv.positive_int
    })
}, extra=vol.ALLOW_EXTRA)


SET_URL_API = 'http://{0}:{1}/luci/lm/api/config'
TEMPERATURE_NAME = 'temperature'
TEMPERATURE_DEFAULT = '225'
_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    _LOGGER.debug("HeaterMeter init.py: config = %s", config[DOMAIN])

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][CONF_HOST]                = config[DOMAIN][CONF_HOST]
    hass.data[DOMAIN][CONF_PORT]                = config[DOMAIN][CONF_PORT]
    #hass.data[DOMAIN][CONF_TEMPERATURE_UNIT]    = config[DOMAIN][CONF_TEMPERATURE_UNIT]
    hass.data[DOMAIN][CONF_API_KEY]             = config[DOMAIN][CONF_API_KEY]
    hass.data[DOMAIN][CONF_SCAN_INTERVAL]       = config[DOMAIN][CONF_SCAN_INTERVAL]

    _LOGGER.debug("HeaterMeter init.py: hass.data = %s", hass.data[DOMAIN])


    def handle_setpoint(temperature):
        _LOGGER.debug("HeaterMeter handle_setpoint: temp = %s", temperature)


    def handle_setpoint_api(call):
        """Handle the service call."""
        _LOGGER.debug("HeaterMeter init.py: calli = %s", call)
 
        temp = call.data.get(TEMPERATURE_NAME, TEMPERATURE_DEFAULT)
        _LOGGER.debug("HeaterMeter init.py: temp = %s", temp)

        #SET_URL_API = 'http://{0}:{1}/luci/lm/api/config'
        try:
            data = {'sp':temp, 'apikey':hass.data[DOMAIN][CONF_API_KEY]}
        
            _LOGGER.debug("HeaterMeter handle_setpoint: data = %s", data)

            url = SET_URL_API.format(
                    hass.data[DOMAIN][CONF_HOST], hass.data[DOMAIN][CONF_PORT]
            )
            _LOGGER.debug("HeaterMeter handle_setpoint: ADMIN_URL = %s", url)
            
            r = requests.post(url, data = data)
            if r.status_code == 200:
                _LOGGER.info("HeaterMeter handle_setpoint Setpoint updated: %s" % (temp))
                _LOGGER.debug("HeaterMeter handle_setpoint Status: %s" % (r.text))
                _LOGGER.debug("HeaterMeter handle_setpoint headers: %s" % (r.headers))
            elif r.status_code == 404:
                _LOGGER.debug("HeaterMeter handle_setpoint_api wrong API version, reverting to old setpoint api")
                handle_setpoint(temp)
            elif r.status_code == 403:
                _LOGGER.debug("HeaterMeter handle_setpoint_api User has explicitly disabled external API")

            else:
                _LOGGER.debug("HeaterMeter handle_setpoint_api unknown http reply %s", temp)

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            _LOGGER.error("HeaterMeter handle_setpoint Post Connection error %s" % (r.status_code))

    hass.services.register(DOMAIN, 'set_temperature', handle_setpoint_api)

    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)

    # Return boolean to indicate that initialization was successfully.
    return True
