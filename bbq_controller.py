class HeaterMeter(object):
    """Representation of a BBQ Controller device on the network.
    """

    def __init__(self, bbq_info: HeaterMeterInfo):
        """Initialize the BBQ controller device."""

        self._bbq_info = bbq_info
        self.services = bbq_info.services
        self.bbq_status = None
        self._available = False
        self._status_listener: Optional[bbqStatusListener] = None
        self._hass_bbq_controller: Optional[HomeAssistantController] = None

        self._add_remove_handler = None
        self._bbq_view_remove_handler = None

    @property
    def device_info(self):
        """Return information about the device."""
        bbq_info = self._bbq_info

        if bbq_info.model_name == "HeaterMeter":
            return None

        return {
            "name": bbq_info.friendly_name,
            "identifiers": {(BBQ_DOMAIN, bbq_info.uuid.replace("-", ""))},
            "model": bbq_info.model_name,
            "manufacturer": bbq_info.manufacturer,
        }