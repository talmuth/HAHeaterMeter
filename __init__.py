"""
Support for reading HeaterMeter data. See https://store.heatermeter.com/

configuration.yaml

heatermeter:
    host: smoker.lan
    port: 80
    username: PORTAL_LOGIN
    password: PORTAL_PASSWORD
    scan_interval: 2
    api_key: api key from HeaterMeter API
"""
import logging
import requests
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (
        CONF_USERNAME, CONF_PASSWORD, CONF_HOST, CONF_PORT, CONF_API_KEY, CONF_SCAN_INTERVAL
    )

DOMAIN = 'heatermeter'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_PORT, default=80): cv.positive_int,
        vol.Optional(CONF_SCAN_INTERVAL, default=10): cv.positive_int
    })
}, extra=vol.ALLOW_EXTRA)

ADMIN_URL = 'http://{0}:{1}/luci/admin/lm'
SET_URL = 'http://{0}:{1}/luci/;{2}/admin/lm/set?sp={3}'
SET_URL_API = 'http://{0}:{1}/luci/lm/api/config'
TEMPERATURE_NAME = 'temperature'
TEMPERATURE_DEFAULT = '110'
_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    _LOGGER.debug("HeaterMeter init.py: config = %s", config[DOMAIN])

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][CONF_HOST]            = config[DOMAIN][CONF_HOST]
    hass.data[DOMAIN][CONF_PORT]            = config[DOMAIN][CONF_PORT]
    hass.data[DOMAIN][CONF_USERNAME]        = config[DOMAIN][CONF_USERNAME]
    hass.data[DOMAIN][CONF_PASSWORD]        = config[DOMAIN][CONF_PASSWORD]
    hass.data[DOMAIN][CONF_API_KEY]         = config[DOMAIN][CONF_API_KEY]
    hass.data[DOMAIN][CONF_SCAN_INTERVAL]   = config[DOMAIN][CONF_SCAN_INTERVAL]

    _LOGGER.debug("HeaterMeter init.py: hass.data = %s", hass.data[DOMAIN])


    def handle_setpoint(temperature):
        _LOGGER.debug("HeaterMeter handle_setpoint: temp = %s", temperature)


        try:
            data = {'username':hass.data[DOMAIN][CONF_USERNAME], 
                'password':hass.data[DOMAIN][CONF_PASSWORD]}

            _LOGGER.debug("HeaterMeter handle_setpoint: data = %s", data)

            url = ADMIN_URL.format(
                    hass.data[DOMAIN][CONF_HOST], hass.data[DOMAIN][CONF_PORT]
            )
            _LOGGER.debug("HeaterMeter handle_setpoint: ADMIN_URL = %s", url)
            
            r = requests.post(url, data = data)
            if r.status_code == 200:
                _LOGGER.debug("HeaterMeter handle_setpoint Status: %s" % (r.text))
                _LOGGER.debug("HeaterMeter handle_setpoint headers: %s" % (r.headers))
                _LOGGER.debug("HeaterMeter handle_setpoint cookies: %s" % (r.cookies))
                
    
                tokens = r.headers['set-cookie'].split(';')
                headers = {'Cookie': tokens[0] +';'}
                
                url = SET_URL.format(
                        hass.data[DOMAIN][CONF_HOST], hass.data[DOMAIN][CONF_PORT], tokens[2] , temperature
                )
                _LOGGER.debug("HeaterMeter handle_setpoint: SET_URL = %s", url)
                #url = 'http://smoker.lan/luci/;'+ tokens[2] + '/admin/lm/set?sp=' + temperature
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    _LOGGER.info("HeaterMeter handle_setpoint Setpoint updated: %s" % (temperature))

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            _LOGGER.error("HeaterMeter handle_setpoint Post Connection error %s" % (e))
    
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
