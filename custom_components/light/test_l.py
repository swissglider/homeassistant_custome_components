from homeassistant.components.light import ATTR_BRIGHTNESS, Light

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([TestLight()])

class TestLight(Light):
    """Representation of an Test Light."""

    def __init__(self):
        self._state = 'off'
        self._brightness = None
    
    @property
    def unique_id(self):
        return "T-Light"

    @property
    def name(self):
        return "T-Light"

    @property
    def brightness(self):
        return self._brightness

    @property
    def is_on(self):
        return self._state

    def turn_on(self, **kwargs):
        self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        self._state = "on"

    def turn_off(self, **kwargs):
        self._state = "off"

    def update(self):
        pass